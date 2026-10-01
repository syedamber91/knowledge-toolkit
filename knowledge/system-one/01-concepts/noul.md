---
title: Noul Primitive
kind: reference
source: Noul; API reference
source_url: https://docs.typesafe.ai/primitives/noul
tags: [primitives, guardrails]
topics: [topic-guardrails, topic-calibration]
---
# Noul Primitive
> A yes/no question; returns one number 0..1 = probability the answer is yes. Use for checks, guardrails, verification and as a ranking signal.

## What it is / How it works
- Answer: single number `noul`; 0 = no, 1 = yes. It is "the answer and the certainty in one". **No separate `confidence`** field (binary distribution is fully described by one number).
- **Request fields** (per question): `type: "noul"`; `instructions` (yes/no question, or a statement to judge; string/object/array); `criteria` **optional** object with `true` and `false` descriptions (each string/object/array) of what yes (near 1) and no (near 0) mean.
- Question ID is yours; not sent to the model.
- Python:
```python
from typesafe_sdk import Noul, NoulCriteria, TypeSafeClient
Noul(instructions="Has the customer contacted support about this before?",
     criteria=NoulCriteria(true="Mentions a prior attempt, ticket, or that they have asked before",
                           false="No sign of any previous contact"))
# client.system_one(model="jev-latest", state=..., questions={...}); read answers[id].noul
```
- Response for state "I have asked three times now. Can I please just talk to a real person?": `is_human_escalation` 0.99; `is_repeat_contact` 0.93 (model jev-1.13.0; usage 360 in / 39 out).

## Reading a Noul
~1 strong yes, ~0 strong no, ~0.5 yes and no similar probability. Recorded `jev-1.13.0` answers to `is_human_escalation` ("Is the customer asking for a human agent?"):
| State | noul |
| - | - |
| Thanks, that fixed it! | 0.02 |
| How do I reset my password? | 0.07 |
| I need this sorted today, whatever it takes. | 0.26 |
| Are you a bot? | 0.40 |
| Is there any way to speak to someone about my invoice? | 0.84 |
| I have asked three times now. Can I please just talk to a real person? | 0.99 |
"Urgent but never asks for a person" = 0.26; "Are you a bot?" hints at wanting a human without asking -> near-even split 0.40. Those are the messages where a code-side threshold decision matters.

### Thresholding
Usually threshold `noul` into a boolean (e.g. `> 0.9` -> route to agent). Where to set the threshold depends on cost of being wrong:
- 0.5 when yes and no are equally easy to act on.
- **Raise** when a false yes is expensive (paging someone, issuing a refund).
- **Lower** when missing a true yes is expensive (failing to flag a safety issue).
- Middle values can go to a person -- the same three-way split as [[confidence]].

### A Noul is not a degree scale
The value is a probability, not the amount of the thing. Four candidates, Noul "Is the candidate strong in Python?" vs Score "How much Python experience does the candidate have?" (levels: no experience, some familiarity, regular use in a job, deep expertise):
| Candidate | Noul | Score |
| - | - | - |
| Java and Go only, no Python | 0.03 | 0.0 (No experience) |
| Python occasionally for small scripts alongside Java | 0.14 | 1.0 (Some familiarity) |
| Python daily two years, mostly data pipelines | 0.81 | 2.05 (Regular use in a job) |
| Python daily eight years incl. large Django codebase | 0.92 | 2.89 (Deep expertise) |
Why: Noul judges one proposition ("strong"); you could carve 0-1 into bands in code (0.3-0.7 = "some experience") but the model never sees those bands, so nothing was judged against them; a middle value can mean medium experience or an unclear case; spacing between candidates isn't chosen by you. Score judges each level description separately, so answers land at/near levels you wrote and `probabilities` show the division; if you disagree, reword a level and rerun. See [[score]].

