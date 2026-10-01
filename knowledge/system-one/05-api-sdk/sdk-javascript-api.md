---
title: JavaScript SDK API Reference
kind: reference
source: JavaScript SDK API reference (classes, interfaces, type aliases, variables, functions)
source_url: https://docs.typesafe.ai/sdk/javascript/api
tags: [api-sdk]
topics: [topic-agent-integration, topic-cost-latency]
---
# JavaScript SDK API Reference
> Compact reference of every public symbol in `@typesafe-ai/sdk` v0.6.0: client, config, retry policy, request options, question builders, answer types, error classes, aliases, constants.

Index page lists: 14 classes, 18 interfaces, 12 type aliases, 3 variables, 3 functions.

## TypeSafeClient (class)
`new TypeSafeClient(config?: TypeSafeClientConfig = {})`. Explicit options beat env vars, then SDK defaults; empty/whitespace env values ignored. **Throws** if API key missing, config invalid, or runtime unsupported.
| Property (readonly) | Meaning |
|---|---|
| `baseURL` | API root, trailing slashes removed |
| `defaultHeaders` | extra headers sent with each request |
| `defaultModel` | model used when a request omits `model` |
| `fetch` | HTTP fetch impl |
| `logger` | configured logger filtered to `logLevel` |
| `logLevel` | log verbosity |
| `models` | `Models` resource |
| `retry` | `RetryPolicy` with constructor overrides applied |
| `timeout` | per-attempt timeout ms |

`systemOne<Q extends Questions>(request: SystemOneRequest<Q>, options?: RequestOptions = {}): APIPromise<SystemOneResult<Q>>` — answers named questions about text or structured state. Throws: questions empty, **or score criteria not a list of at least two entries**; non-2xx after retries; connect/timeout after retries; caller abort. Example: `const { answers } = await client.systemOne({ state: "I was charged twice. Please help.", questions: { billing: noul("Is this about billing?") } }); answers.billing.noul`.

## TypeSafeClientConfig (interface; all optional)
| Field | Default / fallback |
|---|---|
| `apiKey` | required; falls back to `TYPESAFE_API_KEY` |
| `baseURL` | `TYPESAFE_BASE_URL`, then `https://api.typesafe.ai` |
| `dangerouslyAllowBrowser` | `false` — allow browser use, exposing key to page users |
| `defaultHeaders` | none; per-call headers take precedence |
| `defaultModel` | `TYPESAFE_DEFAULT_MODEL`, then `jev-latest` |
| `fetch` | global `fetch` (custom for transport config/tests) |
| `logger` | prefixed `console` |
| `logLevel` | `TYPESAFE_LOG_LEVEL`, then `warn`. `info` logs request summaries; `debug` adds headers and bodies. Known credential headers redacted; bodies are not |
| `retry` | `Partial<RetryPolicy>`; omitted fields use defaults |
| `timeout` | per attempt ms, no total retry budget; **10000** |

## RetryPolicy (interface; partial overrides inherit)
| Field | Default |
|---|---|
| `maxRetries` | **2** (retries after initial attempt; 0 disables) |
| `backoffInitialMs` | **500** (doubled up to max) |
| `backoffMaxMs` | **5000** |
| `backoffJitter` | **0.25** (fraction randomly subtracted, 0..1) |
| `httpStatuses` | `ReadonlySet<number>`: **408, 429, 500–599** |
| `respectRetryAfter` | **true** (honor `Retry-After` and `retry-after-ms` up to `maxRetryAfterMs`) |
| `maxRetryAfterMs` | **60000** (longer server delays fall back to backoff) |
| `apiConnectionError` | **true** (retry `APIConnectionError` incl. interrupted response bodies) |
| `apiTimeoutError` | **true** |
Compare with Python's `RetryPolicy` (different field set, `timeout` total budget): [[sdk-python-retries-and-exceptions]].

## RequestOptions (per call)
`headers?: Record<string,string>` (merged over `defaultHeaders`), `retry?: Partial<RetryPolicy>` (omitted fields inherit), `signal?: AbortSignal` (cancels request **and pending retries**), `timeout?: number` (per attempt ms; **no total retry budget**).

## Request / result interfaces
| Interface | Fields |
|---|---|
| `SystemOneRequest<Q>` | `state: EntryType` (text, JSON object/array, or `null`), `questions: Q` (nonempty), `model?: string` (omitted inherits `defaultModel`). Additional properties on a request variable are **forwarded, including `null` values** |
| `SystemOneRequestPayload` | extends request; body for **`POST /v1/systemone`** with `model` resolved (required) |
| `SystemOneResult<Q>` | `answers: { [K]: ResultFor<Q[K]> }` (types inferred), `model: string`, `usage: Usage` |
| `Usage` | `input_tokens: number`, `output_tokens: number` (non-null, unlike Python) |
| `Models` | `list(options?: RequestOptions): APIPromise<ModelCard[]>` |
| `ModelCard` | `name`, `description`, `release_date` (strings) |
| `Questions` | index signature `[name: string]: Question` |
| `WithResponse<T>` | `data: T`, `requestId: string \| undefined`, `response: Response` (body consumed) |
| `Logger` | `debug/info/warn/error(message: string, ...args: unknown[]): void`; compatible with `console` |

## Question builders and question/answer shapes
| Function | Signature | Notes |
|---|---|---|
| `noul` | `noul(instructions?: EntryType = null, criteria?: {false?: EntryType; true?: EntryType} \| null): NoulQuestion` | `true` = yes outcome description, `false` = no |
| `choice` | `choice<T extends ChoiceCriteria>(instructions: EntryType, criteria: T): ChoiceQuestion<T>` | labels -> descriptions or `null` |
| `score` | `score<T extends ScoreCriteria>(instructions: EntryType, criteria: T): ScoreQuestion<T>` | **at least two** descriptions indexed from zero; entries may be `null` |

