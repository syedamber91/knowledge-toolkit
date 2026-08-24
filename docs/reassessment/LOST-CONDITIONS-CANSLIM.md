# Lost-condition adjudication: `canslim_sales-001` / `canslim_pat-001`

This file adjudicates the "lost condition" findings the mechanical detector
raised against the two CANSLIM gates in
`soic-ladder/rulebook/soic-ladder-rules-v1.yaml`:

- `canslim_sales-001` — G0, `sales_growth_yoy_pct >= 15`, `requires_attribute: {}`
- `canslim_pat-001` — G0, `pat_growth_yoy_pct >= 20`, `requires_attribute: {}`

Both are hard PASS/FAIL gates at G0 — one of only four gates in this
rulebook that can actually exclude a company from ever becoming a
CANDIDATE. Both cite the same provenance: `MASTEC 00:09:35`, "screen for
>15% YoY quarterly sales growth and >20% PAT growth."

The detector matches purely on shared metric name (`sales_growth_yoy_pct` /
`pat_growth_yoy_pct` appearing anywhere else in the transcripts), with zero
awareness of whether the surrounding lecture is talking about a universal
rule, one company's one-off situation, or a different question entirely.
Source: `out/lost_conditions_digest.json`, entries `canslim_sales-001` and
`canslim_pat-001`.

Constraint carried over from the rulebook itself: `RESOLVABLE_ATTRIBUTE_KEYS
= {company, sector, is_lender}` (`src/soic_ladder/resolvable_attributes.py`).
A condition only lands in bucket 1 if it can be expressed through one of
those three keys (or some other concrete, resolvable mechanism I can name
exactly).

---

## Citations shared identically between both gates

### 1. DSEFD 01:23:16 — "Today sideways market, so can slim often fails."

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

Read literally, this is a statement about the overall market regime, not
about any company. The instructor is saying CANSLIM as a screening
methodology (both its sales-growth and PAT-growth legs — the quote says
"can slim," not "the sales leg" or "the PAT leg") tends to underperform or
misfire when the broader market itself is sideways/range-bound, as opposed
to trending. There is no company-level fact this maps to. `company`,
`sector`, and `is_lender` are all properties of the company being screened;
"is the market currently sideways" is a property of the market at the time
of the screen, which none of `RESOLVABLE_ATTRIBUTE_KEYS` can express, and
which would need to be re-evaluated on every screening run regardless of
which company is being looked at — not something `requires_attribute`
scoping was built for.

This is exactly the class of condition the task brief names as the
canonical NOT-STRUCTURALLY-RESOLVABLE case: overall market regime. Naming
it here is still valuable even though nothing in the rulebook can act on
it — a future "market regime" input (if this system ever gains one) is the
right place to revisit this, not a per-company attribute.

Applies identically to both `canslim_sales-001` and `canslim_pat-001`.

---

### 2. SGBT2 00:27:39 — "the strongest quarter in the hotel industry is your Q3 quarter, now Q3 quarter will be compared with Q3, not Q2"

### 3. SGBT2 00:28:08 — "So now we will see year on year, right?"

**Verdict: ALREADY-CORRECTLY-SCOPED** (both citations, taken together)

