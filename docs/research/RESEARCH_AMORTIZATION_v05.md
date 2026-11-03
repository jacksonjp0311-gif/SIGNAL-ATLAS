# Research Amortization — v0.5 evaluation boundary

**Mission:** Reuse provenance-backed research to reduce repeated source discovery and parsing while maintaining answer correctness. The first packet format is a read-only, versioned metadata retrieval artifact.

## Added this edition

1. A topic map in JSON and an accessible human explorer, linking source IDs to lessons.
2. A merged corpus with individual source IDs, rights notes, review status and a new observational dataset.
3. An offline test suite with fixed diagnostic queries.
4. A benchmark protocol for **real agents** with randomized matched information tasks, citation/faithfulness scoring, freshness checks and total token/latency/ingestion costs.

## What we have **not** proven

No controlled experiment with a live model and a strong end-to-end web/RAG baseline has been run. We cannot claim compute or reasoning improvement on the basis of JSON payload size. This is a hypothesis for future testing.

## Candidate invariant

A reusable answer should carry a compact `who/what/when/how/limits` context to remain auditable: source identity, publication/retrieval date, measurement/processing conditions, evidence status, and specific caveats. This is a proposed engineering discipline, not a new law of physics.
