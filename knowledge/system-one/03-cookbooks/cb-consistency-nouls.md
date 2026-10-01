---
title: Self-Consistency of Nouls
kind: cookbook
source: Cookbooks - Self-consistency - nouls
source_url: https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook
tags: [cookbook, evaluation, confidence]
topics: [topic-calibration, topic-cost-latency, topic-routing]
---
# Self-Consistency of Nouls
> Re-run one auto-insurance claim through a 14-`Noul` rubric 15 times per condition (TypeSafe vs LLMs); TypeSafe's probabilities barely move (mean std 0.0102) but can still straddle 0.5, so map P(true) into yes / uncertain (0.30-0.70 inclusive) / no and send the middle to a human.

## What it is / How it works
One auto-insurance claim run through **14 `Noul` questions** (each answer = P(true) for a True/False question); each run = one call answering all 14. **`NUM_SAMPLES` = 15** repeats per condition (condition = model + setting); every probability returned is shown. In a claims-triage pipeline (pay / deny / send-to-human) probabilities guide the decision, and small changes near a threshold can flip the action. Sampled **2026-09-11** on the production API (`https://api.typesafe.ai`, timeout 30 s) with `jev-latest`, which resolved to **`jev-1.13.0` for all 15 calls**.

Setup: `pip install anthropic openai matplotlib ipython 'cooksafe>=0.2.0,<0.3.0'`; env `TYPESAFE_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`. `json_cache.json` ships with the cookbook (replay, no spend); delete to re-sample live. Cache key = sample_index + rubric hash (sha256[:12] of claim + questions) + model.

### Conditions
| group | model | Probability t=0 | Probability default | Yes/no t=0 |
|---|---|:-:|:-:|:-:|
| Non-reasoning LLM | `claude-haiku-4-5` | yes | yes | yes |
| Non-reasoning LLM | `gpt-5.4-mini` | yes | yes | yes |
| Reasoning LLM | `gpt-5.5` | - | yes | - |
| Reasoning LLM | `claude-opus-4-8` | - | yes | - |
| TypeSafe | `jev-latest` (`typesafe_noul`) | - | yes | - |

- Default = no temperature sent (non-reasoning use API default; reasoning models and TypeSafe have no temperature setting). Temperature 0 is "usual advice for repeatability", compared with default.
- LLM probability mode: prompt = `uid` line + `json.dumps(CLAIM)` + 14 questions, "give your probability that the answer is yes ... ONLY a JSON object mapping each key to a number between 0.00 and 1.00".
- Yes/no mode (non-reasoning only): bare "yes"/"no" per question mapped to 1.0/0.0; forces a hard decision, shows what models do when they cannot leave mass in the uncertain middle. Anything else (missing key, non-number, neither yes nor no) = NaN, never a legit-looking value.
- Reasoning: Claude `thinking: {"type": "adaptive"}` (max_tokens 4096); OpenAI `reasoning_effort="high"`.
- **TypeSafe call**: one `system_one` request; state `{"uid": "<i>:<token_hex(4)>", "claim": CLAIM}` (dict passed directly); `questions = {key: Noul(instructions=question)}`; read `response.answers[key].noul`.
- **`uid`**: fresh throwaway value each run (LLM prompt + extra TypeSafe state field), leaves claim/rubric unchanged. Caveat: setup **cannot separate sensitivity to the irrelevant field from variation on identical requests**.
- Note: `claude-haiku-4-5` wraps nearly every reply in a ```json fence that strict `json.loads` rejects despite "ONLY a JSON object" (other models return bare JSON); helper peels one fence; a still-failing reply = parse failure, counted but not scored.
- Questions phrased so **yes = the thing checked for is true**, keeping every row comparable (model probability and TypeSafe `noul` measure the same thing).

### The state: claim (borderline calls built in)
Policy `AP-77413` (Dana M.; effective 2026-01-15 to 2027-01-15; coverages collision True, rental_reimbursement False; deductible $500; per_incident_limit $10,000; listed drivers Dana M., Sam M.; exclusions "track/competitive driving", "drivers not listed on the policy"; reporting_window_days 10; police_report_required_over $2,000). Claim `CLM-55029`: incident 2026-06-28, reported 2026-07-04, driver Sam M.; description: attended a track-day event, rear-ended by another car in the spectator parking lot while stationary, not on the circuit; claimed $3,250 = rear bumper $1,700 + paint/refinish $800 + parking-sensor recalibration $450 + rental car (6 days) $300; docs: repair estimate PDF, 8 damage photos. Adjuster note from `auto-triage`: "Collision coverage active. Approved. Pay full amount $3,250 to policyholder, 5-10 business days." Claim history: 2 claims in last 12 months, 0 prior denied.

Built-in borderline traps: (1) track-day event vs the track exclusion but loss in parking lot while stationary; (2) rental-car line item with no rental coverage; (3) no police report attached though required for collisions > $2,000; (4) auto-triage already marked "approved, pay full amount" before human review and without withholding the deductible. (Line items sum 1700+800+450+300 = 3,250 [inference: arithmetic check; matches claimed amount]; reported 6 days after incident, inside 10-day window [inference].)

### The rubric: 14 `Noul` questions
| key | question |
|---|---|
| `covered` | Is the loss covered under the policy's collision coverage? |
| `exclusion` | Does a policy exclusion apply to this loss? |
| `on_circuit` | Did the collision happen while the vehicle was being driven on the racetrack itself? |
| `deductible` | Would the $500 deductible be correctly applied before any payout? |
| `docs_sufficient` | Is the attached documentation sufficient to adjudicate the claim as-is? |
| `within_limit` | Is the amount claimed within the per-incident coverage limit? |
| `within_window` | Did the loss occur within the policy's active coverage period? |
| `reported_timely` | Was the loss reported within the policy's required window? |
| `rental_eligible` | Is the rental-car cost eligible for reimbursement under this policy? |
| `fraud_flag` | Are there indicators that warrant a fraud review? |
| `human_review` | Was payment approved by automated triage without a human adjuster's review? |
| `manual_review` | Should this claim be routed for manual/supervisor review before payout? |
| `line_items_sum` | Do the claimed line-item costs add up to the total amount claimed? |
| `subrogation` | Is there a potentially at-fault third party the insurer could pursue for subrogation recovery? |

## When to use / when NOT to use
- Use as the template for checking run-to-run stability of a True/False rubric, and for converting P(true) into a three-way decision with an explicit human-review band instead of a single 0.5 cut.
- The uncertainty band is application logic over the returned probability: **no new question, no second API call**.
- NOT a proof of correctness: an automatic decision that clears the band "is not shown to be correct"; the model is no more deterministic for the band.

## Worked example(s) - results

### Variance findings
- LLM answers move from run to run, at temperature 0 too; on judgment calls the models disagree with *themselves* and with each other.
- TypeSafe mean per-question probability standard deviation = **0.0102**, "below all LLM probability conditions here" (the per-condition std table is not printed in this page).
- TypeSafe variation is highest on `covered` (**0.43 to 0.53**, crosses 0.5) and `exclusion` (**0.53 to 0.62**). Its other 13 questions stay on one side of 0.5 throughout this run (note: `exclusion` stays above 0.5, `covered` is the only row that crosses).
- Factual checks hold steady across most conditions; judgment-heavy ones are where LLM rows move: `exclusion`, `rental_eligible`, `fraud_flag`, `manual_review` shift across samples or disagree across models.
- Heatmap colour: red = higher P(yes), green = lower; for risk questions a red cell is one the rubric flagged.

### Uncertain-outcome band
With a single 0.5 threshold, 0.49 and 0.51 cause opposite actions despite both expressing substantial uncertainty. Instead:
```python
def noul_decision_with_uncertainty(p):
    if p < 0.30: return "no"
    if p > 0.70: return "yes"
    return "uncertain"      # 0.30 through 0.70 inclusive