| Interface | Fields |
|---|---|
| `NoulQuestion` | `type: "noul"`, `instructions?`, `criteria?` (as above or `null`) |
| `ChoiceQuestion<T>` | `type: "choice"`, `instructions?`, `criteria: T` |
| `ScoreQuestion<T>` | `type: "score"`, `instructions?`, `criteria: T` |
| `NoulResponse` | `type: "noul"`, `noul: number` (probability of yes, 0..1) |
| `ChoiceResponse<T>` | `type: "choice"`, `choice: keyof T & string`, `confidence: number`, `probabilities` keyed by label |
| `ScoreResponse<T>` | `type: "score"`, `score: number` (expected, may fall between integer levels), `confidence: number`, `legend: ScoreLegend<T>`, `probabilities` keyed by score (number or numeric string) |

## Type aliases
| Alias | Definition |
|---|---|
| `EntryType` | `string \| {[key:string]: JsonValue} \| JsonValue[] \| null` (state, instructions, criteria) |
| `Description` | = `EntryType`; `null` leaves a label undescribed |
| `JsonValue` | string, number, boolean, null, array, object |
| `ChoiceCriteria` | `{[label: string]: EntryType}` |
| `ScoreCriteria` | `readonly [EntryType, EntryType, ...EntryType[]]` (at least two) |
| `ScoreLegend<T>` | `{ readonly [score in ScoreOf<T>]: T[score] }` |
| `ScoreOf<T>` | `number` if tuple length unknown, else its indices (`Extract<keyof T, \`${number}\`>`) |
| `Question` | `NoulQuestion \| ScoreQuestion \| ChoiceQuestion` (by `type`) |
| `ResultFor<T>` | NoulQuestion -> `NoulResponse`; ScoreQuestion<S> -> `ScoreResponse<S>`; ChoiceQuestion<E> -> `ChoiceResponse<E>` |
| `LogLevel` | `"debug" \| "info" \| "warn" \| "error" \| "off"` |
| `Fetch` | `(input: string, init?: RequestInit) => Promise<Response>` |
| `EnvVar` | `typeof ENV[keyof typeof ENV]` |

## Variables
| Name | Value |
|---|---|
| `ENV` | `{apiKey: "TYPESAFE_API_KEY", baseURL: "TYPESAFE_BASE_URL" (default `https://api.typesafe.ai`), defaultModel: "TYPESAFE_DEFAULT_MODEL" (default `jev-latest`), logLevel: "TYPESAFE_LOG_LEVEL" (default `warn`)}` |
| `LOG_LEVELS` | `readonly LogLevel[]`, most to least verbose |
| `VERSION` | `"0.6.0"` |

## APIPromise<T> (class extends Promise<T>)
"A promise for the parsed result with access to the HTTP response." Non-2xx rejects with `APIError` (also via `asResponse()`).
| Method | Behaviour |
|---|---|
| `asResponse()` | resolves raw `Response` without parsing body. SDK buffers full body under request timeout before handoff; reading afterwards is caller-owned. **Don't also await the parsed result on the same promise** |
| `withResponse()` | `Promise<WithResponse<T>>`: parsed result + HTTP response + request ID |
| `map(fn)` | transform parsed result; shares HTTP response and a single body parse |
| `then / catch / finally` | standard Promise |
Constructor: `new APIPromise(responsePromise, parseResponse)`.

## Error classes
```
Error
 └ TypeSafeError (base)
    ├ APIConnectionError  ("Connection error."; DNS, TLS, closed connection, response-body delivery failures)
    │   └ APITimeoutError (timeoutMs: number) — full response not within timeout
    ├ APIUserAbortError ("Request was aborted."; caller cancelled via AbortSignal)
    └ APIError (status, body, headers, requestId; static fromResponse(status, body, headers))
        ├ BadRequestError 400   ├ AuthenticationError 401   ├ PermissionDeniedError 403
        ├ NotFoundError 404     ├ UnprocessableEntityError 422 (validation)
        ├ RateLimitError 429 (retryAfterMs: number | undefined — absent or invalid -> undefined)
        └ InternalServerError 5xx
```
`APIError` props (readonly): `status: number`; `body: unknown` (parsed JSON, response text, or `undefined` for empty); `headers: Headers`; `requestId: string \| undefined` from `x-typesafe-request-id`. Constructors `(status, body, headers, message?)`. `APIConnectionError(message?, options?: ErrorOptions)`. `APIUserAbortError` is **not** an `APIError` and not a connection error.

## Python vs JS mapping
| Python | JS |
|---|---|
| `TypeSafeAPIError` | `APIError` |
| `TypeSafeAPIConnectionError` / `TypeSafeAPITimeoutError` | `APIConnectionError` / `APITimeoutError` |
| `TypeSafeRateLimitError.retry_after_ms` | `RateLimitError.retryAfterMs` |
| `TypeSafeAPIResponseValidationError` | none listed in JS reference |
| (no abort class listed) | `APIUserAbortError` |

## Gotchas
- Score needs >= 2 criteria in JS (type-level tuple and runtime throw); Python only requires nonempty.
- JS `timeout` is per attempt; there is **no total budget** (Python has `RetryPolicy.timeout`).
- Browser use needs `dangerouslyAllowBrowser`; avoid.
- Don't both `asResponse()` and await parsed result.
- SDK version constant 0.6.0 corresponds to the docs; check `VERSION` vs your install.

## Related
[[sdk-javascript]], [[sdk-overview]], [[sdk-python-types]], [[sdk-python-retries-and-exceptions]], [[sdk-changelogs]], [[http-api-reference]]
