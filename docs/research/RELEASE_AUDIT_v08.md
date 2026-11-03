# Signal Atlas v0.8 release audit

## Collection and method

- The package retains the exact NOAA SWPC one-minute plasma and magnetic-field response bytes plus source URLs, capture interval, time-tag bounds, row counts, and SHA-256 digests.
- The raw records include all returned spacecraft. Active-selected views include records only when `active` is the JSON boolean `true`.
- Plasma and magnetic-field rows are paired only on identical `time_tag` and `source`; no timestamp rounding, interpolation, or cross-spacecraft pairing is used.
- Source values, missing values, spacecraft identity, and reported quality fields remain inspectable. The builder applies no undocumented quality threshold.
- Daily summaries count paired records against 1,440 UTC minutes. The two bins are partial (740 and 291 matched minutes). Estimated Kp appears only when its separate source row contains all eight three-hour intervals.
- The builder and release checks consume frozen package inputs and make no network request. Fetching a future rolling sample is a separate, explicitly documented action.

## Checks performed

- `python -B -m py_compile tools/build_rtsw_v08.py tools/fetch_rtsw_snapshot_v08.py tools/validate_v08.py tests/test_v08_solar_wind.py` — passed.
- `python -B -m unittest discover -s tests -p "test_v08_solar_wind.py"` — 6 tests passed. Cases cover exact time/source pairing, active flag handling, duplicate keys, incomplete daily Kp, frozen-input hash mismatch, packet checksum, and deterministic offline rebuilding.
- `python -B tools/validate.py` — passed: 145 sources, 76 claims, 20 research notes, 18 geopolitical profiles, and 30 SVGs; local references and core structure resolved.
- `python -B tools/validate_science.py` — passed: 26 publication records, 4 local PDFs, and 30 document records.
- `python -B tools/validate_v08.py` — passed: raw plasma 3,247 records, raw magnetometer 3,432, active exact pairs 1,031, two partial daily summaries, 8 registry datasets, 255 inherited v0.7 manifest paths, and zero unexpected inherited-file changes.
- `python -B tools/release.py --version v0.8 --output PATH_TO_OUTPUT_ZIP` — runs the checks above, writes `MANIFEST.sha256`, checks ZIP CRCs, and compares every packaged file byte-for-byte against the manifest.

## Version ancestry and full-package preservation

The actual v0.5, v0.6, v0.7, and v0.8 ZIPs were compared, then the v0.8 archive was extracted and checked again.

- The original v0.5 archive SHA-256 matches the value recorded by the v0.6 lineage file. All 208 v0.5 paths and their recorded original hashes match the ZIP, and all 208 paths are present in v0.6.
- The 24 v0.5 files with revised contents in v0.6 are exactly the v0.6 declared edit set; their pre-edit hashes remain in the lineage record.
- All 237 v0.6 archive paths are present in v0.7. Its 15 changed paths, including the regenerated manifest, are within the v0.7 integration allowlist.
- All 256 v0.7 archive paths are present in v0.8. Its 17 changed paths, including the regenerated manifest, are within the v0.8 integration allowlist.
- The extracted v0.8 manifest contains 278 file entries; every extracted file hash matches and there are no missing or unlisted files.

The reproducibility check uses the frozen snapshots included in the package. `python -B tools/fetch_rtsw_snapshot_v08.py` retrieves the current rolling NOAA files and will not reproduce this dated capture.

## Interpretation limits

- The capture is a roughly one-day rolling feed snapshot, not a long historical solar-wind series.
- The active spacecraft changes during the sample. The source field is retained; selected plasma and field streams are paired only where source and time tags match exactly.
- The two UTC-day groups are incomplete and include gaps. Their descriptive statistics summarize sampled minutes only.
- Spacecraft measurements are upstream of Earth. The package applies no propagation delay; daily Kp is separate context, not a causal alignment.
- These checks establish byte/hash consistency, deterministic transformations, selected data joins, inherited-file integrity, and archive packaging. They do not establish forecast skill, physical causation, instrument validation, or scientific completeness.
