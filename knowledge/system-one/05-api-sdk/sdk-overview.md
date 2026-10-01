---
title: Client SDKs Overview
kind: reference
source: Client SDKs; Python SDK; JavaScript SDK; Python and JavaScript changelogs
source_url: https://docs.typesafe.ai/sdk, https://docs.typesafe.ai/sdk/python, https://docs.typesafe.ai/sdk/javascript
tags: [api-sdk, system-one]
topics: [topic-agent-integration, topic-cost-latency]
---
# Client SDKs Overview
> Two official TypeSafe client SDKs (Python, JavaScript/TypeScript) wrap the HTTP API with typed questions/answers and automatic retries; pick this note to choose between them and see the side-by-side differences.

## What it is / How it works
- TypeSafe ships **two** client SDKs. The landing page says both provide "typed questions and answers" for the TypeSafe API and "handle retries automatically with their default retry policy".
- You may also skip SDKs and call the raw HTTP API from any language (see [[http-api-reference]]).
- Each SDK wraps one main call, **System One** (`system_one` in Python, `systemOne` in JS) that takes `state` + a named map of questions and returns answers keyed by question name, plus `model` and token `usage` (see [[state]], [[primitives-overview]], [[noul]], [[choice]], [[score]]).
- Both SDKs also expose a **models** resource to list models available to the account (name, description, release date) (see [[models-and-versions]]).

| Aspect | Python SDK | JavaScript / TypeScript SDK |
|---|---|---|
| Package | `typesafe-sdk` (pip / uv) | `@typesafe-ai/sdk` (npm) |
| Import | `typesafe_sdk` | `@typesafe-ai/sdk` |
| Runtime | not stated on the pages | Node.js 20 or newer; ships ESM, CommonJS, TS declarations |
| Clients | `TypeSafeClient` (sync) and `AsyncTypeSafeClient` | `TypeSafeClient` (promise based, returns `APIPromise`) |
| Main method | `client.system_one(state, questions, ...)` | `client.systemOne({state, questions, model?}, options?)` |
| Question builders | classes `Noul`, `Choice`, `Score` (pydantic models) or raw dicts | functions `noul()`, `choice()`, `score()` |
| Answer access | `response.nouls[name].noul`, `.choices[name].choice`, `.scores[name].score` | `response.answers[name].noul / .choice / .score` (types inferred from questions) |
| Extra typed response | `response_model=` a pydantic model (since v0.7.0) | types inferred statically via `ResultFor<Q>` |
| API key env var | `TYPESAFE_API_KEY` (required) | `TYPESAFE_API_KEY` (required) |
| Base URL env / default | `TYPESAFE_BASE_URL`, `https://api.typesafe.ai` | same |
| Default model | `jev-latest` (`TYPESAFE_DEFAULT_MODEL`) | `jev-latest` (`TYPESAFE_DEFAULT_MODEL`) |
| Default timeout | 10.0 s per HTTP operation | 10000 ms per attempt |
| Log env var | `TYPESAFE_LOG_LEVEL` (`debug,info,warning,error,off`) | `TYPESAFE_LOG_LEVEL` (`debug,info,warn,error,off`, default `warn`) |
| Latest version in docs | v0.7.2 (2026-09-26) | v0.6.0 (2026-09-15) |
| Source | github.com/typesafe-ai/typesafe-sdk-python | github.com/typesafe-ai/typesafe-sdk-js |

## Quickstart shape (both SDKs)
1. Install the package.
2. Put the API key in `TYPESAFE_API_KEY` (keys come from console.typesafe.ai).
3. Build a client, call System One with `state` and a named map of questions, read answers.

Canonical quickstart question set (same in Python docs): state = "I was charged twice. Please fix this ASAP." with a Noul "Is this ticket about billing?", a Choice "What is the customer's tone?" over `calm / frustrated / angry`, and a Score "How urgent is this ticket?" with ordered criteria `["can wait", "this week", "today"]`. The JS quickstart uses a single Choice `category` over `billing / technical / other` (all criteria `null`) and prints `response.answers.category.choice`.

## When to use / when NOT to use
- Use an SDK when you want typed answers, validation of the API key at construction, retry/backoff and per-call overrides for free.
- Use the raw HTTP API ([[http-api-reference]]) from languages with no SDK, or when you need exact wire control.
- Use an AI gateway through the Python SDK's `base_url`/`model` options (OpenRouter, Vercel AI Gateway, Pydantic AI Gateway) — see [[sdk-python-usage]].
- For coding-agent integrations prefer [[typesafe-agent-skill]] and [[jev-mcp-server]].

## Numbers & limits
| Item | Value |
|---|---|
| Python default timeout | 10.0 s (`DEFAULT_TIMEOUT`) |
| JS default timeout | 10000 ms per attempt, no total retry budget |
| JS default retries | `maxRetries` 2; backoff 500 ms initial, 5000 ms max, jitter 0.25; statuses 408, 429, 500-599 |
| Python retries | `RetryPolicy` (defaults not printed on the docs page) |
| Default model | `jev-latest` |

## Gotchas
- Python and JS differ on score criteria shape rules: Python requires a nonempty ordered sequence; JS requires at least two entries (see [[sdk-javascript-api]]). Both SDKs moved to an **ordered sequence** for `Score.criteria` in v0.6.0 (a breaking change from an integer-keyed dict).
- Timeout semantic differs: Python `RetryPolicy.timeout` is a total retry budget per call; JS `timeout` is per attempt only.
- Python log level name is `warning`; JS is `warn`.
- Typed output guarantees interface not truth ([[confidence]]).
- The JS SDK is browser-blocked by default (`dangerouslyAllowBrowser: false`) since it would expose the API key.

## Related
[[sdk-python]], [[sdk-python-usage]], [[sdk-python-clients]], [[sdk-python-types]], [[sdk-python-retries-and-exceptions]], [[sdk-javascript]], [[sdk-javascript-api]], [[sdk-changelogs]], [[http-api-reference]], [[quickstart]], [[how-to-build-with-system-one]]
