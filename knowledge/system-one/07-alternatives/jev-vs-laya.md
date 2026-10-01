---
title: Jev vs Laya
kind: comparison
source: "vanekt 'Laya: one more System One model'; eesel 'Laya AI'; Menon Lab 'Laya: A 421M Local Decision Model'; Layer3Labs 'Laya Alternatives'; SOTAAZ benchmark; laya-ai.com tracker"
source_url: https://vanekt.github.io/blog/laya-vs-jev/ ; https://www.eesel.ai/blog/laya-ai ; https://themenonlab.blog/blog/laya-local-system-1-decision-model ; https://www.layer3labs.io/comparisons/laya-alternatives ; https://sotaaz.com/post/jev-alternatives-bench-en ; https://laya-ai.com/system-one-models
tags: [alternatives, system-one, cost-latency]
topics: [topic-model-selection, topic-cost-latency, topic-calibration]
---
# Jev vs Laya
> Hosted, closed, zero-shot-capable Jev vs open, local, small, fine-tune-first Laya: the decision turns on privacy, option count, context length, fine-tuning appetite and volume. All figures are third-party; see [[benchmarks-and-comparisons]] for trust levels.

## What each is (per sources)
| | **Jev** (TypeSafe AI) | **Laya** (Convai Innovations) |
|---|---|---|
| Access | hosted API only; "every request goes to their server and back" | local / server / laptop; self-hosted |
| Licence | proprietary, closed | Apache 2.0, open weights on Hugging Face |
| Size | undisclosed | 421M English (ModernBERT-large), 322M multilingual (mmBERT-base) |
| Cost | usage-based; eesel quotes $0.042 per million tokens | $0 licence; compute only (eesel $0.00/M tokens) |
| Latency | 230-280 ms (vanekt); 236-276 ms (eesel); ~317 ms round trip (Menon) | 30-40 ms (vanekt); 32.8 ms p50 T4 (eesel); ~33 ms single / P50 ~9 ms batched (Menon); 23 ms A100 median (SOTAAZ) |
| Memory | n/a | ~1 GB |
| Context | ~4,000 tokens (vanekt) | 512 (vanekt) / up to 8,192 multilingual, 1,024 default (Menon) |
| Zero-shot accuracy | "sold as usable zero-shot" (eesel) | base ~0.362 near random 0.318; headline 0.766 needs fine-tune |
| Many options (50-100) | ~87% (vanekt) / 0.870 (eesel; 72-label, descriptions) / 76.3% on 77 (nibzard via SOTAAZ) | ~42% (vanekt) / 0.425 (eesel) / 37.0% default, 46.1% at 512, 59.1% shortlist (SOTAAZ) |
| Calibration (ECE) | 0.246 (eesel, third-party Jev) | 0.081 after temperature refit |
| Typed-decisions accuracy | 0.727 (Laya benchmark) or 0.754 (OpenDecider author) | 0.766 fine-tuned |
| Languages | provider-dependent; no published multilingual numbers (eesel) | 100+ checkpoint; 45 of 51 above 3x random |
| Privacy | payload goes to TypeSafe cloud | stays on your network; air-gap/HIPAA/GDPR friendly |
| Ops burden | none (Layer3Labs: "zero-maintenance routing") | host it (vLLM/ONNX Runtime), maybe fine-tune; free 2xT4 Kaggle notebook, ~4 h |

## Shared model of operation (vanekt)
Both take context + question and return: yes/no with confidence; a pick from a predefined list with confidence per option; or a number on a scale (e.g., bug severity 0-5). No explanation or reasoning. See [[primitives-overview]].

