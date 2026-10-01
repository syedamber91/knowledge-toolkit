---
title: Autoresearch Feature Discovery (Questions as Features for CatBoost)
kind: cookbook
source: Autoresearch feature discovery (cookbooks/autoresearch_feature_discovery)
source_url: https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery
tags: [cookbook, extraction, evaluation]
topics: [topic-extraction, topic-calibration, topic-cost-latency]
---
# Autoresearch Feature Discovery (Questions as Features for CatBoost)
> Turn free text into numeric features by having an LLM propose System One questions, answering them per row, training CatBoost on the answers, and feeding CatBoost's errors/importances back into the next proposal round. Reached held-out RMSE 1.77 on wine-review scores.

## What it is / How it works
Goal: predict a numeric label (critic score 80-100) from free text (tasting note) with a supervised **CatBoost regressor**. CatBoost needs numbers; the table of numbers is built from questions about the note, none written by hand.

**Loop roles:** an LLM *proposer* writes questions; TypeSafe (`jev-1.12`) answers them for every row; CatBoost trains on the answers; CatBoost then reports which questions it used and which rows it still gets wrong; the next proposal call reads that report and the loop repeats.

Data flow (final model): note -> **38 TypeSafe questions** = 29 `Score` questions x 2 columns (expected rubric level + answer uncertainty) = 58 columns, plus 9 `Noul` questions x 1 column (probability true) = 9 -> **67 numeric columns** -> CatBoost -> predicted critic score; held-out RMSE **1.77**.

### Two question types the proposer can emit
| `kind` | Primitive | Column(s) | Use for |
|---|---|---|---|
| `intensity` | `Score` over a fixed 5-level rubric | mean level (and spread) | anything with degrees |
| `presence` | `Noul` with fixed true/false criteria | one probability | yes/no fact (e.g. fault named) |

Intensity rubric (every intensity question graded on it): 0 Not present in this note at all; 1 Barely present - mentioned once, in passing; 2 Present at a moderate level; 3 Present strongly - the note dwells on it; 4 Dominant - the note is largely about this. A note between "moderate" and "strongly" comes out between the two (the column is the average level).
Presence criteria: true = "The note states this or clearly implies it"; false = "The note gives no indication of this".

### Encodings (`ENCODING = "mean_spread"`)
Given the probabilities over levels: `mean = p @ levels`; `mean_spread` adds `sd = sqrt(E[l^2] - mean^2)` (variance clipped at 0); alternative modes: `mean` only, or one column per level (`name_p0..pN`). Presence = a single column. Importances of a score question's columns are summed back to one per-question percentage.

### Proposer (step 1)
- `PROPOSER = "claude-sonnet-5"` (code also has a branch for `gpt-5.6-luna` using `reasoning_effort="high"`; **not run**). Anthropic call: `max_tokens=16000`, `output_config` effort "medium" with JSON-schema structured output. OpenAI branch uses `json_object` + schema in prompt.
- `PROPOSALS = 18` actions max per round; output schema: `actions[]` of `{op: add|revise|drop, target, name, kind: intensity|presence, question}`; all five properties `required` (structured output), so unused fields come back empty (e.g. `target` empty for add; drop carries empty name/question and `kind: intensity`).
- Action semantics: **add** = new feature (must not duplicate an existing one); **revise** = replace the question wording of existing feature `target` (use when it measures the right thing badly: too narrow, too vague, or worded so almost every note answers the same); **drop** = remove a feature not earning its place.
- The only wine-specific string is `PROPOSER_TASK`: "designing numeric features for a gradient-boosting model that predicts the score a wine critic gave (80-100) from the tasting note alone. The model sees nothing but the features you design." Guidance: good features can be judged from the note's own words, vary from note to note, and carry information about quality the other features do not; reviewers describe structure, fruit, oak, length, complexity, drinkability, and also signal quality through word choice. Intensity questions must be worded so the 5 levels make sense.
- Prompt = task + example notes block + (if any) current features list (`name (kind): question`) + feedback block.
- Examples shown: round 1 = `EXAMPLES=60` dev notes spread across the score range (quantile picks, with scores). Later rounds = the **30 worst-predicted + 30 best-predicted** dev notes (by out-of-fold absolute error), each with score, current prediction and (if available) the previous round's prediction. Header tells the proposer the first half is where questions miss most and the second half where they are right, so "what separates the halves is what the questions have not captured."
- Feedback block (numbers rounded so a replay hits the cache): CV RMSE per round so far; count of dev notes now predicted better / worse by more than 0.1 points vs previous round; for every feature (sorted by importance): importance % of total and column spread (std over dev rows) with the hint "Low importance or low spread means the question is not doing much; revise or drop it."

