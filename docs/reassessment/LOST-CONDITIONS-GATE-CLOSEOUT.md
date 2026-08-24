# Gate-level lost-condition adjudication: closed out 2026-08-25

Ties [`LOST-CONDITIONS-CANSLIM.md`](LOST-CONDITIONS-CANSLIM.md),
[`LOST-CONDITIONS-ENTRY-TECHNICALS.md`](LOST-CONDITIONS-ENTRY-TECHNICALS.md),
and [`LOST-CONDITIONS-CAPITAL-EFFICIENCY.md`](LOST-CONDITIONS-CAPITAL-EFFICIENCY.md)
into one place. Read this first for the result; read those three for the
per-citation reasoning.

## What this adjudicated, and what it didn't

Stage 3's detector ([`STAGE3-CLAIM-EXTRACTION.md`](STAGE3-CLAIM-EXTRACTION.md))
originally reported "96 findings across 8 rules." That number conflated two
very different stakes levels: most of it (68 of the original 96, now 71 after
the coverage-gap work added 4 more observations) sits on **observations** —
`pe_context-001`, `growth_trap_flag-001`, `peg_ratio-001`, and the coverage-gap
additions — which by this rulebook's own design can never exclude a company
(`Observation` has no `requires_attribute` field at all; see the rulebook's
header). Only **29 findings, re-verified against the current rulebook,
consolidating to 21 distinct citations, sit on actual GATES** — rules that can
genuinely FAIL a company out of contention: `canslim_sales-001`,
`canslim_pat-001`, `entry_rsi-001`, `entry_adx-001`,
`capital_efficiency_gate-001`, `roe_lender-001`. This adjudication covers
only those 21 — the gate-level ones, where a wrong answer has real
consequences for a real company's verdict today. The 71 observation-level
findings are lower-stakes cleanup, not covered here.

## The result: 0 rulebook edits, and that is not a null result

| Bucket | Count | Meaning |
|---|---|---|
| GENUINE-NARROWING-NEEDED | **0** | Nothing could be fixed by editing YAML today |
| NOT-STRUCTURALLY-RESOLVABLE | **12** | Real, SOIC genuinely says this — but no `requires_attribute` key in `{company, sector, is_lender}` can express it |
| CONTEXT-MISMATCH-FALSE-POSITIVE | **5** | The detector matched on shared metric name, not shared meaning — mostly exit-side commentary matched to entry-only gates |
| ALREADY-CORRECTLY-SCOPED | **4** | The citation, read carefully, confirms the gate's current design rather than contradicting it |

**Zero rulebook edits does not mean "the detector found nothing real."** 12 of
21 citations are genuine SOIC-stated conditions this rulebook's current
attribute-resolution system cannot act on — including the exact turnaround
waiver that seeded this entire reassessment thread. The honest finding here
is about the schema, not the evidence.

## The turnaround waiver, specifically — the finding this whole thread started from

`capital_efficiency_gate-001`'s original seed finding, "ROC criteria can be
removed... where the company is inflecting from the turnaround" (FESTF
00:42:09, corroborated by the duplicate recording TFELT), **survived
adjudication as genuine** — verified verbatim, in-context. It lands in
NOT-STRUCTURALLY-RESOLVABLE for one precise reason: "turnaround" is not
`company`, `sector`, or `is_lender`. No `is_turnaround`-style attribute exists
in `RESOLVABLE_ATTRIBUTE_KEYS` today. The fix this needs is a schema
extension — a new resolvable attribute, plus whatever data signal would let
`resolve_attributes` actually determine turnaround status for a real company
— not a YAML edit. That is real, scoped, unstarted work, not a dead end.

The gate's third citation (RSSER, "trending toward 15%") turned out not to be
a fresh miss at all — it restates language already in the rule's own
provenance quote ("or trending toward it"), and
`docs/superpowers/specs/2026-08-21-g3-roce-triage-briefing.md` shows the
original human triage session already knew this and deliberately shipped a
point-in-time-only rule, deferring a multi-year `roce_3y_avg` derivation as
its own small feature. Real gap, but in the metric/grammar layer (a
3-year-average variant of an existing metric), not the attribute-resolution
layer this adjudication was checking.

