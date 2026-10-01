---
title: Jev Introduction
kind: concept
source: Introduction (docs.typesafe.ai); Legal
source_url: https://docs.typesafe.ai/introduction ; https://docs.typesafe.ai/legal
tags: [system-one, primitives]
topics: [topic-calibration, topic-agent-integration, topic-model-selection]
---
# Jev Introduction
> Jev = TypeSafe's flagship model and the first System One model: send a state plus typed questions, get typed answers (+ probabilities, + confidence for Choice/Score) your code can branch on. Read this first to know what Jev is and the three question types.

## What it is / How it works
- Problem framed by the docs: LLMs produce text for humans; when code needs a judgment, you coerce text into structure and parse it back. Jev skips both steps: no text generation, no parsing.
- Jev evaluates typed **questions** against a **state** and returns typed values and probability distributions your code can branch on, sort by, and route with. See [[state]], [[system-one-model-category]].
- **One request in, one response out.** Input = `state` + `questions`; the model evaluates each question against the state **in parallel and in isolation**; output = typed answers + probabilities + confidence (Choice and Score only).
- Adding questions "barely changes the response time"; because each question is evaluated independently, extra questions do **not** cause context-rot. (This is the basis of [[speculative-fan-out]].)
- All three question types can be mixed in one API call.

### The three primitives (AI primitives; "modular, composable, structured, reliable, fast")
| Question type | Goal | Returns |
| - | - | - |
| Choice | Choose an option from a list | `choice`, `probabilities`, `confidence` |
| Score | Score the state on a rubric | `score`, `probabilities`, `confidence` |
| Noul | Is this statement true? | `noul` (0–1) |

Details: [[primitives-overview]], [[choice]], [[score]], [[noul]]; confidence semantics: [[confidence]].

### Atomic questions, composed in code (core design rule)
- Each question should ask **one specific, well-scoped thing** — a "gut-check determination": the kind of judgment a highly knowledgeable person could make in a few seconds given the right context.
- If the question needs extended reasoning or weighs multiple independent factors: **decompose** it, ask each factor as its own question, combine results with logic in your code. Keeps each evaluation reliable and gives full control over weighting.
- Source's example: instead of "rate this startup pitch", ask separately about **market size, technical feasibility, differentiation**, combine with your own formula; when priorities shift, change a coefficient in code rather than rewriting a prompt. See [[composite-scoring]], [[how-to-build-with-system-one]].

## When to use / when NOT to use
- Use for fast structured judgments inside a software workflow (routing, scoring, true/false checks) — see [[jev-with-coding-agents]] for the "when worth reaching for" list.
- NOT a text generator, chat model, or code completion model — see [[jev-with-coding-agents]], [[system-one-model-category]]. Questions that need extended reasoning / multi-factor weighing must be decomposed. Known weak spots: [[jev-1-13-jaggedness]].

## Worked example(s)
Diagram in source (flowchart): `state + questions` --one request--> TypeSafe model "evaluate each question against the state in parallel" --one response--> `typed answers + probabilities + confidence (Choice and Score)` --> your code: branch, sort, and route. Concrete request/response: [[quickstart]]. Startup-pitch decomposition above is the only other example on this page.

## Numbers & limits
No numeric limits on this page (limits/prices live in [[models-and-versions]]).

## Gotchas
- Confidence is returned for Choice and Score; Noul returns just `noul` (0–1) in the documented shape.
- Don't hide several judgments inside one question; don't ask for extended reasoning in one question.

## Other facts
- **Next-step pages the source points to:** Quick Start ([[quickstart]]), AI Primer ([[ai-primer-calibrated-decisions]]), Primitives (Questions) ([[primitives-overview]]), Confidence ([[confidence]]), Patterns ([[patterns-overview]]).
- **Legal page (docs.typesafe.ai/legal):** links to three documents — Data Processing Agreement (how customer data is processed on your behalf, incl. data retention; typesafe.ai/legal/data-processing), Master Customer Agreement (general terms for your account; typesafe.ai/legal/mca), Privacy Policy (what data is collected and how used, incl. the **commitment not to train models on user data**; typesafe.ai/legal/privacy-policy). **Zero data retention (ZDR)** is offered to enterprise customers: contact sales@typesafe.ai. (Same data-handling statement appears in [[models-and-versions]].)

## Related
[[system-one-model-category]] · [[ai-primer-calibrated-decisions]] · [[jev-with-coding-agents]] · [[quickstart]] · [[models-and-versions]] · [[jev-1-13-jaggedness]] · [[state]] · [[primitives-overview]] · [[patterns-overview]] · [[topic-calibration]]
