# Lesson 25 — Frequency stability and measurement limits

## Goal

Explain why an oscillator's accuracy, stability, calibration traceability, and measurement uncertainty are different questions. Reproduce a deterministic synthetic frequency-stability calculation and identify what its result cannot establish.

## Core ideas

- Frequency is a rate; a time series can reveal offset, drift, and variation at different averaging intervals.
- A stability statistic must name its estimator, sampling assumptions, units, and averaging interval `τ`.
- Calibration relates a stated measurand to a reference under defined conditions. A service description is not an instrument's calibration certificate.
- A small Allan deviation does not by itself prove accuracy or a traceable reference.
- The SI definition of the metre fixes the speed of light's numerical value; that definition does not erase uncertainty in real measurements.

## Activity

Run `python tools/frequency_stability_lab.py --output data/experiments/frequency_stability_v06.json`. For each reported `τ`, inspect the number of non-overlapping averages, the input data hash, and the estimator. Re-run the command and compare the output bytes.

## Explain

Write a two-sentence interpretation for one averaging interval. Name the sample source, state that the data are synthetic, and distinguish the computed stability measure from accuracy. Propose one additional reference or environmental measurement needed for a real calibration study.

## Assessment

Full credit requires a reproducible output, correct units, a named `τ`, the distinction between stability and accuracy, and one limitation. No live RF collection is part of this activity.

## Sources

[NIST SP 1065](../docs/science/07_frequency_stability_and_uncertainty.md), [NIST SI definition](https://www.nist.gov/pml/special-publication-330/sp-330-section-2), and [calibration services](https://www.nist.gov/pml/time-and-frequency-division/time-services/calibration-services-time-and-frequency-division).
