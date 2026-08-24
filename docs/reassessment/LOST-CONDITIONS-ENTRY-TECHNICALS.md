# Lost-condition adjudication: entry_rsi-001 / entry_adx-001 (G8)

This file adjudicates the mechanical lost-condition detector's findings against
`entry_rsi-001` (G8, `weekly_rsi >= 50`) and `entry_adx-001` (G8, `weekly_adx >= 20`) in
`soic-ladder/rulebook/soic-ladder-rules-v1.yaml`. Both rules are unscoped
(`requires_attribute: {}`) and both `display_text` fields say "entry" — G8 is
specifically an entry-timing gate, not an exit/sell gate. Source of evidence:
`out/lost_conditions_digest.json`'s `entry_rsi-001` and `entry_adx-001` entries.

**Adjudication method.** The detector matches purely on shared metric name
(`weekly_rsi` / `weekly_adx`), with no awareness of entry-vs-exit framing. Every
dropped condition is read against the rule it was matched to, against
`RESOLVABLE_ATTRIBUTE_KEYS = {company, sector, is_lender}` (per the rulebook's own
header), and against how gates actually combine
(`report.py::final_verdict` — **every** gate (G0, G1, G3, G8, …) must pass or be
NOT_APPLICABLE for a company to reach CANDIDATE; a FAIL on any one gate demotes the
whole company to WATCH). Two citations (`CSLRC 00:12:07`, `PALLOC 01:28:23`) and one
(`TVPD2 01:10:30`) are cited by both digests and are adjudicated once, noted as
shared.

Buckets, one section per distinct citation:

1. GENUINE-NARROWING-NEEDED
2. NOT-STRUCTURALLY-RESOLVABLE
3. CONTEXT-MISMATCH-FALSE-POSITIVE
4. ALREADY-CORRECTLY-SCOPED

---

## Applies to both gates

### CSLRC 00:12:07 — "you should be a little more validating on the basis of L3"

> **Statement:** A triggered LTI/Parabolic SAR buy or averaging-up signal should not
> be acted on from technicals alone — it must be cross-checked against the L3
> fundamentals/valuation framework first.

**Verdict: ALREADY-CORRECTLY-SCOPED**

This is not a scoping condition for *when* the RSI/ADX bar applies — it's a caution
that a technicals-only signal shouldn't be acted on in isolation. But that's exactly
what this rulebook already does structurally: `final_verdict()` requires G8 (entry
technicals) **and** G0 (CANSLIM sales/PAT growth) **and** G1 (leverage) **and** G3
(capital efficiency / ROE) to all pass (or be NOT_APPLICABLE) before a company reaches
CANDIDATE — a FAIL on any single gate demotes the whole company to WATCH. A
technicals-only pass on G8 with fundamentals failing elsewhere already cannot produce
a CANDIDATE verdict. The quote describes a discipline this multi-gate architecture
already enforces by construction; there is no gap to fix here.

### PALLOC 01:28:23 — "because the type of market we are in choppy market, technicals are not going to work much here"

> **Statement:** In a sideways or choppy market regime, weekly technical trend
> filters such as RSI and ADX should be de-weighted relative to fundamental
> judgment, since they tend to produce premature stop-outs.

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

