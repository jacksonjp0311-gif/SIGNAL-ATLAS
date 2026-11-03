# Signal Atlas v0.6 release audit

**Date:** 2026-11-02  
**Status:** validated local release package; not published to GitHub

## Baseline and inheritance

The repository was built from the complete original `SIGNAL-ATLAS-v0.5.zip`, not the later 12-file README patch archive. The original ZIP SHA-256 is `B7FDA71A48C858CE41A8D44ACA9ACD999D354EFB026A0E191951EFC9198DBAEE`. Its 208 distinct file paths are recorded in `data/release_v06_lineage.json`; the v0.6 validator verifies that each path remains present and that files outside the declared edit set retain their original hashes. The prior v0.5 NOAA observation, query evaluation receipt, example packet, and audit are retained.

The evergreen logo and roadmap artwork are inherited from the accepted prior update package and are present as `assets/signal_atlas_logo_header.png` and `assets/signal_atlas_roadmap_to_release.png`. The logo leads the README; the version-specific v0.5 hero remains as a historical asset.

## Release inventory

- **Sources:** 142 (8 added, `SRC-136`–`SRC-143`)
- **Claims:** 76 (7 added, `C-070`–`C-076`)
- **Publications / technical records:** 26 (3 added, `PUB-024`–`PUB-026`)
- **World profiles:** 18 (Canada and Australia records linked to new attributed histories)
- **Research notes:** 20 (2 new editorial-first-pass notes)
- **Lessons:** 26 (2 new lessons)
- **SVG graphics:** 28 (3 new; all parse as SVG and include accessible title/description)
- **Third-party local PDFs:** 0 new; four original Atlas-authored PDFs retained

## Tests and reproducibility

Run from the extracted `SIGNAL-ATLAS` directory:

```text
python -m unittest discover -s tests -v
python tools/validate.py
python tools/validate_science.py
python tools/validate_v06.py
python tools/frequency_stability_lab.py --output data/experiments/frequency_stability_v06.json
python tools/packet_query_v06.py "frequency stability" --limit 5 --output data/packets/examples/frequency-stability.v0.6.packet.json
python tools/packet_query_v06.py "public records RG 457" --limit 5 --output data/packets/examples/public-records.v0.6.packet.json
python tools/evaluate_packets_v06.py
python tools/build_atlas_index.py
python tools/build_science_index.py
```

Observed results in the release build environment:

| Check | Result |
| --- | --- |
| `unittest` suite | 8 passed |
| generic package validation | 142 sources, 76 claims, 20 notes, 18 profiles, 28 SVGs; pass after fixing the inherited title-tag check to accept accessible SVG title IDs |
| science / document validation | 26 publication records, 4 local Atlas PDFs, 30 document records; pass |
| extracted v0.5 regression audit | 134 sources, 69 claims, 23 publications, 18 profiles, 24 lessons, 25 SVGs; pass using `validate_v05.py --root <extracted-v0.5-repository>` |
| v0.6 package validation | all joins, rights flags, 208-path inheritance inventory, packet checksums, graph links, site markers, SVG labels, and local links pass |
| packet tests | alias reason and source URLs present; catalog and claim hashes match; packet digest verifies; unknown request stays unresolved; candidates excluded by default; limit is bounded |
| frequency-stability tests | deterministic fixed-seed series; known two-block Allan deviation equals `sqrt(2)` for the test vector; insufficient blocks rejected |
| derived SQLite indexes | rebuilt from canonical JSONL and current publication/course records; manifests match canonical input files |

The comparison reads the stored v0.5 JSON receipt instead of rewriting it. Its exact 20 queries remain a curator-authored in-sample diagnostic; seven of the v0.6 alias mappings were selected to repair known misses from those queries. The 20/20 result is therefore a targeted regression result only. It is not a held-out retrieval test, agent benchmark, model answer evaluation, or cost experiment.

## Measurement and historical evidence limits

The frequency lab uses fixed-seed synthetic values and a simple non-overlapping estimator under regular-sampling assumptions. It illustrates method and interval dependence; it is not real device data, empirical clock performance, calibration, or a traceability demonstration.

New source cards summarize NIST technical records and public institutional/archive pages from NSA, CSE, and ASD. Records remain hosted by original institutions. Institutional histories are explicitly attributed; finding aids describe archival scope and do not establish every underlying event. Pages were reviewed selectively on the release date, not independently audited line by line. Recheck volatile pages, access terms, and source scope before reuse.

No external PDFs were newly mirrored. Packet checksums establish exact local input/output bytes only. They do not establish factual correctness, URL freshness, legal rights, completeness, or answer quality. No GitHub repository or public site was changed.
