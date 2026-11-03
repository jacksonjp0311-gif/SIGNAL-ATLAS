# Emerging insight: knowledge discovery with scientific controls

**Names:** knowledge discovery in databases (KDD), literature-based discovery, cross-domain synthesis, knowledge graph completion/inference, abductive hypothesis generation, and scientific discovery. **Emergence** is a useful metaphor for a nonobvious connection, not evidence that an inferred relation is new or true.

We want a chain:

**Publication -> exact claim -> equations and constraints -> shared concepts -> candidate cross-domain relationship -> falsifiable hypothesis -> test -> reviewed result.**

An AI may propose an analogy between Fourier representations of radio, audio and seismic data because the same mathematics can represent different measurements. But the physical medium, units, sensors, and boundary conditions differ, and a method that works in one domain may fail elsewhere.

**Compression requirements:** preserve a lossless source pointer, license, date/version, assumptions, exact equation (with units), experimental conditions, competing explanations, and uncertainty. Compressed summaries are derived views; they are never the only remaining copy of the evidence.

**Hypothesis card template:**

- Claim: sentence that could be false.
- Derivation: relevant source IDs and page/equation anchors.
- Shared invariant: a precise mathematical statement, not a word similarity.
- Assumptions: every approximation, measurement range and exclusion.
- Prediction: measurable output and expected direction.
- Null: a simpler mechanism that could explain the data.
- Experiment: synthetic/open data, reproducible code and evaluation metric.
- Outcome: supported/not supported/uncertain, including negative results.

**Example candidate, not a discovery:** Can a conditionally valid adaptive STFT rule improve reconstruction on synthetic signals with mixed transient/steady-state content under identical error metrics? Sources: PUB-002, PUB-003. This requires an experiment, not a guess.

**Figure:** [The evidence loop](../../assets/science_discovery_loop.svg).
