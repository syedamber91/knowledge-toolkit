---
title: Python SDK Types
kind: reference
source: Python SDK Common types; Questions; Answers and responses
source_url: https://docs.typesafe.ai/sdk/python/api/types/common, https://docs.typesafe.ai/sdk/python/api/types/questions, https://docs.typesafe.ai/sdk/python/api/types/responses
tags: [api-sdk, primitives]
topics: [topic-agent-integration, topic-calibration]
---
# Python SDK Types
> Reference for question objects (`Noul`, `Choice`, `Score`), their TypedDict twins, answer models (`NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer`), `SystemOneResponse`, `Usage` and `ListModelsResponse`.

## Common types
| Name | Meaning |
|---|---|
| `JSONValue` | JSON-like value; may be nested and contain `None` |
| `JSONContent` | plain `str`, or a mapping/sequence of `JSONValue` entries |

## State
`state` = the text or JSON object you ask questions about. **Cannot be `None`**, but values *inside* an object may be `None`. (Concept: [[state]].)

## Question objects (pydantic models; `additionalProperties: false`)
All three have `type` (literal, defaulted) and `instructions` (`JSONContent | None`, default `None`; "the question to ask, as text, JSON object, or array; optional").
| Class | Fields | Notes |
|---|---|---|
| `Noul` | `type="noul"`, `instructions`, `criteria: NoulCriteria \| None` (default `None`) | yes/no question; optional descriptions of the yes and no outcomes ([[noul]]) |
| `Choice` | `type="choice"`, `instructions`, `criteria: Mapping[str, JSONContent \| None]` (**required**) | label -> description (or `None` for undescribed label) ([[choice]]) |
| `Score` | `type="score"`, `instructions`, `criteria: Sequence[JSONContent]` (**required**) | nonempty, ordered; one description per score **from zero** ([[score]]) |

`NoulCriteria` (TypedDict): keys `true` and `false`, each text/object/array or `None` (None = leave undescribed).

Aliases: `Question` = question object or question dict; `Questions` = inputs keyed by the names identifying their answers.

## Question dictionaries (TypedDicts)
Carry a `type` key `"noul"`, `"choice"`, or `"score"`; same fields as above. Names: `NoulModel`, `ChoiceModel`, `ScoreModel`; union alias `QuestionModel`. Objects and dicts may be mixed in one request.

## Responses
### `SystemOneResponse` (pydantic; config `extra=ignore`, `frozen=True`, `strict=True`)
| Member | Type / meaning |
|---|---|
| `model` | `str` — model used (required) |
| `usage` | `Usage` — token usage (required) |
| `answers` | `dict[str, Answer]` — all answers keyed by question name |
| `nouls` | cached property: yes/no answers by question name |
| `choices` | cached property: choice answers by name |
| `scores` | cached property: score answers by name |
| `request_id` | cached property: value of the `x-typesafe-request-id` response header |
| `raw_http_response` | property: underlying `httpx2.Response` (status, headers, body) |

### `Usage`
`input_tokens: int \| None`, `output_tokens: int \| None` — `None` when the API did not report them. (JS version has non-null numbers; see [[sdk-javascript-api]].)

### Answers (all frozen/strict/extra-ignore)
| Class | Fields | Semantics |
|---|---|---|
| `NoulAnswer` | `type="noul"`, `noul: float` | Probability of yes/true, 0..1. Near 1 = yes, near 0 = no, near 0.5 = uncertainty. **No confidence field** ([[noul]]) |
| `ChoiceAnswer` | `type="choice"`, `choice: str`, `confidence: float`, `probabilities: dict[str, float]` | `choice` = label with highest probability. `confidence` 0..1: higher = greater certainty; use lower values to flag for review. `probabilities` per label, sum approx 1 ([[choice]], [[confidence]]) |
| `ScoreAnswer` | `type="score"`, `score: float`, `confidence: float`, `legend: dict[int, str\|dict\|list]`, `probabilities: dict[int, float]` | `score` = probability-weighted average of rubric levels, may fall **between** integer levels. `legend` = rubric descriptions keyed by integer score; `probabilities` keyed by integer score ([[score]]) |
| `Answer` | alias | an answer identified by its `type` |

### `ListModelsResponse`
Same base as `SystemOneResponse` (`request_id`, `raw_http_response`). Field `models: tuple[ModelMetadata, ...]`.
`ModelMetadata`: `name: str` (model name or alias accepted by a request's `model` field), `description: str`, `release_date: str` (YYYY-MM-DD). See [[models-and-versions]].

## Gotchas
- Frozen models: you cannot mutate answers.
- `strict=True`: wrong types in the response body fail validation ([[sdk-python-retries-and-exceptions]] `TypeSafeAPIResponseValidationError`).
- Unknown answer kinds are skipped with a warning; use `raw_http_response` ([[sdk-python-usage]]).
- Score keys in `legend`/`probabilities` are ints in Python; in JS they are number-or-numeric-string keys.
- Noul has no confidence; "near 0.5" means similar yes/no probability, not medium intensity ([[confidence]]).

## Related
[[sdk-python]], [[sdk-python-clients]], [[sdk-python-usage]], [[primitives-overview]], [[sdk-overview]]
