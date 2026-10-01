---
title: Parallel Questions (Batching Is Free)
kind: cookbook
source: Parallel questions (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/parallel_questions
tags: [cookbook, cost-latency, system-one]
topics: [topic-cost-latency, topic-state-design, topic-calibration]
---
# Parallel Questions (Batching Is Free)
> Put all N questions about one document into ONE call: answers are identical to N single-question calls (no bias, no added noise), but 12.2x cheaper and 10.0x faster on a 13-question GDPR briefing. Always batch.

## What it is / How it works
Claim: each question is scored independently against the document, so an answer does not depend on which other questions share the request. Test: ask each question several times both ways (all N in one request; one question per request) and compare the **mean** (does batching bias?) and **run-to-run std dev** (does batching add noise?). Result: whatever noise a question has, it has under both strategies; batching adds none. Most answers were identical across all 5 repeats (std dev exactly 0.0).

Cost/speed do change: the document dominates every request. N single calls pay for it N times, in N round trips; the batched call pays once. The bigger the document, the nearer the saving comes to a full Nx. See [[state]], [[speculative-fan-out]].

**Case:** regulatory briefing. Document = Wikipedia article "General Data Protection Regulation", pinned revision `1363040264` (as of 2026-07), plain-text extract via the MediaWiki API (`prop=extracts&explaintext=1`), cached next to the API calls, **53,777 characters** (~54,000; "document-dominated workload"). Compliance team wants 13 checks: **8 `Noul`, 2 `Choice`, 3 `Score`**.

**Tracked number per answer type**
| Type | Metric tracked |
|---|---|
| Noul | probability of "yes" (`answer.noul`) |
| Choice | max prob = probability on the picked label (`max(answer.probabilities.values())`); `criteria` maps label -> meaning |
| Score | score normalised to 0-1 = `score / (len(criteria) - 1)`; `criteria` lists level descriptions from level 0 up |

**Call shape:** `client.system_one(state={"article": DOCUMENT}, questions={key: QUESTIONS[key] for key in keys}, model="jev-1.12")`; `DOCUMENT = {"source": url, "text": text}`; document byte-identical in every call; client `timeout=120.0`. `RUNS = 5` repeats per strategy; `run` param only forces a distinct live call per repeat under the cache. Price applied after cache retrieval (so a price change needs no new calls); token counts and latency cached.

## When to use / when NOT to use
- Use: any time you have several questions about the same state/document: put them all in one request. Saving holds regardless of how you fire the calls.
- Speed caveat: the 10.0x speed figure sums the 13 single-call latencies, i.e. assumes they run **sequentially**. Fire them concurrently and the speed gap shrinks, **but the 13x token cost stays**.
- Source states no case where batching hurts answers.

## Worked example(s)
The 13 questions (exact design):

| Key | Type | Question / options |
|---|---|---|
| breach_72h | Noul | Must a personal data breach be reported to the supervisory authority within 72 hours? |
| applies_non_eu | Noul | Does the regulation apply to organisations established outside the EU that offer goods or services to people in the EU? |
| dpo_all_orgs | Noul | Must every organisation appoint a Data Protection Officer, regardless of what data it processes? |
| pre_ticked_consent | Noul | Can valid consent be obtained through pre-ticked boxes or inactivity? |
| right_erasure | Noul | Does the regulation grant individuals a right to erasure of their personal data? |
| data_portability | Noul | Does the regulation include a right to data portability? |
| us_federal_law | Noul | Is the GDPR a United States federal law? |
| criminal_penalties | Noul | Does the GDPR itself impose criminal penalties such as imprisonment? |
| instrument_type | Choice | What kind of EU legal instrument is the GDPR? Options: Regulation (directly binding in all member states), Directive (sets goals, national implementation), Treaty, Recommendation (non-binding) |
| max_fine | Choice | Max administrative fine for most serious infringements? Options: TwentyM_or_4pct (EUR 20M or 4% worldwide turnover, whichever greater), TenM_or_2pct, FixedCap, NoFines |
| individual_rights | Score (4 levels, 0-3) | None / Weak (right to be informed) / Moderate (access+correction) / Strong (access, erasure, portability, objection, with enforcement) |
| penalty_severity | Score (4 levels, 0-3) | None / Symbolic / Substantial / Severe (fines scaled to global revenue) |
| compliance_burden | Score (5 levels, 0-4) | Negligible / Light / Moderate / Heavy / Extreme (ordinary organisations cannot fully comply) |

Per-question result, batched mean vs single mean (std dev batched / single):

| Question | metric | batched mean | single mean | batched std | single std |
|---|---|---|---|---|---|
| breach_72h | p(yes) | 0.804 | 0.814 | 0.0055 | 0.0055 |
| applies_non_eu | p(yes) | 0.990 | 0.990 | 0 | 0 |
| dpo_all_orgs | p(yes) | 0.030 | 0.030 | 0 | 0 |
| pre_ticked_consent | p(yes) | 0.040 | 0.040 | 0 | 0 |
| right_erasure | p(yes) | 0.990 | 0.990 | 0 | 0 |
| data_portability | p(yes) | 0.990 | 0.990 | 0 | 0 |
| us_federal_law | p(yes) | 0.010 | 0.010 | 0 | 0 |
| criminal_penalties | p(yes) | 0.108 | 0.108 | 0.0045 | 0.0084 |
| instrument_type | max prob | 1.000 | 1.000 | 0 | 0 |
| max_fine | max prob | 1.000 | 1.000 | 0 | 0 |
| individual_rights | norm. score | 1.000 | 1.000 | 0 | 0 |
| penalty_severity | norm. score | 1.000 | 1.000 | 0 | 0 |
| compliance_burden | norm. score | 0.750 | 0.750 | 0 | 0 |

Reading: Choices, Scores and 6 of 8 Nouls are identical across all 5 repeats under both strategies. `breach_72h` and `criminal_penalties` carry small run-to-run sampling noise, the same size under both strategies, means agreeing within that noise (criminal_penalties std 0.0045 batched vs 0.0084 single; the source calls these "the same size" noise, a property of the question). Conclusion: no question's answer depends on the 12 other questions sharing its request.

## Numbers & limits
| Item | One call (all 13) | 13 calls (one each) | Ratio |
|---|---|---|---|
| Calls | 1 | 13 | 13x |
| Cost | $0.000497 | $0.006090 | **12.2x cheaper** |
| Total time | 0.27 s | 2.71 s | **10.0x faster** (sequential assumption) |

- Price used: `PRICE = (0.042, 0.00)` USD per 1M tokens (input, output) for `jev-1.12` "as of 2026-09". Cost = in_tokens/1e6*0.042 + out_tokens/1e6*0.00. Output is priced at $0.00.
- [inference] $0.000497 / $0.042 per M implies about 11.8k input tokens for the batched call; not stated in the source.
- Averages over 5 runs. Model `jev-1.12`. Setup: `pip install ipython 'cooksafe>=0.2.0,<0.3.0'`, set `TYPESAFE_API_KEY`. Calls cached to `json_cache.json` (shipped; delete to re-run live).
- Saving approaches full Nx as the document grows relative to the questions (12.2x here vs the 13x ceiling for N=13).

## Gotchas
- Cost ratio 12.2x < 13x because question tokens and per-call overhead are not zero; the document is not 100% of the request.
- The speed number assumes sequential single calls; concurrency narrows the speed gap, never the token cost.
- Residual noise on borderline Nouls (e.g. breach_72h p 0.80-0.81, criminal_penalties ~0.11) exists regardless of batching; repeat calls or gate on confidence if it matters ([[confidence]]).
- Normalisation of Scores for comparison: divide by top level index (levels 0..L-1).

## Related
[[state]] · [[noul]] · [[choice]] · [[score]] · [[primitives-overview]] · [[speculative-fan-out]] · [[composite-scoring]] · [[cb-consistency-nouls]] · [[cb-consistency-choices]] · [[cookbooks-overview]]
