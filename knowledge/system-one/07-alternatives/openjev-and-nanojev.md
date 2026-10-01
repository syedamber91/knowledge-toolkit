---
title: OpenJev and NanoJev
kind: tool
source: "SOTAAZ 'Jev Alternatives Benchmarked'; laya-ai.com tracker; Awesome Jev README (AbdelStark)"
source_url: https://sotaaz.com/post/jev-alternatives-bench-en ; https://laya-ai.com/system-one-models ; https://github.com/AbdelStark/awesome-typesafe-jev
tags: [alternatives, system-one, model-limits]
topics: [topic-model-selection, topic-cost-latency]
---
# OpenJev and NanoJev
> Two very different open Jev-style projects: "openjev" = a Jev-compatible server over the 26B DiffusionGemma (heavy GPU, decent on many options), and NanoJev = a 0.6B game-decision model that is NOT a text classifier. Read this before assuming either name means what you think.

## NAME COLLISION — "OpenJev" is at least four different projects
| What | Author | What it is | Licence | Source |
|---|---|---|---|---|
| **openjev** (the one SOTAAZ benchmarked, v0.4.0) | razorback16/openjev (per Awesome README) | Jev-compatible server over DiffusionGemma 26B-A4B on the vLLM structured-read PR; NVIDIA + Apple silicon backends; optional image input | "Apache-licensed" | SOTAAZ, Awesome |
| **SemIf (formerly OpenJev)** | TheoLeeCJ | training-free; frozen open model scores typed options directly, per-workload temperature calibration | MIT | tracker, Awesome |
| **OpenJev-4B** | ejhshen (Junhao Shen) | Qwen3.5-4B + option-set decision head, SFT then RL on OpenJevData-140k, MIT, CUDA, local `/v1/systemone` | MIT | tracker |
| **Open-Jev** | Zefan Cai | LoRA adapter + scalar decision head on Qwen3.5 (2B/9B/27B), Apache 2.0, NVIDIA GPU, local `/v1/systemone` | Apache 2.0 | tracker |
(Also adjacent: OpenDecider, djev = mmastrac's DiffusionGemma reader — see [[system-one-alternatives-overview]].) When an agent sees "openjev", resolve which one from the repo owner before reasoning.

## openjev (DiffusionGemma server) — How it works
- Reads Choice/Score/Noul probabilities from **DiffusionGemma 26B** (a discrete-diffusion LLM; variant `google/diffusiongemma-26B-A4B-it`) in one read through a System One-shaped API (Awesome).
- SOTAAZ: built on the vLLM structured-read PR the author measured in an earlier post. Normally serves an **NVFP4 checkpoint**; the A100 cannot run FP4 natively so it served **bf16** weights. Docker image patches vLLM in two places: label-id cap 128 -> 512, and image attention fix (neither applies to 77 text labels; SOTAAZ ran the unpatched commit).
- Key design difference vs the vLLM "example server": openjev puts **all 77 labels in one question** named A-Z, a-z and single-token letter pairs; the example server stops at 26 options and makes you split into groups (two-stage reads). openjev also **hides the question id** from the model; the example server shows it. Past Z, label writing differs.
- Awesome README caveats: "Its NVIDIA path pins an unmerged vLLM branch, some limits differ from Jev, and answer quality needs evaluation on the reader's own tasks."
- Hardware: needs a GPU that can hold a 26B model (SOTAAZ). Tracker for djev: NVIDIA GPU with vLLM; 26B-A4B in DGX Spark recipe.

## openjev results (SOTAAZ, one A100 80GB, one request at a time, one noise draw)
| Dataset | Condition | Accuracy | Latency (median) |
|---|---|---|---|
| TREC-6 (500 q) | label names only | 66.0% | 48 ms |
| TREC-6 | names + one-line descriptions | 80.0% | — |
| BANKING77 (154 msgs) | one read, all 77 options | 66.9% | 81 ms |
| AG News (200) | — | 85.0% | — |
Compared with the vLLM example server (same weights, same vLLM commit): TREC names-only 67.0% / with descriptions 87.6% / 49 ms; BANKING77 two-stage 54.5% / 119 ms (without `--async-scheduling`); AG News 86.5%.
- Failure mode: 65 TREC questions whose answer is a person ("Who invented the telephone?"): openjev got 0, example server 1; nearly all went to `entity`; the models read the label "human" literally. A one-line description per label from the TREC taxonomy ("human: a person, a group of people or an organization") moved the example server from 335 to 438 correct (57 of 65 person questions) — about +20 points; moved openjev ~+14; moved laya ~+2 (p = 0.25).
- Paired tests (exact two-sided McNemar): on identical vLLM instance, BANKING77 openjev one read beat two-stage 33 to 12 on messages only one got right (p = 0.002); TREC with descriptions example server ahead 44 to 6 (p < 0.001) — the server matters as much as the model. `--async-scheduling` alone changed 28 of 154 example-server answers (accuracy within 2 messages; back-to-back runs with same flags reproduced every answer).
- SOTAAZ's recommendation: "Without labels, openjev at 67% is the best open option I measured, and it needs a GPU that can hold a 26B model." If evaluating any DiffusionGemma-based tool, "write the descriptions before you judge it."
- Related SOTAAZ post teasers: example server dropped from 54.5% to 31.8% on BANKING77 after adding one sentence describing the input; the author's transformers version of the two-stage read scored 68.2%. Across 8 noise draws, 77-80% of openjev's wrong answers were unanimous (so repeated-draw agreement is a weak "sureness" signal; probabilities did better but varied by task).
- Calibration was NOT measured in the main SOTAAZ benchmark: "only which option each tool ranked first."

## NanoJev — How it works
- By TianyuCodings; **0.6B** (Qwen3-0.6B with decision heads); MIT; local GPU; compact replica with an end-to-end training pipeline; "small parallel decision model" (tracker). Release tested: `unified-games-v1`. API compat: not stated. Languages: not stated.
- Trained on **game decisions**: Maze, Snake, ViZDoom ("replayable game comparisons"). Awesome: "Open 0.6B Jev-style model for one-pass action probabilities in Maze, Snake, and ViZDoom, with public checkpoint, training data ... it is specialized to those games and is not a general Jev API replacement."
- NanoJev requires a description per option; where none was given SOTAAZ fed it the label name.

## NanoJev results (SOTAAZ)
| Dataset | Names only | With descriptions | Latency |
|---|---|---|---|
| TREC-6 | 18.4% | 23.8% | 31 ms |
| BANKING77 | 20.1% | — | 73 ms |
| AG News | 31.0% ("just over chance"; 4 topics) | — | — |
Below the 27.6% you get by answering `description` for every TREC question. Verdict: "NanoJev: not for text classification. It is a game-decision model, and its own results are on games."

## When to use / when NOT to use
- openjev: only if you have a GPU for a 26B model, no labelled data, and many options (it can ask all 77 at once). Not if you can train a classifier (see [[minilm-embeddings]]) or can use hosted Jev.
- NanoJev: only for the game-like action selection it was trained for.
- SemIf/AnyJev-style training-free approaches: tracker "No training at all" use case.

## Gotchas
- Results are on one A100, one noise draw (samples: 1), not tuned; openjev's normal NVFP4 not tested.
- Different vLLM server config can swing results more than the "model" (see paired tests).
- No Jev API access for the SOTAAZ author; Jev figures there are third-party (see [[benchmarks-and-comparisons]]).

## Related
[[benchmarks-and-comparisons]] · [[laya]] · [[kev]] · [[minilm-embeddings]] · [[system-one-alternatives-overview]] · [[jev-vs-laya]] · [[topic-model-selection]]
