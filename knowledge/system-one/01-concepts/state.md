---
title: State
kind: concept
source: Concepts > State
source_url: https://docs.typesafe.ai/concepts/state
tags: [state-design, system-one]
topics: [topic-state-design]
---
# State
> The `state` field = the content (and supporting facts) a System One model evaluates; one state per request, many questions against it. String, JSON object, or array of text.

## What it is / How it works
- **State** is the content you ask a System One model to evaluate: a support message, a passage, or the current state of your application. Passed in the `state` field of an API request, alongside the questions ([[primitives-overview]]).
- Each request evaluates **one state against one or more questions**. All questions see the same state and are evaluated **independently**. Choice, Score and Noul can be mixed in one request.
- Mental model: state is "the material you would present to a panel of experts before asking them to make a judgment."
- In Python pass the string/dict/list directly: `client.system_one(state=...)` ([[sdk-python-usage]]).

### Accepted shapes
| Format | Useful for | Example |
| - | - | - |
| String | A message, article, or passage | `"My card was charged twice."` |
| Object | Named fields, related records, application state | `{"message": "My card was charged twice.", "order_id": "A-104"}` |
| Array | A sequence of messages or records | `["Hi", "My customer number is TS1337.", "My card was charged twice."]` |
- **Use an object for most requests** so each part has a descriptive name and relationships stay clear. A string suits simple cases with just one piece of text.
- **Text only:** string, JSON object, or array of text values; no images/audio/video (yet). **Primary training language is English;** other languages including CJK scripts are accepted but currently have **lower accuracy** (see [[models-and-versions]], "Language support").

## When to use / when NOT to use
- Put related information together **when the decision requires comparing those parts** (conversation + order + policy = one state).
- **Separate content from questions:** state = content and supporting facts; [[primitives-overview|questions]] = the judgments about it. E.g. keep refund request + policy in the state; ask whether the customer requested a refund and whether the policy supports it.
- Don't pad state with irrelevant detail ([[jev-1-13-jaggedness]] #5; [[how-to-build-with-system-one]] "Decompose the input state").

## Worked example(s)
Support conversation as ONE state (even though it holds a conversation, an order and a policy):
```json
{ "ticket": { "subject": "Duplicate charge",
    "messages": [ {"from":"customer","text":"I was charged twice for order A-104. Please refund the duplicate."},
                  {"from":"support","text":"We are checking the charges."} ] },
  "order": { "id": "A-104", "charges": [ {"amount_usd":49,"status":"captured"}, {"amount_usd":49,"status":"captured"} ] },
  "refund_policy": "Duplicate charges are eligible for a refund." }
```

## Numbers & limits
Token budgets (64k per request; 32k for state + longest question) live in [[models-and-versions]].

## Gotchas
- Non-text inputs must be converted to text/structured fields first.
- Non-English / CJK: test on your own content; watch [[confidence]].
- Source points to the API reference ([[http-api-reference]]) for the request schema and the SDK pages ([[sdk-overview]]) for typed inputs and response handling.

## Related
[[system-one-model-category]] · [[how-to-build-with-system-one]] · [[advanced-structure]] · [[models-and-versions]] · [[jev-1-13-jaggedness]] · [[topic-state-design]]
