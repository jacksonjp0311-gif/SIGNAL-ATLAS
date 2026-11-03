# Signal Atlas v0.7 release summary

## Purpose

v0.7 is a focused step toward v1.0: it turns two dated public observation feeds into a coherent, browsable collection that can be reused by people and AI tools.

## What is included

- A dated NOAA SWPC daily geomagnetic snapshot, source record SRC-144, its normalized JSON representation, and a provenance entry.
- The existing 30-point F10.7 snapshot from v0.6, retained unchanged as an input.
- A 29-row daily comparison for 2026-10-05 through 2026-11-02, joined by date label and exported as JSON and CSV.
- A dataset registry that identifies observed, derived, forecast, and synthetic data as separate kinds. This release's registry contains the two observed inputs, their derived comparison, and the synthetic v0.6 frequency-stability teaching series.
- A searchable Data Explorer, a two-panel teaching chart, a science guide, Lesson 27, a reusable data-collection guide, and an AI-readable packet.
- A roadmap that keeps the work pointed toward v1.0.
- A lineage record derived from the complete v0.6 manifest. All 236 manifested v0.6 files are retained; intentional changes are listed.

The README keeps the evergreen Signal Atlas logo graphic unchanged. The v0.5 and v0.6 archives remain separate versioned releases.

## Validation result

The focused v0.7 suite passed seven tests. The catalog, science, v0.7 data, and inheritance validators passed. The exact commands and their limits are in [RELEASE_AUDIT_v07.md](RELEASE_AUDIT_v07.md).

## Reading the comparison

The NOAA F10.7 feed provides solar radio flux in solar flux units. The geomagnetic snapshot provides estimated planetary Kp values. The Atlas retains all eight three-hour Kp values for each complete day and adds daily mean and maximum fields.

The 2026-11-03 row stays in the archived raw and normalized geomagnetic data, but is marked partial and excluded from the complete daily join. The date-keyed comparison is descriptive; it does not establish that F10.7 caused geomagnetic activity.

## Next release direction

v0.8 should add data batches that close the clearest coverage gaps, keeping the same observed/derived/forecast/synthetic classification and linking each batch to the source catalog, explanation, navigational view, and packet. See the [roadmap to v1.0](ROADMAP_TO_1.0.md).
