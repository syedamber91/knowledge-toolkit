---
title: Jev 1.13 Jaggedness
kind: reference
source: Model jaggedness > Jev 1.13
source_url: https://docs.typesafe.ai/model-jaggedness/jev-1.13
tags: [model-limits, guardrails, system-one]
topics: [topic-model-selection, topic-guardrails]
---
# Jev 1.13 Jaggedness (known weaknesses)
> Nine documented failure modes of `jev-1.13` with the prescribed workaround for each. An agent should consult this to decide when NOT to call Jev (or how to reshape the question). Source: "Applies to `jev-1.13`. Last reviewed 2026-09-17." Many are expected to be fixed in later versions.

## What it is / How it works
Overall characterization (source): `jev-1.13` is fast, calibrated and good at common-sense judgment but not perfect. It does best on [[system-one-model-category|System One]] tasks. It **may struggle with tasks that require additional levels of indirection**, can be **quite literal**, and **struggles with numeric precision**.

## Quick decision table (the 9 failure modes)
| # | Failure mode | Do this instead |
| - | - | - |
| 1 | Literal reading | Write the exact condition; criteria for each option |
| 2 | Math and numbers (counting, numeric representations, math using score) | Keep the arithmetic in code |
| 3 | Date and time comparison | Extract components; compare in code |
| 4 | Indirection | Reduce hops; point to the relevant state |
| 5 | Large state full of irrelevant detail | Filter first; send only what the question needs |
| 6 | Adversarial content | Write precise prompts, test edge cases before deploying |
| 7 | Contradictory instructions and criteria | Align the criteria and instruction |
| 8 | Common-sense structural invariants | Ask each decision one way; enforce identities in code |
| 9 | Generation | Use a generative model |

## When NOT to call Jev (derived directly from the list — "As a reminder, avoid")
- Asking the model something **code can compute exactly**.
- **Hiding several judgments inside one question.**
- **System Two tasks:** more layers of indirection.
- **Giving it more context in `state` than the question needs** — Jev suffers from context rot; unrelated material costs accuracy.

## The failure modes in detail

### 1. Literal reading
- `jev-1.13` answers the question you *wrote*, not the one you *meant*. Scoping words, negations and implied conditions are read at face value; a person might read the intent behind the instruction, the model reads the words.
- **Instead:** state the exact condition in `instructions`; be specific; put boundary cases in the criteria. If, when looking at a wrong answer, you find yourself explaining what you *really* meant, that explanation is the missing half of the instruction. Where interpretation is unavoidable, **split into two literal questions and combine in code**.

### 2. Math and numbers
Jev is **not a calculator**; strongly recommended to implement any mathematical logic in code. It performs better on semantic than mathematical questions.
- **2a. Counting** — does **not** count reliably: characters in a word, occurrences of a term in a passage, items in a long list. It recognizes the *shape* of an answer rather than tallying; **error grows with the size of the thing counted**. Before asking a counting question, ask why the count needs a model at all: if a regex/parser can find the unit, count in code. **Instead:** iterate in code over candidates, ask one question per candidate, add up the answers yourself.
  ```python
  items = ["typesafe","apple","california","banana","likes","calibration","orange","vertex"]
  result = client.system_one({"items": items},
      {f"item_{i}": Noul(instructions=f"Is `items[{i}]` the name of a fruit?") for i in range(len(items))})
  count = sum(result.nouls[f"item_{i}"].noul > YES for i in range(len(items)))   # YES = 0.5, tune per use case
  ```
  (Client created with `TypeSafeClient(model="jev-1.13")`; the 0.5 threshold is "up to you … depends on your usecase". The example uses backtick-referenced list indices, `items[i]` — see [[how-to-build-with-system-one]].)
- **2b. Numeric representations** — performs better on **semantic** than **numeric** representations. E.g. colors via hex values underperform vs English names; given RGB triples or hex values it **cannot reliably judge whether two values are near each other**. Likewise high-level programming languages beat low-level assembly or binary-encoded instructions. **Instead:** do the conversion in code; pass the computed number or a named bucket; keep the model for the genuine judgment (e.g. whether a color reads as a warning).
- **2c. Math using score** — do **not** use Score outputs (expectation, probability) to compute the exact magnitude of a number between two levels of a criterion. You may use the expectation to check whether it passes a particular threshold, but Score levels are **weak in numerical calibration**; it cannot reconstruct an exact number by interpolating between the nearest two levels. (See [[score]].)

### 3. Date and time comparison
- Reads dates **as text, not as ordered quantities**. Which of two dates comes first, how far apart, whether one is inside a window — **unreliable**. Worse with mixed formats, relative references, and domain boundaries (quarters, settlement windows, accrual periods).
- **Instead — split the work:** extraction is a judgment (model); arithmetic is not (code). Each date part is a small closed set (12 months, 31 possible days, bounded range of years), so extraction becomes a [[choice|Choice]] over enumerated options rather than free-form parsing, with an explicit **"not stated"** option so a missing part is reported rather than guessed. Code assembles parts into a real date and owns ordering, duration, offset, weekday. Worked version incl. relative dates and confidence gating: [[cb-date-extraction]].

