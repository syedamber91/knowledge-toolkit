# Errata — corrections to this reassessment's own findings

Every item here is a **controller analysis error**, not a defect in the SOIC
corpus, the lecture briefs, or the `soic-ladder` rulebook. All 58 lecture briefs
cleared their quote gate and none of their content is affected. What was wrong
was the layer above them: how the rulebook was read, and how source references
were resolved.

Corrected 2026-08-24, after `scripts/audit_rulebook.py` made the check
mechanical. Read this before trusting any earlier claim about what the ladder
"is missing".

---

## E1 — The ladder's citations are 15/16 sound, not 13/16

**Claimed:** three rulebook citations were defective — `pe_context-001`
(`ref: null`), `canslim_sales-001`/`canslim_pat-001` (a timestamp that does not
exist), and `growth_trap_flag-001` (a citation pointing nowhere).

**Actual:** exactly **one** is defective.

| Rule | Verdict | Note |
|---|---|---|
| `pe_context-001` | **NO_REF** — real defect | `provenance.ref` is literally `null`; read straight from the YAML, no resolution involved |
| `canslim_sales-001` / `canslim_pat-001` | **OK** | `MASTEC 00:09:35` resolves to *15.12.24 Class 4 How to Filter Epic Stocks*, where that timestamp carries the cited sentence verbatim |
| `growth_trap_flag-001` | **OK** | `TVGPF` resolves to *18.01.26 Part 1 Valuations*, where the cited window discusses growth traps and value traps |

**Root cause, two distinct mistakes with one shape — resolving an identifier
without establishing it was unique:**

1. `TVGPF` was assumed to abbreviate "TVGP Framework" and searched for in the
   two TVGP lectures. It does not; the crosswalk names a different lecture.
2. **A REF code is not a unique key. 25 of 221 codes map to more than one
   lesson** (`MODULB` maps to eight). A last-wins loader silently picked one
   candidate per collision, and picked wrong for `MASTEC`.

**Fix in force:** resolve the pair `(REF, timestamp)` — among a code's
candidates, the correct lesson is the one containing the cited timestamp. This
is now a Global Constraint of the plan, implemented in
`src/soic_wiki/ref_crosswalk.py`, and pinned by regression tests in
`tests/test_ref_crosswalk.py` and `tests/test_citation_audit.py`.

---

## E2 — The ladder already implements the exit layer

**Claimed, repeatedly:** the ladder has no moving-average rule, no concept of
relative strength, no exit rule of any kind, and an `ExitTriggers` column that no
rulebook entry defines.

**Actual:** `judge.py` computes all of it, cited to `FRAMEC`, and `cli.py`
appends it unconditionally on every run:

| Metric | What it is |
|---|---|
| `ema30_break_pct` | the 30-week EMA break |
| `nifty500_relative_strength` | relative strength vs the Nifty 500 |
| `weekly_volatility_stop` | the volatility stop |
| `exit_triggers_fired_count` | F23's 3-trigger exit count |
| `ema_period_used` | discloses when the recent-IPO EMA fallback applied |

**Root cause:** the rulebook YAML (16 entries) and the results table were read;
`judge.py` was not. These observations are appended in code, outside the YAML, so
they are invisible to anyone reading only the rulebook. Every downstream agent
inherited this framing from the context pack built for them.

**The surviving finding, which is real and narrower:** the exit layer exists and
**gates nothing**. It is observation-only, by the same deliberate design that
leaves G2 and G6 unoccupied.

---

## E3 — `ExitTriggers` does not mean "exits fired"

**Claimed:** NATIONALUM is a `CANDIDATE` carrying two fired exit triggers, so the
ladder contradicts itself.

**Actual:** the column is **how many of three triggers are currently firing**,
against a reference band of `< 3`. F23 fires only when **all three** fire at
once. NATIONALUM at 2 is *inside* the band — not an exit signal.

Measured across the 2026-08-22 run of 500 companies: 222 at zero, 43 at one, 54
at two, **151 at three**, 30 unmeasurable. And **zero `CANDIDATE`s have all three
firing** — the ladder is internally consistent on this point.

**Consequences:** the `EXIT_FIRED` transition class in the D14 weekly-loop spec
rested on this misreading, as did its rationale for ranking exits above new
candidates. Both are corrected in that spec.

---

## What this does not change

- The 58 lecture briefs and their quote gate: untouched.
- **E4 (still stands):** `pe_context-001` is the only rulebook entry with no
  source, it is contradicted by five lectures, and 27 of the 38 shortlisted names
  fail it.
- **E5 (still stands):** the screen taught in *How to Filter Epic Stocks* has four
  legs — sales ≥15%, PAT ≥20%, ROC ≥15%, **market cap ≥ ₹1,000cr** — and the
  ladder encodes the first three. The market-cap floor has no counterpart.
- **E6 (still stands):** rules recorded without the conditions attached to them in
  the source. That remains the project's central thesis and is untouched by any
  correction here.

## The generalisable lesson

Every erroneous finding above came from **inferring a reference rather than
resolving it** — guessing what a code abbreviated, letting a dict silently
overwrite a collision, reading a configuration file and assuming it was the whole
system. Where the same claims were checked mechanically, they held.

A verification gate on the *briefs* did not protect the *analysis built on top of
them*. That layer needed its own gate, which is what
`scripts/audit_rulebook.py` now is.
