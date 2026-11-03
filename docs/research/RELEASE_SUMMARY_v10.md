# SIGNAL ATLAS v1.0 — Release summary

Release date: 2026-11-03  
Status: first complete, locally validated edition

Signal Atlas compiles public science, signal, technology, and historical material into a reusable library for people and AI. The core goal is to collect useful data, make it coherent, and make the compiled library navigable again.

## Included

- Complete inherited v0.8 tree; evergreen, version-neutral README logo preserved.
- 150 source cards, 82 scoped claims, 21 research notes, 26 publication records, 30 lessons, and 10 registered datasets.
- Five public-history routes across NSA, GCHQ, and ASD, with attributed source cards and scoped claims.
- Frozen NOAA GOES primary X-ray response: 716 raw rows, capture metadata and raw SHA-256; 358 exact timestamp/satellite pairs across two energy bands.
- Offline unified search across sources, claims, notes, publications, datasets, lessons, and selected research documents.
- Dataset coverage view, CLI, deterministic input manifest, provenance, teaching graphic, two lessons, and AI-readable query packet.

## Start

Open START-HERE.md, then site/unified_search.html and site/coverage.html.

~~~powershell
python tools/atlas_search_v10.py "solar wind" --kind dataset
python tools/atlas_search_v10.py "Pearl Harbor" --kind source --json
~~~

## Limits

The GOES file is one rolling six-hour capture, not a continuous archive. Physical quantities and time supports differ. No interpolation, event causality, nowcast, or forecast is claimed. Search is lexical over bundled metadata and selected Markdown; it does not crawl remote pages, index PDF full text, or answer with an LLM.

The requested public GitHub name is SIGNAL-ATLAS. Public creation is authorized but pending because current connected GitHub tools cannot create a repository. Artifacts should remain in the persistent SIGNAL ATLAS Library with earlier versions.
