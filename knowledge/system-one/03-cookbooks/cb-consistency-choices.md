---
title: Self-Consistency of Choices
kind: cookbook
source: Cookbooks - Self-consistency - choices
source_url: https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook
tags: [cookbook, evaluation, confidence]
topics: [topic-calibration, topic-cost-latency, topic-routing]
---
# Self-Consistency of Choices
> Re-run one borderline moderation post through an 8-`Choice` rubric 15 times per condition (TypeSafe vs LLMs) and measure label stability; adding an `uncertain` outcome below top-probability 0.60 lifts TypeSafe agreement from 90.8% to 99.2% while still acting automatically on 74.2% of answers.

## What it is / How it works
One borderline user post, run through a moderation rubric of **8 `Choice` questions**; each run = one call answering all 8. **15 repeats (`NUM_SAMPLES`) per condition**; a condition = one model plus one setting. Each answer is one label from a fixed set (the routing decision: remove/leave up, escalate/auto-resolve, which queue). If the label wobbles between runs the same post routes to different places for no good reason. Run sampled **2026-09-11** against the production API (`https://api.typesafe.ai`, timeout 30 s), model alias `jev-latest`, which resolved to **`jev-1.13.0` on all 15 calls** (the code records `response.model` so alias drift is visible).

Setup: `pip install anthropic openai matplotlib ipython 'cooksafe>=0.2.0,<0.3.0'`; env `TYPESAFE_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`. `json_cache.json` ships with the cookbook so a re-render costs nothing; delete it to re-sample live. Cache key includes `sample_index` (each repeat is an independent draw), a `rubric_hash` (sha256[:12] of state+questions) and the model so edits bust the cache.

### Conditions
| group | model | Distribution t=0 | Distribution default | Single-pick t=0 |
|---|---|:-:|:-:|:-:|
| Non-reasoning LLM | `claude-haiku-4-5` | yes | yes | yes |
| Non-reasoning LLM | `gpt-5.4-mini` | yes | yes | yes |
| Reasoning LLM | `gpt-5.5` | - | yes | - |
| Reasoning LLM | `claude-opus-4-8` | - | yes | - |
| TypeSafe | `jev-latest` (`typesafe_choice`) | - | yes | - |

