---
title: Benchmarks and Comparisons
kind: comparison
source: "SOTAAZ 'Jev Alternatives Benchmarked'; eesel 'Laya AI'; vanekt 'Laya vs Jev'; Menon Lab Laya post; laya-ai.com tracker; Layer3Labs; Awesome Jev README"
source_url: https://sotaaz.com/post/jev-alternatives-bench-en ; https://www.eesel.ai/blog/laya-ai ; https://vanekt.github.io/blog/laya-vs-jev/ ; https://themenonlab.blog/blog/laya-local-system-1-decision-model ; https://laya-ai.com/system-one-models ; https://www.layer3labs.io/comparisons/laya-alternatives ; https://github.com/AbdelStark/awesome-typesafe-jev
tags: [alternatives, evaluation, cost-latency]
topics: [topic-model-selection, topic-calibration, topic-cost-latency]
---
# Benchmarks and Comparisons
> Every benchmark number the third-party sources give for Jev vs Laya vs open alternatives, labelled by who measured it, on what data, and how much to trust it. One independent run (SOTAAZ), many self-reported claims.

## Trust ladder
| Tier | Source | Why |
|---|---|---|
| Best available | **SOTAAZ** | ran laya, openjev, NanoJev on one A100 80GB, same public human-labelled datasets, seed 20260918, exact two-sided McNemar tests; but NO Jev API access, small samples, one noise draw, no calibration measured |
| Project self-reports | Laya's benchmark (via eesel, Menon Lab); tracker rows (Anarkali, Jeeves, Rizzo Flow, OpenDecider, Jev-Omni, Jev-Style, Kev via Awesome) | author's own data, prompts, hardware; sometimes on training mixes; "different prompts and sample sizes rather than a controlled head-to-head" (Awesome on Laya) |
| Commentary | vanekt, Layer3Labs, eesel | repeats vendor figures; Layer3Labs (consultancy) and eesel (vendor) have commercial angles; Layer3Labs says "published operational characteristics and public benchmarks" but cites no numbers |

## A. SOTAAZ independent benchmark (measured 2026-09-23)
**Setup.** One A100 80GB PCIe, driver 580.178.04; laya 0.3.7 and NanoJev `unified-games-v1` on torch 2.14.0+cu130, transformers 5.17; openjev 0.4.0 and vLLM example server on vLLM `1b3b88e` with `--async-scheduling`, canvas 64, `google/diffusiongemma-26B-A4B-it` bf16, one noise draw. One request at a time. One instruction per dataset: BANKING77 "Which intent does this banking customer's message express?"; TREC "What kind of answer does this question ask for?"; AG News "Which topic is this news article about?". Datasets: BANKING77 (PolyAI, CC-BY-4.0, 77 intents, 154 messages = 2 per intent, not in laya's training per its benchmark code); TREC (Li & Roth, 6 question types, full 500 test set, not mentioned by any tool); AG News (Zhang et al., 4 topics, 200 = 50 per topic, in laya's training mix per its docs). Samples drawn with seed 20260918.

### TREC (6 options, 500 questions)
| Tool | Label names only | Names + one-line descriptions | Median latency (names only) |
|---|---|---|---|
| MiniLM embeddings + logistic regression, trained on 5,452 | 90.4% | — | 5.7 ms (CPU) |
| laya | 86.6% | 88.6% | 23 ms |
| DiffusionGemma, vLLM example server | 67.0% | 87.6% | 49 ms |
| DiffusionGemma, openjev | 66.0% | 80.0% | 48 ms |
| MiniLM embeddings, nearest label name | 48.6% | — | — |
| NanoJev | 18.4% | 23.8% | 31 ms |
- laya (training data does not list TREC) landed 4 points under the trained classifier (38 vs 57 on questions only one got right, p = 0.06); the only tool that did not need descriptions. Typed-decisions checkpoint scored 81.8% (below base). Descriptions moved the example server ~20 pts (335 -> 438 correct), openjev ~14, laya 2 (p = 0.25). Failure: "person" questions read literally -> `entity` (openjev 0/65, example server 1/65 -> 57/65 with description). NanoJev below always-answer-`description` (27.6%).

