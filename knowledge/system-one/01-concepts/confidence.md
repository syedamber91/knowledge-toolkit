---
title: Confidence
kind: concept
source: Confidence
source_url: https://docs.typesafe.ai/confidence
tags: [confidence, system-one]
topics: [topic-calibration, topic-routing]
---
# Confidence
> A 0-1 summary of how peaked an answer's probability distribution is, returned on every Choice and Score answer; use it to decide act / confirm / escalate.

## What it is / How it works
- Choice and Score answers include `probabilities` (distribution over options or levels). The **shape** says how certain the model is: concentrated on one outcome = confident; spread out = uncertain.
- `confidence` collapses that shape to one number 0..1 so you can threshold without doing the math. **Noul answers carry none** (a single probability describes it, see [[noul]]).
- It is a statistic **derived from `probabilities`**; TypeSafe computes it and returns it on every Choice/Score answer. The exact formula is not given on this page (only "how spread/peaked"); an interactive `ConfidenceExplorer` widget exists on the page but is not in the source dump. `[inference]` do not assume entropy vs max-probability; check observed pairs below.
- "A solid default": a convenient measure for most uses, but you are not locked in -- the full `probabilities` are returned so you can compute a different measure. Pros/cons of alternatives are promised for a separate cookbook (link not yet added in the source).
- Meaning by type: Choice low = no option clearly wins; Score low = levels ambiguous, multi-dimensional, or state lacks enough information.

Observed (probabilities -> confidence) pairs from the docs, useful as calibration anchors:
| Primitive | probabilities | confidence |
| - | - | - |
| Choice | 1.0 / 0 / 0 | 1.0 |
| Choice | 0.84 / 0.16 / 0 | 0.76 |
| Choice | 0.74 / 0.26 / 0 / 0 / 0 | 0.67 |
| Choice | 0.61 / 0.35 / 0.04 | 0.42 |
| Choice | 0.40 / 0.34 / 0.24 / 0.02 | 0.20 |
| Choice (API ref) | 0.88 / 0.12 / 0.0 | 0.81 |
| Score | 0 / 0.57 / 0.43 | 0.35 |
| Score | 0 / 0.72 / 0.28 | 0.58 |
| Score | 0 / 0.76 / 0.24 | 0.64 |
| Score | 0 / 0.89 / 0.11 | 0.84 |
| Score | 0 / 0.91 / 0.09 | 0.87 |
| Score (API ref) | 0 / 0.95 / 0.05 | 0.92 |
| Score | 0.45 / 0.55 / 0 (numbers-only levels) | 0.33 |

## "I don't know" is a useful signal
A system that can't express honest uncertainty can't be trusted. Confidence is the built-in way for the model to say "I'm not sure about this one", enabling different behaviour per certainty level -- the foundation for reliable systems.

## Three paths
| Range | Behaviour |
| - | - |
| High | Act automatically; clear read, no human involvement |
| Medium | Proceed with caution: ask user to confirm, flag for review, or gather more info |
| Low | Do not act: route to a human, request clarification, or fall back to another system (insufficient information or question is a bad fit) |
Where you draw boundaries depends on the stakes. Same three-way split applies to Noul via the probability itself ([[noul]]).

## Thresholds scale with risk
A confidence threshold is not one number; gate different actions in one system differently. Page example (Choice `action`: `check_balance` "View account balance", `approve_transfer` "Approve the pending withdrawal request", `support` "Get help with an issue"):
```python
if confidence < 0.5:            route_to_human(user_message)       # genuinely unsure; don't guess
elif choice == "check_balance": show_balance(account_id)           # low stakes, recoverable
elif choice == "approve_transfer":
    if confidence > 0.9: confirm_then_execute(account_id)          # high stakes + high confidence
    else:                ask_user_to_confirm(account_id)           # high stakes, moderate confidence
```
The **0.5 floor** catches anything reported as genuinely uncertain; above it, the bar for acting without confirmation is higher for a destructive operation than for a read-only one. Your code encodes the risk tolerance.

## Numbers & limits
| Item | Value |
| - | - |
| Range | 0 to 1 |
| Present on | Choice, Score (not Noul) |
| Example floor | 0.5 (route to human below) |
| High-stakes act threshold | >0.9 (with confirmation) |
| Other thresholds elsewhere in docs | 0.3 manual triage and 0.5 ask-customer in [[choice]] |

## Gotchas
- **Correct thresholds depend on domain and the model's performance on your use case: start conservative, test on your own data, adjust.** (Page note.) No universal values are given.
- Confidence 1.0 describes the returned distribution, not correctness ([[score]]).
- Same Score can hide different distributions; read `probabilities` too.
- Low confidence on a Score: levels overlap / multi-dimensional / thin state -> fix the question, not just the threshold.

## Related
[[primitives-overview]] -- [[choice]] -- [[score]] -- [[noul]] -- [[confidence-gated-routing]] -- [[cb-classification-using-confidence]] -- [[ai-primer-calibrated-decisions]] -- [[topic-calibration]] -- [[topic-routing]]