### Answering (step 2)
One request per note carries every question of the round: `client.system_one(state=note, questions=..., model=jev-1.12)`; `featurize` runs **8 workers in flight** (`ThreadPoolExecutor`). Score probabilities kept for every level (`got.probabilities`), Noul keeps `got.noul`. No question is filtered **before** it is answered ("A question that applies to one row in ten will look useless in the 60 notes the proposer reads, and still be the most useful column in the set"). Only the round's *new* questions are answered each round (answers cached per feature id); all 2,000 rows (dev + held-out) are featurised.

### Fit and judge (step 3)
- CatBoost: `iterations=400, depth=4, learning_rate=0.05, loss RMSE, random_seed=0, thread_count=1`.
- Cross-validation: **5 folds x 3 repeats** (repeats steady the error at this sample size), label-stratified (sort by label with seeded tiebreak, deal off the top); out-of-fold predictions averaged across repeats.
- Rules each round:
  1. each **added** question: kept unless its column is flat (`std < MIN_SPREAD = 0.05` on dev rows, journaled "flat"); importance later shows whether it earned its place.
  2. each **revision**: swapped in, refit, kept only if dev CV RMSE <= previous + `CHANGE_TOLERANCE` (0.0, i.e. must improve; "reject" otherwise).
  3. each **drop**: refit without it; dropped only if dev CV does not get worse (<= tolerance), else "keep". A refit costs **no API calls**, so trying and rejecting is free.
  4. revision of a name an earlier round already dropped is journaled "stale".
- Out-of-fold predictions do three jobs: judge revisions/drops, choose next round's example notes, and tell the proposer which questions helped.
- Names are slugged (lowercase, non-alnum -> `_`, uniqueness suffix `_2`), ids `name@round`.

Pseudocode from the source:
```
for each round:
  notes   <- round 1 ? 60 dev notes across score range : 30 worst + 30 best
  actions <- LLM(brief, questions, notes, importance and error so far)
  answers[q] <- TypeSafe(note, all new questions of this round) for every row
  added q: keep unless flat | revised q: refit, keep if dev error drops
  dropped q: refit, drop only if dev error drops
  out_of_fold <- k-fold CatBoost   # judges + picks next notes
```

## When to use / when NOT to use
Use when you have **labelled text** and a supervised model, and want interpretable, question-shaped features rather than opaque embeddings or word counts. Point it at your data by editing only `PROPOSER_TASK` (and passing any list of strings to `featurize()`). Editing the brief changes the proposal prompt, which is part of the cache key, so the next run calls the API again for every round.
Cost shape: **one request per row per round** (not per question): 100,000 rows = 100,000 requests a round; extra questions in a round add no requests, but a **revision counts as a new question and costs another pass over every row**. Rate-limit warning: "Raise the worker pool slowly. Eight is already enough to hit a rate limit on a shared key."
Source stresses limits: one dataset, one run of the loop; much of the gain comes from the first proposal call; 245-character notes leave limited room for questions (see round 5).

## Worked example: wine reviews
- Dataset: 2,000 wine reviews (GroNLP/ik-nlp-22_winemag, pinned HF commit, deduplicated verbatim notes, seeded shuffle seed 0): note in, critic score out. **N_DEV=1,200, N_TEST=800** (loop reads dev labels only; test scored once at the end). Scores 80-98, mean 88.73, sd 3.17. Notes ~245 characters. Rounds: `ROUNDS=5`.
- Setup: `pip install anthropic openai catboost numpy matplotlib ipython 'cooksafe>=0.2.0,<0.3.0'`; set `TYPESAFE_API_KEY` and `ANTHROPIC_API_KEY`; `json_cache.json` ships so a re-render replays numbers. Numbers came from TypeSafe `jev-1.12` and `claude-sonnet-5` on 2026-08-03.

### Headline table (800 held-out rows, RMSE in critic-score points, lower is better)
| Arm | RMSE | Spearman |
|---|---|---|
| Predict mean of dev scores (reads no text) | 3.088 (3.09) | -0.014 |
| Same CatBoost, note as word counts (`text_features`; not a tuned text pipeline) | 2.466 (2.47) | 0.605 |
| Ask TypeSafe for the score itself (one `Score`, 10 bands, rescaled to 80-100, shifted -1.71) | 2.145 (2.15) | 0.761 |
| 18 questions from round 1, no loop | 1.869 (1.87) | 0.778 |
| **38 questions after all 5 rounds** | **1.772 (1.77)** | **0.799** |

