#!/usr/bin/env python3
"""Read-only consistency checks for the documented single-series AC baseline schema."""
import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

ENERGY = ("site_load_kwh", "pv_generation_kwh", "pv_self_consumed_kwh", "grid_import_kwh", "grid_export_kwh")
POWER = ("avg_site_load_kw", "avg_grid_import_kw")
REQUIRED = ("site_id", "meter_id", "interval_start_utc", "interval_end_utc",
            "interval_start_local", "interval_minutes", *ENERGY, *POWER, "quality_flag")


def parse_aware(value):
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("Timestamp needs Z or an explicit UTC offset")
    return timestamp


def validate(rows, metadata):
    issues = []
    def issue(code, row=None, detail=""):
        issues.append({"code": code, "row": row, "detail": detail})
    expected_meta = {"energy_unit": "kWh", "power_unit": "kW", "quantity_basis": "interval_energy", "interval_minutes": 15}
    for key, expected in expected_meta.items():
        if metadata.get(key) != expected:
            issue("metadata", detail=f"{key} must be {expected!r}")
    if metadata.get("storage_present") is not False:
        issue("unsupported_boundary", detail="This schema requires a no-storage AC baseline")
    try:
        zone = ZoneInfo(metadata["timezone"])
        begin = parse_aware(metadata["period_start_utc"]).astimezone(timezone.utc)
        end = parse_aware(metadata["period_end_utc_exclusive"]).astimezone(timezone.utc)
        periods = (end - begin).total_seconds() / 900
        if periods <= 0 or periods != int(periods) or periods > 1_000_000:
            raise ValueError("Invalid or excessive expected time span")
        if begin.timestamp() % 900 or end.timestamp() % 900:
            raise ValueError("Period bounds must align to 15-minute UTC intervals")
    except (KeyError, ValueError) as exc:
        issue("period_metadata", detail=str(exc))
        return {"passed": False, "rows": len(rows), "issues": issues}
    seen, previous, peaks = [], None, []
    for number, row in enumerate(rows, start=2):
        missing_fields = [key for key in REQUIRED if key not in row or row[key] in (None, "")]
        if missing_fields:
            issue("missing_field", number, ",".join(missing_fields))
            continue
        for key in ("site_id", "meter_id"):
            if row[key] != metadata.get(key):
                issue("series_identity", number, key)
        try:
            raw_start, raw_end = parse_aware(row["interval_start_utc"]), parse_aware(row["interval_end_utc"])
            start, stop = raw_start.astimezone(timezone.utc), raw_end.astimezone(timezone.utc)
            local = parse_aware(row["interval_start_local"])
            if raw_start.utcoffset() != timedelta(0) or raw_end.utcoffset() != timedelta(0):
                issue("utc_column_offset", number)
            if (stop - start).total_seconds() != 900 or Decimal(row["interval_minutes"]) != 15:
                issue("duration", number)
            if start.timestamp() % 900:
                issue("alignment", number)
            correct_local = start.astimezone(zone)
            if local.astimezone(timezone.utc) != start or local.isoformat() != correct_local.isoformat():
                issue("local_timestamp", number, "Local clock and offset must agree with the named zone")
            if previous is not None and start < previous:
                issue("unsorted", number)
            previous = start
            seen.append(start)
        except (ValueError, InvalidOperation) as exc:
            issue("timestamp", number, str(exc))
            continue
        try:
            quantities = {key: Decimal(str(row[key])) for key in (*ENERGY, *POWER)}
            if any(not value.is_finite() for value in quantities.values()):
                raise ValueError("Non-finite quantity")
            if any(value < 0 for value in quantities.values()):
                issue("negative_quantity", number, "Directional channels use non-negative values")
            q = quantities
            # All channels use one AC boundary. Storage needs additional charge/discharge terms.
            if abs(q["grid_import_kwh"] + q["pv_generation_kwh"] - q["site_load_kwh"] - q["grid_export_kwh"]) > Decimal("0.0001"):
                issue("energy_balance", number)
            if abs(q["pv_self_consumed_kwh"] + q["grid_import_kwh"] - q["site_load_kwh"]) > Decimal("0.0001"):
                issue("self_consumption_balance", number)
            if abs(q["pv_self_consumed_kwh"] + q["grid_export_kwh"] - q["pv_generation_kwh"]) > Decimal("0.0001"):
                issue("pv_balance", number)
            if abs(q["avg_site_load_kw"] - q["site_load_kwh"] * 4) > Decimal("0.01"):
                issue("energy_power_units", number, "Average site kW must equal interval kWh /0.25h")
            if abs(q["avg_grid_import_kw"] - q["grid_import_kwh"] * 4) > Decimal("0.01"):
                issue("energy_power_units", number, "Average import kW must equal interval kWh /0.25h")
            peaks.append((float(q["avg_grid_import_kw"]), row["interval_start_utc"], row["quality_flag"]))
        except (InvalidOperation, ValueError) as exc:
            issue("quantity", number, str(exc))
    count = Counter(seen)
    duplicates = sum(n - 1 for n in count.values())
    if duplicates:
        issue("duplicate_utc", detail=str(duplicates))
    expected = {begin + timedelta(minutes=15 * i) for i in range(int(periods))}
    missing, outside = expected - set(seen), set(seen) - expected
    if missing:
        issue("missing_intervals", detail=str(len(missing)))
    if outside:
        issue("outside_period", detail=str(len(outside)))
    return {"passed": not issues, "rows": len(rows), "expected_intervals": len(expected),
            "missing_intervals": len(missing), "duplicate_intervals": duplicates,
            "largest_interval_average_import_kw": sorted(peaks, reverse=True)[:5],
            "issues": issues,
            "scope": "File consistency only. Peaks are interval averages. No tariff, battery sizing or financeability decision."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("metadata_file", type=Path)
    args = parser.parse_args()
    with args.csv_file.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = validate(rows, json.loads(args.metadata_file.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