Read literally, these two quotes are one continuous exchange about *which
comparison window* to use for a quarterly growth screen. The instructor's
worked example (00:27:39) warns against comparing a seasonal business's
strong quarter (hotels' Q3) against the immediately preceding quarter
(Q2) — that would manufacture a growth number driven by seasonality, not
by the business improving. The resolution, confirmed at 00:28:08, is to
compare year-on-year instead: same calendar quarter, prior year. The
digest's own `scope_statement` for the second quote makes this explicit —
it calls the YoY comparison correct for *both* the seasonal (hotel) and
non-seasonal (IT) case, i.e. this settles into one universal comparison
rule, not a sector-conditional one.

That is exactly what these two gates already do. Both metrics are named
`sales_growth_yoy_pct` and `pat_growth_yoy_pct` — confirmed in
`rulebook/vendor/metric-registry.yaml` as "Quarterly Sales Growth YoY %"
and "Quarterly PAT Growth YoY %" respectively. The "YoY" in the metric name
*is* the same-quarter-prior-year comparison SGBT2 arrives at. There is no
separate QoQ variant these gates could be confused with, and no sector
carve-out to add, because the lecture's own conclusion is "always compare
year-on-year," which is what the gate already measures by construction.

I want to be precise about what this verdict does *not* cover: whether the
metric-fetch layer somewhere else in the codebase actually computes
same-quarter-prior-year correctly for every company is an implementation
question, not a rulebook-scoping question, and is out of scope for this
adjudication — the digest's dropped-condition claim was about whether the
*rule* needs a comparison-window condition it's missing, and it doesn't:
the rule is already defined against a YoY metric.

Applies identically to both gates (both use a `_yoy_pct` metric).

---

### 4. VACRA 02:01:53 — "in an up market these businesses work like steroids when it comes to profit growth. But in a down market the opposite happens."

**Verdict: NOT-STRUCTURALLY-RESOLVABLE**

The `scope_statement` names the subject as AMC/wealth-management
businesses specifically, and at first glance that looks like a `sector`
match — the one `RESOLVABLE_ATTRIBUTE_KEYS` entry built for exactly this
kind of business-model carve-out (the same key that scopes `leverage-001`
and `capital_efficiency_gate-001` away from lenders).

Reading the quote literally, though, the defect it names is not "AMC
growth numbers are structurally the wrong shape for this metric" (the
`is_lender` case: a lender's balance sheet makes ROCE's denominator
*always* mean something different, in any market). It's "AMC growth
numbers are directionally distorted depending on where the broader equity
cycle currently stands" — inflated in an up market, collapsed in a down
market. The sign and magnitude of the distortion is a function of the
market regime at the time of the screen, not a fixed property of the
sector. A `requires_attribute: {sector: "asset_management"}` exclusion
would remove AMCs from this gate unconditionally, but that overstates what
VACRA says: in some market regimes an AMC's reported growth number may be
perfectly informative, and a blanket sector exclusion would silently
discard that. Correctly implementing what the source actually says would
require knowing the equity-cycle position at evaluation time, which is a
market-regime input, not a company/sector/is_lender attribute — the same
structural gap as citation 1 above, just narrower in scope (one sector
instead of every company).

I considered forcing this into bucket 1 as a coarse `sector`-based
exclusion (mirroring the lender exclusions), and rejected it: unlike the
lender case, the source's own reasoning is explicitly market-timing-
conditional, not a claim that the ratio is structurally meaningless for
this sector. Encoding a sector exclusion here would be solving a different,
easier problem than the one VACRA actually raises, and would look more
sourced than it is — the same overreach the file's own 2026-08-13 revision
history (header comment items 2–4) already flagged and walked back once.

Applies identically to both `canslim_sales-001` and `canslim_pat-001` (the
quote covers "profit growth" but the digest attaches it to both metrics,
and the same up-market/down-market MTM distortion applies to reported
sales/AUM-linked revenue for these businesses too).

---

## Citation specific to `canslim_pat-001` only

### 5. PALLOC 01:33:32 — "over next 18 months, the company will not see any [PAT] growth because interest, cost, depreciation will keep killing the profit and loss statement but even though business within itself will become stronger I like the long term prospects of the business"

**Verdict: CONTEXT-MISMATCH-FALSE-POSITIVE**

Read literally, this is the instructor talking through his own view of one
specific company's specific situation ("the company," a single named case
in that lecture) during a capex ramp-up — not a stated universal rule
about when the PAT-growth screen should or shouldn't apply. Two things
mark it as a mismatch rather than a real scoping gap:

