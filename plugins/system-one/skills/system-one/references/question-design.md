# Question design — state, primitive, wording, thresholds, batching

Condensed from vault note `question-design-checklist`. Citations are vault note names.

## State
- JSON object with named fields when multi-part (conversation + order + policy = one state) (state).
- Only the fields the question needs; filter in code (jaggedness #5: context rot). If you can't, a relevance Noul per item (cb-classifying-rag-passages).
- Point at fields with backticked paths inside the question: `` `ticket.messages[0].text` `` (how-to-build-with-system-one).
- Pairs in one state (`query`+`passage`, `entity_a`+`entity_b`, `claim`+`section`) so each question is about the pair.
- Don't send what code can read (blank lines, markers, numbers) (cb-structure-recovery, cb-entity-alignment).
- Text only; English best; other languages lower — test (models-and-versions).
- Budget 64k tokens/request, 32k state + longest question (models-and-versions; OpenRouter says 32,000 total).
- User-controlled state is adversarial input; not treated as hostile by default (jaggedness #6).

## Pick the primitive
| Need | Use |
|---|---|
| one of a known unordered set | Choice -> `choice`, `probabilities`, `confidence` |
| degree on a describable scale | Score -> fractional `score`, `legend`, `probabilities`, `confidence` |
| clean yes/no; probability is the signal | Noul -> `noul` 0-1, no confidence |
Tie-breaker: the type your code acts on directly. Several labels may apply -> one
Noul per label. Ordered outcomes with a middle "human" band -> Score with one level
per outcome (cb-entity-alignment: rounding at 0.5/1.5 is the whole rule).
Noul and Choice give different numbers for the same question (0.22 vs yes 0.01) —
don't swap them or their thresholds (jaggedness #8).

## Instructions
- One atomic, gut-check judgment; split multi-factor judgments and weight in code (composite-scoring).
- Literal: write the exact condition; if you're explaining what you "really meant", that's the missing instruction (jaggedness #1).
- Direct, few hops, no double negatives (jaggedness #4).
- Question ID is never sent — full meaning goes in `instructions`.
- Narrowest objective fact: "picks up mid-sentence" -> 17 correct blocks; "same paragraph" -> 12, lists collapsed (cb-structure-recovery).
- Ask about the idea, not the parameter name (cb-function-calling).
- Gate questions ask whether an action is wanted, not the topic (cb-skill-suggestion).
- Keep policy (include/exclude) in code, not in the question (cb-classifying-rag-passages).
- JSON instructions OK: question in one field, data in another (advanced-structure).

## Choice options
- Full list, up to 255 (each option a few tokens); "reliably up to roughly 240" (cb-classification-using-confidence).
- Add `other` / `none` when input might not fit (otherwise forced misclassification).
- Descriptions must separate options; for confusable pairs use objects `what` / `not_for` / `examples` with the same field names on every option.
- `null` description when the label or the state already says it all.
- Descriptions change results: +~20 pts on TREC for a DiffusionGemma server, +14 openjev; "human" read literally -> `entity` (openjev-and-nanojev).
- Deep taxonomy: one Choice per level, option value = child subtree (trim big ones); beam K=3 got 4/4 vs greedy 2/4 (cb-hierarchical-classification). Sibling order is part of the question.

## Score levels
- Situations, not degrees ("Broken, workaround exists", not "moderately severe").
- Numbers-blind: criteria `["0","1","2"]` -> 0.55 at confidence 0.33; descriptive -> 0.0 at 1.0 (score).
- 2-10 levels (11 = server error); one dimension per Score; rare extreme gets its own level.
- Examples steer only if they resemble real inputs (1.43/0.35 -> 1.03/0.96 with matching example; unchanged with unrelated). Test revisions on separate inputs.
- Normalize before combining: `score / (len(criteria) - 1)`.
- Threshold the expectation; never interpolate exact magnitudes (jaggedness 2c).

## Noul wording
- One proposition per Noul; high value = yes; true mapped to "no" performs worse.
- For verifiers frame bad = TRUE, with explicit criteria (cb-sde-cascade).
- Unambiguous boundary ("any Python experience?"); subtle -> `criteria.true/false` with definition + examples; A/B with and without criteria.

## Escape outcomes and companion questions
| Need | Pattern | Source |
|---|---|---|
| nothing fits | `other` / `none` option | choice, cb-pre-parsed-value-extraction |
| part not stated | explicit "not stated" option | cb-date-extraction |
| any answer at all? | `exists` Noul beside a ranking Choice (Choice always has a winner) | cb-line-by-line-search |
| say anything at all? | per-candidate `fits` Nouls beside the Choice (Choice = which, Nouls = whether) | cb-skill-suggestion |
| which fields disagree? | one Noul per compared field | cb-entity-alignment |
| argument mentioned? | `stated` Noul; omitted -> function default | cb-function-calling |
| uncertain | top prob < 0.60; Noul 0.30-0.70 | cb-consistency-choices, cb-consistency-nouls |

## Thresholds seen (illustrative — tune on labelled data, start conservative)
| Use | Value | Source |
|---|---|---|
| Choice confidence floor | 0.3 / 0.5 / 0.6 / 0.75 / 0.8 | choice, confidence, confidence-gated-routing, how-to-build |
| high-stakes auto-act | > 0.85 or > 0.9, else confirm | confidence-gated-routing, confidence |
| per-action bars | balance .50, dispute .70, transfer .85, close account .90 | community-guide-marktechpost |
| citation auto-accept | 0.8 | cb-citation-check |
| fine vs coarse label | 0.9 | cb-classification-using-confidence |
| Noul YES/NO with review band | 0.8 / 0.2; or 0.30-0.70 | noul, cb-consistency-nouls |
| RAG passage routing (first match) | injection > .70 exclude; contradicts > .70 conflict; relevant < .45 exclude; evidence > .55 include | cb-classifying-rag-passages |
| guardrails | review .35; action .70 strict / .85 permissive; severity >= 2.0 turns review into block | cb-llm-guardrails |
| verifier | any P(wrong) > 0.7 | cb-sde-cascade |
| skill gate / fits | 0.30 / 0.30 | cb-skill-suggestion |
| exists found / absent | >= 0.7 / < 0.35 | cb-line-by-line-search |
| date review | min part confidence < 0.60 | cb-date-extraction |
| line stitch | 0.2 after dangling line; 0.5 after terminal punctuation | cb-structure-recovery |
Choice `confidence = (n x peak - 1)/(n - 1)` (published; community-guide-marktechpost;
matches every observed pair in the confidence note) — so it ignores the runner-up.
Add a margin check when the gap matters (`jev_classify` `minimum_margin` 0.5).
Pin the model version you tuned on; plot confidence vs accuracy.

## Aggregation in code
| Combine | Use | Source |
|---|---|---|
| min | multi-part call confidence (function args, date parts) | cb-function-calling, cb-date-extraction |
| max | failure-check batteries | cb-sde-cascade, jev_audit |
| mean of oriented Nouls | soft gate (invert negative ones first) | cb-skill-suggestion |
| normalized weighted sum | compensating preferences; "any serious violation" needs separate conditions | composite-scoring, typesafe-agent-skill |
| geometric mean of path probs | beam search across depths (log space beyond ~10 layers) | cb-hierarchical-classification |
| precedence list | support > block > review > pass | cb-llm-guardrails |

## Batching
- All questions over one state in one request, speculative ones included, each stating its premise; read them only on the matching branch (speculative-fan-out, demo-smart-home).
- One request per state: pairwise judgments can't share a state, so cost scales with candidates.
- Second request only if it needs the first answer (skill rerank, structure-recovery pass 2, hierarchy walk).

## Process
- Questions + thresholds as constants in one file; humans review — "agents aren't great at writing questions" (typesafe-agent-skill).
- Store raw probabilities; re-routing after a threshold change costs zero API calls.
- Screen a candidate question before paying for it: answerable from the text? one meaning? applies to most rows? varies? (cb-autoresearch-feature-discovery).
