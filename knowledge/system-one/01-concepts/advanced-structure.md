---
title: Advanced Structure (JSON in Instructions and Criteria)
kind: concept
source: Advanced - structure
source_url: https://docs.typesafe.ai/primitives/advanced
tags: [primitives, system-one]
topics: [topic-state-design, topic-classification]
---
# Advanced Structure (JSON in Instructions and Criteria)
> Instructions, Choice option descriptions, Score level descriptions and Noul criteria all accept JSON (object/array) because System One models are trained to understand structure.

## What it is / How it works
Every one of these fields is an `EntryType` (SDK type alias):
| Field | Applies to | Accepted shape |
| - | - | - |
| `instructions` | Choice, Score, Noul | string, object, array, or null |
| `criteria` values (option descriptions) | Choice | string, object, array, or null |
| `criteria` entries (level descriptions) | Score | string, object, array, or null |
| `criteria.true` / `criteria.false` | Noul | string, object, array, or null |

Field names inside objects are yours (none reserved); the model sees both names and values, so use short labelling names ([[choice]]).

## When to use / when NOT to use
- **When it helps clarity**: a question with multiple parts is clearer as JSON because keys label the parts.
- **When the question needs supporting data**: a schema, taxonomy or DB row is already JSON -- pass it (or the relevant subfields) directly rather than serializing into a string template.
- Otherwise start with plain strings (stated repeatedly on [[choice]], [[score]], [[noul]]).

## Structured instructions
One `field` object describes the field being checked and each question refers to it by key. The same shape drives a Noul that verifies a value, a Choice that picks one from candidates, and two Scores that place a value on a scale. In code you could loop over potential records and build one question per field, all in a single call (SDE cascade cookbook does similar: [[cb-sde-cascade]]). (The concrete request of this example is a rendered widget not present in the source dump.)

Arrays work for a list of things to check/compare:
```json
"instructions": {
  "question": "Does the claimed sender identity conflict with the sending domain?",
  "compare": ["ticket.sender.display_name", "ticket.sender.email"],
  "focus": "Compare the named organization with the email domain."
}
```
(The compare values are dot-paths into the state, see [[state]] and path-reference convention in [[primitives-overview]].)

## Structured Choice options
- **JSON rubric for boundary clarification**: each option's description is an object saying what it does and does *not* cover; sharpens the boundary between options (example in [[choice]]: `return_policy` vs `return_status` -> answered `return_status` at confidence 1.0).
- **Walking a taxonomy**: for a deep taxonomy ask **one Choice per level and walk the tree in code**. At each step the options are the children of the current node and **each option's value is that child's subtree**, so the model can see what lives under a branch before committing (matters when the leaf name isn't obvious from the branch name).
  - Example: product listing of a bike water bottle; first Choice picks top-level department. It plausibly fits two: `Sporting Goods > Cycling > Bike Bottles & Cages` and `Home & Kitchen > Drinkware > Water Bottles`. Seeing the subtrees lets the model weigh the listing's emphasis on bike cages against everyday drinkware; `probabilities` tell you whether the split is close enough to explore both branches.
  - Then ask the next Choice with that department's children as options and their subtrees as values; repeat to a leaf. In code: a loop over a nested dict where each question's `criteria` is simply the current node.
  - The Hierarchical Classification cookbook shows a similar walk including **beam search** keeping several candidate paths alive when probabilities are close ([[cb-hierarchical-classification]]).
  - **Subtrees can get large: if a branch is too large, trim the value to its direct children and a sample of leaves.**

## Structured Score levels
Each entry in a Score `criteria` array can be an object (e.g. `what` + `examples`; same field names on every level). Effects, with numbers, are in [[score]] (matching example 1.43/0.35 -> 1.03/0.96; unrelated example gives no change).

## Structured Noul criteria
Optional; when the yes/no boundary is subtle, structured `true` and `false` descriptions pin it down with a **definition and examples on each side**. (Example request is a widget not in the dump.) See [[noul]].

## Numbers & limits
No numeric limits are given on this page. Related: Choice max 255 options; Score max 10 levels ([[http-api-reference]]). Size/token cost of large subtrees: not quantified in source -- only the advice to trim.

## Gotchas
- Large taxonomy subtrees bloat the prompt: trim to direct children + sample leaves.
- Examples only help when they resemble real inputs ([[score]]).
- Keep field names consistent across levels/options so the model compares like with like.

## Related
[[primitives-overview]] -- [[choice]] -- [[score]] -- [[noul]] -- [[state]] -- [[how-to-build-with-system-one]] -- [[cb-hierarchical-classification]] -- [[cb-sde-cascade]] -- [[http-api-reference]] -- [[topic-state-design]]
