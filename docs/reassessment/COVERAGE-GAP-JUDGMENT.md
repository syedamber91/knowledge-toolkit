# Coverage-gap judgment: do these 20 metrics deserve a rulebook rule?

This file judges the 20 metrics named in [`STAGE3-CLAIM-EXTRACTION.md`
§6](STAGE3-CLAIM-EXTRACTION.md) ("Widening the metric vocabulary — what it
actually measured") as **thresholds on quantities the 16-rule
`soic-ladder/rulebook/soic-ladder-rules-v1.yaml` rulebook has no rule for at
all** (54/127 = 43% of v2's verified claims land here). That earlier stage
built a mechanical "lost condition" detector — it can only check a rulebook
rule against the lectures if a rule exists to check. These 20 metrics have
no rule to check, so they never went through that detector; this file is
the separate judgment pass the §6 finding called for.

**Source of evidence:** `out/coverage_gap_digest.json`, a mechanical (no-LLM)
pull of every threshold/scope row for these 20 metrics from the Stage 3
claim set. Every row's quote has already been verified verbatim against the
raw lecture transcript by Stage 3's pipeline — that check is not redone
here. This file only asks: given what the evidence actually says, does it
add up to a rule a real screening gate could enforce?

**Reading the current rulebook mattered.** `soic-ladder-rules-v1.yaml` and
its own extensive header commentary record several precedents reused below:
G2 (forensic veto) and G6 (valuation) are *deliberately* left unoccupied
because every valuation number in this corpus reads as one-lecture-date /
one-sector calibration rather than a durable universal bar; lenders are
excluded from ROCE and D/E rules because their balance-sheet shape breaks
the ratio; portfolio-construction concerns (position sizing, holdings
count) are treated as a different kind of rule from a company screen. Those
same precedents apply directly to several of the 20 metrics below.

---

## base_range_pct

**Verdict: PROMOTE CAUTIOUSLY**

Only one lecture (SBFTS) states the bound (`< 15`, base peak-to-trough
swing) and its own scope condition (only meaningful when the stock's trend
state is classified sideways — a base doesn't exist in an uptrend or
downtrend). The concept is clear and the scope condition is explicit and
usable, but it rests on a single citation with no corroboration elsewhere
in the corpus. Thin, not wrong.

If promoted: `base_range_pct <= 15`, scope = "only evaluated when
trend_state == sideways; not meaningful in a trending market." Needs a
second citation before treating it as durable.

## cwip_to_fixed_assets_pct

**Verdict: PROMOTE CAUTIOUSLY — conflicting bounds**

Two lectures give materially different bars for what should be the same
"active capex cycle" screen: DSEFD says CWIP reaching **~50%** of fixed
assets is the screen; FMFDF says CWIP must **exceed 100%** of net block
(i.e. CWIP bigger than the fixed assets already on the books). A 50% floor
and a 100% floor are not the same rule — one accepts a company halfway
through a capex cycle, the other only accepts one where work-in-progress
has already overtaken the existing asset base. Before this can ship as one
rule, someone needs to determine whether these are two different screens
(e.g. a looser vs. stricter cut) or a genuine disagreement across lectures.

## dividend_yield_pct

**Verdict: PROMOTE CAUTIOUSLY**

Single citation (WBSNW), `> 6%`, explicitly framed as a value-approach
screen, not a universal bar. No corroboration, no scope beyond "value
approach." Too thin on its own to set a durable threshold; a real rule
would also need `requires_attribute` scoping to a value/deep-value style
context so it doesn't silently apply to growth-style screening.

## eps_growth_yoy_pct

**Verdict: NOT RULE-WORTHY**

The one threshold citation (FMFDF, `>= 20`) sets the exact same 20% bar the
rulebook already enforces via `canslim_pat-001` (`pat_growth_yoy_pct >=
20`, gate G0). EPS growth and PAT growth diverge only through share-count
effects (dilution/buybacks) — for the common case they're the same
screening question asked twice. The one scope row (GARP requires both PE
and EPS growth, unlike a valuation-only deep-value entry) is useful
color but doesn't change that this is a duplicate at the current evidence
level. If a future citation shows EPS growth used somewhere PAT growth
structurally can't substitute (e.g. explicitly to catch buyback-driven EPS
inflation), revisit.

## ev_to_ebitda

**Verdict: PROMOTE CAUTIOUSLY — rich but conflicting/sector-bound evidence**

The largest evidence set of the 20 (11 rows from SMEC2, BVB, VACRA), and it
genuinely conflicts even within a single lecture (SMEC2): a general ceiling
of ~20-22x in one pass, `< 30` as a separate "very expensive" ceiling, a
hospital-specific band (`<= 20` cheap / `>= 30` expensive), a cement-specific
`<= 21` with a `17-18` fallback described as garbled speech. Multiple scope
rows say EV/EBITDA should NOT be used at all for real estate or asset-light
platform businesses, and only applies when P/E is unusable (mid-capex
earnings depression, asset-heavy businesses). This is exactly the pattern
the rulebook's own header already names as the reason G6 (valuation) ships
empty: sector-specific calibration numbers, not a durable universal bar. If
this is added at all, it should follow `pe_context-001`'s shape — an
**observation**, not a hard gate — carrying the sector-conditional bands and
the explicit real-estate/asset-light exclusions, not a single number.

## fixed_asset_turnover

**Verdict: NOT RULE-WORTHY**

Single citation (FSNAF, `< 2` sales-per-rupee-of-fixed-assets), and it is
used to *classify* a company as asset-heavy vs. asset-light — i.e. it
routes which valuation method applies (this classification is exactly what
several `ev_to_ebitda` scope rows and the existing
`fixed_asset_turnover-001` observation's direction-only framing are about)
rather than gating pass/fail on the company itself. A classification
threshold that decides which other rule applies is not the same thing as a
screening bar.

## market_cap

**Verdict: RULE-WORTHY**

The `> 1000` crore liquidity floor is stated identically across three
independent lectures (FESTF, FMFDF, TFELT) as the default screening tier,
with a consistent, explicit rationale (liquidity) and consistent scope
language about what changes near the floor. That's the strongest
corroboration of any metric in this set.

Proposed shape: `metric: market_cap`, `check_rule: ">= 1000"` (crore),
gate: a new or existing eligibility gate (e.g. G0, alongside the CANSLIM
growth screens, since it's a pre-screen liquidity floor rather than a
quality/valuation judgment). `requires_attribute: {}`.

Scope note the rule must carry: this is the *default* tier — the source
explicitly allows looser 500cr/100cr tiers as a deliberate trade-off, with
explicit added risk near the 100cr floor (negative cash flow, weak business
models more common there) — so a real rule needs a configurable floor, not
a single hardcoded 1000. Do **not** fold in FMFDF's separate `< 15000` cap
(a different, screen-specific gross-block/capex scan) or TVGPT's 5000-7000cr
"sweet spot" (a soft re-rating observation, not an exclusion criterion,
framed as "a sign the company is doing well" rather than a bar) — both are
narrower, screen-specific numbers that would corrupt a general liquidity
floor if merged in.

## operating_margin_pct

**Verdict: PROMOTE CAUTIOUSLY**

Single citation (SDBES, `> 6%`), explicitly the *second, stricter* pass of
a named "margin-expansion scan" — implying a first, looser pass exists with
a different (unrecorded) number. A 6% floor is also a strikingly low bar
next to other margin-adjacent numbers elsewhere in the corpus (e.g. the
existing `capital_efficiency-001` observation cites an operating margin
"near 28-29%" in a different context) — not necessarily a conflict, since
these are different scans for different purposes, but a sign this metric's
context is scan-specific and not yet a stable, portable bar.

## pct_above_200ema

**Verdict: PROMOTE CAUTIOUSLY**

Two lectures (DSFDO, SESCS) agree on the concept and the rough number:
above ~80% stretch over the 200-day EMA is read as an overextension/exit
signal. But DSFDO's own citation notes the instructor states the number
*inconsistently in the same breath* (80%, then 70%, then "beyond 80%") —
a real-quote quality flag on the primary citation, not a transcription
artifact. This is also structurally an exit signal, and the rulebook
already declined to encode the one exit-trigger stub it has (F23) because
it depends on `weekly_price_series`, which is `not_yet_fetchable` — the
same fetchability blocker would likely apply here.

## pct_stocks_above_200ema

**Verdict: NOT RULE-WORTHY**

This is a market-breadth indicator — the same number applies to every
company on a given day, since it describes the whole index, not one
company. The rulebook's gates are architected to evaluate individual
companies; a per-market macro signal doesn't fit that shape at all (it
would need to live in a market-timing/regime layer, not a per-company
gate). Separately, the two lectures don't even agree on a specific number:
BVB puts the buy-zone floor at `< 25` and the overheated ceiling at `> 90`;
MSRTM puts the capitulation buy point at `<= 13` — a materially different
number for what's framed as the same kind of signal.

## portfolio_holdings_count

**Verdict: NOT RULE-WORTHY**

Explicitly the kind of thing the task brief calls out: a
portfolio-construction rule (total number of holdings), not a
company-screening gate — this metric doesn't describe a company at all,
it describes a portfolio. It also has no single defensible bar even within
its own category: DSEFD alone gives three different bands depending on
risk style (aggressive `<= 10`, "decent risk management" `15-25`,
"excessive" `25-30`), plus FMFDF's `<= 30`, BUFF's `17-19`, and PALLOC's
`20-30` diminishing-returns point. If a portfolio-construction layer is
ever built in this system, that's where this belongs — not the per-company
ladder.

## position_size_pct

**Verdict: NOT RULE-WORTHY**

Same category as `portfolio_holdings_count` — this describes how much of a
*portfolio* one position should occupy, not a property of the company
itself, so it cannot gate a company pass/fail. The evidence itself
confirms this is a portfolio-management framework (the 3-6-9 sizing tiers,
scoped by conviction/track-record/growth-runway, explicitly distinguished
from a "beginner 2-6-8 framework") rather than a stock-screening bar.

## price_to_book

**Verdict: PROMOTE CAUTIOUSLY**

Single threshold citation (WBSNW, `< 1`), explicitly framed as a
value-approach signal the same way `dividend_yield_pct` is — thin on its
own. The scope citation is stronger and consistent with an existing
rulebook pattern: BVB states P/E doesn't apply to NBFCs (use P/B instead)
or life insurers (use embedded value instead), which is the same kind of
sector-routing logic the rulebook already encodes for lenders in
`leverage-001` and `capital_efficiency_gate-001` (`requires_attribute:
{is_lender: "false"}`). That routing logic is solid; the actual `< 1`
threshold behind it is not yet corroborated enough to set a number.

## price_to_cash_flow

**Verdict: PROMOTE CAUTIOUSLY**

Two lectures give roughly consistent numbers — SMEC2's general closing
checklist ceiling of `22-23x` and VACRB's hospital-specific `< 25x` — close
enough to not conflict, but both are valuation multiples from the same
corpus the rulebook's own header already treats with caution (G6 left
unoccupied). Given the scope rows tie this metric to the same
asset-heavy/depressed-earnings contexts as `ev_to_ebitda`, this should be
judged together with that metric rather than in isolation — likely the
same "observation, not hard gate" treatment if either ships.

