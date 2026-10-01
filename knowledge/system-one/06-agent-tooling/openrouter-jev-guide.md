---
title: OpenRouter Jev Guide
kind: reference
source: Jev Documentation - TypeSafe Decision Model on OpenRouter (openrouter.ai/docs/guides/community/jev)
source_url: https://openrouter.ai/docs/guides/community/jev
tags: [api-sdk, alternatives, cost-latency]
topics: [topic-agent-integration, topic-cost-latency, topic-model-selection]
---
# OpenRouter Jev Guide
> THIRD-PARTY (OpenRouter's community-guide page, not TypeSafe docs). How to reach Jev through an OpenRouter key instead of a TypeSafe account: model ids, two API surfaces, billing, limits, cookbooks.

Provenance: OpenRouter hosts this page as an index to its Jev resources and points to upstream TypeSafe documentation for concepts/SDKs. Facts below are as stated by OpenRouter "as of the Jev model page"; OpenRouter itself defers to the model page for the current price (no number on this page).

## What it is / how it works
- Jev = structured decision model from TypeSafe, "the first of its System One models". Send application state + one or more typed questions; get typed answers with probabilities, not generated text. Billed to the OpenRouter account.
- **Model ids:** `typesafe/jev-1.13`; alias `~typesafe/jev-latest` tracks the newest release.
- **Access:** "no waitlist or separate TypeSafe account" — just create an OpenRouter API key; first call "under five minutes". The same OpenRouter key authenticates both API surfaces and the TypeSafe SDK pointed at OpenRouter.
- **Primitives (as OpenRouter tabulates):**

| Primitive | Question | Returns |
|---|---|---|
| Choice | Which one of these options? | selected option, probability per option, confidence |
| Noul | Does this condition hold? | probability of yes |
| Score | Where on an ordered scale? | probability-weighted position, probability per level, confidence |

- Output is typed so code branches directly. Jev gives no reasoning traces, explanations or free text; "not a drop-in replacement for a chat model" — it replaces the prompt-and-parse step for narrow questions. Suited to routing, classification, verification, ranking, other decision points.

### Two API surfaces (same key, same billing)
| Surface | Endpoint | Use when |
|---|---|---|
| Decisions API | `POST https://openrouter.ai/api/alpha/decisions` | any language over plain HTTP, or via OpenRouter TypeScript/Python/Go SDK |
| System One API | `POST https://openrouter.ai/api/v1/systemone` | you already use the TypeSafe JS or Python SDK; switch by changing the base URL only |
The "Jev SDK" guide documents the System One path; the Decisions API reference documents the other. Do not send these questions to chat-completions ([third-party directory], [[awesome-typesafe-jev]]).

## Numbers & limits
| Item | Value (per OpenRouter) |
|---|---|
| Model id | `typesafe/jev-1.13` |
| Alias | `~typesafe/jev-latest` |
| Input | text: a state object plus questions |
| Context length | **32,000 tokens** ("the state you send plus the questions") |
| Output | typed decisions; output tokens **free** |
| Billing | per input token at the model-page price; every response has a `usage.cost` field (USD) |
| Provider | TypeSafe, routed via OpenRouter |
| Price number | not stated on this page — read the model page |

## Cookbooks it lists (OpenRouter-authored recipes; contents only described, not shown)
1. **Gate Agent Tool Calls with Jev** — checks each risky tool call against the user's request: safe calls run, unsupported refused, only ambiguous pause for a human.
2. **Cut LLM Cost with a Jev-Verified Cascade** — draft with a cheap model, verify draft against retrieved context with Jev, escalate to a stronger model only if the check fails.
3. **Classify and Tag Text at Scale** — one category + any number of tags per item in a batch; picks a threshold per tag from a small labelled sample; computes cost per 1,000 items from `usage.cost`.
4. **Classify Reddit and YouTube Comments (with ScrapeCreators)** — scores each comment for relevance and sentiment; stores raw judgments so thresholds can be re-tuned without new requests.
5. **Auto-Approve Coding Agent Permission Prompts** — answers prompts from Claude Code, Codex, Cursor, OpenCode via a Jev reversibility check; routine commands run, risky ones still ask.
Other resources: Jev Tutorial (curl/TypeScript/Python first Choice/Noul/Score call), Jev model page (pricing, context, provider, data policy), Decisions API reference, Jev SDK guide, **Jev Router** (OpenRouter router that uses Jev to pick a model and reasoning effort per request), **Jev Lab** (live browser demos: ticket triage, agent oversight, structured extraction; shows state, questions, raw probabilities).
TypeSafe docs it recommends for design: System One, How to build with System One (decomposing workflows), State (what to send, nested field references), Primitives, Confidence (reading probabilities, thresholds), JS SDK, Python SDK. See [[state]], [[primitives-overview]], [[confidence]], [[sdk-overview]].

## FAQ (as stated)
- Is Jev an LLM? No; System One decision model, typed answers + probabilities, no text/reasoning/explanations.
- Who makes it? TypeSafe; OpenRouter routes and bills.
- Cost? Input tokens only; output free; price on model page; `usage.cost` per response.
- Context window? 32,000 tokens (state + questions).
- TypeSafe account/key needed? No — OpenRouter key authenticates both.
- Can Jev explain answers? No. If you need written justification, have Jev decide then have a chat model explain it; if confidence is low, route to a human.

## When to use / not
- Use when you already have OpenRouter billing, want no TypeSafe signup, or want Decisions API from any HTTP client. [inference] Also convenient where one gateway key is mandated.
- Not for prose, explanations, or open-ended reasoning.

## Gotchas / disagreements with other third-party sources
- **Context limit conflict:** OpenRouter says 32,000 tokens total for state+questions. The dev.to guide ([[community-guide-devto]]) says 64k tokens for state plus all questions together and 32k for state plus the single longest question. Not resolved by sources; the first-party limits live in TypeSafe docs (see [[http-api-reference]], [[models-and-versions]]) — verify there. [inference] The difference may be per-route (OpenRouter vs direct), but neither source says so.
- **Access:** OpenRouter says no waitlist; dev.to says TypeSafe direct keys are waitlisted early access (or via Vercel AI Gateway). Consistent if routes differ.
- Third-party directory also lists OpenRouter route as `typesafe/jev-1.13` or its latest-model route and warns about request-shape differences ([[awesome-typesafe-jev]]).
- The directory mentions OpenRouter as a Jev provider in numerous tools (jev-cli, pytest-jev, Jev Cookbook, jev-certify via OpenRouter); gateways may not expose the exact model version (Jevals, jev-ood-calibration notes) — log versions.

## Related
[[awesome-typesafe-jev]] · [[community-guide-devto]] · [[community-guide-marktechpost]] · [[sdk-overview]] · [[http-api-reference]] · [[models-and-versions]] · [[typesafe-agent-skill]] · topics: [[topic-cost-latency]] [[topic-agent-integration]] [[topic-model-selection]]
