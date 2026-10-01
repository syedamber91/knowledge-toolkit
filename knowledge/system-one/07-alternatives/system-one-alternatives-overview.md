---
title: System One Alternatives Overview
kind: comparison
source: "System One Decision Models: Laya, Jev, AnyJev, Nimble and Open Alternatives (laya-ai.com tracker); Laya Alternatives (Layer3Labs); Jev Alternatives Benchmarked (SOTAAZ); Awesome Jev / TypeSafe README (AbdelStark)"
source_url: https://laya-ai.com/system-one-models ; https://www.layer3labs.io/comparisons/laya-alternatives ; https://sotaaz.com/post/jev-alternatives-bench-en ; https://github.com/AbdelStark/awesome-typesafe-jev
tags: [alternatives, system-one, model-limits]
topics: [topic-model-selection, topic-cost-latency]
---
# System One Alternatives Overview
> Map of every non-TypeSafe "System One" / typed-decision model the third-party sources name, with size, licence, hardware, API-compat and the stated "which to pick" rules. Reach for it when deciding whether to self-host or swap away from hosted Jev.

**Source reliability (read first).** Everything here is THIRD-PARTY. The tracker (laya-ai.com) says it was "Checked against each project's own pages on Oct 1, 2026" — so its rows are each project's self-description, not measurements. The tracker itself warns: "Benchmarks in this space are young and mostly self-reported, on different datasets." The page does not name its publisher; the domain is `laya-ai.com` [inference: do not assume it is independent of Laya]. Layer3Labs is a consultancy (ends with "Book a free 30-minute AI workflow audit") and eesel is a vendor selling an AI-support product; both are marketing-adjacent. SOTAAZ is a hands-on measurement blog (author sells courses, no Jev API access). See [[benchmarks-and-comparisons]] for the numbers and [[jev-vs-laya]] for the head-to-head.

## What it is / How it works
A System One model (tracker): reads a *state* (ticket, email, JSON) plus a set of typed questions; returns an answer plus a probability for every allowed option in one pass, no free text to generate or parse. TypeSafe Jev "named the category on September 15, 2026, and a wave of open models followed within days." See [[system-one-model-category]], [[jev-introduction]].

Three build strategies (tracker):
| Strategy | Examples | Consequence |
|---|---|---|
| Train an encoder with decision heads | Laya, Von, (nano) OpenDecider, GLiNER2.5-Decide, Anarkali, open-jev-deberta | smallest models, CPU-friendly |
| Fine-tune an open LLM | Kev, Decider, Nimble, Tev1, Rizzo Flow, Jeeves, JevK5, Jev-Style, OpenThai-SystemOne, AgentJev, OpenJev-4B, Open-Jev, Jev-Omni | bigger, needs GPU (or llama.cpp), higher accuracy potential |
| Training-free, read decisions from an existing LLM | AnyJev, SemIf (formerly OpenJev), djev | no training; size/hardware = the host model |
The strategy "changes the model size, the hardware you need, and how the probabilities are calibrated."

## The full landscape table (tracker, as of Oct 1 2026)
Columns: approach; size; licence; runs on; Jev-API-compatible?; languages. "Compat" = serves/accepts the Jev-style `POST /v1/systemone` shape.

