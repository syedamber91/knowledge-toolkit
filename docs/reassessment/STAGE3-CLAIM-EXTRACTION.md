# Stage 3 — the lost-condition detector: task, method, and results

Durable record of what Stage 3 was asked to do, what was actually built, the
extraction/verification pipeline used to run it end-to-end across all 58
reassessment briefs (twice), and every defect the run itself exposed. Written
because the raw run artifacts live under `out/`, which is gitignored scratch
(see CLAUDE.md's "Gitignored outputs" rule) — this file is what survives.

Plan: [`docs/superpowers/plans/2026-08-24-stage3-lost-condition-detector.md`](../superpowers/plans/2026-08-24-stage3-lost-condition-detector.md).
Roadmap: [`ROADMAP.md`](ROADMAP.md). Prior stages: Stage 1 (explain one
company) and Stage 2 (weekly short list), both in `soic-ladder`, merged.

---

## 1. The task

The reassessment (`docs/reassessment/`, see [`README.md`](README.md)) had
already re-read all 58 SOIC L3/L4/L5/Crash-Course lectures and gated each
brief at ≥80% verbatim-quote presence against the raw transcripts. That
proved the briefs are trustworthy. It did **not** prove the `soic-ladder`
rulebook (16 rules, `soic-ladder/rulebook/soic-ladder-rules-v1.yaml`) still
says what those lectures actually taught.

The concern, stated in the original brief for this whole reassessment: a
rulebook encodes the method as scalar thresholds, and a threshold lifted out
of a lecture loses the sentence that said *when it applies*. Stage 3's job
was to test that concern **mechanically** — build something that reads
claims out of the gated briefs, checks every claim against the raw
transcript (not the brief, not the rulebook), and reports any rulebook rule
whose threshold has a stated condition it does not carry.

**The acceptance criterion, fixed before any extraction ran:** the detector
must independently rediscover two known lost conditions — the returns-gate
waiver for a company inflecting out of a turnaround, and the P/E band's
growth-matching condition — having been told about neither. If it doesn't,
the fix is to the schema or the extraction prompt, never to hand-edit claims
until the test passes.

## 2. Architecture

```
gated brief (already quote-verified at 80%+)
        |
        v
  extractor (Sonnet subagent, one per brief)  --  emits threshold/scope claims
        |
        v
  assemble_claims.py
    1. LINK    scope claims to threshold claims, by metric, across ALL briefs
    2. VERIFY  every claim's quote against the RAW TRANSCRIPT at its cited
               timestamp (never against the brief — the brief is one hop
               removed from the source)
    3. DROP    anything that doesn't verify verbatim. Never repaired.
        |
        v
  detect_lost_conditions.py  (pure Python, zero LLM calls, deterministic)
    for each rulebook rule with a metric+bound:
      find the threshold claim with the same metric+bound
      find every scope claim that governs that metric
      report the rule as a finding if it doesn't already narrow by the
      condition the scope claim states
        |
        v
  findings (never written to the rulebook — a human adjudicates)
```

Two invariants carried over from the rest of this reassessment and enforced
throughout Stage 3:

- **A REF code is verified by `(REF, timestamp)`, never inferred.** See
  `soic_wiki.ref_crosswalk.Resolver`.
- **The quote gate catches fabrication, never omission.** A claim that
  verifies is real; a brief that yields zero claims may still contain
  material a second read would catch. One pass is a lower bound, not a
  ceiling.

### Roles (owner's instruction: "Sonnet implements, Opus reviews")

- **Sonnet** — one subagent per lecture brief, dispatched in parallel
  (waves of ~14–18, gated by the 20-subagent concurrency cap), each reading
  only the shared extraction brief plus its own lecture brief. No subagent
  saw another's output or the rulebook.
- **Opus** (this session, orchestrating inline rather than via
  `subagent-driven-development`'s task-reviewer template, because the task
  was "dispatch 58 independent extractions and assemble," not a
  file-by-file implementation plan) — wrote the schema and extraction
  brief, dispatched every subagent, ran the deterministic assembly and
  detector, and — critically — investigated every anomaly in the numbers
  rather than reporting them as-is. Three of the anomalies found this way
  turned out to be bugs in the orchestrator's own code, not in the
  extraction.

## 3. Claim schema

Two kinds only, on purpose — mechanism, procedure, and worked examples are
explicitly out of scope for this pass:

- **`threshold`** — a stated numeric bar on a measurable quantity:
  `{claim_id, kind: "threshold", ref, ts, quote, statement, metric, bound,
  source_brief}`.
- **`scope`** — a stated condition that narrows, waives, or overrides a
  threshold: same shape but `metric`/`bound` are `null` and
  `governs_metrics: [...]` names what it governs.

Implemented as a Pydantic model (`src/soic_wiki/claims.py`) whose validator
refuses a `threshold` with no metric+bound and a `worked_example` with a
bound — the type system, not a reviewer, rejects a dated illustration
promoted to a universal rule.

**Grounding rules given to every extractor**, tightened once between v1 and
v2 (§6):

1. `quote` must be copied character-for-character from a quoted span in the
   brief — never tidied, joined, or paraphrased. Checked mechanically
   afterward; anything that doesn't match verbatim is dropped, never
   repaired.
2. `ts` must be the timestamp cited beside that quote in the brief.
3. (v2 only) **A bound must come from inside the quoted span, not the
   brief's surrounding prose.** If the number appears only in the brief
   author's gloss or summary line, do not emit the claim.
4. `statement` is the extractor's own words — never a copy of the quote.
5. Emit nothing ungroundable. `[]` is a legitimate, common result.
6. A number illustrating one company at one moment is not a threshold.
   Promoting a dated worked example to a universal rule was flagged as
   "the single most common defect in this corpus."
7. A threshold needs both a vocabulary metric and a bound — no term, no
   claim (never emit with a null metric). Extractors were told to name any
   bar they had to skip for lack of a vocabulary term in their return
   summary; that is what produced the vocabulary-widening evidence in §6.

## 4. What was extracted, and how much survived scrutiny

### Pilot (4 briefs, before this session)

FESTF, BVB, VALU2, TFELT → 40 extracted, 4 schema-rejected, 36 verified, 0
dropped. Detector ran, found both acceptance targets unprompted plus one
unpredicted rule (`peg_ratio-001`). Stage 3 acceptance test **passed**.

### Full corpus, v1 (this session — 15-term metric vocabulary)

All 58 briefs, one Sonnet extractor per brief, dispatched in parallel waves.
154 claims extracted → 4 schema-rejected → **138 verified** (after the
bug fixes in §7) → 101 findings across **9 of 16 rules**.

### Full corpus, v2 (this session — widened to 41 terms, §6)

Same 58 briefs, re-extracted from scratch with a widened vocabulary and two
tightened grounding rules. 217 claims extracted → 0 schema-rejected →
**197 verified** (after the same bug fixes) → 96 findings across 8 rules.

| | claims extracted | schema-rejected | verified | dropped | findings | rules hit |
|---|---|---|---|---|---|---|
| pilot (4 briefs) | 40 | 4 | 36 | 0 | 2 | 3 |
| **v1** (58 briefs, 15 metrics) | 154 | 4 | **138** | 12 | **101** | **9** |
| **v2** (58 briefs, 41 metrics) | 217 | 0 | **197** | 20 | **96** | **8** |

## 5. Findings — v2, deduplicated for shared recordings

Two lecture pairs turned out to be the same recording published under two
REF codes (`TFELT`=`FESTF`, `JFSNJ`=`CFSHC`; confirmed by sha256 of
`body_text`, see §7.3). The table below counts distinct recordings, not raw
REF codes.

| rule | findings | distinct recordings | what the rule narrows by |
|---|---|---|---|
| `pe_context-001` | 31 | 14 | **nothing** |
| `growth_trap_flag-001` | 31 | 14 | **nothing** |
| `entry_adx-001` | 10 | 5 | **nothing** |
| `entry_rsi-001` | 6 | 5 | **nothing** |
| `peg_ratio-001` | 6 | 5 | **nothing** |
| `canslim_pat-001` | 5 | 4 | **nothing** |
| `canslim_sales-001` | 4 | 3 | **nothing** |
| `capital_efficiency_gate-001` (acceptance target) | 3 | 2 | `is_lender: false` |

`pe_context-001` and `growth_trap_flag-001` draw identical counts because
both govern `stock_pe`; the same scope claims legitimately attach to both.
`leverage-001` was found in v1 (after the bug fix) but not v2 — see §7.1 for
why apparent rule-level differences between v1 and v2 must be read against
the bugs, not taken at face value.

The detector **reports; it never writes to a rulebook.** Every finding
carries its citation so a human adjudicates.

## 6. Widening the metric vocabulary — what it actually measured

v1 extractors kept independently reporting a clearly stated bar they could
not record because no vocabulary term existed for it. **`ROE` was flagged
by four separate extractors** — the vocabulary only had `roce`, a different
ratio. Also reported missing: EV/EBITDA, price-to-book, price-to-sales,
dividend yield, operating margin, promoter holding, position size, market
breadth.

The vocabulary was widened from 15 to 41 terms, every addition traced to a
bar an extractor named as blocked — nothing speculative:

```
Growth:        sales_growth_yoy_pct · sales_growth_3y_pct · pat_growth_yoy_pct ·
               revenue_cagr_pct · eps_growth_yoy_pct
Returns:       roce · roe · operating_margin_pct · gross_margin_pct
Valuation:     stock_pe · peg_ratio · ev_to_ebitda · price_to_book ·
               price_to_sales · price_to_cash_flow · dividend_yield_pct ·
               sector_pe
Balance sheet: debt_to_equity · debt_to_equity_delta_3y · total_debt_delta_3y ·
               cfo_to_pat_3yr · cfo_to_ebitda_pct_3y · cwip_to_fixed_assets_pct ·
               fixed_asset_turnover · fixed_asset_turnover_delta_3y ·
               capex_expansion_delta_3y
Ownership:     market_cap · promoter_holding_pct · free_float_pct
Technical:     weekly_rsi · weekly_adx · monthly_rsi · monthly_adx ·
               pct_above_200ema · relative_strength_vs_index ·
               volume_vs_avg_multiple · base_range_pct
Market-level:  pct_stocks_above_200ema
Portfolio:     position_size_pct · portfolio_holdings_count · sector_weight_pct
```

Two grounding rules were tightened in the **same** edit (rule 3 in §3, and
splitting weekly/monthly indicators into distinct terms rather than
defaulting to weekly). That conflates two variables in one experiment — the
v1→v2 deltas below cannot be cleanly attributed to vocabulary alone. Noted
rather than smoothed over.

### The result was not "more lost conditions." It was a coverage measurement.

A lost-condition finding requires a rulebook rule to bind to. v2 holds 43%
more verified claims than v1 (197 vs 138) but **fewer** findings (96 vs
101), because:

```
thresholds on metrics the rulebook has NO rule for at all
  v1:   2 / 76   (3%)
  v2:  54 / 127  (43%)
```

**Widening the vocabulary did not surface more dropped conditions — it
measured how much of the taught method the rulebook never encodes in the
first place.** Roughly 43% of the stated numeric bars in this corpus are on
quantities (ROE, EV/EBITDA, price-to-book, price-to-sales, dividend yield,
position sizing, holdings count, market breadth, relative strength, CWIP,
free float, ...) the 16-rule rulebook does not model. That is a bigger,
different finding than the one this stage set out to produce, and it directly
answers "what is the ladder not even trying to measure?"

### Residual gaps, named unprompted by extractors even after widening

Mostly **indicator parameters, not thresholds** — an EMA length or a
Parabolic-SAR increment configures a tool, it does not gate a company, so
these arguably do not belong in a claims vocabulary at all:

ATR/volatility-stop multipliers, EMA lengths (10/30/40), V-Stop length, SAR
increment, the 30-week EMA specifically (distinct from `pct_above_200ema`),
holding-period/time-stop duration in quarters or years, base-formation
duration in weeks, aggregate core-vs-satellite bucket allocation (as
opposed to one position's size), `promoter_pledge`, 3-year PAT growth,
`ebitda_margin_pct` (distinct from `operating_margin_pct`), GNPA's 90-day
definition, RevPAR, per-tonne unit economics, API $/kg pricing.

## 7. Bugs the run exposed, all in the orchestrator's own code

Every one of these produced a wrong number that was reported as an anomaly,
investigated instead of accepted, and turned out to be the coordinator's
defect — continuing this reassessment's pattern (see
[`ERRATA.md`](ERRATA.md)) that almost every error in this project has come
from *inferring* something instead of *resolving* it.

### 7.1 — Bound strings compared literally, silently erasing 3 rules' findings

`bind_rules()` matched a rulebook's `reference_band` (e.g. `">= 15"`)
against a claim's `bound` by whitespace-stripped string equality. v2
extractors, following the tightened "bound must come from inside the quote"
rule, wrote `"> 15"` for a speaker who said "more than 15%" — semantically
the same bar as the rulebook's `>= 15`, but a different string. Three rules
— `capital_efficiency_gate-001` (**the acceptance target**),
`canslim_pat-001`, `canslim_sales-001` — silently dropped to **zero
findings**. The evidence never changed; a string comparison did.

**Fix:** `_norm_bound()` in `src/soic_wiki/lost_conditions.py` now reduces a
bound to `(direction, values)` — `> 15` and `>= 15` both become `"ge:15.0"`,
while `< 15`, `>= 20`, and a different metric still do not match. Restored
all three rules' findings, and as a side effect surfaced a 9th rule in v1
(`leverage-001`) that had been silently missed the entire time. Tests:
`tests/test_lost_conditions.py::test_bound_matching_is_semantic_not_string`,
`::test_between_bounds_do_not_collapse_into_open_ended_ones`.

### 7.2 — Timestamp *ranges* never resolved, dropping all 29 range-cited claims

This corpus cites both a moment (`00:09:35`) and a span
(`00:09:35-00:10:02`) — both are valid brief citations. `verify_claim()`
passed the whole `"start-end"` string to the resolver as if it were a
single timestamp, which never matches. **Every one of 29 span-cited v2
claims was dropped**, not because the quote was wrong but because the
verifier couldn't parse its own citation format.

**Fix:** `split_ts()` in `src/soic_wiki/claims.py` splits a citation into
`(start, end)`; a span resolves the lesson on its start and checks the
quote across the full span. Tests:
`tests/test_claims.py::test_split_ts_handles_a_span_and_a_moment`,
`::test_verify_claim_accepts_a_span_timestamp`.

Combined effect of 7.1 + 7.2 on the numbers reported to the user (before →
after, all figures in this doc are already "after"):

| | verified | dropped | findings | rules |
|---|---|---|---|---|
| v1 | 127 → 138 | 23 → 12 | 95 → 101 | 8 → 9 |
| v2 | 172 → 197 | 45 → 20 | 93 → 96 | 5 → 8 |

### 7.3 — A withdrawn-then-restored corroboration claim

Reported mid-session that `capital_efficiency_gate-001`'s turnaround waiver
was "independently corroborated from two different lectures" (FESTF,
TFELT). Wrong: those two REF codes are **byte-identical transcripts**
(sha256-confirmed, 128,973 chars) — one class published into two courses,
not two lectures agreeing. Withdrawn once caught. The same corpus-wide hash
check found one further collision (`JFSNJ`/`CFSHC`, 123,141 chars) that is
almost certainly a **capture defect** — two differently titled Crash Course
classes ("Joining the Financial Statements" vs "Cash Flow Statement")
cannot legitimately share a transcript. Every claim citing either code has
a doubtful lecture attribution (the quote itself still verifies; only which
lecture it came from is in question). On the full 58-brief corpus, the
turnaround waiver **is** genuinely corroborated — by FESTF and RSSER,
confirmed distinct recordings. The conclusion held; the evidence under it
changed.

### 7.4 — `assemble_claims.py` re-ingested its own output

Globbed `*.json` over the input directory with no exclusion, so a
previously written `claims.json` in that same directory became a 59th
"brief" on the next run. Fixed by skipping that filename explicitly. Caught
before it corrupted a real run only because the pilot's `claims.json` had
been written to a different directory than the full-corpus run.

## 8. What the run did *not* find wrong (equally load-bearing)

- The 80%-quote-gate discipline from the earlier reassessment stages held —
  every dropped claim in the final numbers is a genuine non-match, not a
  false accusation, confirmed by manual spot-check of the drop list.
- `Resolver`'s `(REF, timestamp)` resolution, hardened earlier in this
  reassessment against exactly this kind of collision (see
  `soic-reassessment-gotchas` in project memory), is what made the
  byte-identical-transcript discovery in §7.3 possible at all — a
  last-wins REF lookup would have hidden it.
- Extraction variance is real and is **not** something to average away:
  the same brief, extracted twice under different rules, disagreed
  (`TVGPT`'s ₹5,000–7,000cr market-cap band: excluded in v1 as a disclaimed
  personal aside, kept in v2 as a stated bar — a live, unresolved
  contradiction between two runs, not a bug in either). `HGBYH`'s RSI
  83–85 band, by contrast, was correctly dropped in v2 (it lived only in
  brief prose, not the speaker's quoted words) after being wrongly kept in
  v1 — the tightened grounding rule working as intended. `MAAIM` refused
  to guess an ADX threshold's weekly/monthly timeframe in v2 rather than
  assume "weekly" as v1 had. **One extraction pass is a lower bound on
  what a brief contains, never a ceiling** — the quote gate proves a claim
  isn't fabricated; it says nothing about what a different, equally valid
  reading might have added.

## 9. Where things live

| What | Where |
|---|---|
| This doc | `docs/reassessment/STAGE3-CLAIM-EXTRACTION.md` |
| Plan | `docs/superpowers/plans/2026-08-24-stage3-lost-condition-detector.md` |
| Claim model + verification | `src/soic_wiki/claims.py` |
| Lost-condition detector | `src/soic_wiki/lost_conditions.py` |
| CLI | `scripts/detect_lost_conditions.py` (reports only, never writes) |
| Assembly (LINK→VERIFY→DROP) | `scripts/assemble_claims.py` |
| Tests | `tests/test_claims.py`, `tests/test_lost_conditions.py` |
| Raw run artifacts (58×2 extractor outputs, assembled claims) | `out/` — **gitignored, not committed**; this doc is what survives it |
| Progress ledger (session-internal) | `.superpowers/sdd/progress-stage3.md` — **gitignored** |
| Commits | `6219711` (claim model) → `05bea7f` (Resolver.window fix) → `ede6c3d` (detector) → `410fc9c` (requires_attribute fix) → `8c7b36f` (REF crosswalk fix) → `d7616bf` (full-corpus v1) → `f8d991c` (vocabulary widening v2 + both bug fixes in §7.1/7.2) |

## 10. Open questions for a human

1. **The 43% coverage gap (§6)** is the largest single finding of this
   stage and is not yet acted on. Deciding which of the 18 unmodelled
   metrics deserve new rulebook rules is a bigger call than adjudicating
   the 96 existing findings and has not been made. **Owner's instruction
   for that follow-up work: Opus orchestrates, Sonnet performs** — same
   split used throughout Stage 3 (one Sonnet extractor per brief, Opus
   dispatching and reviewing). Deferred, not started, pending Claude usage
   budget.
2. **96 findings await adjudication.** The detector proposes; it never
   writes to `soic-ladder-rules-v1.yaml`. Each finding needs a human
   decision: does the rule gain the condition, or was the condition
   itself lecture-specific commentary that shouldn't generalize?
3. **`TVGPT`'s market-cap band (§8)** is a live, unresolved disagreement
   between two independent readings of the same brief and needs a human
   read of the source quote, not another extraction pass.
4. **The `JFSNJ`/`CFSHC` transcript collision (§7.3)** looks like a
   capture-time defect in the underlying Stock Market Vault content, not
   an extraction problem — worth checking against the raw portal capture
   before trusting either REF's attribution further.
5. Whether to extend the pipeline built here (schema, extraction brief,
   assembly, detector) past this reassessment corpus, and whether
   indicator-parameter terms (ATR multiplier, EMA length, SAR increment)
   belong in a *separate* vocabulary from company-fundamental thresholds
   rather than being folded into — or permanently excluded from — this one.
