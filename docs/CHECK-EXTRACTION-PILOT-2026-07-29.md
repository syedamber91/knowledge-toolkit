# Check-extraction pilot — NotebookLM thematic querying (2026-07-29)

**Read this before extracting machine-checkable rules from the concept-note
corpus, or before assuming a NotebookLM-backed extraction is cheap/complete.**

Goal: turn the 459-note persona wiki into a reusable library of *falsifiable
checks* ("CFO/PAT should exceed 90–95%") that can be run against a company's
live data — without paying to read all 459 notes end-to-end.

Pilot scope: the `forensic` tag, 38 admitted notes, 217,638 chars.
Artifacts: `scripts/check_extraction/` (seed / query / verify / route) and
`forensic_pilot_results.json` (all 104 proposals with their verdicts).

---

## 1. The idea being tested: invert the loop

Per-note iteration is the obvious shape and the expensive one — 222 reads to
discover that dozens of notes all say "check cash conversion". You pay full
price to rediscover duplication.

Seeding the notes as NotebookLM sources allows querying **by theme** instead
(10 queries: cash conversion, working capital, revenue quality, capitalisation,
promoter conduct, related-party, auditor/governance, balance-sheet health,
margins, checklists). Deduplication happens *inside* the query. NotebookLM is a
flat-fee subscription, so its share of the work is not token-billed — the same
arbitrage the NotebookLM-brain sector redesign already made.

**One source per note, never batched.** The verification step must know which
note a claim came from, so source granularity has to match note granularity.

---

## 2. Measured results

| Metric | Value |
|---|---|
| Proposals parsed (10 themes) | 104 |
| NUMERIC-VERIFIED (threshold + quote both found in cited note) | **54** |
| ADVISORY (real test, source states no number) | 50 |
| **REJECTED (fabricated threshold or quote)** | **0** |
| Unresolvable source attribution | 0 |
| Distinct checks after dedup | **37** |
| Note coverage | **25 / 38 (66%)** |

### What genuinely improved over the previous process

- **Yield.** 52% of proposals carry a source-verified number. The F1–F41
  framework pass yielded a machine signal on roughly 20–25% of entries.
  *Caveat on the comparison:* different units (F-entries vs note-level
  proposals), so treat this as "thematic querying surfaces thresholds that
  framework-level compression discarded", not as a like-for-like ratio.
- **Fabrication.** Zero across 104 proposals. The prior NotebookLM
  framework-evolution run fabricated a quote ("cash cow" attributed to a
  timestamp that never contained it) and scored 71% on citation verification.
  Two changes account for the difference: (a) the prompt makes abstention the
  cheap path — `THRESHOLD: NONE STATED` is declared correct and expected, and
  50 proposals took it; (b) one-source-per-note gives exact provenance, so a
  claim cannot be laundered across notes.
- **Cost.** ~200k tokens for what a per-note read of the same 38 notes would
  have cost several times over, and the output is company-independent — the
  check library amortises across every future company.

### What did NOT improve — an honest regression

- **Coverage fell to 66%.** Per-note reading is 100% by construction; thematic
  querying is not. 13 notes were cited by nothing, including
  `tvgp-framework`, `risk-assessment-before-analysis`, and
  `financial-fraud-and-management-quality` — which certainly contain checkable
  content. **This is a real recall gap, not a rounding error.** The residual
  per-note pass over uncited notes is load-bearing, not optional. Any future
  run must report this number and spend the residual pass; treating thematic
  coverage as complete silently drops real rules.

---

## 3. The failure that cost the most: the checker, not the model

The first verification run reported **10 REJECTED + 8 ADVISORY-UNGROUNDED**,
implying a ~14% fabrication rate. **All 18 were defects in the verifier.**

1. NotebookLM returns each quote wrapped in the citation apparatus the notes
   themselves use — `(MODULA 00:20:23-00:20:33, MODULA 00:23:07)` — plus its
   own footnote markers `[2]`. Neither is part of the quoted sentence, so
   verbatim matching failed on genuine quotes.
2. The same apparatus appears in the THRESHOLD field, so `(SOICC 00:14:01)`
   contributed `00`, `14`, `01` as if they were claimed threshold numbers.

Both are fixed in `verify_claims.py` (`_REF_CITE_RE`, `_FOOTNOTE_RE`, applied
to quote *and* threshold before comparison), plus a fragment fallback for
quotes the model trims. After the fix: 0 rejections.

**Generalisable lesson: when a verifier accuses a generator, suspect the
verifier first.** A false-positive fabrication rate is worse than no check —
it destroys trust in a component that was working correctly. Reporting run
one's numbers would have been a materially wrong claim about NotebookLM.

---

## 4. Verification proves provenance, not applicability

Some verified numbers are context-stripped: `47% to 42%`, `10%, 11%, or 12%`,
`60% margin while another achieves only 30%`. Those digits genuinely appear in
the source, so the deterministic gate passes them — but they are figures from a
worked example, not general thresholds.

**The gate answers "did the source say this number?", never "is this number a
rule?"** A human pass is still required to separate SOIC's actual rule from a
number SOIC happened to say. Do not wire a verified-but-illustrative figure
into a scoring rule.

