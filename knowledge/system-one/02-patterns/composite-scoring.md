---
title: Composite Scoring
kind: pattern
source: Patterns > Composite scoring
source_url: https://docs.typesafe.ai/patterns/composite-scoring
tags: [patterns, primitives]
topics: [topic-routing]
---
# Composite Scoring
> Break a complex judgment into independent atomic Score dimensions, normalize, then combine with weights you own in code.

## What it is / How it works
To rank items on several criteria at once: break the judgment into independent dimensions, score each separately (one request, parallel), then combine with weights controlled in code. Weights let you change relative importance without losing the nuance of individual scores, and give visibility into how the final score is built. If top-ranked candidates don't match expectations, adjust the weights.

## When to use / when NOT to use
Use for ranking/selecting top-X by several criteria, or when different consumers (roles) weight the same signals differently. Not for exact numeric interpolation from Score levels ([[jev-1-13-jaggedness]] 2c).

## Worked example — resume screening for engineering roles
Request: candidate resume + **4 Score questions**: `python_depth`, `team_leadership`, `system_design`, `generalist`. (Question definitions are a rendered component, not captured.)
- Step 1: score each dimension independently.
- Step 2: normalize each to 0–1 by **dividing by 4** (implies 5 levels, 0–4 [inference]); weight:
```python
py = ...["python_depth"].score / 4;  lead = ...["team_leadership"].score / 4
arch = ...["system_design"].score / 4;  general = ...["generalist"].score / 4
ic_score = 0.40*py + 0.10*lead + 0.40*arch + 0.10*general   # Senior IC
em_score = 0.15*py + 0.40*lead + 0.20*arch + 0.25*general   # Engineering Manager
```
Then rank candidates per role.

| Role | Python | Leadership | System design | Generalist | Sum |
| - | - | - | - | - | - |
| Senior IC | 40% | 10% | 40% | 10% | 100% |
| Engineering Manager | 15% | 40% | 20% | 25% | 100% |

## Numbers & limits
Weights above; divisor 4. Source lists benefits: Cost, Reliability, Speed ([[patterns-overview]]).

## Gotchas
- One set of dimension scores serves many weightings (no re-call per role).
- Same idea in [[how-to-build-with-system-one]] step 7 (quality = 0.4/0.4/0.2 with `1 - noul` for a negative signal) and the triage spam score. For a learned composition use probabilities as features in a classical model ([[cb-autoresearch-feature-discovery]]).

## Related
[[patterns-overview]] · [[score]] · [[speculative-fan-out]] · [[how-to-build-with-system-one]] · [[cb-reranking]] · [[topic-routing]]
