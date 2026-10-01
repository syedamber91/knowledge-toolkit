---
title: Pre-Parsed Value Extraction
kind: cookbook
source: Pre-parsed value extraction (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook
tags: [cookbook, extraction, primitives]
topics: [topic-extraction, topic-classification, topic-calibration]
---
# Pre-Parsed Value Extraction
> Regex finds candidate spans (emails, phones, amounts), TypeSafe picks the one the question asks for, code copies it verbatim and normalizes it. Reach for it when you need an exact value out of a document and must never get an invented or digit-transposed one.

## What it is / How it works
Three steps:
1. **Regex finds candidates.** Tune it to over-find (recall over precision).
2. **TypeSafe picks** which candidate the question is asking for, and reads off any attribute the code needs downstream (currency, country, credit-vs-charge).
3. **Code copies the picked value and normalizes it** (lowercase, E.164, Decimal).

Guarantee: TypeSafe only chooses among spans the regex found, so the returned value is one of those spans, copied unchanged. It cannot invent a value or transpose a digit. Model chooses, code owns the string.

Primitives used (see [[primitives-overview]], [[choice]], [[noul]]):
- `pick` = a [[choice]] whose options ARE the candidate spans (criteria value `None` for each) plus an escape-hatch option `none` described as "None of these is the requested value." Returns `{choice, confidence}`.
- `classify` = a [[choice]] over a fixed label set (currency, country). Returns `{choice, confidence}`.
- `is_true` = a yes/no [[noul]]; returns P(yes).
- All calls go through `ts.system_one(state=document, questions={...}, model="jev-1.12")`; `state` is the raw document string. See [[state]].
- Calls cached via cooksafe `JsonCache("json_cache.json")` so re-rendering makes no API calls; API key falls back to the literal "cache-only" so cached re-renders need no key. Client timeout 30.0s; `base_url` defaults to https://api.typesafe.ai/ (env override TYPESAFE_BASE_URL).

Setup: `pip install ipython phonenumbers 'cooksafe>=0.2.0,<0.3.0'`, set `TYPESAFE_API_KEY`. Model constant `TYPESAFE_MODEL = "jev-1.12"` (see [[models-and-versions]]).

Regexes used (recall-tuned; `find` dedupes in document order and strips whitespace):

| Kind | Pattern |
|---|---|
| email | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` |
| phone | `\(?\+?\d[\d\s()\-.]{6,}\d` |
| money | `[$€£¥]\s?\d[\d,]*(?:\.\d{2})?` |

## When to use / when NOT to use
Use when:
- The answer must be a verbatim span of the source (addresses, phone numbers, amounts) and downstream code acts on it.
- The right candidate depends on role/context words, not on the characters (which email is the receipt address, which phone is the mobile).
- You also need attributes inferred from context (country for E.164, currency, credit vs charge).

Do NOT / limits (source's "Two limits"):
- `Choice` allows at most **255 options**. With more candidates, narrow in two stages: pick the section first, then the span inside it.
- Finding candidates is the real work. Emails, phones and amounts have regexes; a **name does not**, so its candidates must come from a roster you already have, a named-entity recognizer, or an LLM that proposes them. TypeSafe then picks.

## Worked examples
### Email: pick by role
Document headers: From dana.whit@acme-corp.com; To billing@acme-corp.com; Cc orders@acme-corp.com; Reply-To dana.personal@gmail.com; body says "please don't use the billing alias... Send my receipt to my personal address instead." Four regex candidates. Two questions over the same candidates:

| Question | Pick | Confidence |
|---|---|---|
| Which email address does the sender want their receipt sent to? | dana.personal@gmail.com (Reply-To line) | 0.98 |
| Which email address did this message come from (the From line)? | dana.whit@acme-corp.com | 1.00 |

Code lowercases the copied value; never re-types it. Answer depends on reading the body, not the headers alone.

### Phone: pick the mobile, normalize to E.164
Doc: San Francisco office; main desk (415) 555-0199, billing fax (415) 555-0142, direct cell (415) 555-0177, "Call the cell if it's urgent." Three candidates, none with a country code.
- `pick` "Which of these is the direct mobile / cell number?" -> `(415) 555-0177`, conf 1.00.
- `classify` "In what country is this office located?" over `["US","GB","DE","FR","CA","AU"]` -> `US`, conf 0.90.
- `phonenumbers.parse(mobile, region)` then `format_number(..., E164)` -> `+14155550177`.
Nothing in the digits says which is the mobile or the country; the surrounding words do.

### Money: pick amount, classify currency, flag credit vs charge
Invoice INV-2087: Subtotal $1,200.00; Sales tax $115.50; Total due $1,315.50; "A $50.00 courtesy credit from last month has already been applied." Four candidates: `$1,200.00`, `$115.50`, `$1,315.50`, `$50.00`.
- `classify` currency over `["USD","EUR","GBP","JPY","CAD"]` -> USD.
- `pick` "Which amount is the total the customer must pay?" -> `$1,315.50`.
- `pick` "Which amount is the courtesy credit that was applied?" -> `$50.00`.
- `is_true` per picked amount: "Is the amount X a credit or refund to the customer, not a charge?"; kind = credit if P > 0.5 else charge.

| Item | Picked | Parsed | P(credit) | Kind |
|---|---|---|---|---|
| total due | $1,315.50 | 1315.50 USD | 0.01 | charge |
| credit | $50.00 | 50.00 USD | 0.99 | credit |

`to_decimal` = `Decimal(re.sub(r"[^\d.]", "", value))`.

## Numbers & limits
| Item | Value |
|---|---|
| Max Choice options | 255 |
| Model | jev-1.12 |
| Client timeout | 30.0 s |
| Email pick confidences | 0.98 (receipt), 1.00 (sender) |
| Phone pick / country confidences | 1.00 / 0.90 |
| Credit-flag P(credit) | 0.01 (total) / 0.99 (credit) |
| Credit threshold in code | > 0.5 |

No latency, cost or accuracy-benchmark numbers given in this page.

## Gotchas
- `to_decimal` assumes comma = thousands separator, dot = decimal point (true for `$1,315.50`). In `€1.315,50` it is reversed. Fix per source: ask a [[noul]] which convention the document uses and branch on it in code.
- Escape hatch `none` is on every selection; handle it (it means no candidate fit).
- Regex must over-find; a missed candidate can never be returned.
- Playground: `make_playground_link(EMAIL_DOC, {"receipt": Choice(...)}, models=[TYPESAFE_MODEL])` builds a share link that opens the thread with the receipt question and the four regex-found addresses as options (criteria = emails + `none`).

## Related
[[choice]], [[noul]], [[state]], [[cb-date-extraction]], [[cb-entity-alignment]], [[cb-sde-cascade]], [[topic-extraction]], [[cookbooks-overview]]
