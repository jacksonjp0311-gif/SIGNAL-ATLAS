# 28. Pairing solar-wind measurements without hiding the time axis

## Learning goal

Use NOAA's source and active flags to compile one-minute plasma and magnetic-field data while preserving spacecraft identity, missing values, timestamp alignment, and partial coverage.

## Read and inspect

1. Open the [Solar-wind Explorer](../site/solar_wind.html).
2. Compare the raw plasma and magnetometer JSON files. Find `time_tag`, `source`, and `active`.
3. Open the [v0.8 collection guide](../docs/research/DATA_COLLECTION_GUIDE_v08.md) and the [science explanation](../docs/science/09_solar_wind_observations.md).
4. Locate the active spacecraft change. Confirm that the same source is paired across both data families.

## Apply

For the first daily summary row, calculate paired coverage as `matched_active_minutes / 1440`. Explain why it is labeled partial. Then compare the table's median proton speed with its minimum GSM Bz. Use the source row count and the full daily estimated Kp context, but keep the different time coverage visible.

## Check

- A pair is valid only when both exact `time_tag` and `source` values match and both source rows have `active: true`.
- The other spacecraft records remain in the raw inputs and do not disappear from the archive.
- No missing reading is filled, no timestamp is rounded, and no propagation delay is guessed.
- A one-minute upstream value and a daily Kp maximum do not establish a same-time cause-and-effect relationship.

## Explain one limitation

Describe what additional data and time treatment would be needed to test whether an upstream field or plasma change is associated with a later geomagnetic response. This sample alone is too short and incomplete for that conclusion.
