# Industrial Energy Data Readiness Toolkit

**Author: Csott Károly Péter**  
ASCII name: Csott Karoly Peter

Prepare a traceable input package before screening an industrial solar PV, battery storage or energy-efficiency project. This toolkit combines a client data request, a field dictionary, a practical checklist and a read-only Python validator. All included examples are synthetic.

The commercial question is specific: which inputs are measured, which are assumptions, and which remain missing before a project can be assessed? A clean CSV is one part of that answer. Tariffs, network constraints, equipment limits and contractual responsibilities need their own evidence.

## Start here

1. Use [the checklist](CHECKLIST.md) to agree the assessment boundary.
2. Complete `templates/client_data_request.csv` or the accompanying Excel template with the data owner. Leave unavailable values blank and identify the missing source.
3. Map fields with [the dictionary](docs/DATA_DICTIONARY.md). Keep original exports unchanged.
4. Run the example and review the validation output using [the short guide](docs/USAGE.md).
5. Record unresolved items before passing inputs to an engineer, modeller, EPC contractor or financing party.

## Files

| File | Purpose |
| --- | --- |
| `CHECKLIST.md` | Measurement, technology and commercial input checks |
| `templates/client_data_request.csv` | Empty client data request with units and evidence requirements |
| `templates/client_data_request.xlsx` | Readable version of the request and field dictionary |
| `templates/project_assumptions.json` | Empty PV/BESS/tariff/contract assumption structure |
| `docs/DATA_DICTIONARY.md` | Definitions and measurement boundaries |
| `docs/USAGE.md` | Commands and interpretation |
| `docs/SOURCES.md` | Primary references and access date |
| `examples/synthetic_meter_2026-10-25.csv` | One synthetic 25-hour local day, 100 intervals |
| `examples/synthetic_meter_2026-10-25.metadata.json` | Units, timezone and exact expected period |
| `tools/validate_intervals.py` | Read-only checks; JSON report on standard output |
| `tools/generate_synthetic.py` | Reproducible synthetic example generator |
| `tests/test_readiness.py` | Tests for DST, missing data, units and energy balances |

## Keep kWh, kW and kWp separate

- **kWh** is interval energy. State whether a column contains interval energy or a cumulative meter register.
- **kW** is power. For an interval-energy value, average power is `energy_kwh / duration_hours`. For example, 125 kWh over 15 minutes is 500 kW on average. This does not establish the instantaneous maximum.
- **kWp** identifies nominal PV DC nameplate power under the specified reference conditions. It is neither generated kWh nor the inverter's AC limit.

The supplied schema uses 15-minute interval energy in kWh and average AC power in kW. It does not convert cumulative registers or resample a different interval length automatically.

## Time and missing intervals

Retain UTC timestamps, the named local timezone and explicit local UTC offsets. Use interval starts and an exclusive interval end. Compare instants in UTC before checking gaps or duplicates.

The synthetic example uses `Europe/Budapest`. On 25 October 2026, the local day contains 100 quarter-hour intervals. Two entries can legitimately share the same local clock reading with different UTC offsets. The validator checks the expected period, including missing first and last intervals, rather than assuming every local day has 96 rows.

## Consumption, PV and export

Record the measurement location and sign convention. Grid import alone does not describe gross site consumption when generation or storage operates behind the meter.

For the supplied common-AC, no-storage baseline:

`grid_import_kwh + pv_generation_kwh = site_load_kwh + grid_export_kwh`

The example assumes constant average load and PV within each interval. Its self-consumption calculation is part of that synthetic construction. In real measurements, `min(interval_load, interval_PV)` can overestimate coincidence within the interval. Directional import and export can both be positive during one quarter-hour if the instantaneous flow reverses. Keep measured channels and their aggregation rules.

PV screening also needs the weather/yield source, location, DC size, inverter AC size, orientation, shading, losses, degradation, export limit and curtailment assumptions. The example's mathematical PV shape is not a weather-based yield forecast.

## BESS inputs

Collect nominal and usable energy separately, charge and discharge power limits, AC/DC boundaries, operating SOC range, depth of discharge (DoD), efficiency definitions, auxiliaries, degradation and warranty limits.

Illustrative arithmetic only: 500 kWh nominal with an allowed SOC range of 10–90% gives a 400 kWh DC operating window. At an assumed 95% discharge efficiency, this corresponds to 380 kWh AC before other losses. A 200 kW AC discharge limit would give an ideal energy-limited duration of 1.9 hours at that power. Project constraints may reduce it. Do not apply DoD again to a rating already defined as usable energy.

State whether efficiency is one-way or round-trip. Two hypothetical 95% one-way efficiencies produce 90.25% round-trip efficiency. A quoted AC-to-AC round-trip value already includes losses within its stated boundary; avoid applying the same loss twice.

The included validator checks a no-storage baseline. It does not simulate BESS dispatch, calculate an optimum capacity or validate a storage energy balance.

## Tariffs, RHD and contract inputs

Keep commodity energy prices, grid/network use charges (RHD in Hungarian terminology), demand or contracted-power charges, fixed charges, export settlement, taxes and VAT treatment separate. Record currency, units, effective dates, time bands and the evidence source for every component. An avoided imported kWh does not automatically avoid every invoice charge.

For ESCO or PPA screening, collect the baseline and adjustment method, metering and settlement boundary, savings or production obligations, ownership, offtake profile, term, indexation, credit assumptions, guarantees, curtailment allocation and termination provisions. These are input requirements, not a commitment that a project qualifies for financing.

## Run the checks

Python 3.9 or later is required, together with an available IANA timezone database. If the operating system has no timezone data, install the maintained `tzdata` package in your own environment.

```bash
python3 tools/validate_intervals.py \
  examples/synthetic_meter_2026-10-25.csv \
  examples/synthetic_meter_2026-10-25.metadata.json

python3 -m unittest discover -s tests -v
```

Exit code 0 means the documented file-consistency checks passed. Exit code 2 means that issues need review. A pass does not validate meter calibration, seasonal representativeness, tariff applicability, equipment design or project economics. No input file is modified by the validator.

## Author and scope

Csott Károly Péter works in senior B2B energy sales, business development, PV, BESS, HVAC, energy project coordination and commercial project screening. Energy Management Network is an independent professional concept, not a registered company or a statement of current employment.

This material was prepared with generative AI assistance. The examples, code and stated assumptions are supplied for transparent technical review. No customer load profile, partner list, contractual price or internal financial model is included.

See [the sources](docs/SOURCES.md) and [the MIT licence](LICENSE).
