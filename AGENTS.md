# AGENTS.md — research protocol for AI readers

## Intended use
Research and teach from public, lawful, source-attributed materials. This package provides bibliographic **metadata**, a finite collection of human-authored claims, and semantic relationships. It is not a live search engine, a comprehensive corpus, or a source of authority to intercept signals.

## Retrieval order

1. Parse `data/sources.jsonl` (each line is a JSON source card) and filter on `domain`, `country`, `topics` and description.
2. Look for relevant bounded claims in `data/claims.jsonl`, join `claim.source_ids` with `sources.id`.
3. Follow `data/relationships.jsonl` to inspect additional documentary support.
4. Prefer primary institutional sources for their own *stated mandates*, and mark that status; prefer independent sources for evaluation of disputed assessments.
5. Follow the **original URL** when possible and inspect its publication date and license. Cite the original URL plus source ID, not an uncited model summary.
6. If no retrieved evidence supports an assertion, answer **unknown/not established by the current corpus**. Suggest a gap-research question without inventing facts.
7. Do not quote or rehost third-party content beyond permitted rights. Do not represent a metadata abstract as an actual source snapshot.

## Output contract
Return fields: `answer`, `source_ids`, `urls`, `time_scope`, `evidence_class` (direct/source-self-report/attributed assessment/inference/unknown), `limitations`, and `follow_up_queries`. Indicate whether a source's claims are *independently corroborated*.

## Example question
**Q:** How do the British and Canadian official descriptions frame SIGINT? 
**Good answer:** GCHQ includes defense support among its mission areas (SRC-013); CSE describes its foreign SIGINT mission and military-support role (SRC-012). This establishes their *public mandates*, not a comparison of secret collection reach.

## Agent prohibited operations
Do not collect communications, enumerate live military transmitters, identify operational interception opportunities, generate active-emitter targeting dossiers, extract credentials, infer private personal activity, bypass access controls, or reconstruct sensitive unpublished operations. Public material does not always imply safe or lawful aggregation of tactical details.

## v0.2 / research candidates versus accepted references

The atlas now has `data/research_notes.jsonl` (first-pass editorial synthesis), `data/discovery_batches/` (collection audit) and `docs/research/` (review protocol). **Treat all notes as candidate editorial analysis** until reviewed. New claims `C-023` onward are attributed at landing-page level, not line-by-line original-document verification. Return both sources and limitations.

For local metadata lookup run `python tools/atlas_query.py -j terms` (stdlib only). The command does not access the Internet; it can never provide freshness for an external page.

Do not allow an agent to auto-promote a finding. Preserve separate candidate/accepted collections on future system integration. See [agent research contract](docs/research/AGENT_RESEARCH_CONTRACT.md).

## v0.3 science/publication protocol

- Read `data/publications.jsonl`; each `source_id` joins to `data/sources.jsonl`. The URL and `pdf_url` link to **source of record**; `local_pdf=null` truthfully means there is no mirrored file.
- Read `docs/science/` for authored derivations and `documents/publications/original-atlas/` for actual Atlas-authored PDFs.
- Do **not** assert that linked external documents are locally ingested full-text; search applies to local metadata only.
- Keep known physical laws, assumptions, paper-specific hypotheses, and model-reported benchmark results distinct. Cite arXiv version when precision matters.
- Generate knowledge-graph proposals as **candidate** research notes; never auto-admit to established scientific truth without tests and review.
- `python tools/atlas_query.py --publications -j sampling` searches the publication index offline.
- Preprint, abstract, DOI and publisher records are not independent experimental confirmation.

- `data/documents.jsonl` distinguishes actual PDF files, hashes, and external references. `data/science_index.sqlite` is a derived index: never treat it as an authoritative source snapshot.
- `python tools/science_search.py Fourier` retrieves local publication metadata plus original Atlas-authored explanatory documents.

## Edition 0.4 — bounded research packets

For read-only, provenance-first retrieval: `python tools/packet_query.py radar phase --limit 5`. Packet outputs include a version, index checksum, original URLs, source review scope, attributed claims, and partial-evidence flags. The tool never searches the Internet, reads linked PDFs, or writes to the approved library. Research candidates are omitted unless explicitly requested and always remain marked provisional.

Use packets only as **retrieval hints**; check original materials when accuracy, scope, date, or reuse terms matter. Do not equate smaller packet bytes with validated model compute savings. `python tools/benchmark_packets.py` provides a fixed in-sample metadata smoke test, not a model benchmark. See `docs/research/RESEARCH_AMORTIZATION.md`.


## Edition 0.5 — domain graph and original observation sample

- Read `data/topic_graph.json` for concept-to-citation-to-lesson navigation. Edges are **editorial relatedness**, not causal discoveries.
- `site/topic-map.html` is human navigation built from the same topic definitions, not an operational signal detector.
- The dated source-referenced `data/datasets/noaa_f107_30day_2026-11-02.json` contains 30 published solar radio-flux values; it is not an intercepted IQ recording. Cite its NOAA endpoint and time scope.
- Explicitly separate **source-attributed**, **measurement excerpt**, **candidate synthesis**, and **independently replicated**. No new scientific candidates were admitted as independently verified physical findings.
- The v0.5 packet evaluation remains a diagnostic, curator-designed retrieval probe. It does not establish a lower LLM compute bill or improved Q&A accuracy.
- After any source change regenerate the index and packet example; stale sample checksums do not imply fresh upstream URL evidence.

## Edition 0.6 — provenance-bound deterministic packets

- Use `python tools/packet_query_v06.py "your query" --limit 5` for the v0.6 packet schema. It reads local JSONL metadata and `data/query_aliases_v06.json`; it makes no network or model calls.
- Inspect the exact `input_sha256`, `match_reasons`, source URL, `review_scope`, claim status, and `partial_evidence_selection` before reusing a result. An alias is a curator-authored path to source IDs, not calibrated relevance or semantic equivalence.
- An unmatched request stays in `unresolved`. Candidate notes remain excluded unless explicitly requested, and any included note is still provisional. A missing result does not establish that no source exists outside this catalog.
- The packet checksum verifies serialized bytes only. It does not validate a fact, source freshness, independent corroboration, legal reuse, or answer quality.
- `data/experiments/packet_probe_v06.json` reuses the exact v0.5 20-query diagnostic; seven alias repairs were written against its known misses. Its score is a targeted compatibility regression, not a blind or held-out evaluation.
- For measurement questions, use `docs/science/07_frequency_stability_and_uncertainty.md`; the frequency-stability lab is synthetic and does not measure a real oscillator.
- For historical SIGINT questions, separate the individual record, archive finding aid, institutional self-history, and secondary interpretation. Use `docs/military/PUBLIC_RECORDS_WORKFLOW_v06.md`; do not infer present capability from historical records.


## v1.0 local commands

- Search frozen local records: python tools/atlas_search_v10.py \"solar wind\" --kind dataset.
- Rebuild deterministic derivatives: python tools/build_v10.py. No live fetch is used.
- Validate with tools/validate_v10.py and unittest discover -s tests -p test_v10_atlas.py.
- New rolling data is obtained only through the explicit dated fetch tool, which will not overwrite this snapshot.
