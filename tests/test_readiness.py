import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from generate_synthetic import generate
from validate_intervals import parse_aware, validate


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.meta = generate("2026-10-25", 1)

    def codes(self, rows=None, meta=None):
        return {x["code"] for x in validate(self.rows if rows is None else rows, self.meta if meta is None else meta)["issues"]}

    def test_25_hour_day_has_100_unique_utc_intervals(self):
        self.assertEqual(len(self.rows), 100)
        self.assertTrue(validate(self.rows, self.meta)["passed"])

    def test_23_hour_day_has_92_intervals(self):
        rows, meta = generate("2026-03-29", 1)
        self.assertEqual(len(rows), 92)
        self.assertTrue(validate(rows, meta)["passed"])

    def test_week_including_fall_transition_has_676_rows(self):
        rows, meta = generate("2026-10-19", 7)
        self.assertEqual(len(rows), 676)
        self.assertTrue(validate(rows, meta)["passed"])

    def test_leading_missing_interval_is_detected(self):
        self.assertIn("missing_intervals", self.codes(self.rows[1:]))

    def test_trailing_missing_interval_is_detected(self):
        self.assertIn("missing_intervals", self.codes(self.rows[:-1]))

    def test_duplicate_instant_is_detected(self):
        self.assertIn("duplicate_utc", self.codes([self.rows[0]] + self.rows))

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_aware("2026-10-25T02:00:00")

    def test_local_clock_repeat_with_distinct_offsets_is_valid(self):
        two = [r for r in self.rows if r["interval_start_local"].startswith("2026-10-25T02:00:")]
        self.assertEqual(len(two), 2)
        self.assertNotEqual(two[0]["interval_start_utc"], two[1]["interval_start_utc"])

    def test_mwh_is_not_silently_treated_as_kwh(self):
        meta = dict(self.meta, energy_unit="MWh")
        self.assertIn("metadata", self.codes(meta=meta))

    def test_negative_import_is_rejected(self):
        rows = copy.deepcopy(self.rows); rows[0]["grid_import_kwh"] = "-1"
        self.assertIn("negative_quantity", self.codes(rows))

    def test_non_finite_quantity_is_rejected(self):
        rows = copy.deepcopy(self.rows); rows[0]["site_load_kwh"] = "NaN"
        self.assertIn("quantity", self.codes(rows))

    def test_broken_energy_balance_is_detected(self):
        rows = copy.deepcopy(self.rows); rows[0]["pv_generation_kwh"] = "1000"
        self.assertIn("energy_balance", self.codes(rows))

    def test_125_kwh_per_quarter_hour_equals_500_kw(self):
        from decimal import Decimal
        self.assertEqual(Decimal("125") / Decimal("0.25"), Decimal("500"))

    def test_storage_boundary_is_explicitly_unsupported(self):
        self.assertIn("unsupported_boundary", self.codes(meta=dict(self.meta, storage_present=True)))


if __name__ == "__main__":
    unittest.main()
