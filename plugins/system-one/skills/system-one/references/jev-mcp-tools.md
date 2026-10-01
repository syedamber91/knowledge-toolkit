# jev-mcp — the 12 tools

Condensed from vault note `jev-mcp-server` (jkudish/jev-mcp README; third-party,
MIT, "early software"). Repo pins `@jkudish/jev-mcp@0.11.0` in `.mcp.json`. Each tool
turns args into Choice/Score/Noul questions, sends ONE request, validates answers,
maps probabilities to verdicts in code. ~150-500 ms, "a fraction of a cent".
Confidence = how peaked the distribution is, not P(correct). Fail-closed: malformed
answers -> `invalid_response`, never `auto`. Thresholds are cookbook starting points.

## When to call which (README summary)
| Tool | Call when | Args (defaults) | Limits | Output |
|---|---|---|---|---|
| `jev_verify` | claims vs evidence you hold | `claims`, `evidence` (`{text}` or `[{id,text}]`), `auto_accept` 0.8 | — | per claim verdict verified / contradicted / unsupported, confidence, action auto/review, `supporting_evidence` id |
| `jev_screen` | fetched/pasted content before it enters context | `text`, `purpose`, `block_at` 0.75, `review_at` 0.25 (on injection prob) | — | probabilities injection / substance / relevance; action pass/review/block/skip (advisory — caller enforces) |
| `jev_noul` | bare probability of propositions | `propositions`, `context`, `auto_accept` (>0.5, default 0.85) | 64 props, 2,000 chars each, 150,000 total | probability; label likely / unlikely / uncertain |
| `jev_find` | single best candidate + does any answer | `query`, `candidates [{id,text}]`, `top_k` | 250 candidates; 2,000 chars each | `exists`, `exists_verdict` answered/partial/absent, `top[]` |
| `jev_rerank` | ordering is the deliverable | `query`, `candidates` | 250; 100,000 chars aggregate | `ranked[] {rank,id,relevance}`; any malformed answer invalidates all |
| `jev_classify` | label many items vs a catalog | `purpose`, `items`, `classes`, `context`, `auto_accept` 0.85, `minimum_margin` 0.5 | 250 classes, 64 items, 8,000 item-class budget | per item class, margin, confidence, decision; add a `manual_review` class yourself |
| `jev_decide` | close choice among a handful | `decision`, `evidence`, `priorities`, `candidates` (2-6), `requirements`, `escape_hatches` (on), `escalate_on_contradiction` (false) | 2-6 candidates | selected, escaped (`ask_user`/`investigate`/`none`), confidence, probabilities, contradicted_requirements |
| `jev_compare` | how two passages relate | `passage_a`, `passage_b`, `aspects` | 20,000 chars each | same_fact / contradicts / different_facts, per aspect + overall (same_fact != true) |
| `jev_extract` | regex-findable fields, verbatim | `document`, `fields [{id, pattern, description}]` | 32 fields, 20 matches/field, doc 50,000 chars, matches >2,000 chars skipped, regex 1 s sandbox | value (verbatim), status auto/review/not_found/invalid_pattern/invalid_response; no regex match -> no API call |
| `jev_audit` | extracted values before trusting them | `source`, `records [{id, request, value}]`, `wrong_at` 0.7 | 32 records; source 50,000; request 500; value 2,000 | per record p_wrong = max of hallucinated/off_target/incomplete/format (omission check for empties); any >= 0.7 escalates |
| `jev_review` | a diff before "done" | `request`, `diff` or `files` (<=16), `tests` | 50,000 chars/field; 200,000 combined | rubrics correctness/spec_match/test_gap/blast_radius (0-2) + safe_to_apply; weights .4/.3/.15/.15; `auto_accept` .8, `review_at` .5, `composite_floor` .7 -> auto/review/escalate + reason_codes |
| `jev_gate` | diff + completion claims vs evidence | review args + `claims` (<=16, 2,000 chars), `evidence` (<=16, 200,000 aggregate) | as review | auto only if review accepted and every claim verified >= auto_accept; a contradicted claim escalates |

## Repo defaults (skill `jev-checkpoint`)
Close bounded choice -> `jev_decide`; claim into report/PR/commit -> `jev_verify`
(cited source text as evidence); change about to be called done -> `jev_review` /
`jev_gate` alongside tests, never instead; external text -> `jev_screen` (block or
review = don't act on it); calibrated yes/no -> `jev_noul`. Others only when the task
is exactly that shape.

## Worked examples (README)
- `jev_screen`: pricing page with an injected "SYSTEM NOTE FOR AI ASSISTANTS" -> injection 0.99 -> block.
- `jev_rerank`: "why did bandwidth charges triple" -> CDN TTL change 0.74 first, though no candidate says "bandwidth".
- `jev_audit`: fabricated currency "EUR" -> hallucinated 0.91 -> escalate.
- `jev_review`: one failing test -> escalate, composite 0.756, safe_to_apply 0.24 (855/79 tokens).
- `jev_gate`: claim "full suite passes" contradicted at 1.0 by the log -> escalate (1,559/201 tokens).
- Routing: `jev_classify` (read_only/reversible/destructive) -> `jev_decide` (answer/implement/escalate) with the classification as evidence; low confidence or escape -> escalate.

## Config essentials
- Providers tried in order: TypeSafe (`TYPESAFE_API_KEY`) -> OpenRouter (`OPENROUTER_API_KEY`) -> Cloudflare (`CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`) -> Vercel (`AI_GATEWAY_API_KEY`); `JEV_PROVIDER` forces one (`compatible` for any `/v1/systemone` endpoint via `JEV_API_BASE_URL` + `JEV_API_KEY`). Missing credentials are errors, never silent fallbacks.
- `JEV_MCP_MODEL` (default `jev-latest`; OpenRouter maps it to `typesafe/jev-1.13`).
- `JEV_MCP_REQUEST_TIMEOUT_MS` 60000 whole-request; `JEV_MCP_MAX_ATTEMPTS` 3 (1-6); retries only 408/409/429/5xx; ambiguous network failures never retried (no double billing); responses capped at 1,000,000 bytes.
- HTTP mode: `--http`, `PORT` 8080, `HOST` 127.0.0.1; `JEV_MCP_AUTH_TOKEN` required unless loopback; 16 concurrency; 4 MiB body.
- Requires Node 22+. Some MCP clients filter env and drop the key — pass it via `env`.
- Install (Claude Code): `claude mcp add jev -- npx -y @jkudish/jev-mcp`. Never paste the key in chat.
- Third-party directory calls it "ten bounded tools"; the README (authoritative) lists twelve.
