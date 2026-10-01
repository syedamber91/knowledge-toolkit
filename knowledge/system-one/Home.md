---
title: System One Home
kind: index
source: generated
tags: [system-one]
topics: []
---

# System One — Home
> Everything from TypeSafe's Jev / System One docs plus the open alternatives (Laya, Kev, MiniLM), condensed for autonomous agents. Start at [[when-to-use-which-model]] or [[agent-operating-protocol]]. History: [[Log|Ingestion Log]].

## Topic hubs
- [[topic-calibration]] — Probabilities that mean something; confidence vs probability; thresholds.
- [[topic-routing]] — Send each input to code, a small model, an LLM or a human based on answer + confidence.
- [[topic-classification]] — Choice-based labelling, hierarchies, 'unsure' outcomes.
- [[topic-extraction]] — Pulling dates, values, structure and fields out of text, verified in code.
- [[topic-guardrails]] — Screening, citation checks, hazard scoring, pass/review/block.
- [[topic-retrieval-rerank]] — Shortlist cheaply, then score candidates with typed questions.
- [[topic-cost-latency]] — Batching, fan-out, cascades; the measured numbers.
- [[topic-state-design]] — What to put in state; how to word questions, options, levels.
- [[topic-agent-integration]] — MCP server, agent skill, SDKs, OpenRouter, cloud/local setup.
- [[topic-model-selection]] — Jev vs Laya vs Kev vs MiniLM vs LLMs: when each wins.

## Orientation
- [[ai-primer-calibrated-decisions]] — Why TypeSafe trains models for calibrated decisions (RLCD) rather than generated text (RLHF/RLVR): the theory behind Jev's probabilities and confidence.
- [[jev-1-13-jaggedness]] — Nine documented failure modes of `jev-1.13` with the prescribed workaround for each. An agent should consult this to decide when NOT to call Jev (or how to reshape the question). Source: "Applies to `jev-1.13`. Last reviewed 2026-09-17." Many are expected to be fixed in later versions.
- [[jev-introduction]] — Jev = TypeSafe's flagship model and the first System One model: send a state plus typed questions, get typed answers (+ probabilities, + confidence for Choice/Score) your code can branch on. Read this first to know what Jev is and the three question types.
- [[jev-with-coding-agents]] — Jev is NOT a drop-in LLM for Claude Code/Cursor/etc. Use your coding agent to write code that calls Jev; install the TypeSafe agent skill for correct integrations.
- [[models-and-versions]] — Current model (`jev-1.13.0`), price, rate limits, context budget, aliases (`jev-latest`/`jev-preview`), customization stance, language support, `GET /v1/models`.
- [[quickstart]] — Four ways in: Playground, HTTP API (`POST /v1/systemone`), Python SDK, agent skill. Contains the canonical request and response shapes.
- [[system-one-model-category]] — What a "System One model" is (fast, structured, calibrated decisions for software), how it differs from an LLM, and the refund-workflow example of using it inside a larger system.

## Concepts & primitives
- [[advanced-structure]] — Instructions, Choice option descriptions, Score level descriptions and Noul criteria all accept JSON (object/array) because System One models are trained to understand structure.
- [[choice]] — Select one option from a fixed, unordered set; returns the chosen option, a probability per option, and a confidence. Use for routing and classification.
- [[confidence]] — A 0-1 summary of how peaked an answer's probability distribution is, returned on every Choice and Score answer; use it to decide act / confirm / escalate.
- [[how-to-build-with-system-one]] — Design recipe: keep code in control of the workflow, give System One narrow typed questions, run many in one parallel request, combine in code, route on confidence. Includes the 8-step workflow and a full triage example.
- [[noul]] — A yes/no question; returns one number 0..1 = probability the answer is yes. Use for checks, guardrails, verification and as a ranking signal.
- [[primitives-overview]] — The three question types (Choice, Score, Noul), the typed answer each returns, how to pick between them, and how to batch many questions into one request.
- [[score]] — Rate content against ordered, descriptive levels; returns a fractional position (probability-weighted level number), per-level probabilities, a legend and confidence. Use for spectra (severity, frustration, experience) and as building blocks for weighted composites.
- [[state]] — The `state` field = the content (and supporting facts) a System One model evaluates; one state per request, many questions against it. String, JSON object, or array of text.

