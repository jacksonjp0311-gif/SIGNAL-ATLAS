# v0.5 packet retrieval diagnostic

Run `python tools/evaluate_packets_v05.py` from any directory. The test reads curated source metadata and emits JSON to `data/experiments/packet_probe_v05.json`.

There are 20 *author-curated* queries, including straightforward matches, paraphrases and cases likely to fail. Gold expected source IDs are explicit in the script. This is deliberately a **diagnostic stress test**, not a blinded or representative benchmark; the questions and the source index were curated by the same project authoring process.

It verifies that returned source URL matches its ID, rights notes exist, and the packet hash matches canonical JSON serialization. Report misses openly. The text matcher requires all significant query tokens and often misses paraphrases and original-language synonyms. This limitation motivates a better retriever—not fake claims of agent accuracy.

**Pending:** real model-with/without-packets experiment with source-grounded answer scoring, total compute token budget, maintenance costs and held-out questions. See `AGENT_BENCHMARK_PROTOCOL.md`.
