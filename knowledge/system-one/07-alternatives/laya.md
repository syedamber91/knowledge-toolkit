---
title: Laya
kind: tool
source: "eesel AI 'Laya AI: the open 33ms decision model'; Menon Lab 'Laya: A 421M Local Decision Model'; vanekt 'Laya: one more System One model'; Layer3Labs 'Laya Alternatives'; SOTAAZ benchmark; laya-ai.com tracker; Awesome Jev README"
source_url: https://www.eesel.ai/blog/laya-ai ; https://themenonlab.blog/blog/laya-local-system-1-decision-model ; https://vanekt.github.io/blog/laya-vs-jev/ ; https://www.layer3labs.io/comparisons/laya-alternatives ; https://sotaaz.com/post/jev-alternatives-bench-en ; https://laya-ai.com/system-one-models ; https://github.com/AbdelStark/awesome-typesafe-jev
tags: [alternatives, system-one, model-limits]
topics: [topic-model-selection, topic-calibration, topic-cost-latency]
---
# Laya
> Open (Apache 2.0), local, non-autoregressive encoder from Convai Innovations that answers Jev-style choice/score/noul questions in one forward pass. Fast and private, but weak zero-shot and with many options; reach for it for few-option English/multilingual routing you will fine-tune.

**Source-bias map.** eesel = vendor selling an AI support teammate (positive on calibration; does flag the fine-tune caveat). Menon Lab = enthusiast explainer (leans on Laya's own claims; physics-of-latency argument). vanekt = personal blog (sceptical-balanced). Layer3Labs = consultancy lead-gen page (praises Laya's "parameter-to-accuracy efficiency"). SOTAAZ = independent measurement on A100 (most neutral, but small samples). laya-ai.com = tracker whose publisher is unnamed [inference: domain suggests ties to Laya, unverified]. Most headline benchmarks are Laya's OWN (eesel: "Jev figures third-party published, since Convai had no API access"). Awesome README: "its Jev comparisons use different prompts and sample sizes rather than a controlled head-to-head, and raw calibration and some languages remain weak."

## What it is / How it works
- Maker: Convai Innovations; builder Nandakishor Mukkunnoth (eesel) / "Nandakishor M." (vanekt) / GitHub `NandhaKishorM/laya`. Tagline "decisions, not text" (eesel). Quote of builder (eesel): "Not every AI problem requires an autoregressive chatbot."
- **Architecture (eesel):** bidirectional encoder reading the whole input at once, scores options rather than writing them. Every option is packed with its own `[MASK]` token; the model reads the hidden state at that marker to produce a logit, then softmaxes over the question's options. Answer space defined at request time, so new schemas need no retraining. English checkpoint = ModernBERT-large (421M) + small decision head.
- **Menon Lab's explanation:** non-autoregressive / prefill-only; one pass over input, answers read off dedicated output heads (one small classifier per question type); all answers for all questions emitted in a single pass; no decoding/JSON/regex.
- **Question types:** `choice` (probability over N named options), `score` (probability over ordered scale, e.g. 0-3), `noul` (yes/no, calibrated P(true) 0.0-1.0). See [[primitives-overview]], [[choice]], [[score]], [[noul]].
- **Router (all but Layer3Labs):** inspects script/language and picks checkpoint (English -> English; else `laya-multilingual`). eesel: script detection "under half a millisecond". `Router(preload=True)` keeps every checkpoint resident, avoiding a 7-10 s cold reload on language switches.
- **Training (RLCD):** reinforcement learning against strictly proper scoring rules (log-loss, Brier). Menon: a proper scoring rule is maximised only when the model reports its true probability, so honest calibrated probabilities are forced. eesel quote of builder: "Naive RL maximizes accuracy by destroying calibration"; LLM-stated "confidence: 0.95" has "zero mathematical calibration behind it". After training, calibration temperatures are fitted (rescaling so reported probabilities match observed frequencies). SOTAAZ: "trained with reinforcement learning against proper scoring rules", tested version 0.3.7.
- **Priority claim (eesel, vanekt):** builder says he published the non-autoregressive RL-trained approach earlier — eesel: March 2025 arXiv paper + September 2025 follow-up; vanekt: "back in early 2025" paper on RLCD. Claims TypeSafe released Jev without crediting it; vanekt: Laya was put together "in a couple of days", appeared three days after Jev. HN reaction (eesel): launch hit >1,300 points; r/LocalLLaMA debate on who copied whom. eesel's verdict: priority fight "a distraction from a strong release".
- Popularity: eesel says GitHub >9,000 stars; vanekt "thousands of stars". (SOTAAZ mentions one alternative project with 18,000 stars without naming it — do not attribute.)

