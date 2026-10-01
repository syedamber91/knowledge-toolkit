---
title: Patterns Overview
kind: pattern
source: Patterns
source_url: https://docs.typesafe.ai/patterns
tags: [patterns, system-one]
topics: [topic-routing, topic-cost-latency]
---
# Patterns Overview
> Index of the four architectural patterns for building with TypeSafe; each is one atomic-decision composition idea.

## What it is / How it works
TypeSafe is designed to sit *within* a larger system, powering decisions with AI. Key skill: think in **discrete, atomic decisions that compose into complex system behavior**. Prerequisites assumed: the primitives ([[primitives-overview]]) and how confidence works ([[confidence]]).

| Pattern | What it does | Benefits (as listed) | Note |
| - | - | - | - |
| Speculative Fan-Out | Send many questions in one call, including speculative ones; code decides what's relevant | Cost, Speed | [[speculative-fan-out]] |
| Confidence-Gated Routing | Use confidence as a second decision axis to build safer systems | Reliability, Safety | [[confidence-gated-routing]] |
| Composite Scoring | Combine several dimensions of analysis into a single score | Cost, Reliability, Speed | [[composite-scoring]] |
| Intent Routing | Classify a user's intent and route to the appropriate handler | Cost, Speed | [[intent-routing]] |

## When to use / when NOT to use
- Fan-out: whenever multiple answers might be needed; avoids serial round trips.
- Confidence gating: whenever acting on a wrong answer has asymmetric cost.
- Composite scoring: ranking/selecting by several criteria with adjustable weights.
- Intent routing: cheap front-door classifier before expensive handlers.
- They combine: [[how-to-build-with-system-one]] triage example uses fan-out + composite scoring + confidence gates together.

## Worked example(s)
Each pattern page has one: support ticket triage (fan-out), voice banking (confidence), resume screening (composite), customer-service routing (intent).

## Numbers & limits
No numbers on this page; thresholds live in each pattern.

## Gotchas
- Source invites users to send in "killer use cases" for inclusion (note to the vendor; not an operational fact).
- Thresholds in pattern pages are illustrative; calibrate on your data ([[how-to-build-with-system-one]] step 8).

## Related
[[speculative-fan-out]] · [[confidence-gated-routing]] · [[composite-scoring]] · [[intent-routing]] · [[how-to-build-with-system-one]] · [[topic-routing]]
