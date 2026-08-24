# Fable independent second review: closed out 2026-08-25

Ties [`FABLE-REVIEW-CANSLIM.md`](FABLE-REVIEW-CANSLIM.md),
[`FABLE-REVIEW-ENTRY-TECHNICALS.md`](FABLE-REVIEW-ENTRY-TECHNICALS.md),
[`FABLE-REVIEW-CAPITAL-EFFICIENCY.md`](FABLE-REVIEW-CAPITAL-EFFICIENCY.md),
and [`FABLE-REVIEW-OBSERVATIONS.md`](FABLE-REVIEW-OBSERVATIONS.md) together.
An adversarial second pass over the Sonnet-tier adjudications in
[`LOST-CONDITIONS-GATE-CLOSEOUT.md`](LOST-CONDITIONS-GATE-CLOSEOUT.md) and
[`LOST-CONDITIONS-OBSERVATION-CLOSEOUT.md`](LOST-CONDITIONS-OBSERVATION-CLOSEOUT.md),
run specifically because those closeouts had reached a conclusion — "0 gate
edits" — worth checking harder before treating it as final. One bar was
applied that the prior pass never used: **every real condition must end as
either a gate fix or at least an observation.** "Not structurally resolvable
as a gate" was allowed to be an intermediate finding; it was never allowed
to be the last word — this rulebook's own header already proves that move
(`cash_conversion-001`: real condition, no resolvable attribute → keep the
information, drop the exclusion power).

## The result: the "0 fixes" conclusion did not survive

| | Prior (Sonnet) pass | Fable's independent re-check |
|---|---|---|
| New observations | 0 | **7** |
| New gates | 0 | 1 real candidate found (`entry_vstop-001`) — **owner chose observation instead** |
| Fabricated/misattributed citations found | — | **0**, across ~50 independently re-verified quotes |
| Factual errors in the prior pass's reasoning | — | 2 (below) |

Every one of the 7 additions was independently re-verified against the raw
transcript at its cited timestamp before being applied — not trusted from
the digest, and not trusted from Fable's own draft either; spot-checked a
third time before dispatch (e.g. the load-bearing `SMEC2 01:07:54` PEG
quote, the `pe_context-001` sector-exclusion citations).

## What actually landed — 7 additions + 1 correction, all live

All in `soic-ladder/rulebook/soic-ladder-rules-v1.yaml`, commits `8057ea9`
and `876edee`. 335 tests passing throughout, verified independently after
each apply, not just trusted from the executor's report.

**`turnaround_context-001`** — the headline finding. `capital_efficiency_gate-001`'s
seed citation, the one this entire reassessment started from months ago
("ROC criteria can be removed... where the company is inflecting from the
turnaround," FESTF 00:42:09), survived every review this thread has run and
finally has a home. Structurally still cannot become a gate — "turnaround"
is a lifecycle state, not `company`/`sector`/`is_lender` — but a reader
watching a turnaround name get a G3 FAIL now sees exactly what SOIC's own
material says about that.

**`canslim_market_direction-001`**, **`amc_growth_cycle_distortion-001`**,
**`pat_capex_distortion-001`** — three market/cycle-conditional caveats on
the CANSLIM growth gates, none gateable (market regime and equity-cycle
state are not company attributes), all now visible as context.

**`entry_rsi_context-001`**, **`entry_adx_context-001`** — surface a real,
previously-undocumented fact: the course states RSI's entry cutoff two
different ways (45 in the LTI-tool lectures, 50 in the gate's own
provenance). This project's own `DECISION-REVIEW.md` (decision D10) already
set the policy for exactly this situation — keep the deployed number, flag
the contest in output — and nothing implemented that flag until now.

**`entry_vstop_context-001`** — the one genuine new-gate candidate found in
this whole review. Multiple lectures independently describe price-above-V-Stop
as a required third entry condition alongside RSI/ADX, and the data is
already fetched (used today on the exit side). **Explicit owner decision:
observation, not a gate** — informs a reader, changes no company's
exclusion status.

**`peg_ratio-001` correction** — not an addition, a fix. The observation-level
work applied earlier today had introduced a real defect: "SOIC's stated
upper limit... is roughly 2x, with an explicit exception up to 2x for
consumer-sector businesses" is self-contradictory (if 2x is the general
ceiling, an "exception up to 2x" grants nothing). Fable traced this to two
non-identical source statements being merged into one over-neat rule —
SMEC2 states ~2x as the danger line for non-consumer names, VDVUV states
the hard rule as 1.5x with permission to 2x for consumer names specifically.
Both quotes hold up; the synthesis didn't. Corrected to state both lines
honestly rather than collapsing them.

## Two factual corrections to the prior pass's record, worth keeping

**`RSSER` is not independent corroboration of anything on
`capital_efficiency_gate-001`.** Resolving the `(REF, timestamp)` pair
properly — this reassessment's own standing discipline — showed `RSSER
01:36:57` and the gate's existing `MASTED 01:36:54-01:36:57` provenance are
the **same lesson, same moment**, cited under two different REF-code
vocabularies. The prior pass called this "the same idea" and moved on;
treating it as a second source anywhere would have been self-corroboration.
Recorded so it never gets re-added later as if it were independent evidence.

**The CANSLIM prior pass's rationale for skipping the seasonality citation
was backwards, even though its conclusion was right.** It claimed the raw
transcript settles on one universal year-on-year comparison; the transcript
actually shows SOIC reads quarter-on-quarter for non-seasonal businesses,
with year-on-year specifically protecting the seasonal case. The gate's
`_yoy_pct` metrics are still correct — YoY is the conservative, safe window
for both cases — but the reasoning on record for why no change was needed
was wrong, and would have misled anyone reading it later. Corrected in
`FABLE-REVIEW-CANSLIM.md`.

## What this confirms about the whole reassessment's method

Every addition that survived independent Fable re-verification was
corroborated across **multiple separate lectures**. Every citation Fable
still agreed to drop was single-sourced, self-disclaimed, or genuinely about
something else. That is the same bar this project settled on during the
coverage-gap work — cross-lecture corroboration, not one compelling quote —
holding up under a second, independently-run adversarial pass with real
teeth (it found a self-contradiction already sitting in a live file, a stale
technical premise, and a self-corroboration risk the first pass missed
entirely).

## Status across the whole reassessment, updated

| | State |
|---|---|
| Stage 1, Stage 2 | ✅ done, merged |
| Stage 3 detector | ✅ built, run twice |
| Coverage gap (20 unmodelled metrics) | ✅ closed at 25% |
| Gate-level + observation-level lost-condition adjudication (100 original findings) | ✅ closed, then **independently re-reviewed by Fable** |
| Fable's independent second review | ✅ **closed — this doc.** 7 additions + 1 correction applied, one new-gate candidate found and deliberately kept as observation-only per owner decision |
| Public/private repo split, Task 3 (publish) | still pending — awaits explicit go |

Every rulebook entry touched by this reassessment — 8 new (`roe_lender-001`
plus 4 coverage-gap observations plus this review's 7 minus the 1 correction
that touched an existing entry) — has now been read by at least two
independent model-tier passes before landing, with every citation traced to
a raw transcript both times.
