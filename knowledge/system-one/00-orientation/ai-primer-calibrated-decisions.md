---
title: AI Primer Calibrated Decisions
kind: concept
source: Introduction > AI primer
source_url: https://docs.typesafe.ai/introduction/machine-learning-primer
tags: [system-one, confidence]
topics: [topic-calibration]
---
# AI Primer: Calibrated Decisions (RLCD)
> Why TypeSafe trains models for calibrated decisions (RLCD) rather than generated text (RLHF/RLVR): the theory behind Jev's probabilities and confidence.

## What it is / How it works
- **Bet:** large-scale automation will be dominated by AI-to-AI and AI-to-software interactions, so the machine interface matters more than the chat interface.
- **Machine Native Intelligence** (TypeSafe's term): AI with software-like properties — structure, reliability, observability, testability, speed, consistency, low cost.
- **"Building prod, not God":** not a do-everything model; built for production systems where code needs a narrow decision it can inspect and act on. Expectation: AI automation ≈ **99% machine-to-machine, 1% human** interaction → design target shifts from responses that read well to outputs that behave predictably in software. (Manifesto: typesafe.ai/manifesto.)

### Three post-training approaches
| Approach | Expansion | What it does |
| - | - | - |
| RLHF | Reinforcement learning from human feedback | Turned pretrained models into chatbots; trains models to produce responses people prefer. Used to train InstructGPT and ChatGPT; co-invented by Diogo Almeida, cofounder of TypeSafe |
| RLVR | Reinforcement learning with verifiable rewards | Created reasoning models, strong at tasks such as mathematics, but **slower and more expensive** |
| RLCD | Reinforcement learning for calibrated decisions | TypeSafe's path: returns decisions + calibrated probabilities instead of generated text |

### RLCD output contract
- Model does not generate text; returns decisions and probabilities.
- Higher probability should correspond to a greater chance the answer is correct.
- **Calibration** (across many predictions of a well-calibrated model): outcomes assigned 0.2 occur ~20% of the time; 0.8 → ~80%; 1.0 → 100%. These are rates over **groups** of predictions, **not** a guarantee about any single answer. Guidance on when to act vs escalate: [[confidence]].

### The problems with RLHF (per the source)
- Teaches a model to say what people prefer: fine for chatbots, but can reward **sycophancy** and **confident-sounding hallucinations**.
- **Mode dropping:** preference optimization makes the model favor a style (e.g. instruction following) and lowers probability of other possible outputs (diagram: base distribution vs narrowed one after RLHF).
- Mode dropping is a milder version of **mode collapse** — classic GAN failure where the generator repeats the same kind of output because it keeps fooling the discriminator (analogy accordion with images of repeated characters).
- Warning in source: an output can be compelling to a person without being reliable enough for unattended automation; human preference and machine trustworthiness are **different optimization targets**.
- RLHF "remains a good fit for conversational models"; TypeSafe's position: production automation needs a different objective — constrained decisions and calibrated uncertainty.

## When to use / when NOT to use
- Read this to justify using probabilities/confidence as decision inputs ([[confidence-gated-routing]]). It is rationale, not a how-to.
- Don't read calibration as a per-answer guarantee.

## Worked example(s)
Only the numeric calibration illustration above (0.2/0.8/1.0). No code.

## Numbers & limits
| Claim | Value |
| - | - |
| Calibration at p=0.2 / 0.8 / 1.0 | ~20% / ~80% / 100% over many predictions |
| Expected automation split | ~99% machine-to-machine / 1% human |

## Gotchas
- Jev's own docs list structural cases where probabilities across *different questions* are not comparable ([[jev-1-13-jaggedness]], "Common-sense structural invariants"): calibration is per output, not an identity across questions.

## Related
[[system-one-model-category]] · [[jev-introduction]] · [[confidence]] · [[confidence-gated-routing]] · [[topic-calibration]]
