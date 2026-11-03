# Signal Atlas v0.7 release audit

## Scope

This release checks the internal consistency of the v0.7 collection and preserves the complete v0.6 package as its base. It focuses on data coverage, joining, catalog integration, local reproducibility, and navigation.

## Collected data and transformation

- NOAA SWPC daily geomagnetic product, issued 0330 UT on 2026-11-03: 30 daily labels are retained. The final row is partial.
- Existing NOAA F10.7 snapshot: 30 dated values from the v0.6 package.
- Normalized geomagnetic data: each row preserves the middle-latitude, high-latitude, and estimated planetary values. Source sentinel -1 becomes JSON null.
- Joined data: 29 complete date matches from 2026-10-05 through 2026-11-02. No interpolation or timezone shift is applied.
- Daily Kp summaries: maximum and arithmetic mean of the eight estimated planetary Kp values. All original interval values remain in the joined output.

The 2026-11-03 partial row remains visible in the source snapshot and normalized output; it is not used as a complete daily comparison.

## Reproduction

The builder uses only the packaged text and JSON inputs and does not make a network request:

    python -B tools/build_space_weather_v07.py

The release tool rebuilds the collection, runs the validators and focused tests, writes the SHA-256 manifest, and creates a ZIP whose CRC entries are checked:

    python -B tools/release.py --version v0.7 --output PATH_TO_OUTPUT_ZIP

## Checks run

| Check | Result |
|---|---|
| Focused parser, incomplete-row, join, chart-label, registry-type, and idempotence tests | 7 passed |
| General package validator | PASS; 143 source cards, 76 claims, 20 research notes, 18 geopolitical profiles, 29 SVG diagrams |
| Science/document validator | PASS; 26 publication records, 4 local PDFs, 30 document records |
| v0.7 integration validator | PASS; 4 registry datasets, 30 geomagnetic rows, 29 joined rows |
| Inherited-file comparison | PASS; 236 v0.6 manifest entries checked, zero unexpected changes |

## Limits

- The observed overlap is short and suited to exploration, not a general physical conclusion, forecast, or causal attribution.
- F10.7 time tags in the retained v0.6 JSON do not include a timezone suffix. The join uses the supplied date label without shifting it.
- Planetary Kp values are estimated, and the daily maximum compresses eight three-hour values into one summary.
- NOAA rolling products can change. The dated files in this release preserve the exact local inputs used for this result.
- The work prioritizes collection and coherence. It does not include independent rights or citation review, and it does not claim that the Atlas contains every relevant source or measurement.
- Tests establish parser, integration, file-hash, link, and package consistency. They do not independently validate NOAA's scientific instruments or establish a causal solar-terrestrial relationship.

No GitHub publication was performed.
