---
title: Primitives Overview (Questions and Answers)
kind: concept
source: Primitives (Questions)
source_url: https://docs.typesafe.ai/primitives
tags: [primitives, system-one]
topics: [topic-extraction, topic-classification, topic-cost-latency]
---
# Primitives Overview (Questions and Answers)
> The three question types (Choice, Score, Noul), the typed answer each returns, how to pick between them, and how to batch many questions into one request.

## What it is / How it works
Primitives come in pairs: a **question** defines one judgment a System One model makes about a **state** (see [[state]]); the **answer** is the typed value that comes back. You compose answers in ordinary code to make decisions. Every question in one request sees the same state, is evaluated **independently**, and returns under the ID you chose.

| Type | Answers | Returns |
| - | - | - |
| [[choice]] | Which of these options? | `choice`, `probabilities`, `confidence` |
| [[score]] | Which level? | `score`, `legend`, `probabilities`, `confidence` |
| [[noul]] | Is this true? | `noul` (0 to 1) |

### Question anatomy
Every question has an ID, a `type`, and `instructions`. Choice and Score also take `criteria`; Noul accepts `criteria` optionally.
- **ID**: your key (e.g. `refund_requested`); identifies the answer in the response. **Not sent to the model** -- write the full question in `instructions` even if the ID seems self-explanatory.
- **`type`**: `choice` | `score` | `noul`.
- **`instructions`**: the question about the state; where evaluation logic goes. Write as a clear specific question, or a statement for the model to judge. String is enough for most; may be object/array to put the question in one field and referenced data in others (see [[advanced-structure]], [[how-to-build-with-system-one]]).
- **`criteria`**: possible answers. Choice = map of options; Score = ordered list of levels; Noul = optional description of yes and no.

Minimal Python (SDK) example from the page:
```python
from typesafe_sdk import Noul
questions = {"refund_requested": Noul(instructions="Does the customer request a refund?")}
```

### Philosophy: one snap judgment per question
- System One models are built for fast, focused judgments: ask what a knowledgeable person decides in a second given the right context.
- Good: "Does this message convey urgency?" Bad: "Analyze this message and determine the best course of action" (needs slow reasoning; split into small questions and compose in code).
- If a judgment depends on several independent factors, ask about each separately and combine in code. Example: instead of "rate this startup pitch", ask market size, technical feasibility, differentiation, and weight in code. When priorities shift, change weights, not a prompt.

## When to use / when NOT to use -- choosing a question type
Pick the type matching the shape of the answer you need.
- **Choice**: one of a known set of options, no order (route a ticket to a department, document type, programming language). Give the full options list; add `other` / `none of the above` when the list might not cover every input.
- **Score**: a spectrum where you can describe what each point means (bug severity, customer frustration, skill level). Levels are yours; the model returns a position along them.
- **Noul**: a clean yes/no where the probability itself is the useful signal (contains PII? requesting a refund? resume mentions distributed systems?).
- **Tie-breaker**: if two types fit, prefer the one whose answer your code can act on directly. Choice among `refund`/`rebook`/`information` -> three code paths. Score of frustration -> a threshold. Noul -> an `if`.

### Noul vs Score (explicit warning in source)
"Is this candidate strong in Python?" needs a clear definition of "strong". A Noul of 0.5 means the model gives yes and no equal probability; it does **not** mean medium skill. To measure skill level use a Score with defined levels (no experience, some familiarity, daily use, deep expertise). For a yes/no decision define the condition crisply: "Does the resume state that the candidate has used Python at work?" See [[noul]] for the 4-candidate comparison table.

## What comes back
| Type | Answer fields | How to read |
| - | - | - |
| Choice | `choice`, `probabilities`, `confidence` | `choice` = selected option; `probabilities` = distribution across every option; `confidence` = how peaked that distribution is |
| Score | `score`, `legend`, `probabilities`, `confidence` | `score` = position along your levels, may fall between two; `legend` repeats levels by number; `probabilities` = distribution across levels |
| Noul | `noul` | probability answer is yes; ~1 strong yes, ~0 strong no, ~0.5 uncertain; **no separate `confidence`** |

Two composability properties:
1. **Every answer is constrained to the options you supplied** -- the model returns a probability distribution over your options/levels, never a value outside them; no recovering values from prose.
2. **Every answer is independent** -- one answer is not hidden context for another; add/remove questions without changing others' results.

