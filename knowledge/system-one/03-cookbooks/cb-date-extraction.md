---
title: Cookbook - Date Extraction
kind: cookbook
source: Date extraction (TypeSafe docs cookbook)
source_url: https://docs.typesafe.ai/cookbooks/date_extraction_cookbook
tags: [cookbook, extraction, confidence]
topics: [topic-extraction, topic-calibration]
---
# Cookbook: Date Extraction
> Read a date's PARTS off the text with 7 `Choice` questions in one call, then resolve them to a real `date` in code (code does the calendar math, never the model); min-confidence across used parts gates human review.

## What it is / How it works
`extract_date(document, role)` takes a document and a phrase naming the wanted date ("the deadline to return the form") and returns a `date`, a confidence, a `needs_review` flag and a note. Handles absolute ("August 14, 2027") and relative ("tomorrow", "next Thursday") dates, flags low-confidence reads, flags dates whose parts do not assemble, and flags dates the doc never states. TypeSafe reads what the text says; code turns answers into a `date` counting from `TODAY`.

### The 7 Choice questions (one call, `role` interpolated)
| Part | Options | Role |
|---|---|---|
| `mode` | `absolute` (names a month), `relative` (today/tomorrow/day after/named weekday), `none` (not stated) | How the date is written; code reads only the parts mode calls for |
| `month` | 12 month names + `none` | absolute only |
| `day` | "1".."31" + `none` | absolute only |
| `year` | one option per year **1900..2050** (151) + `out_of_range` (stated but outside list; code flags, doesn't guess) + `none` (no year stated; code infers) | absolute only |
| `day_anchor` | `today`, `tomorrow`, `day_after` (day after tomorrow), `weekday`, `none` | relative |
| `weekday` | Monday..Sunday + `none` | when a weekday is named |
| `week_offset` | `current` ("this Thursday"), `next` ("next Thursday"/"Thursday next week"), `none` (bare weekday) | which week |

Criteria values are `None` (no per-option description) except escape options which carry the text "The document does not state this, or it is not this kind of date." Tip in source: if a 153-option year list bothers you, pull year-like numbers out of the text first and offer only those.

### Resolution rules (code, `assemble()`)
- Call: `client.system_one(state=document, questions=date_questions(role), model="jev-1.12").answers`, keep `{part: {choice, confidence}}`.
- `mode == none` -> date None, note "no such date stated".
- `absolute`: if month/day is `none` or day not digit or month unknown -> None, "absolute date incomplete". `year == out_of_range` -> None, "year outside 1900-2050". `year == none` -> use `TODAY.year`; if resolved date < TODAY - 31 days, use next year. Invalid (e.g. February 30) -> None, "impossible date". Stated year -> `date(year, month, day)`.
- `relative`: today -> TODAY; tomorrow -> +1; day_after -> +2; weekday -> `resolve_weekday`.
- Weekday convention: bare weekday = next occurrence **on or after** today (`(w - today.weekday()) % 7`); `next` = the following calendar week (this Monday + 7 + w); `current` = this week (this Monday + w). "next Thursday" is ambiguous, so code decides.
- Confidence = **min** of the confidences of the parts actually used (mode plus its dependent parts), so one weak part sends the whole date to review.
- `needs_review` = date is None, or confidence None, or confidence < `REVIEW_BELOW` = **0.60**.
- Pinned `TODAY = date(2026, 7, 30)` (a Thursday) so relative dates reproduce.

## Worked example (6 questions, 4 documents; model jev-1.12)
| Document | Role | Expected | Got | Conf | Flag |
|---|---|---|---|---|---|
| CONTRACT "effective January 1, 2025 and expires December 31, 2027." | agreement takes effect | 2025-01-01 | 2025-01-01 | 0.97 | - |
| same | agreement expires | 2027-12-31 | 2027-12-31 | 0.91 | - |
| FORM "return the signed form by August 14." | deadline to return form | 2026-08-14 | 2026-08-14 | 0.95 | - |
| same | date of the kickoff call | none | none | 0.46 | review ("absolute date incomplete") |
| SURVEY "customer survey closes today at 5pm." | survey closes | 2026-07-30 | 2026-07-30 | 0.94 | - |
| REVIEW "schedule the design review for next Thursday." | design review | 2026-08-06 | 2026-08-06 | 0.92 | - |

Result: all 6 match expectation; 5 auto-accepted, 1 sent to review. Contract years came off the text; form has no year so code filled 2026; "today" and "next Thursday" use the same function. Kickoff call: form has a date, just not this one — `mode` came back `absolute` with no month, date empty, confidence 0.46 -> flagged.

## When to use / when NOT to use
- Use when you need typed, verifiable dates from messy text; model reads, code computes (never ask model for date arithmetic).
- Year list is long; consider pre-filtering year-like numbers. Convention for week offsets is yours to set.
- Source gives no accuracy benchmark beyond these 6 rows.

## Numbers & limits
| Item | Value |
|---|---|
| Questions | 7 Choice in 1 call |
| Year window | 1900-2050 (+ out_of_range, none) |
| REVIEW_BELOW | 0.60 |
| No-year bump | date more than 31 days in past -> next year |
| TODAY (pinned) | 2026-07-30 (Thursday) |
| Client timeout | 30.0s; base_url from env `TYPESAFE_BASE_URL` |
| Setup | `pip install ipython 'cooksafe>=0.2.0,<0.3.0'`, `TYPESAFE_API_KEY`; cached in `json_cache.json` (delete for live) |

## Gotchas
- Absolute date with `none` month/day or impossible combos is treated as "no date" and routed to review, not guessed.
- `out_of_range` is flagged (None), not auto-resolved.
- Env var here is `TYPESAFE_BASE_URL` while the other cookbooks use `TYPESAFE_ENDPOINT` (source inconsistency; same client param `base_url`).
- Demo code gated by `if __name__ == "__cookbook__":` so calendar math is unit-testable.
- A playground link carries the "next Thursday" message with the same questions.

## Related
[[choice]] · [[confidence]] · [[cb-pre-parsed-value-extraction]] · [[cb-sde-cascade]] · [[confidence-gated-routing]] · [[cookbooks-overview]] · [[topic-extraction]]
