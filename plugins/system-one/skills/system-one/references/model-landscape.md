# Model landscape — Jev, Laya, Kev, openjev/NanoJev, MiniLM, LLM tiers

Condensed from vault notes `models-and-versions`, `system-one-model-category`,
`laya`, `kev`, `openjev-and-nanojev`, `minilm-embeddings`, `jev-vs-laya`,
`benchmarks-and-comparisons`, `system-one-alternatives-overview`. Most non-TypeSafe
numbers are author-reported; SOTAAZ is the one independent measurer (no Jev access).

## What a System One model is
Fast, structured decisions software can use: reads a text `state` + typed questions,
returns typed answers with probabilities — no generated text, no explanations.
Name from Kahneman's System 1. Jev introduced the category on 2026-09-15; open
models followed within days (system-one-model-category, system-one-alternatives-overview).

## Jev (TypeSafe, hosted)
| Fact | Value |
|---|---|
| Current model | `jev-1.13.0`; aliases `jev-latest` (stable, SDK default) and `jev-preview` (currently same) |
| Endpoint | `POST https://api.typesafe.ai/v1/systemone`; `GET /v1/models` |
| Price | $0.042 / M input tokens; output free |
| Rate limits | 100K tokens/s, 40 req/s; change without notice; 429 over either (dev.to reports 250K tok/s, 1,200 req/min) |
| Context | 64k tokens/request; 32k for state + longest question (OpenRouter page: 32,000 total) |
| Input | text only (string, JSON object, array of text) |
| Languages | English best; CJK and others handled, lower accuracy — test |
| Training | RLCD (calibrated decisions); same weights for all accounts; no fine-tuning/LoRA on customer data |
| Data | not trained on customer requests; DPA; ZDR for enterprise |
| Limits | Choice <=255 options (~240 reliable); Score 2-10 levels |
| Latency | ~100 ms "most queries" (vendor); 111-114 ms mean measured in cookbooks; 150-500 ms via jev-mcp; 230-317 ms per Laya-side comparisons |
| Access routes | TypeSafe direct; OpenRouter (`typesafe/jev-1.13`, alias `~typesafe/jev-latest` — jev-mcp says OpenRouter serves pinned only); Vercel AI Gateway (`typesafe-ai/jev`); Cloudflare Workers AI (`typesafe/jev`); Pydantic AI Gateway; jev-mcp |
| SDKs | Python `typesafe-sdk` (>=3.10; v0.7.2), JS `@typesafe-ai/sdk` (Node 20+; v0.6.0) |
Weak spots (jaggedness): literal reading, math/counting/numbers, dates, indirection,
large irrelevant state, adversarial content, contradictory criteria, cross-question
invariants, generation. Pin the version when thresholds are tuned.

Independent evidence on Jev (awesome-typesafe-jev, third-party): KoBBQ — chose
"unknown" on 95% of 300 ambiguous items, 79% stereotype picks without it; CLINC150
conformal routing — 84.75% auto-routed at 2.25% loss, scope gate missed target 3.6x
under shift; ChaosNLI — Choice overconfident on contested items (ECE gap 0.264);
dice test — 82.9% mass on one face at 19.0% accuracy; 111-case action gate — Jev 100
vs Claude 102 correct, one unsafe allow each; earnings memory test — no detectable
memory (AUC 0.506).

## Laya (Convai Innovations; open, local)
| Fact | Value |
|---|---|
| Licence / size | Apache 2.0; 421M English (ModernBERT-large), 322M multilingual (mmBERT-base); `laya-typed-decisions` 421M |
| Mechanism | non-autoregressive encoder; each option gets a `[MASK]` slot -> logit -> softmax; RL against proper scoring rules + fitted temperatures |
| Run | `pip install laya`; `Router()`; ~1 GB RAM; CPU ok; `laya-serve` exposes `POST /v1/systemone` (Jev clients switch by base URL) |
| Latency | 23 ms A100 (SOTAAZ); 32.8 ms p50 T4; 30-40 ms; ~9 ms P50 batched / ~86 decisions/s |
| Accuracy | zero-shot base 0.362 (random 0.318) vs fine-tuned 0.766 on its own 2,000-decision benchmark; spam 0.993, phishing 0.980, guardrails 0.755-0.762, RAG relevance 0.657, 10-way routing 0.522 (own) |
| SOTAAZ | TREC 86.6% (88.6% with descriptions); BANKING77 37.0% default, 46.1% at 512-token option budget, 59.1% on MiniLM top-20; AG News 94.5% (in training mix) |
| Calibration | ECE 0.081 after refit (own); raw weak; English root 0.000 accuracy on Khmer at 0.952 confidence — use the Router |
| Limits | 192-token shared option budget; degrades past ~20 options; context 512 (vanekt) vs 8,192 max / 1,024 default multilingual (Menon) — unresolved |
| Fine-tune | free Kaggle 2xT4 notebook, ~4 h |
Use for (Jev-first exceptions): privacy, few options, English or routed multilingual, high volume, binary
safety calls, when you can fine-tune. Not for: zero-shot 50-100 options, long inputs.

