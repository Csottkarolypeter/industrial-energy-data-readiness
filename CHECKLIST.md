# Industrial energy data readiness checklist

Author: Csott Károly Péter

## Measurement boundary and provenance

- [ ] Agree site, meter, point of connection and AC/DC boundary.
- [ ] Obtain permission to use the data for this assessment. Keep client files outside the public repository.
- [ ] Preserve the original export, filename, retrieval date, owner and file hash.
- [ ] Document interval energy versus cumulative registers, import/export signs and CT/PT multipliers.
- [ ] Obtain separate gross-load, PV and import/export channels where relevant. Record missing channels explicitly.

## Time series

- [ ] Confirm 15-minute duration, start/end convention, UTC offsets and the named local timezone.
- [ ] Check the exact requested period, including leading and trailing gaps.
- [ ] Detect repeated UTC instants without deleting legitimate repeated local clocks at a DST transition.
- [ ] Keep missing values, zeros and estimated/substituted values distinct.
- [ ] Investigate negative values, non-finite values and balance failures against the original export.
- [ ] Surface high interval-average demand. Check meter limits, invoice demand windows and operational explanations before treating a peak as an error.
- [ ] Review seasonal coverage, shutdowns, shift patterns, planned electrification and HVAC demand changes.

## PV

- [ ] Separate DC kWp, inverter AC kW and generated kWh.
- [ ] Identify the yield/weather source, period, orientation, shading, loss and degradation assumptions.
- [ ] Record export limits, connection status and curtailment. Align PV and load timestamps.
- [ ] Keep proposed PV generation separate from measured existing generation.

## BESS

- [ ] Separate nominal kWh, usable kWh and AC charge/discharge kW.
- [ ] Document SOC limits/DoD, efficiency boundary, auxiliary consumption, temperature and warranty limits.
- [ ] Apply losses once. Separate one-way and round-trip efficiency.
- [ ] State whether the objective is peak management, self-consumption, tariff shifting, backup or another service.
- [ ] Obtain a justified dispatch model before claiming battery size, savings, throughput or lifetime.

## Tariffs and commercial screening

- [ ] Obtain current invoices and contract schedules through an authorized private channel.
- [ ] Split commodity, RHD/network, demand, fixed, tax and export components with units and effective dates.
- [ ] Confirm which charges can actually change under the proposed operating model.
- [ ] Record currency, escalation, VAT basis and the source of every price assumption.
- [ ] For EPC: define scope, interface responsibilities, commissioning, performance tests and change control.
- [ ] For ESCO: define baseline, adjustments, savings verification and allocation of performance risk.
- [ ] For PPA: define delivery/settlement point, term, indexation, offtake and credit assumptions, curtailment and termination.

## Handover

- [ ] List missing inputs and their owners. Do not replace them with undocumented defaults.
- [ ] Separate measured data, derived values and assumptions.
- [ ] Keep a versioned record of changes and unresolved issues.
- [ ] State the permitted use of the resulting assessment and the next decision it can support.
