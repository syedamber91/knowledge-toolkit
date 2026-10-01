---
title: JavaScript SDK
kind: reference
source: JavaScript SDK
source_url: https://docs.typesafe.ai/sdk/javascript
tags: [api-sdk]
topics: [topic-agent-integration]
---
# JavaScript SDK
> Install `@typesafe-ai/sdk` (Node 20+), set `TYPESAFE_API_KEY`, call `client.systemOne({state, questions})` with `choice()/noul()/score()`; answer types are inferred from the questions.

## What it is / How it works
- JavaScript and TypeScript SDK for TypeSafe AI. Package: **`@typesafe-ai/sdk`**. Requires **Node.js 20 or newer**. Ships **ESM, CommonJS, and TypeScript declarations**.
- Install: `npm install @typesafe-ai/sdk`.
- Set `TYPESAFE_API_KEY` in the environment, then `new TypeSafeClient()`.
- Answer types are **inferred from your questions** (see `ResultFor` in [[sdk-javascript-api]]).

## Quickstart (verbatim shape)
```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const response = await client.systemOne({
  state: { document: "I was charged twice. Please fix this ASAP." },
  questions: {
    category: choice("What is this ticket about?", {
      billing: null, technical: null, other: null,
    }),
  },
});
console.log(response.answers.category.choice);
```
- `choice(instructions, criteria)`: criteria is label -> description; `null` leaves a label undescribed ([[choice]]).
- `noul(instructions?, criteria?)` and `score(instructions, criteria)` are the other builders ([[noul]], [[score]]).
- Note the shape difference from Python: answers are at `response.answers[name]` (no `nouls/choices/scores` accessors) ([[sdk-python-types]]).

## Documentation pointers
- Docs say: learn what TypeSafe can do at docs.typesafe.ai; for API options and defaults read the SDK's `client.ts` and `types.ts` (docs link pinned at tag **v0.6.0**: github.com/typesafe-ai/typesafe-sdk-js/blob/v0.6.0/src/client.ts and .../src/types.ts).
- API reference (classes, interfaces, aliases): [[sdk-javascript-api]].
- Changelog: [[sdk-changelogs]] (latest v0.6.0, 2026-09-15; initial public release v0.5.7, 2026-09-11).

## When to use / when NOT to use
- Use in Node/TS backends. Keep the API key **server-side**: browser use is blocked unless `dangerouslyAllowBrowser: true`, which exposes the key to page users ([[sdk-javascript-api]]).
- Python: [[sdk-python]]; raw HTTP: [[http-api-reference]].

## Numbers & limits
| Item | Value |
|---|---|
| Node.js | >= 20 |
| Latest version in docs | 0.6.0 (`VERSION` constant) |
| Default timeout | 10000 ms per attempt |
| Default retries | 2 |

## Gotchas
- JS `score()` needs **at least two** criteria entries (a tuple type); criteria is an ordered array since v0.6.0 (previously an integer-keyed dict).
- The quickstart wraps state in `{document: ...}`; state can also be plain text, JSON object/array, or `null` (`EntryType`) — contrast Python where `state` cannot be `None`.
- The jev-mcp README links a known SDK cancellation crash (typesafe-sdk-js issue #2) and notes jev-mcp's direct fetch path avoids it — see [[jev-mcp-server]]. The SDK docs themselves do not mention it `[inference: relevant if you use AbortSignal heavily]`.

## Related
[[sdk-overview]], [[sdk-javascript-api]], [[sdk-changelogs]], [[quickstart]], [[primitives-overview]], [[state]]
