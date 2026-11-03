# Signal Atlas roadmap to v1.0

## v1.0 delivered — 2026-11-03

This first complete edition compiles public records, dated observations, provenance-bound derivations, offline search, a coverage view, public SIGINT history, and teaching routes. See the [release summary](RELEASE_SUMMARY_v10.md) and [audit](RELEASE_AUDIT_v10.md). Future releases should extend dated collections and source coverage based on actual use.


## Goal

Build a growing, navigable research library that collects useful signal-related data and documentation, connects related material, and packages it so people and AI tools can reuse it.

The Atlas records what has been collected and how it fits together. It is not meant to imply that every signal, historical record, or measurement on the internet has already been captured.

## Release path

### v0.7 — Turn collections into linked data

Completed. The NOAA daily geomagnetic snapshot is paired by date with the retained F10.7 series and connected through the registry, viewer, lesson, provenance, and AI packet.

### v0.8 — Broaden real data coverage

Current step. Add a direct measured solar-wind layer—plasma and magnetic field—to the solar-radio-flux and geomagnetic records. Preserve raw 1-minute inputs, spacecraft identity and active-source changes, then link exact paired measurements and coverage-aware summaries through one registry, explorer, science guide, lesson, and packet. Longer historical windows and additional signal/spectrum and public-history material remain open coverage priorities.

### v0.9 — Make cross-library retrieval dependable

Unify search across the source catalog, dataset registry, lessons, technical notes, and public-history collection. Add filters for date, domain, data type, and observed versus synthetic status. Keep direct links from each result to its data, source record, and explanatory material.

### v1.0 — A stable, useful research library

Ship a clearly indexed collection with a repeatable offline build, retained data snapshots, coherent catalog IDs, learning routes, accessible teaching graphics, AI-readable packets, and a tested archive. Publish a coverage view that shows what is included and where the collection still has gaps.

## Working principles

- Grow the collection through useful batches and keep their original data together with the derived outputs.
- Make the distinction between observed, derived, forecast, and synthetic material visible.
- Connect each new data batch to the source catalog, topic pages, learning path, and reusable packet.
- Preserve dated versions so a rolling feed cannot silently change an older release.
- Keep basic provenance in the collection so future work can trace a value to its file and input. Independent legal or citation review is not a release gate for this roadmap.
- Do not turn descriptive comparisons into causal or forecasting claims without the data and analysis needed to support them.