This is the market-regime case flagged explicitly in the adjudication brief. "Choppy
market" is a property of the overall index/tape at a point in time, not a property of
`company`, `sector`, or `is_lender`. No `requires_attribute` scoping can express "skip
this gate when the market is choppy" — that would need a market-regime signal the
rulebook has no metric for at all (and no company-level attribute could carry it even
if it existed, since it's the same value for every company on a given day). Real
condition, structurally out of reach for this encoding.

### TVPD2 01:10:30 — "Entry gets triggered when your V stop is positive"

> **Statement:** RSI above 50 and ADX above 20 are each necessary but not sufficient
> for an entry signal; V-Stop must also be positive before entry actually triggers.

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

This is a real, additional entry precondition — but it's a *third gate metric*
(V-Stop / volatility-stop, derived from `weekly_price_series`), not a scoping
condition on when RSI/ADX apply to a given company. It doesn't fit
`RESOLVABLE_ATTRIBUTE_KEYS` at all (it's not company/sector/is_lender-shaped), and the
rulebook's own header already excludes this exact dependency: F23's stage4 exit
trigger stub was deliberately left out of v1 because it depends on
`weekly_price_series`, which is `not_yet_fetchable` (no fetch, no derivation) —
and any rule needing it would ABSTAIN for every company forever, which is contagious
to `final_verdict` (any ABSTAIN → INSUFFICIENT). Adding a V-Stop-gated version of
entry_rsi/entry_adx today would hit the identical wall already documented in the
header. Confirms the existing exclusion rather than adding a new one.

---

## entry_rsi-001 only

### FSSDF 00:29:08 — "overbought or above 70 RSI cannot be a reason to particularly sell a stock"

**Verdict: CONTEXT-MISMATCH-FALSE-POSITIVE**

Explicitly about **selling** — an overbought RSI reading being rejected as a sell
trigger. `entry_rsi-001` is an entry gate (`weekly_rsi >= 50`, a *lower* bound, not an
overbought-at-70 upper bound used for exits). The detector matched on the shared
`weekly_rsi` metric name, not on any actual overlap in what the rule does. No change
needed.

### FSSMF 01:53:46 — "for buying selling this is a worst indicator because it will make you miss a lot of good opportunities"

**Verdict: CONTEXT-MISMATCH-FALSE-POSITIVE**

Read in context, this is again the sell-side critique: RSI (overbought readings) is
rejected as a basis for exiting a compounding stock, since selling on it causes
investors to miss further upside. Not a statement about the entry-side ">= 50"
threshold this gate encodes.

### TVPD2 01:15:25 — "High RSI does not indicate an exit"

**Verdict: CONTEXT-MISMATCH-FALSE-POSITIVE**

Same pattern, explicit this time: "does not indicate an **exit**." This is the
exit-side companion rule to the entry-side threshold `entry_rsi-001` encodes; they are
about different decisions (when to sell vs. when to buy), not conflicting statements
about the same decision.

---

## entry_adx-001 only

### CSLRC 00:12:24 — "you can use ADX 20 or you can choose to ignore it as well"

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

States ADX>=20 is optional in the underlying LTI tool — a trader's discretionary
choice to include or drop it, not a condition keyed to any company/sector/is_lender
attribute. There's no resolvable variable here to hang a `requires_attribute` clause
on; it's "sometimes traders skip this filter," which isn't a fact about a company at
all.

### CSLRC 00:14:14 — "ADX you can use as 20 just for confirmation"

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

Same discretionary-role point from the same lecture: when kept, ADX should function as
a confirming signal rather than a required independent trigger. That's a statement
about how heavily to weight the signal in a human trader's overall judgment, not a
condition that maps to `company`, `sector`, or `is_lender`.

### ESRLE 01:49:29 — "you can experiment with ADX as 0 and you can experiment with ADX as 45 or 20"

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

This is the "specific numeric range being acceptable rather than one fixed cutoff"
case named in the adjudication brief — the instructor presents 20 as one adjustable
default among several the trader might experiment with (0/20/45), not a scoping
condition on which companies the >=20 bar applies to. No resolvable attribute
expresses "sometimes 0, sometimes 45."

### MAAIM 00:26:26 — "because it's the cyclical business preferably I'll use weekly because these cycles they last anywhere between 6 to 9 months"

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

At first glance this looks like a `sector`-attribute condition (cyclical vs.
non-cyclical), which is one of the three resolvable keys — but the actual content is a
**timeframe** choice (weekly vs. monthly ADX), not a threshold or applicability
condition on the existing `weekly_adx >= 20` rule. The rulebook's registry has no
`monthly_adx` metric, and the quote doesn't state what the bar (or timeframe) should
be for *non*-cyclical businesses — only that weekly is preferred for cyclicals, which
happens to be what this rule already does. Encoding "read ADX weekly for cyclicals"
would require a metric (`monthly_adx`) that doesn't exist in this corpus's fetchable
set; there's nothing here to safely narrow *this* rule with.

### MAAIM 00:22:33 — "you have to combine volatility stock with ADX otherwise it won't be of a use"

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

Same shape as the shared TVPD2 01:10:30 finding above: ADX alone is described as
insufficient without a companion volatility-stop signal. That companion metric is not
in `RESOLVABLE_ATTRIBUTE_KEYS`, and (per the rulebook header's F23 exclusion) anything
built on `weekly_price_series`-derived signals is `not_yet_fetchable` and would poison
`final_verdict` with contagious ABSTAIN. Real condition, same structural wall as
before.

### MAAIM 00:12:50 — "ADX is a very good buy indicator, but ADX is not a good sell indicator"

**Verdict: ALREADY-CORRECTLY-SCOPED**

This is direct, explicit confirmation of the current design, not a gap. The
instructor states in one breath that ADX is well-suited to buy/entry decisions and
poorly suited to sell/exit decisions. `entry_adx-001` sits in G8, an entry-only gate,
with no exit-side ADX rule anywhere in the rulebook. The citation is evidence the
placement is right, exactly the "ADX is good for buying, not for selling" example
named in the adjudication brief as the canonical bucket-4 case.

### TVPD2 00:32:09 — "ADX isn't to be used for a like a selling sign"

**Verdict: CONTEXT-MISMATCH-FALSE-POSITIVE**

Explicit exit-side exclusion, mirroring the RSI exit-side quotes above: ADX weakening
should not be read as a sell trigger. `entry_adx-001` never claims ADX works
symmetrically for exits — it's an entry-only gate — so this citation describes a
decision this rule doesn't make, matched only because it shares the `weekly_adx`
metric name.

---

## Summary table

| Citation (ref + ts) | Applies to | Bucket | One-line reason |
|---|---|---|---|
| CSLRC 00:12:07 | both | ALREADY-CORRECTLY-SCOPED | Multi-gate `final_verdict` already requires fundamentals gates alongside G8; technicals-only can't reach CANDIDATE |
| PALLOC 01:28:23 | both | NOT-STRUCTURALLY-RESOLVABLE | Choppy-market regime is not a company/sector/is_lender attribute |
| TVPD2 01:10:30 | both | NOT-STRUCTURALLY-RESOLVABLE | V-Stop precondition needs `weekly_price_series`, already documented `not_yet_fetchable` |
| FSSDF 00:29:08 | RSI | CONTEXT-MISMATCH-FALSE-POSITIVE | About rejecting overbought RSI as a sell trigger, not entry |
| FSSMF 01:53:46 | RSI | CONTEXT-MISMATCH-FALSE-POSITIVE | About RSI as a bad indicator for selling/exiting |
| TVPD2 01:15:25 | RSI | CONTEXT-MISMATCH-FALSE-POSITIVE | "High RSI does not indicate an exit" — exit-side statement |
| CSLRC 00:12:24 | ADX | NOT-STRUCTURALLY-RESOLVABLE | Discretionary "use it or ignore it" — no resolvable attribute captures trader discretion |
| CSLRC 00:14:14 | ADX | NOT-STRUCTURALLY-RESOLVABLE | "Use as confirmation only" is a weighting preference, not a scoping condition |
| ESRLE 01:49:29 | ADX | NOT-STRUCTURALLY-RESOLVABLE | Presents 20 as one experimental value among 0/20/45, not a fixed scoped cutoff |
| MAAIM 00:26:26 | ADX | NOT-STRUCTURALLY-RESOLVABLE | Timeframe (weekly vs. monthly) preference for cyclicals; no `monthly_adx` metric exists |
| MAAIM 00:22:33 | ADX | NOT-STRUCTURALLY-RESOLVABLE | Requires combining with a not-yet-fetchable volatility-stop signal |
| MAAIM 00:12:50 | ADX | ALREADY-CORRECTLY-SCOPED | "ADX is a good buy indicator, not a good sell indicator" confirms entry-only placement |
| TVPD2 00:32:09 | ADX | CONTEXT-MISMATCH-FALSE-POSITIVE | "ADX isn't to be used for a selling sign" — exit-side exclusion |

**Totals: 13 distinct citations — 0 GENUINE-NARROWING-NEEDED, 7 NOT-STRUCTURALLY-RESOLVABLE, 4 CONTEXT-MISMATCH-FALSE-POSITIVE, 2 ALREADY-CORRECTLY-SCOPED.**

**Headline finding.** No citation calls for a YAML change. The dominant pattern (4/13)
is exactly the false-positive mode named in the adjudication brief: the detector's
metric-name-only matching pulls in exit/sell-side commentary about RSI and ADX and
pins it on an entry-only gate purely because the metric names coincide — none of these
citations say anything about when *entry* should or shouldn't fire. The
market-regime and companion-indicator citations (7/13) are real statements from the
source material but depend on signals this rulebook has already, deliberately, chosen
not to encode (market regime, `weekly_price_series`-derived V-Stop/volatility-stop),
consistent with the header's existing F23 exclusion. Two citations actively confirm
the current design is correct rather than gap it. `entry_rsi-001` and `entry_adx-001`
need no change.
