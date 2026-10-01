---
title: Score Primitive
kind: reference
source: Score; API reference
source_url: https://docs.typesafe.ai/primitives/score
tags: [primitives, evaluation]
topics: [topic-calibration, topic-classification]
---
# Score Primitive
> Rate content against ordered, descriptive levels; returns a fractional position (probability-weighted level number), per-level probabilities, a legend and confidence. Use for spectra (severity, frustration, experience) and as building blocks for weighted composites.

## What it is / How it works
**Request fields** (per question): `type: "score"`; `instructions` (what is being rated); `criteria` = **ordered array** of level descriptions from low end to high end. "Should have at least two levels; the API accepts up to 10." Each entry may be string/object/array ([[advanced-structure]]). Question ID is yours, not sent to the model.

**Levels**: a level's number is its **position in `criteria` starting at 0** (array order *is* the numbering). The model gets **only the descriptions** (no numbers, no neighbours); **each level is judged on its own** against the state.

**Response fields**: `type`; `probabilities` (per-level probability keyed by level number **as a string**, sums to 1); `score` = sum(level_number x probability) -> position on 0..top_level, can land between levels; `legend` (level number -> description); `confidence` (0-1 from how spread `probabilities` is, see [[confidence]]). Plus top-level `model`, `usage`.
Math from the page: 0x0.0 + 1x0.57 + 2x0.43 = **1.43**.
Python SDK: `ScoreAnswer` has typed `score`, `confidence`, `probabilities`, `legend`; **the SDK keys `probabilities` and `legend` by integer level** rather than string.

Python request:
```python
Score(instructions="How severe is the reported issue?",
      criteria=["Cosmetic; no impact to functionality",
                "Broken or degraded feature, but workaround exists",
                "Blocking issue; no workaround exists"])
```
State "The export button crashes the settings page in Safari. It works in Chrome, but a few of our customers only use Safari." -> `score 1.43, confidence 0.35, probs {0:0.0, 1:0.57, 2:0.43}`, usage 332/18, model jev-1.13.0. Reading: model split between 1 and 2, leaning 1 (Chrome is a workaround for most, not for Safari-only customers).

## When to use / when NOT to use
- Use for a position on a spectrum describable in steps (bug severity, customer happiness, Python experience).
- Not: unordered categories -> [[choice]] (or several [[noul]]); yes/no -> Noul. If "there is no in-between at all", use Choice or split into Nouls. Comparison [[primitives-overview]].
- Split multi-factor judgments into several Scores (below).

## Reading a Score -- table of recorded behaviour (severity question)
| State | score | confidence | L0 | L1 | L2 |
| - | - | - | - | - | - |
| Export button misaligned by a few pixels on the settings page | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| PDF export button does nothing; CSV works, convert myself, takes ages | 1.0 | 1.0 | 0.0 | 1.0 | 0.0 |
| PDF export spinner never finishes; some say CSV works, others fails | 1.11 | 0.84 | 0.0 | 0.89 | 0.11 |
| Export crashes settings page in Safari; works in Chrome; some customers only Safari | 1.43 | 0.35 | 0.0 | 0.57 | 0.43 |
| Nobody on team can log in since this morning, 500 on every attempt | 2.0 | 1.0 | 0.0 | 0.0 | 1.0 |

Rules of thumb stated:
- Confidence 1.0 = distribution all on one level; **describes the model's answer, not a guarantee of correctness**.
- Score is a **probability-weighted mean of level numbers**; more weight on level 2 raises it. It does **not** measure e.g. the fraction of customers without a workaround.
- **Different distributions can give the same score**: 1.0 can be all on L1, or half on L0 and half on L2 -> read `probabilities` + `confidence` too.
- A fractional score is a position: rank reports by it, or round to nearest level when code needs one outcome (entity-alignment cookbook rounds to nearest level: [[cb-entity-alignment]]).
- Low confidence on a Score usually means: levels overlap for this state, question measures more than one thing, or state doesn't say enough.

## Writing good levels
- **Describe situations, not degrees.** "Broken or degraded feature, but workaround exists" gives something to match; "Moderately severe" doesn't. Check answers against known examples; higher confidence alone does not show a description is better.
- **Levels are numbers-blind.** Numbers in descriptions/instructions don't help ("worse than the previous level" means nothing). Experiment on the misaligned-button report: instructions "Rate severity from 0 to 2, where 2 is worst", criteria `["0","1","2"]` -> **score 0.55, confidence 0.33, probs 0:0.45, 1:0.55, 2:0.0**. The same report with the three descriptive levels -> **0.0 at confidence 1.0**.
- Use as many levels as you can describe **distinctly**, up to 10. Three is fine. Don't add levels you can't describe distinctly.
- **One dimension per Score.** "punctual and smart and experienced" = three things; an input high on one and low on another can't be placed; confidence drops. Split and combine in code.
- **Give a rare extreme its own level** if you act on it differently: e.g. sentiment ending at "very angry" can add "abusive or threatening", else both may score near the top.
- Test levels on your own data: two wordings of the same scale can behave differently.