1. **Single-company narrative, not a stated rule.** The quote never
   generalizes ("companies undergoing capex ramp-up should be exempted
   from the PAT growth gate"); it's the instructor explaining why *he*
   personally likes *this* business despite its numbers being weak for the
   next 18 months. That is the same shape of defect the rulebook's own
   header already names and rejects for `embedded_growth-001`: a
   one-company, dated illustration should not be read as if it were a
   general screening rule.
2. **Different investing style, not a scoping condition on this one.**
   CANSLIM (the "C" and part of the "A" in the acronym) is specifically a
   current-growth momentum screen — it exists to filter FOR companies
   already showing strong quarterly growth. The instructor here is
   describing a long-horizon, turnaround/value-style thesis: he's
   comfortable holding a company that fails a growth screen today because
   he expects the underlying business to strengthen regardless. That's not
   evidence the CANSLIM PAT bar is misapplied when it correctly fails this
   company — it's evidence that CANSLIM screening and this instructor's
   long-horizon thesis-driven investing are two different tools, and here
   he's explicitly choosing the second one over the first for a specific
   name. A hard G0 gate correctly rejecting a company from the CANSLIM
   candidate path doesn't contradict a different, non-CANSLIM rationale for
   still liking the stock — the ladder isn't claiming to be the only lens
   SOIC ever uses.

This is not a case where the citation is about an unrelated topic — it
genuinely is about PAT growth being weak for a real reason — but it's
talking about a different question (should *I*, as an investor with a
specific thesis, hold this specific company) than the one this gate asks
(does this company clear a stated universal quarterly-growth screening
bar). That's the CONTEXT-MISMATCH pattern as defined: a single company's
one-off situation, framed through a different investing style's logic,
rather than a stated universal rule this gate should be narrowed by.

Applies only to `canslim_pat-001` — not cited against the sales gate.

---

## Summary table

| Citation (ref + ts) | Bucket | One-line reason |
|---|---|---|
| DSEFD 01:23:16 — "sideways market, so can slim often fails" | NOT-STRUCTURALLY-RESOLVABLE | Market regime (sideways vs. trending) at screening time — no company/sector/is_lender attribute expresses that; applies identically to both gates. |
| SGBT2 00:27:39 — "Q3 will be compared with Q3, not Q2" | ALREADY-CORRECTLY-SCOPED | Settles on year-on-year comparison for seasonal businesses, which is exactly what the `_yoy_pct` metric already measures by definition; applies identically to both gates. |
| SGBT2 00:28:08 — "So now we will see year on year, right?" | ALREADY-CORRECTLY-SCOPED | Confirms YoY as the universal comparison window for seasonal and non-seasonal businesses alike — no carve-out needed since the gate already uses a YoY metric; applies identically to both gates. |
| VACRA 02:01:53 — "steroids in an up market... opposite in a down market" | NOT-STRUCTURALLY-RESOLVABLE | AMC/wealth-management growth distortion is direction-dependent on the equity cycle, not a fixed sector property — a sector exclusion would overstate what the source says; applies identically to both gates. |
| PALLOC 01:33:32 — "will not see any [PAT] growth... I like the long term prospects" | CONTEXT-MISMATCH-FALSE-POSITIVE | One company's capex-ramp narrative filtered through the instructor's own long-horizon thesis, not a stated universal PAT-growth screening exception; `canslim_pat-001` only. |

**Bucket totals:** GENUINE-NARROWING-NEEDED: 0. NOT-STRUCTURALLY-RESOLVABLE:
2 (DSEFD, VACRA — each counted once, applying identically to both gates).
CONTEXT-MISMATCH-FALSE-POSITIVE: 1 (PALLOC, `canslim_pat-001` only).
ALREADY-CORRECTLY-SCOPED: 2 (both SGBT2 quotes, applying identically to
both gates). No proposed YAML change: nothing here rises to a genuine,
resolvable narrowing gap in `canslim_sales-001` or `canslim_pat-001` as
currently written.
