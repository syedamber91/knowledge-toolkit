# SOIC L3/L4/L5 Crux Reassessment — design

**Date:** 2026-08-23
**Status:** approved, L3 in flight

## Problem

`soic-ladder`'s current rulebook (`rulebook/soic-ladder-rules-v1.yaml`, 16 entries)
encodes the SOIC method as numeric thresholds. Only **four** of those entries are
gates that can fail a company:

| Gate | Rule | Threshold |
|---|---|---|
| G0 | `canslim_sales-001` | sales_growth_yoy_pct >= 15 |
| G0 | `canslim_pat-001` | pat_growth_yoy_pct >= 20 |
| G1 | `leverage-001` | debt/equity |
| G3 | `capital_efficiency_gate-001` | ROCE |
| G8 | `entry_rsi-001`, `entry_adx-001` | RSI / ADX band |

**G2 (forensic veto) and G6 (valuation) are deliberately unoccupied.** No company
can be REJECTED by the engine today. That was an honest call at authoring time —
better no veto than a guessed one — but it means the screen is a growth-and-returns
filter wearing a SOIC label.

The remaining 10 entries are `observations:` — they print, they never gate.

The lectures behind those rules carry conditions, mechanisms, and disqualifiers
that do not survive translation into a scalar comparison. A threshold lifted out
of a lecture loses the sentence that said *when it applies*. This pass goes back
to the lectures whole and asks what was dropped.

The concrete deliverable is a challenge to the **current 38-name shortlist**
(`runs/out_v4/shariah-compliant-full-2026-08-22.md`, 26 CANDIDATE + 12 WATCH):
are these the right companies to research further?

This is algo *investing*, not algo trading. The unit of judgement is a business,
not a trade.

## Source of truth

**Stock Market Vault**, not `learning-vault-invest`.

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Stock Market Vault/
```

Readers read the `*-transcript.md` files, which carry inline `[HH:MM:SS]`
timestamps. They do **not** read the sibling AI-summary note — the portal's
summary is a lossy compression, and compressing a compression is the failure
mode this pass exists to undo. `learning-vault-invest` is likewise excluded:
its concept notes are a synthesised layer, one more step removed from what
was said.

Scope: 31 real lectures.

| Level | Vault dir | Lectures |
|---|---|---|
| L3 — value a company & portfolio creation | `level-3-how-to-value-a-company-portfolio-creation/` | 9 |
| L4 — when to hold, buy & sell using technicals | `l4-when-to-hold-buy-sell-using-technicals-for-long-term/` | 18 |
| L5 — how to screen & filter epic stocks | `level-5-how-to-screen-filter-epic-stocks/` | 4 |

Placeholder lessons (0-char, e.g. `quiz.md`, `links-to-best-talks-on-valuation.md`)
are excluded, consistent with `configs/course_eligibility.yaml`.

## Architecture

Three rounds, one per level, run in order L3 -> L4 -> L5. The user is in the
loop between rounds. Each round is six steps.

### 1. Fable delegates

One **Fable** agent per level, the *Level Lead*. Its context:

- the level's lecture list (paths + char counts)
- the current 16-entry rulebook
- the current 38-name shortlist with its gate columns
- the crux-brief format below

It fans out one **Sonnet** reader per lecture, in parallel.

**Fallback if agent nesting fails:** the main loop dispatches the Sonnet readers
directly, and Fable takes over at step 3 (consolidation + the adversarial
"what the ladder misses" pass). Same artifacts, one less layer. This is
determined on L3, not discovered at the end.

### 2. One Sonnet reader per lecture -> a crux brief

Each reader reads exactly one transcript end to end and emits:

```
LECTURE: <title>    REF: <mnemonic>

1. CRUX            one sentence: what this lecture is actually for
2. MECHANISM       3-6 bullets: how the thing works in the instructor's own logic
3. SIGNALS         every decision-relevant item, each tagged:
                     [HARD]  computable from data the ladder already fetches
                     [SOFT]  checkable, but needs data we do not fetch
                             (annual report text, concalls, promoter behaviour)
                     [JUDGE] genuinely human
                   every quote or number carries (REF HH:MM:SS)
4. WHAT THE LADDER MISSES
                   adversarial, and specific. One of:
                     - a rule we encoded that the lecture conditions or qualifies
                     - a central point the ladder has no rule for at all
                     - a threshold that is a dated one-company example, not a bar
