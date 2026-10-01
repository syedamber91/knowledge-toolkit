---
title: Python SDK Usage Guide
kind: cookbook
source: Python SDK Usage
source_url: https://docs.typesafe.ai/sdk/python/usage
tags: [api-sdk, cost-latency]
topics: [topic-agent-integration, topic-cost-latency, topic-model-selection]
---
# Python SDK Usage Guide
> Patterns for the Python SDK: calling System One, typed `response_model`, model selection, AI-gateway base URLs, HTTP/2, retries, errors, logging, env vars, forward-compat escape hatches.

## 1. Calling System One
Same call in async (`AsyncTypeSafeClient`, `await client.system_one(...)`) and sync (`TypeSafeClient`). State is positional first arg, questions second.
```python
result = client.system_one(
    "I was charged twice. Please help ASAP.",
    {"billing": Noul(instructions="Is this about billing?"),
     "tone": Choice(instructions="What is the tone?", criteria={"calm": None, "angry": None}),
     "urgency": Score(instructions="How urgent is this?", criteria=["low", "medium", "high"])})
result.nouls["billing"].noul; result.choices["tone"].choice; result.scores["urgency"].score
```
See [[noul]], [[choice]], [[score]], [[state]].

## 2. Typed `system_one` responses (`response_model`)
- Pass `response_model=` a pydantic model to make results type-safe.
- **Inherit `SystemOneResponse`** and declare answer fields by question name:
  ```python
  class BillingResponse(SystemOneResponse):
      billing: NoulAnswer
  result = client.system_one("I was charged twice.",
      {"billing": Noul(instructions="Is this about billing?")}, response_model=BillingResponse)
  assert 0 <= result.billing.noul <= 1
  assert result.billing == result.nouls["billing"]
  print(result.request_id)   # still available when inheriting SystemOneResponse
  ```
- **Custom response types** need not inherit it: define `BillingAnswers(BaseModel)` with `billing: NoulAnswer`, then `BillingResponse(BaseModel)` with `answers: BillingAnswers`; access as `result.answers.billing.noul`. (A fully custom model lacks `request_id`/`raw_http_response` conveniences unless inheriting — `[inference]`, source only shows `request_id` on the inheriting variant.)
- Answer classes available: `NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer` ([[sdk-python-types]]).
- Mismatch between body and model raises `TypeSafeAPIResponseValidationError` ([[sdk-python-retries-and-exceptions]]).

## 3. Choosing a model
- List: `await client.models.list()` / `client.models.list()` (returns name, description, release date; see [[models-and-versions]]).
- Select at construction: `TypeSafeClient(model="jev")` / `AsyncTypeSafeClient(model="jev")`.
- Per call override: `system_one(..., model=...)`; default via `TYPESAFE_DEFAULT_MODEL`; fallback `jev-latest`.

## 4. Configuring base URL / AI gateways
Set `base_url=` on the client or `TYPESAFE_BASE_URL`. The alternative API must follow the **TypeSafe OpenAPI spec** (api.typesafe.ai/docs/). Use the gateway's own API key and model id:

| Gateway | `api_key` source | `base_url` | `model` |
|---|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api` | `~typesafe/jev-latest` (OpenRouter model id page: openrouter.ai/~typesafe/jev-latest/) |
| Vercel AI Gateway | `AI_GATEWAY_API_KEY` | `https://ai-gateway.vercel.sh/typesafe` | `typesafe-ai/jev` |
| Pydantic AI Gateway | `PYDANTIC_AI_GATEWAY_API_KEY` | `https://gateway-us.pydantic.dev/proxy/typesafe` | `jev-latest` |

Each shown for async (`async with AsyncTypeSafeClient(api_key=os.environ[...], base_url=..., model=...)`) and sync. See [[openrouter-jev-guide]].

## 5. HTTP/2
- Tip from source: often beneficial when sending **many concurrent requests**, since requests multiplex over one connection. Install `'typesafe-sdk[http2]'`.
- Uses `httpx2` (docs link: pydantic.dev/docs/httpx2): `AsyncTypeSafeClient(http_client=httpx2.AsyncClient(http2=True))` / `TypeSafeClient(http_client=httpx2.Client(http2=True))`.
- `http_client` and `transport` are mutually exclusive; the SDK closes a supplied client when it closes.

## 6. Retries
- Pass `RetryPolicy` as `retry=` on the client **or** per call. Example: `RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0)`.
- Invalid API keys raise `TypeSafeError` during client creation, before any request or retry.
- Disable retries: `RetryPolicy(max_retries=0)`.
- Full field table: [[sdk-python-retries-and-exceptions]].

## 7. Error handling
`except TypeSafeAPIError as error: print(error.status, error.request_id)` (works in sync and async). Hierarchy and fields in [[sdk-python-retries-and-exceptions]].

## 8. Logging
- Logger name `typesafe_sdk`; standard logging: `logging.getLogger("typesafe_sdk").setLevel(logging.DEBUG)`.
- Or set `TYPESAFE_LOG_LEVEL` to `debug`, `info`, `warning`, `error`, `off` **before importing the SDK** (applied once at import).
- `info` = one summary line per request; `debug` also logs request/response headers and bodies.
- Secret headers (authorization, API keys, cookies, any header name containing `token` or `secret`) are redacted. **Request and response bodies are NOT redacted** — mind your state contents (privacy; see [[topic-cost-latency]]).

## 9. Environment variables
| Variable | Configures | Default |
|---|---|---|
| `TYPESAFE_API_KEY` | API key (required) | none |
| `TYPESAFE_BASE_URL` | API root URL | `https://api.typesafe.ai` |
| `TYPESAFE_DEFAULT_MODEL` | default model | `jev-latest` |
| `TYPESAFE_LOG_LEVEL` | `typesafe_sdk` logger level, applied once at import | unset |

- Explicit options beat env vars; empty/whitespace-only env values are ignored.
- API key whitespace: leading/trailing whitespace (including newlines from key files) is stripped. Empty keys, internal whitespace, control characters, non-ASCII characters are rejected before sending. An explicitly empty `api_key` does **not** fall back to the environment.

## 10. Forward compatibility (adopt API features before SDK support)
- **`extra_body={"beam_width": 4}`** — extra top-level request fields. The source says `beam_width` is **illustrative**; only send fields the API supports. Shallow merge, last write wins (can overwrite `state`, `model`, `questions`); objects replaced, not deep-merged.
- **Raw question dicts**: `{"billing": {"type": "noul", "instructions": "About billing?", "weight": 2}}`. The `weight` key here is an unknown-field example. Tip: unknown fields are an escape hatch; ignore their type-check errors and prefer upgrading the SDK.
- **Unknown answer kinds**: the SDK logs a warning and skips them; use `result.raw_http_response.json()["answers"]` to see everything.
- **Unknown response fields** on recognised responses are ignored.

## Gotchas
- Models: TypeSafe's own docs show `~typesafe/jev-latest` for OpenRouter here, whereas the jev-mcp README says OpenRouter serves pinned versions (maps `jev-latest` to `typesafe/jev-1.13`) — see [[jev-mcp-server]]; verify the id against the gateway.
- Logging bodies leak user content if debug is on in production.
- `TYPESAFE_LOG_LEVEL` read once at import; change later via `logging`.

## Related
[[sdk-python]], [[sdk-python-clients]], [[sdk-python-types]], [[sdk-python-retries-and-exceptions]], [[sdk-overview]], [[http-api-reference]]
