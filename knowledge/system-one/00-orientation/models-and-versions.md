---
title: Models And Versions
kind: reference
source: Models
source_url: https://docs.typesafe.ai/models
tags: [api-sdk, cost-latency, model-limits]
topics: [topic-model-selection, topic-cost-latency]
---
# Models And Versions
> Current model (`jev-1.13.0`), price, rate limits, context budget, aliases (`jev-latest`/`jev-preview`), customization stance, language support, `GET /v1/models`.

## What it is / How it works
Every model is served by the same endpoint `POST /v1/systemone`; the request `model` field selects which one handles the call ([[http-api-reference]]).

### Current model: Jev 1.13 (`jev-1.13.0`)
| Property | Value |
| - | - |
| Price (per Btok / per Mtok) | **$42 / $0.042** (Btok = billion tokens, Mtok = million) |
| What is billed | per **input** token; **output tokens are free** |
| Rate limits | **100K tokens/second** and **40 requests/second** |
| Context length | **64k tokens per request**; **32k tokens for `state` + the longest question** |
| Input | text only: string, JSON object, or array of text values; no image/audio/video |

- **Rate limits:** exceeding either returns `429 Too Many Requests`. Client SDKs retry with backoff by default and honor the `retry-after` header when present. Direct HTTP callers: see "Handling rate limits" in [[http-api-reference]].
- **Context:** Jev ingests the `state` once and evaluates every question against it in parallel. The 64k budget covers state + all questions combined; the 32k budget applies to state + the single longest question. Packing many questions: [[speculative-fan-out]]. Accuracy shifts as state grows: [[jev-1-13-jaggedness]] ("Large state full of irrelevant detail").
- **Input:** pre-process non-text (images, audio, video, binaries) into text/structured fields before sending as `state` ([[state]]).
- **WARNING in source: rate limits adjust dynamically.** Serving very large demand; limits "can change without notice" while upcoming large GPU deals land and more users are let in. Stable limits later. **Higher limits on custom and enterprise plans:** sales@typesafe.ai.

### Aliases
| Alias | Points to | Meaning |
| - | - | - |
| `jev-latest` | `jev-1.13.0` | Most recent **stable, official** release. SDK default; the name used in docs examples |
| `jev-preview` | `jev-1.13.0` | Most recent release, official or not; moves ahead of `jev-latest` when a preview build exists |
- **Warning:** `jev-preview` currently points to the same model as `jev-latest`; **no preview build available right now**.
- An alias moves when a new release ships, so answers behind it can change without a change on your side. The response `model` field reports the versioned ID that answered — log it. **If you tuned confidence thresholds against a specific version, pin that version's ID** and migrate on your own schedule.

### Customizing Jev
- **Not** fine-tuned or LoRA-adapted with customer data; trained with RLCD ([[ai-primer-calibrated-decisions]]); the same weights serve every account.
- Shape answers through the request instead:
  - Put proprietary content/records/reference material in `state` ([[state]]).
  - Encode domain rules and boundary cases in each question's `instructions` and `criteria` ([[how-to-build-with-system-one]], [[advanced-structure]]).
  - Decompose broad judgments into atomic questions, combine in code ([[composite-scoring]]); optionally train a downstream classical model on Jev's probabilities ([[cb-autoresearch-feature-discovery]]).

### Language support
Natural-language text. **English is the primary training language and where accuracy is currently best.** Other languages, including CJK scripts, are handled but not equally well: test on your own content before relying on Jev for non-English workloads and pay close attention to [[confidence]] when routing.

### Data handling
Jev is **not trained on customer requests or responses**. Legal docs: DPA, Privacy Policy, ZDR for enterprise (see "Other facts" in [[jev-introduction]]).

### Listing models: `GET /v1/models`
- Returns names your account can send in `model`, each with `name` (ID or alias), `description`, `release_date`. **Currently lists the aliases.** Versioned IDs like `jev-1.13.0` are accepted by `model` whether or not listed.
- Python: `client.models.list().models` (iterate `.name/.release_date/.description`); JS: `new TypeSafeClient()` from `@typesafe-ai/sdk`, `await client.models.list()`; cURL: `curl https://api.typesafe.ai/v1/models -H "Authorization: Bearer $TYPESAFE_API_KEY"`. SDK refs: Python `typesafe_sdk.Models.list`, JS `Models` interface ([[sdk-python-clients]], [[sdk-javascript-api]]).

## When to use / when NOT to use
- Use `jev-latest` for exploration/defaults; **pin `jev-1.13.0`** where thresholds are tuned.
- Don't expect per-customer fine-tuning. Don't send non-text input.

## Worked example(s)
Alias resolution: send `model: "jev-latest"` -> response `model: "jev-1.13.0"` ([[quickstart]]).

## Numbers & limits
(See tables above.) Cost math from source numbers: $0.042 per million input tokens; the [[quickstart]] sample used 392 input tokens [inference: ~$0.0000165 for that call at $0.042/Mtok].

## Gotchas
- Rate limits may change without notice.
- `jev-preview` == `jev-latest` today.
- Alias drift silently changes answers; thresholds are version-specific.
- The jaggedness page's code sample constructs `TypeSafeClient(model="jev-1.13")` (no patch version) — a form not otherwise documented here; whether `jev-1.13` resolves is **not stated** in Models (only `jev-1.13.0` and aliases are).

## Related
[[jev-introduction]] · [[jev-1-13-jaggedness]] · [[quickstart]] · [[http-api-reference]] · [[state]] · [[confidence]] · [[topic-model-selection]] · [[topic-cost-latency]]
