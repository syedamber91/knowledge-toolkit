# Anti-patterns, source disagreements, vendor bias

Condensed from vault note `anti-patterns`. Citations are vault note names.

## Wrong kind of question (jev-1-13-jaggedness, `jev-1.13`, reviewed 2026-09-17)
| Anti-pattern | Fix |
|---|---|
| counting in one question (error grows with size) | one Noul per item, sum in code |
| numeric representations (hex, RGB, assembly) | convert in code; pass a named bucket |
| exact magnitude from Score levels | threshold the expectation only |
| date order / gap / window | Choice per date part + "not stated"; code does calendar math |
| indirection, double negatives | direct wording; name the field |
| big irrelevant state | filter first; relevance Noul |
| assuming state is safe | explicit criteria; test adversarial cases |
| instructions vs criteria disagree | align them |
| assuming P(q) + P(not q) = 1 | ask each decision one way (0.72 + 0.47 = 1.19 observed) |
| generation via chained choices | candidates from regex/LLM, model picks |
| several judgments in one question | atomic questions, compose in code |
| using Jev as a coding agent's LLM | no such setting; code calls Jev |

## Wording traps
Vague/overlapping options; no `other`; parameter-named questions; topical instead
of narrow-fact questions; Score levels as numbers or degrees; two dimensions in one
Score; inverted or compound Noul; subject-matter gate questions; policy decision
inside the question; labels read literally without descriptions; stale agent skill
-> invented request/response fields; unreviewed agent-written questions.

## Confidence misuse
- Confidence/probability read as correctness — calibration is over groups (ai-primer-calibrated-decisions).
- One global threshold — thresholds scale with risk, per action (confidence-gated-routing).
- Single 0.5 cut on a Noul — `covered` ranged 0.43-0.53 across 15 repeats (only a throwaway uid changed) (cb-consistency-nouls).
- Noul 0.5 read as "medium" — it means uncertain.
- Noul threshold reused on a Choice.
- Thresholds everywhere — argmax needs none; use raw probabilities for statistics (typesafe-agent-skill).
- Expecting `confidence` to see a close runner-up — formula uses only peak and n.
- Multiplying per-part probabilities — use min (cb-function-calling).
- Averaging verifier flags — use max (cb-sde-cascade); vague holistic judge gave 0.56 where per-field heads gave 0.95.
- Same score = same distribution — not so (score).
- High confidence = task fits the model — jaggedness cases can return 0.97.
- Thresholds from tiny sets (<~100 labelled rows; examples fitted on 10-24 items) or transferred across datasets (Janus: optimum, gap sign and payoff all changed) (awesome-typesafe-jev).
- Repeatability read as accuracy (Haiku t=0: 100% agreement, says nothing about correctness).
- Alias drift — pin `jev-1.13.0`, log `response.model`.

## Pipeline traps
- Sequential calls for batchable questions; acting on speculative answers outside their branch.
- Agent `while` loops where a workflow suffices (how-to-build-with-system-one).
- Trusting similarity rank: the injection passage ranked 1st, the corrector 7th (cb-classifying-rag-passages).
- Treating an injection score / `jev_screen` as a security boundary — it's one advisory filter.
- Merging evidence and conflict prompt blocks; reordering first-match rules.
- Expecting reranking to fix recall; reading a Choice winner without an `exists` check.
- Regex that under-finds; unhandled `none`; locale-blind number parsing (`€1.315,50`).
- Schema validation as proof (schema-valid fabrication passes); `same_fact` read as true.
- Greedy taxonomy walks (2/4 vs beam 4/4; catch-all leaf attracted mass).
- Pushy suggestions (a wrong suggestion is worse than none; 7 of 315 broken).
- Laya English root on non-Latin scripts (0.000 accuracy at 0.952 confidence); Laya with 77 options at its 192-token default (37.0%).
- Decomposition has costs: dimension scores beat a direct question (0.9076 vs 0.8373) but flagged ~25x more hard benign rows (awesome-typesafe-jev).
- Sorting by probability: two-decimal ties (53/360 at 0.99); batching 40 rows flipped a ranking gate.
- No no-match option: KoBBQ 79% stereotype picks when "unknown" was removed.
- Adversarial text vs gates: authority framing moved 3/30 dangerous commands; blunt injections caused 10% false denials (jev-engineering).

## Operational traps
- Immediate retries on 429/529 (use backoff); retrying ambiguous network failures (double billing).
- Fast worker ramp (8 already hits a shared-key limit).
- Debug logging in production (bodies unredacted); keys in browser JS, chat, or plaintext stores.
- MCP clients silently dropping env vars; HTTP jev-mcp beyond loopback without auth token.
- `extra_body` clobbering `questions`; dict-keyed `Score.criteria` after SDK v0.6.0.
- Hooks that send diffs every turn or turn advisory into a gate.
- Faking a result when tools are absent; retry loops.

## Source disagreements (state both; never average)
| Topic | A | B |
|---|---|---|
| confidence vs runner-up | classification cookbook: confidence separates 0.45/0.44 from 0.45/scattered | published formula `(n*peak-1)/(n-1)` uses only peak and n; fits all observed pairs |
| confidence formula | confidence note: not given | MarkTechPost: given |
| batching | 11.5x / 9.6x (Primitives page) | 12.2x / 10.0x (cookbook) |
| batching neutrality | "no change in answers" | changed a ranking gate (jev-orderby-bench) |
| rate limits | 100K tok/s, 40 req/s (docs) | 250K tok/s, 1,200 req/min (dev.to) |
| context | 64k / 32k (docs) | 32,000 total (OpenRouter); ~4,000 (vanekt) |
| Jev latency | ~100 ms / 150 ms (vendor) | 230-317 ms (third party); 150-500 ms (MCP) |
| calibration | vendor: calibrated, not overconfident | ChaosNLI ECE gap 0.264 on contested items; dice test 82.9% on one face; OOD overconfidence |
| Choice capacity | 255 (API) | "reliably ~240" (cookbook) |
| Jev BANKING77 | 0.870 / ~87% | 76.3% on all 77 (0.870 was a 72-label pilot) |
| Jev typed-decisions | 0.727 | 0.754 |
| Laya context | 512 | 8,192 max / 1,024 default |
| Laya speed ratio | 6-7x / 7.8x | 20-30x (throughput) |
| Kev sizes/base | 0.8/4/9(/27)B, Qwen3.5/3.8 | 0.6/4/8B, Qwen2.5/3.5 (Layer3Labs) |
| OpenRouter model id | `~typesafe/jev-latest` | pinned only; `jev-latest` -> `typesafe/jev-1.13` (jev-mcp) |
| jev-mcp tool count | twelve (README) | "ten" (directory) |
| structure-recovery cost | $0.0003 printed | $0.0015 in prose (~$0.00043 computed) |
| cookbook count | "19" | 18 listed |
| jev-trader latency | ~81 ms | measured with a mock model |
| access | waitlisted (direct) | no waitlist (OpenRouter) |

## Bias map
TypeSafe docs and its 4-workflow eval are self-run (consensus labels from GPT and
Claude; "0% structured errors" asserted, not measured). eesel (vendor) and
Layer3Labs (consultancy) are commercial; laya-ai.com's publisher is unnamed;
Laya's Jev numbers are third-party; SOTAAZ is the only independent measurement and
had no Jev access; the dev.to guide is published by a search vendor; awesome
directory numbers are author-reported.

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