```
Constants `NOUL_UNCERTAINTY_LOW = 0.30`, `NOUL_UNCERTAINTY_HIGH = 0.70`. Uncertain -> human. Band is illustrative: not a calibrated guarantee, not an optimised threshold; set production boundaries from labeled examples and the cost of wrong decisions and of review. The page applies it to recorded TypeSafe probabilities in a heatmap (green no / grey uncertain / blue yes) with probabilities printed in each cell. The band absorbs fluctuation around 0.5 without opposite automatic actions, but has its own edges: a value near 0.30 or 0.70 can still move between `uncertain` and yes/no.

## Numbers & limits
Cost + speed per full 14-question rubric call (mean of 15 calls; LLMs in a 16-way pool; TypeSafe sequential):

| condition | time/call | cost/call | speed vs TS | cost vs TS |
|---|---|---|---|---|
| claude-haiku-4-5 t=0 | 1780 ms | $0.001798 | 16.0x | 42.2x |
| claude-haiku-4-5 t=default | 1644 ms | $0.001798 | 14.8x | 42.2x |
| claude-haiku-4-5 yes/no t=0 | 1485 ms | $0.001650 | 13.4x | 38.8x |
| gpt-5.4-mini t=0 | 1405 ms | $0.001089 | 12.7x | 25.6x |
| gpt-5.4-mini t=default | 1177 ms | $0.001179 | 10.6x | 27.7x |
| gpt-5.4-mini yes/no t=0 | 1113 ms | $0.000950 | 10.0x | 22.3x |
| gpt-5.5-reasoning | 11125 ms | $0.033157 | 100.2x | 778.9x |
| claude-opus-4-8-reasoning | 13886 ms | $0.034275 | 125.0x | 805.1x |
| typesafe_noul | **111 ms** | **$0.000043** | 1.0x | 1.0x |

TypeSafe mean round trip 111 ms; LLM range 1.1 s to 13.9 s under the stated concurrency. Prices (per 1M tokens in/out, "as of 2026-07"): haiku-4-5 $1.00/$5.00; gpt-5.4-mini $0.75/$4.50; gpt-5.5 $5.00/$30.00; opus-4-8 $5.00/$25.00; TypeSafe $0.042/$0.00 ("Historical TypeSafe rate, as of 2026-08").

## Gotchas
- Cost figures use historical price assumptions (page text names the `speed_latest` rate for TypeSafe); "not verified `jev-latest` prices or current billing amounts".
- A 0.5 cut on P(true) is fragile where TypeSafe itself ranges 0.43-0.53 (`covered`): a review band is the mitigation, not a cure.
- Yes/no mode removes all uncertainty signal (values are only 0.0 / 1.0).
- Haiku's code fence breaks naive `json.loads`; unparseable output must be counted as a failure, not coerced.
- `uid` confound (above); record `response.model` since an alias can resolve to a different version.
- Playground link opens the same claim + 14 Noul on `jev-latest`, omitting the changing `uid`.

## Related
[[cb-consistency-choices]] · [[noul]] · [[confidence]] · [[score]] · [[cb-classification-using-confidence]] · [[confidence-gated-routing]] · [[benchmarks-and-comparisons]] · [[jev-1-13-jaggedness]] · [[topic-calibration]] · [[topic-routing]] · [[topic-cost-latency]]
