# Coverage-gap gathering: mechanical-grep follow-up on the 8 thin/conflicting metrics

This file is the follow-up gathering pass called for by
[`COVERAGE-GAP-JUDGMENT.md`](COVERAGE-GAP-JUDGMENT.md) for the 8 metrics it
judged **PROMOTE CAUTIOUSLY** on thin or conflicting evidence:
`base_range_pct`, `cwip_to_fixed_assets_pct`, `dividend_yield_pct`,
`operating_margin_pct`, `pct_above_200ema`, `price_to_book`,
`relative_strength_vs_index`, `volume_vs_avg_multiple`. (`ev_to_ebitda` and
`price_to_cash_flow` were judged already well-evidenced and are out of
scope.)

**Source of candidates:** `out/gather/candidates_digest.json`, a mechanical
(no-LLM) keyword grep over the 58-lecture corpus, up to 3 candidate lectures
per metric, each with short keyword-hit snippets. Every candidate below was
opened at its full transcript (resolved via `out/gather/ref_to_file.json` to
the file under the iCloud `Stock Market Vault`) and read in surrounding
context before being accepted or rejected — the digest snippets themselves
are not evidence, only pointers. Quotes below are copied character-for-
character from the transcript, not retyped from the snippet.

This file proposes changes; it does not edit `COVERAGE-GAP-JUDGMENT.md`
itself.

---

## base_range_pct

**No new evidence found.** All three candidates (WESNW
`when-how-to-enter-a-stock`, SESCS `class-5-soic-exit-strategies`, SGBTS
`spotting-growth-businesses`) are false-positive keyword hits. WESNW and
SESCS discuss "base formation" extensively but only qualitatively (e.g.
SESCS 02:58:53: "always remember this higher the base bigger the
breakout") — no peak-to-trough percentage is ever stated. SGBTS's "base"
hits are all about a company's revenue/AUM *base effect* on growth rates
(a completely different sense of "base"), not a price consolidation range.
The existing verdict (single citation, SBFTS, `< 15`) is unchanged — still
thin.

## cwip_to_fixed_assets_pct

**No new evidence found.** FSNAF (`11224-class-2-financial-statements`)
gives a single-company illustration — "the example of yashu industries
just again example almost 3 times... fixed block of 200 crores, more than
600 crores" (FSNAF 00:19:16) — explicitly flagged twice as "just an
example," not a stated screening bar, so per the extraction discipline
(universal bound, not a dated single-company illustration) it doesn't
count. JFSNJ and CFSHC turned out to be the *same* segment of course
content duplicated across two lecture files (`class-6-joining-the-
financial-statements` and `class-3-cash-flow-statement`) — both only
explain what CWIP *is* (money moves from CWIP to fixed assets once
construction completes) with no percentage bound anywhere. The existing
conflict (DSEFD ~50% vs. FMFDF >100%) is unresolved and unchanged.

## dividend_yield_pct

**Found new evidence — makes the conflict worse, not better.** FMFDF
(`class-3-finding-multibaggers-fundamental-analysis`) states a *different*
numeric bar for a dividend-type-company screen: "Companies giving out
profits is also a good screen that companies are sharing dividends so if
you want to see a dividend type company then you can come here and see it
and you can actually put a dividend yield here that dividend yield should
be more than 3% But typically I don't go to dividend yielding companies
because I just think they might not have avenues to grow." (FMFDF
02:44:14). This is a real, explicit numeric screen bar — not an
illustration — but it sets `> 3%`, materially looser than the existing
WBSNW citation's `> 6%`. Rather than corroborating the existing bound, this
is a second independent citation that *conflicts* with it, the same
pattern already seen in `cwip_to_fixed_assets_pct`. (ODDM's dividend-yield
mentions are all about Nifty's index-level average yield contributing to
long-term index CAGR, not a company screening bar; DSEFD only names
"dividend yield stocks" as a value-investing style category with no
number — both are false positives.) Recommend re-labeling this verdict
"PROMOTE CAUTIOUSLY — conflicting bounds (3% vs. 6%)," matching the
`cwip_to_fixed_assets_pct` treatment, rather than "thin, single citation."

