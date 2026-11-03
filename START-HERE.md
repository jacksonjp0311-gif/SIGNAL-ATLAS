# START HERE — 20-minute atlas orientation

**Current data route (v0.7):** open the [NOAA Data Explorer](site/datasets.html), then read the [space-weather observations guide](docs/science/08_space_weather_observations.md) and [Lesson 27](courses/27_space_weather_data_join.md). The [dataset registry](data/dataset_registry.json) distinguishes observed, derived, and synthetic collections.

**The central insight:** the electromagnetic spectrum is a physical phenomenon; SIGINT is an intelligence discipline drawing information from signals and systems; public-source research is a *way of studying* these disciplines without engaging in interception.

Start with `assets/spectrum_atlas.svg`. The horizontal blocks are widely used RF band names, not active channel allocations.

1. Read [frequency and wavelength](docs/spectrum/01_waves_and_units.md). Calculate wavelength at a frequency using λ = c / f.
2. Read [modulation and observable properties](docs/spectrum/02_signal_families.md).
3. Read [SIGINT definitions](docs/military/01_definitions.md) and [military context](docs/military/02_application_framework.md).
4. Open `site/index.html`, type **FRA**, **NASA**, or **France**, then open an original source.
5. Compare source entries SRC-011 (ASD definitions), SRC-020 (NATO EM warfare), and SRC-029 (US law). Ask what they do—and do not—establish.
6. Open `data/claims.jsonl`. Find C-013 and trace its `source_ids` to the original French military article.

**Success criterion:** you can distinguish a band, an allocation, a technical signal observation, an intelligence claim, and a report about a country's intelligence organization.

## New in edition 0.2

- **Open the visual lab** in `site/index.html` to learn with original SVGs.
- **Look for new evidence:** [Research Desk](docs/research/README.md) → [First batch findings](docs/research/FIRST_BATCH_FINDINGS.md).
- **Want a precise answer?** Search `data/sources.jsonl` or run `python tools/atlas_query.py radar`, then open the linked original URLs.
- **Add findings responsibly:** [Review checklist](docs/research/REVIEW_CHECKLIST.md).

## Science and actual papers (v0.3)

Use [the Science Division](docs/science/README.md), browse the [publication index](documents/INDEX.md), open the **local original PDF briefs**, or launch `site/index.html` and select **Science & Papers**. An external paper can be indexed without having its PDF copied into the repository.

## Edition 0.4 quick links

- [New experimental science lab](courses/18-synthetic-signal-experiment.md)
- [Learn evidence packets](courses/19-evidence-packet-lab.md)
- [Packet implementation guide](docs/research/RESEARCH_AMORTIZATION.md)
- [View actual local test results](experiments/README.md)


## v0.5 quick routes

- **Five minutes:** [Visual topic map](site/topic-map.html) → [Actual NOAA radio flux graph](assets/experiment_noaa_f107.svg) → [Lesson 21](courses/21-observational-solar-radio-flux.md).
- **Science:** [Satellite SAR phase versus amplitude](courses/22-sar-phase-and-intensity.md) and [interferometer calibration](courses/23-calibration-and-source-assumptions.md).
- **Historical evidence:** [Finland](docs/regions/finland.md), [Brazil](docs/regions/brazil.md) and [New Zealand oversight sources](docs/research/SOURCE_REVIEW_v05.md).
- **AI reuse:** [Packet integrity exercise](courses/24-research-packet-integrity.md) and [agent research contract](AGENTS.md).


## Version 1.0

1. Use [Unified Search](site/unified_search.html) to find sources, claims, datasets, lessons, or research documents.
2. Check [dataset coverage](site/coverage.html) for time windows and gaps.
3. Follow [Lesson 30](courses/30-compile-observations-and-provenance.md) from raw input to derived series.
4. Follow [Lesson 29](courses/29-public-sigint-history.md) for public military SIGINT research routes.
