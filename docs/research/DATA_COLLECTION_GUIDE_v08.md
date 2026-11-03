# v0.8 NOAA solar-wind data collection guide

## What was captured

Two frozen NOAA SWPC JSON inputs retain the one-minute solar-wind plasma and magnetic-field values available during the 2026-11-03 capture. Raw inputs include records from all spacecraft in the service response. The common snapshot metadata file records retrieval time, endpoint, row count, time-tag bounds, and SHA-256 for each input.

## How the local collection is built

1. Keep raw endpoint files unchanged.
2. Create separate `active: true` files because NOAA's active flag identifies the spacecraft currently selected by forecasters for that measurement type.
3. Pair plasma and magnetometer rows only when both `time_tag` and `source` are exactly equal. Do not cross-pair spacecraft or silently round timestamps.
4. Preserve quality fields and missing values. No undocumented quality threshold is applied.
5. Group paired values by the source time-tag date for a coverage-aware daily view. Mark every incomplete UTC day as partial.
6. Display complete daily estimated Kp only as day-level context. Apply no propagation delay and make no causal claim.

## Reproduce offline

The acquisition step is separate: `python -B tools/fetch_rtsw_snapshot_v08.py` fetches NOAA's current rolling files and refuses to overwrite an existing snapshot unless `--force` is supplied. Do not use it when reproducing this release.

The builder and checks are offline and use the dated files already in the package:

```text
python -B tools/build_rtsw_v08.py
python -B -m unittest discover -s tests -p "test_v08_solar_wind.py"
python -B tools/validate_v08.py
```

The full package release command also runs the general and science/document validators and writes a manifest before creating the ZIP.
