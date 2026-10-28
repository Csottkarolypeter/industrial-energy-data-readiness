# Short usage guide

Author: Csott Károly Péter

## Run the supplied synthetic day

From the repository directory:

```bash
python3 tools/validate_intervals.py examples/synthetic_meter_2026-10-25.csv examples/synthetic_meter_2026-10-25.metadata.json
```

Expected coverage: 100 intervals for the 25-hour local day in Europe/Budapest. Read `issues`, `missing_intervals` and `duplicate_intervals` before interpreting the reported high interval averages.

## Generate another teaching example

```bash
python3 tools/generate_synthetic.py --start-date 2026-10-19 --days 7 --output examples/another_synthetic_week.csv
python3 tools/validate_intervals.py examples/another_synthetic_week.csv examples/another_synthetic_week.metadata.json
```

The generator creates both CSV and metadata. It uses an explicit mathematical load/PV pattern; changing the dates does not turn it into a calibrated forecast. Keep generated files separate from original meter exports.

## Adapt a real export privately

1. Preserve the original file and its units, timezone, register semantics and meter multiplier.
2. Establish the measurement boundary and convert cumulative registers only with a documented reset/rollover policy.
3. Map a supported interval-energy series to the schema. Keep estimated readings flagged. Do not fill missing channels with zero.
4. Set the expected period from the requested assessment window, not the first and last rows that happen to be present.
5. Review failures with the data owner. Record every correction and keep the original value.
6. Review tariffs, equipment and contract inputs separately using the checklist.

For a storage-equipped site, extend the balance and metering scheme with charge/discharge and loss terms in a separately reviewed model. The supplied checker intentionally accepts the documented no-storage schema only.

## Interpret the result

A file-consistency pass permits the next review step for this schema. It provides no evidence of meter calibration, physical feasibility, annual yield, savings, grid approval or financing approval. A large interval average is a review item; the script never deletes or caps it.

Run the regression tests with `python3 -m unittest discover -s tests -v`. Test data include short and long DST days, gaps at both period boundaries, repeated UTC instants, naive timestamps, unit errors, non-finite values and broken balances.
