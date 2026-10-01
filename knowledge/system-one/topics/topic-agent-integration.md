---
title: Agent integration
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Agent integration
> MCP server, agent skill, SDKs, OpenRouter, cloud/local setup.

## Notes on this topic (26)
- [[jev-introduction]] — Jev = TypeSafe's flagship model and the first System One model: send a state plus typed questions, get typed answers (+ probabilities, + confidence for Choice/Score) your code can branch on. Read this first to know what Jev is and the three question types.
- [[jev-with-coding-agents]] — Jev is NOT a drop-in LLM for Claude Code/Cursor/etc. Use your coding agent to write code that calls Jev; install the TypeSafe agent skill for correct integrations.
- [[quickstart]] — Four ways in: Playground, HTTP API (`POST /v1/systemone`), Python SDK, agent skill. Contains the canonical request and response shapes.
- [[cb-function-calling]] — Turn a natural-language sentence into a call to an ordinary typed Python function (name + arguments), where every argument is an evaluated enum with a probability, via a `Dispatcher` built from a plain-words spec. Reach for it when function arguments come from fixed lists and you want per-argument confidence.
- [[cb-skill-suggestion]] — Pick at most one skill for an agent turn out of the 182 in Nous Research's Hermes catalog using two TypeSafe requests (rank all, then re-check top 3). Cuts wrong skill loads 16.8% -> 7.3% and needless loads 9.8% -> 4.0%.
- [[demo-smart-home]] — Demo app that evaluates smart-home requests with one up-front batch of "speculative" questions, uses an LLM only to split compound requests and to chat; reach for it as the reference for [[speculative-fan-out]] plus LLM fallback.
- [[http-api-reference]] — One endpoint: POST a `state` plus a map of typed `questions`; get one typed answer per question plus token usage.
- [[sdk-changelogs]] — Release history of the TypeSafe Python and JavaScript SDKs (Sept 2026), with breaking changes flagged.
- [[sdk-javascript-api]] — Compact reference of every public symbol in `@typesafe-ai/sdk` v0.6.0: client, config, retry policy, request options, question builders, answer types, error classes, aliases, constants.
- [[sdk-javascript]] — Install `@typesafe-ai/sdk` (Node 20+), set `TYPESAFE_API_KEY`, call `client.systemOne({state, questions})` with `choice()/noul()/score()`; answer types are inferred from the questions.
- [[sdk-overview]] — Two official TypeSafe client SDKs (Python, JavaScript/TypeScript) wrap the HTTP API with typed questions/answers and automatic retries; pick this note to choose between them and see the side-by-side differences.
- [[sdk-python-clients]] — Reference for `TypeSafeClient` / `AsyncTypeSafeClient` (constructor args, `system_one`, `models.list`, close) and module constants.
- [[sdk-python-retries-and-exceptions]] — `RetryPolicy` fields and the `TypeSafe*` exception hierarchy of the Python SDK, with which statuses map to which class.
- [[sdk-python-types]] — Reference for question objects (`Noul`, `Choice`, `Score`), their TypedDict twins, answer models (`NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer`), `SystemOneResponse`, `Usage` and `ListModelsResponse`.
- [[sdk-python-usage]] — Patterns for the Python SDK: calling System One, typed `response_model`, model selection, AI-gateway base URLs, HTTP/2, retries, errors, logging, env vars, forward-compat escape hatches.
- [[sdk-python]] — Install `typesafe-sdk`, set `TYPESAFE_API_KEY`, and call System One with the sync `TypeSafeClient` or async `AsyncTypeSafeClient`; start here, then go to [[sdk-python-usage]] for patterns.
- [[awesome-typesafe-jev]] — THIRD-PARTY, independent, not affiliated with TypeSafe. A curated catalogue of ~246 community SDKs, agent tools, apps, games, evaluations and open alternatives around Jev, plus five "before you trust a decision" independent findings. Reach for it to find an existing client/tool or to see what independent tests measured. All numbers below are author-reported by the listed projects, as the directory relays them; many are single-run, small-sample, or private-data.
- [[community-guide-marktechpost]] — THIRD-PARTY runnable notebook (Python, typesafe-sdk 0.7.0) covering all three primitives, state shapes, the confidence formula, fan-out vs separate calls, gated routing, composite scoring, function calling, counting, and the async/typed production shape. Contains code and prose but **no measured outputs** — it prints results at runtime; the article quotes none.
- [[jev-mcp-server]] — Third-party (author J. Kudish, MIT, "early software") MCP server exposing TypeSafe's Jev model as **twelve typed-judgment tools** — verify, screen, noul, find, rerank, classify, decide, compare, extract, audit, review, gate — each ~150–500 ms and a fraction of a cent.
- [[openrouter-jev-guide]] — THIRD-PARTY (OpenRouter's community-guide page, not TypeSafe docs). How to reach Jev through an OpenRouter key instead of a TypeSafe account: model ids, two API surfaces, billing, limits, cookbooks.
- [[typesafe-agent-skill]] — The vendor's drop-in skill (`typesafe-ai`) that tells coding agents how to build with System One/Jev: read live docs first, pick the right primitive, design narrow questions, compose in parallel, verify; plus install steps and troubleshooting.
- [[agent-operating-protocol]] — Runbook for an autonomous agent deciding whether and how to use a System One model: availability check -> classify shape -> pick tool -> design question -> fan out once -> route on confidence -> act/escalate -> report. Advisory only in this owner's repo.
- [[cheat-sheet]] — One page: primitives, thresholds, latency/cost, minimal calls, model landscape, the 12 jev-mcp tools. Follow links for caveats.
- [[model-tiering-sonnet-opus]] — Owner rule: Sonnet for READING and CONDENSATION; Opus for SYNTHESIS and for INFORMATION RETRIEVAL/ROUTING. System One models sit below both as the cheap judgment layer. The orchestrating main session dispatches both tiers because a subagent cannot spawn subagents.
- [[privacy-and-cost-gates]] — What may go to a hosted System One API (Jev, directly or via a gateway) vs what must stay local; owner rules; cost and latency budgets with sourced numbers; kill-switch conditions.
- [[retrieval-protocol-opus]] — How the Opus agent answers from THIS vault: grep-first routing via `Home.md` -> topic hub -> note, which notes to open per question type, depth rules, citation format, and how to say "the vault doesn't cover it". Plus how System One tools and embeddings shortlist big corpora.

Back to [[Home]].
