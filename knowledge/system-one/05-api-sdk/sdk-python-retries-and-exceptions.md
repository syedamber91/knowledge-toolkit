---
title: Python SDK Retries and Exceptions
kind: reference
source: Python SDK Retries; Exceptions
source_url: https://docs.typesafe.ai/sdk/python/api/retries, https://docs.typesafe.ai/sdk/python/api/exceptions
tags: [api-sdk, cost-latency]
topics: [topic-agent-integration, topic-cost-latency]
---
# Python SDK Retries and Exceptions
> `RetryPolicy` fields and the `TypeSafe*` exception hierarchy of the Python SDK, with which statuses map to which class.

## RetryPolicy (dataclass; `typesafe_sdk.RetryPolicy`)
Pass as `retry=` on a client or per `system_one` / `models.list` call. The docs page lists fields but **does not print default values**; do not assume them (the JS SDK defaults differ in naming and are given in [[sdk-javascript-api]]).
| Field | Meaning |
|---|---|
| `max_retries` | Max retries **after the initial attempt**; `0` disables retries |
| `backoff_initial` | First backoff delay in seconds, doubled each attempt up to `backoff_max`; zero disables backoff |
| `backoff_max` | Maximum backoff delay in seconds; zero disables backoff |
| `backoff_jitter` | Fraction of each backoff delay randomly **subtracted**, between 0 and 1 |
| `http_statuses` | HTTP status codes that are retried |
| `respect_retry_after` | Honor `Retry-After` and `retry-after-ms` response headers |
| `api_connection_error` | Retry `TypeSafeAPIConnectionError` (cannot reach / read from server) |
| `api_timeout_error` | Retry `TypeSafeAPITimeoutError` (exceeded timeout) |
| `exceptions` | Extra exception types that trigger a retry, on top of built-in rules |
| `predicate` | Optional callable given the raised exception; `True` triggers a retry in addition to other rules |
| `timeout` | **Total retry budget in seconds per SDK call**, including the initial attempt and delays; `None` = no limit. Stops *before* a retry whose delay would reach or exceed the budget, re-raising the last error |

Example from source: `RetryPolicy(max_retries=3, timeout=10.0, http_statuses={429, 500, 502, 503, 504})` (an example, not stated as default). Usage guide example: `RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0)`.

Notes:
- Invalid values in `RetryPolicy` are handled (fixed in v0.6.0).
- Invalid API keys raise `TypeSafeError` **before** any request/retry.
- Separate from `RetryPolicy.timeout`, the client `timeout` (default 10.0 s) applies per HTTP operation.

## Exception hierarchy
```
Exception
 └─ TypeSafeError                    (base for SDK failures)
     ├─ TypeSafeAPIError             (unsuccessful HTTP response)
     │   ├─ TypeSafeBadRequestError            400
     │   ├─ TypeSafeAuthenticationError        401
     │   ├─ TypeSafePermissionDeniedError      403
     │   ├─ TypeSafeNotFoundError              404
     │   ├─ TypeSafeUnprocessableEntityError   422 (failed server validation)
     │   ├─ TypeSafeRateLimitError             429  (+ retry_after_ms)
     │   ├─ TypeSafeInternalServerError        5xx
     │   └─ TypeSafeAPIResponseValidationError (2xx but body missing/invalid required data)
     └─ TypeSafeAPIConnectionError   (also subclasses builtin ConnectionError; request failed without HTTP response)
         └─ TypeSafeAPITimeoutError  (also subclasses builtin TimeoutError; exceeded configured timeout)
```
### Attributes
| Class | Attribute | Meaning |
|---|---|---|
| `TypeSafeAPIError` | `status` | HTTP status code |
| | `body` | server JSON error body, plain text, or `None` for empty body |
| | `headers` | response headers |
| | `endpoint` | request method + URL **without** credentials, query params, or fragment, when available |
| | `request_id` (property) | `x-typesafe-request-id` header, or `None` |
| `TypeSafeRateLimitError` | `retry_after_ms` | server's requested wait in ms, or `None` |
| `TypeSafeAPITimeoutError` | `timeout` | timeout setting in seconds or `httpx2.Timeout` |
| `TypeSafeAPIResponseValidationError` | `field_path` | dotted path to offending field, e.g. `answers.tone.confidence` |
| | `args` | `(status, body, headers, field_path, endpoint)` |

## Where each is raised
| Situation | Exception |
|---|---|
| Missing/invalid API key, invalid timeout | `TypeSafeError` (constructor) |
| Empty questions / empty score criteria | `TypeSafeError` |
| Non-2xx after retries | `TypeSafeAPIError` subclass by status |
| Cannot connect / timeout after retries | `TypeSafeAPIConnectionError` / `TypeSafeAPITimeoutError` |
| Body fails `response_model` / missing required data | `TypeSafeAPIResponseValidationError` |
| Both `transport` and `http_client` passed | builtin `ValueError` |

## Gotchas
- Catch `TypeSafeAPIError` for HTTP failures, but also `TypeSafeAPIConnectionError` for no-response failures (a different branch of the tree).
- `TypeSafeAPIResponseValidationError` is a *subclass of APIError* although the HTTP status was successful.
- Exceptions and responses are picklable (v0.6.0). Error messages include HTTP details and metadata; v0.7.1 keeps the API key out of logged exceptions.
- Naming: JS SDK classes drop the `TypeSafe` prefix (`APIError`, `RateLimitError`...) — see [[sdk-javascript-api]].

## Related
[[sdk-python]], [[sdk-python-usage]], [[sdk-python-clients]], [[sdk-changelogs]], [[sdk-overview]], [[http-api-reference]]
