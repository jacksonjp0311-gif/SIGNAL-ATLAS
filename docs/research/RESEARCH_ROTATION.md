# Each-run research rotation protocol

Versioned release cycle for humans and agents. This package is **not** a continuously running crawler. Each authorized research pass should be explicit, reproducible, and preserve the previous released snapshot.

## Intake

1. Preserve the previous version unchanged and record its checksum and source counts.
2. Discover public, lawful scholarly sources via arXiv metadata, DOI/Crossref, government repositories and authoritative domain indexes; rate limit, respect usage terms and keep source-specific rights fields.
3. Deduplicate by DOI, arXiv version and canonical URL (not title similarity alone).
4. Add bibliographic and document records. A PDF must have actual bytes and a SHA-256 hash before `local_pdf_present=true`.
5. Read new eligible PDFs and attach precise page/equation evidence; keep mere metadata-level claims explicitly qualified.
6. Cross-reference assumptions, units and limits. Candidate relationships stay in the Research Desk until independently tested and reviewed.
7. Expand a teaching path for every important technical discovery; original visuals must include text descriptions and link to evidence.
8. Audit both a human search path and a machine/agent search path.
9. Run `python tools/validate.py`, `python tools/validate_science.py`, `python tools/build_science_index.py`, and `python tools/release.py --version vNEXT --output /path/to/release.zip`.
10. Create a changelog with exactly what was added, rejected, reproduced or left unresolved. Never overwrite a prior version ZIP.

**Mandatory checks:** geographic balance, original-language support, author-reported versus independently tested results, per-paper redistribution rights, paper retractions/withdrawals, bibliographic version, cross-domain unit consistency, and no tactical emitter or private communication dossiers.

[Science coverage audit](SCIENCE_COVERAGE_AUDIT.md) · [Scientific protocol](../science/05_experiment_design.md) · [Source rights](../../documents/RIGHTS_AND_ACCESS.md).

## v0.4 next-run gate

Every research pass must review inherited data shape (especially duplicate CSV headers), source URL uniqueness, public access versus reuse rights, claims to source references, candidate/admitted status, newly created diagrams, and one human/agent navigation scenario. Record what was actually **read**, **indexed**, **downloaded**, and **experimentally tested**. Emit a new ZIP only after all local validators pass. No automatic GitHub push or perpetual crawler is implied.


## v0.5 run-to-run contract

Keep earlier release ZIPs immutable. Start the next run by checking `MANIFEST.sha256`, `data/datasets/` provenance, `data/topic_graph.json` referential integrity, and v0.5 experiment and citation checks. Maintain a source-by-source ledger recording examined versus only linked material. Test a human path and an AI retrieval path before each release. Do not auto-promote candidate notes or claim an agent benchmark before running one.