How `confidence` derives from `probabilities`: see [[confidence]].

## Referencing specific fields of the state
If the state is a JSON object with several parts (conversation, record, policy), name the part in `instructions` with a **dot-and-index path in backticks**, e.g. `` `ticket.messages[0].text` ``, so the model knows which part to judge. See [[state]].

Worked example state (support conversation): `ticket.subject = "Duplicate charge"`, `ticket.messages[0] = customer: "I was charged twice for order A-104. Please refund the duplicate."`, `order.charges = two captured charges of 49 USD`, `refund_policy = "Duplicate charges are eligible for a refund."`. Two Noul questions:
- `refund_requested`: "Does `ticket.messages[0].text` request a refund?"
- `policy_supports_refund`: "Does `refund_policy` support the refund requested in `ticket.messages[0].text`, given `order.charges`?"

## Asking multiple questions together
- Send **every question that uses the same state in one request**; mix types freely. System One evaluates all questions in a request **in parallel**. Adding questions barely changes response time and costs only the extra question tokens, which are cheap. A question you might not need is close to free.
- Python: pass a `questions` dict of `Choice`/`Noul`/`Score` objects to `client.system_one(state=..., questions=...)`; read `response.answers["id"].noul / .choice / .score`.

Worked example (flight cancelled): state `{"ticket_message": "My flight was cancelled. Can I get a refund?", "refund_policy": "Cancelled flights are eligible for a full refund."}`; questions: Noul `refund_requested` ("Does `ticket_message` request a refund?"); Choice `request_type` (refund = money returned / rebooking = replacement flight / information = asking only); Score `frustration` (levels: "Calm and neutral." / "Concerned but civil." / "Very angry or using strong language."). The page does not print the response values for this one.

### Speculative questions
Ask every question your code might need, even ones that only matter for some inputs, and let code decide which answers to use (e.g. ignore the severity answer if the ticket isn't a bug report). This is the [[speculative-fan-out]] pattern. Cited benchmark: the Parallel questions cookbook shows batching **13 questions into one call is 11.5x cheaper and 9.6x faster** than 13 separate calls, with no change in answers ([[cb-parallel-questions]]).
Tip: coding agents fall into "one question per call" more than people; the TypeSafe agent skill tells the agent to put many questions per call including conditional ones ([[typesafe-agent-skill]]).

### Splitting a complex judgment
One question per factor; combine with weights in code; tune weights when results don't match team judgment. Example: ticket priority from three Scores (bug severity, customer frustration, report quality) -- full code in [[score]]. Pattern: [[composite-scoring]].

### When one question depends on another
Questions in one request are independent. If a later judgment depends on an earlier answer, make a **second request in code**. The dependency is real only when code cannot build the second request until it has the first answer -- because it needs the answer to (a) fetch more data for the state, (b) decide what the state is made of, or (c) pick the next question's options. Otherwise ask together and combine in code. If the second request's questions could have been asked against the original state, ask them in the first request and ignore what's not needed.
Three cookbooks with a legitimate second request:
- Skill suggestion: ranks 182 skills in one request, then fetches full text of top three and re-judges ([[cb-skill-suggestion]]).
- Structure recovery: asks whether each line break split a sentence, merges lines into blocks, then classifies the blocks, which did not exist until request one answered ([[cb-structure-recovery]]).
- Hierarchical classification: each Choice answer decides which options the next request offers ([[cb-hierarchical-classification]]).

## Numbers & limits
| Item | Value |
| - | - |
| Choice options per question | max 255 (stated on [[choice]] / [[http-api-reference]]) |
| Score levels | min 2, max 10 ([[score]]) |
| Noul value range | 0 to 1 |
| Parallel batching benchmark | 13 questions in one call: 11.5x cheaper, 9.6x faster |

## Gotchas
- Question IDs are not sent to the model.
- Noul 0.5 != medium degree (use Score for degree).
- Questions can't read each other's answers inside one request.
- Do not ask multi-step reasoning questions; split.

## Related
[[state]] -- [[choice]] -- [[score]] -- [[noul]] -- [[advanced-structure]] -- [[confidence]] -- [[http-api-reference]] -- [[how-to-build-with-system-one]] -- [[patterns-overview]] -- [[question-design-checklist]] -- [[topic-classification]] -- [[topic-cost-latency]]
