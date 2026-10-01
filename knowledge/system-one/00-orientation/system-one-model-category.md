---
title: System One Model Category
kind: concept
source: Concepts > System One
source_url: https://docs.typesafe.ai/concepts/system-one
tags: [system-one, confidence]
topics: [topic-calibration, topic-model-selection]
---
# System One Model Category
> What a "System One model" is (fast, structured, calibrated decisions for software), how it differs from an LLM, and the refund-workflow example of using it inside a larger system.

## What it is / How it works
- A **System One model** is a class of AI models built to make fast, structured decisions that software can use directly. It evaluates a [[state]] and returns typed answers and probabilities. **Jev** is TypeSafe's flagship model and the *first* System One model ([[jev-introduction]]).
- Like an LLM it understands natural-language input; unlike an LLM it returns **typed decisions and probabilities, not generated text**.
- **Input is text only (currently):** strings, JSON objects, arrays of text. Images, audio, video not supported "(yet)".
- **Name origin:** Daniel Kahneman's *Thinking, Fast and Slow* — System 1 = fast/intuitive, System 2 = slower/deliberate. Here the emphasis is fast, focused judgments.

### How it differs from an LLM
- Trained for **calibrated decisions**: probabilities are optimized against outcomes to reflect uncertainty (see [[ai-primer-calibrated-decisions]]). Calibration is measured across *groups* of predictions; it does **not** guarantee any individual answer is correct.
- Does **not** write replies, produce code, or generate explanations of its reasoning. You define possible answers through primitives:

| Primitive | Example question | Example answer space | Example output |
| - | - | - | - |
| Choice | Which team should handle this ticket? | `billing`, `technical`, `account` | `choice: "billing"` |
| Score | How frustrated is this customer? | 0 = calm, 1 = frustrated, 2 = very frustrated | `score: 1.4` |
| Noul | Does this message request a refund? | true / false | `noul: 0.95` |
(Source states these are illustrative configurations/values; primitive pages hold the real options — [[primitives-overview]].)

Note `score: 1.4` in the example shows Score returns a fractional (expected) value over the rubric levels, not just an integer [inference from the example; see [[score]]].

## When to use / when NOT to use
- Use as fast judgment steps inside a larger workflow; code stays in charge ([[how-to-build-with-system-one]]).
- Answers include [[confidence]] so you can decide when to act and when to escalate to a person or a reasoning model.
- Not for generation of text/code/explanations. Model-specific weak spots: [[jev-1-13-jaggedness]].

## Worked example(s) — refund request (fast judgments inside a workflow)
1. Build a state containing the customer's message, the relevant transactions, and the refund policy.
2. Ask independent questions together: was a refund requested? does the evidence indicate a duplicate charge? does the policy support a refund?
3. Combine the answers with deterministic checks in code, then route the case for action or review.
Because outputs are typed/constrained, code can inspect and combine them into predictable workflows.

## Numbers & limits
| Item | Value |
| - | - |
| Input modality | text only (string / JSON object / array of text) |
| Default model name in docs & SDK | `jev-latest` |
| Endpoint | `POST /v1/systemone` (HTTP API); `model` field selects the model |
Prices, aliases, rate limits: [[models-and-versions]].

## Gotchas
- Calibration ≠ per-answer correctness guarantee.
- Don't expect explanations/rationales back — there are none.

## Other facts
- Call a System One model via a client SDK or `POST /v1/systemone`. Source says to start with [[state]] then Primitives.

## Related
[[jev-introduction]] · [[ai-primer-calibrated-decisions]] · [[state]] · [[confidence]] · [[how-to-build-with-system-one]] · [[models-and-versions]] · [[topic-calibration]]
