---
title: Choice Primitive
kind: reference
source: Choice; API reference
source_url: https://docs.typesafe.ai/primitives/choice
tags: [primitives, classification]
topics: [topic-classification, topic-routing]
---
# Choice Primitive
> Select one option from a fixed, unordered set; returns the chosen option, a probability per option, and a confidence. Use for routing and classification.

## What it is / How it works
A Choice answer is the selected option in `choice`; the model also returns a probability for every option in `probabilities` and a `confidence` for the selection.

**Request fields** (per question; the POST body top level is `state`, `model`, `questions`):
- `type`: always `"choice"`.
- `instructions`: the question the model answers.
- `criteria`: map; key = option name, value = description of that option. Description may be `null` (use when the option name is self-explanatory) or string/object/array ([[advanced-structure]]).
- Question ID (e.g. `department`) is chosen by you, returned under the same ID, **never seen by the model**. Option **names and descriptions are both sent to the model** -> write descriptions that separate options from each other.
- Endpoint `https://api.typesafe.ai/v1/systemone` / SDK method `system_one`; `model` selects the model ([[http-api-reference]], [[models-and-versions]]).

Python:
```python
from typesafe_sdk import Choice, TypeSafeClient
with TypeSafeClient() as client:
    response = client.system_one(
        state="My running shoes arrived in the wrong size. Can I swap them for a size 10?",
        questions={"department": Choice(
            instructions="Which team should handle this?",
            criteria={"returns": "Exchanges, wrong or damaged items",
                      "shipping": "Delivery status, delays, lost packages",
                      "billing": "Charges, invoices, payment problems"})})
    print(response.answers["department"].choice)
```

**Response fields**: `type`, `choice` (highest-probability option), `probabilities` (full distribution over every option, sums to 1), `confidence` (0 to 1, computed from how `probabilities` is spread; flat = low, single peak = high; see [[confidence]]). Top-level response also has `model` and `usage` (`input_tokens`, `output_tokens`).

Basic response (easy ticket): `choice: returns`, `confidence 1.0`, probs shipping 0.0 / returns 1.0 / billing 0.0; model `jev-1.13.0`; usage 328 in / 34 out. A ticket mentioning a wrong size AND a missing refund would split probability between `returns` and `billing` and confidence drops.

Example question + options from the page:
- "What programming language is this code written in" -> python, javascript, typescript, go, rust, other
- "What type of meeting is this based on the title and description" -> standup, planning, retrospective, one on one, brainstorm, none of the above
- "Which product category does this item belong to" -> electronics, clothing, home garden, food and beverage

## When to use / when NOT to use
- Use: answer is one of a fixed set (team, category, language).
- Not: position on a spectrum -> [[score]]; yes/no -> [[noul]]. Comparison: [[primitives-overview]].
- Many options: **up to 255 options per question** and each option costs only a few tokens, so give the **full list** of teams/categories rather than a shortlist. Add `other` / `none of the above` when the list might not cover every input.
- Deep taxonomy: chain Choice questions level by level; the Hierarchical Classification cookbook runs a **beam search** over Choice probabilities, keeping the best K candidate paths per level instead of one greedy path ([[cb-hierarchical-classification]], also [[advanced-structure]]).
- Good practice: ask every Choice your code might need in one request (parallel, barely changes latency) and ignore unneeded answers ([[speculative-fan-out]]).

## Worked example: five Choice questions, one ticket
State is an ambiguous shoe-store ticket involving three teams that never says what the customer wants (the page's `<TypesafeExample />` ticket text is not reproduced in the source dump; only the answers are). Questions: `department` (returns/shipping/billing), `return_reason` (wrong_size/wrong_item/damaged/changed_mind/other), `shipping_issue` (not_delivered/delayed/wrong_address/damaged_in_transit/other), `requested_resolution` (exchange/refund/replacement/information), `tone` (calm/frustrated/angry, all descriptions `null`). `return_reason` and `shipping_issue` are **speculative** (only matter if department is returns / shipping).

Response (model jev-1.13.0, usage 589 in / 212 out):
| Question | choice | confidence | probabilities |
| - | - | - | - |
| department | returns | 0.42 | returns 0.61, billing 0.35, shipping 0.04 |
| return_reason | wrong_size | 1.0 | wrong_size 1.0, others 0.0 |
| shipping_issue | delayed | 0.67 | delayed 0.74, other 0.26, rest 0.0 |
| requested_resolution | refund | 0.20 | refund 0.40, replacement 0.34, exchange 0.24, information 0.02 |
| tone | frustrated | 0.76 | frustrated 0.84, angry 0.16, calm 0.0 |

Interpretation: ticket belongs to two teams (double charge -> billing, wrong size -> returns), so confidence 0.42; `shipping_issue` split but ignorable since department != shipping; resolution unspecified by customer, low confidence 0.20.

Routing code logic (from page): 
1. `department.confidence < 0.3` -> manual triage.
2. returns -> assign with `return_reason.choice`; shipping -> assign with `shipping_issue.choice`; else billing.
3. Any other team with `probability > 0.25` gets a copy (billing at 0.35 qualifies).
4. `requested_resolution.confidence < 0.5` -> ask customer what they want; elif choice == refund -> flag for refund approval.
5. `tone.choice == "angry"` -> flag senior agent.
Result for the example: assigned to returns with issue wrong_size; billing gets a copy (0.35 > 0.25); customer asked what they want (0.20 < 0.5); `shipping_issue` unused. Adding e.g. customer language or product = add another Choice; request count stays one. Larger demo: the smart-home demo asks the category, room, device, and action Choices in one call and ignores most ([[demo-smart-home]]).

## Writing options and structured descriptions
- Start with a one-line description per option.
- When two options are similar and the model confuses them, describe each with an **object**: fields for what it covers, what belongs to a neighbouring option instead, and example inputs.
- Example (`return_topic`): options `return_policy` vs `return_status`, both mention returns/refunds so each says what it is *not for*. Response: `return_status`, confidence 1.0 (probs return_policy 0.0, return_status 1.0), usage 407/32. (The request's exact JSON is a rendered widget not present in the source dump.)
- Field names `question`, `focus`, `what`, `not_for`, `examples` are **not part of the API and none are reserved**; you pick them; the model sees names and values, so use short names that label what follows.

## Numbers & limits
| Item | Value |
| - | - |
| Max options per Choice | 255 |
| probabilities sum | 1 |
| confidence range | 0 to 1 |
| Example thresholds in page code | confidence <0.3 manual triage; secondary-team probability >0.25 notify; resolution confidence <0.5 ask customer |
| Basic call usage | 328 in / 34 out tokens |
| 5-question call usage | 589 in / 212 out tokens |

## Gotchas
- Option descriptions are part of the prompt; vague/overlapping ones directly hurt accuracy.
- Without an `other` option the model must pick among given ones -> forced mis-classification on out-of-list input.
- `choice` is just the argmax; check `probabilities`/`confidence` before acting. Split probability = multi-team case.
- Question ID is not sent to the model.

## Related
[[primitives-overview]] -- [[score]] -- [[noul]] -- [[advanced-structure]] -- [[confidence]] -- [[http-api-reference]] -- [[cb-hierarchical-classification]] -- [[cb-classification-using-confidence]] -- [[intent-routing]] -- [[confidence-gated-routing]] -- [[topic-classification]] -- [[topic-routing]]
