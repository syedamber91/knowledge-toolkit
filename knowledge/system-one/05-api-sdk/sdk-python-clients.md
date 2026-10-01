---
title: Python SDK Clients and Constants
kind: reference
source: Python Synchronous client; Asynchronous client; Constants
source_url: https://docs.typesafe.ai/sdk/python/api/clients/sync, https://docs.typesafe.ai/sdk/python/api/clients/async, https://docs.typesafe.ai/sdk/python/api/constants
tags: [api-sdk]
topics: [topic-agent-integration]
---
# Python SDK Clients and Constants
> Reference for `TypeSafeClient` / `AsyncTypeSafeClient` (constructor args, `system_one`, `models.list`, close) and module constants.

## What it is
Two near-identical classes. Sync: `typesafe_sdk.TypeSafeClient`; async: `typesafe_sdk.AsyncTypeSafeClient`. Both: explicit options beat env vars; empty/whitespace env values ignored. Context-manager support. Logging tip: logger `typesafe_sdk`, `TYPESAFE_LOG_LEVEL`, secret headers redacted, bodies not.

## Constructor parameters (all default `None`)
| Param | Type | Meaning |
|---|---|---|
| `api_key` | `str \| None` | Required; or `TYPESAFE_API_KEY`. Strip whitespace; reject empty / internal whitespace / control chars / non-ASCII |
| `model` | `str \| None` | Model name; or `TYPESAFE_DEFAULT_MODEL` |
| `retry` | `RetryPolicy \| None` | Retry behaviour; `RetryPolicy(max_retries=0)` disables ([[sdk-python-retries-and-exceptions]]) |
| `timeout` | `float \| httpx2.Timeout \| None` | HTTP op timeout; inherits `http_client.timeout` if supplied, else SDK default (10.0 s) |
| `headers` | `Mapping[str,str] \| None` | Extra request headers |
| `transport` | `httpx2.BaseTransport` (sync) / `httpx2.AsyncBaseTransport` (async) | Custom transport, closed when SDK client closes |
| `http_client` | `httpx2.Client` / `httpx2.AsyncClient` | Mutually exclusive with `transport`; closed with the SDK client |
| `base_url` | `str \| None` | API root; or `TYPESAFE_BASE_URL` |

Raises at construction: `TypeSafeError` (API key missing/invalid, or timeout invalid); `ValueError` (both `transport` and `http_client` supplied).

## `system_one` (async: `await`; sync: plain)
Answers named questions about text or structured state. Parameters:
| Param | Type | Default | Notes |
|---|---|---|---|
| `state` | `JSONContent` | required | Text, JSON object, or array. See [[state]] |
| `questions` | `Mapping[str, Question]` | required | **Nonempty** mapping of names to question objects or raw dicts |
| `model` | `str \| None` | `None` | Override; `None` inherits client default |
| `retry` | `RetryPolicy \| None` | `None` | Per-call override |
| `timeout` | `float \| httpx2.Timeout \| None` | `None` | Per-call override, seconds |
| `extra_headers` | `Mapping[str,str] \| None` | `None` | Additional headers |
| `extra_body` | `Mapping[str, JSONValue \| None] \| None` | `None` | Top-level body fields, shallow-merged **after** `state`/`model`/`questions` are set; last-write-wins; collisions override; objects replaced not deep-merged |
| `response_model` | `type[ResponseT] \| None` | `None` | Pydantic `BaseModel` describing the response incl. nested answer models |

Returns: instance of `response_model`, or `SystemOneResponse` (answers keyed by question name + model and token usage).

Raises:
| Exception | When |
|---|---|
| `TypeSafeError` | Questions empty, or a score question's criteria list empty |
| `TypeSafeAPIError` | Unsuccessful HTTP response after retries |
| `TypeSafeAPIConnectionError` | Cannot connect or times out after retries |
| `TypeSafeAPIResponseValidationError` | Response body does not match the response model |

Question forms (both shown in source): named objects (`Noul(instructions=...)`, `Choice(..., criteria={"calm": None, "angry": None})`) or dicts (`{"type": "noul", "instructions": ...}`, `{"type": "choice", "instructions": ..., "criteria": {...}}`); state as dict e.g. `{"message": "I was charged twice. Please help."}`. They can be mixed in one request. Asserts in docs: `0 <= result.nouls["billing"].noul <= 1` and `result.choices["tone"].choice in {"calm","angry"}`.

## `models` (cached property) → Models resource
`client.models.list()` (async: `await`). Class names: `typesafe_sdk.Models` / `typesafe_sdk.AsyncModels`.
| Param | Notes |
|---|---|
| `retry` | per-call `RetryPolicy` override |
| `timeout` | per-operation override; `None` inherits |
| `extra_headers` | overrides for extra headers; authentication, SDK identification and `Accept` remain **protected** |
Returns `ListModelsResponse` whose `models` hold each model's name, description, release date ([[sdk-python-types]], [[models-and-versions]]). Raises `TypeSafeAPIError`, `TypeSafeAPIConnectionError`.

## Closing
- Sync `close() -> None`; async `aclose() -> None` — release network resources and close the underlying HTTP client, **including a supplied one**.

## Constants (`typesafe_sdk.constants`)
| Constant | Value | Role |
|---|---|---|
| `API_KEY_ENV` | `'TYPESAFE_API_KEY'` | API key env var |
| `BASE_URL_ENV` | `'TYPESAFE_BASE_URL'` | base URL env var |
| `DEFAULT_MODEL_ENV` | `'TYPESAFE_DEFAULT_MODEL'` | default model env var |
| `LOG_LEVEL_ENV` | `'TYPESAFE_LOG_LEVEL'` | logging level env var |
| `DEFAULT_BASE_URL` | `'https://api.typesafe.ai'` | default API base |
| `DEFAULT_MODEL` | `'jev-latest'` | default model |
| `DEFAULT_TIMEOUT` | `10.0` | seconds, per HTTP operation |

## Gotchas
- `transport` and `http_client` are exclusive.
- `extra_body` can clobber `questions` — use deliberately.
- The `models.list` extra_headers cannot override auth.
- Async client must be closed via `aclose()` or `async with`.

## Related
[[sdk-python]], [[sdk-python-usage]], [[sdk-python-types]], [[sdk-python-retries-and-exceptions]], [[sdk-overview]], [[http-api-reference]]
