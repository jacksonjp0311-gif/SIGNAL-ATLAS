# Building an evidence picture when sources are incomplete

## A reproducible example: understanding an institution's publicly reported mission

**Question:** Does official documentation describe national SIGINT support to military decision-makers?

1. Record the exact mission text, publication year and source (e.g. SRC-012 for Canada).
2. Compare it with the agency's publicly stated statutory remit (SRC-033), noting this is the same institutional family, not independent confirmation of effectiveness.
3. Seek published parliamentary, legal or public audit context, explicitly distinguishing verified facts from claims.
4. Link sources to a bounded claim in `claims.jsonl`, preserving `asserted_by`, jurisdiction and dates.
5. Record unanswered questions about governance or terminology as a `GAP-*` research item.

### Confidence matrix

| Class | Description | Example |
|---|---|---|
| Direct source fact | Original source says a specified thing | Source X describes its public mandate |
| Attributed assessment | One government evaluates another | US report assesses China's military |
| Corroborated public claim | Independent sources agree on an explicit public fact | Two independent histories support a dated historical event |
| Analytical hypothesis | Possible conclusion requiring testing | Similar terms may reflect differing organizational models |
| Unknown | Unsupported by sources in this package | Whether an unpublished contemporary capability exists |

**Never transform the lack of public information into a precise guess about live operations, emitter locations or access methods.** Even if multiple pages suggest a pattern, constrain your conclusion to what those pages can legitimately establish.
