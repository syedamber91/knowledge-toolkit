---
title: Cookbook - Double-Checking Citations
kind: cookbook
source: Double-checking citations (TypeSafe docs cookbook)
source_url: https://docs.typesafe.ai/cookbooks/citation_check
tags: [cookbook, guardrails, evaluation]
topics: [topic-guardrails, topic-calibration, topic-classification]
---
# Cookbook: Double-Checking Citations
> Catch wrong or hallucinated LLM citations: an ordinary string match finds fabricated quotes, then ONE `Choice` question reads the quote's section and decides supports / contradicts / says nothing; a 0.8 confidence gate sends weak verdicts to a human.

## What it is / How it works
Problem: an LLM answers a question and attaches citations (claim + source section + quote). Some are wrong: the quote may be absent from the document, or present word-for-word while its context says the opposite. Manual check is slow.

`check_citation(sections, citation)` returns one of four verdicts (`verified`, `unsupported`, `contradicted`, `fabricated`) plus a confidence flagging which a human should review.

Pipeline (two steps):
1. **String match (no model).** Normalize whitespace and fold curly quotes (`“ ” ‘ ’` -> straight), then substring search across numbered sections (sorted numerically, e.g. "4.1.3"). Quote not found -> `missing` -> verdict `fabricated`, confidence `None` (no model called), `auto=True`. Found -> the containing section is the text for step 2 (status `found`). Citation with no quote (`quote: null`) -> status `section-only`; take the section the citation names and go straight to the model.
2. **Choice question** ("How does the section relate to the claim?"), one per surviving citation, sent via `client.system_one(state={"claim":..., "section":...}, questions=QUESTIONS, model="jev-1.12")`:

| Option | Meaning | Verdict |
|---|---|---|
| `supports` | Section states the claim or directly implies it is true | verified |
| `contradicts` | Section states the opposite or implies it is false | contradicted |
| `says_nothing` | Section does not address what the claim asserts, either way | unsupported |

Highest-probability option is the verdict. Gate: `AUTO_ACCEPT = 0.8`. Confidence >= 0.8 -> verdict stands; < 0.8 -> a human confirms before anything acts on it. Advice: "start high" (more human review) and lower the threshold as you learn how the model does on your own documents.

Flow (mermaid in source): cite -> match? -> found/no quote -> Choice request; not found -> fabricated. Choice -> confidence >= 0.8? -> stand / human confirms.

## When to use / when NOT to use
- Use: verifying RAG/LLM answers with citations against a known source doc; detecting contradiction, not only absence.
- NOT sufficient alone: string match; its example `pii_encryption` quote is verbatim in the source, yet its section says nothing about the claim.
- The match is exact after normalization: a truncated or lightly reworded quote comes back `fabricated`. A production system tolerant of sloppy quoting would need fuzzy matching (not built here).
- `load_source()` / `split_sections()` are written for an RFC's layout; other document shapes need their own parsing.

## Dataset / setup
- Source: RFC 7519 (JSON Web Token) from rfc-editor.org, saved as `rfc7519.txt`; page headers/footers stripped (regexes for "Jones, et al. ... [Page N]" and "RFC 7519 JSON Web Token (JWT) May 2015" lines), 3+ blank lines collapsed. Result: **58,365 characters, 45 numbered sections, 8 citations**.
- `citations.json`: 8 citations written by an LLM against the RFC; 4 accurate, 4 edited to fail. Fields: `id`, `claim`, `quote` (nullable), `section`.
- Install: `pip install ipython 'cooksafe>=0.2.0,<0.3.0'`; set `TYPESAFE_API_KEY`. Every API call is cached in shipped `json_cache.json` (replays published numbers; delete to run live). Client: `TypeSafeClient(api_key=..., base_url=env TYPESAFE_ENDPOINT, timeout=120.0)`. Numbers from **`jev-1.12` on 2026-08-16**.
- Response fields read: `answer.choice`, `.probabilities`, `.confidence`, `response.usage.input_tokens/output_tokens`.

## Worked example: step 1 results
| id | status | section size |
|---|---|---|
| epoch_seconds | found | 3,122 chars |
| aud_reject | found | 761 chars |
| sig_reporting | missing | - |
| clock_skew | found | 529 chars |
| exp_required | found | 529 chars |
| pii_encryption | found | 1,653 chars |
| iat_future | section-only (quote null, section 4.1.6) | 270 chars |
| duplicate_names | found | 918 chars |

Sample citation: `aud_reject`, claim "If a validator does not find itself in a token's audience list, it has to reject the token.", quote from section 4.1.3 ("...MUST be rejected."). Claim-only sample: `iat_future` ("iat" requires rejecting future-issued tokens, section 4.1.6, quote null).

## Final results (all 8)
| citation | quote | relation | conf | verdict | action |
|---|---|---|---|---|---|
| epoch_seconds | found | supports | 0.93 | verified | auto |
| aud_reject | found | supports | 0.95 | verified | auto |
| sig_reporting | missing | - | - | fabricated | auto |
| clock_skew | found | supports | 0.99 | verified | auto |
| exp_required | found | contradicts | 0.99 | contradicted | auto |
| pii_encryption | found | says_nothing | 0.27 | unsupported | review |
| iat_future | section-only | says_nothing | 0.56 | unsupported | review |
| duplicate_names | found | supports | 0.99 | verified | auto |

Outcome: 4 verified, 1 fabricated, 1 contradicted, 2 unsupported; all four planted failures caught (fabricated quote, contradicted claim, two unsupported sent to a human). The 4 accurate ones were verified at >= 0.93. `exp_required` quotes 4.1.4 verbatim but the same section says "Use of this claim is OPTIONAL", so contradicted at 0.99. `pii_encryption` (0.27) and `iat_future` (0.56) fell under 0.8 -> human.

## Numbers & limits
| Item | Value |
|---|---|
| Model | jev-1.12 |
| AUTO_ACCEPT | 0.8 |
| Lowest auto-accepted conf | 0.93 (verified); 0.99 (contradicted) |
| Review confidences | 0.27, 0.56 |
| Questions per citation | 1 Choice, 3 options |
| Model calls for fabricated quote | 0 |
| Client timeout | 120.0s |
| Latency/cost per call | recorded in code (`seconds`, tokens) but not printed in source |

## Gotchas
- Fabricated verdict has confidence `None`; handle it in code (`auto=True`).
- Section-only citations skip the quote check, so they can only be `verified/contradicted/unsupported`, never `fabricated`.
- A playground link in the source loads one citation's claim + section + question (the `exp_required` example) for live editing.

## Related
[[choice]] · [[confidence]] · [[confidence-gated-routing]] · [[cb-llm-guardrails]] · [[cb-classifying-rag-passages]] · [[use-case-map]] · [[cookbooks-overview]] · [[topic-guardrails]]