## Splitting a complex judgment into several Scores (composite scoring)
Send all Scores in one request (parallel; few extra tokens). Weights live in your code; adjust when the combined result disagrees with team judgment. Pattern: [[composite-scoring]].

Example: spinner ticket (with more context; the ticket text itself is in a widget not in the dump) with three Scores.
- `severity` levels: Cosmetic / Broken-but-workaround / Blocking (3 levels).
- `frustration`: "Calm, just stating facts" / "Frustrated but civil" / "Very angry, strong language or threatening to leave" (3).
- `report_quality`: "No detail; just says something is broken" / "Names the feature but no steps or environment" / "Steps to reproduce or environment, but not both" / "Steps to reproduce and environment" (4).

Response (usage 468 in / 43 out, jev-1.13.0):
| Q | score | confidence | probs |
| - | - | - | - |
| severity | 1.24 | 0.64 | 0:0.0, 1:0.76, 2:0.24 |
| frustration | 1.28 | 0.58 | 0:0.0, 1:0.72, 2:0.28 ("third time" and "I'm done" shift some mass up) |
| report_quality | 3.0 | 1.0 | 3:1.0 (steps and browser version both stated) |

**Normalize before combining**: scales differ in length (4 levels -> 0-3, 3 levels -> 0-2). Divide each score by its top level number, `len(criteria) - 1`, to map to 0-1. Then weights mean what they say (0.6 severity vs 0.3 frustration = twice as much). Code:
```python
def normalized(answers, qid):
    top = len(TRIAGE_QUESTIONS[qid].criteria) - 1
    return answers[qid].score / top
priority = 0.6*severity + 0.3*frustration + 0.1*report_quality  # report quality raises priority slightly
```
Computed: normalized 0.62 / 0.64 / 1.0 -> 0.6x0.62 + 0.3x0.64 + 0.1x1.0 = **0.664 ~ 0.66**.

## Structured level descriptions
Start with plain text. When the model keeps scoring between two neighbouring levels on inputs you think are clear, give each level an **object** with a field for what it covers and a field of example situations. **Use the same field names on every level.**
Example (spinner ticket, `what` + `examples`): levels = Cosmetic (examples: typo in a label, misaligned icon); Broken-but-workaround (export fails in one browser but works in another); Blocking (cannot log in, data loss). Response: score **1.09**, confidence **0.87**, probs 0:0.0, 1:0.91, 2:0.09, usage 379/18. With plain strings the same ticket was 1.11 / 0.84 (small shift since plain strings already placed it well). Note the `legend` echoes the structured objects back.

Examples steer, but only if they resemble real inputs (opening Safari report):
| Level description | score | confidence |
| - | - | - |
| plain string | 1.43 | 0.35 |
| examples array incl. "export fails in one browser but works in another" | 1.03 | 0.96 |
| examples array with unrelated example "search fails, but browsing categories still works" | 1.43 | 0.35 |
Higher confidence does not establish correctness; choose examples with known expected levels and **test revised descriptions on separate inputs before keeping them**.

## Numbers & limits
| Item | Value |
| - | - |
| Levels | at least 2 (recommended), API accepts up to 10 |
| Level numbering | 0-based array index; `probabilities`/`legend` keys are strings in the API, ints in the Python SDK |
| score range | 0 .. (levels-1) |
| Normalizer | score / (len(criteria)-1) |
| Usage examples | 332/18, 468/43, 379/18 (in/out tokens) |

## Gotchas
- Numbers-only levels collapse (0.33 confidence experiment).
- Same score != same distribution.
- Confidence 1.0 isn't correctness.
- Multi-dimensional descriptions break the scale.
- Mixed-length scales must be normalized before weighting.
- The `ScoreExplorer` interactive widget on the page is not captured in the source dump.

## Related
[[primitives-overview]] -- [[choice]] -- [[noul]] -- [[advanced-structure]] -- [[confidence]] -- [[composite-scoring]] -- [[cb-entity-alignment]] -- [[http-api-reference]] -- [[topic-calibration]]
