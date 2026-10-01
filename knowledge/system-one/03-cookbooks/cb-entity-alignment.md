---
title: Knowledge Graph Entity Alignment
kind: cookbook
source: Knowledge graph entity alignment (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/entity_alignment
tags: [cookbook, classification, routing]
topics: [topic-classification, topic-routing, topic-calibration]
---
# Knowledge Graph Entity Alignment
> Decide, for each of 450 candidate duplicate pairs (two beer catalogues), whether to merge, drop, or send to a human curator, using ONE `Score` question (3 levels) plus three companion `Noul` questions in a single request. No fitted threshold anywhere.

## What it is / How it works
**Problem.** Two sources describe overlapping sets of things (knowledge-graph "entities"). A cheap, rough first pass already produced 450 candidate pairs worth a closer look. Each pair needs a judgment call.

**Asymmetric cost.** Wrongly merging is the expensive error: every fact about either entity now describes the merged one, and everything linked to either comes along; undoing it means working out which fact came from where. Missing a match only leaves a duplicate. So the decision needs a third outcome: pairs that are neither safe to merge nor safe to drop.

**The design: one `Score` with one level per outcome** (see [[score]], [[primitives-overview]]):

| Score level | Level description (as written in the code) | Outcome (`OUTCOME` map) |
|---|---|---|
| 0 | "They describe two different products." | `leave unlinked` |
| 1 | "They describe closely related products that may or may not be the same one: a variant, a special edition, or a name that could plausibly refer to either." | `curator queue` |
| 2 | "They describe one and the same product." | `assert sameAs` |

- The merge outcome is called `assert sameAs` because `sameAs` is the standard way to record two entities are the same thing, and writing one is how the merge actually happens.
- **Why Score, not Noul or Choice:** a Score lets you attach a semantic label (the score criteria) directly to every outcome, including the middle one. A Noul could only do this indirectly via thresholding its output; a Choice would lose the *ordered* relationship of the three outcomes.
- **Companion Nouls** (one per compared field) ride in the same request and exist only to give the curator detail on *which fields disagree* when the score lands in the middle level. Three fields get a Noul: name, brewery, style. **Alcohol content (abv) gets none**: comparing two numbers is arithmetic, do it in code if wanted.
- **Single state, two entities:** both entities go into one state as `entity_a` and `entity_b`, so every question is about the *pair*, not either side alone. All four questions go in one request (one request per pair; spend scales with the number of pairs, not source size). See [[state]], [[speculative-fan-out]].
- **`route()`**: the entire decision rule is rounding the score to the nearest level: `OUTCOME[min(int(score + 0.5), len(LEVELS) - 1)]`. Cut points are therefore **0.5** and **1.5**. No threshold constant exists in the file; level descriptions can be written *before seeing a single score* (unlike a number you have to fit).
- Middle-level wording is the part worth writing carefully; here it covers variants, special editions and plausibly-either names so they reach a curator instead of being merged or dropped.

**Questions as coded** (`QUESTIONS` dict):
- `link_state`: `Score(instructions="How do the two entity descriptions relate as products?", criteria=LEVELS)`
- `same_name`: `Noul("Do the two entities state the same beer name?")`
- `same_brewery`: `Noul("Are the two entities from the same brewery?")`
- `same_style`: `Noul("Do the two entities describe the same beer style?")`

Call shape (the exact part that matters): `client.system_one(state={"entity_a": ..., "entity_b": ...}, questions=QUESTIONS, model="jev-1.12")`; read `response.answers["link_state"].score / .probabilities / .confidence` and `response.answers[k].noul` for the Nouls; `response.usage.input_tokens/output_tokens` recorded (source: "tokens and requests are the durable units; don't cache a derived cost").

**Porting to other data:** rewrite `QUESTIONS` and `LEVELS`. The only other beer-aware code is the two print functions naming the fields.

## When to use / when NOT to use
- Use when: deduplicating/linking entities across sources where only natural-language descriptions exist, a cheap blocking/candidate-generation pass already exists, and a wrong merge is costlier than a missed one (so you want a human-review middle band).
- The source does not say when NOT to use it. It does state the tradeoff that alternatives (Noul-thresholding, Choice) were rejected for the reasons above.
- Numeric fields: do not ask the model; compute in code.

## Worked example(s)
Dataset: Beer data from the **Magellan** collection (two beer catalogues scraped from different websites, pre-cut to 450 pairs). Each entity has 4 fields: name, brewery, style, abv. Each pair also has `known_same_as` (the benchmark's own answer; **the source never reports accuracy against it**, only the routing distribution). Text left as published, **no pre-processing**: unconverted HTML entities, apostrophes split off as separate words, a few wrongly decoded characters.

First pair as the model sees it: "C N Red Imperial Red Ale" / Redwood Lodge / American Amber / Red Ale / 8.10 % vs "Kinetic Infrared Imperial Red Ale" / Kinetic Brewing Company / American Strong Ale / 9.30 %.

Four shown pairs (score, confidence, routed outcome; Noul values name/brewery/style):

| Pair | What it is | score | confidence | -> | name / brewery / style |
|---|---|---|---|---|---|
| c446 | Thomas Hooker Old Marley Barleywine, styles "American Barleywine" vs "Barley Wine" (same product) | 1.94 | 0.92 | assert sameAs | 0.97 / 0.99 / 0.81 |
| c427 | Frost Quake Bourbon Barrel Aged Barley Wine (Wellington County) vs Lompoc Bourbon Barrel Aged Proletariat Red A... (Lompoc) (two products) | 0.03 | 0.95 | leave unlinked | 0.02 / 0.09 / 0.08 |
| c100 | Belle Gueule Rousse; brewery "Brasseurs R.J." vs "Brasseurs RJ"; styles "American Amber / Red Ale" vs "Amber Lager/Vienna" (same name and brewery, styles worded differently) | 1.30 | 0.27 | curator queue | 0.95 / 0.94 / 0.35 |
| c428 | "Ambleside Amber Ale" vs "Bridge Ambleside Amber Ale - Pomegranate & Galena Hops" (a beer vs a fruit-and-hop variant; same brewery Bridge Brewing Company, same abv) | 1.10 | 0.77 | curator queue | 0.63 / 0.98 / 0.74 |

Note c100 has the lowest confidence (0.27) of the four; c428 has a confident middle score (0.77). The two middle cases land there for different reasons (style wording differs vs. a variant).

## Numbers & limits
| Item | Value |
|---|---|
| Candidate pairs | 450 |
| Model / date | `jev-1.12`, numbers from 2026-08-11 |
| Outcome: assert sameAs | 40 (8.9%) |
| Outcome: curator queue | 50 (11.1%) |
| Outcome: leave unlinked | 360 (80.0%) |
| Cut points | 0.5 and 1.5 (rounding) |
| Pairs within 0.1 of upper cut (1.5; decides merges) | 9 |
| Pairs within 0.1 of lower cut (0.5; only decides whether curator sees it) | 47 |
| Typical score on this set | most land near 0.25 (not on whole numbers) |
| Concurrency | `MAX_WORKERS=6`; public endpoint rate-limits above roughly eight; a live run takes "a few minutes" |
| Client timeout | 120.0 s |
| Setup | `pip install matplotlib ipython 'cooksafe>=0.2.0,<0.3.0'`, set `TYPESAFE_API_KEY`; calls cached to `json_cache.json` (delete to re-run live) |

- Why scores sit near 0.25: two beers with nothing in common may share a style name or have alike brewery names, so the model gives the middle level some probability instead of none. What decides a pair is **which side of a cut point it falls on**, not how near it sits to a level.
- Neither cut is tuned; both follow from how the level wording is written, and the **middle-level wording is what moves pairs between curator and unlinked**.

## Gotchas
- Wording of the middle level controls the curator-queue volume (47 pairs crowd the lower cut vs 9 at the upper), so the "no threshold" claim means the tuning knob is prose, not a number.
- Upper cut (merge) is far less crowded than the lower cut; the risky decision (merge) has few near-boundary cases here.
- Raw unclean text is fine here (no preprocessing was done), per the source.
- Accuracy vs `known_same_as` is **not reported** in the source; do not assume it.
- Confidence (`link.confidence`) is returned and printed but is not part of the `route()` rule; the source does not use it for routing. [inference] one could gate on it, but the cookbook does not.

## Related
[[score]] · [[noul]] · [[primitives-overview]] · [[state]] · [[confidence]] · [[confidence-gated-routing]] · [[cb-classification-using-confidence]] · [[cookbooks-overview]]
