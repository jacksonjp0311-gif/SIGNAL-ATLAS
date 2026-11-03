# Signal mathematics: mapping observed patterns to equations

## Complex exponential and Fourier transform

A pure sinusoid is periodic; any sufficiently well-behaved signal can be studied in terms of frequency content. A conventional continuous Fourier transform is

`X(f) = integral_{-infinity}^{infinity} x(t) exp(-j 2 pi f t) dt`.

The complex magnitude represents spectral amplitude, while the phase captures alignment that magnitude-only summaries discard. The transform does **not** tell you why a component exists.

## Sampling and aliases

For a signal bandlimited strictly below `B Hz`, sampling faster than `2B` permits ideal reconstruction under the classical sampling assumptions. Practical antialias filtering and the difference between analog frequency support and sampled baseband must be included in an instrument design.

Example: a 7 Hz sinusoid sampled at 10 samples per second has the same sample values as a -3 Hz sinusoid (`7 - 10 = -3`); under real-valued sinusoidal conventions this can appear as a 3 Hz component. The visual is a mathematical illustration, **not an intercepted transmission**.

## Spectral resolution

A shorter analysis window improves localization of changes but broadens frequency features. A longer window improves frequency resolution while blending neighboring events in time. Adaptive-window methods are an active research topic, not a license to ignore tradeoffs.

## Noise and SNR

Signal-to-noise ratio (`SNR`) in power units: `10 log10(P_signal / P_noise)` dB. State bandwidth, noise model, detector and estimator: SNR alone does not establish detection accuracy.

## Information is not unlimited

Shannon's capacity for an ideal bandlimited additive-white-Gaussian-noise link is `C = B log2(1 + SNR_linear)` bits/s. It is a model-specific upper bound, not a measured rate for every propagation or interference environment.

**Figures:** [Fourier dual view](../../assets/science_fourier_bridge.svg) and [sample aliasing](../../assets/science_sampling_aliasing.svg).

**Sources:** [PUB-002](../../documents/publications/reference-cards/PUB-002.md) (STFT preprint); [PUB-003](../../documents/publications/reference-cards/PUB-003.md) (sampling recovery survey); [PUB-012](../../documents/publications/reference-cards/PUB-012.md) (MIT signals course).
