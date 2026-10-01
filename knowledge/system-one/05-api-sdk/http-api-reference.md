---
title: HTTP API Reference
kind: reference
source: API reference
source_url: https://docs.typesafe.ai/api
tags: [api-sdk, primitives]
topics: [topic-agent-integration, topic-cost-latency]
---
# HTTP API Reference
> One endpoint: POST a `state` plus a map of typed `questions`; get one typed answer per question plus token usage.

## Endpoint
```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
```
Guided intro: [[primitives-overview]]. SDK method of the same name: `system_one` ([[sdk-overview]]).

## Request body
| Field | Type | Meaning |
| - | - | - |
| `state` | string / object / array | Content to evaluate: plain text, or structured data (chat logs, records, app state). See [[state]] |
| `model` | string | Model that handles the request. Use `"jev-latest"`, the flagship; aliases in [[models-and-versions]] |
| `questions` | map<string, Question> | You choose each key; answers return under the same key. **Key is not sent to the underlying model and not used in inference.** |

Minimal request: `{"state": "Help! My payouts have been failing for 3 days.", "model": "jev-latest", "questions": {"is_urgent": {"type": "noul", "instructions": "Does this convey urgency?"}}}`

## Question types
All three share `type` and `instructions`; each adds `criteria`. `instructions` may be string, object or array: break a long question with context/data into a structured object with the question in one field and data in others; refer to data fields by name in backticks (same as pointing at nested `state` values). Example: `{"potential_duplicate": {"name":"John Smith","location":"Oakland, California","last_employer":"Google"}, "question":"Is the resume for the same person as \`potential_duplicate\`?"}`. See [[advanced-structure]].

| Type | `type` | `instructions` | `criteria` | Limits |
| - | - | - | - | - |
| [[noul]] | `"noul"` | yes/no question | optional object `{true, false}`, each string/object/array: what yes (near 1) / no (near 0) mean | -- |
| [[choice]] | `"choice"` | what the model decides | map option -> rubric description (string/object/array/**null** when no extra detail needed) | **max 255 options** |
| [[score]] | `"score"` | what to rate | ordered array of level descriptions (string/object/array) | **at least 2 levels, API accepts up to 10** |

Examples from the page (state "Help! My payouts have been failing for 3 days."):
- Noul `is_urgent`: instructions "Does this convey urgency?", criteria true "Explicitly time-sensitive", false "No urgency expressed".
- Choice `department`: "Which team should handle this?" options billing "Payments, invoicing, refunds" / technical "Bugs, outages, integrations" / sales "Pricing, upgrades, new accounts".
- Score `frustration`: "How frustrated is the customer?" criteria `["Calm","Frustrated","Very angry"]`.

## Response body
| Field | Type | Meaning |
| - | - | - |
| `model` | string | Model that performed the evaluation (e.g. `jev-1.13.0` when you asked `jev-latest`) |
| `answers` | map<string, Answer> | One Answer per question, same ids |
| `usage` | object | `input_tokens` (int), `output_tokens` (int) |

Example: `{"model":"jev-1.13.0","answers":{"is_urgent":{"type":"noul","noul":0.95}},"usage":{"input_tokens":296,"output_tokens":20}}`

## Answer types
Every answer has `type` matching its question. Choice and Score also carry `confidence` (0-1, derived from the distribution; [[confidence]]).
| Answer | Fields |
| - | - |
| Noul | `type:"noul"`, `noul` number 0 (no) to 1 (yes) |
| Choice | `type:"choice"`, `choice` (highest-probability option), `probabilities` map option->float (sums to 1), `confidence` |
| Score | `type:"score"`, `score` (probability-weighted value across levels, can land between), `legend` map level-number->description, `probabilities` map level (string key, matches legend)->float (sums to 1), `confidence` |

Examples: Choice `department` -> `{"choice":"billing","probabilities":{"billing":0.88,"technical":0.12,"sales":0.0},"confidence":0.81}` (usage 318/34). Score `frustration` -> `{"score":1.05,"legend":{"0":"Calm","1":"Frustrated","2":"Very angry"},"probabilities":{"0":0.0,"1":0.95,"2":0.05},"confidence":0.92}` (usage 304/18). Noul `is_urgent` 0.95 (usage 307/20).

## Errors
Standard HTTP status codes with a JSON body describing what went wrong.
| Status | Meaning |
| - | - |
| 401 Unauthorized | Missing or invalid API key; check the `Authorization` header |
| 422 Unprocessable Entity | Body failed validation (e.g. missing required field, malformed question); body details the offending field |
| 429 Too Many Requests | Rate limit exceeded; back off and retry after a short delay |
| 529 Overloaded | TypeSafe temporarily overloaded; retry after a short delay |

### Handling rate limits
On 429 or 529 retry with **exponential backoff**, not immediately. The client SDKs do this automatically under the default retry policy ([[sdk-python-retries-and-exceptions]], [[sdk-javascript]]). Other SDK exception classes (e.g. bad request, not found, permission denied, internal server) appear in the SDK docs, not on this page.

## Numbers & limits
| Item | Value |
| - | - |
| Max Choice options | 255 |
| Score levels | 2+ (up to 10) |
| Noul range | 0..1 |
| Retryable statuses | 429, 529 |
| Auth | Bearer API key |
| Latency/pricing | not stated on this page (see [[models-and-versions]], [[benchmarks-and-comparisons]]) |

## Gotchas
- Question key never reaches the model: put the full question in `instructions`.
- Score `probabilities`/`legend` keys are strings in the HTTP API (SDK Python converts to ints, see [[score]]).
- Use `"jev-latest"` alias for the flagship; the response `model` shows the pinned version actually used.
- Choice option descriptions may be `null`.
- The page has no pagination/batch, rate-limit numbers, or max request size; do not assume any `[inference]`.

## Related
[[primitives-overview]] -- [[choice]] -- [[score]] -- [[noul]] -- [[advanced-structure]] -- [[confidence]] -- [[state]] -- [[sdk-overview]] -- [[quickstart]] -- [[typesafe-agent-skill]] -- [[topic-agent-integration]]
