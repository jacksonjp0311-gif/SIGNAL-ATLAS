# Data collection guide

This guide describes how to add a useful data collection to the Signal Atlas and connect it to the rest of the library.

## Add a data batch

1. **Choose a question and a collection.** Record what the data can help someone compare, inspect, or learn.
2. **Add a source card.** Give the source a stable SRC ID in sources.jsonl and the matching row in sources.csv. Keep the direct data-product link.
3. **Keep a dated input.** Save the exact fetched data under data/datasets with a date in the file name. Do not replace a previous release's snapshot with the newest contents of a rolling feed.
4. **Normalize without hiding the original.** Retain the raw file. In normalized data, keep supplied values and units, represent missing values explicitly, and record how the parser treats sentinels.
5. **Register the dataset.** Add stable dataset IDs and use one of four kinds: observed, derived, forecast, or synthetic. State whether an observation is estimated, preliminary, or partial in a separate descriptive field.
6. **Record the data path.** For each derived product, list input files, code used, join or calculation method, output files, and SHA-256 hashes in a provenance JSONL record.
7. **Make it useful to people and tools.** Connect the batch to a short explanation, a learning route or data view, and a machine-readable packet that carries the source IDs, date window, method, and limitations.
8. **Check the collection.** Run the relevant parser tests and catalog, science, and release validators. Keep the exact command and result in the release audit.

## Classification

- **Observed:** a measurement series or its normalized representation. Preserve the provider's distinction between directly observed and estimated values.
- **Derived:** an output calculated from one or more inputs. State the transformation and keep the input files.
- **Forecast:** a future estimate or outlook; never merge it with observations without labeling.
- **Synthetic:** generated teaching or test data; do not present it as a field measurement.

The dataset registry is the discovery index. The source catalog explains where each collection comes from. The provenance ledger explains how its local files relate. A packet packages these links and the interpretation limits for reuse.

## Example: the v0.7 NOAA collection

The v0.7 space-weather batch contains two observed inputs, a derived date-keyed table, and a separately labeled synthetic frequency-stability example. Its incomplete current-day row stays in the raw data but is not promoted to a complete daily comparison. The [Data Explorer](../../site/datasets.html), [registry](../../data/dataset_registry.json), [provenance records](../../data/provenance/release_v07_sources.jsonl), and [research packet](../../data/packets/examples/space-weather-noaa-2026-11-03.v0.7.packet.json) show the full path.