5. NAMED COMPANIES every company named + why. He teaches by worked example;
                   the named set is direct evidence of what "good" looks like.
```

REF codes come from `soic_wiki.notebooklm_sector_pipeline.assign_ref_codes()`,
collision-checked corpus-wide. Reuse, do not re-derive.

### 3. Consolidate, then gate

Fable merges the level's briefs and dedups overlapping signals.

Every brief then passes `soic_wiki.gates.verify_cited_quotes()` against
`data/content.json` (28MB, present in the main repo checkout — the vault was
built from it, so the text is the same). **Hard bar: >= 80% of cited quotes
verbatim-present in the lesson their REF names.** Below bar -> that reader
re-runs once with tightened wording.

This gate is not ceremony. A subagent fabricating a plausible-sounding SOIC
rule has already happened in this repo: the first live framework-evolution
query invented a `"cash cow"` quote at a timestamp where the phrase never
appears, and only this same check caught it (71%, below bar). Swap the brain,
keep the judge.

**Citation format**, stated positively because showing the wrong pattern primes
reproduction of it: the REF code appears exactly once, immediately followed by
one or two `HH:MM:SS` values — `(PIPE 00:04:12)` or `(PIPE 00:04:12-00:05:30)`.

### 4. Present to the user, ELI5, lecture by lecture

Crux -> mechanism -> what the ladder misses. One lecture at a time. The user
decides which signals are real. Nothing is written to a rulebook or a challenge
sheet before that conversation.

### 5. Two outputs per level

**(a) Rule preview.** Accepted `[HARD]` signals are drafted as new or revised
rulebook entries in a *preview* YAML under `soic-ladder/rulebook/`, with full
`provenance.quote` / `ref` blocks in the existing schema. Aimed primarily at the
empty G2 and G6. **Never applied to the live rulebook without the user's
review** — same discipline as every framework diff in this repo.

**(b) Challenge sheet.** `[SOFT]` and `[JUDGE]` signals become a numbered list of
questions pointed at named companies:

> *Lecture X argues a business like this only compounds if `<condition>`.
> Of the 38, these N names need that checked.*

Committed to this repo under `docs/`. It accumulates across all three levels.

### 6. Final reassessment

After L5, walk all 38 names against the accumulated challenge sheet. This is
the answer to the original question.

## Artifacts and locations

| Artifact | Path | Committed? |
|---|---|---|
| Crux briefs | `out/reassess_l3/briefs/*.md` (and `_l4`, `_l5`) | no — `out/` is gitignored scratch |
| REF map | `out/reassess_l3/refs.json` | no |
| Gate report | `out/reassess_l3/gate_report.md` | no |
| Challenge sheet | `docs/SOIC-CHALLENGE-SHEET.md` | yes, accumulates |
| Rule preview | `soic-ladder/rulebook/preview-l3l5-rules.yaml` | yes, never auto-applied |

## Non-goals

- No change to the live rulebook in this pass. Previews only.
- No re-run of the ladder engine. The 38-name list is the fixed thing under test.
- No new capture from the SOIC portal. Everything needed is already in the vault.
- No investment advice. The output is a set of questions to research, not verdicts.

## Success criteria

1. All 31 lectures produce a brief that clears the 80% quote gate.
2. Every `[HARD]` signal is either drafted as a rule or explicitly rejected with
   a reason, so nothing is silently dropped.
3. G2 and G6 either gain a defensible rule or the spec records why they still
   cannot — an honest "no veto yet" restated with fresh evidence beats a guess.
4. Each of the 38 companies ends with at least one named, cited challenge, or a
   statement that the corpus raises none against it.

## Known costs and risks

- **~1M tokens of transcript reading.** 31 lectures averaging ~110k chars.
  Sonnet readers make this affordable; it is not free.
- **L4 skew.** 18 of 31 lectures are buy/sell timing, not company identification.
  Expect fewer selection signals there and more entry/exit ones. Still useful:
  G8 is the ladder's weakest gate (RSI + ADX only).
- **Verification proves provenance, never applicability.** A number quoted from a
  worked example verifies exactly as cleanly as a durable threshold. Separating
  the two is the user's judgement call in step 4, not the gate's job.
