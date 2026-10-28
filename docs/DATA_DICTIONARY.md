# Data dictionary

Author: Csott Károly Péter

## Interval CSV

Each row describes one interval in one synthetic meter series. All energy channels share a common AC boundary. Intervals include their start and exclude their end. Storage is absent from this baseline.

| Field | Type / unit | Meaning |
| --- | --- | --- |
| `site_id` | text | Non-personal series identifier; synthetic in the example |
| `meter_id` | text | Meter/channel identifier |
| `interval_start_utc` | ISO 8601, UTC | Inclusive interval start, explicit `+00:00` or `Z` |
| `interval_end_utc` | ISO 8601, UTC | Exclusive interval end |
| `interval_start_local` | ISO 8601 with offset | Same instant in the named local timezone |
| `interval_minutes` | minutes | 15 in the supported schema |
| `site_load_kwh` | kWh per interval | Gross site electricity use at the stated boundary |
| `pv_generation_kwh` | kWh per interval | PV AC energy delivered within the boundary |
| `pv_self_consumed_kwh` | kWh per interval | PV energy used by site loads; synthetic construction in the sample |
| `grid_import_kwh` | kWh per interval | Directional energy entering the site from the grid, non-negative |
| `grid_export_kwh` | kWh per interval | Directional energy leaving the site for the grid, non-negative |
| `avg_site_load_kw` | kW | `site_load_kwh /0.25h`, an interval average |
| `avg_grid_import_kw` | kW | `grid_import_kwh /0.25h`, an interval average |
| `quality_flag` | text | Provenance/quality label; all sample rows are synthetic |

## File metadata

`timezone` is an IANA name. `period_start_utc` and `period_end_utc_exclusive` define the expected coverage independently of the rows received. `quantity_basis` is `interval_energy`. `energy_unit` is `kWh`; `power_unit` is `kW`. `storage_present` is false for this schema. A different boundary needs a different documented balance equation.

## Project inputs beyond the CSV

| Input | Unit / basis | Evidence required |
| --- | --- | --- |
| Existing and proposed PV DC nameplate | kWp DC | Equipment/design schedule; keep existing and proposed separate |
| Inverter rating and clipping limit | kW AC | Datasheet and design assumptions |
| PV yield series | kWh per interval | Model/version, weather source, timezone and loss assumptions |
| Tilt and azimuth | degrees, convention stated | Survey/design; clarify azimuth convention |
| Shading, losses and degradation | fraction or % explicitly | Survey, model or warranty source |
| Grid export limit | kW AC | Applicable connection agreement and operating restrictions |
| BESS nominal energy | kWh, AC/DC boundary | Datasheet/rating conditions |
| BESS usable energy | kWh, boundary and age | SOC limits and warranted conditions |
| Charge / discharge power | kW, AC/DC boundary | Continuous and short-term limits separately |
| SOC minimum / maximum, DoD | fraction in JSON, % in a source if labelled | Operating policy and warranty; no double application to usable ratings |
| Charge / discharge efficiency | fraction, one-way | Define measurement boundary and load dependence |
| Round-trip efficiency | fraction | Define boundary and included auxiliaries |
| Auxiliary demand | kW or kWh by interval | Equipment and environmental assumptions |
| Degradation and throughput | stated time/cycle/energy basis | Warranty and dispatch assumptions |
| Import commodity charge | currency/kWh, effective period | Applicable tariff/contract schedule |
| RHD / network charges | currency/kWh, currency/kW or fixed basis | Invoice and applicable network schedule; separate components |
| Demand / contracted-power charges | currency/kW per billing period | Demand window and billing rule |
| Export settlement | currency/kWh and settlement basis | Agreement; keep separate from avoided import price |
| Currency and VAT basis | currency code; inclusive/exclusive | Contract/invoice convention |
| EPC delivery scope | text | Scope, interfaces, exclusions, tests and risk allocation |
| ESCO baseline and adjustments | text plus baseline period | Agreed M&V method and responsibilities |
| PPA delivery and settlement point | text | Metering boundary, eligible delivery, offtake and settlement |
| Contract duration / indexation | years and explicit formula | Commercial assumptions with source/date |
| Credit, security and termination | text | Terms assessed by authorized commercial/financing parties |

Blank means missing or not supplied, not zero. Preserve original values and source units before a documented conversion. Source files may contain confidential material; the public examples do not.