### 4. Indirection
- Instructions with **double negatives** or complex indirection are answered less reliably. A question about a property of a property, or needing multiple hops of reasoning, costs accuracy.
- **Instead:** write instructions as directly as possible; when possible identify the relevant parts of state **by name**.

### 5. Large state full of irrelevant detail
- Accuracy **falls** as the state grows with content unrelated to the decision. Unrelated detail is a **distractor**, and a large state makes it harder to tell which part of the input produced a wrong answer.
- **Instead:** retrieve and filter in code first; send only the fields the question needs. When filtering in state isn't possible, use a [[noul|Noul]] to filter for relevance — worked example in [[cb-classifying-rag-passages]].
- Context window is bounded: exact limits in [[models-and-versions]] (64k per request; 32k for state + longest question).

### 6. Adversarial content
- State is data, and `jev-1.13` does **not** treat it as hostile by default. Content written to adversarially steer the model — an **injected instruction**, a **deliberately misleading framing**, or **text that argues for its own classification** — can move the answer. The vendor expects to improve this.
- **Instead:** be explicit in the criteria; **test your integration thoroughly before deploying to many users.**

### 7. Contradictory instructions and criteria
- When `instructions` and `criteria` ask for different things, the model might get confused. Best performance = clear phrasing. Example: a Noul where `true` maps to "no" and `false` maps to "yes" performs **worse**. Aim for instructions easy for the average person to read.
- **Instead:** treat criteria as an extension of the instruction; align the two with clear, precise language.

### 8. Common-sense structural invariants
`jev-1.13` is extremely **consistent** (quantitatively similar outputs for semantically similar inputs), but many structural invariants you might imagine **are not guaranteed**.

Worked example A — same question as Noul vs yes/no Choice. Question: "Is the customer asking for a refund?" on ticket *"I'm not happy with the fit. What are my options here?"*
| Noul `noul` | Choice `yes` | Choice `no` | Choice `confidence` |
| - | - | - | - |
| 0.22 | 0.01 | 0.99 | 0.97 |
Comparable numbers are `noul` and `probabilities["yes"]` (0.22 vs 0.01); how to interpret the Choice output/confidence for the Noul question, or vice versa, is "not obvious".

Worked example B — question and its negation as two Nouls. "Is the customer asking for a refund?" vs "Is the customer asking for something other than a refund?" on ticket *"I was charged twice for the same order. Can someone look into this?"*
| `refund` | `not_refund` | Sum |
| - | - | - |
| 0.72 | 0.47 | **1.19** (not 1.0) |
"There are many reasons that `P(noul)` and `1 - P(not noul)` may not be directly comparable."

- **Instead:** don't rely on expected structural invariance; word questions to mean directly what you want. **Don't carry a threshold tuned on a Noul over to a Choice**, and don't hold the model to arithmetic identities between separate questions. A Choice over options and one Noul per option answer *different* questions: Choice is **relative** (settles *which* option), each Noul is **absolute** and can be low for all of them. [[cb-skill-suggestion]] uses both on the same shortlist — Choice to pick a skill, Nouls to decide whether to suggest one at all.

### 9. Generation
- Not trained to generate text. You *can* force it by chaining choices, but it will **not work well and will be very slow**. For data extraction: extract candidate options with regex or a generative model and let Jev **pick** the correct extraction.
- **Instead:** when the answer space is bounded, turn extraction into a Choice over the options rather than asking for the value itself. If you really need generation: "there are other models for that."

## Numbers & limits
| Item | Value |
| - | - |
| Version covered | `jev-1.13`; last reviewed 2026-09-17 |
| Example Noul threshold in counting snippet | 0.5 (user-tuned) |
| Context window | see [[models-and-versions]] |
| Noul pair sum in example B | 0.72 + 0.47 = 1.19 |

## Gotchas
- Jev itself does not flag these cases; confidence may still look high (e.g. Choice confidence 0.97 in example A on a Noul-comparable question) — don't treat confidence as proof the task fit the model.
- Items 1/4/7 are *wording* fixes; items 2/3/9 are *use code instead*; 5 is *filter state*; 6 is *test*; 8 is *don't assume cross-question identities*.
- Source invites reports of new failure modes via Discord (discord.com/invite/WUujKYBp8s).

## Related
[[models-and-versions]] · [[how-to-build-with-system-one]] · [[state]] · [[confidence]] · [[cb-date-extraction]] · [[cb-classifying-rag-passages]] · [[cb-skill-suggestion]] · [[composite-scoring]] · [[topic-model-selection]] · [[topic-guardrails]]
