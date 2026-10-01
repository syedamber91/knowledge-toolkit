---
title: Speculative Fan-Out
kind: pattern
source: Patterns > Speculative fan-out
source_url: https://docs.typesafe.ai/patterns/fan-out
tags: [patterns, cost-latency]
topics: [topic-cost-latency, topic-routing]
---
# Speculative Fan-Out
> Put every question your system might need into ONE request (including ones that may turn out irrelevant), then let code pick which answers matter.

## What it is / How it works
- TypeSafe supports many questions per API call; the recommendation is to put **all** questions the system needs in a single request and decide relevance in code afterwards.
- All questions are evaluated in parallel, so extra questions usually have **little effect on response time** ([[jev-introduction]]).
- Saves serial round trips: instead of "classify, then (if bug) ask severity" in two calls, ask both now; ignore the severity result if the ticket isn't a bug.

## When to use / when NOT to use
- Use when the follow-up question depends on the first answer but each is cheap to ask.
- Speculative answers are ignored when irrelevant and "save a round trip when they are not."
- Caveats (from other pages): context budget bounds how many questions fit — 64k tokens total, 32k for state + longest question ([[models-and-versions]]); keep each question atomic ([[how-to-build-with-system-one]]).

## Worked example — support ticket triage
One request: ticket + **5 questions** -> one response with 5 answers (decisions + probabilities).
| Question | Type | Relevant when |
| - | - | - |
| `category` | Choice | always (bug_report / billing / feature_request seen in routing) |
| `bug_severity` | Score | only if bug report |
| `has_reproducible_steps` | Noul ("reproducible steps?") | only if bug report |
| `refund_requested` | Noul | only if billing |
| `frustration` | Score | regardless of category |
The actual question definitions are a rendered component in the source, not captured.

Routing code (thresholds from source):
- category `bug_report`: if `bug_severity.score > 1.5` **and** `has_reproducible_steps.noul > 0.6` -> `escalate_to_engineering(severity="high")`; else `add_to_bug_backlog`.
- category `billing`: if `refund_requested.noul > 0.7` -> `route_to_billing_with_flag(refund_likely=True)`; else `route_to_billing`.
- category `feature_request`: `log_feature_request` ("sent to devs" per diagram).
- Independently of category: `frustration.score > 1.5` -> `flag_for_priority_response`.
"Everything needed for the full decision tree comes from one call."

## Numbers & limits
| Item | Value |
| - | - |
| Questions in example | 5 (1 Choice, 2 Score, 2 Noul) |
| Bug escalation | severity > 1.5 and repro > 0.6 |
| Refund flag | > 0.7 |
| Priority flag | frustration > 1.5 |
| Context cap | 64k tokens/request, 32k state + longest question |

## Gotchas
- Speculative answers still cost input tokens (billing is per input token; [[models-and-versions]]) [inference: more questions = more input tokens].
- Don't act on a speculative answer without checking the category branch first; the code only consults it inside the relevant branch.
- Note the code's `Noul` thresholds (0.6/0.7) are illustrative; this example gates Noul values directly without confidence (Noul has no confidence field in documented output).

## Related
[[patterns-overview]] · [[how-to-build-with-system-one]] · [[cb-parallel-questions]] · [[composite-scoring]] · [[confidence-gated-routing]] · [[topic-cost-latency]]