## operating_margin_pct

**No new evidence found.** TFMLT (`class-4-tools-to-find-multibaggers`)
gives two single-company illustrations with no stated bar: a rhetorical
"are these margins high or on the lower side?" over one company's reported
20/25/21/23/24% margin series (TFMLT 00:06:58), and a specific company
(LGB) described as "operating margins continue to be healthy at 17%"
(TFMLT 02:34:27) — a described outcome, not a threshold. DSEFD
(00:18:34–00:19:44) is purely directional ("if the operating margin of
the company has started to improve, that is usually the first signal...")
with no number at all. FMFDF (02:13:27) states a YoY *trend* condition
("the operating margins should be higher than operating margins last
year") — a distinct kind of condition (delta vs. prior year, not an
absolute floor) from the existing SDBES `> 6%` citation, so it neither
corroborates nor conflicts with it. Verdict unchanged — still a single
citation for the absolute-floor version.

## pct_above_200ema

**No new evidence found — all three candidates are keyword false
positives for a different metric.** BVB (`250126-part-b-valuation`,
00:18:14–00:20:07) and FSSMF (`framework-on-how-to-sell-stocks`,
00:05:15–00:05:37, 00:19:11) both discuss **% of stocks in the market**
above their 200 DMA — that's the market-breadth metric
`pct_stocks_above_200ema` (already separately judged NOT RULE-WORTHY, out
of scope here), not one stock's own stretch above its own 200 EMA. SDBES's
"200" hit (00:20:18–00:24:36) is about a breakout-window scan definition
("breakout will be done after 200 days") — unrelated to EMA distance
entirely. The existing verdict (DSFDO/SESCS ~80%, with DSFDO's own
inconsistent 80/70/"beyond 80" wording) is unchanged.

## price_to_book

**Found new evidence — resolves the thin-citation problem, upgrade
recommended.** FMNAF (`010226-part-1-financial-modelling`) independently
states the *same* `< 1` bound the existing WBSNW citation gives, scoped to
cyclical/deep-value stocks and illustrated with Tata Steel: "one of the
things that deep value investors will do in these type of cyclical
companies is to look at these companies when the price to book actually
goes below like one times" (FMNAF 00:50:00), and again: "this is a deep
value strategy that can be taken into 6 equals like Tata Steel whenever it
falls below 1 times, valuation comfort can emerge because P ratio here
gets infinitely higher" (FMNAF 00:51:29). Unlike a bare "Tata Steel's P/B
was X" data point, this is stated as a general practice ("deep value
investors... will do") with Tata Steel as the worked illustration, so it
clears the universal-bound bar. This is now a second, independent
citation for the exact `< 1` threshold, in the same value/deep-value
context WBSNW already carries — the threshold is no longer single-cited.
Separately, ARTBV (`art-of-business-valuation-different-methods`,
00:40:20–00:42:34) independently corroborates and extends the existing
BVB scope citation: it gives an explicit sector-routing table stating P/E
"will not work in life insurance companies, will not work in banks, will
not work in real estate companies" and that P/B is the tool for banks and
"cyclical stocks... as a wonderful tool" — a second, independent source
for the same sector-routing logic. VDVUV added no new numeric evidence
(re-rating discussion and company examples only, e.g. Groove & Anse
13-14x, no stated bound). Recommend upgrading from "single citation for
the threshold" to a stronger PROMOTE — two independent citations now
agree on `< 1` for cyclical/deep-value names, and two independent
citations now agree on the P/B-for-banks-and-cyclicals /
P/E-doesn't-apply-to-banks-or-insurers routing.

## relative_strength_vs_index

**Found new evidence — mixed: corroborates one operationalization while
adding a third, distinct one, so the core conflict is not resolved.**
RSCAR (`how-relative-strength-combined-with-vstop-used-to-buy-stock`,
00:11:13–00:11:28) is a third independent citation for the zero-crossing
operationalization already established by FSSDF/SESCS: "relative strength
scans and relative strength like so relative strength going above like
going above zero right. So it is for the index it has started going above
zero." That strengthens confidence specifically in the zero-crossing
variant (now 3 lectures, not 2). But FESTF (`151224-class-4-how-to-
filter-epic-stocks`, 01:11:19–01:11:32) states a **third, different**
screening definition entirely — the RS *line* making a 52-week high, not
a zero-crossing and not a percentage bar: "Stocks where relative strength
is 52 weeks high, not the stock price, relative strength, what does it
mean? ... so the line of relative strength when it makes 52 weeks high,
this is where this screen starts." (TFELT is a duplicate re-recording of
this exact same class — identical wording — so it is one source, not
two.) Net effect: the existing "concept corroborated, but two conflicting
operationalizations" (zero-crossing vs. `> 2%`) becomes three
operationalizations (zero-crossing, `> 2%`, 52-week RS-line high), with
zero-crossing now the best-corroborated of the three. If forced to pick
one operationalization to encode, zero-crossing is now the strongest
candidate — but the underlying "which one is the real rule" problem the
original verdict flagged is not resolved, it's more fragmented.

