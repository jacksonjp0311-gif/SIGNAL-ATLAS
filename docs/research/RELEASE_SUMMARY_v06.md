# Signal Atlas v0.6 release summary

**Release date:** 2026-11-02  
**Package:** `SIGNAL-ATLAS-v0.6.zip`  
**Parent:** complete original `SIGNAL-ATLAS-v0.5.zip`, SHA-256 `B7FDA71A48C858CE41A8D44ACA9ACD999D354EFB026A0E191951EFC9198DBAEE`

**Persistent Library:** [SIGNAL ATLAS](https://chatgpt.com/space/page_6ae966acc9048191b13367c980107ee3)

Signal Atlas v0.6 adds measurement-science instruction, public historical record navigation, and provenance-bound offline packets while preserving the complete prior repository. All 208 file paths from the original v0.5 archive are accounted for in `data/release_v06_lineage.json`; unchanged inherited files retain their earlier hashes. The later 12-file v0.5 update archive was used only for the evergreen logo and roadmap graphics, never as the repository base.

## What is included

- 142 source cards, 76 scoped claims, 18 world profiles, and 20 research notes.
- 26 linked scientific reference records; the four pre-existing Atlas-authored PDFs remain local and third-party PDFs remain link-only.
- 26 course lessons, including a new synthetic frequency-stability exercise and a public historical source-criticism exercise.
- An authored measurement chapter with a stated non-overlapping Allan-deviation estimator and a deterministic, fixed-seed synthetic data generator.
- Eight NIST, NSA, CSE, and ASD source cards, with explicit review scope and institutional attribution.
- Three original, accessible SVG teaching diagrams for metrology, archive provenance, and AI-readable packet lineage.
- A v0.6 packet schema that records source, claims, and alias input hashes; query match reasons; source-to-claim joins; partial evidence; candidates; unresolved queries; and packet integrity digest.
- Updated offline topic graph and explorer, plus a retained copy of the accepted evergreen logo and roadmap graphic.

## Validation performed

The standard-library test suite has eight checks covering alias retrieval, source and claim hashes, packet checksum verification, unresolved queries, candidate defaults, bounded limits, Allan-deviation arithmetic, and deterministic synthetic output. Release validators check catalog joins, URLs, rights state, historical v0.5 file lineage, graph edges, SVG XML/accessibility labels, site navigation, local PDFs, SQLite manifests, and packet hashes. The unchanged v0.5 evaluation receipt is preserved and compared without overwrite.

The 20-query retrieval compatibility diagnostic records the original v0.5 result (13/20) and the targeted v0.6 result (20/20). Seven new aliases were authored against the exact known misses and target IDs from that same query set, so this is a retrospective regression repair rather than independent or held-out evidence. No LLM was executed; no answer quality, latency, or inference-compute reduction was tested.

## Scope limits

External sources and publications remain linked, not mirrored. Page review was selective and source-attributed; this release does not independently corroborate every historical statement or perform a blanket license audit. The synthetic lab is not a real oscillator measurement or calibration certificate. Public finding aids and institutional histories are selective historical sources and do not support claims about current operational capabilities. No GitHub publication or deployment was performed.

For exact commands, numerical receipts, and limits, see [the release audit](RELEASE_AUDIT_v06.md). For continuation guidance, see [the handoff](../../THREAD-RESUME-HANDOFF.md).
