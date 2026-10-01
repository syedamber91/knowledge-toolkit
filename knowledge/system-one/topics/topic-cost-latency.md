---
title: Cost & latency
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Cost & latency
> Batching, fan-out, cascades; the measured numbers.

## Notes on this topic (33)
- [[models-and-versions]] — Current model (`jev-1.13.0`), price, rate limits, context budget, aliases (`jev-latest`/`jev-preview`), customization stance, language support, `GET /v1/models`.
- [[primitives-overview]] — The three question types (Choice, Score, Noul), the typed answer each returns, how to pick between them, and how to batch many questions into one request.
- [[intent-routing]] — Use Jev as a fast, cheap front-door classifier that sends each request to deterministic code, a specialist LLM, or a human — so expensive resources only run when needed.
- [[patterns-overview]] — Index of the four architectural patterns for building with TypeSafe; each is one atomic-decision composition idea.
- [[speculative-fan-out]] — Put every question your system might need into ONE request (including ones that may turn out irrelevant), then let code pick which answers matter.
- [[cb-autoresearch-feature-discovery]] — Turn free text into numeric features by having an LLM propose System One questions, answering them per row, training CatBoost on the answers, and feeding CatBoost's errors/importances back into the next proposal round. Reached held-out RMSE 1.77 on wine-review scores.
- [[cb-consistency-choices]] — Re-run one borderline moderation post through an 8-`Choice` rubric 15 times per condition (TypeSafe vs LLMs) and measure label stability; adding an `uncertain` outcome below top-probability 0.60 lifts TypeSafe agreement from 90.8% to 99.2% while still acting automatically on 74.2% of answers.
- [[cb-consistency-nouls]] — Re-run one auto-insurance claim through a 14-`Noul` rubric 15 times per condition (TypeSafe vs LLMs); TypeSafe's probabilities barely move (mean std 0.0102) but can still straddle 0.5, so map P(true) into yes / uncertain (0.30-0.70 inclusive) / no and send the middle to a human.
- [[cb-hierarchical-classification]] — Classify a document to a leaf of a deep taxonomy (patents, retail, biomedical, code) by asking one `Choice` per node over its direct children, in parallel across K beam paths. Beam K=3 got 4/4 expected leaves; greedy got 2/4.
- [[cb-llm-guardrails]] — Screen every message into and out of an LLM app with ONE request (a battery of `Noul` hazard questions + one `Score` severity question), then threshold in your own code to pass / review / block / support.
- [[cb-parallel-questions]] — Put all N questions about one document into ONE call: answers are identical to N single-question calls (no bias, no added noise), but 12.2x cheaper and 10.0x faster on a 13-question GDPR briefing. Always batch.
- [[cb-reranking]] — Fast search (BM25) builds a 30-passage shortlist; one Noul question per (query, candidate) pair scores each; sort by noul. On 40 CLERC legal queries: top-1 5% -> 18%, top-10 38% -> 62%, 1,200 calls for $0.0645.
- [[cb-sde-cascade]] — Structured-data-extraction cascade: extract with a cheap mini model -> verify per field with TypeSafe Noul questions -> escalate to a reasoning model only if any field's P(wrong) > 0.7. Gets most of the big model's quality at a fraction of the cost.
- [[cb-skill-suggestion]] — Pick at most one skill for an agent turn out of the 182 in Nous Research's Hermes catalog using two TypeSafe requests (rank all, then re-check top 3). Cuts wrong skill loads 16.8% -> 7.3% and needless loads 9.8% -> 4.0%.
- [[cb-structure-recovery]] — Rebuild Markdown from plain text that lost its formatting using two System One requests (stitch split sentences with Noul, classify blocks with Choice) while code does all rendering, so no output character is ever model-generated.
- [[demo-smart-home]] — Demo app that evaluates smart-home requests with one up-front batch of "speculative" questions, uses an LLM only to split compound requests and to chat; reach for it as the reference for [[speculative-fan-out]] plus LLM fallback.
- [[http-api-reference]] — One endpoint: POST a `state` plus a map of typed `questions`; get one typed answer per question plus token usage.
- [[sdk-javascript-api]] — Compact reference of every public symbol in `@typesafe-ai/sdk` v0.6.0: client, config, retry policy, request options, question builders, answer types, error classes, aliases, constants.
- [[sdk-overview]] — Two official TypeSafe client SDKs (Python, JavaScript/TypeScript) wrap the HTTP API with typed questions/answers and automatic retries; pick this note to choose between them and see the side-by-side differences.
- [[sdk-python-retries-and-exceptions]] — `RetryPolicy` fields and the `TypeSafe*` exception hierarchy of the Python SDK, with which statuses map to which class.
- [[sdk-python-usage]] — Patterns for the Python SDK: calling System One, typed `response_model`, model selection, AI-gateway base URLs, HTTP/2, retries, errors, logging, env vars, forward-compat escape hatches.
- [[community-guide-devto]] — THIRD-PARTY blog guide: setup, three primitives, five patterns, launch-week projects, failure modes, an "honest scorecard". Quotes TypeSafe's own numbers as self-run and unreproduced. Read for the cascade economics and the skeptic's checklist.
- [[jev-mcp-server]] — Third-party (author J. Kudish, MIT, "early software") MCP server exposing TypeSafe's Jev model as **twelve typed-judgment tools** — verify, screen, noul, find, rerank, classify, decide, compare, extract, audit, review, gate — each ~150–500 ms and a fraction of a cent.
- [[openrouter-jev-guide]] — THIRD-PARTY (OpenRouter's community-guide page, not TypeSafe docs). How to reach Jev through an OpenRouter key instead of a TypeSafe account: model ids, two API surfaces, billing, limits, cookbooks.
- [[benchmarks-and-comparisons]] — Every benchmark number the third-party sources give for Jev vs Laya vs open alternatives, labelled by who measured it, on what data, and how much to trust it. One independent run (SOTAAZ), many self-reported claims.
- [[jev-vs-laya]] — Hosted, closed, zero-shot-capable Jev vs open, local, small, fine-tune-first Laya: the decision turns on privacy, option count, context length, fine-tuning appetite and volume. All figures are third-party; see [[benchmarks-and-comparisons]] for trust levels.
- [[laya]] — Open (Apache 2.0), local, non-autoregressive encoder from Convai Innovations that answers Jev-style choice/score/noul questions in one forward pass. Fast and private, but weak zero-shot and with many options; reach for it for few-option English/multilingual routing you will fine-tune.
- [[openjev-and-nanojev]] — Two very different open Jev-style projects: "openjev" = a Jev-compatible server over the 26B DiffusionGemma (heavy GPU, decent on many options), and NanoJev = a 0.6B game-decision model that is NOT a text classifier. Read this before assuming either name means what you think.
- [[system-one-alternatives-overview]] — Map of every non-TypeSafe "System One" / typed-decision model the third-party sources name, with size, licence, hardware, API-compat and the stated "which to pick" rules. Reach for it when deciding whether to self-host or swap away from hosted Jev.
- [[cheat-sheet]] — One page: primitives, thresholds, latency/cost, minimal calls, model landscape, the 12 jev-mcp tools. Follow links for caveats.
- [[model-tiering-sonnet-opus]] — Owner rule: Sonnet for READING and CONDENSATION; Opus for SYNTHESIS and for INFORMATION RETRIEVAL/ROUTING. System One models sit below both as the cheap judgment layer. The orchestrating main session dispatches both tiers because a subagent cannot spawn subagents.
- [[privacy-and-cost-gates]] — What may go to a hosted System One API (Jev, directly or via a gateway) vs what must stay local; owner rules; cost and latency budgets with sourced numbers; kill-switch conditions.
- [[when-to-use-which-model]] — Executable decision matrix: deterministic code vs MiniLM-style embeddings vs a System One model (Jev hosted / Laya local / Kev / openjev) vs Sonnet vs Opus. Ladder, escalation triggers, never-use list. Every number cites the note it came from; trust labels matter.

Back to [[Home]].
