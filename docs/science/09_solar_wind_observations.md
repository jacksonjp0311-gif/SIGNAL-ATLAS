# Solar-wind observations and time alignment

## What the measurements describe

The solar wind is a stream of plasma and embedded magnetic field flowing outward from the Sun. NOAA SWPC receives in-situ measurements from spacecraft upstream of Earth and uses them to monitor disturbances that may affect the geospace environment. The SWPC display identifies the spacecraft selected as active for each measurement stream; that selection can change during an observation window. [NOAA SWPC Solar Wind](https://www.spaceweather.gov/products/solar-wind)

The v0.8 collection uses two NOAA SWPC one-minute JSON feeds:

- `rtsw_wind_1m.json`: proton speed, density, temperature, spacecraft source, active flag, and reported quality fields.
- `rtsw_mag_1m.json`: interplanetary magnetic-field magnitude and GSM components, spacecraft source, active flag, and reported quality fields.

NOAA's product change notice defines the new `source` and `active` metadata and the replacement field names. NOAA's SWFO instrument documentation describes solar-wind plasma measurements in km/s, cm⁻³, and K, and magnetometer measurements in nT. [NOAA SWPC product notice](https://www.weather.gov/media/notification/pdf_2026/scn26-21_Data_Format_Changes_Impacting_SWPC_Products.pdf), [NOAA NCEI SWFO instruments](https://www.ncei.noaa.gov/products/space-weather/swfo)

## What v0.8 preserves and derives

The two fetched JSON files are kept as dated raw snapshots, including the records from spacecraft that were not selected as active. Separate active-selected files preserve only records whose JSON boolean is `true`. The paired series requires exact equality of both `time_tag` and `source`, so observations from different spacecraft are never silently combined. All reported quality values and nulls are retained; v0.8 adds no undocumented quality threshold.

The capture spans the rolling 24-hour endpoint window from 2026-11-02 into 2026-11-03. Its paired minute records are grouped into UTC-date summaries with a count out of 1,440 possible minutes. Both dates are partial. A complete daily estimated planetary Kp summary is shown only for the date with all eight three-hour intervals; it remains separate context because Kp is a different data product and cadence.

The source tags are preserved as supplied. The collection does not shift timestamps, interpolate gaps, or apply a solar-wind propagation delay. The field `bz_gsm` is the north/south magnetic-field component in the GSM coordinate system; negative values indicate southward orientation. NOAA's display marks Bz thresholds in nT. [NOAA SWPC Solar Wind](https://www.spaceweather.gov/products/solar-wind)

## How to use the collection

Open the [Solar-wind Explorer](../../site/solar_wind.html) for the chart, source-switch indicator, daily coverage table, and direct links to raw and derived files. The [dataset registry](../../data/dataset_registry.json) separates observed inputs from derived products. The [AI-readable packet](../../data/packets/examples/solar-wind-noaa-2026-11-03.v0.8.packet.json) records its inputs, joins, hashes, and interpretation limits.

## Limits

- The release contains a rolling one-day snapshot, not a long historical record.
- The active spacecraft changes during the window; source identity is part of the join key.
- The measurement point is upstream of Earth. Direct comparison with geomagnetic indices requires modeling and a propagation-time treatment; v0.8 does neither.
- The available daily bins cover only a fraction of each UTC day. Summary values are descriptive and retain coverage counts.
- Kp is estimated and summarizes three-hour intervals. A daily Kp value is not a one-minute measurement.
- This release supports navigation and exploration. It does not demonstrate a causal relationship, storm prediction skill, or instrument validation.
