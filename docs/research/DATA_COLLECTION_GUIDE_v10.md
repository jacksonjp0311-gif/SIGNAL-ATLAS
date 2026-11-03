# Collection and compilation guide v1.0

## Goal

Compile useful public observations and research records while keeping each item's origin, time basis, units, evidence role, and limitation attached.

## Collection steps

1. Record the publisher, exact URL, UTC capture interval, response metadata, raw bytes and SHA-256, row count, fields, time coverage, units, and quality flags.
2. Store new captures under dated names; never overwrite an earlier release.
3. Check parseability, required fields, dates, duplicate keys, and data kind: observed, derived, or synthetic.
4. Keep derived joins separate. State the exact key and unmatched-row rule.
5. Update the dataset registry and provenance ledger with source IDs and file hashes.
6. Rebuild SQLite and unified search from frozen local inputs.
7. Use the coverage view to find time gaps, domain imbalance, and missing routes.
8. Run focused checks and record commands, results, and limitations.

The [coverage view](../../site/coverage.html) separates 10 registrations: daily F10.7 and estimated Kp, minute-scale plasma and magnetic field, explicit joins and context views, a synthetic lab, and a six-hour GOES X-ray capture with paired channels.

These records are not one continuous or interchangeable time series. Future captures should extend the dated evidence rather than replace earlier windows. Ordinary builds and tests do not fetch live data.
