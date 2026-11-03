# Signal Atlas v0.8 release summary

## Purpose

v0.8 extends the linked data collection with one-minute solar-wind plasma and magnetic-field observations. This adds an in-situ upstream measurement layer alongside the retained solar radio-flux and geomagnetic-index series.

## Contents

- Full dated NOAA SWPC plasma and magnetometer JSON snapshots, with metadata and SHA-256 digests.
- Active-selected views that preserve the primary-source flags and spacecraft identity.
- An exact paired series keyed by both unchanged time tag and spacecraft source.
- Partial UTC-day summaries with coverage counts and complete daily Kp shown only as separate context.
- Two new source cards, four registry entries, source and transformation provenance, an offline full-text index rebuild, and a searchable Solar-wind Explorer.
- A two-panel educational SVG, science guide, Lesson 28, data-collection guide, and AI-readable packet.
- A v0.7 lineage manifest check. Earlier version packages and the evergreen README logo remain preserved.

## Data coverage

The frozen endpoint responses contain 3,247 plasma and 3,432 magnetometer records. The active-selected views contain 1,085 and 1,243 rows. Pairing on exact `time_tag` and `source` yields 1,031 measurements. They fall into two incomplete UTC-day buckets with 740 and 291 paired minutes, respectively. Actual values and coverage fractions are in the registry and data files.

## Next toward v1.0

Expand the time window and add more useful signal families and public research records, while keeping observed data, derived products, forecasts, and synthetic teaching series clearly separated. Improve cross-library search and finish the v1.0 coverage view against the full collection.

