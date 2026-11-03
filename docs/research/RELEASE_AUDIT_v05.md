# SIGNAL ATLAS v0.5 — evidence-based release audit

**Research snapshot date:** 2026-11-02. **Built from:** v0.4 package, not a clean restart.

## What actually shipped

| Category | v0.4 | v0.5 | Explanation |
|---|---:|---:|---|
| Curated source cards | 112 | **134** | 22 new URL-unique official/scholarly public references; GNU Radio and SigMF duplicates were reused instead of recounted |
| Attributed, scoped claims | 56 | **69** | 13 more source-linked claims, not unqualified operational assertions |
| Publication and resource records | 17 | **23** | Three linked scholarly papers and three technical/data-reference entries; **zero external publisher PDF bytes** mirrored |
| World/context profiles | 15 | **18** | Finland, Brazil, South Africa; the Brazilian source concerns civilian intelligence and the South African source is general reporting only |
| Sequenced lessons | 20 | **24** | Solar observation, SAR data semantics, radio-astronomy calibration, research packet integrity |
| Original editable SVG figures | 19 | **25** | New hero/banner, evidence chain, SAR product diagram, global evidence types, topic map and actual solar observation chart |
| Local original Atlas PDFs | 4 | **4** | Unchanged, indexed and SHA-256 verified; no claim of new full-text ingestion |
| Cataloged research candidates | 14 | **18** | Four new hypotheses/editorial syntheses, separate from admitted science |

Additional files: an illustrated visual research vision, `site/topic-map.html`, `data/topic_graph.json`, a derived cross-corpus SQLite FTS index, and a real 30-point solar radio-flux subset with its source link, timestamp and checksum.

## Scientific experiments and findings

**Experiment A — actual reported solar radio-flux observations.** A 30-day excerpt from NOAA SWPC's 10 cm flux data product, representing dated readings from 2026-10-04 through 2026-11-02, was retained and reprocessed offline. The 30 values range from 89 to 137 sfu, mean **109.9 sfu**. This demonstrates a reproducible observational data pipeline beyond synthetic signal generation. It is not a solar-cycle study, an RF capture, a causality demonstration, or a novel physical effect. Time tags in the frozen subset have no explicit time-zone offset.

**Experiment B — versioned packet retrieval diagnostic.** On 20 published, author-curated queries, the expected target source appeared in the first five results in **13/20** cases. All 20 packets preserved correct source IDs, original URLs and valid integrity hashes; seven query formulations missed relevant references. The misses involve semantic paraphrase/rigid all-word matching and mismatched scopes. This is a better quality signal than making unqualified 100% accuracy claims. Crucially the test is **not blind or independently held out**, and **did not invoke an AI model**. It provides no proof of lower total inference cost or improved answer accuracy.

For details and reproducibility:

- [Observed measurement lab](../../experiments/noaa_f107_lab.py)
- [Retrieved observations and methodology](../../data/datasets/README.md)
- [Retrieval probe script](../../tools/evaluate_packets_v05.py)
- [Recorded retrieval results](../../data/experiments/packet_probe_v05.json)
- [Protocol for future model comparison](../../experiments/AGENT_BENCHMARK_PROTOCOL.md)

## Source evidence and global coverage

Added official NOAA/F10.7, ESA/Copernicus SAR, Finnish intelligence review 2026, Japanese white-paper text, NZ independent oversight, Brazilian civilian intelligence historical context, South African defense annual-report portal, and Smirnov radio-interferometer scholarly abstracts. **All these are bibliographic or landing-page/abstract-level additions, not line-by-line independent audits of their complete linked documents.** The public institutional information is historical and conceptual and has not been used to create live tactical collection inventories.

Original diagrams were authored for Atlas. The visual research poster is an editorial illustration. Other providers' photographs, underlying SAR imagery, and research papers were linked but not copied. Source licenses are recorded individually, and publicly accessible does not imply redistributed under a permissive license.

## Visual and navigation checks

The README begins with an original scalable banner, followed by a version-development infographic. The topic graph is accessible both as editable `data/topic_graph.json` and as human-friendly `site/topic-map.html`; graph edges denote editorial links and do not prove causal relationships. All 24 lessons are linked in the offline explorer's course section. The catalog and SQLite source indexes contain the original source IDs and descriptive limitations.

## Inherited and current limitations

- **No controlled agent-versus-agent benchmark** was run; the measured 13/20 is an offline string-matching diagnostic only.
- No independent human learner comprehension study; diagrams have accessible textual explanations but have not been tested with students.
- Only four Atlas-authored PDF guides are stored locally; third-party scientific paper full text is mostly linked, not mirrored.
- Multilingual original texts are indexed, but no independently evaluated multilingual semantic retrieval exists. This likely contributes to search misses.
- The dataset is a 30-day observation window, not a long-term historical archive; 30 values are insufficient to establish trends or new physics.
- An agency's publicly stated role or an official budget report cannot establish its classified capabilities.
- No automated recurring crawler, GitHub publication, or integration into other projects has been executed.

## Next version goals

1. **Retrieval quality:** multilingual query expansion, source-aware hybrid retrieval, citations graded against held-out independent questions. Build a fair RAG/web baseline.
2. **Scientific depth:** obtain and review eligible publication full text with page/figure/equation provenance and lawful reuse; add more genuine measurement data with clearly stated licenses.
3. **World coverage:** seek independent original-language corroboration and archival historical documents beyond organization self-descriptions.
4. **Learning impact:** recruit human participants to test whether the new diagrams improve explanation quality, task accuracy and time to evidence.
5. **Research Amortization economics:** assess corpus-building/refresh expenses plus per-task model tokens and latency with no quality loss. Do not declare a compute breakthrough without the experiment.

**Bottom line:** v0.5 is a stronger *reusable research prototype*, not a validated AI efficiency breakthrough or a new physics discovery. It has acquired both an observed-data pilot and a measurable retrieval failure profile—two useful foundations for the next experimental pass.
