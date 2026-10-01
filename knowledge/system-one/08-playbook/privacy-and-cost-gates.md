---
title: Privacy And Cost Gates
kind: playbook
source: Synthesis of vault notes + repo jev-checkpoint skill and docs/JEV-MCP-SETUP.md (Opus synthesis pass, 2026-10-02)
source_url: vault-internal
tags: [guardrails, cost-latency, agent-tooling]
topics: [topic-guardrails, topic-cost-latency, topic-agent-integration, topic-model-selection]
---
# Privacy and Cost Gates
> What may go to a hosted System One API (Jev, directly or via a gateway) vs what must stay local; owner rules; cost and latency budgets with sourced numbers; kill-switch conditions.

## 1. Where the data goes
| Route | Who sees the state | Facts | Source |
|---|---|---|---|
| TypeSafe direct (`api.typesafe.ai`) | TypeSafe | not trained on customer requests/responses; DPA + Privacy Policy; **ZDR only for enterprise** (sales@typesafe.ai) | [[jev-introduction]], [[models-and-versions]] |
| OpenRouter | OpenRouter + TypeSafe | Decisions API is alpha, adds a hop; `usage.cost` per response | [[openrouter-jev-guide]], [[jev-mcp-server]] |
| Vercel AI Gateway | Vercel + TypeSafe | calls appear in Vercel logs and budgets | [[jev-mcp-server]] |
| Cloudflare Workers AI | Cloudflare + TypeSafe | model `typesafe/jev`, no pinned versions | [[jev-mcp-server]] |
| jev-mcp (stdio) | as its provider | every tool call sends your arguments (claims, diffs, pages) to the provider | [[jev-mcp-server]] |
| Laya / Kev / other self-hosted | nobody outside your network | "stays on your network; air-gap/HIPAA/GDPR friendly" (third-party claim) | [[jev-vs-laya]], [[laya]] |
| Deterministic code, local MiniLM | local | — | [[minilm-embeddings]] |
Third-party tools in the ecosystem routinely send full content (files, diffs, lyrics, every SQL row) and some store keys in plaintext ([[awesome-typesafe-jev]]).

