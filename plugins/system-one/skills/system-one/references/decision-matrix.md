# Decision matrix — which tier for which task

Condensed from vault note `when-to-use-which-model` (and the notes it cites).
Citations are vault note names. `[inference]` = synthesis, not stated in a source.

## Owner-measured (spoken passages, hand labels)
**Owner-measured (2026-10-03) vs hand-checked labels, 66 spoken passages:** Jev topic question 0.64 top-1; Jev yes/no 0.52; MiniLM 0.37-0.41; Laya 0.23-0.39; BGE-reranker-v2-m3 zero-shot 0.39 (best local on the lenient measure); Qwen3-Reranker-0.6B 0.31; mxbai 0.28; TF-IDF 0.16-0.18. CI about +-0.13, sample built from Jev disagreements: rank, don't read accuracy. For whole notes all but TF-IDF-on-passages are indistinguishable at n=20. Details: docs/SYSTEM-ONE-TRAINING.md.

## Ladder
```
1 deterministic code / regex      free, exact: always first
2 Jev hosted (DEFAULT model)      bounded judgment over messy text: Choice | Score | Noul | jev_* tools
  exceptions -> local substitute: trained MiniLM + logistic regression when labels exist | Laya / Kev when private, offline or high-volume few-option
  narrowing (not a rung): MiniLM / BM25 shortlist only when options > ~240 or candidates will not fit in state
  (NOT for page-finding in long financial PDFs: owner-measured 36/58 vs 40/58 plain text; read all pages + grep - references/anti-patterns.md G)
3 Sonnet - generation, reading, condensation
4 Opus - synthesis, retrieval/routing, contradiction resolution, final answers
```
Basis: code first (how-to-build-with-system-one step 1); "code -> Jev -> text LLM"
(awesome-typesafe-jev); Jev beat every zero-shot local option in the owner-measured table
above (rank, not accuracy); trained MiniLM+LR still beats Jev when labels exist (BANKING77
below); reasoning model only for flagged items (cb-sde-cascade). Sonnet/Opus split is the
owner's rule. Jev-first is the owner's 2026-10-04 default, set after an Opus review: code stays
first because it is free and exact, and the privacy rule stops a full flip.

## Task shape -> first rung
| Shape | Rung | Source |
|---|---|---|
| rule on known fields, math, count, date order | code | jev-1-13-jaggedness #2, #3 |
| candidate spans (emails, phones, money) | regex, tuned to over-find | cb-pre-parsed-value-extraction |
| one of N known options from messy text | Choice | choice, intent-routing |
| is X true of this text | Noul | noul |
| position on an ordered rubric | Score | score |
| rank many candidates vs a query | <=~240 candidates: `jev_rerank` directly; more: shortlist -> Noul per (query, candidate) | cb-reranking |
| dozens of classes + thousands of labels | MiniLM + logistic regression | minilm-embeddings |
| write prose / code / summary / rationale | Sonnet | jev-with-coding-agents, jev-1-13-jaggedness #9 |
| multi-hop reasoning, synthesis across sources | Opus | jev-1-13-jaggedness #4; owner rule |

## Matrix
| | Code/regex | MiniLM | Jev hosted | Laya local | Kev/openjev | Sonnet | Opus |
|---|---|---|---|---|---|---|---|
| Latency | ~0 [inference] | 5.7-6.8 ms CPU (trained LR) | ~100 ms vendor; 111-114 ms measured; 150-500 ms via MCP; 230-317 ms third-party | 23 ms A100; 32.8 ms T4; ~9 ms P50 batched | openjev 48-81 ms; Kev: none published | 195x Jev per case (Sonnet 5, TypeSafe self-run) | 10.4-13.9 s per rubric call (Opus 4.8 reasoning) |
| Cost | 0 | local | $0.042/M input, output free; ~$0.000045 per 8-14-question call | $0 licence | compute | 293x Jev per case | $0.028-0.034 per rubric call (617-805x) |
| Privacy | local | local (hosted if OpenAI embeddings) | state leaves the box | stays on network | local | Anthropic API [inference] | Anthropic API [inference] |
| Calibration | exact | not measured | RLCD per vendor; independent tests show overconfidence on contested/OOD items | ECE 0.081 after temperature refit; raw weak; 0.952 conf at 0.000 acc on Khmer without Router | Kev ships fitted temperature | LLM probabilities drift run to run | same |
| Languages | n/a | not stated | English best; CJK worse — test | EN + 100+ via `laya-multilingual` | not stated | — | — |
| Limits | returns only what it finds | needs labels; nearest-label-name weak (48.6% TREC, 56.5% BANKING77) | 64k/request, 32k state+longest question; 255 options (~240 reliable); Score 2-10 levels | 192-token option budget; degrades past ~20 options; zero-shot 0.362 vs fine-tuned 0.766 | NanoJev games only | — | — |
Sources: models-and-versions, cb-consistency-choices, cb-consistency-nouls,
community-guide-devto, laya, kev, openjev-and-nanojev, minilm-embeddings,
benchmarks-and-comparisons, jev-mcp-server, how-to-build-with-system-one.

