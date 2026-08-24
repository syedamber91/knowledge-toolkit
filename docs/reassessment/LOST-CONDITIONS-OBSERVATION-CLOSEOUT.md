# Observation-level lost-condition adjudication: closed out 2026-08-25

Ties [`LOST-CONDITIONS-PE-CONTEXT.md`](LOST-CONDITIONS-PE-CONTEXT.md),
[`LOST-CONDITIONS-PEG.md`](LOST-CONDITIONS-PEG.md), and
[`LOST-CONDITIONS-MARKETCAP-PB.md`](LOST-CONDITIONS-MARKETCAP-PB.md)
together. Companion to [`LOST-CONDITIONS-GATE-CLOSEOUT.md`](LOST-CONDITIONS-GATE-CLOSEOUT.md),
which adjudicated the higher-stakes half of Stage 3's original findings (the
29 that sit on GATES, which can exclude a company). These 71 sit on
**observations** — `Observation` has no `requires_attribute` field by
design, so nothing here could ever have changed who gets excluded. The
question this thread answered was narrower and lower-stakes: is the
*informational text a reader sees* complete, or silently thin.

## What actually changed

Three `display_text` fields, all in `soic-ladder/rulebook/soic-ladder-rules-v1.yaml`,
commit `84c5028`. No `metric`, `reference_band`, `gate`, or `requires_attribute`
changed anywhere — this thread could not and did not touch exclusion logic.

**`pe_context-001`** — the biggest finding of the whole thread. This is the
rulebook's **most-cited observation** (30 independent lecture citations
pointed at it) and its `display_text` was one bare sentence: *"Price to
earnings, read against a 15 to 35 reference band."* Verified independently
before applying (not just trusting the adjudication pass) — the sector
exclusion is real and shows up across at least four separate lectures in
almost identical language: ARTBV ("will not work in life insurance
companies, will not work in banks, will not work in real estate companies"),
SMECS ("banks, real estate companies and life insurance companies you can't
see the PE ratio"), BUFF ("never ever look at price to earnings ratio,
especially... cement sector"), BVB ("cannot value a hospital stock on P").
Grew to 613 characters: now states plainly that P/E does not apply to
banks/NBFCs/insurers (use price-to-book or embedded value), real estate, or
deep-cyclicals like cement; is unreliable for earnings depressed by one-offs
or operating leverage; reads best on mature stable-earners or low-gestation
names; and — the second theme, corroborated separately — is a screening
signal only when read alongside growth, never a standalone bar.

**`growth_trap_flag-001`** — one sentence appended, stating the reverse
condition the source also states: a rich multiple can be *justified*, not
flagged as a trap, if growth is fast enough to sustain it or the investor
accepts riding out a multi-year correction rather than treating the multiple
as fixed.

**`peg_ratio-001`** — corrected a real mischaracterization, not just an
omission. The existing text said SOIC's PEG target is "below 1.5x" as if
that were the ceiling. Verified against the raw quotes: SMEC2 states the
real ceiling as "more than 2x pegged ratio for any businesses apart from the
consumer sector," VDVUV explains the consumer exception ("easier to
forecast"), BVB gives a further nuance (ceiling stretches to ~1.75x at high
entry P/E if growth keeps pace). 1.5x is a *target*; SOIC's actual stated
upper limit is roughly 2x, with a named sector exception. Grew to 854
characters to say so, plus the growth-runway leniency clause (RSSER).

**`market_cap_floor-001` and `price_to_book_deep_value-001`** — no changes.
Both were added earlier in this same session; the adjudication pass
confirmed all 3 of their findings were already reflected in the
`display_text` written when they were created. One minor wording note
surfaced (the rulebook's gloss says "banks -> P/B" but the underlying BVB
quote says "NBFC" — the "banks" phrasing actually comes from the
corroborating ARTBV citation) — recorded as a possible future tightening,
not acted on, since `is_lender` already covers both populations identically.

## The pattern across both closeouts, worth remembering

Every observation-level bucket-1 finding that survived independent
verification was corroborated across **multiple separate lectures**, often
using near-identical language. Every citation that came from a single
lecture, a single company's illustration, or read like personal
commentary landed in "too thin" or "already covered," not "add this." That
bar — cross-lecture corroboration, not a single compelling quote — is what
should keep governing any future pass over this rulebook's text, gate or
observation.

## Status across the whole reassessment, updated

| | State |
|---|---|
| Stage 1, Stage 2 | ✅ done, merged |
| Stage 3 detector | ✅ built, run twice |
| Coverage gap (20 unmodelled metrics) | ✅ closed at 25% |
| Gate-level lost-condition findings (21 distinct citations) | ✅ closed — 0 edits, 1 real unfixable-today gap named (turnaround signal) |
| Observation-level lost-condition findings (40 distinct citations across 5 observations) | ✅ **closed — this doc.** 3 `display_text` fields expanded, verified against raw quotes before applying |
| Public/private repo split, Task 3 (publish) | still pending — awaits explicit go |

Every Stage-3 finding — all 100 of them, gate and observation alike — has
now been read, verified, and adjudicated. Nothing from that detector's
output remains untouched.