### BANKING77 (77 options, 154 messages)
| Tool | Accuracy | Median latency |
|---|---|---|
| MiniLM embeddings + logistic regression, trained | 90.3% | 6.8 ms (CPU) |
| GPT-5.6 Terra, label only | 83.8% | 1,351 ms |
| DiffusionGemma, openjev, one read | 66.9% | 81 ms |
| laya, candidates cut to 20 by MiniLM first | 59.1% | 43 ms |
| MiniLM embeddings, nearest label name | 56.5% | — |
| DiffusionGemma, vLLM example server, two stages | 54.5% (without `--async-scheduling`, from the previous post) | 119 ms |
| laya, option budget raised to 512 tokens | 46.1% | 28 ms |
| laya, defaults | 37.0% | 27 ms |
| NanoJev | 20.1% | 73 ms |
- laya's default result predicted by its docs: 192-token shared option budget -> 77 labels at ~4 tokens each, indistinguishable. 512-token budget 57 -> 71 correct (p = 0.04); MiniLM top-20 shortlist -> 91 correct (59.1%). Nearest label name right for 87; shortlist top-1 (instruction+message embedded) 82; laya on the 20 added 4-9 over those (p = 0.57, 0.16, not significant). Typed-decisions checkpoint 39.0% defaults / 46.1% at 512.
- openjev one read beat the example server's two stages 33 to 12 on discordant messages (p = 0.002; rerun gave 82 correct for example server on openjev's instance). SOTAAZ transformers version scored 105 both one-read and nine-group two-stage; openjev with the example server's generic prompt reached 103 -> task-specific prompt not the cause of the 14-point lead; loss lies in the example server's two-stage implementation (group labelling, restated first answer, or option layout; not separated).

### AG News (4 options, 200 articles)
| Tool | Accuracy |
|---|---|
| laya | 94.5% (typed-decisions ckpt 95.0%) — measures retention, AG News is in its training mix |
| logistic regression trained on 4,000 articles | 88.5% (laya ahead 15 vs 3, p = 0.008) |
| DiffusionGemma vLLM example server | 86.5% |
| DiffusionGemma openjev | 85.0% |
| NanoJev | 31.0% (just over chance) |

### Where Jev stands in SOTAAZ (third-party only)
| Reported by | Jev result | Caveat |
|---|---|---|
| AbdelStark pilot | Jev 1.13.0: 0.910 on AG News; 0.870 on a 72-label BANKING77 variant; 100 examples each; label descriptions supplied | descriptions moved DiffusionGemma by 20 pts on TREC; 72 not 77 labels |
| nibzard benchmark | 76.3% with all 77 intents; gpt-oss-120b 81.3%, GLM-5.3 80.4% same task | different sample; Jev "mid-table" |
SOTAAZ reading: "With 77 options, then, Jev lands about 9 points above the best open alternative here, on a different sample."

### SOTAAZ closing advice
- "A handful of options, English text, low latency: laya ... Check that your task is not one it already saw in training."
- "Dozens of options: none of these replaces training a small classifier ... Without labels, openjev at 67% is the best open option I measured" (needs a 26B-capable GPU).
- "NanoJev: not for text classification."
- Two confounders: **labels are part of the prompt** (descriptions: +20 example server, +14 openjev, ~0 laya on TREC) and **the server is part of the model** (same weights, same vLLM commit, different results; `--async-scheduling` flipped 28 of 154 answers).
- Not shown: tuning, calibration, multi-request load, NVFP4 openjev, patched-Docker openjev.
- SOTAAZ follow-up teasers (not captured in detail): across 8 noise draws 77-80% of openjev's wrong answers were unanimous; laya could auto-accept 88% of TREC at 95% accuracy but 0% of BANKING77; "CLM-8B" stayed near chance on all three with label names. "Jev in 10 Minutes": 421M model 86.6% in 23 ms with a handful of options; with 77 a small trained classifier on CPU still led at 90%. Ollama post: Nimble 9B 95.6% TREC vs Jev 89.0%, but 76.0 vs 85.7 on a 4,599-question reasoning-heavy panel.

## B. Laya's published benchmark vs Jev (via eesel; Menon Lab)
Single Tesla T4; Jev figures third-party published (Convai had no API access).
| Metric | Laya | Jev |
|---|---|---|
| p50 latency, one routed question | 32.8 ms | 236-276 ms (7.8x) |
| ECE after temperature refit | 0.081 | 0.246 |
| Typed-decisions accuracy (2,000 decisions) | 0.766 (fine-tuned), beats 0.735 teacher ceiling | 0.727 |
| Base (zero-shot) typed-decisions | ~0.362 (random 0.318) | n/a |
| Languages | 45 of 51 above 3x random (routed) | no published multilingual |
| Banking77 (77 labels) | 0.425 | 0.870 |
| Cost per M tokens | $0.00 self-hosted | $0.042 |
Menon Lab version: ~86 decisions/s, P50 ~9 ms (single-call ~33 ms) vs cloud ~3 decisions/s, ~317 ms round trip, "~20-30x gap". Per-workflow: spam 0.993, phishing 0.980, guardrails 0.755-0.762 (0.931 at 50% selective coverage), RAG passage relevance 0.657, 10-way ticket routing 0.522. See [[laya]].