## Kev (Jared Palmer; open)
Apache 2.0, Qwen-based Jev-style models, 0.8B/4B/9B (+27B per tracker); fitted
temperature per checkpoint; System One-compatible server, TypeSafe SDK works
unchanged; Kev-9B 0.822 vs hosted Jev 0.857 on its suite (author). No latency
numbers anywhere. Layer3Labs conflicts: 0.6B/4B/8B on Qwen2.5/3.5 — prefer tracker.
Hardware: Mac (0.8B) to one 80 GB GPU (27B).

## openjev / NanoJev (and the name collision)
- "OpenJev" = four projects: razorback16/openjev (DiffusionGemma 26B server — the one SOTAAZ measured), SemIf formerly OpenJev (TheoLeeCJ, training-free), OpenJev-4B (ejhshen), Open-Jev (Zefan Cai). Resolve by repo owner.
- openjev (SOTAAZ, A100, bf16): BANKING77 66.9% one read, 81 ms; TREC 66.0% names / 80.0% with descriptions, 48 ms; AG News 85.0%. Needs a 26B-capable GPU. "Without labels, openjev at 67% is the best open option I measured."
- Server config swings results: `--async-scheduling` changed 28/154 answers; example server two-stage 54.5% vs one read 66.9%.
- NanoJev (0.6B, games: Maze/Snake/ViZDoom): TREC 18.4%, BANKING77 20.1%, AG News 31.0% — not for text.

## MiniLM embeddings (SOTAAZ only)
- Trained MiniLM + logistic regression: TREC 90.4% (5.7 ms CPU, 5,452 training examples); BANKING77 90.3% (6.8 ms CPU) — beat every decision model on BANKING77 by >20 points.
- Nearest label name (zero-shot): TREC 48.6%, BANKING77 56.5%.
- As a shortlister in front of Laya: top-20 lifted Laya 37.0% -> 59.1%, but "most of that row is MiniLM's work".
- Not a System One model: no typed schema; calibration not measured; exact checkpoint unknown.
- Use (Jev-first exception) when dozens of classes + labels exist, or to shortlist for a small-budget decision model.

## Other open/hosted options (tracker, self-reported)
Liquid AI d1 (hosted, `POST /decisions/v1/systemone`, free tier), OpenAI Decisions API
(preview, own interface), OpenDecider, Decider, Von, Bespoke Nimble, Rizzo Flow (0.648
vs Jev 0.727, uncalibrated), AnyJev (training-free), Jev-Style, Anarkali (68M, 74.0% vs
72.7%), Jeeves (9B, thinks; 0.935 vs 0.866), OpenThai-SystemOne, GLiNER2.5-Decide. Self-host
with existing clients: Laya, Kev, Decider, OpenDecider, Von, OpenThai-SystemOne.
"Measure on your own data before switching."

## LLM tiers (vault has no list prices)
| Model | Number (source) |
|---|---|
| Claude Haiku 4.5 | 0.99-3.9 s, $0.0015-0.0035 per rubric call; t=0 100% agreement (repeatability only) (cb-consistency-*) |
| Claude Sonnet 5 | 67.8% on TypeSafe's 4-workflow eval at 293x Jev cost, 195x latency (community-guide-devto, self-run) |
| Claude Opus 4.8 reasoning | 10.4-13.9 s, $0.028-0.034 per rubric call; 92.5% raw agreement (cb-consistency-*) |
| Opus 5 | 73.1% on the 4-workflow eval; $0.032 per computer-use decision vs Jev $0.0002 |
| gpt-5.5 reasoning | ~0.81 extraction quality at ~$0.10 per extraction (cb-sde-cascade) |
