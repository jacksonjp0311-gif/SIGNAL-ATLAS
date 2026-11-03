# Observational radio measurements — v0.5

## Why this matters

Signal Atlas now contains a small authentic measurement sample rather than only synthetic waveforms. NOAA's F10.7 solar radio-flux values represent emissions near 2800 MHz, or ~10.7 cm wavelength. The sample is a 30-day observational series, **not** a raw baseband IQ recording.

## Data and experiment

- Local excerpt: [`data/datasets/noaa_f107_30day_2026-11-02.json`](../../data/datasets/noaa_f107_30day_2026-11-02.json)
- Plot: [`assets/experiment_noaa_f107.svg`](../../assets/experiment_noaa_f107.svg)
- Reproducible calculation: [`experiments/noaa_f107_lab.py`](../../experiments/noaa_f107_lab.py)
- Source: https://services.swpc.noaa.gov/products/10cm-flux-30-day.json (SRC-116)
- Physical description: https://www.spaceweather.gov/phenomena/f107-cm-radio-emissions (SRC-114)

## Physical scale

For vacuum propagation, wavelength = c / frequency. At f = 2800 MHz, lambda ≈ 0.107 m. This calculation concerns scale, not actual terrestrial propagation or military spectrum use.

## Limitations

Do not use this 30-day period to infer solar-cycle trends, predict communication outages, or assert a causal association with ionospheric conditions without independent measurements and controlled analysis. The provider's time tags lack an explicit UTC offset in the captured JSON.
