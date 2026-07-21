# SOIC Method Extraction — Pilot Report

**Date:** 2026-07-21
**Plan:** `docs/superpowers/plans/2026-07-20-soic-method-extraction.md`
**Spec:** `docs/superpowers/specs/2026-07-20-soic-method-spec-design.md`
**Branch:** `claude/soic-method-extraction`
**Bundle:** `out/pilot-bundle/` (gitignored — regenerate with `scripts/pilot_run.py`)

**Verdict: CONDITIONAL GO** — with one scope change that the pilot itself
argues for. See *Go/no-go* at the end.

---

## What was run

The full pipeline, end to end, against the real corpus:

```
route → extract → verify (Gate 1) → corroborate (Gate 1b)
      → refute (Gate 2) → reconcile (Gate 3) → publish
```

**Pilot slice** (per the plan's revised scoping): Level 5's 4 lessons **plus**
the Level 6 `Identifying Scalable Businesses` module (Parts 1, 2, Q&A) — 7
lessons, ~529k chars. Course-title scoping was abandoned in the design phase
after the existing SOIC wiki showed screening content tracing to Level 6, not
Level 5. **The pilot confirms that call was right**: the L6 module produced the
cross-lesson corroboration that Level 5 alone could not.

**Router output:** 24 candidate spans across the 7 lessons.

---

## Who played the LLM roles

**The extractor and refuter were played by the operating agent (Claude),
reading real spans and recording judgments in `scripts/pilot_run.py`**, rather
than by a wired API client. This was an explicit, human-approved choice: no LLM
client exists anywhere in the codebase (every task was built against an
injected fake `llm` callable, per the plan's own "no LLM call inside a test"
constraint), and wiring one was out of scope for a 24-span pilot.

**This is the single biggest caveat on the results below** and it is called out
again where it distorts a specific number. Every judgment is traceable to a
real span in the real corpus; nothing was invented. But an agent that can see
the whole span while choosing what to extract is not equivalent to a
cold-called production LLM.

---

## Results against the six falsifiable criteria

| # | Criterion | Pass condition | Result |
|---|---|---|---|
| 1 | Ear-verification | n=10, digit-bearing oversampled, verbatim courses only, **zero** failures | ⚠️ **Deferred to human** — see below |
| 2 | Rejection rate | Reported **and** within 5–40% | ⚠️ **15.4% overall, but 0% at Gate 1** — see below |
| 3 | Gate 3 exercised | ≥1 conflict reaches `conflicts.open.yaml` | ✅ **PASS — and with a *real* conflict, not the synthetic seed** |
| 4 | Attribution | Zero rules from ineligible courses **or modules** | ✅ **PASS** |
| 5 | Bindings | Bound/unbound split reported; `gaps.md` non-empty | ✅ **PASS** — 0 bound / 4 unbound |
| 6 | Acceptance | Human recognizes the method | ⚠️ **Deferred to human** (by design — it is a human test) |

### Funnel

```
extracted            13
Gate 1 verified      13   (rejected 0)
Gate 2 survived      11   (refuted 2)
Gate 3 active         4
Gate 3 conflicts      1
```

### Rules extracted

| rule_key | value | corroboration | status |
|---|---|---|---|
| `screen.sales_growth.floor` | ≥ 15% | 3 | **active** |
| `screen.pat_growth.floor` | ≥ 20% | 3 | **active** |
| `screen.roc.floor` | ≥ 15% | 1 | needs_audio_check |
| `screen.market_cap.floor` | ≥ 1000 cr | 1 | needs_audio_check |
| `screen.pe.ceiling` | **15–30 vs 40–50** | — | **CONFLICT** |

All 4 non-conflicted rules ship `binding.status: unbound` — nothing was
asserted as `bound`, per the global constraint.

---

## Criterion 3 — the headline result

**A genuine conflict surfaced without needing the synthetic seed.** P/E is
stated two different ways in two different lessons:

- `"pe ratio is between 15 to 30"` — lesson 3586296 @ **00:34:15**
- `"p should be less than 50 times i can do less than 40"` — lesson 4150532 @ **01:18:01**

Neither carries a scope attestation, so Gate 3 correctly refused to launder
them into "scoped variants" and routed both to `conflicts.open.yaml` for human
adjudication. This is exactly the behaviour the conflict-by-default inversion
was designed to produce, validated on real data rather than a fixture.

It also independently confirms the design spec's own worked example: the spec
cited *"P/E less than 50 or 40 times"* as the archetypal ambiguity a scalar
threshold cannot represent — and that exact phrasing turned up verbatim in the
corpus.

**The synthetic seed (plan Step 2) was therefore not needed and not used.** A
real conflict is strictly better evidence that Gate 3 works.

---

## Criterion 2 — why 0% at Gate 1 is a caveat, not a triumph

Overall rejection across the funnel is **2/13 = 15.4%**, inside the 5–40% band.
But the composition matters, and the honest reading is unflattering:

- **Gate 1 rejected 0.** Not because Gate 1 is weak — it survived six rounds of
  adversarial review — but because **the extractor was an agent that had
  already read the span and only proposed rules it could see were literally
  supported.** A production LLM extractor will fail Gate 1 far more often. This
  number says almost nothing about Gate 1's real-world rejection rate.
- **Gate 2 rejected 2**, both correctly and for the two distinct reasons the
  refuter exists for:
  - *Reported speech* — Usha Martin management's own raised EBITDA-margin
    guidance (`"management has raised its minimum ebitda margin benchmark 20%"`),
    which reads exactly like a SOIC threshold and is not one.
  - *ASR incoherence* — `"if you get 3000% margin, if you get 500% then roc will
    explode"`, garbled past the point of supporting any rule.

**Criterion 2 should be re-measured once a real LLM extractor is wired.** The
current figure is not a valid baseline.

---

## Criterion 1 — the spot-check you need to run

Ear-verification is a human acceptance test and cannot be self-certified by the
agent that did the extraction. What *was* verified mechanically: **every
citation, when sliced from the real corpus by its recorded offsets, contains
text genuinely stating its rule.** Nothing cites a span that doesn't support it.

The three highest-value spot-checks, all in `verbatim`-fidelity courses:

| Rule | Lesson | Timestamp | Expect to hear |
|---|---|---|---|
| sales ≥15% / PAT ≥20% / ROC ≥15% | 3586296 *Tools To Find Epic Stocks* | **00:23:47** | the three-part screen stated together |
| same screen restated | 3586296 | **00:41:57** | *"...roc criteria can be removed... where the company is inflecting from the turnaround"* |
| P/E conflict, side B | 4150532 *Part 2 Scalable Businesses* | **01:18:01** | *"p should be less than 50 times i can do less than 40"* |

If any of these does not match the audio, the offset→timestamp resolution is
wrong and every citation in the bundle is suspect.

---

## Criterion 4 — attribution, and a real find

Zero rules came from ineligible courses or modules. More importantly, **Step 1's
classification of all 40 Level-6 modules found a third guest-led module that the
`-by-<person>` naming convention misses**: *"Unseen Trends in Bio-Technology"*
(11 lessons) is presented by external investor Sajal Kapoor
(`"today we have with us Mr. Sajjal Kapoor"` [ASR sp.]).

Without module-level eligibility, 11 lessons of an independent third party's
methodology would have been extracted and attributed to SOIC — carrying fully
valid citations, and invisible to every downstream gate, because the gates check
whether a rule is *supported by its source*, never whether the source is
*SOIC's own voice*. Eligible lessons: 365 → **354**.

Two scan false-positives were documented and kept eligible (*Spotting
Turnarounds*, *Fluorine Industry* both open with a host introducing Ishmohit),
and one borderline call is recorded inline in the config for auditability
(*Oil & Gas Sector Simplified* is taught by SOIC team members Neel and Shuchi —
kept eligible as SOIC's own institutional voice, since the guest exclusion
exists to keep a *third party's* independent methodology out).

---

## Criterion 5 — the data-gap list

**0 bound / 4 unbound.** `gaps.md` lists all four. To execute even this minimal
screen, `stock_analyzer` needs fields for: quarterly sales growth, quarterly PAT
growth, ROC/ROCE, and market cap. Per the spec's open items, the column
inventory is still unverified, so nothing was asserted as `bound`.

Note the platform is already known to be blocked on market cap
(`market_cap_updater` fails against NSE), so at least one of these four gaps is
a known-open problem rather than a new discovery.

---

## Vocabulary bootstrap (plan Step 3)

Run as designed. The first pass was key-free; the four metric clusters that
emerged (`sales_growth`, `pat_growth`, `roc`, `market_cap`, plus `pe`) were
named and became `rule_key`s. Because the pilot slice is small and the clusters
were unambiguous, the bootstrap converged in one pass rather than needing the
full cluster→name→re-run loop. **`configs/rule_keys.yaml` was therefore not
committed as a separate artifact** — the vocabulary is currently implicit in
the extraction. This is a real deviation from the plan and should be made
explicit before any full-corpus run, where the cluster set will be much larger
and much less obvious.

---

## Token spend

Not separately metered — the extractor/refuter roles ran inside the operating
agent's own session rather than as discrete billed API calls, so there is no
per-call figure to report. A production run with a wired client would need this
instrumented before full-corpus extraction is costed.

---

## Go/no-go

**CONDITIONAL GO**, with one scope change the pilot argues for directly.

**What the pilot proved:**
- The pipeline works end to end on real data and produces a real, publishable
  bundle with clickable citations.
- Gate 3's conflict-by-default design catches a genuine contradiction — the
  single most important thing this architecture exists to do.
- Module-level eligibility caught a guest module the naming heuristic missed.
  This alone justified the design.
- Corroboration separated single-lesson from multi-lesson rules: the two rules
  stated in only one lesson sat at `needs_audio_check` rather than `active`.

  > **Correction (added after the final whole-branch review).** An earlier
  > version of this report claimed corroboration *"meaningfully discriminates."*
  > That claim was **not supported** and is withdrawn. The final review measured
  > Gate 1b against the real corpus and found it near-random at scale: because
  > `_attested_in` scanned an entire ~100KB transcript for a bare number,
  > **41 of 100 arbitrary values reached `active`** — 52–56 of the integers
  > 1–100 appear *somewhere* in any given pilot lesson. The two rules landed at
  > `needs_audio_check` for being single-lesson, not because the gate
  > discriminated on content. Task 6's 60-char fixtures hid this entirely.
  >
  > **Fixed** in `4fe01f9`: an attesting occurrence must now fall within a
  > bounded window that also contains a relevant metric term (reusing
  > `router.SIGNAL_TERMS`). Re-measured **41/100 → 1/100**, while the pilot's
  > real corroboration counts were **unchanged at 3/3/1/1** — the tightening
  > removed coincidence, not evidence.
  >
  > Residual, recorded openly: ~9% mean false-positive rate across rule keys,
  > concentrated in two 17% buckets (`screen.market_cap.floor` and unnamed
  > rules) — exactly the keys naming no metric the vocabulary knows, so only the
  > window bound is working. Narrowing to ±100 barely moved them, confirming the
  > cause is the vocabulary gap, not window width.

**What it did not prove, and should not be claimed:**
- **Gate 1's real rejection rate** — 0% is an artifact of who played the
  extractor.
- **That a large `rules.yaml` is extractable.** 7 lessons and 24 candidate spans
  yielded **4 active rules and 1 conflict**. Extrapolated naïvely across 354
  eligible lessons that's optimistic-sounding, but the pilot slice was chosen
  *because* it is the most rule-dense material in the corpus. The rest of the
  corpus is sector applications, not method — the yield curve is very unlikely
  to be linear.

**The scope change the pilot argues for:** the spec's own contingency —
*"the real deliverable is a small knockout set plus well-cited rubrics"* — looks
more likely than a large executable rules file. Every rule found is a
**graded/preference** threshold; the pilot produced **zero knockouts**, and the
most decision-relevant thing it surfaced was not a threshold at all but a
*disagreement* requiring human judgment. That is evidence for the two-tier
design and against expecting scale from tier 2.

**Recommended next step — not full-corpus extraction.** Instead: wire a real
LLM extractor, re-run this same 7-lesson slice, and re-measure criterion 2
against a genuine baseline. Full-corpus extraction should be gated on that
number, not on this one.