## volume_vs_avg_multiple

**No new evidence found.** SMECS (`class-7-soic-method-explained-
valuation-part-1`, 02:19:45) gives one company's actual daily volume
numbers ("average volume is 30K, 25K, 16K, 13,000") in a float-corner
illustration — no multiple stated. VPVUV (`volumes-power-of-volumes-
study`) and TVPDT (`how-to-use-trading-view-part1`) both only explain the
*concept* of a volume moving average and how to set it up as a chart
indicator, with no numeric "X times average" bound anywhere in either
file. The existing conflict (FESTF `> 1.5x` on a 10-day/20-day window vs.
SDBES `> 1.2x` on a 10-day/50-day window) is unchanged.

---

## Correction (2026-08-25): `relative_strength_vs_index`'s zero-crossing
## variant is not a real coverage gap

Re-reading FSSDF and SESCS's exact quoted spans (not just the earlier
paraphrase) before drafting a proposed rulebook entry for the
zero-crossing operationalization -- the strongest-corroborated of the
three found -- turned up a defect in the coverage-gap accounting itself,
not a fix to it.

**SESCS 01:41:47, verbatim:** "some people sell when the relative
strength goes below zero some people do that on weekly or monthly charts
so that is one of the exit strategies." That is not describing a new
signal. It is describing `soic_ladder/judge.py`'s existing
`exit_rs_nifty-001` -- an Observation, already `>= 0`, already fetchable
today, keyed on `nifty500_relative_strength` (Mansfield RS vs Nifty500,
26-week), part of the F23 exit-signal group appended to every judged
company. **FSSDF 00:09:06** ("when you see zero, it means... below zero
means Nifty500 is doing better... as soon as it goes above zero") is a
neutral explanation of the same zero-line semantics, not evidence of a
distinct entry-side rule either. Only RSCAR's citation ("relative
strength scans... going above zero... it is for the index it has started
going above zero," RSCAR 00:11:13) is genuinely ambiguous about
entry-vs-exit use.

So of the "three conflicting operationalizations" the judgment pass
counted, one was never a gap: it is `exit_rs_nifty-001` under a different
name, cited by lectures that describe it as an exit strategy in the
lecturer's own words. **No new rulebook entry was added for it** --
duplicating an already-fetchable, already-live observation under a second
metric key would be the exact "duplicate under a different name" trap
`eps_growth_yoy_pct` and `total_debt_delta_3y` were already correctly
excluded for in `COVERAGE-GAP-JUDGMENT.md`.

This does not change the mechanical 33% coverage figure --
`relative_strength_vs_index` and `nifty500_relative_strength` are
different metric keys in `claims_v2.json`'s vocabulary, so the automated
count still marks the former unmodelled. It changes what the number
*means*: at least one of the 17 remaining "unmodelled" metrics is closer
to "modelled under a name the extraction vocabulary didn't know to
match" than to a genuine hole. The `> 2%` (SDBES) and 52-week-RS-line-high
(FESTF) operationalizations are unaffected by this correction -- neither
maps to `nifty500_relative_strength`'s definition, and the underlying
"which one is the real screening rule" question for those two stands as
recorded above.
