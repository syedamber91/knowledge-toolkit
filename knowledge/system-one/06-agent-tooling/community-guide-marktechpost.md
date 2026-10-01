---
title: Community Guide (MarkTechPost Coding Tutorial)
kind: cookbook
source: "A Coding Guide to TypeSafe AI Jev: Typed Decisions, Calibrated Confidence, and Speculative Fan-Out with a System One Model" (MarkTechPost, 2026-09-23, Asif Razzaq; credits an external researcher's project)
source_url: https://www.marktechpost.com/2026/09/23/a-coding-guide-to-typesafe-ai-jev/
tags: [cookbook, api-sdk, patterns]
topics: [topic-agent-integration, topic-calibration, topic-routing]
---
# Community Guide (MarkTechPost Coding Tutorial)
> THIRD-PARTY runnable notebook (Python, typesafe-sdk 0.7.0) covering all three primitives, state shapes, the confidence formula, fan-out vs separate calls, gated routing, composite scoring, function calling, counting, and the async/typed production shape. Contains code and prose but **no measured outputs** — it prints results at runtime; the article quotes none.

Provenance: tutorial article; "All credit goes to the researcher of this project" (full code lives in an external repo). Nothing here is TypeSafe-verified. Numbers below are code constants/formulas, not results.

## Setup (section 0)
- `pip install typesafe-sdk==0.7.0` (pinned to the version the notebook was written against; the DEV guide only says `pip install typesafe-sdk`). Key loaded from `TYPESAFE_API_KEY`, Colab Secrets, or hidden prompt (console.typesafe.ai/keys). `TypeSafeClient()` reads the env var, defaults to alias `jev-latest`.
- `client.models.list().models` -> each has `.name`, `.release_date`, `.description` (shows which names/pinned versions the key can use).
- Helper `ask(state, questions, **kw)` wraps `client.system_one`, times it, adds `response.usage.input_tokens/output_tokens` to a ledger. Cost constant: `USD_PER_MILLION_INPUT_TOKENS = 0.042` (Jev list price; output free).

## Walkthrough
1. **Three primitives, one call.** State = ticket JSON (subject, messages, order A-104 with two captured $49 charges, refund_policy "full refund within 30 days"). Questions: department Choice (billing/technical/sales), frustration Score (3 levels, instruction points at `` `ticket.messages[0].text` `` with backticked nested path), refund_requested Noul, policy_supports Noul (instruction references `` `refund_policy` ``). Response accessors in this SDK version: `response.choices[name].choice/.confidence/.probabilities`, `response.scores[name].score/.legend/.probabilities/.confidence`, `response.nouls[name].noul`, plus `response.answers[name]`, `response.model` (pinned version that answered), `response.usage`. Question **names never reach the model**, so instructions must carry the full meaning. All questions run in parallel and in isolation from one another.
2. **State shapes.** Same Noul ("customer is eligible for a refund under the written policy"), with optional `criteria={"true": ..., "false": ...}` on a Noul, asked over (a) bare string, (b) array of conversation texts, (c) full object (ticket + order + policy). Point: only the object carries policy + charges; difference in probability is attributable to state; token column shows cost of extra context. Named fields recommended when context has several parts, so instructions can refer by name. (No results printed in the article.)
3. **Confidence is recomputable.** Formula: `confidence = (count * peak - 1) / (count - 1)` where count = number of options, peak = max probability. Score value = `sum(level * p)` over levels. Noul has **no confidence field**: its value is the probability of yes; **0.5 means undecided, not "medium"**. Test messages: blunt ("third outage this week ... Fix it NOW or I cancel today.") vs ambiguous ("Well. That was certainly an experience...") through a tone Choice (angry/calm/excited) and urgency Score (Can wait / this week / today). See [[confidence]].
4. **Speculative fan-out.** 10 questions (2 Choice, 2 Score, 6 Noul) about an incident postmortem (Incident 2291; 18% of EU checkouts timing out; connection pool limit lowered 400 -> 40 by config sync; 3,420 failed checkouts; ~61,000 USD delayed revenue; status page updated after recovery). Run in one call vs ten separate calls; compare wall time, input tokens, answers. Claim: state sent once instead of ten times is where latency and token savings come from; agreement column tests the isolation claim (a question should get the same answer alone or batched). Comparison tolerance in code: strings equal, numbers within 0.05. **No numeric result given** in the article (compare TypeSafe's cookbook figures 12.2x cheaper/10.0x faster quoted in [[community-guide-devto]]).
5. **Confidence-gated routing, bar rises with stakes.** Banking intent Choice (check_balance, approve_transfer, dispute_charge, close_account, other). Per-action bars in code: `check_balance 0.50, dispute_charge 0.70, approve_transfer 0.85, close_account 0.90`. Rule: answer `other` or confidence < 0.50 -> human; recognised but under its bar -> confirm with user first; else run. Six sample messages (e.g. "i guess maybe move some money around? not sure"). Thresholds are plain Python so risk tolerance is reviewed/versioned/tested. See [[confidence-gated-routing]].
6. **Composite scoring.** Four Score dimensions (python_depth, ml_systems, leadership, communication; 4 levels each, described as concrete situations not degrees), four candidates (Asha, Bruno, Chen, Dara). Normalise `score / (levels - 1)`. Two weight vectors: senior IC {python .40, ml .40, leadership .05, comms .15}; team lead {.15, .25, .45, .15}. "Two rankings, four model calls: changing the weights re-ran no inference." See [[composite-scoring]].
7. **Typed function calling.** Smart-home: `tool` Choice (set_lights, set_thermostat, play_music, `none`), `room` Choice with options but None descriptions (living_room, bedroom, kitchen, office), then argument Choices `state` (on/off/dim), `mode` (heat/cool/eco), `genre` (jazz/classical/rock/ambient) — all asked speculatively in one call; code reads only the selected tool's args; **weakest judgment = min confidence of tool, room, arg** is the call's confidence. Commands include "order me a pizza" -> none. Note: Choice `criteria` dict values may be `None` (label only). See [[cb-function-calling]].
8. **Counting done right.** 8-item basket (mango, spanner, kiwi, router, plum, stapler, fig, lychee): one Noul per item (`` `items[i]` is the name of a fruit ``) in one request, sum `noul > 0.5` in code, because Jev does not count reliably in one question.
9. **Production shape.** `class TicketDecision(SystemOneResponse)` with `department: ChoiceAnswer`, `frustration: ScoreAnswer`, `refund_requested: NoulAnswer` -> pass `response_model=TicketDecision` for attribute access validated by Pydantic. `AsyncTypeSafeClient` + `asyncio.gather` over a 12-ticket queue; `run_async` helper handles Jupyter/Colab running event loops (thread pool + `asyncio.run`). `RetryPolicy(max_retries=3, backoff_initial=0.5, backoff_max=4.0, timeout=20.0)`; client `timeout=10.0`. Typed errors: empty question set -> `TypeSafeError` raised before any request; unknown model (`jev-does-not-exist`, `retry=RetryPolicy(max_retries=0)`) -> `TypeSafeAPIError` subclass with `.status` (HTTP). Imports: `AsyncTypeSafeClient, ChoiceAnswer, NoulAnswer, RetryPolicy, ScoreAnswer, SystemOneResponse, TypeSafeAPIError, TypeSafeError`.
10. **Summary / ledger.** Totals calls, input tokens, output tokens (free), cost = input tokens/1e6 x 0.042. "Where to go next": patterns docs, cookbooks (re-ranking, RAG passage filtering, citation checks, LLM guardrails, hierarchical classification), jaggedness page `docs.typesafe.ai/model-jaggedness/jev-1.13` (literal reading, arithmetic, counting, date comparison, large irrelevant state), compare vs an LLM via `typesafe-ai/system-one-adapter-python`, pin with `TypeSafeClient(model="jev-1.13.0")`; `response.model` reports what answered.

## Numbers & limits (code constants only; no measured results)
| Item | Value |
|---|---|
| SDK version pinned | typesafe-sdk 0.7.0 |
| Price constant | $0.042 / M input tokens, output free |
| Confidence formula | (n x peak - 1)/(n - 1) |
| Routing bars | 0.50 / 0.70 / 0.85 / 0.90; global floor 0.50 |
| Retry | 3 retries, backoff 0.5-4.0 s, 20 s retry timeout, 10 s client timeout |
| Fan-out test | 10 questions (2 Choice, 2 Score, 6 Noul); same-answer tolerance 0.05 |
| Queue | 12 tickets concurrent |

## When to use / not
Use as a runnable template for production wiring (typed responses, async fan-out, retries). The article's conclusion: remaining work "no SDK can do" is evaluating questions, criteria and thresholds on your own data before trusting them with real actions.

## Gotchas / disagreements
- Accessor styles differ across sources: this tutorial uses `response.choices/scores/nouls[...]`; awesome's Python example uses `result.choices[...]`/`result.nouls[...]`; DEV guide uses `response.answers[...]`; JS uses `answers.team.choice`. All appear valid for their SDK version ([inference]: not contradictory but verify against [[sdk-python-types]]).
- Noul `criteria` with `"true"`/`"false"` keys appears only here; the DEV guide and directory show Noul with just `instructions`.
- Threshold values 0.5-0.9 here are teaching constants; the directory warns such thresholds are illustrative and need calibration on own labelled data ([[awesome-typesafe-jev]]).
- Article asserts but does not show numbers for isolation/agreement, speedup or cost; do not cite them as results.

## Related
[[community-guide-devto]] · [[openrouter-jev-guide]] · [[awesome-typesafe-jev]] · [[quickstart]] · [[sdk-python]] · [[sdk-python-clients]] · [[sdk-python-types]] · [[sdk-python-retries-and-exceptions]] · [[speculative-fan-out]] · [[confidence-gated-routing]] · [[composite-scoring]] · [[cb-function-calling]] · topics: [[topic-agent-integration]] [[topic-calibration]] [[topic-routing]]