## The other 11 NOT-STRUCTURALLY-RESOLVABLE citations, grouped by what's missing

- **Market regime** (5 citations — DSEFD, PALLOC ×2, VACRA, and one more) —
  "sideways market, so CANSLIM often fails," "choppy market, technicals
  won't work much here," growth that "works like steroids" in an up market
  and reverses in a down one. None of these are properties of a *company*;
  they're properties of the *market at judging time*. This rulebook's
  architecture judges one company against one snapshot — there is currently
  no market-regime signal anywhere in it to condition on, for any rule.
- **Trader-discretion / tunable defaults** (5 ADX citations — CSLRC ×2,
  ESRLE, MAAIM ×2) — "you can use ADX as 20 or ignore it," "experiment with
  ADX as 0 or 45 or 20," timeframe choice depending on a sector's typical
  cycle length. These describe a *range of acceptable practice*, not a
  narrower universal bar — encoding any single alternative would just
  replace one arbitrary cutoff with another, not fix anything.
- **A missing derived series** (1 citation, TVPD2) — "entry gets triggered
  when your V-Stop is positive" depends on `weekly_price_series`, already
  documented in this rulebook's own header as `not_yet_fetchable` and
  explicitly excluded from v1 for exactly that reason (F23's
  `stage4_exit_trigger` stub).

## The 5 false positives — the failure mode worth naming for next time

All 5 are RSI/ADX citations that are explicitly about **exiting or selling**
a position ("overbought RSI cannot be a reason to sell," "high RSI does not
indicate an exit," "not to be used for a selling sign") matched against
`entry_rsi-001`/`entry_adx-001`, which are entry-only gates. The detector
binds a scope claim to a threshold purely by shared metric name — it has no
concept of entry-vs-exit context, so any citation using the same indicator
for a different purpose reads as a false "dropped condition." This is the
same class of defect as the `relative_strength_vs_index` correction in
[`COVERAGE-GAP-GATHERING.md`](COVERAGE-GAP-GATHERING.md) — worth remembering
as a standing caveat on this detector's raw output, not something to
re-discover each time.

## What would actually move this further (deliberately not started here)

**Extend `RESOLVABLE_ATTRIBUTE_KEYS` with a turnaround signal.** The one
citation this reassessment has repeatedly returned to as its clearest real
gap. Needs: a definition of "inflecting from a turnaround" precise enough to
resolve from data (e.g., trailing N quarters of margin/PAT improvement off a
low base), a fetch or derivation for it, and a `requires_attribute: {}`-shaped
decision about which existing gates should be scoped by it. A real, bounded
next project — not started here, and not something to force through today's
schema.

**Market regime is a bigger, more structural gap.** Five independent
citations across three different rules all point at the same architectural
limitation: nothing in this system currently reads the market as a whole. Not
scoped or estimated here — naming it plainly is as far as this adjudication
goes.

## Status across the whole reassessment, updated

| | State |
|---|---|
| Stage 1, Stage 2 | ✅ done, merged |
| Stage 3 detector | ✅ built, run twice |
| Coverage gap (20 unmodelled metrics) | ✅ closed at 25% — see [`COVERAGE-GAP-CLOSEOUT.md`](COVERAGE-GAP-CLOSEOUT.md) |
| Gate-level lost-condition findings (21 distinct citations, 29 raw) | ✅ **closed — this doc.** 0 edits made; 12 real-but-unfixable-today, 5 false positives, 4 confirmations |
| Observation-level lost-condition findings (71) | **not yet looked at** — lower stakes (never excludes anyone), but still untouched |
| Public/private repo split, Task 3 (publish) | still pending — awaits explicit go |
