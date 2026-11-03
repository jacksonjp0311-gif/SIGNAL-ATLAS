# Agent-facing research contract

## Two independent operations

**Retrieve from trusted Atlas:** search primary `sources.jsonl`, lookup `claims.jsonl`, verify each `source_id`, return references and uncertainty. The source index alone does not establish truth.

**Conduct candidate research:** retrieve lawful public metadata or licensed texts, produce a candidate with source URL and time scope, check whether another independently obtained source supports it, and write a proposed claim or research gap. Candidate records must never overwrite accepted source IDs or claim history.

## Default answer JSON (template, not a running API)

```json
{
  "question": "How does France publicly define ROEM?",
  "answer": "The French Directorate of Military Intelligence describes ROEM as electromagnetic-origin intelligence.",
  "source_ids": ["REPLACE_WITH_RECORD_ID"],
  "claim_ids": ["REPLACE_WITH_CLAIM_ID"],
  "evidence_type": "institutional-self-description",
  "time_scope": "public 2024–2026 descriptions",
  "limitations": "Not an assessment of current operational capability",
  "status": "retrieved-source-attribution",
  "next_questions": ["How does French usage compare with published NATO terminology?"]
}
```

Only emit actual IDs supported by the corpus; do not use the placeholders literally. For research conclusions, keep sources' independence and rights status explicit.

## Future system integration

- Import `sources.jsonl` as the bibliographic registry.
- Import `claims.jsonl` as attributed statements; **do not automatically treat `evidence_status=verified` as independently proven**.
- Add a read-only retrieval boundary to Pegasus or other agent harnesses initially.
- Keep agent-contributed hypotheses in a separate candidate store until human editorial admission.
- Use content hashes and review history for any future reusable local snapshots.

The included CLI is a lightweight **local metadata lookup**, not a model, autonomous agent, open-web crawler, or military signal receiver.