## C. vanekt (commentary, undated)
Jev 230-280 ms vs Laya 30-40 ms (6-7x); Laya context 512 vs ~4,000 tokens for Jev; 50-100 options without fine-tune: Laya ~42% vs Jev ~87%; both do binary splits fine.

## D. Tracker rows with benchmark claims (self-reported, different datasets; checked Oct 1 2026)
| Model | Claim |
|---|---|
| Liquid AI d1 | first place on Jev Decision Index (Hugging Face), ahead of Jev 1.13 (AlphaSignal) |
| OpenAI Decisions API | 150 ms vs 1.6 s for regular GPT-6 Luna (OpenAI figures) |
| OpenDecider nano ~400M | 0.796 typed-decisions vs 0.766 Laya fine-tuned vs 0.754 Jev (author) |
| Anarkali 68M | 74.0% vs Jev 72.7%; within 2.6 pts of Laya at 1/6 the size; lowest calibration error of the three |
| Jeeves 9B | 0.935 vs 0.866 JevBench public; 0.865 vs 0.730 hard; ~0.3 s no-think, 3.3 s median thinking, one H100; Jev leads MMLU-Pro |
| Rizzo Flow | 0.648 vs Jev 0.727 |
| Jev-Omni 12B | 86.15% matched JevBench groups |
| Jev-Style v3 0.8B | 79.2% on 2,000 typed decisions |
| Kev-9B (Awesome) | 0.822 new-source dev accuracy vs hosted Jev 0.857 on that suite |
| Verdict 118M (Awesome) | lower than Laya on published typed-decision suite |

## Contradictions / reading cautions
1. **Jev typed-decisions: 0.727 vs 0.754** (Laya benchmark/Rizzo/Anarkali vs OpenDecider author).
2. **Jev BANKING77: 0.870 / ~87% (eesel, vanekt) vs 76.3% (nibzard via SOTAAZ)**; the 0.870 is a 72-label, 100-example, descriptions-supplied variant. So claims of a 2x Jev advantage on 77 options are likely inflated; SOTAAZ puts Jev ~9 pts over best open.
3. **Laya BANKING77 default: 0.425 (eesel) vs 37.0% (SOTAAZ)**; Laya fine-tuned vs not (the 0.766 headline needs fine-tune).
4. **Laya latency: 23 ms (A100, SOTAAZ) / 32.8 ms (T4, eesel) / 30-40 ms (vanekt) / ~33 ms single, 9 ms P50 batched (Menon)** — consistent order of magnitude; differing hardware.
5. **Laya context:** 512 (vanekt) vs up to 8,192 for multilingual (Menon).
6. **Layer3Labs "superior parameter-to-accuracy efficiency"** unsupported; trained MiniLM beats Laya on BANKING77 by >20 pts ([[minilm-embeddings]]).
7. **Contamination:** laya's AG News in training; typed-decisions checkpoint tuned on its own benchmark; "measures retention, not a new task".
8. Laya's Jev comparison used third-party Jev numbers (different prompts/sample sizes) — not controlled (Awesome).
9. Latency ratios: Menon says ~20-30x (throughput-ish), eesel 7.8x, vanekt 6-7x — different metrics (throughput vs p50 latency).

## Gotchas for an agent
- Don't quote any single headline as "Laya beats Jev"; it depends on option count and fine-tuning.
- Measure on your own labelled data (tracker, Awesome, SOTAAZ all say so).
- Calibrate: Laya refit temperature; Kev ships fitted temperature; Rizzo Flow uncalibrated unless you calibrate.

## Related
[[jev-vs-laya]] · [[laya]] · [[kev]] · [[openjev-and-nanojev]] · [[minilm-embeddings]] · [[system-one-alternatives-overview]] · [[models-and-versions]] · [[jev-1-13-jaggedness]] · [[topic-calibration]]