## Writing a Noul question
1. **One yes/no per Noul.** "Is the customer angry and asking for a refund?" makes the value mean less; ask two Nouls and combine in code.
2. **High value = yes.** "Does the message contain personal data?" good; "Is the message free of personal data?" inverts the meaning and later code will read it backwards.
3. **A statement works too** ("The customer is requesting a refund"; near 1 = true). Try both phrasings on your data.
4. **Unambiguous boundary.** "Does this candidate have any Python experience?" -- "any" leaves no middle ground. For subtle boundaries add `criteria` true/false (definition + examples on each side, see [[advanced-structure]]). Instruction alone is enough for most; **test with and without `criteria`** and keep what answers better on your documents.
5. Checklist of conditions: many Nouls in one request, one per condition, code decides what the combination means; parallel evaluation barely changes latency ([[primitives-overview]], [[speculative-fan-out]]).

## Handling multiple Noul answers in code (worked example)
Code from the page: `YES = 0.8`, `NO = 0.2`; if `NO < wants_human < YES` or `NO < repeat < YES` -> `send_to_review`; else `priority = "high" if repeat > YES else "normal"`; if `wants_human > YES` -> route_to_agent(priority) else route_to_bot(priority). Outcome: "I have asked three times..." (0.99 / 0.93) -> agent, high priority; "How do I reset my password?" (0.07 on both) -> bot. Thresholds live in code: too many reviewer cases -> narrow the NO..YES gap; too many wrong routes -> widen it. Adding questions (mentions a payment? contains personal data?) keeps request count at one.

## Structured instructions: duplicate-record check
A new resume vs candidate-database records that might be the same person. Each record goes into a `potential_duplicate` field, the `question` text is fixed; the question key embeds the DB id (`same_as_record_<id>`); all records in one request.
```python
SAME_PERSON = "Is the resume for the same person as `potential_duplicate`?"
Noul(instructions={"potential_duplicate": {"name":..., "location":..., "last_employer":...},
                   "question": SAME_PERSON})   # state={"resume": resume}; keep answers with .noul > 0.7
```
Response (usage 535/58): `same_as_record_18` **0.74** (name spelled differently but location + employer match); `same_as_record_42` **0.09** (same name, different city and employer); `same_as_record_77` **0.08** (similar name, same location, different employer). Threshold each and send middle values to a person. The SDE cascade cookbook uses the same idea: every field gets the same questions; `instructions` has `main_question` plus per-field `field_spec` and `extracted_field` ([[cb-sde-cascade]]).

## Noul in the cookbooks
- Parallel questions: 13-question regulatory checklist over one article in one request ([[cb-parallel-questions]]).
- Self-consistency: nouls: scores an insurance claim on a 15-question rubric, measures stability across runs ([[cb-consistency-nouls]]).
- Re-ranking: uses the raw probability, one Noul per query-candidate pair, sort by value ([[cb-reranking]]).
- Line-by-line search: Choice finds the matching line + Noul checks whether the document contains an answer at all ([[cb-line-by-line-search]]).
- Structure recovery: one Noul per pair of lines "did a line break split a sentence" ([[cb-structure-recovery]]).

## Numbers & limits
| Item | Value |
| - | - |
| Value range | 0..1 |
| confidence field | none for Noul |
| Typical thresholds shown | >0.9 (route to agent); YES 0.8 / NO 0.2 with review band; >0.7 duplicate |
| Usage examples | 360/39; 535/58 for 3 structured questions |

## Gotchas
- Don't read 0.5 as "medium"; it is uncertainty (or equal yes/no weight).
- Compound questions and inverted phrasing weaken/flip meaning.
- Hints-without-asking messages (e.g. "Are you a bot?" 0.40) sit mid-range; plan a review path.
- Whether `criteria` helps is empirical; A/B it.

## Related
[[primitives-overview]] -- [[choice]] -- [[score]] -- [[advanced-structure]] -- [[confidence]] -- [[http-api-reference]] -- [[cb-citation-check]] -- [[cb-llm-guardrails]] -- [[topic-guardrails]]
