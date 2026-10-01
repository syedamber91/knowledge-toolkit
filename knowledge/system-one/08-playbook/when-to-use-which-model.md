---
title: When To Use Which Model
kind: playbook
source: Synthesis of vault notes 00-07 (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [alternatives, routing, cost-latency]
topics: [topic-model-selection, topic-routing, topic-cost-latency, topic-calibration]
---
# When To Use Which Model
> Executable decision matrix: deterministic code vs MiniLM-style embeddings vs a System One model (Jev hosted / Laya local / Kev / openjev) vs Sonnet vs Opus. Ladder, escalation triggers, never-use list. Every number cites the note it came from; trust labels matter.

## 0. The ladder (climb only when the rung below cannot decide)
```
1 deterministic code / regex      exact rules, arithmetic, dates, counting, lookups, candidate finding
2 embedding shortlist (MiniLM)    many options or big corpus -> cut to ~20-30 candidates (or train LR if labels exist)
3 System One decision model       bounded judgment over messy text: Jev hosted | Laya/Kev local
4 Sonnet                          generation, reading/condensing, extraction an LLM must write
5 Opus                            synthesis, multi-hop reasoning, routing over sources, contradiction resolution, final answer
```
Basis: code first ([[how-to-build-with-system-one]] step 1; [[awesome-typesafe-jev]] "Choose the right tool": code -> Jev -> text LLM); shortlist before judging ([[cb-reranking]] BM25 top-30; [[minilm-embeddings]] Laya top-20; [[cb-classifying-rag-passages]] cosine top-12); Jev for bounded judgments ([[jev-introduction]]); LLM for generation ([[jev-1-13-jaggedness]] #9); expensive reasoning model only for flagged items ([[cb-sde-cascade]]). Sonnet-vs-Opus split = owner rule, see [[model-tiering-sonnet-opus]].

## 1. Classify the task shape first
| Shape | First rung that can own it | Evidence |
|---|---|---|
| Rule on known fields, math, count, date order | code | [[jev-1-13-jaggedness]] #2, #3 |
| Find candidate spans (emails, phones, money) | regex (over-find) | [[cb-pre-parsed-value-extraction]] |
| Pick one of N known options from messy text | System One Choice | [[choice]], [[intent-routing]] |
| Is X true of this text | System One Noul | [[noul]] |
| Position on an ordered rubric | System One Score | [[score]] |
| Rank many candidates vs a query | shortlist (BM25/embeddings) -> Noul per pair | [[cb-reranking]], [[jev-mcp-server]] `jev_rerank` |
| Many classes + thousands of labels | trained MiniLM + logistic regression | [[minilm-embeddings]] |
| Write prose / code / summary / explanation | LLM (Sonnet) | [[jev-with-coding-agents]], [[jev-1-13-jaggedness]] #9 |
| Multi-hop / System Two reasoning, synthesis across sources | Opus | [[jev-1-13-jaggedness]] #4 + "avoid System Two tasks"; [[model-tiering-sonnet-opus]] |

## 2. Decision matrix
| | Deterministic code / regex | MiniLM embeddings | Jev (hosted) | Laya (local) | Kev / openjev / other open | Sonnet | Opus |
|---|---|---|---|---|---|---|---|
| Task shape | exact rules, arithmetic, dates, counting, candidate spans | similarity shortlist; trained classifier head | bounded Choice/Score/Noul over text state | same primitives; few options; binary safety calls | same primitives, self-hosted | generation, reading, condensation, extraction it must write | synthesis, routing over sources, hard reasoning |
| Latency | ~0 [inference] | 5.7-6.8 ms CPU (trained LR) [[minilm-embeddings]] | ~100 ms "most queries" (vendor, [[how-to-build-with-system-one]]); 111-114 ms measured mean ([[cb-consistency-nouls]], [[cb-consistency-choices]]); 150-500 ms via MCP ([[jev-mcp-server]]); 230-317 ms per third parties ([[jev-vs-laya]]) | 23 ms A100 (SOTAAZ), 32.8 ms T4, 30-40 ms, ~9 ms P50 batched ([[laya]]) | openjev 48-81 ms on A100; Kev: no numbers ([[openjev-and-nanojev]], [[kev]]) | Sonnet 5 at 195x Jev latency per case (TypeSafe's eval via [[community-guide-devto]]) | Opus 4.8 reasoning 10.4-13.9 s per rubric call ([[cb-consistency-choices]], [[cb-consistency-nouls]]) |
| Cost | 0 | local compute | $0.042/M input, output free ([[models-and-versions]]); ~$0.000043-46 per 8-14-question call | $0 licence, compute only ([[laya]]) | compute only ([[kev]]) | 293x Jev cost per case (Sonnet 5, [[community-guide-devto]]); list price not in vault | $0.028-0.034 per rubric call, 617-805x Jev ([[cb-consistency-choices]], [[cb-consistency-nouls]]) |
| Privacy | local | local (MiniLM); hosted if `text-embedding-3-small` ([[cb-classifying-rag-passages]]) | state leaves the box to TypeSafe or a gateway ([[privacy-and-cost-gates]]) | stays on your network ([[jev-vs-laya]]) | local | Anthropic API [inference] | Anthropic API [inference] |
| Calibration | exact | not measured in sources ([[minilm-embeddings]]) | RLCD-calibrated per vendor ([[ai-primer-calibrated-decisions]]); independent: overconfident on contested/OOD items ([[awesome-typesafe-jev]]) | ECE 0.081 after temperature refit, raw calibration weak; 0.952 confidence at 0.000 accuracy on Khmer w/o Router ([[laya]]) | Kev ships fitted temperature; Rizzo Flow uncalibrated ([[system-one-alternatives-overview]]) | LLM-stated probabilities flip run to run ([[cb-consistency-nouls]]) | same; Opus 92.5% raw agreement over 15 repeats ([[cb-consistency-choices]]) |
| Languages | n/a | not stated | English best; CJK handled but worse; test + watch confidence ([[models-and-versions]]) | English 421M; `laya-multilingual` 322M, 100+ langs, 45/51 above 3x random ([[laya]]) | Kev: not stated ([[kev]]) | not in vault | not in vault |
| Hardware | none | CPU | none (hosted) | ~1 GB RAM, CPU ok ([[laya]]) | 0.8B Mac .. 27B on 80 GB GPU (Kev); 26B GPU (openjev) | hosted | hosted |
| Limits | regex can only return what it finds | needs labels for LR; nearest-label-name weak (48.6% TREC, 56.5% BANKING77) | 64k tokens/request, 32k state+longest question; 255 Choice options ("reliably ~240"); Score 2-10 levels ([[models-and-versions]], [[http-api-reference]], [[cb-classification-using-confidence]]) | 192-token shared option budget; degrades past ~20 options; zero-shot 0.362 vs fine-tuned 0.766 ([[laya]]) | NanoJev = games only ([[openjev-and-nanojev]]) | — | — |
| Failure modes | brittle on semantics | no typed schema; no calibrated probs | 9 jaggedness modes ([[jev-1-13-jaggedness]]); injection can move answers | many options; context 512 (vanekt) vs 8,192 (Menon) unresolved | name collisions; server config swings results | LLM extraction can be schema-valid yet fabricated (shown for gpt-5.4-mini, [[cb-sde-cascade]]); run-to-run drift ([[cb-consistency-nouls]]) | slow/expensive; use sparingly |
| What was measured | — | SOTAAZ: TREC 90.4%, BANKING77 90.3% trained LR ([[benchmarks-and-comparisons]]) | rerank top-1 5%->18%, top-10 38%->62% ([[cb-reranking]]); skill loads 16.8%->7.3% ([[cb-skill-suggestion]]); 39/60 forced vs 48/60 with fallback ([[cb-classification-using-confidence]]) | SOTAAZ TREC 86.6%, BANKING77 37.0% default / 59.1% with MiniLM shortlist | Kev-9B 0.822 vs Jev 0.857 (author); openjev BANKING77 66.9% | Sonnet 5 67.8% on TypeSafe's 4-workflow eval ([[community-guide-devto]]) | Opus 5 73.1% same eval |

## 3. Escalation triggers (rung N -> N+1)
| Trigger | Escalate to | Source |
|---|---|---|
| Code cannot express the judgment (meaning, tone, intent, relevance) | System One | [[how-to-build-with-system-one]] |
| More options than the model handles well (Laya >~20; Jev >255 hard cap, ~240 reliable) | shortlist first, or walk a hierarchy | [[laya]], [[choice]], [[cb-hierarchical-classification]] |
| Choice `confidence` below floor (examples: 0.3 triage, 0.5, 0.6, 0.75, 0.8) | human / bigger model / coarser label | [[choice]], [[confidence]], [[confidence-gated-routing]], [[how-to-build-with-system-one]] |
| Top probability < 0.60 -> label `uncertain` | human review | [[cb-consistency-choices]] |
| Noul in 0.30-0.70 inclusive -> `uncertain` | human review | [[cb-consistency-nouls]] |
| Any per-field P(wrong) > 0.7 (max-gated) | reasoning model re-extracts | [[cb-sde-cascade]], `jev_audit` in [[jev-mcp-server]] |
| Classification confidence < 0.9 | report parent label (division) or hand to person | [[cb-classification-using-confidence]] |
| `jev_decide` escaped (`ask_user`/`investigate`/`none`) or contradicted requirement | human / Opus | [[jev-mcp-server]] |
| Task needs text output, rationale, or multi-hop reasoning | Sonnet (write) / Opus (reason) | [[jev-1-13-jaggedness]], [[community-guide-devto]] |
| Sources disagree, or answer must be synthesized from several notes | Opus | [[model-tiering-sonnet-opus]] |
All thresholds above are the sources' illustrative values; every source says tune on your own labelled data ([[confidence]], [[awesome-typesafe-jev]] jevcal: <~100 labelled rows not trustworthy).

## 4. Jev vs Laya in one rule
Privacy hard requirement -> Laya/local regardless of accuracy. Many options, long inputs, zero labels, no fine-tune capacity -> Jev (or trained MiniLM+LR if labels exist). Few options, English, high volume, binary safety calls -> Laya. Multilingual -> Laya Router. ([[jev-vs-laya]]). Jev's "87% vs Laya 42% on many options" is likely overstated: 0.870 was a 72-label, descriptions-supplied pilot; 76.3% on all 77 ([[benchmarks-and-comparisons]]).

## 5. Never use a System One model for
From [[jev-1-13-jaggedness]] ("As a reminder, avoid") and [[how-to-build-with-system-one]]:
- anything code can compute exactly (counting, arithmetic, numeric nearness, date order/gaps/windows);
- several judgments hidden in one question; System Two / multi-hop indirection;
- more state than the question needs (context rot);
- generation of text, code, summaries, explanations, rationales ([[jev-with-coding-agents]], [[system-one-model-category]]); Jev also cannot hold a conversation, stream, call tools, or power a coding agent;
- exact magnitudes interpolated from Score levels (2c);
- trusting adversarial state as safe — injection filter is "only one filter", not a security boundary ([[cb-classifying-rag-passages]]);
- non-text input without pre-processing ([[state]]);
- control-rate or perception loops ([[community-guide-devto]], jev-drone); safety decisions on raw answers (HA-Jev, [[awesome-typesafe-jev]]);
- decisions needing a written rationale for an auditor, genuinely open answer spaces ([[community-guide-devto]]).
Laya additionally: zero-shot with 50-100 options; long inputs ([[laya]]). NanoJev: any text classification ([[openjev-and-nanojev]]).

## 6. Disagreements an agent must not paper over
- **Jev latency:** ~100 ms (vendor) / 150 ms ([[use-case-map]]) / 70-500 ms ([[community-guide-devto]]) / 111-114 ms measured / 230-317 ms (third parties). Network path + region differ [inference].
- **Rate limits:** 100K tokens/s + 40 req/s ([[models-and-versions]]) vs 250,000 tokens/s + 1,200 req/min ([[community-guide-devto]]). Trust first-party; limits "change without notice".
- **Context:** 64k/32k ([[models-and-versions]]) vs 32,000 total ([[openrouter-jev-guide]]) vs "~4,000" ([[jev-vs-laya]], vanekt).
- **Calibration:** vendor "calibrated instead of overconfident" ([[how-to-build-with-system-one]]) vs ChaosNLI ECE gap 0.264 on contested items and dice test 82.9% on one face ([[awesome-typesafe-jev]]).
- **Jev typed-decisions accuracy:** 0.727 vs 0.754 ([[benchmarks-and-comparisons]]).

## Related
[[model-tiering-sonnet-opus]] · [[agent-operating-protocol]] · [[question-design-checklist]] · [[anti-patterns]] · [[privacy-and-cost-gates]] · [[cheat-sheet]] · [[system-one-alternatives-overview]] · [[topic-model-selection]] · [[topic-routing]]
