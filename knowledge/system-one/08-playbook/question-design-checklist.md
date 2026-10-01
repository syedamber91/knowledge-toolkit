---
title: Question Design Checklist
kind: playbook
source: Synthesis of concept, pattern and cookbook notes (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [primitives, state-design, confidence]
topics: [topic-state-design, topic-classification, topic-calibration, topic-routing]
---
# Question Design Checklist
> Write the state, pick Choice/Score/Noul, word options/levels/criteria, add escape outcomes, set thresholds, add companion Nouls, batch in one call. Every rule carries the example or number that proves it.

## A. State
- [ ] **Object with named fields** for anything multi-part (conversation + order + policy = one state) ([[state]]).
- [ ] **Only what the question needs**; filter in code first. Large irrelevant state lowers accuracy (context rot) ([[jev-1-13-jaggedness]] #5). Can't filter? A relevance Noul per item ([[cb-classifying-rag-passages]]).
- [ ] **Point at fields with backticked paths** inside the question: `` `ticket.messages[0].text` `` — backticks required ([[how-to-build-with-system-one]] step 3).
- [ ] **Pairs go in one state** (`query`+`passage`, `entity_a`+`entity_b`, `claim`+`section`) so every question is about the pair ([[cb-classifying-rag-passages]], [[cb-entity-alignment]], [[cb-citation-check]]).
- [ ] **Don't send what code can read** (blank lines, markers, numbers to compare) ([[cb-structure-recovery]], [[cb-entity-alignment]] abv).
- [ ] **Text only**; English best, others (incl. CJK) lower — test, watch confidence ([[models-and-versions]]).
- [ ] Budget: 64k tokens/request, 32k for state + longest question ([[models-and-versions]]; OpenRouter says 32,000 total — [[openrouter-jev-guide]]).
- [ ] User-controlled state is adversarial input; it is not treated as hostile by default ([[jev-1-13-jaggedness]] #6).

## B. Choose the primitive (by the shape of the answer)
| Need | Use | Not |
|---|---|---|
| one of a known set, unordered | **Choice** | Score (no order) |
| degree on a describable scale | **Score** | Noul ("Noul 0.5 is not medium") |
| clean yes/no; probability itself useful | **Noul** | Choice yes/no (different numbers: Noul 0.22 vs Choice yes 0.01 on the same ticket) |
Tie-breaker: the type your code acts on directly ([[primitives-overview]]). Several labels may apply -> one Noul per label ([[typesafe-agent-skill]] Rule 3). Ordered outcomes incl. a middle "send to human" -> Score with one level per outcome ([[cb-entity-alignment]]).

## C. Instructions
- [ ] **One atomic, gut-check judgment** ("what a knowledgeable person decides in a second") ([[primitives-overview]]). Split multi-factor judgments; weight in code ([[composite-scoring]]).
- [ ] **Literal:** say exactly what you mean; if you catch yourself explaining what you "really meant", that is the missing half of the instruction; or split into two literal questions ([[jev-1-13-jaggedness]] #1).
- [ ] **Direct, few hops**, no double negatives; name the state field ([[jev-1-13-jaggedness]] #4).
- [ ] **Question ID is never sent** — full meaning in `instructions` ([[primitives-overview]]).
- [ ] **Ask the narrowest objective fact that decides it**: "picks up mid-sentence" gave 17 correct blocks; "same paragraph" collapsed lists to 12 (list lines scored 0.77-0.91 vs 0.05-0.22) ([[cb-structure-recovery]]).
- [ ] **Ask about the idea, not the parameter name** ("Which resolution?" matches nothing) ([[cb-function-calling]]).
- [ ] Gate questions ask whether an **action** is wanted, not the subject matter ([[cb-skill-suggestion]]).
- [ ] Never put the policy decision ("should we include it?") in the question — keep it in code ([[cb-classifying-rag-passages]]).
- [ ] JSON instructions allowed: question in one field, data in others (`potential_duplicate`, `field_spec`) ([[advanced-structure]], [[noul]]).

## D. Choice options
- [ ] **Full list** — up to 255 options, a few tokens each ([[choice]]); "works reliably up to roughly 240" ([[cb-classification-using-confidence]]).
- [ ] **Add `other` / `none of the above` / `none`** whenever input may not fit; without it the model is forced to mis-classify ([[choice]]). Function-call `__tool__` has none — every command picks a function ([[cb-function-calling]]).
- [ ] **Descriptions separate options**; for confusable pairs use objects with `what` / `not_for` / `examples`, **same field names on every option** (`return_policy` vs `return_status` -> 1.0) ([[choice]], [[how-to-build-with-system-one]]).
- [ ] `null` description fine when the label is self-explanatory or the state already holds the text (line ids) ([[cb-line-by-line-search]]).
- [ ] **Descriptions are part of the model**: one-line descriptions moved DiffusionGemma TREC accuracy ~+20 pts, openjev +14 ([[openjev-and-nanojev]]); "human" read literally -> `entity`.
- [ ] Missing parent names: describe a group by its members ("<umbrella> - includes: <up to 8>") ([[cb-classification-using-confidence]]).
- [ ] Taxonomy: one Choice per level, option value = child's subtree (trim large subtrees) ([[advanced-structure]]); beam K=3 beat greedy 4/4 vs 2/4 ([[cb-hierarchical-classification]]).
- [ ] Sibling order is part of the question ([[cb-hierarchical-classification]]).

## E. Score levels
- [ ] **Describe situations, not degrees** ("Broken but workaround exists" not "Moderately severe") ([[score]]).
- [ ] **Numbers-blind:** criteria `["0","1","2"]` gave 0.55 / conf 0.33 on a cosmetic bug; descriptive levels gave 0.0 / conf 1.0 ([[score]]).
- [ ] 2-10 levels; 11 = server error ([[cb-autoresearch-feature-discovery]]); only as many as you can describe distinctly.
- [ ] **One dimension per Score**; rare extreme gets its own level ("abusive or threatening").
- [ ] Examples steer only if they resemble real inputs (1.43/0.35 -> 1.03/0.96 with a matching example; unchanged with an unrelated one) — test revisions on separate inputs.
- [ ] Normalize before combining: `score / (len(criteria)-1)` ([[score]], [[composite-scoring]]).
- [ ] Use expectation for thresholds/ranking, never to interpolate exact magnitudes ([[jev-1-13-jaggedness]] 2c).

## F. Noul wording
- [ ] **One proposition per Noul** ("angry AND refund" -> two Nouls) ([[noul]]).
- [ ] **High = yes** ("contains personal data?" not "free of personal data?") ([[noul]]); true mapped to "no" performs worse ([[jev-1-13-jaggedness]] #7).
- [ ] For verifiers: **bad = TRUE** with explicit criteria ([[cb-sde-cascade]]).
- [ ] Unambiguous boundary ("any Python experience?"); subtle boundary -> `criteria.true/false` with definition + examples; **A/B with and without criteria** ([[noul]]).
- [ ] Statement form works too; try both on your data.

## G. Escape outcomes and companions
| Need | Pattern | Source |
|---|---|---|
| "nothing fits" | `other`/`none` option; `none` escape on candidate picks | [[choice]], [[cb-pre-parsed-value-extraction]] |
| "not stated" | explicit option per part (dates) | [[cb-date-extraction]] |
| "is there an answer at all?" | companion `exists` Noul next to a ranking Choice | [[cb-line-by-line-search]] |
| "should we say anything?" | per-candidate `fits` Nouls next to a Choice (Choice = which; Nouls = whether) | [[cb-skill-suggestion]] |
| "which fields disagree?" | companion Noul per compared field | [[cb-entity-alignment]] |
| "does the user mention this arg?" | `stated` Noul; omitted -> default | [[cb-function-calling]] |
| "uncertain" | top prob < 0.60 (Choice) / 0.30-0.70 band (Noul) | [[cb-consistency-choices]], [[cb-consistency-nouls]] |
| independent gate on a choice | `requirements` checks in `jev_decide`, escape hatches | [[jev-mcp-server]] |

## H. Thresholds (all illustrative — calibrate on labelled data; start conservative)
| Use | Value | Source |
|---|---|---|
| Choice confidence floor | 0.3 / 0.5 / 0.6 / 0.75 / 0.8 | [[choice]], [[confidence]], [[confidence-gated-routing]], [[how-to-build-with-system-one]] |
| High-stakes act | > 0.85 / > 0.9 (else confirm) | [[confidence-gated-routing]], [[confidence]] |
| Per-action bars | balance .50, dispute .70, transfer .85, close account .90 | [[community-guide-marktechpost]] |
| Citation auto-accept | 0.8 | [[cb-citation-check]] |
| Fine vs coarse label | 0.9 | [[cb-classification-using-confidence]] |
| Noul yes/no/review | YES 0.8 / NO 0.2; or 0.30-0.70 band; > 0.7 duplicate | [[noul]], [[cb-consistency-nouls]] |
| RAG routing | injection > .70 exclude, contradicts > .70 conflict, relevant < .45 exclude, evidence > .55 include (first match wins) | [[cb-classifying-rag-passages]] |
| Guardrail policies | review .35, action .70 strict / .85 permissive, severity block 2.0 | [[cb-llm-guardrails]] |
| Verifier escalate | any P(wrong) > 0.7 | [[cb-sde-cascade]] |
| Skill gate / fits | 0.30 / 0.30 | [[cb-skill-suggestion]] |
| Exists found / absent | >= 0.7 / < 0.35 | [[cb-line-by-line-search]] |
| Date review | min part confidence < 0.60 | [[cb-date-extraction]] |
| Stitch join | 0.2 after dangling line, 0.5 after terminal punctuation | [[cb-structure-recovery]] |
- Thresholds scale with risk; conditional thresholds beat one global cut ([[confidence]], [[cb-structure-recovery]]). Don't move a Noul-tuned threshold to a Choice ([[jev-1-13-jaggedness]] #8). Plot confidence vs accuracy ([[how-to-build-with-system-one]] step 8). Pin the model version you tuned on ([[models-and-versions]]).
- Choice `confidence` = `(n x peak - 1)/(n - 1)` (published formula, [[community-guide-marktechpost]]; matches every observed pair in [[confidence]] [inference: checked]). So it ignores the runner-up: add a **margin** check when the gap matters (`jev_classify` `minimum_margin` 0.5, [[jev-mcp-server]]).

## I. Aggregation in code
| Combine | Use | Source |
|---|---|---|
| min over parts | call/date confidence (one weak part spoils the result) | [[cb-function-calling]], [[cb-date-extraction]] |
| max over failure checks | escalate on one confident red flag | [[cb-sde-cascade]], [[jev-mcp-server]] `jev_audit` |
| mean of oriented Nouls | soft gate (invert "prose suffices" first) | [[cb-skill-suggestion]] |
| weighted sum (normalized) | compensating preferences; "any serious violation" needs separate conditions | [[composite-scoring]], [[typesafe-agent-skill]] |
| geometric mean of path probs | beam search across depths (log-space > 10 layers) | [[cb-hierarchical-classification]] |
| precedence list | support > block > review > pass | [[cb-llm-guardrails]] |

## J. Batching
- [ ] Every question over the same state in **one request**, speculative ones included; parallel and isolated ([[speculative-fan-out]]). 13 questions: same answers, 12.2x cheaper, 10.0x faster ([[cb-parallel-questions]]).
- [ ] One request per *state*: pairs (query, candidate) can't be batched into one state ([[cb-classifying-rag-passages]]); cost scales with k.
- [ ] Second request only when it needs the first answer ([[primitives-overview]]): skill rerank, structure recovery pass 2, hierarchy walk.
- [ ] Speculative questions state their premise ("what action on the lights?") and are read only on the matching branch ([[demo-smart-home]]).

## K. Process
- [ ] Questions + thresholds as constants in **one file**; humans review — "agents aren't great at writing questions" ([[typesafe-agent-skill]]).
- [ ] Re-routing from stored answers costs zero API calls; store raw probabilities ([[cb-classifying-rag-passages]]).
- [ ] Screen a proposed question before paying for it (answerable? one meaning? applies to most rows? varies?) ([[cb-autoresearch-feature-discovery]] next steps).

## Related
[[agent-operating-protocol]] · [[anti-patterns]] · [[cheat-sheet]] · [[primitives-overview]] · [[confidence]] · [[topic-state-design]] · [[topic-calibration]]
