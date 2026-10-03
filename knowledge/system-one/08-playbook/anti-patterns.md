---
title: Anti Patterns
kind: playbook
source: Synthesis of every Gotchas/Contradictions section in the vault (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [model-limits, guardrails, evaluation]
topics: [topic-guardrails, topic-calibration, topic-model-selection]
---
# Anti-Patterns
> Every documented failure mode, trap and pitfall across the vault, grouped, each with the fix and the note that proves it. Section F lists source disagreements and vendor bias.

## A. Asking the model the wrong kind of question (jaggedness, `jev-1.13`)
| Anti-pattern | Fix | Source |
|---|---|---|
| Counting in one question (error grows with size) | one Noul per item, sum in code | [[jev-1-13-jaggedness]] #2a |
| Numeric representations (hex, RGB, assembly) | convert in code; pass named bucket | #2b |
| Interpolating exact magnitudes from Score | threshold on expectation only | #2c |
| Date order/gap/window | Choice per date part + "not stated"; code does calendar math | #3, [[cb-date-extraction]] |
| Indirection, double negatives, property-of-a-property | direct wording, name the field | #4 |
| Big state of irrelevant detail | filter first; relevance Noul | #5 |
| Assuming state is safe | explicit criteria; test adversarial cases | #6 |
| Instructions and criteria disagree (true = "no") | align; criteria extend the instruction | #7 |
| Assuming P(q) + P(not q) = 1, or Noul = Choice | ask each decision one way; identities in code (0.72 + 0.47 = 1.19) | #8 |
| Generation by chained choices | regex/LLM candidates, Jev picks | #9 |
| Hiding several judgments in one question / "analyze and decide" | atomic questions, compose in code | [[primitives-overview]], [[noul]] |
| Using Jev as the coding agent's LLM | no such setting; Jev is called by code | [[jev-with-coding-agents]] |

## B. Question-wording traps
- Vague/overlapping option descriptions; no `other` option -> forced misclassification ([[choice]]).
- Naming a question after its parameter ([[cb-function-calling]]); topical question where a narrow fact decides ("same paragraph" collapsed lists 17 -> 12 blocks, [[cb-structure-recovery]]).
- Score levels as numbers or degrees (0.55/0.33 vs 0.0/1.0); multi-dimensional levels; examples unlike real inputs ([[score]]).
- Inverted Noul ("free of personal data?"); compound Noul ([[noul]]).
- Subject-matter gate questions that can't separate "explain a monad" from a skill request ([[cb-skill-suggestion]]).
- Labels read literally ("human" -> `entity`, 0/65) without one-line descriptions ([[openjev-and-nanojev]]).
- Putting the include/exclude decision inside the question ([[cb-classifying-rag-passages]]).
- Stale skill -> agent invents request/response fields ([[typesafe-agent-skill]]); trusting agent-written questions unreviewed ("agents aren't great at writing questions").

## C. Confidence misuse
| Anti-pattern | Why wrong | Source |
|---|---|---|
| Treating confidence/probability as correctness | calibration is over groups; 1.0 describes the distribution | [[ai-primer-calibrated-decisions]], [[score]] |
| One global threshold | thresholds scale with risk; per action | [[confidence]], [[confidence-gated-routing]] |
| Single 0.5 cut on a Noul | 0.49 vs 0.51 flip actions; `covered` ranged 0.43-0.53 across runs | [[cb-consistency-nouls]] |
| Reading Noul 0.5 as "medium" | it is uncertainty, not degree | [[noul]], [[primitives-overview]] |
| Carrying a Noul threshold to a Choice | different questions, different numbers | [[jev-1-13-jaggedness]] #8 |
| Thresholds everywhere | argmax needs none; statistical algorithms should use probabilities | [[typesafe-agent-skill]] |
| Trusting `confidence` to capture a close runner-up | published formula depends only on peak and option count | [[community-guide-marktechpost]]; contradicts [[cb-classification-using-confidence]] (see F) |
| Multiplying per-argument probabilities | falls with argument count; use min | [[cb-function-calling]] |
| Averaging verifier flags | one confident red flag gets "averaged into silence"; use max | [[cb-sde-cascade]] |
| Vague holistic "is this good?" judge | mushy, uncalibrated (0.56 vs per-field 0.95) | [[cb-sde-cascade]] |
| Same score = same situation | 1.0 can be all-L1 or half L0/half L2 | [[score]] |
| High confidence = task fits model | jaggedness cases can still return 0.97 | [[jev-1-13-jaggedness]] |
| Thresholds fitted on tiny sets | <~100 labelled rows untrustworthy (jevcal); 14/21/10/24-item examples | [[awesome-typesafe-jev]] |
| Thresholds transferred across datasets | Janus: optimal threshold, accuracy-gap sign, payoff all changed | [[awesome-typesafe-jev]] |
| Repeatability read as accuracy | Haiku t=0 100% agreement says nothing about correctness | [[cb-consistency-choices]] |
| Alias drift | `jev-latest` moves; pin the version you tuned; log `response.model` | [[models-and-versions]] |

## D. Architecture / pipeline traps
- Sequential calls for questions that could be batched (smart-home "wrong way") ([[demo-smart-home]], [[speculative-fan-out]]).
- Acting on a speculative answer outside its branch ([[speculative-fan-out]]).
- Agent `while` loops where a workflow suffices ("every loop is another opportunity to go off the rails") ([[how-to-build-with-system-one]]).
- Trusting similarity rank: the injection passage ranked 1st, the corrector 7th ([[cb-classifying-rag-passages]]).
- Treating an injection filter as a security boundary ([[cb-classifying-rag-passages]]); `jev_screen` is advisory — the agent must enforce ([[jev-mcp-server]]).
- Merging evidence and conflict blocks; reordering first-match rules (contradiction must precede relevance floor) ([[cb-classifying-rag-passages]]).
- Expecting reranking to fix recall ([[cb-reranking]]); reading a Choice winner as an answer without an `exists` check ([[cb-line-by-line-search]], `jev_find`).
- Regex that under-finds (a missed candidate can never be returned); no `none` handling ([[cb-pre-parsed-value-extraction]]).
- `to_decimal` assuming `1,315.50` convention on `€1.315,50` ([[cb-pre-parsed-value-extraction]]).
- Schema validation as proof: schema-valid fabrication passes jsonschema ([[cb-sde-cascade]]); `jev_compare` `same_fact` means agreement, not truth ([[jev-mcp-server]]).
- Greedy taxonomy walks (2/4 vs beam 4/4; catch-all leaf attracted probability) ([[cb-hierarchical-classification]]).
- Pushy suggestion wording (wrong suggestion is worse than none; 7 of 315 broken) ([[cb-skill-suggestion]]).
- Judging a feature question on 60 examples (rare signals look useless); revising questions casually (each revision = full pass over all rows) ([[cb-autoresearch-feature-discovery]]).
- Laya English root on non-Latin scripts: 0.000 accuracy at 0.952 confidence — use the Router ([[laya]]).
- Laya with 77 options at default 192-token option budget (37.0%) ([[laya]], [[minilm-embeddings]]).
- Decomposition is not free: 12-14 dimension scores beat a direct question (0.9076 vs 0.8373) but flagged ~25x more hard benign rows as attacks (Jev Judge vs Dimension Scores, [[awesome-typesafe-jev]]).
- Sorting by probability: two-decimal outputs left 53/360 rows tied at 0.99; batching 40 rows turned a passing gate into a failure (jev-orderby-bench, [[awesome-typesafe-jev]]).
- Forced answers without a no-match option: KoBBQ 79% stereotype picks when "unknown" removed ([[awesome-typesafe-jev]]).
- Over-trusting gates against adversarial text: authority framing moved 3/30 dangerous commands; blunt injections caused 10% false denials (jev-engineering); pi-verdict "can be swayed" ([[awesome-typesafe-jev]]).

## E. Operational / SDK / security traps
- Retrying 429/529 immediately — use exponential backoff; SDKs do it ([[http-api-reference]]). Retrying ambiguous network failures can double-bill (jev-mcp never does) ([[jev-mcp-server]]).
- Raising worker pools fast: 8 already hits a shared-key rate limit; endpoint rate-limits above ~8 ([[cb-autoresearch-feature-discovery]], [[cb-entity-alignment]]). Limits change without notice ([[models-and-versions]]).
- Debug logging in production: bodies are NOT redacted ([[sdk-python-usage]], [[sdk-javascript-api]]).
- API key in browser JS (`dangerouslyAllowBrowser`), plaintext key stores (Jeview, unclutter, JevNoiseGate) ([[sdk-javascript]], [[awesome-typesafe-jev]]).
- Pasting the key into chat; MCP clients silently dropping env vars ([[jev-mcp-server]]).
- `extra_body` clobbering `questions`; `transport` + `http_client` together ([[sdk-python-clients]]).
- Old dict-keyed `Score.criteria` after v0.6.0 ([[sdk-changelogs]]); JS needs >= 2 Score criteria ([[sdk-javascript-api]]).
- Exposing jev-mcp HTTP beyond loopback without `JEV_MCP_AUTH_TOKEN` ([[jev-mcp-server]]).
- Hooks that send diffs every turn / turn advisory into a gate (repo setup doc; [[agent-operating-protocol]]).
- Faking a Jev result when tools are absent; retry loops ([[agent-operating-protocol]]).

## F. Source disagreements and vendor bias (do not average; cite both)
| Topic | Claim A | Claim B |
|---|---|---|
| Confidence vs runner-up | "confidence separates 0.45/0.44 from 0.45/scattered" ([[cb-classification-using-confidence]]) | published formula `(n·peak-1)/(n-1)` uses only peak and n ([[community-guide-marktechpost]]); matches all 13 observed pairs in [[confidence]] plus [[quickstart]]'s 0.85 -> 0.78 [inference: arithmetic check] |
| Confidence formula known? | "not given on this page" ([[confidence]]) | formula given ([[community-guide-marktechpost]]) |
| Batching saving | 11.5x cheaper / 9.6x faster ([[primitives-overview]]) | 12.2x / 10.0x ([[cb-parallel-questions]]) — same cookbook |
| Batching neutrality | "no change in answers" ([[cb-parallel-questions]]) | batching changed a ranking gate's outcome ([[awesome-typesafe-jev]]) |
| Rate limits | 100K tok/s, 40 req/s ([[models-and-versions]]) | 250K tok/s, 1,200 req/min ([[community-guide-devto]]) |
| Context | 64k/32k ([[models-and-versions]]) | 32,000 total ([[openrouter-jev-guide]]); ~4,000 ([[jev-vs-laya]]) |
| Jev latency | ~100 ms; 150 ms ([[how-to-build-with-system-one]], [[use-case-map]]) | 230-317 ms (third parties, [[jev-vs-laya]]); 150-500 ms ([[jev-mcp-server]]) |
| Calibration | "calibrated instead of overconfident" (vendor) | overconfident on contested items (ECE gap 0.264), dice 82.9% on one face, OOD overconfidence ([[awesome-typesafe-jev]]) |
| Choice capacity | 255 options ([[http-api-reference]]) | "reliably up to roughly 240" ([[cb-classification-using-confidence]]) |
| Jev BANKING77 | 0.870 / ~87% ([[jev-vs-laya]]) | 76.3% on all 77 (72-label pilot inflated) ([[benchmarks-and-comparisons]]) |
| Jev typed-decisions | 0.727 | 0.754 ([[benchmarks-and-comparisons]]) |
| Laya context | 512 (vanekt) | 8,192 max / 1,024 default (Menon) ([[laya]]) |
| Laya latency ratio | 6-7x / 7.8x | 20-30x (throughput) ([[jev-vs-laya]]) |
| Kev sizes/base | 0.8/4/9(/27)B, Qwen3.5/3.8 | 0.6/4/8B, Qwen2.5/3.5 (Layer3Labs) ([[kev]]) |
| OpenRouter model id | `~typesafe/jev-latest` ([[sdk-python-usage]], [[openrouter-jev-guide]]) | pinned only; `jev-latest` -> `typesafe/jev-1.13` ([[jev-mcp-server]]) |
| jev-mcp tool count | twelve ([[jev-mcp-server]]) | "ten bounded tools" (directory, [[awesome-typesafe-jev]]) |
| Structure-recovery cost | $0.0003 printed | $0.0015 in prose; ~$0.00043 computed ([[cb-structure-recovery]]) |
| Cookbook count | "Index of 19" (gist) | 18 recipes in its own table ([[cookbooks-overview]]) |
| jev-trader latency | ~81 ms ([[community-guide-devto]]) | measured with a mock model ([[awesome-typesafe-jev]]) |
| Access | waitlisted ([[community-guide-devto]]) | no waitlist via OpenRouter ([[openrouter-jev-guide]]) |
| Laya vs Jev priority | Laya author claims prior RLCD paper | unresolved ([[jev-vs-laya]]) |
**Bias map:** TypeSafe docs and its 4-workflow eval are self-run (consensus labels from GPT/Claude, biased toward them; "0% structured errors" asserted, not measured) ([[community-guide-devto]]); eesel (vendor) and Layer3Labs (consultancy) are commercial; laya-ai.com publisher unnamed; Laya's Jev numbers are third-party; SOTAAZ is the only independent measurement but had no Jev access ([[benchmarks-and-comparisons]], [[laya]]); dev.to is published by a search vendor ([[community-guide-devto]]); awesome directory numbers are author-reported ([[awesome-typesafe-jev]]).

## G. Page-finder in front of the reader on long PDFs (owner-measured)
**Owner-measured warning (2026-10-02, llama-index extraction spike, PR #29 in this repo).** On 6 real public PDFs
(58 facts + 12 "not in the doc" traps, answer key read off page images; small sample, one run per cell, one extractor
model) a page-finder in front of Claude made results WORSE: MiniLM top-4 pages -> Claude 36/58, versus 40/58 for plain
pypdf text and 53/58 for OCR on every page; MiniLM recall@4 was only 0.40-0.55 on the long reports; MiniLM + zero-shot
Laya -> Claude 10/37 on the small docs (Laya's page recall below MiniLM on all 4; zero-shot only, so NOT evidence about a
fine-tuned Laya). Claude + grep over per-page text files scored 21/21 on two long born-digital annual reports. So for
page-finding in long financial PDFs: read every page through `media_core.pdf_text` (pypdf, OCR only on empty pages), grep the
page files, and do NOT put an embedding or zero-shot System One shortlist in front of the reader. The shortlist advice above
comes from short-candidate benchmarks (BM25 top-30 rerank, MiniLM on BANKING77/TREC), not from long-document page recall.

## Related
[[jev-1-13-jaggedness]] · [[question-design-checklist]] · [[when-to-use-which-model]] · [[privacy-and-cost-gates]] · [[benchmarks-and-comparisons]] · [[topic-guardrails]] · [[topic-calibration]]
