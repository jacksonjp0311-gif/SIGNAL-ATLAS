# SIGNAL ATLAS v1.0 — Release audit

## Integrity and lineage

- Parent release: v0.8; retained manifest SHA-256: 622efefdef3e3dafd7dfa2f9f02c0040097bfb08a0c25ae234232f591dfe8dee.
- Parent paths: 278; required unchanged or explicitly modified.
- Modified parent paths and new files are enumerated in data/release_v10_lineage.json.
- Evergreen logo is verified against the parent manifest.
- Release packaging checks ZIP CRC, complete manifest membership, and SHA-256 for every file.

## Data checks

- Catalog: 150 sources, 82 claims, 21 research notes, and 10 registered datasets.
- GOES capture: 716 raw rows, 2026-11-03T00:42:00Z to 2026-11-03T06:39:00Z; captured 2026-11-03T06:43:15Z; raw SHA-256 e8e289be79d1734bb2e5cca7613d4924c4a45e3a77dcf61897782b984c47e23f.
- Derived channel table: 358 exact timestamp/satellite pairs; validator recomputes matches and duplicate/unmatched handling.
- Search input hashes and packet digest are recomputed by validation.

## Release checks

The release runs tools/validate.py, tools/validate_science.py, tools/validate_v10.py, unittest discover -s tests -p test_v10_atlas.py, then tools/release.py --version v1.0 --output <outputs/SIGNAL-ATLAS-v1.0.zip>. The packaging step verifies each ZIP member against the file manifest.

## Limits

This checks internal consistency, reproducible local derivation, v0.8 inheritance, and package integrity. It does not establish complete scientific or archive coverage, independent truth assessment of every source, or end-user utility through a user study. GOES records are a six-hour capture; no cross-instrument physical attribution or forecast validation is claimed. Search is not PDF full-text search or semantic truth scoring.
