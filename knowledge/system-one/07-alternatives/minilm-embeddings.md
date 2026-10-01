---
title: MiniLM Embeddings
kind: reference
source: "SOTAAZ 'Jev Alternatives Benchmarked' (only substantive source); Awesome Jev README and other five assigned sources have no MiniLM mentions"
source_url: https://sotaaz.com/post/jev-alternatives-bench-en
tags: [alternatives, retrieval-rerank, model-limits]
topics: [topic-model-selection, topic-retrieval-rerank]
---
# MiniLM Embeddings
> A small sentence-embedding model used in the SOTAAZ benchmarks as (a) a trained-classifier baseline, (b) a nearest-label-name zero-shot baseline, and (c) a candidate shortlister in front of Laya. It is NOT a typed, calibrated System One decision model — it embeds text; it does not natively answer choice/score/noul questions with calibrated probabilities.

**Evidence status.** Sources mention MiniLM only in passing, inside SOTAAZ's benchmark tables and prose. `grep -i minilm` over the Awesome README, the laya-ai.com tracker, Layer3Labs, eesel, vanekt and Menon Lab returns nothing. The exact MiniLM checkpoint (e.g. which sentence-transformers variant), parameter count, embedding dimension and training are **not stated in the sources**; anything beyond below is marked `[inference]`.

## Role (what the sources say it does)
1. **Baseline classifier: "MiniLM embeddings + logistic regression", trained on labelled data.** Embed the text with MiniLM, fit a logistic regression on the labelled examples. CPU-only.
2. **Zero-shot baseline: "MiniLM embeddings, nearest label name."** Embed message and each label name; pick the closest label. No training.
3. **Shortlister in front of a decision model.** Laya's own documentation recommends cutting a long option list to ~20 candidates with an embedding model first (SOTAAZ: "Its other recommendation, cutting the list to 20 candidates with an embedding model first"). In SOTAAZ's run the shortlist embeds the *instruction along with the message*.
Role summary: embedding model for similarity/shortlisting and for a cheap trained classifier head; no typed question schema, no per-option probabilities in the System One sense [inference: logistic regression does output class probabilities, but SOTAAZ says it did not measure calibration, "only which option each tool ranked first"].

## Numbers (all SOTAAZ, one A100 box for GPU tools; MiniLM rows are CPU)
| Task | MiniLM variant | Accuracy | Median latency |
|---|---|---|---|
| TREC-6, 500 q | embeddings + logistic regression trained on 5,452 TREC examples | 90.4% | 5.7 ms (CPU) |
| TREC-6 | nearest label name | 48.6% | — |
| BANKING77, 154 msgs (2 per intent) | embeddings + logistic regression, trained | 90.3% | 6.8 ms (CPU) |
| BANKING77 | nearest label name | 56.5% (87 of 154 correct) | — |
| BANKING77 | shortlist's own top candidate (instruction embedded with message) | 82 of 154 correct [inference: ≈53.2%, computed] | — |
| BANKING77 | laya on the 20 MiniLM candidates | 59.1% (91 of 154) | 43 ms |
| AG News, 200 articles | logistic regression trained on 4,000 articles | 88.5% | — |
Comparison points: on BANKING77 MiniLM+LR (90.3%) beat GPT-5.6 Terra label-only (83.8%, 1,351 ms), openjev (66.9%), laya variants (37.0-59.1%), vLLM example server (54.5%), NanoJev (20.1%). On TREC, MiniLM+LR 90.4% vs laya 86.6%/88.6%, DiffusionGemma servers 67.0/66.0 names-only (87.6/80.0 with descriptions).

## Findings the sources draw
- **"Dozens of options: none of these replaces training a small classifier. With a few thousand labelled examples, MiniLM plus logistic regression beat every tool on BANKING77 by more than 20 points"** (SOTAAZ). On TREC it "was level with laya once laya had descriptions (32 against 41, p = 0.35)" (paired discordant counts as stated; direction not spelled out).
- **Shortlisting does most of the work.** Laya on 20 candidates added only 4 to 9 messages over the embedding model's own picks (87 nearest-label; 82 shortlist top-1); differences not significant (p = 0.57 and 0.16). "Most of that row is MiniLM's work."
- Shortlist rescue of Laya: 57 correct (defaults, 192-token shared budget) -> 71 with 512-token budget (p = 0.04) -> 91 with MiniLM top-20 shortlist.
- Speed: 5.7-6.8 ms on CPU vs laya 23-43 ms GPU and API models 1.35 s — i.e. the embedding route is the fastest tool in the table.

## When to use / when NOT to use
- Use: many classes (dozens+) AND a few thousand labelled examples -> train MiniLM+LR; many options and a decision model with a small option budget -> shortlist to ~20 first; need CPU-only sub-10 ms classification.
- Don't: no labels and no descriptions (nearest-label-name is weak: 48.6% TREC, 56.5% BANKING77); when you need typed question schemas, score/noul primitives, or calibrated confidences out of the box — use a System One model ([[laya]], [[kev]], hosted Jev) and calibrate on your data ([[confidence]]).
- Relation to Jev's own patterns: pre-shortlisting is the same idea as [[cb-reranking]] style flows [inference: linked for context only; these sources do not connect them].

## Gotchas
- Measurement limits: one box, small samples (154/500/200), one instruction per dataset; MiniLM-LR was trained on the dataset's own training split (5,452 TREC; 4,000 AG News) — a trained baseline vs mostly zero-shot tools, so the comparison is not apples-to-apples. SOTAAZ states this framing explicitly ("a classifier trained on the full TREC training set").
- Contradiction/limit: Layer3Labs says Laya shows "superior parameter-to-accuracy efficiency on standard benchmarks" — SOTAAZ's trained MiniLM baseline contradicts that for BANKING77 (>20 points ahead) and nearly ties on TREC.
- Which MiniLM, embedding size, and training details unknown from sources. [inference] Sentence-transformer MiniLM models are generally ~20-120M-parameter distilled encoders; not verified here — check the SOTAAZ repo/posts before quoting.
- Related posts by SOTAAZ (teasers only, content not captured): "Jev's Speed Claims: Benchmarking Label-Only Alternatives on BANKING77" (MiniLM + LR 90.3% at 6.8 ms CPU).

## Related
[[laya]] · [[benchmarks-and-comparisons]] · [[openjev-and-nanojev]] · [[system-one-alternatives-overview]] · [[cb-reranking]] · [[topic-retrieval-rerank]] · [[topic-model-selection]]