## Patterns
- [[composite-scoring]] — Break a complex judgment into independent atomic Score dimensions, normalize, then combine with weights you own in code.
- [[confidence-gated-routing]] — The answer says WHAT; confidence says WHETHER to act. Set per-action thresholds by risk, escalate to a human or ask for confirmation in the middle band.
- [[intent-routing]] — Use Jev as a fast, cheap front-door classifier that sends each request to deterministic code, a specialist LLM, or a human — so expensive resources only run when needed.
- [[patterns-overview]] — Index of the four architectural patterns for building with TypeSafe; each is one atomic-decision composition idea.
- [[speculative-fan-out]] — Put every question your system might need into ONE request (including ones that may turn out irrelevant), then let code pick which answers matter.

## Cookbooks
- [[cb-autoresearch-feature-discovery]] — Turn free text into numeric features by having an LLM propose System One questions, answering them per row, training CatBoost on the answers, and feeding CatBoost's errors/importances back into the next proposal round. Reached held-out RMSE 1.77 on wine-review scores.
- [[cb-citation-check]] — Catch wrong or hallucinated LLM citations: an ordinary string match finds fabricated quotes, then ONE `Choice` question reads the quote's section and decides supports / contradicts / says nothing; a 0.8 confidence gate sends weak verdicts to a human.
- [[cb-classification-using-confidence]] — One 75-option `Choice` per document; read its `confidence`; if >= 0.9 report the fine label (industry group), else report the parent label (division). One request per document, no second model, no extra calls.
- [[cb-classifying-rag-passages]] — Between retrieval and generation, score every retrieved passage with ONE `system_one` call of four `Noul` questions, then route it in plain code to evidence / conflict / dropped. Use when similarity search hands noisy, contradicting or prompt-injected passages to an answering LLM.
- [[cb-consistency-choices]] — Re-run one borderline moderation post through an 8-`Choice` rubric 15 times per condition (TypeSafe vs LLMs) and measure label stability; adding an `uncertain` outcome below top-probability 0.60 lifts TypeSafe agreement from 90.8% to 99.2% while still acting automatically on 74.2% of answers.
- [[cb-consistency-nouls]] — Re-run one auto-insurance claim through a 14-`Noul` rubric 15 times per condition (TypeSafe vs LLMs); TypeSafe's probabilities barely move (mean std 0.0102) but can still straddle 0.5, so map P(true) into yes / uncertain (0.30-0.70 inclusive) / no and send the middle to a human.
- [[cb-date-extraction]] — Read a date's PARTS off the text with 7 `Choice` questions in one call, then resolve them to a real `date` in code (code does the calendar math, never the model); min-confidence across used parts gates human review.
- [[cb-entity-alignment]] — Decide, for each of 450 candidate duplicate pairs (two beer catalogues), whether to merge, drop, or send to a human curator, using ONE `Score` question (3 levels) plus three companion `Noul` questions in a single request. No fitted threshold anywhere.
- [[cb-function-calling]] — Turn a natural-language sentence into a call to an ordinary typed Python function (name + arguments), where every argument is an evaluated enum with a probability, via a `Dispatcher` built from a plain-words spec. Reach for it when function arguments come from fixed lists and you want per-argument confidence.
- [[cb-hierarchical-classification]] — Classify a document to a leaf of a deep taxonomy (patents, retail, biomedical, code) by asking one `Choice` per node over its direct children, in parallel across K beam paths. Beam K=3 got 4/4 expected leaves; greedy got 2/4.
- [[cb-line-by-line-search]] — Semantic search over one document in a single request: tag each line with an ID, use a Choice over the line IDs to rank lines, and a Noul in the same request to say whether the document answers at all. Returns `exists` probability + one relevance score per line.
- [[cb-llm-guardrails]] — Screen every message into and out of an LLM app with ONE request (a battery of `Noul` hazard questions + one `Score` severity question), then threshold in your own code to pass / review / block / support.
- [[cb-parallel-questions]] — Put all N questions about one document into ONE call: answers are identical to N single-question calls (no bias, no added noise), but 12.2x cheaper and 10.0x faster on a 13-question GDPR briefing. Always batch.
- [[cb-pre-parsed-value-extraction]] — Regex finds candidate spans (emails, phones, amounts), TypeSafe picks the one the question asks for, code copies it verbatim and normalizes it. Reach for it when you need an exact value out of a document and must never get an invented or digit-transposed one.
- [[cb-reranking]] — Fast search (BM25) builds a 30-passage shortlist; one Noul question per (query, candidate) pair scores each; sort by noul. On 40 CLERC legal queries: top-1 5% -> 18%, top-10 38% -> 62%, 1,200 calls for $0.0645.
- [[cb-sde-cascade]] — Structured-data-extraction cascade: extract with a cheap mini model -> verify per field with TypeSafe Noul questions -> escalate to a reasoning model only if any field's P(wrong) > 0.7. Gets most of the big model's quality at a fraction of the cost.
- [[cb-skill-suggestion]] — Pick at most one skill for an agent turn out of the 182 in Nous Research's Hermes catalog using two TypeSafe requests (rank all, then re-check top 3). Cuts wrong skill loads 16.8% -> 7.3% and needless loads 9.8% -> 4.0%.
- [[cb-structure-recovery]] — Rebuild Markdown from plain text that lost its formatting using two System One requests (stitch split sentences with Noul, classify blocks with Choice) while code does all rendering, so no output character is ever model-generated.
- [[cookbooks-overview]] — Index of 19 end-to-end TypeSafe recipes grouped by theme, with each recipe's one-line outcome, headline numbers and difficulty level.

