# Editor / human navigation review checklist

For each monthly or release-time research batch:

- [ ] All source cards have unique IDs, functioning canonical URLs, language and publication date (when available).
- [ ] All new source claims have traceable and accurately scoped original references.
- [ ] Attribution is preserved for governmental self-descriptions and contested military assessments.
- [ ] Time scope is clear: a historic claim never silently becomes a current capability claim.
- [ ] Compare at least two **independent** supporting sources when making a contested, nontrivial conclusion.
- [ ] Confirm that rights allow any full-text, image, dataset or thumbnail copied into the repo.
- [ ] Every new teaching graphic has title/alt text, explanatory prose and source links for technical concepts.
- [ ] A first-time visitor can reach a lesson, a country profile and a specific original source within 3–4 actions.
- [ ] Agent query returns evidence IDs, original URL, date/period, confidence/limits and whether it is a self-report.
- [ ] No active tactical emitter catalogs, intercepted personal communications, or sensitive targeting dossiers.
- [ ] CSV and JSONL agree, graph claims resolve to real source IDs, archive checksums validate.
- [ ] Run `python tools/validate.py` (stdlib only) and try `python tools/atlas_query.py radar`.

**Release rules:** prevent unreviewed research notes from masquerading as accepted evidence. No claim about an actual crawl, full-text snapshots, or automatic updates unless a crawl/audit log exists.
