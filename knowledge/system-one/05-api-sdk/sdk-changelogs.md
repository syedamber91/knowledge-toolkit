---
title: SDK Changelogs
kind: reference
source: Python SDK Changelog; JavaScript SDK Changelog
source_url: https://docs.typesafe.ai/sdk/python/changelog, https://docs.typesafe.ai/sdk/javascript/changelog
tags: [api-sdk]
topics: [topic-agent-integration]
---
# SDK Changelogs
> Release history of the TypeSafe Python and JavaScript SDKs (Sept 2026), with breaking changes flagged.

## Python SDK (`typesafe-sdk`)
| Version | Date | Type | Change |
|---|---|---|---|
| **v0.7.2** | 2026-09-26 | Misc | add `http2` extra to the `typesafe-sdk` package |
| | | Docs | document usage with HTTP/2 support |
| **v0.7.1** | 2026-09-21 | Bug fix | validate the API key early; exclude the key value from logged exceptions |
| | | Docs | add examples for usage with AI gateways |
| **v0.7.0** | 2026-09-18 | **Breaking** | ser/de library changed from `msgspec` to `pydantic` |
| | | Bug fix | `str` subclasses now serialize as strings (not lists of characters) |
| | | Feature | `system_one` accepts a new `response_model` argument (a desired pydantic model) for extra type-safety |
| **v0.6.0** | 2026-09-15 | **Breaking** | `Score.criteria` accepted as an **ordered sequence** instead of a dict keyed by integers |
| | | Feature | input annotations accept abstract types like `Mapping` and `Sequence` |
| | | Feature | error messages include HTTP details and metadata |
| | | Bug fix | handle invalid values in `RetryPolicy` |
| | | Bug fix | exceptions and responses are picklable |
| | | Docs | link more concepts from the main docs |
| **v0.5.7** | 2026-09-14 | Initial | first public release of the Python SDK |

## JavaScript SDK (`@typesafe-ai/sdk`)
| Version | Date | Change |
|---|---|---|
| **v0.6.0** | 2026-09-15 | **Breaking**: `Score.criteria` accepted as an ordered sequence instead of a dictionary keyed by integers |
| **v0.5.7** | 2026-09-11 | Initial public release of the JS/TS SDK |

## What to take from this
- Both SDKs are **very young** (initial public releases 2026-09-11 JS / 2026-09-14 Python) and pre-1.0: breaking changes already shipped within a week (v0.6.0). Pin versions.
- Both share the same v0.6.0 Score-criteria breaking change; code written for an older dict-keyed form must change to a list/tuple ([[score]]).
- Python v0.7.0 (pydantic) changes ser/de: custom response models are pydantic ([[sdk-python-usage]], [[sdk-python-types]]).
- Security-relevant: v0.7.1 keeps API key values out of logged exceptions ([[sdk-python-retries-and-exceptions]]).
- HTTP/2 only arrives in Python v0.7.2 via the `http2` extra.

## Gotchas
- Date oddity: JS v0.5.7 is dated 2026-09-11 and Python v0.5.7 2026-09-14 — same version number, different dates (as printed in the two changelogs).
- The JS docs pin SDK source links to tag v0.6.0; no JS release after v0.6.0 is listed.

## Related
[[sdk-overview]], [[sdk-python]], [[sdk-javascript]], [[sdk-javascript-api]], [[models-and-versions]]
