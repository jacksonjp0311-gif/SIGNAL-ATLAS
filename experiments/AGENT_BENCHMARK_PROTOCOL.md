# Future controlled AI research-amortization experiment (not yet run)

**Research question:** With equal or better verifiable answer quality, does retrieval from a versioned Atlas reduce total research cost compared with independent web/RAG research?

## Arms

- A — Baseline agent with approved web search and the same primary-source pool, no prior Atlas cards.
- B — Agent with Atlas packet retrieval, allowed to check original sources whenever necessary.
- Optional C — Strong ordinary RAG system over the same licensed full-text corpus.

Use identical model weights, temperature/seed if available, tasks, evidence sources, time budget, and permitted tools. Randomly assign task order and counterbalance arms. Do not tune retrieval or prompts on the held-out evaluation questions. Use new questions **independently authored and checked by domain reviewers** after the retrieval system is frozen.

## Record for every task

- Exact prompt/question, gold answer with source paragraphs, date and source edition.
- Tool and browser calls, network bytes, documents fetched, source snapshots, retrieval cache hits.
- Input/output model tokens, model reasoning effort if exposed, latency, and priced inference/network costs.
- Up-front corpus preparation and maintenance costs allocated per request, including source freshness checks.
- Blind human or structured citation grading: factual accuracy, support of each claim, omitted caveats, timeliness, and unsafe overreach.
- Answers with unresolved or disputed evidence must be able to say “unknown”.

## Analysis

For N requests, include the **amortized** Atlas build/refresh costs in the treatment arm. Report task-level and aggregate quality-conditioned savings, 95% bootstrap intervals where appropriate, and failure cases. Do not present packet byte-count savings as inference compute savings. Stratify tasks by newly published versus stable content, and original-language versus English-language evidence.

## Admission gate

A claimed improvement requires a pre-registered study, independent gold answers and citation checks, a quality non-inferiority threshold, and a reproducible run receipt. Until then, Research Amortization is a measurable hypothesis supported only by prototype retrieval.