- "default" = no temperature argument sent: non-reasoning models use API default; reasoning models and TypeSafe have no temperature dial.
- Distribution mode: model returns per question an object of probabilities over labels (0.00-1.00, sum 1). Single-pick mode: one bare label per question; analysis puts all mass on it (one-hot), so NO uncertainty estimate -> excluded from agreement chart/table and std-dev table.
- Reasoning calls: Claude `thinking: {"type": "adaptive"}` (max_tokens 4096); OpenAI `reasoning_effort="high"`. Temperature 0 is the commonly suggested repeatability trick, so compared with default.
- **TypeSafe call**: one `system_one` request, state `{"uid": "<hash>:<i>:<token_hex(4)>", "post": POST}` (the dict directly), `questions` = 8 `Choice(instructions=..., criteria={label: description})`. Reads `response.answers[key].probabilities` (a dict label->prob) and orders by label list.
- **`uid` trick**: every query gets a fresh throwaway unique `uid` (appears in LLM prompt and as extra field in TypeSafe state) so repeats are distinct draws while post+rubric are unchanged. Caveat stated: this setup **cannot separate sensitivity to the irrelevant field from variation on truly identical requests**.
- LLM prompt: `json.dumps(POST)` + all 8 questions with every allowed label and description + exclusivity note ("labels mutually exclusive... if arguably more than one, pick the single most severe / most specific label") + answer-format instruction. Haiku sometimes wraps JSON in a ```json fence despite "ONLY a JSON object"; the helper peels one fence; unparseable replies become NaN = parse failure (never massaged to fit).

### The state (borderline post, all kept)
`post_id P-88213`; author `u/4471`, account_age_days 38, prior_strikes 1, followers 210; context: public reply, in reply to another user defending a game patch, community `r/gamedebates`; content: heated insulting text aimed at a person, community and argument, with "you need to be dealt with", "Come say it to my face, invite's right here" and "Keep it up and I'll end your whole channel" (threat never cleanly phrased), `has_link` true, `link_domain` `discord.gg`, language en; reports: 4 user_reports, reasons harassment, spam, threat. Designed so no single answer is obvious: small wording differences should not randomly move the same post between enforcement paths.

### The rubric: 8 `Choice` questions (labels are mutually exclusive, each with a description)
| key | question | labels |
|---|---|---|
| `category` | single most applicable content-policy category | None, Harass (insults a person, no threat, no protected-class attack), Hate (protected characteristic), Violence (credible threat/incitement), Spam (promo/link spam, no personal attack), Sexual |
| `primary_risk` | primary risk that should drive triage | Harassment, Violence (threat/intimidation), LinkAbuse (off-platform coordination), AccountHistory (prior strikes/repeat behaviour), LowRisk |
| `target` | who/what is it directed at | None, Person, Group (protected), Platform (community/platform itself) |
| `action` | enforcement action | Allow, Warn (label), Remove (no account penalty), Strike (remove + strike), Escalate (no automated action; human decides) |
| `queue` | which single moderation queue owns it | Auto, General, Threat, Spam, TSLead (trust-and-safety lead/senior) |
| `link_handling` | how to handle the external link/invite | Allow, RmLink (strip link keep post), Brigade (treat as coordinated brigading/abuse), Escalate (specialist assesses) |
| `review_path` | who makes the final call | Auto, Human (frontline), Senior (specialist), Legal (legal/law enforcement) |
| `severity` | overall severity | None, Low (rude, harmless), Medium (harassment, no clearly credible threat), High (harassment plus threat that could be read as credible) |

## When to use / when NOT to use
- Use as the template for testing whether a multi-question rubric produces stable routing, and for adding an "uncertain -> human review" outcome from returned probabilities instead of forcing the argmax.
- The `0.60` rule uses the returned **probabilities, not the API's separate `confidence` field**, and adds no model calls.
- NOT evidence of accuracy or superiority: "These percentages measure repeatability only." Haiku at t=0 scored 100% agreement with no abstentions and 100% repeatability "does not imply correctness"; the experiment does not measure accuracy.

## Worked example(s) - results

### Uncertain-outcome rule (the key technique)
`label = argmax(probs)`; if any value missing/non-numeric or outside [0,1] -> parse failure (None); else `label` if `max(probs) >= 0.60` else `"uncertain"` (send to human). At exactly 0.60 pick the top label. `MIN_CHOICE_PROBABILITY = 0.60` is "illustrative", not calibrated, not tuned to maximise this run's agreement; choose production thresholds from labeled examples and the cost of wrong actions and human review. Same rule applied to every probability-output condition.

### Raw label flips before abstention (TypeSafe)
- Clearer questions hold steady: `target` = Person and `severity` = High across all conditions.
- Borderline ones split across conditions: `category`, `primary_risk`, `action`, `review_path`, `link_handling`; some conditions flip within their own 15 repeats.
- TypeSafe top-label changes: `primary_risk` Harassment x11 / Violence x4; `link_handling` RmLink x8 / Brigade x7. After the 0.60 rule both rows read `uncertain` throughout (top probabilities below 0.60).

### Agreement table (agreement = share of the plurality decision over all 15 draws, averaged over 8 questions; parse failures count against)
| condition | raw agree | policy agree (uncertain counts as a decision) | uncertain | automatic | conflicts |
|---|---|---|---|---|---|
| claude-haiku-4-5 t=0 | 100.0% | 100.0% | 0.0% | 100.0% | 0 |
| claude-haiku-4-5 t=default | 87.5% | 86.7% | 0.8% | 98.3% | 2 |
| gpt-5.4-mini t=0 | 99.2% | 87.5% | 12.5% | 87.5% | 0 |
| gpt-5.4-mini t=default | 90.8% | 84.2% | 22.5% | 77.5% | 2 |
| gpt-5.5-reasoning | 90.0% | 93.3% | 30.8% | 69.2% | 1 |
| claude-opus-4-8-reasoning | 92.5% | 94.2% | 33.3% | 66.7% | 0 |
| typesafe_choice | 90.8% | 99.2% | 25.8% | 74.2% | 0 |

Column defs: `automatic` = share of all answers that select a label; `conflicts` = number of questions with >1 concrete label across repeats (abstentions ignored). Raw agreement uses original model outputs.
- Headline: LLM distribution settings repeat their plurality labels 87.5%-100% raw vs TypeSafe 90.8%. TypeSafe flips on 2 of 8 questions before abstention.
- With the 0.60 rule: TypeSafe 90.8% -> **99.2%**, uncertain 25.8%, automatic 74.2%. `primary_risk` and `link_handling` uncertain on **every** repeat; `category` alternated between Violence and `uncertain` (crossing the threshold on some repeats not others); **no question produced two different concrete TypeSafe labels**. With the rule the other LLM conditions land 84.2%-94.2% (Haiku t=0 excepted at 100%).

### Probability std dev (full vectors; per-label std across 15 repeats, averaged over labels and questions; single-pick rows excluded)
| condition | mean prob std | max prob std | parse fail | x TypeSafe |
|---|---|---|---|---|
| claude-haiku-4-5 t=0 | 0.0012 | 0.0221 | 0% | 0.12x |
| claude-haiku-4-5 t=default | 0.0516 | 0.3150 | 1% | 5.29x |
| gpt-5.4-mini t=0 | 0.0312 | 0.0905 | 0% | 3.20x |
| gpt-5.4-mini t=default | 0.0543 | 0.2303 | 0% | 5.56x |
| gpt-5.5-reasoning | 0.0305 | 0.1047 | 0% | 3.12x |
| claude-opus-4-8-reasoning | 0.0245 | 0.0693 | 0% | 2.52x |
| typesafe_choice | 0.0098 | 0.0515 | 0% | 1.00x |

TypeSafe has lower mean std than five of the six LLM distribution conditions (~2.5x-5.6x of TypeSafe); Haiku t=0 is lower (0.0012). "Small changes can still switch the top label when two labels are close."

## Numbers & limits
Cost + speed per full 8-question rubric call (mean of 15; LLMs ran in a 16-way thread pool; TypeSafe calls were drawn sequentially after the LLM pool closed so latency is a clean round trip):

| condition | time/call | cost/call | speed vs TS | cost vs TS |
|---|---|---|---|---|
| claude-haiku-4-5 t=0 | 3853 ms | $0.003498 | 33.8x | 76.1x |
| claude-haiku-4-5 t=default | 3860 ms | $0.003494 | 33.8x | 76.0x |
| claude-haiku-4-5 single-pick t=0 | 992 ms | $0.001527 | 8.7x | 33.2x |
| gpt-5.4-mini t=0 | 2293 ms | $0.002299 | 20.1x | 50.0x |
| gpt-5.4-mini t=default | 1986 ms | $0.002164 | 17.4x | 47.1x |
| gpt-5.4-mini single-pick t=0 | 826 ms | $0.000936 | 7.2x | 20.3x |
| gpt-5.5-reasoning | 12978 ms | $0.041255 | 113.7x | 897.4x |
| claude-opus-4-8-reasoning | 10376 ms | $0.028375 | 90.9x | 617.2x |
| typesafe_choice | **114 ms** | **$0.000046** | 1.0x | 1.0x |

Price table used (per 1M tokens, input/output; "prices + model ids as of 2026-07"): haiku-4-5 $1.00/$5.00; gpt-5.4-mini $0.75/$4.50; gpt-5.5 $5.00/$30.00; opus-4-8 $5.00/$25.00; TypeSafe **$0.042 input / $0.00 output** ("Historical TypeSafe rate, as of 2026-08").
Other fixed values: `NUM_SAMPLES` 15; `MIN_CHOICE_PROBABILITY` 0.60; LLM `max_tokens` 4096. LLM latency range 826 ms to 13.0 s under the concurrency used.

## Gotchas
- **Price caveat:** costs use historical price assumptions (page text mentions "the `speed_latest` rate for TypeSafe"; code comment says "Historical TypeSafe rate, as of 2026-08"); "not verified `jev-latest` prices or current billing amounts". Treat cost ratios as indicative. See [[models-and-versions]].
- Policy decisions do not make the model deterministic: a probability near 0.60 can still flip between a concrete label and `uncertain`; abstaining only collapses competing labels into the same human-review outcome. Probability stats and the `raw agree` column still report original outputs.
- Uncertain-by-threshold is not accuracy: none of this "shows accuracy or superiority".
- Single-pick LLM outputs carry no uncertainty (one-hot) so cannot be compared on the abstention policy.
- Haiku t=0 near-zero variance (std 0.0012, 100% agreement) is a reminder repeatability != correctness.
- `uid` confound (see above).
- The page's `typesafe_choice` model row records the *returned* model; an alias can resolve to a different version later - store `response.model` with results.
- Playground link opens the same post and 8 `Choice`s on `jev-latest` (without the changing `uid`).

## Related
[[cb-consistency-nouls]] · [[choice]] · [[confidence]] · [[cb-classification-using-confidence]] · [[confidence-gated-routing]] · [[cb-hierarchical-classification]] · [[benchmarks-and-comparisons]] · [[jev-1-13-jaggedness]] · [[topic-calibration]] · [[topic-routing]] · [[topic-cost-latency]]
