# Source harvesting, ethics, security & rights policy

**Publicly readable ≠ public domain ≠ licensed for scraping or redistribution.** In particular, government sites across jurisdictions have different copyrights and terms. Use original commentary and URLs when reuse is uncertain.

### Acquisition decision
1. Is the source publicly reachable without circumventing login, paywall, access controls, robots or rate limits?
2. Do site terms and robots policies permit the planned crawl? Prefer APIs, bulk datasets and permission requests when appropriate.
3. Does the content's copyright/public license permit storage and republishing? Record attribution, version and license requirements.
4. Does the source contain personal/private communications, sensitive identifying data, proprietary secrets, leaked classified materials, or operational targeting information? If yes, exclude or review and minimize.
5. Can a reader inspect provenance? Preserve original URL, title, publisher, publication date, captured date, summary, hash, license basis and any transformations.

### Allowed in a public research catalog
Published institutional mission descriptions, declassified historical material when lawfully redistributed or linked, spectrum allocation charts, scientific articles and standards, permitted educational examples, software reference manuals, archival histories, public parliamentary oversight reports.

### Avoid as indexed intelligence targets
Active tactical radio frequencies or emitter mapping, decrypted private traffic, live-force operational footprints, combatant location tracking, sensitive military network specifications, exploit chains, protected communications and unauthorized recordings.

### Legal caveat
Rules vary across places and technologies. See the primary statute linked in SRC-029 as a US example; seek competent legal guidance when collecting real-world signals. Course labs should use simulated data, personally owned equipment, or explicitly authorized/public educational signals.

### Robot / terms workflow for a future crawler
Before each domain crawl, check robots rules, terms, API alternatives, reuse license and public safety. Rate-limit with a documented user agent, use conditional fetching and canonical URLs, never evade access restrictions, and maintain a take-down process. No crawler is shipped in v0.1.

## v0.3 scientific literature

No public/research/science status overrides copyright. Include factual knowledge, bibliographic references, scholarly URLs, DOI and original paraphrase; full PDFs only when the original work is redistributable and attribution is preserved. Verify arXiv *version-specific* license. Default arXiv license is not onward redistribution authority. See [document rights](documents/RIGHTS_AND_ACCESS.md).