## price_to_sales

**Verdict: NOT RULE-WORTHY**

The source explicitly disclaims standalone use: "price-to-sales should
never be used as a standalone valuation screen — it must always be read
jointly with P/E, current margin level, and forward PE" (VACRA). Encoding
a bare `price_to_sales <= X` rule would directly contradict that
instruction. The sector-specific numbers underneath it also vary too much
to be one bar anyway — manufacturing `< 3x` vs. SaaS `< 10x`, more than a
3x spread depending on business model.

## relative_strength_vs_index

**Verdict: PROMOTE CAUTIOUSLY — corroborated concept, conflicting operationalization**

Three lectures agree on the underlying idea (RS vs. benchmark, zero-line
significance) but state it two different ways: FSSDF and SESCS both use a
simple zero-crossing oscillator (`> 0` = outperforming / `< 0` = exit
signal), while SDBES cites a specific `> 2%` bar in a different scan. It's
not clear from the digest whether `> 2%` is the same oscillator read at a
stricter level or a genuinely different indicator (a percentage spread
rather than a zero-crossing ratio) sharing the same name. A real rule also
needs the explicit scope FSSMF states: this technical exit system applies
only to satellite/momentum positions, explicitly not to core conviction
holdings — a company-level rule here would need a portfolio-role attribute
the rulebook doesn't currently resolve (`RESOLVABLE_ATTRIBUTE_KEYS` is
`{company, sector, is_lender}` per the existing rulebook's own comments).

