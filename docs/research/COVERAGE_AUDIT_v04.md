# Edition 0.4 — coverage and data integrity audit

**Source cards:** 112  ·  **Claim cards:** 56  ·  **Publication/resource records:** 17  ·  **SVGs:** 19

## Domain distribution (metadata cards, not independent verification)
- military: 33
- science: 21
- history: 17
- technology: 11
- spectrum: 9
- law: 9
- research: 7
- education: 3
- applications: 2

## Geographic attribution (publisher/primary scope, not a map of military capability)
- International: 46
- United States: 29
- Australia: 7
- United Kingdom: 6
- France: 4
- Japan: 4
- Netherlands: 4
- New Zealand: 3
- Canada: 2
- Sweden: 2
- Germany: 1
- Israel: 1
- Russia: 1
- China: 1
- Norway: 1

## Audit findings
- Prior v0.3 `sources.csv` had 226 header columns due to repeated appended `language, checked_at, review_scope, research_batch` fields; v0.4 rebuilt one canonical 18-field CSV.
- US/International publishers remain overrepresented in source records; 15 country/alliance profiles do not imply equally corroborated country coverage.
- Many foreign SIGINT accounts derive from an agency’s public history or mission statement and need independent archival corroboration.
- Research documents/third-party PDFs are bibliographic entries unless explicit local paths and checksums exist.
- 10/10 in-sample lexical retrieval checks passed, but the questions were taken from the same curated corpus. No end-to-end agent inference measurement exists.
- The validated Fourier lab demonstrates standard theory on synthetic noiseless data; not a new law or a real-world SDR evaluation.
