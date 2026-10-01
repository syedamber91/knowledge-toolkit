---
title: Smart Home Assistant Demo
kind: pattern
source: Demos; Smart home assistant demo (TypeSafe docs)
source_url: https://docs.typesafe.ai/demos ; https://docs.typesafe.ai/demos/smart-home
tags: [use-case, patterns, routing]
topics: [topic-routing, topic-cost-latency, topic-agent-integration]
---
# Smart Home Assistant Demo
> Demo app that evaluates smart-home requests with one up-front batch of "speculative" questions, uses an LLM only to split compound requests and to chat; reach for it as the reference for [[speculative-fan-out]] plus LLM fallback.

## What it is / How it works
- A simple Vite/React single-page app that calls the TypeSafe API to evaluate each user request. A demo video is embedded on the page (no transcript in source).
- Chief pattern: **speculative fan-out** ([[speculative-fan-out]]). Each request is evaluated against a long list of questions, many of which will be irrelevant for most requests. All are asked in parallel in one call; code filters irrelevant answers afterwards.
- Demos index page lists only this one demo ("Evaluate user smart home requests with speculative questions and LLM fallback"). It also invites users to send in killer use cases.

### Worked example: "Turn off all of the lights in the house"
Only these answers are needed by code:
| Question | Answer |
|---|---|
| What category of request is this? | smarthome command |
| What domain is this request targeting? | whole house |
| What type of device is this request targeting? | lights |
| What action should be taken on the lights? | turn off |

The last question is *speculative*: it presumes the user is commanding lights and is asked before it is known whether that is true.

### The wrong way: sequential calls
1. Ask category -> "smarthome command".
2. Only then ask domain ("whole house") and device type ("lights").
3. Only then ask the action ("turn off").
Optimizes for the minimum number of questions but is "much slower and more expensive" than batching all questions in one upfront call. (Contrast [[intent-routing]] / [[cb-parallel-questions]] for the measured batching numbers: 12.2x cheaper, 10.0x faster per [[cookbooks-overview]].)

### Pairing with an LLM
1. **Splitting a compound request:** one question is a [[noul]] asking whether the request asks for more than one distinct action. If true, an LLM splits it into a list of atomic commands; each is then evaluated by TypeSafe individually.
2. **Conversational fallback:** when TypeSafe decides the query is general information/conversation, an LLM is called to generate a free-form reply. Known deterministic behaviour stays fast and cheap; generative flexibility is available when needed. The initial TypeSafe response is so fast compared to the LLM's that it adds "negligible latency".

## When to use / when NOT to use
- Use when one input can mean many things and you want a single question set to cover a wide variety of requests.
- Use LLM only for string generation steps (splitting, chatting); let typed answers drive code paths.
- Not to do: waiting to ask a question until its relevance is certain (sequential calls).

## Numbers & limits
No latency/cost numbers are given on this page. Source code "will be available on GitHub at release"; its README explains running locally and which source bits do what. [inference] repo URL not in source.

## Gotchas
- Speculative questions must be phrased under the assumption the earlier branch is true (e.g. "what action should be taken on the lights?") — code must discard them when the category answer says otherwise.

## Related
[[speculative-fan-out]] · [[intent-routing]] · [[cb-parallel-questions]] · [[use-case-map]] · [[cookbooks-overview]] · [[noul]] · [[topic-routing]]
