# Coverage-gap work: closed out at 25%, 2026-08-25

Status marker, not a new analysis. Ties together
[`STAGE3-CLAIM-EXTRACTION.md`](STAGE3-CLAIM-EXTRACTION.md) §6 (which
measured the gap), [`COVERAGE-GAP-JUDGMENT.md`](COVERAGE-GAP-JUDGMENT.md)
(which judged it), [`COVERAGE-GAP-GATHERING.md`](COVERAGE-GAP-GATHERING.md)
(which re-scanned the thin cases) into one place, records the five rulebook
entries that actually landed as a result, and says plainly what didn't move
and why. **Closed for now, not finished** — the remaining 25% needs either a
policy call this project deliberately hasn't made, or evidence from outside
the 58-lecture corpus this project hasn't gone looking for. Either is a real
next project, not a loose end of this one.

## The arc, in one table

| Stage | What it did | Result |
|---|---|---|
| Stage 3 §6 | Measured how much of the rulebook's threshold evidence sits on metrics with no rule at all | **43%** (54/127 v2 claims), 20 distinct metrics |
| Judgment | Read each of the 20 against the rulebook's own precedents | 2 RULE-WORTHY, 10 PROMOTE CAUTIOUSLY, 8 NOT RULE-WORTHY |
| Gathering | Re-scanned raw transcripts for the 8 thinnest PROMOTE-CAUTIOUSLY cases | 3 changed (1 worse, 1 stronger, 1 more fragmented), 5 unchanged; also caught a false gap (`relative_strength_vs_index`'s zero-crossing variant was already `exit_rs_nifty-001` under a different name) |
| Five additions | `roe`, `market_cap`, `price_to_book`, `ev_to_ebitda`, `price_to_cash_flow` written into `soic-ladder-rules-v1.yaml` | **43% → 25%** |
| Live judge | Ran the updated rulebook against the real Aug-22 500-company snapshot | 13 companies' verdict changed, all lenders (the ROE fix); 2 real downgrades (PAYTM 4.7% ROE, PIRAMALFIN 0.86% ROE) caught doing exactly what the gap predicted |

## The five rulebook entries, and why each took the shape it did

All five live in `soic-ladder/rulebook/soic-ladder-rules-v1.yaml`, each with
its own inline comment explaining the same reasoning recorded here — this
table is a locator, not a replacement for reading them.

| id | metric | shape | why |
|---|---|---|---|
| `roe_lender-001` | `roe` | **gate**, G3, `>= 14`, `is_lender: true` | Fills a real hole: `capital_efficiency_gate-001` explicitly excludes lenders from ROCE (deposits break the ratio); nothing screened lenders on capital efficiency at all before this. Clean bar, one well-defined population — a gate, not an observation. |
| `market_cap_floor-001` | `market_cap` | observation, `>= 1000` | Best-corroborated of all five (3 independent lectures) but the source itself treats the floor as tiered (500cr/100cr looser tiers explicitly allowed at higher accepted risk) — `requires_attribute` has no way to express "looser at researcher discretion," so a hard gate would silently exclude names the source says are researchable. |
| `price_to_book_deep_value-001` | `price_to_book` | observation, `<= 1` | Context-conditional deep-value signal (2 independent citations on the threshold, 2 on the bank/insurer sector-routing scope) — most quality companies legitimately trade above 1x book, so a hard gate would reject good businesses for reasons unrelated to quality. Metric registered `not_yet_fetchable` (cheaply derivable from two already-fetched metrics, `market_cap / book_value` — not yet built). |
| `ev_to_ebitda_context-001` | `ev_to_ebitda` | observation, `<= 22` | Richest evidence of the five (11 citations) — the earlier judgment pass thought it was sector-conflicting (matching the reason G6 ships empty), but the actual numbers cluster into ONE band: hospital (20/30) and cement (21, 17-18 fallback) both land inside the general 20-22/30 range, not outside it. One observation, not three sector-scoped ones, with the applicability routing (asset-heavy names, mid-capex-depressed earnings; never real estate or exchange/platform businesses) in `display_text`. Metric registered `not_yet_fetchable` — genuinely not cheap, needs net-debt/cash and EBITDA figures not yet fetched at all. |
| `price_to_cash_flow_context-001` | `price_to_cash_flow` | observation, `<= 22` | Same shape and reasoning as EV/EBITDA, corroborated separately. One real divergence flagged rather than smoothed over: the hospital-specific number (VACRB, below 25x) is *looser* than the general 22-23x band — recorded as a genuine difference, not folded in as if it agreed. Also `not_yet_fetchable`. |

Every addition followed the same governance the rulebook's own header already
established for its original ~30 rules: a human decision made against the
evidence in front of them, recorded inline, never something a detector wrote
on its own. The only difference here is the provenance chain is this
reassessment's, not `decision-frameworks-v1.md`'s — each entry's comment
says so explicitly and links back to the judgment/gathering doc it came from.

## What's left at 25% (15 metrics), and why nothing here was a quick win

None of these got a rule, and none should have, without one of the two real
projects named in "What would actually move this further" below:

- **Genuinely disagrees with itself in the corpus.** `cwip_to_fixed_assets_pct`
  (50% vs 100%), `dividend_yield_pct` (3% vs 6%, got *worse* under gathering,
  not better), `volume_vs_avg_multiple` (two different formulas — 10d/20d vs
  10d/50d — sharing one name, not one metric read two ways).
- **Thin, already searched, nothing more in this corpus.** `base_range_pct`,
  `operating_margin_pct`, `pct_above_200ema` — one citation each; the
  gathering pass went back to the raw transcripts specifically looking for
  more and came back empty.
- **Structurally can't be a company-level rule at all.** `portfolio_holdings_count`,
  `position_size_pct`, `sector_weight_pct` — these describe a *portfolio*,
  not a company; no per-company gate can enforce them.
- **Duplicates an existing rule under a different name.** `eps_growth_yoy_pct`
  (same bar as `pat_growth_yoy_pct`), `total_debt_delta_3y` (same direction
  as `debt_to_equity_delta_3y`), `fixed_asset_turnover` (a routing threshold,
  not a pass/fail bar), `price_to_sales` (the source explicitly disclaims
  standalone use of it).

## What would actually move this further (deliberately not started here)

Two different real projects, not two settings of the same dial:

1. **Reverse the G6-empty precedent on purpose, for real sector-conflicting
   metrics.** `ev_to_ebitda`/`price_to_cash_flow` turned out not to need
   this — but a metric that *is* genuinely sector-conflicting (none currently
   is, at this evidence level) would need actual sector-scoped
   `requires_attribute` entries, which is a bigger, deliberate reversal of a
   decision this rulebook's header already made on purpose. Needs an explicit
   yes on that specific point, not a rule added quietly alongside others.
2. **Widen the search past these 58 lectures.** The existing rulebook's own
   citations already draw from courses outside this reassessment's L3/L4/L5/
   Crash-Course scope (`MASTEC`, `MASTED`, `SOICA6`, `INSIGN`, `SOICC`,
   `FLUORA` — Masterclass, sector courses, and others, roughly 380 more
   transcripts in the Stock Market Vault never re-read for this project).
   Real, could genuinely resolve some of the thin ones — but a materially
   bigger job than anything done in this thread.

## Where things stand across the whole reassessment right now

| | State |
|---|---|
| Stage 1 (explain one company) | ✅ done, merged |
| Stage 2 (weekly short list) | ✅ done, merged |
| Stage 3 (lost-condition detector) | ✅ built, run twice (58 briefs × 2 vocabularies) |
| Stage 3's 96 findings | **not yet adjudicated** — the detector proposes, nothing has decided any of them yet |
| Coverage gap (this doc) | ✅ closed at 25%, five real rulebook entries live |
| Public/private repo split, Task 3 (publish) | **still pending — awaits explicit go** |
| `Stock Framework` Obsidian vault | content complete in iCloud, never opened as a vault locally (no `.obsidian/` folder yet — a one-time Obsidian-side step, not a data problem) |

**Read this next:** the 96 Stage-3 findings are the single largest piece of
this whole reassessment still sitting untouched — every one of them names a
rule that dropped a condition its own source stated, with a citation
attached, exactly like the two that seeded this coverage-gap work
(`capital_efficiency_gate-001`'s turnaround waiver, `pe_context-001`'s
growth-matching condition). Nothing here required adjudicating them; that
work is still ahead, not behind.