## Use cases & demos
- [[demo-smart-home]] — Demo app that evaluates smart-home requests with one up-front batch of "speculative" questions, uses an LLM only to split compound requests and to chat; reach for it as the reference for [[speculative-fan-out]] plus LLM fallback.
- [[use-case-map]] — Brainstorming catalogue: 5 headline categories, 20 industry/task idea lists, and a 10-row "decision shape" table. Open the closest industry, scan the example decisions, adapt to your own documents and actions.

## API & SDKs
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

## Agent tooling & community
- [[awesome-typesafe-jev]] — THIRD-PARTY, independent, not affiliated with TypeSafe. A curated catalogue of ~246 community SDKs, agent tools, apps, games, evaluations and open alternatives around Jev, plus five "before you trust a decision" independent findings. Reach for it to find an existing client/tool or to see what independent tests measured. All numbers below are author-reported by the listed projects, as the directory relays them; many are single-run, small-sample, or private-data.
- [[community-guide-devto]] — THIRD-PARTY blog guide: setup, three primitives, five patterns, launch-week projects, failure modes, an "honest scorecard". Quotes TypeSafe's own numbers as self-run and unreproduced. Read for the cascade economics and the skeptic's checklist.
- [[community-guide-marktechpost]] — THIRD-PARTY runnable notebook (Python, typesafe-sdk 0.7.0) covering all three primitives, state shapes, the confidence formula, fan-out vs separate calls, gated routing, composite scoring, function calling, counting, and the async/typed production shape. Contains code and prose but **no measured outputs** — it prints results at runtime; the article quotes none.
- [[jev-mcp-server]] — Third-party (author J. Kudish, MIT, "early software") MCP server exposing TypeSafe's Jev model as **twelve typed-judgment tools** — verify, screen, noul, find, rerank, classify, decide, compare, extract, audit, review, gate — each ~150–500 ms and a fraction of a cent.
- [[openrouter-jev-guide]] — THIRD-PARTY (OpenRouter's community-guide page, not TypeSafe docs). How to reach Jev through an OpenRouter key instead of a TypeSafe account: model ids, two API surfaces, billing, limits, cookbooks.
- [[typesafe-agent-skill]] — The vendor's drop-in skill (`typesafe-ai`) that tells coding agents how to build with System One/Jev: read live docs first, pick the right primitive, design narrow questions, compose in parallel, verify; plus install steps and troubleshooting.

## Alternatives (Laya, Kev, MiniLM...)
- [[benchmarks-and-comparisons]] — Every benchmark number the third-party sources give for Jev vs Laya vs open alternatives, labelled by who measured it, on what data, and how much to trust it. One independent run (SOTAAZ), many self-reported claims.
- [[jev-vs-laya]] — Hosted, closed, zero-shot-capable Jev vs open, local, small, fine-tune-first Laya: the decision turns on privacy, option count, context length, fine-tuning appetite and volume. All figures are third-party; see [[benchmarks-and-comparisons]] for trust levels.
- [[kev]] — Apache-2.0, locally runnable Jev-style choice/score/noul models fine-tuned from Qwen by Jared Palmer; the "bigger, more accurate, open" self-host option next to the small encoder Laya. Reach for it when you want to self-host Jev-compatible endpoints and have a GPU (or an Apple Silicon Mac for the smallest).
- [[laya]] — Open (Apache 2.0), local, non-autoregressive encoder from Convai Innovations that answers Jev-style choice/score/noul questions in one forward pass. Fast and private, but weak zero-shot and with many options; reach for it for few-option English/multilingual routing you will fine-tune.
- [[minilm-embeddings]] — A small sentence-embedding model used in the SOTAAZ benchmarks as (a) a trained-classifier baseline, (b) a nearest-label-name zero-shot baseline, and (c) a candidate shortlister in front of Laya. It is NOT a typed, calibrated System One decision model — it embeds text; it does not natively answer choice/score/noul questions with calibrated probabilities.
- [[openjev-and-nanojev]] — Two very different open Jev-style projects: "openjev" = a Jev-compatible server over the 26B DiffusionGemma (heavy GPU, decent on many options), and NanoJev = a 0.6B game-decision model that is NOT a text classifier. Read this before assuming either name means what you think.
- [[system-one-alternatives-overview]] — Map of every non-TypeSafe "System One" / typed-decision model the third-party sources name, with size, licence, hardware, API-compat and the stated "which to pick" rules. Reach for it when deciding whether to self-host or swap away from hosted Jev.

## Playbook (agent decision rules)
- [[agent-operating-protocol]] — Runbook for an autonomous agent deciding whether and how to use a System One model: availability check -> classify shape -> pick tool -> design question -> fan out once -> route on confidence -> act/escalate -> report. Advisory only in this owner's repo.
- [[anti-patterns]] — Every documented failure mode, trap and pitfall across the vault, grouped, each with the fix and the note that proves it. Section F lists source disagreements and vendor bias.
- [[cheat-sheet]] — One page: primitives, thresholds, latency/cost, minimal calls, model landscape, the 12 jev-mcp tools. Follow links for caveats.
- [[model-tiering-sonnet-opus]] — Owner rule: Sonnet for READING and CONDENSATION; Opus for SYNTHESIS and for INFORMATION RETRIEVAL/ROUTING. System One models sit below both as the cheap judgment layer. The orchestrating main session dispatches both tiers because a subagent cannot spawn subagents.
- [[privacy-and-cost-gates]] — What may go to a hosted System One API (Jev, directly or via a gateway) vs what must stay local; owner rules; cost and latency budgets with sourced numbers; kill-switch conditions.
- [[question-design-checklist]] — Write the state, pick Choice/Score/Noul, word options/levels/criteria, add escape outcomes, set thresholds, add companion Nouls, batch in one call. Every rule carries the example or number that proves it.
- [[retrieval-protocol-opus]] — How the Opus agent answers from THIS vault: grep-first routing via `Home.md` -> topic hub -> note, which notes to open per question type, depth rules, citation format, and how to say "the vault doesn't cover it". Plus how System One tools and embeddings shortlist big corpora.
- [[when-to-use-which-model]] — Executable decision matrix: deterministic code vs MiniLM-style embeddings vs a System One model (Jev hosted / Laya local / Kev / openjev) vs Sonnet vs Opus. Ladder, escalation triggers, never-use list. Every number cites the note it came from; trust labels matter.
