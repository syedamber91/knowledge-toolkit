---
title: Model selection
kind: topic
source: generated from note frontmatter
tags: [system-one]
topics: []
---
# Model selection
> Jev vs Laya vs Kev vs MiniLM vs LLMs: when each wins.

## Notes on this topic (23)
- [[jev-1-13-jaggedness]] — Nine documented failure modes of `jev-1.13` with the prescribed workaround for each. An agent should consult this to decide when NOT to call Jev (or how to reshape the question). Source: "Applies to `jev-1.13`. Last reviewed 2026-09-17." Many are expected to be fixed in later versions.
- [[jev-introduction]] — Jev = TypeSafe's flagship model and the first System One model: send a state plus typed questions, get typed answers (+ probabilities, + confidence for Choice/Score) your code can branch on. Read this first to know what Jev is and the three question types.
- [[jev-with-coding-agents]] — Jev is NOT a drop-in LLM for Claude Code/Cursor/etc. Use your coding agent to write code that calls Jev; install the TypeSafe agent skill for correct integrations.
- [[models-and-versions]] — Current model (`jev-1.13.0`), price, rate limits, context budget, aliases (`jev-latest`/`jev-preview`), customization stance, language support, `GET /v1/models`.
- [[system-one-model-category]] — What a "System One model" is (fast, structured, calibrated decisions for software), how it differs from an LLM, and the refund-workflow example of using it inside a larger system.
- [[cb-sde-cascade]] — Structured-data-extraction cascade: extract with a cheap mini model -> verify per field with TypeSafe Noul questions -> escalate to a reasoning model only if any field's P(wrong) > 0.7. Gets most of the big model's quality at a fraction of the cost.
- [[sdk-python-usage]] — Patterns for the Python SDK: calling System One, typed `response_model`, model selection, AI-gateway base URLs, HTTP/2, retries, errors, logging, env vars, forward-compat escape hatches.
- [[awesome-typesafe-jev]] — THIRD-PARTY, independent, not affiliated with TypeSafe. A curated catalogue of ~246 community SDKs, agent tools, apps, games, evaluations and open alternatives around Jev, plus five "before you trust a decision" independent findings. Reach for it to find an existing client/tool or to see what independent tests measured. All numbers below are author-reported by the listed projects, as the directory relays them; many are single-run, small-sample, or private-data.
- [[community-guide-devto]] — THIRD-PARTY blog guide: setup, three primitives, five patterns, launch-week projects, failure modes, an "honest scorecard". Quotes TypeSafe's own numbers as self-run and unreproduced. Read for the cascade economics and the skeptic's checklist.
- [[jev-mcp-server]] — Third-party (author J. Kudish, MIT, "early software") MCP server exposing TypeSafe's Jev model as **twelve typed-judgment tools** — verify, screen, noul, find, rerank, classify, decide, compare, extract, audit, review, gate — each ~150–500 ms and a fraction of a cent.
- [[openrouter-jev-guide]] — THIRD-PARTY (OpenRouter's community-guide page, not TypeSafe docs). How to reach Jev through an OpenRouter key instead of a TypeSafe account: model ids, two API surfaces, billing, limits, cookbooks.
- [[benchmarks-and-comparisons]] — Every benchmark number the third-party sources give for Jev vs Laya vs open alternatives, labelled by who measured it, on what data, and how much to trust it. One independent run (SOTAAZ), many self-reported claims.
- [[jev-vs-laya]] — Hosted, closed, zero-shot-capable Jev vs open, local, small, fine-tune-first Laya: the decision turns on privacy, option count, context length, fine-tuning appetite and volume. All figures are third-party; see [[benchmarks-and-comparisons]] for trust levels.
- [[kev]] — Apache-2.0, locally runnable Jev-style choice/score/noul models fine-tuned from Qwen by Jared Palmer; the "bigger, more accurate, open" self-host option next to the small encoder Laya. Reach for it when you want to self-host Jev-compatible endpoints and have a GPU (or an Apple Silicon Mac for the smallest).
- [[laya]] — Open (Apache 2.0), local, non-autoregressive encoder from Convai Innovations that answers Jev-style choice/score/noul questions in one forward pass. Fast and private, but weak zero-shot and with many options; reach for it for few-option English/multilingual routing you will fine-tune.
- [[minilm-embeddings]] — A small sentence-embedding model used in the SOTAAZ benchmarks as (a) a trained-classifier baseline, (b) a nearest-label-name zero-shot baseline, and (c) a candidate shortlister in front of Laya. It is NOT a typed, calibrated System One decision model — it embeds text; it does not natively answer choice/score/noul questions with calibrated probabilities.
- [[openjev-and-nanojev]] — Two very different open Jev-style projects: "openjev" = a Jev-compatible server over the 26B DiffusionGemma (heavy GPU, decent on many options), and NanoJev = a 0.6B game-decision model that is NOT a text classifier. Read this before assuming either name means what you think.
- [[system-one-alternatives-overview]] — Map of every non-TypeSafe "System One" / typed-decision model the third-party sources name, with size, licence, hardware, API-compat and the stated "which to pick" rules. Reach for it when deciding whether to self-host or swap away from hosted Jev.
- [[anti-patterns]] — Every documented failure mode, trap and pitfall across the vault, grouped, each with the fix and the note that proves it. Section F lists source disagreements and vendor bias.
- [[cheat-sheet]] — One page: primitives, thresholds, latency/cost, minimal calls, model landscape, the 12 jev-mcp tools. Follow links for caveats.
- [[model-tiering-sonnet-opus]] — Owner rule: Sonnet for READING and CONDENSATION; Opus for SYNTHESIS and for INFORMATION RETRIEVAL/ROUTING. System One models sit below both as the cheap judgment layer. The orchestrating main session dispatches both tiers because a subagent cannot spawn subagents.
- [[privacy-and-cost-gates]] — What may go to a hosted System One API (Jev, directly or via a gateway) vs what must stay local; owner rules; cost and latency budgets with sourced numbers; kill-switch conditions.
- [[when-to-use-which-model]] — Executable decision matrix: deterministic code vs MiniLM-style embeddings vs a System One model (Jev hosted / Laya local / Kev / openjev) vs Sonnet vs Opus. Ladder, escalation triggers, never-use list. Every number cites the note it came from; trust labels matter.

Back to [[Home]].
