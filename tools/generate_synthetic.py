#!/usr/bin/env python3
"""Deterministic teaching data. Contains no measurements or customer information."""
import argparse
import csv
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

AUTHOR = "Csott Károly Péter"
FIELDS = ["site_id", "meter_id", "interval_start_utc", "interval_end_utc",
          "interval_start_local", "interval_minutes", "site_load_kwh",
          "pv_generation_kwh", "pv_self_consumed_kwh", "grid_import_kwh",
          "grid_export_kwh", "avg_site_load_kw", "avg_grid_import_kw", "quality_flag"]


def generate(start_date="2026-10-19", days=7, tz_name="Europe/Budapest"):
    zone = ZoneInfo(tz_name)
    local_start = datetime.fromisoformat(start_date).replace(tzinfo=zone)
    if local_start.time().isoformat() != "00:00:00" or days < 1:
        raise ValueError("Use a local calendar date at midnight and positive days")
    local_end = local_start + timedelta(days=days)
    cursor = local_start.astimezone(timezone.utc)
    end = local_end.astimezone(timezone.utc)
    rows = []
    while cursor < end:
        local = cursor.astimezone(zone)
        h = local.hour + local.minute / 60
        weekday = local.weekday() < 5
        load = 150.0 if weekday else 90.0
        if 7 <= h < 19:
            load += (300.0 if weekday else 35.0) + 40 * math.sin(math.pi * (h - 7) / 12)
        flag = "SYNTHETIC"
        if weekday and h == 17.25:
            load = 920.0
            flag = "SYNTHETIC_PEAK_EVENT"
        # An idealized mathematical shape, not a PV yield or weather prediction.
        pv = 400 * max(0.0, math.sin(math.pi * (h - 7) / 10)) if 7 < h < 17 else 0.0
        load, pv = round(load, 2), round(pv, 2)
        self_use = min(load, pv)
        imp, exp = max(load - pv, 0), max(pv - load, 0)
        rows.append(dict(zip(FIELDS, [
            "SYNTHETIC-SITE-001", "SYNTHETIC-GRID-001", cursor.isoformat(),
            (cursor + timedelta(minutes=15)).isoformat(), local.isoformat(), "15",
            f"{load / 4:.4f}", f"{pv / 4:.4f}", f"{self_use / 4:.4f}",
            f"{imp / 4:.4f}", f"{exp / 4:.4f}", f"{load:.2f}", f"{imp:.2f}", flag])))
        cursor += timedelta(minutes=15)
    metadata = {
        "title": "Synthetic Industrial Load Profile for PV–BESS Screening",
        "author": AUTHOR, "author_ascii": "Csott Karoly Peter", "version": "0.1.0",
        "is_synthetic": True, "timezone": tz_name, "interval_minutes": 15,
        "period_start_utc": local_start.astimezone(timezone.utc).isoformat(),
        "period_end_utc_exclusive": end.isoformat(), "expected_rows": len(rows),
        "site_id": "SYNTHETIC-SITE-001", "meter_id": "SYNTHETIC-GRID-001",
        "energy_unit": "kWh", "power_unit": "kW", "quantity_basis": "interval_energy",
        "measurement_boundary": "Common AC boundary; illustrative no-storage baseline",
        "storage_present": False, "pv_nameplate_dc_kwp_assumption": 600,
        "pv_inverter_ac_kw_assumption": 450,
        "pv_model": "Idealized 07:00–17:00 local sine shape capped at 400 kW; no weather model",
        "within_interval_assumption": "Constant average load and PV in each interval",
        "limitations": ["Not measured data", "Not a calibrated industrial demand forecast",
                       "Not a PV yield estimate", "No BESS dispatch, tariffs, revenue or project sizing",
                       "Seven days do not establish seasonal or annual representativeness"],
        "ai_disclosure": "Prepared with generative AI assistance. Algorithm and assumptions are explicit."
    }
    return rows, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-date", default="2026-10-19")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--timezone", default="Europe/Budapest")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, metadata = generate(args.start_date, args.days, args.timezone)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    meta_path = args.output.with_suffix(".metadata.json")
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "csv": str(args.output), "metadata": str(meta_path)}))


if __name__ == "__main__":
    main()
