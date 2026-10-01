---
title: SDE Cascade
kind: cookbook
source: SDE cascade (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/sde_cascade
tags: [cookbook, extraction, cost-latency]
topics: [topic-extraction, topic-cost-latency, topic-guardrails, topic-model-selection]
---
# SDE Cascade
> Structured-data-extraction cascade: extract with a cheap mini model -> verify per field with TypeSafe Noul questions -> escalate to a reasoning model only if any field's P(wrong) > 0.7. Gets most of the big model's quality at a fraction of the cost.

## What it is / How it works
Problem: big reasoning models extract structured data well but are slow and expensive; small models are cheap but make mistakes. A cascade gets most of the quality at a fraction of the cost.

Models and prices ($ per 1M tokens, input / output; standard rates checked September 15, 2026):

| Role | Model | Price |
|---|---|---|
| rung 0 (mini) | `gpt-5.4-mini` | $0.75 / $4.50 |
| rung 1 (reasoning, `reasoning_effort="high"`) | `gpt-5.5` | $5.00 / $30.00 (roughly 7x the mini) |
| verifier | TypeSafe `jev-1.12` | $0.042 / $0.00 (output tokens free; published Jev pricing) |

Algorithm:
1. **Extract** with the cheap model.
2. **Verify** with TypeSafe primitives: a per-field yes/no [[noul]] question (e.g. "is this value absent from the source?", "was it lifted from unrelated text?"), each returning P(something is wrong).
3. **Escalate** to the expensive model if a verifier signal fires; otherwise keep the cheap answer.

Design choice: the two extraction rungs use plain text-mode OpenAI. NOT structured outputs / tool calls / JSON mode, because (a) a schema-following mistake is not the mistake expected of an LLM (and is easy to make synthetic data for), (b) if an LLM does fail to follow the schema it is almost always very confused, so constrained decoding does not fix the underlying issue. Source encourages trying them anyway.

Setup: `pip install openai datasets jsonschema ipython 'cooksafe>=0.2.0,<0.3.0'`; set `OPENAI_API_KEY` and `TYPESAFE_API_KEY`. Constants: `MINI="gpt-5.4-mini"`, `REASONING="gpt-5.5"`, `TS_MODEL="jev-1.12"`, `FIRE_T = 0.7` (escalate if any per-field P(wrong) exceeds this; also the "<== FIRES" display marker). TypeSafe client timeout 30.0. The verifier client is served from TypeSafe's package index.

## The verifier: question battery (Step 3)
One `system_one` call per record, state =
`{system_message, instruction, source_text, schema, extraction}` (see [[state]]); questions keyed `field::metric`. Everything is "programmatically decomposed" ("The TypeSafe Way: Decomposition"): decomposition maximizes the intelligence of every prompt and makes the algorithm tunable and interpretable. Each question is framed so `true` = something is wrong.

Per non-empty field, seven main heads (`type_mismatch` is skipped if the field type is "unknown"):

| Head | true means |
|---|---|
| `name_desc_mismatch` | extracted_field does not match the field name or its description (if description empty, judge against path alone) |
| `type_mismatch` | violates the declared `type` |
| `unreasonable` | a reasonable person would not have extracted this value |
| `hallucinated` | unsupported by, or absent from, the source text |
| `off_target` | source does not genuinely provide this field; value pulled from incidental text |
| `incomplete` | field wrongly empty/null/missing a value the source supports (notes whether field is `required`) |
| `format_violation` | violates format/constraints implied by description, schema type, instructions (date format, units, enum membership) |

- **Empty fields** (None, "", [], {}) get only the `absence_wrong` head: "extracted_field is empty... Does the source text contain the information the field_spec describes, making the empty result wrong?" true = "a value was wrongly omitted", false = "returning nothing is correct".
- `field_spec` per field = `{path, type, description, required}` taken from the schema (unwraps anyOf/null for optional fields). It goes inside the Noul `instructions` as a dict with `field_spec`, `extracted_field`, `main_question`.
- One holistic head `__overall__::judge`: "Is this extracted record an incorrect extraction... so it should be escalated to a smarter model?" Computed and displayed for contrast with per-field heads, but **NOT used in the gate**.
- The full production pipeline also has a `spurious` head (whole containers) and an overall `difficulty` score; not shown here (walkthrough keeps to two gating heads).

## The gate (Step 4)
`any_flag`: escalate if ANY per-field flag (excluding `__overall__*`) exceeds 0.7. A `max`-style gate, not a mean, so one confident red flag is enough instead of being averaged into silence.

## When to use / when NOT to use
- Use when extraction quality matters but most records are easy; the verifier is far cheaper than the reasoning model.
- Schema validation (jsonschema) is necessary but not sufficient: catches structural errors, never semantic ones such as a schema-valid fabrication.
- A vague "is this whole thing good?" judge gives mushy, uncalibrated scores; the per-field battery concentrates signal on the field that is actually wrong.

## Worked example (single record, scrapegraphai row 516)
Dataset: HF `scrapegraphai/scrapegraphai-100k`, pinned revision `4bb9fba1dff9181c5acdb60a5a26fea62fa54fe9`, split train, row index 516.
- Prompt: "Find registration open date fall semester for New York University in New York, NY for the 2024-2025 school year."
- Schema `RegistrationOpen`: required `registration_open_date` (mm/dd/yyyy, e.g. 09/05/2024; "Return a blank string if you are unsure") and `description` (its own field description ships the example "Registration opens for the fall semester").
- Content: NYU events-calendar page ("Fall 2024 Census Date") scrape = only navigation and boilerplate; no registration date and no description. Correct behaviour: decline to invent.

Mini extraction (hard-coded in the walkthrough because `gpt-5.4-mini` is very stochastic here, inventing a different `description` on nearly every run even at temperature=0; real pipeline would call `extract(MINI, ..., temperature=0)`):
`{"registration_open_date": "", "description": "Registration opens for the fall semester"}` -> `schema-valid: True`, yet `description` is fabricated (parrots schema example, or could narrate "not found").

Verifier output (P(wrong), sorted):

| qid | P(wrong) |
|---|---|
| description::hallucinated | **0.95** FIRES |
| description::off_target | **0.85** FIRES |
| description::unreasonable | 0.58 |
| __overall__::judge | 0.56 |
| description::incomplete | 0.16 |
| registration_open_date::absence_wrong | 0.14 |
| description::format_violation | 0.10 |
| description::name_desc_mismatch | 0.08 |
| description::type_mismatch | 0.02 |

Calibration observed: high on the wrong field, low on the correct field (`registration_open_date` blank is right: 0.14), medium on a field that looks off without being clearly wrong. Gate: ESCALATE (fired: hallucinated 0.95, off_target 0.85).

Escalation: `gpt-5.5` with `reasoning_effort="high"` returns `{"description": "", "registration_open_date": ""}`. Field diff: description 'Registration opens for the fall semester' -> ''. The cascade turned a confident schema-valid fabrication into an honest empty field and spent reasoning dollars only because the verifier said so. Extraction parse rule: `json.loads` the reply as-is; on failure treat as empty record `{}` (every field reads absent, verifier flags, gate escalates - safe direction).

## Numbers & limits (100-prompt result, Step 6)
Internal TypeSafe results, same loop `gpt-5.4-mini -> gpt-5.5-reasoning`, `any_flag` gate over per-field heads, 100 scrapegraphai prompts; cheap-rung extractions scored by TypeSafe; gate threshold ("cut") swept 0 -> 1 and every config plotted in (cost, quality). Chart is a historical snapshot; costs NOT recalculated at current Jev rate.
- Four models alone (black diamonds): cost climbs with capability; strongest `gpt-5.5-reasoning` at about **0.81 quality for about $0.10/extraction**.
- Cascade points (blue) form a pareto frontier up-and-left of every single model: most of the top model's quality at a fraction of its cost. Cheap rung handles easy items near-free; only flagged items pay for the reasoning model.
- No exact cascade quality/cost figures are given in text (chart only).

## Appendix A: what makes a good verifier signal
- **Narrow and grounded**: one checkable yes/no about one field vs the source; vague questions give mushy, uncalibrated scores.
- **Bad = TRUE, explicit criteria**: frame so the escalate case is `true`; state what true/false mean.
- **Per-field, aggregate with `max`**: localizes error, stays sparse and strong; one confident flag escalates.
- **Independent and cheap**: a dedicated verifier catches the extractor's blind spots; must be cheap or no savings remain.
- **Separating / calibrated**: high on real errors, low on correct ones so one threshold splits accept vs escalate; that separation pushes the pareto curve up-and-left.

## Gotchas
- Cached via `JsonCache` (`json_cache.json` ships with the cookbook; delete to re-run live).
- `verify()` also returns a `playground_link` built via `make_playground_link(state, questions)`.
- The overall judge (0.56 here) would not have fired at 0.7 either; the per-field heads are the working signal.
- 0.7 threshold is a walkthrough choice (`FIRE_T`); source sweeps 0-1 in the 100-prompt study. See [[confidence]] for picking thresholds.

## Related
[[noul]], [[state]], [[confidence]], [[confidence-gated-routing]], [[speculative-fan-out]], [[cb-pre-parsed-value-extraction]], [[cb-date-extraction]], [[cb-llm-guardrails]], [[topic-extraction]], [[topic-cost-latency]], [[topic-model-selection]], [[cookbooks-overview]]