| Model (author) | Approach | Size | Licence | Runs on | Jev API compat | Languages |
|---|---|---|---|---|---|---|
| TypeSafe Jev (TypeSafe AI) | hosted; introduced choice/score/noul | undisclosed | proprietary | TypeSafe cloud only | the reference API | provider-dependent |
| Liquid AI d1 | hosted; released Sep 29 2026; free tier model name `d1:free`; paid price not published | undisclosed | proprietary | Liquid API only, no weights | yes, `POST /decisions/v1/systemone`; works with TypeSafe SDKs | not stated |
| OpenAI Decisions API | announced DevDay Sep 29 2026; pick one answer from a list; 150 ms vs 1.6 s for regular GPT-6 Luna (OpenAI figures); limited preview; price + probability output not published | undisclosed (a version of GPT-6 Luna) | proprietary | OpenAI API only | no, own interface (not documented yet) | not stated; accepts text or images |
| Laya (Convai Innovations) | encoder + choice/score/noul heads on ModernBERT and mmBERT; Router, fine-tuning, many community runtimes | 322M / 421M | Apache 2.0 | CPU, CUDA, Apple Silicon | yes via `laya-serve` | English + 100+ language checkpoint |
| Kev (Jared Palmer) | small Jev-like models on Qwen3.5/Qwen3.8; each checkpoint ships a fitted temperature; fine-tune+deploy loop on Modal | 0.8B/4B/9B/27B | Apache 2.0 | Apple Silicon Mac (0.8B) up to one 80 GB GPU (27B) | yes, TypeSafe SDK unchanged | not stated |
| OpenDecider (Manjunath Shiva) | distilled from two open teachers; nano = trained encoder, small/medium = fine-tuned Qwen; early release | ~400M / 4B / 30B MoE | Apache 2.0 | CPU, CUDA, Apple Silicon (MLX); 30B needs several NVIDIA GPUs | yes, `opendecider serve` (0.2.0+): `POST /v1/systemone` and `/batch` | English (only English evaluated) |
| Decider (Mapika) | one-pass typed decisions, trained on public data + labels from local Qwen3.5-27B teacher; choice supports 2-255 options | 2B / 4B / 35B MoE | Apache 2.0 | local GPU, vLLM serving | yes, `/v1/systemone` | not stated |
| Von (wfzyx) | ModernBERT-Large encoder; v1.2 scores each option independently so answer no longer depends on option order | 395M | Apache 2.0 | local CPU or GPU | yes, `/v1/systemone` server | English |
| Bespoke Nimble (Bespoke Labs) | publishes data-curation/training/serving recipe behind Bespoke-Nimble-9B; now takes 8,192-token inputs and up to 255 choices per field | 9B | not stated in repo | Apple Silicon, NVIDIA GPU | no, own schema format | not stated |
| SemIf, formerly OpenJev (TheoLeeCJ) | training-free; scores typed options directly from a frozen open model, no answer text/JSON parsing; per-workload temperature calibration | depends on model (2B to 27B tested) | MIT | RTX 3090, Apple Silicon, browser (WebGPU demo) | reproduces the interface pattern | depends on model |
| Rizzo Flow (Rizzo AI Academy) | LoRA fine-tune of Spark-X2.5 on llama.cpp; reports 0.648 on typed-decisions vs 0.727 for Jev; probabilities uncalibrated unless you calibrate on your data | 1.7B / 4B | Apache 2.0 | llama.cpp: CUDA, Metal, Vulkan, ROCm, SYCL or CPU | yes, `POST /v1/systemone` | not stated |
| AnyJev (Nokia Applied Research) | training-free library; reads an existing LLM's hidden states; debiasing + calibration levels | depends on model | Apache 2.0 | HF models, vLLM serving | serves its own decision endpoint | depends on model |
| NanoJev (TianyuCodings) | compact replica + end-to-end training pipeline; evaluated on ViZDoom, a maze, Snake vs Jev | 0.6B | MIT | local GPU | not stated | not stated |
| Tev1-4B-experimental (Together AI) | experimental SFT of Qwen3.5-4B, released Sep 23 2026; data recipe + training guide; answers with one option letter | 4B | weights licence being finalized; code MIT | Together API, or self-hosted Transformers/GGUF | no, chat completions with 2-24 options | not stated |
| GLiNER2.5-Decide (Fastino) | takes label sets at call time, scores several heads in one pass; intent/routing/sentiment/priority | 340M (also 1B, and 287M multilingual) | Apache 2.0 | CPU or GPU with `gliner2` package | no, own `classify_text` API | English + multilingual variant |
| OpenThai-SystemOne (iApp Technology) | Qwen3.5-0.8B text tower, output head replaced by 256-way slot softmax, continued-pretrained on Thai | 0.8B | Apache 2.0 | CUDA, MPS, CPU | yes, mirrors `POST /v1/systemone` | Thai, English |
| djev / DiffusionGemma-Jev (mmastrac) | reads decisions from DiffusionGemma (discrete diffusion) in one denoise step via vLLM; djev-dev fork adds native image inputs + live camera | DiffusionGemma (26B-A4B in DGX Spark recipe) | Apache 2.0 | NVIDIA GPU with vLLM | yes, `POST /v1/systemone` | not stated |
| Jev-Omni (akhilaaa3) | multimodal (text/image/audio/video) decision classifier fine-tuned on 30,000 questions; reports 86.15% on matched JevBench groups (self-reported) | 12B (Gemma 4 12B) | Apache 2.0 | NVIDIA GPU | not stated | not stated |
| Open-Jev (Zefan Cai) | scores supplied candidates for choice/noul/score without generating, trained head on Qwen3.5 | 2B, 9B, 27B (LoRA adapter + scalar head) | Apache 2.0 | NVIDIA GPU | yes, local `/v1/systemone` server | not stated |
| JevK5 (alibiserikbay) | Qwen3.5-4B merged LoRA, read out with SemIf protocol + one calibration temperature; >16 options read in several passes | 4B | Apache 2.0 | local GPU | yes, TypeSafe-style `/v1/systemone` runtime | English |
| open-jev-deberta-v3-large (kotoba-lang) | independent reproduction: choice (up to 255 options), score (2-10 levels), noul in one forward pass; measured on public gold labels | 434M | Apache 2.0 | local CPU or GPU | no, a Python library | English |
| AgentJev (malevrigns) | LM head removed, candidate head scores options; published checkpoint judges whether a coding task is finished | 0.6B (Qwen3-0.6B), order-invariant candidate head | Apache 2.0 | local CPU or GPU | no, own server+client | English, Chinese |
| Jev-Style (chaoliangUNSW) | GGUF decision models, calibrated probabilities from a single token; v3 reports 79.2% on 2,000 typed decisions, takes 25,600-token inputs | 0.8B (v3); 2B (v1) | Apache 2.0 | llama.cpp, LM Studio (CPU or GPU) | no, chat completions with logprobs | 51 (v3) |
| Anarkali (ToufiqQureshi) | 68M Ettin encoder; reports 74.0% vs Jev 72.7% on public typed-decisions benchmark, within 2.6 points of Laya at a sixth of the size, lowest calibration error of the three (author-reported) | 68M | Apache 2.0 | CPU or GPU via single 273 MB ONNX file | yes, `POST /v1/systemone` | English only |
| Jeeves (PostHog) | thinks before answering: 0.935 on public JevBench items vs 0.866 Jev (0.865 vs 0.730 hard tier); ~0.3 s/request without thinking, 3.3 s median with it on one H100; Jev still leads MMLU-Pro (author-reported) | 9B (Qwen3.5-9B), LoRA + pointer head | MIT code, Apache 2.0 weights | CUDA GPU (FP8 kernel needs Hopper) | yes, local `/v1/systemone` | not stated |
| OpenJev-4B (ejhshen / Junhao Shen) | options+criteria are inputs, reordering does not change answer; SFT then RL on public OpenJevData-140k; training code included | 4B (Qwen3.5-4B) | MIT | CUDA GPU | yes, local `/v1/systemone` | not stated |

