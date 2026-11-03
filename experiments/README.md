# Experiments — edition 0.4

These are **actual reproducible tests**, not original discoveries. They operate on synthetic data and already-established signal-processing theory.

1. `python experiments/signal_lab.py` — computes a 17 Hz tone under two sample rates and a 20 Hz amplitude-modulated carrier. Writes `data/experiments/signal_lab_v04.json` plus two SVG/PNG graphics. Requires NumPy and Matplotlib. Fails if peaks disagree with analytical predictions.
2. `python tools/benchmark_packets.py` — runs 10 fixed metadata queries against source cards and tests whether an expected source appears in the top five. Writes `data/experiments/packet_benchmark_v04.json`. Uses standard Python library. **In-sample source-ID coverage**, not a blind benchmark or an AI compute/quality test.
3. `python experiments/coverage_chart.py` — rebuilds a graphic from the actual source-domain counts.

### Recorded results

- **Aliasing:** synthetic 17 Hz sampled at 20 Hz → 3 Hz FFT peak; sampled at 100 Hz → 17 Hz FFT peak. Both equal established sampling predictions.
- **Amplitude modulation:** carrier 20 Hz, message 3 Hz, modulation index 0.65 → symmetric spectral lines at 17, 20, 23 Hz and normalized amplitudes 0.325, 1.0, 0.325.
- **Research packets:** 10/10 expected source IDs present among the top five of curated metadata for predeclared fixed queries (after one preliminary query-language mismatch was corrected). Average JSON packet around 2.48 KB vs 82.9 KB for *all catalog source metadata*. That 97% reduction is a **comparison to loading the entire metadata catalog**, not to a well-optimized competing retriever, and does **not** establish LLM token savings, compute cost reductions, retrieval freshness, or correct answers.

The next meaningful experiments require held-out prompts, real agent tasks, ground-truth source checking, cache build/maintenance costs, equivalent answer quality, and measured inference tokens/latency.


## Edition 0.5 experiments

**Observational science:** `python experiments/noaa_f107_lab.py` recomputes descriptive statistics and rebuilds an accessible SVG from 30 dated NOAA radio-flux observations stored in `data/datasets/`. This is physical observational data, not a synthetic waveform or raw IQ capture.

**Research retrieval diagnostic:** `python tools/evaluate_packets_v05.py` evaluates 20 curator-authored metadata queries and logs source-ID hits and failures. It is not a blind agent evaluation. 13/20 hit the designated source in top 5; all returned packets preserve source-ID/citation integrity. See [evaluation notes](RETRIEVAL_EVALUATION_v05.md).

**Future full-agent benchmark:** [protocol](AGENT_BENCHMARK_PROTOCOL.md) requires independent held-out questions, answer accuracy, citation faithfulness, and all-time compute costs.
