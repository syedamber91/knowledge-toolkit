---
title: Python SDK
kind: reference
source: TypeSafe Python SDK; Python API reference index
source_url: https://docs.typesafe.ai/sdk/python, https://docs.typesafe.ai/sdk/python/api
tags: [api-sdk]
topics: [topic-agent-integration]
---
# Python SDK
> Install `typesafe-sdk`, set `TYPESAFE_API_KEY`, and call System One with the sync `TypeSafeClient` or async `AsyncTypeSafeClient`; start here, then go to [[sdk-python-usage]] for patterns.

## What it is / How it works
- Asynchronous and synchronous Python clients for the TypeSafe API. Source on GitHub: typesafe-ai/typesafe-sdk-python.
- Package name `typesafe-sdk`; import root `typesafe_sdk`.
- Install:
  - `uv add typesafe-sdk` or `pip install typesafe-sdk`
  - Add the **`http2` extra** (`typesafe-sdk[http2]`) to enable HTTP/2 (added in v0.7.2; see [[sdk-python-usage]]).
- Set `TYPESAFE_API_KEY` (create at console.typesafe.ai).
- Clients are context managers (`with` / `async with`) and own their HTTP resources; `close()` / `aclose()` release them.

## Quickstart (both flavours produce the same answers)
Async, with `AsyncTypeSafeClient`:
```python
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score
async with AsyncTypeSafeClient() as client:
    response = await client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "billing": Noul(instructions="Is this ticket about billing?"),
            "tone": Choice(instructions="What is the customer's tone?",
                           criteria={"calm": None, "frustrated": None, "angry": None}),
            "urgency": Score(instructions="How urgent is this ticket?",
                             criteria=["can wait", "this week", "today"]),
        })
print(response.nouls["billing"].noul)
print(response.choices["tone"].choice)
print(response.scores["urgency"].score)
```
Sync: identical, with `TypeSafeClient` and no `await`.

- `state` here is a JSON object (`{"document": ...}`); it may also be a plain string (see [[state]]).
- Questions are a named mapping; names are for your code ([[primitives-overview]]).

## API reference map (docs index)
| Page | Slug where captured |
|---|---|
| Sync client / Async client | [[sdk-python-clients]] |
| Types: Common, Questions, Responses | [[sdk-python-types]] |
| Retries, Exceptions | [[sdk-python-retries-and-exceptions]] |
| Constants | [[sdk-python-clients]] (constants table) |
| Usage guide | [[sdk-python-usage]] |
| Changelog | [[sdk-changelogs]] |

## What's next (per the quickstart page)
The Usage guide covers: typed responses (`response_model`), model selection, retries, HTTP/2, error handling.

## When to use / when NOT to use
- Use for Python services calling System One ([[how-to-build-with-system-one]]).
- Use the async client for concurrency (e.g. many parallel questions/requests); enable HTTP/2 when sending many concurrent requests.
- Not for JS/TS: see [[sdk-javascript]]. Other languages: raw [[http-api-reference]].

## Numbers & limits
| Item | Value |
|---|---|
| Latest documented version | 0.7.2 (2026-09-26) |
| Default base URL | `https://api.typesafe.ai` |
| Default model | `jev-latest` |
| Default timeout | 10.0 s per HTTP operation |
| Minimum Python version | not stated in the source |

## Gotchas
- Invalid or missing API keys raise `TypeSafeError` **at client construction**, before any request (v0.7.1 validates early and excludes the key value from logged exceptions).
- Empty `questions` or an empty score criteria list raises `TypeSafeError` client-side.
- Quickstart `system_one` uses keyword args `state=` / `questions=`; the Usage guide calls it positionally `(state, questions)`. Both work.
- Since v0.7.0 pydantic replaced msgspec for ser/de ([[sdk-changelogs]]).

## Related
[[sdk-overview]], [[sdk-python-usage]], [[sdk-python-clients]], [[sdk-python-types]], [[sdk-python-retries-and-exceptions]], [[quickstart]], [[noul]], [[choice]], [[score]]