Related-but-different entry in the Awesome list: **OpenJev (DiffusionGemma)** by razorback16 — see [[openjev-and-nanojev]] (name collision!).

## When to use / when NOT to use — the stated "which fits you" rules
| Situation | Tracker (laya-ai.com) recommendation |
|---|---|
| Already call Jev, want to self-host | pick a model that serves `POST /v1/systemone`: Laya (`laya-serve`), Kev, Decider, OpenDecider, Von or OpenThai-SystemOne; existing client code just points at the new base URL |
| CPU-only servers or low latency | encoders are smallest: Laya (322M to 421M), Von (395M), GLiNER2.5-Decide (340M) |
| Highest accuracy on a large GPU | larger fine-tuned LLMs: Kev-9B / Kev-27B, Decider 35B MoE, Bespoke Nimble 9B, or Jeeves 9B if a few seconds of reasoning/request is acceptable. "Measure on your own data before switching." |
| Non-English | `laya-multilingual` (100+ languages); OpenThai-SystemOne (Thai+English); GLiNER2.5-multi-Decide (Fastino multilingual) |
| Hosted API other than Jev | Liquid AI d1: same System One API, free tier; switch by changing base URL and model name |
| No training at all | training-free: AnyJev, SemIf — read decisions from an open LLM you already run |
Closing advice (tracker): "Compare deployment, calibration, language coverage, option count and latency, and test on your own labelled data before choosing."

Layer3Labs adds a decision rule limited to three options: Jev = zero-ops managed API; Kev = open Apache 2.0, larger-parameter flexibility; Laya = lightweight self-hosted classification (details in [[laya]], [[kev]], [[jev-vs-laya]]). SOTAAZ's rules (A100 measurements): few options + English + low latency -> Laya; dozens of options -> train a small classifier (MiniLM + logistic regression, see [[minilm-embeddings]]); NanoJev is not for text classification (see [[benchmarks-and-comparisons]]).

