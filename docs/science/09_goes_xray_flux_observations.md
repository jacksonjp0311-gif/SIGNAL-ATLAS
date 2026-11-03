# NOAA GOES soft X-ray observations

Signal Atlas v1.0 preserves 716 raw rows from NOAA SWPC's [primary GOES six-hour X-ray product](https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json), timestamped 2026-11-03T00:42:00Z through 2026-11-03T06:39:00Z. Capture time: 2026-11-03T06:43:15Z. Raw-response SHA-256 and HTTP metadata are stored with the bytes.

The payload includes the 0.05-0.4nm and 0.1-0.8nm energy labels. The paired JSON and CSV contain 358 exact (time_tag, satellite) matches. Provider flux, observed_flux, correction, and contamination fields remain separate, including the original field spelling.

## Limits

- A rolling six-hour capture is not a long-term archive.
- Pairing is exact; no interpolation, smoothing, time shifting, or cross-instrument joining is done.
- Timestamp coincidence with solar wind, magnetic field, F10.7, or Kp is not proof of shared cause or forecasting value.
- Quality flags are preserved, not independently calibrated.

## Rebuild

~~~powershell
python tools/build_v10.py
python tools/atlas_search_v10.py "GOES x-ray flux" --kind dataset
python tools/validate_v10.py
~~~

Obtain a new rolling capture only with the explicit dated fetch tool; do not overwrite frozen evidence. See the [registry](../../data/dataset_registry.json), [paired CSV](../../data/datasets/noaa_goes_primary_xrays_6hour_paired_2026-11-03.csv), and source provenance.