## Checkpoints (eesel table; tracker agrees on sizes)
| Checkpoint | Backbone | Params | Best at |
|---|---|---|---|
| `convaiinnovations/laya` | ModernBERT-large | 421M | English guardrails, email triage |
| `laya-multilingual` | mmBERT-base | 322M | 100+ languages, ~2.2x faster |
| `laya-typed-decisions` | ModernBERT-large | 421M | the four typed-decisions workflows (0.766 acc) |
Layer3Labs lists only two "official sizes": 421M English and 322M multilingual. English root model "collapses outside Latin scripts": 0.000 accuracy on Khmer while reporting 0.952 confidence (eesel, 51-language sweep) — confidence gating cannot save you; hence the Router.

## Install / run (Menon Lab, eesel)
```python
pip install laya
from laya import Router
router = Router()  # downloads a checkpoint on first use
r = router.predict(state, questions)  # r["answers"]["department"]["choice"]
```
Python 3.10+, ~1 GB RAM, CPU-only works (GPU faster). Extras: `laya[serve]` (HTTP server, `laya-serve`), `laya[mcp]`, `laya[langchain]`, `laya[onnx]` (ONNX Runtime), `laya[fast]` (GPU fast path). Question shape in Menon's example: `{"type":"choice","instructions":...,"criteria":{...}}`, `{"type":"score","criteria":["not urgent","soon","blocking"]}`, `{"type":"noul"}`.
Hardware (sources): CPU / entry-level GPU (Layer3Labs; "no data-center GPUs"); tracker: CPU, CUDA, Apple Silicon. Layer3Labs says teams "must configure inference engines such as vLLM or ONNX Runtime themselves" and need "meaningful engineering investment" without MLOps staff.

## Fine-tuning
Menon Lab: zero-shot base English checkpoint 0.362 on Laya's 2,000-decision benchmark; fine-tuned 0.766 ("roughly double"). Provided Kaggle notebook runs the whole loop on free 2xT4 GPUs in ~4 h: build dataset, train, fit calibration temperatures, evaluate, push to Hub. eesel: random baseline 0.318; "Treat Laya as a fast foundation to specialize, not a zero-shot oracle", refit temperature on your own data before trusting confidences.