## Numbers worth carrying
| Fact | Value | Source |
|---|---|---|
| Category named | Sep 15 2026 | tracker |
| Liquid d1 | first place on "Jev Decision Index" on Hugging Face, ahead of Jev 1.13 | tracker, citing AlphaSignal |
| OpenDecider nano (~400M) | 0.796 typed-decisions vs 0.766 Laya fine-tuned vs 0.754 Jev (author's measurements) | tracker |
| Rizzo Flow | 0.648 vs Jev 0.727 | tracker |
| Anarkali | 74.0% vs Jev 72.7% | tracker |
| Jeeves | 0.935 vs Jev 0.866 JevBench public; 0.865 vs 0.730 hard tier; 0.3 s / 3.3 s (H100) | tracker |
| Jev-Omni | 86.15% matched JevBench groups | tracker |
| Jev-Style v3 | 79.2% on 2,000 typed decisions; 25,600-token input; 51 languages | tracker |
| Kev-9B | 0.822 new-source dev accuracy vs hosted Jev 0.857 on that suite | Awesome README |

## Gotchas
- **Contradiction: Jev's typed-decisions score.** 0.727 (Laya's published benchmark per eesel; Rizzo Flow; Anarkali 72.7%) vs 0.754 (OpenDecider author's own measurements). Different measurers/samples; none controlled. See [[benchmarks-and-comparisons]].
- **Contradiction: Kev sizes/base** — tracker/Awesome say 0.8B/4B/9B(/27B) on Qwen3.5/3.8; Layer3Labs says 0.6B/4B/8B on Qwen2.5/Qwen3.5. See [[kev]].
- **"OpenJev" is ambiguous**: SemIf was formerly OpenJev (TheoLeeCJ); OpenJev-4B (ejhshen); Open-Jev (Zefan Cai); razorback16/openjev (DiffusionGemma server). See [[openjev-and-nanojev]].
- Most numbers are author-reported, on different datasets; Awesome README's own notes say Jev's training data is unknown, "so this is not a controlled architecture comparison."
- Many "compat" claims mean wire-shape compatibility, not equal accuracy; "no" rows (Nimble, Tev1, GLiNER2.5-Decide, AgentJev, Jev-Style, open-jev-deberta) need client changes.
- Decision models do not generate text, code or summaries; multi-hop synthesis over long documents is out of scope (Layer3Labs, "Workflows Unsuited for System One Decision Models").
- Tracker row for TypeSafe Jev says "Generally available and billed per token"; Layer3Labs says "usage-based per-call API pricing"; eesel quotes $0.042 per million tokens.

## Other facts (Awesome README ecosystem entries mentioning these projects)
- Jev-Switch: Rust gateway + React console + Windows Tauri app, serves a Jev-shaped `/v1/systemone`, routes through an editable graph of upstream routes with failover; v0.1.0 adapters only Vercel AI Gateway and Laya (not TypeSafe's API); request state goes to the selected upstream; README in Chinese.
- NeuroLink (juspay): TS SDK exposing `decide` as a third inference type beside `generate`/`stream`, backed by Jev or open-weights Laya via `inferenceKinds`; fail-open wrappers return `null`. Not affiliated with TypeSafe or Convai.
- Second Thought: Python SDK/CLI/dashboard capturing typed decisions from Laya, Jev or custom classifier, measuring calibration, routing uncertain cases to human review; dataset export excludes Jev decisions; Laya result from a 24-ticket example run.
- stuntd: experimental Jev-compatible proxy on Laya, records decisions in local SQLite, trains a head per decision site, forwards uncertain requests upstream; demos use rule-based teachers.
- Verdict: Apache-2.0 118M multilingual bi-encoder for choice/score/noul, temperature scaling + optional split-conformal abstention; CPU or browser (ONNX); reported score lower than Laya on the published typed-decision suite.
- Zenodo "When a Judgment Layer's Self-Reported Fields Lie": runs Laya locally, Jev and a frontier model remotely on identical items; Murphy/Brier/ECE calibration vs binary ground truth; Jev findings: verdict vocabulary reaching three values where six are documented; `sufficient` field does not separate thin from contradictory evidence; contradiction claim rests on seven live readings with no JSON artifact (stated in its errata).
- laya.tools: unofficial directory of Laya-based projects; not affiliated with ConvAI or TypeSafe; promotes a hosted Laya API.
- Laya for Node.js (receptron/laya): MIT TS client, runs Laya locally via ONNX Runtime, batches a question set per call, first use downloads ~1.7 GB weights.

## Related
[[laya]] · [[kev]] · [[openjev-and-nanojev]] · [[minilm-embeddings]] · [[benchmarks-and-comparisons]] · [[jev-vs-laya]] · [[awesome-typesafe-jev]] · [[system-one-model-category]] · [[when-to-use-which-model]] · [[topic-model-selection]]