## Stated recommendations — who says what
| Source | Choose Jev when | Choose Laya when |
|---|---|---|
| **vanekt** (blog) | production now, accuracy + 4k context; or Laya only as a temporary solution fine-tuned on your data | data cannot leave the network ("the choice ... comes down to this one point, and the rest stops mattering"); independence/privacy; you can fine-tune |
| **eesel** (vendor of AI support teammate) | you want something that works zero-shot, with no GPU management or retraining (quotes HN ianbutler) | you can fine-tune and refit temperature; binary safety calls; multilingual; air-gapped; cost; but "a decision model routes a ticket, it does not resolve it" -> use their product for end-to-end resolution |
| **Layer3Labs** (consultancy) | zero-ops managed API; engineering velocity over compute cost; accept per-call billing and third-party data transit; would become more attractive with big price cuts or on-prem container appliances | lightweight specialised self-hosted classification, CPU/entry-level GPU, high-volume background jobs; "benchmark choice" for compact open weights; present judgement: at high query volumes Jev "can be cost-prohibitive" vs self-hosted Laya or Kev |
| **Menon Lab** | — (focus on Laya) | local latency "physics": a 9 ms local call beats a 317 ms HTTP request; calibrated by proper scoring rules; runs on laptop |
| **SOTAAZ** (measurer, no Jev access) | many options (Jev ~9 pts above best open on 77 options, other samples) | handful of options, English, low latency, no descriptions needed; check training-set overlap |
| **laya-ai.com tracker** | — | already on Jev and want to self-host: Laya (`laya-serve`) serves `POST /v1/systemone`, existing clients just change base URL; CPU/low-latency encoder; non-English via `laya-multilingual` |
Layer3Labs also states conditions that would change its mind (Jev price cut/on-prem; independent proof Kev 0.6B beats Laya 421M).

## The authorship/priority dispute (eesel, vanekt)
Nandakishor M. says he published the RL-trained non-autoregressive decision approach (RLCD) in a paper earlier (vanekt: early 2025; eesel: March 2025 arXiv + September 2025 follow-up) and that Jev was released without crediting it. Laya appeared three days after Jev (vanekt). HN launch >1,300 points; r/LocalLLaMA debate. eesel comments from HN: some say BERT-style models did this for years and mock "can't hallucinate"; others laud open release. eesel: "priority argument is a distraction from a strong release." Contested; no source resolves it.

## When to use / when NOT to use (synthesis, source-grounded)
- Privacy hard requirement -> Laya (or another self-hosted model) regardless of accuracy (vanekt, Layer3Labs, eesel).
- >~20 options, long inputs, zero labelled data, no fine-tune capacity -> Jev (vanekt, eesel, SOTAAZ) — OR train MiniLM+LR if labelled data exists ([[minilm-embeddings]]).
- Few-option routing, spam/phishing/guardrails, high volume -> Laya; budget CPU boxes.
- Multilingual -> Laya's Router + `laya-multilingual` (Jev has no published multilingual numbers per eesel).
- Hybrid (vanekt): start Laya locally as temporary solution and fine-tune on your own data over time; Awesome README lists gateways that mix both (Jev-Switch, NeuroLink `decide`, Second Thought) — see [[system-one-alternatives-overview]].

## Gotchas / contradictions
- **Jev's 87% on many options is likely overstated for 77 intents** (see [[benchmarks-and-comparisons]]: 0.870 is a 72-label, descriptions-supplied, 100-example pilot; 76.3% for all 77).
- **Context window:** vanekt (512) vs Menon (8,192/1,024) for Laya; unresolved.
- **Latency ratio is not a single number:** 6-7x (vanekt), 7.8x (eesel), 20-30x (Menon, throughput 86 vs 3 decisions/s).
- Jev's latency numbers are third-party (Laya author had no API access); SOTAAZ also had none.
- Laya's lead on calibration (0.081 vs 0.246) uses *refit* temperature on Laya's benchmark; Awesome: "raw calibration ... remain weak".
- Cost comparison omits GPU/ops cost for Laya and assumes Jev's token pricing ($0.042/M) [only eesel gives the number].
- Layer3Labs and eesel are commercially motivated; vanekt and Menon Lab are individuals relying on public material ("Everything below is a breakdown based on public material").

## Related
[[laya]] · [[kev]] · [[openjev-and-nanojev]] · [[minilm-embeddings]] · [[benchmarks-and-comparisons]] · [[system-one-alternatives-overview]] · [[jev-introduction]] · [[when-to-use-which-model]] · [[topic-model-selection]]
