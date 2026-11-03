# Signal Atlas thread-resume handoff

## Current release: v1.0

- Goal: compile useful public science, signal, technology, and historical data into a coherent, navigable system for humans and AI, with origin, dates, joins, evidence roles, and limits attached.
- Release: first complete v1.0 edition. Preserve the evergreen version-neutral logo at assets/signal_atlas_logo_header.png.
- Repository source update: Git metadata is excluded from release lineage, validation, and packaging; the original v1.0 ZIP remains a historical snapshot. Preserve the user-created MIT LICENSE for project-owned material.
- User direction: collect more data; make the system coherent and useful; the public GitHub repository is exactly SIGNAL-ATLAS, with no version number.
- GitHub: the public repository is https://github.com/jacksonjp0311-gif/SIGNAL-ATLAS. Keep the repository name version-neutral; versioned archives remain preserved in the Library.
- Library: preserve v0.5, v0.6, v0.7, v0.8, and v1.0 archives with their summary, audit, and handoff in the persistent SIGNAL ATLAS Space.
- Start with README.md, site/unified_search.html, site/coverage.html, docs/research/RELEASE_SUMMARY_v10.md, and docs/research/RELEASE_AUDIT_v10.md.
- New batch: NSA, GCHQ and ASD public-history routes; one frozen NOAA primary GOES X-ray snapshot and exact paired channels.
- Future work: extend dated collections and source coverage in SIGNAL-ATLAS, preserving the published archive history and release provenance.

## Reproduction

From the package root run tools/build_v10.py, tools/atlas_search_v10.py "GOES x-ray flux" --kind dataset, tools/validate.py, tools/validate_science.py, tools/validate_v10.py, and unittest discover -s tests -p test_v10_atlas.py.

Historical v0.5 through v0.8 handoffs remain in their release ZIPs.
