---
title: How To Build With System One
kind: playbook
source: Concepts > How to build with TypeSafe
source_url: https://docs.typesafe.ai/concepts/how-to-build-with-system-one
tags: [system-one, patterns, state-design]
topics: [topic-state-design, topic-routing, topic-calibration]
---
# How To Build With System One
> Design recipe: keep code in control of the workflow, give System One narrow typed questions, run many in one parallel request, combine in code, route on confidence. Includes the 8-step workflow and a full triage example.

## What it is / How it works
System One is for building **AI-powered software, not agents**. It doesn't generate code or choose its next action; it provides AI primitives that embed into software; code stays in control while the model does common-sense judgments over unstructured data.

**Summary box:** build a normal software workflow and insert System One only where AI is needed. (1) Keep control flow, deterministic rules, side effects in code. (2) Break broad judgments into narrow typed questions with explicit instructions/criteria. (3) Give each question only the context it needs. (4) Use probabilities and confidence to act, ask for review, or escalate. (5) Ask independent questions together, then compose answers in code.

### Three software architectures
| Architecture | Characteristics (source) |
| - | - |
| Traditional software | Complex decision tree made of simple, reliable primitives, composable into higher abstractions |
| LLM agents | Agent processes instructions and chooses its next step; fine when a person monitors it, but **every loop is another opportunity to go off the rails** |
| AI-powered software (TypeSafe's target) | Code handles deterministic work and owns control flow; model appears only for programmable common sense / interpreting unstructured data; each AI task atomic and constrained |

### What makes System One composable (six properties)
| Property | Claim |
| - | - |
| Structured | Type-safe by construction; decisions/probabilities conform to your JSON schema; never recover a value from prose |
| Parallel | Questions evaluated independently in parallel; one result never becomes hidden context for another |
| Comparable | Outputs sortable; drive `if` statements, thresholds, comparisons |
| Fast | **Most queries complete in about 100 ms**; fast enough for real-time request paths and UIs |
| Calibrated confidence | RLCD ([[ai-primer-calibrated-decisions]]) gives calibrated probabilities instead of tending toward overconfidence |
| Self-consistent | Designed to return stable answers across repeated evaluations ([[cb-consistency-nouls]]) |
- Output is constrained to supplied options, so the model returns a **full probability distribution over those options** rather than inventing a value outside the schema.
- Vendor target: **>100x intelligence-to-speed-and-cost ratio**; underlying bet: cheaper intelligence creates much more demand.

## The 8-step workflow
1. **Use code when you can.** Deterministic work stays in code (reliable, cheap). Avoid agent `while` loops when a software workflow can express it. Example: `days_overdue = (today - invoice.due_date).days; if days_overdue > 30: route_to_collections(invoice)`. See [[patterns-overview]].
2. **Decompose the input state.** Include only context relevant to the current questions (avoids distraction and context rot). Don't rely on knowledge in model weights when current info can come from your own knowledge base. ([[state]])
3. **Use structure in the input state.** Nested JSON for `state` and `questions`. Point questions at specific values with a **backticked dot-and-index path** such as `support.tickets[0].message` — **include the backtick characters around each path inside the question**. (Same convention in the counting snippet in [[jev-1-13-jaggedness]]: `` `items[3]` ``.)
4. **Decompose the questions** — flagged as "probably the most important concept in this guide". Ask the most explicit, narrow, specific, atomic questions you can; break complex/ill-defined questions into separate questions each evaluating one property. Broad questions hide several judgments behind one answer; atomic ones let you inspect, tune, combine. Source examples: *spam detection* (one broad question = bad vs several decomposed = good — see the triage code below for the decomposed spam signals) and *verifying a tool-call trace* (broad vs decomposed). The question text of the broad/decomposed examples is a rendered component in the source and **not captured** in the page text.
5. **Use structure in the questions.** Keep questions short; `instructions` and `criteria` are usually strings but can be **objects or arrays**. Put the question in one field and the guiding data in others. Structure helps when:
   - the question needs **context or examples** (named fields next to the question, which code can swap without rewriting it);
   - **part of the question comes from your code** (put DB values in their own field instead of splicing into a string template; e.g. a Noul compares a resume in state with a record placed in `potential_duplicate`, referred to by name in backticks; the record can change over time);
   - **several questions have similar instructions** (supplementary data makes them distinct).
   - Criteria descriptions can be objects too: for a Choice, each option's description can say what it covers, what belongs to a different option, and a few examples; **use the same field names across options** so the model can compare them directly.
   - Per-primitive worked examples: [[noul]] (one resume vs several candidate records, one question per record, built in code), [[choice]] (two easily-confused options with covers/not-for/examples), [[score]] (each level with description and example situations). Shared-wording case: [[cb-sde-cascade]]. A short unambiguous question/criterion can stay a string. Full list of places structure is accepted: [[advanced-structure]].
6. **Ask a lot of questions.** Many narrow independent questions about the same state in one request maximizes "intelligence per dollar": parallel, no serial round trips. See [[speculative-fan-out]], [[cb-parallel-questions]]. Tip: decomposition does not require more round trips.
7. **Combine outputs in code (or feed a classical ML model).** Deterministic rules or weighted sums; for learned composition use probabilities as features in a downstream classical model. If you lack labels, **use an ensemble of expensive reasoning models to generate them** ([[cb-autoresearch-feature-discovery]]). Example:
   ```python
   quality = (0.4*answers["answers_request"].noul
            + 0.4*answers["citations_are_supported"].noul
            + 0.2*(1 - answers["contradicts_context"].noul))
   ```
   See [[composite-scoring]].
8. **Route on uncertainty.** Different actions for confident vs unconfident answers; escalate to a person or a more expensive reasoning model; **test thresholds by plotting confidence against accuracy on your data.** Example: `if answer.confidence < 0.8: route_to_human_review(ticket) else: route_to_handler(answer.choice, ticket)` (question `card_help_topic`). See [[confidence]], [[confidence-gated-routing]].

## Worked example — `triage_ticket(ticket, customer)` (full pipeline)
Flow:
1. **Deterministic short-circuit:** `ticket["status"] == "closed"` -> return `"no_action"` (no model call). Filter `open_orders` = customer orders whose status != "delivered".
2. **State (only what's needed):** `ticket{message, sender, links}`, `customer{plan, open_orders}`, `policy{sensitive_credentials: ["password","security code","API key"]}`.
3. **Seven questions, one request** (`TypeSafeClient()` as context manager, `client.system_one(state=..., questions=...)`):
   | Question | Type | Design notes |
   | - | - | - |
   | `topic` | Choice | instructions object {question: "Which team should handle `ticket.message`?", focus: primary request}; criteria objects per option with `what` / `not_for` / `examples`: billing (charges/invoices/refunds/subscriptions; not order tracking/account access), orders (status/delivery/cancel/returns; not charges/account access), account (login/profile/permissions/security; not charges/order tracking) |
   | `requests_credentials` | Noul | compare `ticket.message` vs `policy.sensitive_credentials`; focus: request to disclose the credential itself; true = asks recipient to disclose a listed credential ("Reply with your password"); false = no such ask, **not_for a legitimate reset instruction** ("Use this link to reset your password") |
   | `sender_identity_mismatch` | Noul | compare `ticket.sender.display_name` vs `ticket.sender.email`; named org vs email domain; true e.g. "Acme Payroll sent from claim-bonus.example"; false e.g. same org/domain |
   | `unexpected_reward` | Noul | inspect `ticket.message`; unsolicited prize/payment/reward; false not_for a customer asking about a known refund/payroll deposit |
   | `refund_requested` | Noul | require a requested remedy, **not a billing complaint alone**; false example "Why was I charged twice?" |
   | `mentions_open_order` | Noul | compare message vs `customer.open_orders`; match id or identifying details; false for a generic order question |
   | `frustration` | Score (3 levels, each with `what` + `signals`) | judge expressed frustration, **not issue severity**: calm/matter-of-fact; frustrated but civil; very angry or threatening to leave |
   Noul criteria use `NoulCriteria(true={...}, false={...})`; imports `Choice, Noul, NoulCriteria, Score, TypeSafeClient`.
4. **Composite spam score in code:** `spam_risk = 0.45*requests_credentials + 0.30*sender_identity_mismatch + 0.25*unexpected_reward` (noul values).
5. **Gates:** `spam_is_uncertain = 0.4 < spam_risk < 0.6`; if uncertain **or** `topic.confidence < 0.75` -> `route_to_human_review`; elif `spam_risk >= 0.6` -> `quarantine_as_spam`.
6. **Speculative answers used only on relevant path:** billing -> `route_to_billing(refund_requested = noul >= 0.7)`; orders -> `route_to_orders(mentions_open_order = noul >= 0.7)`; otherwise `priority = "high"` if `frustration.confidence >= 0.7` and `frustration.score >= 1.5` else `"normal"` -> `route_to_account_support`.

## When to use / when NOT to use
Use for any workflow where code can own control flow. Don't use for tasks listed under [[jev-1-13-jaggedness]] (math, dates, generation, indirection).

## Numbers & limits
| Item | Value |
| - | - |
| Typical latency | "about 100 ms" for most queries |
| Cheap-confidence example thresholds | `confidence < 0.8` -> human (step 8) |
| Triage: spam uncertainty band | 0.4 < risk < 0.6 -> human; >= 0.6 -> quarantine |
| Triage: topic confidence floor | 0.75 |
| Triage: Noul thresholds | refund / open-order >= 0.7 |
| Triage: frustration | score >= 1.5 and confidence >= 0.7 -> high priority |
| Spam weights | 0.45 / 0.30 / 0.25 |
All thresholds are the source's illustrative values; the docs say tune on your data.

## Gotchas
- Backticks are required around paths inside questions.
- Keep side effects in code, not in questions.
- Hidden-component gap: several `TypesafeExample` blocks (state-decomposition, nested-reference, spam, tool-call-trace, resume-duplicate, contrastive-Choice) are not in the page text; only the full triage example is.

## Related
[[state]] · [[advanced-structure]] · [[patterns-overview]] · [[speculative-fan-out]] · [[composite-scoring]] · [[confidence-gated-routing]] · [[intent-routing]] · [[cb-autoresearch-feature-discovery]] · [[jev-1-13-jaggedness]] · [[topic-state-design]] · [[topic-routing]] · [[topic-calibration]]
