---
title: Intent Routing
kind: pattern
source: Patterns > Intent routing
source_url: https://docs.typesafe.ai/patterns/intent-routing
tags: [patterns, routing, classification]
topics: [topic-routing, topic-classification, topic-cost-latency]
---
# Intent Routing
> Use Jev as a fast, cheap front-door classifier that sends each request to deterministic code, a specialist LLM, or a human — so expensive resources only run when needed.

## What it is / How it works
Not every request needs the same handler: some are a database lookup, some need an LLM with domain context, some need a human. Classify first (one call), route accordingly, rather than sending every message through an expensive LLM to find out what kind of request it is.

## When to use / when NOT to use
Use as a classifier in front of heterogeneous handlers. Combine with confidence gating ([[confidence-gated-routing]]): low confidence -> human.

## Worked example — customer service routing
One request: customer message + 2 questions: Choice `intent` and Score `complexity`. (Definitions are a rendered component, not captured; intents seen in routing: `order_status`, `product_question`, `return_exchange`, `complaint`.)
| Condition | Handler |
| - | - |
| `intent.confidence < 0.5` | human agent |
| `order_status` | order lookup — deterministic code, **no LLM** |
| `product_question` | product specialist LLM |
| `return_exchange` | returns specialist LLM |
| `complaint` and (`complexity.score > 1` or `complexity.confidence < 0.5`) | human agent (too complex for safe automation, or unsure about complexity) |
| `complaint` otherwise | complaint resolution LLM |
- A higher `complexity.score` leans toward the "escalation needed" end of the scale.
- Source note: also check **confidence on the complexity score**; per [[confidence]], consider what low confidence means given the system and the stakes.
- Outcome: one intent -> deterministic code; two -> different specialist LLMs with different context; one uses complexity to choose LLM vs human. Classification is a single quick call.

## Numbers & limits
| Item | Value |
| - | - |
| Intent confidence floor | 0.5 |
| Complexity escalate | score > 1 or confidence < 0.5 |
| Questions per request | 2 |
Benefits listed: Cost, Speed ([[patterns-overview]]).

## Gotchas
- Floors (0.5 here vs 0.6 in [[confidence-gated-routing]]) are illustrative and application-specific.
- Always have a human/fallback branch for low confidence.
- Intent names in the code are only those four; any other `intent.choice` falls through with no handler in the shown code [inference from the code listing].

## Related
[[patterns-overview]] · [[confidence-gated-routing]] · [[speculative-fan-out]] · [[choice]] · [[score]] · [[cb-hierarchical-classification]] · [[topic-routing]] · [[topic-classification]]
