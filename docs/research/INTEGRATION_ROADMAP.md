# Integrating Signal Atlas with future agent systems

GitHub is the initial canonical **content repository**. The Atlas exposes portable JSONL, CSV, Markdown and SVG rather than requiring a specific agent harness.

## Phase A — Read-only retrieval

Mount a tagged Atlas snapshot in Pegasus or another harness; let agents query source cards and citations. Preserve provenance, time scope and confidence in every generated response. Measure citation correctness on benign historical and synthetic-signal questions. **No autonomous editing of accepted material.**

## Phase B — Candidate research

Agents can create new research proposals in a separate sandbox. Proposals require source URLs, date and publication context, licensing status, alternative explanations, and a claim classification. Automated tests detect broken IDs and unsupported claims, but a human reviewer decides whether to admit each update.

## Phase C — Versioned evidence exchange

Make accepted findings reproducible with versioned snapshots, hashes and rollback. Export only bounded, rights-compatible claims. Measure retrieval quality, freshness, false-citation rates, and unresolved questions.

## Phase D — Optional relationships with other systems

Pegasus can retrieve Atlas references; Symbiote could exchange provenance-rich, reviewed findings after separate integration testing. Feedback is evidence to investigate, not automatically validated knowledge. Keep candidate research separate from the stable knowledge base.

**Status:** conceptual integration roadmap only. The package includes an offline metadata CLI, **not** a deployed plugin, live crawler, network service or linked agent system.

## Edition 0.4 integration boundary

A concrete read-only JSON packet prototype now exists at `tools/packet_query.py`. This is not a deployed API and is not connected to any external agent system. Integration should first test citations, version hashes, permissions, cache expiry and candidate isolation, then compare performance against a strong baseline.
