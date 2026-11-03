# Space-weather observations: F10.7 and estimated planetary Kp

## What is in this collection

This v0.7 module brings two already collected NOAA SWPC data streams into one dated research path:

- F10.7 radio flux at 10.7 cm (2800 MHz), reported in solar flux units (sfu).
- Estimated planetary Kp, a geomagnetic activity index with eight three-hour values per daily row.

The 30-day geomagnetic snapshot is kept as the original NOAA text file and as normalized JSON. The F10.7 values are retained from the existing v0.6 snapshot. The derived table joins values by the date label, preserves each three-hour Kp value, and adds daily Kp mean and maximum fields for browsing.

## Read the files

- Browse the [Data Explorer](../../site/datasets.html) for the chart, searchable table, and downloads.
- Open the [dataset registry](../../data/dataset_registry.json) to see observed, derived, and synthetic series together.
- Read the [AI research packet](../../data/packets/examples/space-weather-noaa-2026-11-03.v0.7.packet.json) for a compact machine-readable summary.
- Follow the [guided data lesson](../../courses/27_space_weather_data_join.md).

## How the join works

The join key is the first ten characters of each F10.7 time tag, matched to the daily date printed in the geomagnetic product. No timezone conversion or time shift is applied. A date match gives a useful daily comparison, but it does not establish that both values are simultaneous observations.

Only rows with all eight estimated planetary Kp values and an F10.7 value enter the joined table. NOAA marks unavailable geomagnetic values with -1; the normalized file stores those as null. In this snapshot, the 2026-11-03 row is partial: it remains visible in the raw and normalized files but is not treated as a complete daily summary.

The daily Kp maximum is the maximum of eight estimated three-hour values. The daily Kp mean is their arithmetic mean. These are convenient summaries added by the Atlas; the original values remain available beside them.

## What can be learned

This is a small observational window for exploring two different signals in a shared time period. Learners can compare the F10.7 series with daily geomagnetic activity, locate days when estimated Kp reaches 5 or more, and inspect how the collection handles missing values and date alignment.

Keep the series distinct. F10.7 is solar radio flux; Kp describes geomagnetic disturbance. A shared date, a similar rise, or a chart does not show that F10.7 caused a Kp change. The 29-day overlap is too short for a forecast or a general solar-terrestrial relationship claim.

## Source products

- [NOAA SWPC F10.7 30-day JSON feed](https://services.swpc.noaa.gov/products/10cm-flux-30-day.json)
- [NOAA SWPC daily geomagnetic indices text feed](https://services.swpc.noaa.gov/text/daily-geomagnetic-indices.txt)
- [NOAA SWPC description of F10.7 cm radio emissions](https://www.spaceweather.gov/phenomena/f107-cm-radio-emissions)
- [NOAA SWPC planetary K-index description](https://www.spaceweather.gov/products/planetary-k-index)

## Rebuild offline

From the repository root, run:

    python tools/build_space_weather_v07.py

The build uses only the bundled text and JSON snapshots. It does not fetch current data. The raw inputs, generated JSON and CSV, chart, registry, provenance records, and packet stay inside the versioned package.