## Numbers & limits (with source + who measured)
| Item | Value | Source / caveat |
|---|---|---|
| Latency p50, one routed question | 32.8 ms on one Tesla T4 vs Jev 236-276 ms = "7.8x" | eesel, Laya's own benchmark; Jev figure third-party |
| Latency, local single call | 30-40 ms (~1 GB) vs Jev 230-280 ms => "6 to 7 times" | vanekt |
| Latency / throughput | ~86 decisions/s, P50 ~9 ms (single-call ~33 ms) vs cloud ~3 decisions/s, ~317 ms; "~20-30x gap" | Menon Lab; reported benchmark. [inference] 86/3 ≈ 29x throughput; 317/9 ≈ 35x, 317/33 ≈ 9.6x latency |
| Measured latency | 23 ms median (TREC, A100), 27 ms (BANKING77 defaults), 28 ms (512 budget), 43 ms (with 20-candidate shortlist), AG News n/a | SOTAAZ, one request at a time |
| Memory | ~1 GB inference | Menon, vanekt |
| Context | 512 tokens (vs ~4000 for Jev) | vanekt |
| Context | multilingual checkpoint reads up to 8,192 tokens, ships defaulting to 1,024, raise `max_len`; ~6,300-token input ~2.5 s on an Apple GPU vs ~0.18 s for short input | Menon |
| Option token budget | all options share a 192-token budget by default; 77 labels -> ~4 tokens each; recommended fix 512 | SOTAAZ ("laya's own documentation predicts") |
| Options before degradation | "degrade past about 20 options at the default token budget"; 3-4 tokens per option at 77 labels | eesel |
| Calibration (ECE) | 0.081 after temperature refit vs Jev 0.246 ("3x better") | eesel (Laya's benchmark) |
| Typed-decisions accuracy | 0.766 fine-tuned vs Jev 0.727; beats 0.735 "teacher ceiling" | eesel; OpenDecider's author measures Jev at 0.754 instead (tracker) |
| Languages | 45 of 51 above 3x random when routed; no published Jev multilingual numbers | eesel |
| Cost | Apache 2.0, $0.00 per million tokens self-hosted vs Jev $0.042/M tokens | eesel; "only cost is the GPU or CPU" |
| Python client size | Laya for Node.js (ONNX) downloads ~1.7 GB on first use | Awesome README |

Per-workflow accuracy (eesel, project-reported):
| Workflow | Accuracy |
|---|---|
| Email spam filtering | 0.993 |
| Phishing detection | 0.980 |
| LLM guardrails / jailbreak detection | 0.755-0.762 (0.931 at 50% selective coverage) |
| RAG passage relevance | 0.657 |
| Support ticket routing, 10-way | 0.522 |
Reading: "binary safety calls are excellent; the wide, fuzzy classification is where it needs the fine-tune."

Independent measurements (SOTAAZ, see [[benchmarks-and-comparisons]]): TREC-6 86.6% (names only) / 88.6% (with descriptions), typed-decisions checkpoint 81.8%; BANKING77 37.0% defaults, 46.1% at 512 tokens, 59.1% with MiniLM shortlist to 20; AG News 94.5% (typed-decisions 95.0%) but AG News is in Laya's training mix. Calibration (SOTAAZ follow-up teaser): laya could auto-accept 88% of TREC at 95% accuracy and 0% of BANKING77.

## When to use / when NOT to use
Use (sources): few options (<~20), English or routed multilingual, low latency, privacy/air-gapped (HIPAA/GDPR per eesel), CPU boxes, high-volume background jobs, binary safety calls (spam, phishing, guardrails), when you can fine-tune. SOTAAZ: "A handful of options, English text, low latency: laya. 23 ms ... no descriptions needed". Check the task was not in its training data.
Do NOT: zero-shot with 50-100 options (vanekt: ~42% vs Jev ~87%; eesel: 0.425 vs 0.870), long inputs (512-token context claim), when you want it to "just work" without fine-tune or GPU management (eesel quoting HN user ianbutler), tasks needing generation or multi-hop synthesis (Layer3Labs), when you need the decision *acted on* (eesel's pitch: decision model routes a ticket, does not resolve it).
Community camps (vanekt): (1) Laya for independence/privacy, run locally rather than send customer emails/invoices to a cloud; (2) without fine-tuning Laya is behind on accuracy + context, so for production now Jev is more reliable — or use Laya as temporary solution and fine-tune over time. Confidentiality is called "the one point" deciding it for closed corporate apps.
HN quotes (eesel): critical — requiring fine-tune "put Laya in a whole different category vs Jev" (cjalmeida); pro — "knock out any arbitrary classification problem in minutes instead of in a week" (soerxpso).

## Gotchas
- **Contradiction: context window.** vanekt 512 tokens; Menon 8,192 max (1,024 default) for multilingual; SOTAAZ 192-token option budget (separate concept: budget for options, not input). Unresolved by sources [inference: may be per-checkpoint/version differences; not confirmed].
- **Contradiction: Jev's BANKING77 score.** vanekt "~87%" / eesel 0.870 vs SOTAAZ: 0.870 is a 72-label variant, 100 examples, label descriptions supplied (AbdelStark pilot, Jev 1.13.0); nibzard reports 76.3% with all 77 intents. So the "Laya 42% vs Jev 87%" gap is likely overstated.
- Laya BANKING77 default: eesel 0.425 vs SOTAAZ 37.0% (different samples; SOTAAZ 154 messages).
- Headline 0.766 is post-fine-tune; base 0.362 (near random 0.318). eesel: "the caveat everyone missed".
- Typed-decisions checkpoint scored BELOW base checkpoint on TREC (81.8% vs 86.6%) and BANKING77 (39.0/46.1) — SOTAAZ.
- AG News result "measures retention, not a new task" (in Laya's training mix).
- "Can't hallucinate" (eesel FAQ): true only within output space — it never emits text, so malformed/invented categories are impossible by construction, but it can still be wrong; confidence matters more than the marketing line. HN commenter (prometheus1992) mocked the "can't hallucinate" pitch.
- Layer3Labs says Laya "demonstrates superior parameter-to-accuracy efficiency" — SOTAAZ shows a trained MiniLM + logistic regression beating it on BANKING77 by >20 points and nearly matching on TREC. Treat Layer3Labs claim as unmeasured.
- Layer3Labs: no intermediate parameter sizes between its two builds.
- Pricing page: eesel notes own product ~40 cents per resolved ticket (irrelevant to Laya; vendor plug).

## Related
[[jev-vs-laya]] · [[kev]] · [[openjev-and-nanojev]] · [[minilm-embeddings]] · [[benchmarks-and-comparisons]] · [[system-one-alternatives-overview]] · [[confidence]] · [[confidence-gated-routing]] · [[topic-calibration]]
