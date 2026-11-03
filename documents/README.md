# Scientific publications · document library

This is the **co-located navigation point** for all Signal Atlas science publications and PDFs. There are **14 scholarly/course/policy references**, plus original Atlas learning briefs in `publications/original-atlas/`. Not every external work is physically copied.

- [Publications catalog](INDEX.md) — linked bibliography with licensing and local status.
- [Machine-readable manifest](../data/publications.jsonl) — IDs, authors, abstracts/summaries, URLs, PDF URLs, rights, checks and local paths.
- `publications/original-atlas/` — **actual original PDF briefs included in this package**.
- `publications/third-party/` — reserved for full PDFs when downloadable and redistribution permitted. **Initially empty**; no third-party PDF is claimed to be present.
- `publications/reference-cards/` — individual human-readable cards for external publications, including a direct PDF link when available.
- [Rights and access policy](RIGHTS_AND_ACCESS.md) — rules for mirroring without compromising scholarly access.
- [Source fetch tool](../tools/fetch_approved_pdfs.py) — opt-in downloads of individually rights-verified external papers (requires network access).

**Practical rule:** Every reference is co-located in the *index*. PDF bytes are co-located only when actually archived; `local_pdf` is null otherwise. A source link is not a stored snapshot.

**Integrity:** [`data/documents.jsonl`](../data/documents.jsonl) includes every PDF/resource with true local-presence status and SHA-256 where present. [`FILES.sha256`](FILES.sha256) lists the four original local PDFs.
