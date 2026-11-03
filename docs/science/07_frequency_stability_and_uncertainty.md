# Frequency stability, calibration, and uncertainty

## Why frequency measurements need a time scale

Frequency is a rate of phase advance. A measured oscillator can have a mean offset from a reference, slow drift, and noise that changes over different averaging intervals. Those are separate properties. Accuracy describes closeness to a defined value or reference under stated conditions; stability describes variation over an interval and method. A calibration result also depends on traceability, the measurand, the reference, and an uncertainty statement.

NIST's *Handbook of Frequency Stability Analysis* (SP 1065) is a tutorial and reference for measurement systems, sample handling, stability estimators, and reporting. The NIST SI Brochure defines the metre using the fixed numerical value of the speed of light, exactly 299,792,458 m/s. This exact definition does not make any physical measurement error-free. NIST's service page gives examples of time/frequency calibration and phase or amplitude modulation-noise measurements; it is a service description, not evidence about an unobserved device.

## A compact Allan variance definition

For a sequence of adjacent, equally spaced averages of fractional frequency, \(ar y_i(	au)\), the basic Allan variance estimate is

\[
\widehat{\sigma_y^2}(	au)=rac{1}{2(M-1)}\sum_{i=1}^{M-1}\left(ar y_{i+1}(	au)-ar y_i(	au)ight)^2,
\qquad \widehat{\sigma_y}(	au)=\sqrt{\widehat{\sigma_y^2}(	au)}.
\]

Here \(	au\) is the averaging interval and \(M\) is the count of non-overlapping block averages. This simple estimator requires regularly sampled fractional-frequency data and at least two adjacent block averages. Different data products and noise types can call for overlapping Allan deviation or other estimators; report the selected estimator rather than treating the word “stability” as a complete method.

## Reproduce the synthetic lab

Run `python tools/frequency_stability_lab.py --output data/experiments/frequency_stability_v06.json`. The script uses only Python's standard library and a fixed random seed to create an explicitly synthetic fractional-frequency series, groups samples at stated averaging intervals, and computes the equation above. It reads no receiver, public transmission, or external measurement.

Check the output's generator, seed, sample interval, sample count, tau values, units, and input digest before reuse. The data illustrate how interval changes the statistic; they do not model a particular clock, demonstrate calibration quality, or establish a universal noise law.

## Evidence to record in a real measurement

Record the measurand, instrument and firmware where relevant, reference source and traceability, sampling and gating, averaging interval, estimator, environmental conditions, calibration date, uncertainty budget, missing-data policy, and analysis version. Preserve raw authorized samples separately from derived values and hash both. A hash protects byte-level provenance; it does not validate the measurement.

## Sources and limits

- [NIST SP 1065 publication record](../../data/sources.csv) · [PUB-024](../../documents/publications/reference-cards/PUB-024.md)
- [SI Brochure metre definition](https://www.nist.gov/pml/special-publication-330/sp-330-section-2) · [PUB-025](../../documents/publications/reference-cards/PUB-025.md)
- [NIST time and frequency calibration services](https://www.nist.gov/pml/time-and-frequency-division/time-services/calibration-services-time-and-frequency-division)
- [Frequency measurement record](../../documents/publications/reference-cards/PUB-026.md)

All external technical pages remain link-only. Their contents can change; recheck the source pages and report the version and date when making a formal technical claim.
