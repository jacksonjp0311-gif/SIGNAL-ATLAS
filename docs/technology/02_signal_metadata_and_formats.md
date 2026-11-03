# Interoperable signal data and metadata

A signal recording without metadata can become scientifically ambiguous. Distinguish (a) the waveform data itself, (b) sample-rate and time-base, (c) sensor and processing transformations, (d) license, and (e) who produced the record.

## Examples

**SigMF** provides a signal metadata convention for IQ/waveform captures. See existing source `SRC-006` and [official project](https://sigmf.org/).

**FDSN miniSEED 3** offers time-series record metadata for seismology, including exact timing and data integrity fields. [Reference](https://docs.fdsn.org/projects/miniseed3/en/latest/background.html).

**W3C PROV-O** can describe how an experimental dataset was derived from a source record; **DCAT 3** can describe the catalog item itself. [PROV](https://www.w3.org/TR/prov-o/) · [DCAT](https://www.w3.org/TR/vocab-dcat-3/).

These formats are not identical and shouldn't be forced into one schema without an explicit adapter and a documented loss-of-information analysis.

## Minimal pedagogical sample card

```json
{"id":"SYNTH-001","signal_origin":"synthetic","sample_rate_hz":8000,"duration_s":1,"units":"arbitrary","rights":"original synthetic example","time_reference":"relative","processing_steps":[],"recorded_at":null}
```

The example is fictional. It contains no intercepted real communications.
