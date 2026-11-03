# Public measurement data used in Signal Atlas

## NOAA F10.7 solar-radio-flux 30-day sample

- **Source URL:** https://services.swpc.noaa.gov/products/10cm-flux-30-day.json
- **Acquisition:** NOAA SWPC public JSON endpoint, values visible during the 2026-11-02 research pass; transcribed into the local subset.
- **Actual local bytes:** `noaa_f107_30day_2026-11-02.json` (30 rows, not entire service archive).
- **SHA-256 of stored excerpt:** `30553983bd2a9156d2864083c3166e46f75a10f1632d3ad98052b8585f27636e`
- **Units:** solar flux units (sfu), 10.7-cm/2800-MHz solar emission; provenance: NOAA SWPC, originating measurements by Canada's NRC/NRCan network per NOAA documentation.
- **Redistribution assessment:** numerical measurement excerpt is included with explicit attribution; do not assume every upstream image, report, or derived dataset is unrestricted.
- **Source ID:** SRC-116.
- **Time bounds:** 2026-10-04 to 2026-11-02 at 20:00 as presented by endpoint; timezone not explicitly supplied in returned time tags.
- **Reproduction:** `python experiments/noaa_f107_lab.py` runs entirely offline against bundled excerpt.
- **Caution:** this rolling JSON feed changes; rerunning a remote fetch later will return a different window. This frozen file is a versioned observation excerpt, not a complete scientific database.

## v0.7 NOAA space-weather collection

- **F10.7 input:** the 30-point snapshot above remains the v0.6 source file; source record SRC-116 points to the live NOAA SWPC feed.
- **Geomagnetic input:** noaa_daily_geomagnetic_2026-11-03.txt is the dated NOAA SWPC text snapshot, issued at 0330 UT on 2026-11-03. Source record SRC-144 points to the feed.
- **Normalized rows:** noaa_daily_geomagnetic_2026-11-03.json retains all 30 daily labels and represents the source sentinel -1 as null. The 2026-11-03 row is partial.
- **Derived comparison:** noaa_f107_kp_daily_join_2026-11-03.json and its CSV companion use the date label only. They retain eight estimated planetary Kp values per complete day and add daily mean and maximum fields.
- **Viewer and machine packet:** open the [Data Explorer](../../site/datasets.html), [dataset registry](../dataset_registry.json), or [AI packet](../packets/examples/space-weather-noaa-2026-11-03.v0.7.packet.json).
- **Rebuild:** run python tools/build_space_weather_v07.py from the repository root. The build reads bundled inputs and makes no network request.
- **Interpretation:** the joined series is a short descriptive window. Daily date labels do not establish simultaneous measurements, and the comparison does not establish causation.

The registry also lists the v0.6 frequency-stability teaching series as synthetic. It is not a set of instrument measurements.

## v0.8 NOAA RTSW snapshots

- Raw plasma: `data/datasets/noaa_rtsw_wind_1m_2026-11-03.json` (3247 records).
- Raw magnetic field: `data/datasets/noaa_rtsw_mag_1m_2026-11-03.json` (3432 records).
- Source-aware paired view: 1031 rows from matching active `time_tag` and `source` values.
- The daily context spans 2026-11-02 through 2026-11-03; all buckets are partial and carry their own coverage counts.
- Raw records and upstream metadata are retained in full; rebuild the derived view offline with `python tools/build_rtsw_v08.py`.