## What was actually measured
- Jev rerank (CLERC legal, 40 queries, BM25 top-30): top-1 5% -> 18%, top-10 38% -> 62%; 1,200 calls $0.0645 (cb-reranking).
- Jev skill suggestion (182 skills, 488 requests): wrong loads 16.8% -> 7.3%, needless 9.8% -> 4.0% (cb-skill-suggestion).
- Jev hierarchical fallback (60 10-K filings, 75 groups): forced 39/60; group-if-confident(>=0.9)-else-division 48/60 (cb-classification-using-confidence).
- SOTAAZ (independent, A100, no Jev access): MiniLM+LR TREC 90.4%, BANKING77 90.3%; Laya TREC 86.6%, BANKING77 37.0% default / 46.1% at 512 tokens / 59.1% with MiniLM top-20; openjev BANKING77 66.9%; NanoJev 18.4-31.0% (benchmarks-and-comparisons).
- Third-party Jev BANKING77: 0.870 (72-label pilot with descriptions) vs 76.3% on all 77 (benchmarks-and-comparisons).
- TypeSafe 4-workflow eval (self-run, consensus labels): Jev 67.8%, Sonnet 5 67.8%, Opus 5 73.1% (community-guide-devto).

## Escalation triggers
| Trigger | Go to | Source |
|---|---|---|
| judgment needs meaning, not rules | System One | how-to-build-with-system-one |
| too many options for the model | shortlist or hierarchy walk (beam K=3) | laya, choice, cb-hierarchical-classification |
| Choice confidence below floor (0.3/0.5/0.6/0.75/0.8 seen) | human / bigger model / coarser label | choice, confidence, confidence-gated-routing |
| top probability < 0.60 | `uncertain` -> review | cb-consistency-choices |
| Noul 0.30-0.70 inclusive | `uncertain` -> review | cb-consistency-nouls |
| any per-field P(wrong) > 0.7 | reasoning model re-extracts | cb-sde-cascade |
| confidence < 0.9 on a fine label | parent label or person | cb-classification-using-confidence |
| `jev_decide` escaped / contradicted requirement | human / Opus | jev-mcp-server |
| needs text, rationale or multi-hop | Sonnet (write) / Opus (reason) | jev-1-13-jaggedness |
| sources disagree; multi-note answer | Opus | owner rule |
All thresholds are illustrative; calibrate on labelled data (jevcal: fewer than ~100 labelled rows is not trustworthy — awesome-typesafe-jev).

## Jev vs Laya in one rule (jev-vs-laya)
Privacy hard requirement -> Laya/local. Many options, long inputs, no labels, no
fine-tune capacity -> Jev (or MiniLM+LR with labels). Few options, English, high
volume, binary safety calls -> Laya. Multilingual -> Laya Router.

## Never use a System One model for
- anything code computes exactly (counting, arithmetic, numeric nearness, dates);
- several judgments in one question; System Two / multi-hop indirection;
- more state than the question needs (context rot);
- generating text, code, summaries, explanations; conversation, streaming, tool calls, driving a coding agent;
- exact magnitudes interpolated from Score levels;
- adversarial state treated as safe (an injection filter is not a security boundary);
- non-text input without pre-processing;
- control-rate or perception loops; safety decisions on raw answers;
- decisions needing a written rationale for an auditor; open answer spaces.
Sources: jev-1-13-jaggedness, how-to-build-with-system-one, jev-with-coding-agents,
system-one-model-category, cb-classifying-rag-passages, community-guide-devto,
awesome-typesafe-jev. Laya additionally: zero-shot 50-100 options, long inputs.
NanoJev: any text classification.
