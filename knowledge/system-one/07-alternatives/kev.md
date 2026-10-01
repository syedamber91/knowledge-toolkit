---
title: Kev
kind: tool
source: "laya-ai.com tracker; Layer3Labs 'Laya Alternatives'; Awesome Jev README (AbdelStark); Menon Lab Laya post (passing mention)"
source_url: https://laya-ai.com/system-one-models ; https://www.layer3labs.io/comparisons/laya-alternatives ; https://github.com/AbdelStark/awesome-typesafe-jev ; https://themenonlab.blog/blog/laya-local-system-1-decision-model
tags: [alternatives, system-one, model-limits]
topics: [topic-model-selection, topic-calibration]
---
# Kev
> Apache-2.0, locally runnable Jev-style choice/score/noul models fine-tuned from Qwen by Jared Palmer; the "bigger, more accurate, open" self-host option next to the small encoder Laya. Reach for it when you want to self-host Jev-compatible endpoints and have a GPU (or an Apple Silicon Mac for the smallest).

**Evidence is thin.** None of the six assigned third-party articles benchmarks Kev. Facts come from the tracker (self-descriptions), Awesome README (curated, cautious), and Layer3Labs (consultancy, and its facts conflict with the others). The Menon Lab Laya post only says "Two days ago I wrote about Kev, an open-source 'decision model' ... Kev was an open reproduction built on Qwen" — the Kev post itself is not among the sources.

## What it is / How it works
- Author: Jared Palmer (`jaredpalmer/kev`). Small Jev-like models on **Qwen3.5 and Qwen3.8 bases** (tracker); fine-tuned LLMs (decoder), not an encoder.
- Each checkpoint ships a **fitted temperature** (calibration; tracker). A **fine-tune and deploy loop runs on Modal** (tracker).
- Awesome README: "Apache-licensed, locally runnable Jev-style Choice, Score, and Noul models at 0.8B, 4B, and 9B, with released weights, training code, a System One-compatible server, frozen evaluation suites, and a playground." Also indexed on the Awesome live site as "Local Jev-style models with released weights and evaluation suites; compare on your own task."
- API: "Yes, the TypeSafe SDK works unchanged" (tracker); Layer3Labs: "wire-compatible schema", "maintains strict wire compatibility with the standard System One request contract, allowing teams to swap endpoints with minimal code changes". See [[sdk-python]], [[http-api-reference]].
- Languages: not stated (tracker).

## Numbers & limits
| Item | Value | Source |
|---|---|---|
| Sizes | 0.8B / 4B / 9B / 27B | tracker (lists 27B; Awesome lists 0.8B/4B/9B) |
| Sizes (conflicting) | 0.6B / 4B / 8B | Layer3Labs |
| Base | Qwen3.5 + Qwen3.8 (tracker); Qwen2.5 + Qwen3.5 (Layer3Labs) | conflict |
| Licence | Apache 2.0 | tracker, Layer3Labs, Awesome |
| Hardware | Apple Silicon Mac (0.8B) up to one 80 GB GPU (27B) | tracker |
| Hardware (Layer3Labs) | 0.6B runs on a single consumer workstation incl. Apple Silicon Mac or entry-level GPU instance; 4B/8B need dedicated GPU memory | Layer3Labs |
| Accuracy | Kev-9B 0.822 "new-source development accuracy" vs hosted Jev 0.857 on that suite | Awesome README (author-reported) |
| Highest-accuracy shortlist | Kev-9B / Kev-27B listed among "larger fine-tuned LLMs" for large-GPU accuracy | tracker |
| Cost | inference compute only | Layer3Labs |

## When to use / when NOT to use
- Tracker: "You already call Jev and want to self-host" -> Kev is one of the servers that accept existing client code by changing base URL; "Highest accuracy on a large GPU" -> Kev-9B/27B among options; "measure on your own data before switching".
- Layer3Labs verdict: Kev "best alternative for teams that prioritize the Apache 2.0 open-source framework and require variable parameter sizing"; "ideal choice for teams that want an open-source foundation with modular parameter tiers for custom fine-tuning"; good for local experiments on consumer hardware and domain fine-tuning. Teams "must budget for the engineering time required to serve and scale these models locally."
- Layer3Labs would make Kev its *default self-hosted* recommendation only if independent contributors publish verified benchmarks showing Kev's 0.6B consistently beats Laya's 421M across standardized classification tasks. Today it says Laya "demonstrates superior parameter-to-accuracy efficiency" (unsubstantiated by the numbers in these sources — see [[benchmarks-and-comparisons]]).
- Not for: conversational/creative generation (Layer3Labs, applies to all System One models).

## Gotchas / contradictions
- **Layer3Labs vs everyone else on sizes, bases and authorship.** Layer3Labs: 0.6B/4B/8B; Qwen2.5+Qwen3.5; "developed independently by the open-source community". Tracker/Awesome: 0.8B/4B/9B(+27B); Qwen3.5+Qwen3.8; author Jared Palmer. Prefer tracker + Awesome (project-sourced); treat Layer3Labs figures as suspect. Both agree Kev is NOT from Convai (Laya's maker) and is Apache 2.0.
- Awesome README caveat: "Jev's training data is unknown, so this is not a controlled architecture comparison; test calibration and option order on your own data before setting a decision threshold."
- Chronology (Menon Lab): Jev -> Kev -> Laya ("naming is getting sillier by the week"); Kev post was two days before Laya post.
- No latency numbers for Kev in any source; no independent benchmark among these six sources [inference: gap, worth measuring if Kev is considered].

## Related
[[laya]] · [[openjev-and-nanojev]] · [[jev-vs-laya]] · [[system-one-alternatives-overview]] · [[benchmarks-and-comparisons]] · [[topic-model-selection]]