## roe

**Verdict: RULE-WORTHY**

Five threshold citations, and read carefully they resolve into two
distinct, non-conflicting groups rather than one messy set: FMNAF, FMODB,
and TVPD2 all state **~14-15% ROE specifically for banks/lenders**
("a bank is considered performing well..."); FMFDF and RSSER state
**>15% ROE for the general case**, stated interchangeably with ROCE
("ROC/ROE above 15%" — the exact phrase already quoted as provenance for
the existing `capital_efficiency_gate-001` rule and `capital_efficiency-001`
observation).

This resolves a real gap rather than duplicating anything: the existing
rulebook's `leverage-001` and `capital_efficiency_gate-001` both explicitly
**exclude lenders** from D/E and ROCE (`is_lender: "false"`) because a
lender's capital-employed/leverage shape breaks those ratios. Nothing in
the current rulebook screens lenders on capital efficiency at all. The ROE
evidence here is specifically about banks — it's the natural fill for that
exact hole, not a second encoding of the same claim.

Proposed shape: `metric: roe`, `check_rule: ">= 14"`,
`requires_attribute: {is_lender: "true"}`, mirroring
`capital_efficiency_gate-001`'s gate (G3) but for the lender population it
currently skips. The general-case (`> 15`, non-lender) citations should
**not** also become a rule — they restate the same "ROC/ROE above 15%" bar
the ROCE rule already enforces for non-lenders, and adding both would gate
the same underlying claim twice under two metric names.