"Ask for the score itself" arm: ten quality bands "Faulty or unpleasant" (level 0) ... "Profound" (level 9); `expected = sum k*p_k`, mapped `80 + 20*expected/9`; then every answer is moved by a single offset measured on dev scores (the only thing it learns from the labels; -1.71 here) because nothing in the question says where this publication's scores sit. Note **ten levels is the most a `Score` question takes; eleven comes back as a server error.** Question: "Judging only by what this tasting note says, how good is the wine?"

### Per-round log (dev CV RMSE, 5-fold x 3 repeats)
| Round | add / revise / drop proposed | Outcome | Features after | Dev CV |
|---|---|---|---|---|
| 1 | 18 add | all 18 kept: complexity, fruit_intensity, tannin_structure, acidity_intensity, oak_intensity, finish_length, balance_harmony, aging_potential, positive_superlative_language, negative_critical_language, drinkability_easiness, body_richness, sweetness_level, texture_descriptors, earthy_savory_notes, flaw_or_defect_mentioned, single_vineyard_or_prestige_signal, varietal_blend_detail | 18 | 1.903 |
| 2 | 5 / 3 / 3 | added power_concentration_language, flavor_distinctiveness, generic_fruit_language, candied_artificial_flavor, rustic_authentic_character; reject oak_dominance (+0.005); revise negative_critical_language (1.897->1.894) and single_vineyard_or_prestige_signal (1.894->1.881); keep (drops rejected) finish_length (+0.009), texture_descriptors (+0.001), varietal_blend_detail (+0.023) | 23 | 1.881 |
| 3 | 7 / 2 / 1 | added elegance_finesse_language, minerality_precision_language, hedged_qualified_praise, underripe_green_character, reviewer_overall_verdict_strength, unusual_or_funky_descriptor_valence, botrytis_or_special_winemaking_signal; revise negative_critical_language (1.868->1.864); revise finish_length -> finish_quality (1.864->1.861); keep candied_artificial_flavor (+0.014) | 30 | 1.861 |
| 4 | 5 / 2 / 3 | added excess_or_imbalance_signal, descriptive_detail_density, critic_enthusiasm_confidence, savory_food_wine_seriousness, note_overall_tone_positivity; revise rustic_authentic_character (1.843->1.838); reject hedged_qualified_praise (+0.014); keep botrytis_or_special_winemaking_signal (+0.011), candied_artificial_flavor (+0.009), unusual_or_funky_descriptor_valence (+0.010) | 35 | 1.838 |
| 5 | 4 / 2 / 8 | added structural_seriousness, youthful_tension_signal, surface_prettiness_vs_depth, price_value_signal; reject unconventional_character_as_virtue (+0.010); revise flavor_distinctiveness (1.849->1.843); **drop underripe_green_character** (1.843->1.840); keep candied_artificial_flavor (+0.002), botrytis (+0.003), hedged_qualified_praise (+0.006), excess_or_imbalance_signal (+0.005), unusual_or_funky (+0.002), texture_descriptors (+0.001), generic_fruit_language (+0.000) | 38 | 1.840 |

Round 5: "the first dev number that did not improve" (1.838 -> 1.840); "by round 5 the proposals had tipped from adding questions to dropping them." Of 8 proposed drops in round 5 only one was accepted. A rejected-then-reproposed pattern repeats (candied_artificial_flavor kept 3 rounds running).

### Did the rounds help? (held-out)
Round 1 -> round 5 on held-out rows: **-0.097 points, 95% CI [-0.147, -0.050]** (paired bootstrap, 2,000 resamples of the 800 rows). "Most of the gain is in that first call": 3.09 -> 1.87 from one proposal call (18 questions) vs 1.87 -> 1.77 from four feedback rounds. The held-out line falls further than the dev line; the dev line runs above held-out the whole way (training-size effect: each dev fold trains on 4/5 of 1,200 rows, the held-out model on all 1,200); the two lines move together, so dev CV tracks held-out error. Whole finding lives inside ~0.15 point. Source caveat: "All of this is one dataset and one run of the loop."

