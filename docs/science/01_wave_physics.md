# Wave physics: the physical layer

A wave is a propagating disturbance; a signal is a measurable variation carrying information about a phenomenon. Electromagnetic waves arise from coupled electric/magnetic fields. In vacuum they propagate at `c = 299,792,458 m/s`.

## Frequency, wavelength and period

`lambda = v / f` and `T = 1/f`. In vacuum, `lambda = c/f`; in a material or waveguide, use the appropriate **phase velocity** and dispersion model instead of treating `c` as universal.

At 100 MHz in vacuum, the wavelength is about 2.9979 m. At 1 GHz, it is about 0.29979 m. Ten times higher frequency implies ten times shorter vacuum wavelength.

## The electromagnetic spectrum

Frequency and wavelength are *physical* quantities. Radio-band naming conventions and government frequency allocations are *human taxonomies*. Recorded energy is *measurement data*. They must never be treated as equivalent evidence.

## Inverse problems

Given a field observation `y = H(x) + n`, estimate the unknown state `x`. Identifiability depends on what `H` measures, the noise `n`, sampling quality, calibration and the assumptions used for inversion. Different `x` may produce nearly the same `y`.

**Figure:** [Frequency/wavelength axis](../../assets/science_wave_scale.svg).

**Read next:** [Fourier and sampling](02_signal_mathematics.md); publications [PUB-005](../../documents/publications/reference-cards/PUB-005.md), [PUB-007](../../documents/publications/reference-cards/PUB-007.md).

## Check your understanding

If a frequency doubles in free space, what happens to the wavelength? Why can a physical wave model disagree with a measured signal after sampling? Which assumptions would you check first?
