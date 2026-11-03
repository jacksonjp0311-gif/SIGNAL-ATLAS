# Machine-readable research data

The v0.7 data expansion adds a central dataset registry and a reproducible NOAA observation join. See dataset_registry.json and the Data Explorer; the package keeps the source catalog, observed datasets, derived tables, and synthetic teaching data distinct.

These files are an **initial seeded index**, not a complete corpus or a completed crawl. All source records were manually assembled from publicly discoverable source pages on 2026-11-02. Their `review_status` is not equivalent to a full page-by-page verification or license clearance. A live URL can change without notice.

- `sources.jsonl` / `sources.csv` — bibliographic cards (one record per source)
- `entities.jsonl` — publicly named countries, alliances and organizations
- `claims.jsonl` — source-attributed, bounded claims
- `relationships.jsonl` — directed edges that support navigation
- `frequency_bands.json` — educational band taxonomy (not live emitter data)
- `coverage_matrix.csv` — **presence of source coverage**, not relative military capability
- `research_questions.jsonl` — explicitly open questions and evidence gaps
- `snapshots/` — our own metadata cards; **no copied source pages**

Key: link a `claim.source_ids` entry to `sources.id`. Never promote a government's own institutional statement or an adversary assessment to independently verified performance. Respect license/usage restrictions before saving the page text or image.

## v0.2 additional data

- `research_notes.jsonl` — editorial first-pass research notes, **not independently verified discoveries**.
- `discovery_batches/2026-11-02-B.md` — source-discovery audit and incomplete checks.
- New bibliographic card fields: `language`, `checked_at`, `review_scope`, `research_batch` (only new cards; optional for old).
- New claims include `review_level` and `time_scope`; treat as qualified source-attributed statements.

**For agents:** `python tools/atlas_query.py -j TERM` returns local matching metadata only. No inference, internet search, or autonomous verification happens during this command.

## v0.3 science

- `publications.jsonl` — scientific source bibliographic IDs, direct publisher PDF links, licensing status, and null `local_pdf` for unmirrored external items.
- Separate publications from original educational PDF briefs and from candidate discovery notes; follow `source_id` joins to the master sources.


## Edition 0.5 additions

- `atlas_index.sqlite`: a **derived** local FTS5 index joining the canonical sources, claims, publications, country/context profiles and provisional notes; built by `python tools/build_atlas_index.py`. The JSONL corpus remains the editable source of truth.
- `topic_graph.json`: eight explicitly editorial subject associations pointing to source cards and course lessons.
- `datasets/noaa_f107_30day_2026-11-02.json`: an actual 30-point NOAA published-observation excerpt with rights/provenance note in `datasets/README.md`.
- `experiments/packet_probe_v05.json` and `noaa_f107_v05.json`: reproducible diagnostic results, not a live inference benchmark.

## v0.8 solar-wind data

The registry adds the two frozen real-time SWPC in-situ inputs, active-selected views, exact source/time paired records, and partial UTC-day summaries. Begin with the [Solar-wind Explorer](../site/solar_wind.html) and [v0.8 collection guide](../docs/research/DATA_COLLECTION_GUIDE_v08.md).


## Version 1.0

- Registry distinguishes observed, derived, and synthetic datasets.
- Unified search index and input manifest are offline derivatives.
- GOES raw snapshot, metadata, paired table, and provenance share source/dataset IDs.
- Coverage report describes this package, not global sensor coverage.