### What the questions turned out to measure
Importance share (CatBoost importance normalised so all 38 questions sum to 100%; a score question's mean and spread columns added back together; not a share of rows, questions or accuracy):

| Rank | Feature | Asked as | Share |
|---|---|---|---|
| 1 | note_overall_tone_positivity | score | 17.4% |
| 2 | savory_food_wine_seriousness | score | 8.7% |
| 3 | positive_superlative_language | score | 8.4% |
| 4 | single_vineyard_or_prestige_signal | noul | 7.2% |
| 5 | descriptive_detail_density | score | 5.7% |
| 6 | elegance_finesse_language | score | 5.0% |
| 7 | complexity | score | 5.0% |
| 8 | aging_potential | score | 5.0% |
| 9 | balance_harmony | score | 2.9% |
| 10 | drinkability_easiness | score | 2.9% |
| 11 | critic_enthusiasm_confidence | score | 2.7% |
| 12 | flavor_distinctiveness | score | 2.6% |

Final set: 29 score + 9 noul. Top question text: "Setting aside specific descriptors, how positive is the overall emotional tone and word choice of the note taken as a whole (warm, admiring language throughout vs. flat, neutral, or lukewarm phrasing)?" Observation: the tone-of-the-whole question outranks specific wine descriptors (structure, oak, etc.); prestige signals work as a noul.

Feature map figure: five held-out reviews (80, 86, 89, 91, 97 points; one per quarter of the score range) against 15 of the 38 questions (top 8 score + top 7 noul by importance), rows ordered by Spearman correlation of answer with critic score so answers above the divider rise with score and those below fall. Row labels lead with that correlation; cells in native scale (score 0-4, noul 0-1).

## Numbers & limits
| Item | Value |
|---|---|
| Data | 2,000 rows: 1,200 dev + 800 held-out |
| Rounds | 5; max 18 proposer actions/round; 60 example notes/round (30 worst + 30 best after round 1) |
| Feature counts by round | 18, 23, 30, 35, 38 |
| API requests | 2,000 TypeSafe requests per round (one per row; all of that round's questions ride it); 5 proposer calls |
| Concurrency | 8 workers |
| Min column spread | 0.05 |
| Change tolerance | 0.0 |
| `Score` max levels | 10 (11 = server error) |
| Models | TypeSafe `jev-1.12`; proposer `claude-sonnet-5` (run 2026-08-03) |
| Cost/latency | Not reported in source |
| RMSE ladder (held-out) | 3.09 / 2.47 / 2.15 / 1.87 / 1.77 |

## Gotchas
- Cache keys are function name + argument spelling; the cookbook passes `seed=` as a keyword on purpose. Rounding numbers in proposer prompts keeps replays hitting the cache.
- Structured output requires all properties in `required`; unused fields arrive empty (validate `op`/`target`).
- Revising a question costs a full extra pass over all rows; dropping costs nothing.
- Don't judge a question on the proposer's 60 examples alone (rare-signal questions can look useless).
- Only dev labels are read by the loop; score the held-out set once, at the end.
- Round-1 questions do most of the work; later rounds buy ~0.10 RMSE.
- Possible same-info redundancy across 38 correlated questions (see Next steps: prune correlated features).

## Next steps listed in the source
1. **Screen a candidate before paying to answer it**: treat the proposed question as the state and ask nouls about it: answerable from source text? means one thing under its criteria? applies to most rows? will vary across rows? Send only those clearing all four with enough confidence.
2. **Prune correlated features**: correlate encoded columns on dev rows, cluster near-duplicates, keep the clearest/most important per cluster.
3. **Add simple baselines** (TF-IDF, character counts, structural features), alone and appended to discovered columns.
4. **Mix proposer families** (Anthropic, OpenAI, Google Gemini, open-source), merge and dedupe before TypeSafe.
5. **Compare predictive models** (linear/elastic-net, SVR, random forests; recalibration for probabilistic outputs) to see if features help outside CatBoost.
6. **Embedding baseline**: `sentence-transformers/all-MiniLM-L6-v2` (local) or OpenAI `text-embedding-3-small` (hosted), appended to discovered columns.
7. **Match validation to deployment**: chronological splits for forecasting, grouped splits for related rows; keep a final test set untouched by both feature discovery and model selection.
8. **Stop on a plateau** (CV RMSE flat for a fixed number of rounds) or at a question/request budget.
9. **Longer search in an agent's Goal mode** with an explicit metric, budget and stopping rule.
10. **Check stability** across seeds/data slices; keep questions that stay useful.

A playground share link (one tasting note + all final questions, model jev-1.12) is provided in the source (not reproduced).

## Related
[[score]] · [[noul]] · [[primitives-overview]] · [[state]] · [[cb-parallel-questions]] · [[cb-reranking]] · [[cb-classification-using-confidence]] · [[minilm-embeddings]] · [[cookbooks-overview]] · [[topic-extraction]] · [[topic-calibration]] · [[topic-cost-latency]]
