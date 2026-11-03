# Edition 0.4 release audit — 2026-11-02

## What was tested

| Test | Observed result | Interpretation |
|---|---|---|
| Source catalog round-trip | 112 JSONL cards exactly matched 112 CSV rows with 18 unique columns | Fixes v0.3's 226-column repeated-header defect |
| Referential integrity | 56 source-attributed claims, 14 research notes, 15 geopolitical entries; local link validator passed | No local dangling IDs/links in the tested structure |
| Publication and PDF manifest | 17 publication/resource cards, 4 genuine original Atlas PDFs, 0 external PDFs mirrored | Local documents distinguished from citations |
| SVG diagrams | 19 original SVG images; 5 added in this edition; XML and accessible title/description checks passed for all new figures | Graphics are real local files, not images from search results |
| Synthetic sampling | 17 Hz tone → 3 Hz FFT bin at 20 Hz sampling, 17 Hz at 100 Hz | Confirms textbook aliasing in a noiseless, deterministic simulation |
| Synthetic AM | 20 Hz carrier, 3 Hz message, modulation 0.65 → amplitudes 0.325, 1, 0.325 at 17/20/23 Hz | Confirms established modulation theory; not new physics |
| Offline research-packet lookup | 10 of 10 fixed in-corpus expected source IDs appeared in top five; mean packet 2,477 bytes vs entire catalog 82,868 bytes | Metadata payload only; no proof of model inference savings or answer accuracy |
| Static browser JS interactions | In Chromium with inline page content: source count 112, claim count 56; Packet Lab navigated, 20 lessons and 17 publications displayed, a radar search returned 2 records, no JS exceptions | Interaction smoke test; not a complete `file://`/asset-load test because direct file navigation is restricted in test environment |

## Research discovery record

17 net-new source URLs were cataloged after URL deduplication. These include NASA/JPL remote-sensing education, MIT signal inference lecture series, public NRAO instrumentation guides, ITU regulations navigation, National Archives historical indexes, Sweden's FRA public history (including original language), and the 2026 Japanese defense white-paper portal. These are **source metadata and landing-page review**, not deep readings of every linked paper, nor independent corroboration of every report.

No external copyright-controlled document was mirrored. Reuse permissions still require per-asset review. Source metadata remains more heavily concentrated in International and U.S. publishers than independent region-specific research; the 15 world profiles are unevenly documented.

## What's new versus not yet achieved

**Achieved:** reproducible synthetic-signal experiments; original scientific charts; a bounded read-only packet contract; repaired catalog integrity; a working offline HTML navigation smoke test.

**Unverified/not achieved:** a novel scientific discovery, a real-world RF sampling experiment, cost saving in inference tokens or total compute, high-accuracy agent answers, robust multilingual search, universally fresh source pages, full publisher PDF local ingestion, and autonomous admission of new research.

## Next release gates

1. Evaluate packets using **blind held-out questions**, source-verified answers, and a strong RAG baseline while counting *all* costs (indexing, update, inference, citation rechecks).
2. Expand geographic evidence via primary original-language archives and independent historical corroboration, not only national agency self-descriptions.
3. Add permission-verified local paper text and stable content hashes where allowed; preserve source context, equations, figures and license.
4. Add human accessibility tests with actual learners; record whether the visual explanations improve comprehension.
5. Promote no candidate research into accepted scientific knowledge without reproducible tests and editorial review.