## sector_weight_pct

**Verdict: NOT RULE-WORTHY**

Single citation (PALLOC, `15-20%` sector-exposure cap, stretchable to 25%
on high conviction) and, like `portfolio_holdings_count` and
`position_size_pct`, this describes portfolio composition (how much of a
*portfolio* sits in one sector) rather than any property of a company —
it cannot gate an individual company pass/fail. Same "different part of
the system" reasoning applies.

## total_debt_delta_3y

**Verdict: NOT RULE-WORTHY**

Single citation (FMFDF: debt today lower than debt 3 years ago). The
concept — debt trending down is good — is already encoded in the rulebook
as the `capital_structure_trend-001` observation
(`debt_to_equity_delta_3y <= 0`). The two metrics are technically distinct
(an absolute rupee-debt change vs. a leverage-ratio change can diverge, e.g.
if equity grows fast enough), but with only one citation and no evidence
the lectures ever needed the absolute-debt version where the ratio version
wouldn't do, this reads as the same claim re-surfacing under a different
name rather than an independently motivated new metric.

## volume_vs_avg_multiple

**Verdict: PROMOTE CAUTIOUSLY — two citations, two different formulas**

FESTF states `> 1.5x` comparing 10-day vs. 20-day average volume; SDBES
states `> 1.2x` comparing 10-day vs. 50-day average volume. These aren't
two measurements of the same ratio disagreeing — they're two different
ratios (different denominator windows) that happen to share a metric name
in the digest. Before this can be one rule, the two need to be split into
distinct metrics (e.g. `volume_10d_vs_20d_multiple` and
`volume_10d_vs_50d_multiple`) or a decision made that only one is the
intended screening signal.

---

## Summary

| Metric | Verdict | One-line reason |
|---|---|---|
| `base_range_pct` | PROMOTE CAUTIOUSLY | Clear concept, single citation only |
| `cwip_to_fixed_assets_pct` | PROMOTE CAUTIOUSLY | Two lectures conflict, 50% vs. 100% |
| `dividend_yield_pct` | PROMOTE CAUTIOUSLY | Single citation, value-style only |
| `eps_growth_yoy_pct` | NOT RULE-WORTHY | Duplicates `pat_growth_yoy_pct >= 20` already in the rulebook |
| `ev_to_ebitda` | PROMOTE CAUTIOUSLY | Rich but sector-conflicting; matches the rulebook's own reason G6 ships empty |
| `fixed_asset_turnover` | NOT RULE-WORTHY | Classification/routing threshold, not a pass/fail gate |
| `market_cap` | RULE-WORTHY | `>= 1000` crore floor, corroborated across 3 independent lectures |
| `operating_margin_pct` | PROMOTE CAUTIOUSLY | Single citation, explicitly a "second, stricter" scan variant |
| `pct_above_200ema` | PROMOTE CAUTIOUSLY | Corroborated direction, but source states the number inconsistently |
| `pct_stocks_above_200ema` | NOT RULE-WORTHY | Market-breadth macro signal, not a per-company property |
| `portfolio_holdings_count` | NOT RULE-WORTHY | Portfolio-construction rule, not a company gate; also style-dependent bands |
| `position_size_pct` | NOT RULE-WORTHY | Portfolio-construction (sizing) rule, not a company gate |
| `price_to_book` | PROMOTE CAUTIOUSLY | Single citation for the threshold; sector-routing scope is solid though |
| `price_to_cash_flow` | PROMOTE CAUTIOUSLY | Consistent numbers but same valuation-multiple caution as EV/EBITDA |
| `price_to_sales` | NOT RULE-WORTHY | Source explicitly disclaims standalone use of this metric |
| `relative_strength_vs_index` | PROMOTE CAUTIOUSLY | Concept corroborated, but two conflicting operationalizations |
| `roe` | RULE-WORTHY | Fills a real gap: lenders are excluded from the existing ROCE rule |
| `sector_weight_pct` | NOT RULE-WORTHY | Portfolio-construction (sector allocation), not a company gate |
| `total_debt_delta_3y` | NOT RULE-WORTHY | Duplicates the existing `debt_to_equity_delta_3y` direction observation |
| `volume_vs_avg_multiple` | PROMOTE CAUTIOUSLY | Two citations are two different formulas, not one metric |