---

## 5. Auth: age is necessary but NOT sufficient (`notebook_preflight.py`)

Long NotebookLM jobs die mid-run when the Google session expires, wasting all
prior work (the seeding run uploads 38 sources one at a time). The first
version of the preflight checked token *age* against the 7-day cache cap.

**It reported a comfortable 156h of headroom on a session Google had already
invalidated server-side** — and the run died anyway, at 12h old. Age-only
preflight shows green and the job still fails, which is the exact failure it
existed to prevent.

`check_auth(functional=True)` (the default) now makes one cheap live call
before committing to work, and reports *"looks fresh by age … but a live call
FAILED — the session is already invalid server-side"*. Pinned by
`test_fresh_by_age_but_dead_session_is_caught_by_the_live_probe`.

Deliberately NOT an auto-refresher: minting a session needs a browser cookie
only a human can supply, so an auto-refresh would relocate the same mid-run
failure somewhere less visible. The module converts a late, expensive, cryptic
failure into an early, cheap, actionable one — nothing more.

**Transient failures are separate from auth failures.** Two of ten themes first
failed on a read timeout and a DNS blip; those are worth retrying. An
`Authentication expired` is not — retrying it three times just burns time.

---

## 6. Prompt design that held up

- Chat-turn input is capped near 5KB — keep prompts to a few lines and let the
  sources carry the corpus.
- State only what a GOOD answer looks like. A "don't do this" example primes
  the model to emit exactly that pattern (the documented `[N-M]` range-syntax
  failure).
- Make abstention explicitly correct and expected. This is what produced 50
  honest `NONE STATED` answers instead of 50 invented numbers.
- Demand the number be copied "character for character" and quoted in its
  containing sentence — that is what makes deterministic verification possible
  at all.

---

## 7. Full-corpus results (all 222 admitted notes, 2026-07-29)

The pilot was extrapolated to the whole admitted corpus: 184 further notes
seeded across 5 notebooks (`seed_corpus.py`, 0 failures), 11 themes asked of
every notebook (`query_corpus.py`, 55 slots), verified by `verify_corpus.py`.

| Metric | Forensic pilot | Full corpus |
|---|---|---|
| Proposals | 104 | **547** |
| NUMERIC-VERIFIED | 54 | **267** (**219 distinct**) |
| ADVISORY | 50 | 276 |
| REJECTED | 0 | **1** |
| ADVISORY-UNGROUNDED | 0 | 3 |
| Note coverage | 66% | **74% (165/222)** |

**Fabrication rate 4/547 = 0.7%, and none is an invented number.** All four are
source misattribution or loose paraphrase — real content, wrong note or
non-verbatim quote. The deterministic gate catches this class exactly as it
catches fabrication, which is the point.

Coverage rose 66% → 74% by asking **every theme of every notebook** rather than
guessing which notebook holds a tag. Notes are chunked by seeding order, not by
topic, so guessing would reintroduce the blind spot §3's residual pass proved
expensive. The extra queries are cheap; the missed rules are not.

### Numeric density is a property of the material, not the method

| Theme | verified/total | Theme | verified/total |
|---|---|---|---|
| technicals_timing | 39/62 | cyclicality | 12/28 |
| quality_moat | 28/47 | behavioral | 14/48 |
| position_sizing | 28/38 | valuation | 8/25 |
| growth | 27/44 | **leverage_risk** | **1/24** |

`leverage_risk` at 1/24 looked like a prompt defect and was checked rather than
assumed. It is not: the 21 advisories are genuine leverage tests that happen to
be qualitative (debt-funded acquisition strategy, working-capital-heavy
liquidity, the DuPont leverage component, masked off-balance-sheet debt), while
the *numeric* leverage rules — D/E `< 0.7 times`, SpiceJet's `15 to 16 times` as
a bankruptcy signal — were already captured under the forensic tag. **Cross-tag
overlap means a rule found once does not need finding again**; a low per-theme
yield is not evidence of a broken query.

### Residual pass, measured (13 uncited forensic notes)

144 tests, 35 numeric (**24%**) — against 52% for the thematic pass. An earlier
reading of this document claimed the uncited notes were ~4× less numeric and
therefore safe to skip; that was based on one batch of six and was **wrong**.
The second batch of seven ran 36% numeric and recovered rules the thematic query
missed entirely: `fundamentals-of-free-float-and-shareholder-types` (8/12 —
the >1% disclosure line, the "90% or more cornered" supply-collapse screen,
order-size-vs-daily-volume circuit risk, promoter indirect control at 75%
official vs 86% actual) and `bombed-out-ipo-framework` (7/12 — a complete
post-IPO timing model). **The residual pass is load-bearing. Do not skip it.**

## 8. Next steps

1. **Residual per-note pass over the 57 still-uncited notes.** Non-optional,
   for the reason measured above.
2. **Human triage separating rules from illustrative figures** (§4) — now
   corroborated by four independent passes. Verified-but-illustrative figures
   (`47% to 42%`, DMART at `122X`, Apple's `35%` buyback) must not reach a
   scoring layer.
3. Only then wire surviving numeric checks into scoring; everything else stays
   advisory, per the standing no-invented-thresholds invariant.