## 2. Send / don't-send rules
**Never send to a hosted tool (owner rules, repo `jev-checkpoint`):**
- `.env`, API keys, tokens, credentials, session cookies.
- Anything the repo's CLAUDE.md marks licensed, private, or do-not-quote (e.g. licensed data such as the FMP data a third-party study withheld, [[awesome-typesafe-jev]] — analogous case).
- Personal data you are not entitled to share [inference].
**Must stay local (use Laya/Kev/code instead):** data that cannot leave the network ("the choice ... comes down to this one point", vanekt via [[jev-vs-laya]]).
**OK to send:** public or owned text needed for the judgment, filtered to the minimum fields ([[jev-1-13-jaggedness]] #5 — also the privacy-minimal choice [inference]).
**Before trusting fetched content** (web page, PDF, gem/LLM reply): `jev_screen` it; `block`/`review` means do not act on it; screening is advisory, you enforce ([[jev-mcp-server]]). Even passages under the injection threshold are untrusted text ([[cb-classifying-rag-passages]]).
**Logs:** SDK `debug` logs request/response bodies unredacted — keep it off in production ([[sdk-python-usage]]). Keys: env/settings only, never chat, never browser ([[sdk-javascript]], [[agent-operating-protocol]]).
**Repo gate rule:** Jev is advisory only; never a substitute for G2 cited-quote verification or `verify_briefs.py` (repo CLAUDE.md, `jev-checkpoint`).

## 3. Cost model
- Jev: **$0.042 per million input tokens; output free** ([[models-and-versions]]). State dominates cost; extra questions cost only their tokens ([[primitives-overview]]). Cookbook price tables call it a historical rate; treat ratios as indicative ([[cb-consistency-choices]]).
- Batch: one request per state, not per question (13 questions: 12.2x cheaper; per Primitives page 11.5x) ([[cb-parallel-questions]], [[primitives-overview]]).
- Cost scales with *states* (pairs, rows, passages): reranking = one request per candidate; RAG filter = one per passage; feature discovery = one per row per round, a revision = another full pass ([[cb-reranking]], [[cb-classifying-rag-passages]], [[cb-autoresearch-feature-discovery]]).

### Sourced cost/latency anchors
| Workload | Cost | Latency | Source |
|---|---|---|---|
| 8-Choice rubric, one call | $0.000046 | 114 ms | [[cb-consistency-choices]] |
| 14-Noul rubric, one call | $0.000043 | 111 ms | [[cb-consistency-nouls]] |
| 13 questions over 53,777-char article | $0.000497 (vs $0.006090 for 13 calls) | 0.27 s (vs 2.71 s sequential) | [[cb-parallel-questions]] |
| 1,200 rerank calls (1,536,002 input tokens) | $0.0645 total | — | [[cb-reranking]] |
| Structure recovery, 2 requests, 10,211 tokens | $0.0003 / $0.0015 (source conflict; ~$0.00043 computed) | 0.8 s | [[cb-structure-recovery]] |
| Skill suggestion wide + rerank | — | 0.16-0.31 s + 0.09-0.12 s | [[cb-skill-suggestion]] |
| jev-mcp tool call | "fraction of a cent" | 150-500 ms | [[jev-mcp-server]] |
| `jev_review` / `jev_gate` example | 855/79 and 1,559/201 tokens | — | [[jev-mcp-server]] |
| Haiku 4.5 same rubrics | $0.0015-0.0035 | 0.99-3.9 s | cookbooks above |
| Opus 4.8 reasoning same rubrics | $0.028-0.034 | 10.4-13.9 s | cookbooks above |
| gpt-5.5 reasoning extraction | ~$0.10 per extraction at ~0.81 quality | — | [[cb-sde-cascade]] |
| TypeSafe 4-workflow eval | Jev ~1/200 cost, 1/50 latency of frontier; Sonnet 5 293x cost, 195x latency | — | [[community-guide-devto]] (self-run) |
| Laya local | $0 licence; compute only | 23-43 ms | [[laya]] |
Budget rules of thumb [inference from the table]: a Jev judgment is ~10^-5 to 10^-4 USD and ~0.1-0.5 s; an Opus reasoning call is ~600-800x the cost and ~100x the latency. Gate expensive calls behind cheap ones (cascade), never the reverse.

## 4. Rate limits and transport budgets
| Item | Value | Source |
|---|---|---|
| Jev rate limits | 100K tokens/s, 40 req/s (first-party; "can change without notice") | [[models-and-versions]] |
| Conflicting third-party figure | 250K tokens/s, 1,200 req/min | [[community-guide-devto]] |
| Retryable | 429, 529 (backoff) | [[http-api-reference]] |
| JS SDK defaults | 2 retries, 500 ms -> 5,000 ms backoff, 10 s per attempt, no total budget | [[sdk-javascript-api]] |
| Python SDK | 10.0 s per HTTP op; `RetryPolicy.timeout` = total budget; defaults not printed | [[sdk-python-retries-and-exceptions]] |
| jev-mcp | 60 s whole-request deadline, 3 attempts (1-6), 16 concurrency, 4 MiB body, 1,000,000-byte response cap; ambiguous network failures never retried | [[jev-mcp-server]] |
| Practical concurrency | 8 workers already hits a shared-key limit; public endpoint rate-limits above ~8 | [[cb-autoresearch-feature-discovery]], [[cb-entity-alignment]] |

## 5. Kill-switch conditions (stop calling the hosted model)
| Condition | Action | Basis |
|---|---|---|
| `mcp__jev__*` absent / key missing / network blocked | one-line notice; fall back (local/code/LLM) | [[agent-operating-protocol]] |
| Payload would contain secrets or restricted content | don't send; use local or skip | §2 |
| Repeated 429/529 or transport errors after SDK retries | stop; report; no manual retry loop | [[http-api-reference]], repo `jev-checkpoint` rule 4 |
| `invalid_response` or truncated input | never auto; review/escalate | [[jev-mcp-server]] |
| `response.model` differs from the pinned version thresholds were tuned on | stop auto-actions until re-validated | [[models-and-versions]] |
| Task matches a jaggedness category | don't call; use code/LLM | [[jev-1-13-jaggedness]] |
| Input non-English and unvalidated | treat as low confidence; validate first | [[models-and-versions]] |
| Spend exceeds a per-task budget the operator set | stop and report [inference: no budget mechanism in jev-mcp; pg-jev/HA-Jev-style caps exist in third-party tools, [[awesome-typesafe-jev]]] | — |

## Related
[[agent-operating-protocol]] · [[when-to-use-which-model]] · [[anti-patterns]] · [[cheat-sheet]] · [[jev-mcp-server]] · [[topic-guardrails]] · [[topic-cost-latency]]
