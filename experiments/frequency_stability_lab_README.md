# Synthetic frequency-stability lab

`python tools/frequency_stability_lab.py --output data/experiments/frequency_stability_v06.json`

The standard-library script generates a deterministic synthetic fractional-frequency sequence from seed 1065 and calculates non-overlapping Allan deviation at several averaging times. It reads no external or live signal data. The seed, generator, sample count, interval, tau list, units, input SHA-256, formula, and output values are recorded in the JSON result.

Expected reproduction: two executions with the same Python implementation and command produce semantically identical JSON values. JSON indentation and platform newline conversion may affect file bytes if redirected differently; the script writes UTF-8 LF bytes directly.

This is a method demonstration, not a model of a particular oscillator, a calibration result, or evidence about achievable instrument performance. NIST SP 1065 is linked as a method reference; it is not embedded in this repository.
