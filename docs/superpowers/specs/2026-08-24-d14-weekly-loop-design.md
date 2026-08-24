# D14 — The weekly loop

**Date:** 2026-08-24 · **Status:** spec, not built
**Decided in:** `brainstorms/2026-08-24-stock-framework-knowledge-graph.md` (D14)
**Review that produced it:** `docs/reassessment/DECISION-REVIEW.md`

## The target state, stated by the owner

> "every week we are able to identify the right set of companies to invest in,
> using the knowledge which is there from the lectures, easily, effectively,
> being able to query and figure out some of this data."

## What is actually missing

The ladder already runs. `soic_ladder.cli` has two subcommands: `snapshot`
(the only networked one — fetches and freezes into `runs/snapshots/<as-of>/`)
and `judge` (evaluates **offline** against a stored snapshot, so a re-run is
reproducible). Verdicts are `CANDIDATE` / `WATCH` / `REJECTED` / `INSUFFICIENT`.

So the engine is not the gap. The gap is that **its output is a wall, not a
reading list**: the 2026-08-22 run produced 49 CANDIDATEs, 27 after the Shariah
screen. Nothing diffs one run against the last, nothing ranks, nothing caps, and
nothing says what to *do* with a name once it appears.

Note also what does and does not change week to week. **The lecture corpus does
not change.** Prices, quarterly results and ratios do — and none of those live in
the claims graph. The graph supplies *judgement*; the snapshot supplies *facts*.
The loop is where they meet.

## Pipeline

```
1. snapshot   networked, paced, frozen        -> runs/snapshots/<as-of>/
2. judge      offline, deterministic          -> ladder-<as-of>.json
3. shariah    existing screen                 -> compliant subset
4. diff       vs the previous accepted run    -> transitions
5. rank       by transition class, NOT a score
6. cap        top N (default 5) + a queue
7. attach     `procedure` claims per name     -> what to actually do
8. emit       weekly brief + append to a log
```

Steps 1-3 exist. **Steps 4-8 are the build.**

## Step 4 — diff is the load-bearing step

A weekly list should answer *what changed*, not *what passes*. Transitions,
computed against the previous accepted run:

| Class | Meaning |
|---|---|
| `NEW_CANDIDATE` | absent or WATCH last week, CANDIDATE now |
| `LOST_CANDIDATE` | CANDIDATE last week, no longer |
| `EXIT_FIRED` | `ExitTriggers` went from 0 to >0 while still CANDIDATE |
| `GATE_FLIP` | any individual gate changed PASS/FAIL |
| `UNCHANGED` | suppressed from the brief entirely |

`UNCHANGED` suppression is what turns 27 names into a handful. A company that
passed last week and passes this week needs no attention.

**`EXIT_FIRED` outranks `NEW_CANDIDATE`.** The current run already contains
NATIONALUM as a CANDIDATE with 2 exit triggers — a contradiction the table
surfaces but nobody is told about. A loop that reports new buys before it reports
fired exits is the wrong way round.

## Step 5 — rank, and the trap in it

**Do not compute a composite score.** Blending corroboration counts, gate
margins and evidence strength into one number would manufacture a ranking nobody
in the corpus stated — the exact failure this whole project exists to correct
(a dated one-company example promoted to a universal bar).

Rank deterministically by transition class in the order above, then within a
class by ticker for stability. **Annotate** with evidence; never fold evidence
into a number:

- corroboration-backed lecture claims for and against the name (from the graph,
  counted by **session** not file — five Crash lectures are two-part recordings)
- whether the name is `contested` in the vault (both doubt and support)
- which gates it passes on a thin margin (ASIANPAINT clears the RSI floor by
  0.74 — that is a fact worth showing, not a number to blend)

## Step 6 — the cap

Default **5 per week**, plus a queue file carrying the overflow with its
transition class, so nothing is silently dropped. The cap exists because the
owner is not a full-time quant; a list that cannot be read will not be read.

## Step 7 — attach the procedure

This is where the lecture corpus earns its place. Every surfaced name carries the
`procedure` claims from the graph — the steps the corpus says to take *after* a
screen fires. From the briefs: read the concall, the DRHP, the AGM, check
guidance-versus-delivered, check whether growth is volume or price, check whether
PAT growth is deleveraging-driven.

That is the answer to "using the knowledge which is there from the lectures":
not the screen, which is only four numbers, but **what the corpus says to do
next**.

## Step 8 — output

`runs/weekly/<as-of>/brief.md`, and an append-only `runs/weekly/LOG.md`
following the repo's existing log contract (parse the last `(N total`, word the
first entry as a backfill, append only on change).

The brief opens with fired exits, then new candidates, then gate flips, then a
one-line "N unchanged, suppressed".

## Deliberately not in scope

- **No auto-apply to the rulebook.** D9 stands: the graph proposes, a human
  applies. The loop consumes the rulebook; it never edits it.
- **No contested threshold silently changing.** Per D14 in the review,
  contested-but-deployed thresholds hold their current values, flagged in the
  brief, until adjudicated. The loop must not stall waiting for adjudication,
  and must not quietly adopt a different number either.
- **No trading actions.** The output is a research list. Nothing here places,
  sizes, or recommends a position.

## How this fails silently — and the guards

| Failure | Guard |
|---|---|
| Snapshot silently stale; the "diff" compares a run to itself | Refuse to emit if `as-of` equals the previous run's date; print both dates in the brief header |
| Shariah step unavailable, loop emits the unscreened list | Hard-fail the step; never fall back to the unfiltered set |
| Previous run missing, so every name reads as `NEW_CANDIDATE` | Detect an empty baseline and label the brief a **backfill**, never a week's news |
| A data fault reads as a real transition | Carry the known-suspect cells forward (CPPLUS's negative cash conversion, CFO/PAT >200% for TMCV/MOTHERSON/EXIDEIND, six blank PEG cells); flag rather than rank them |
| The brief looks authoritative because the graph exists | Every claim in the brief carries its citation; anything unsourced is labelled as such |

## Open questions for the owner

1. **Cadence and trigger** — a scheduled job, or run by hand? Snapshot is
   networked and paced; judge is offline. Auto-running both is read-only and
   safe, but the owner may prefer to trigger it.
2. **What is the "previous accepted run"** — simply the last run, or a run the
   owner marks accepted? Marking prevents a bad snapshot becoming the baseline.
3. **Universe** — the last run used Nifty 500; the CLI defaults to NIFTY200.
   Which is the weekly universe?
4. **Cap of 5** — right number?

## Build order

1. Step 4 (diff) against the two snapshots already on disk (2026-08-20,
   2026-08-22). It is testable immediately with real data and no new fetching.
2. Steps 5-6 (rank, cap).
3. Step 7 (procedure attachment) — depends on `claims.json`, so it lands after
   the graph pilot.
4. Step 8 (brief + log).

Steps 1-2 are independently useful: a diff of the two existing runs answers
"what changed in two days" today, with no graph at all.
