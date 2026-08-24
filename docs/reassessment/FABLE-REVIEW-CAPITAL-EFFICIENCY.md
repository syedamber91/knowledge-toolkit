# Fable second review: capital-efficiency gates (G3) lost conditions

Independent skeptical re-review of
`docs/reassessment/LOST-CONDITIONS-CAPITAL-EFFICIENCY.md` (Sonnet-tier
adjudication of `out/lost_conditions_digest.json` entries for
`capital_efficiency_gate-001` and `roe_lender-001`,
`soic-ladder/rulebook/soic-ladder-rules-v1.yaml`). Reviewed 2026-08-25.

**Bar applied here, which the prior pass did not apply:** every real
condition must end as a GATE fix or at least a new/expanded OBSERVATION.
"Not structurally resolvable as a gate" is a valid intermediate conclusion,
never a valid final one — the rulebook's own header (item 4,
`cash_conversion-001`) records exactly this move already: when the real
condition (`business_model` B2C/B2B) had no resolvable attribute, the fix
was *keep the information, drop the exclusion power* — not *discard the
finding*.

---

## Independent verification (everything re-checked, nothing trusted)

| Prior-pass claim | Re-checked how | Result |
|---|---|---|
| FESTF 00:42:09 quote verbatim, in-context | `crash-course/mastering-fundamental-analysis/151224-class-4-how-to-filter-epic-stocks-transcript.md` line 413 | **Confirmed.** Verbatim, sandwiched between the sales/PAT screen (line 412) and the market-cap line already used for `market_cap_floor-001` (line 414). |
| TFELT 00:42:09 is a duplicate recording, not independent | `level-5-.../tools-to-find-epic-stocks-transcript.md` lines 411–416 vs FESTF same lines | **Confirmed, and stronger than claimed:** the two transcripts are byte-identical at the same line numbers across the whole passage. Same relationship the rulebook already documents on `market_cap_floor-001`'s corroborating_refs. |
| RSSER 01:36:57 quote verbatim | `291224-class-5-research-a-stock-from-scratch-transcript.md` line 726 | **Confirmed** verbatim ("...so it comes that is the ROC and ROE above 15% ... if not above 15% can it go above 15%..."). |
| RSSER restates the gate's own MASTED provenance ("same idea, different REF code, one second apart") | Resolved the (REF, timestamp) pair per the reassessment's own gotcha discipline: checked what Class 4 says at 01:36:54 vs Class 5 | **Confirmed — and the prior pass UNDERSOLD it.** MASTED 01:36:54-01:36:57 and RSSER 01:36:57 are the **same lesson, same moment**. Class 4 (FESTF's lesson) at 01:36:54–56 discusses *relative strength*, not ROC/ROE; Class 5 at 01:36:54 ("First focus is on profitability") → 01:36:57 (the ROC/ROE-15% sentence) is exactly the passage F26 line 336 paraphrases as "ROC/ROE above 15% or trending toward it". MASTED (frameworks-file code) and RSSER (crash refs.json code) are two REF codes for `291224-class-5-research-a-stock-from-scratch`. So Citation 3 is not merely "the same idea" — it is *literally the gate's own provenance sentence*, re-detected under a second code. **Consequence: RSSER must never be added anywhere as a corroborating ref for this rule — it would be self-corroboration.** |
| The 2026-08-21 triage briefing knowingly deferred the trend reading | Read `soic-ladder/docs/superpowers/specs/2026-08-21-g3-roce-triage-briefing.md` in full (note: it lives in the **soic-ladder** repo, not knowledge-toolkit as the review task stated) | **Confirmed.** §1.2 point 1 ("A point-in-time gate does not implement 'sustained'"), §1.5 (multi-year `ROCE %` already parsed and frozen; `roce_3y_avg`/`roce_min_3y` is "small code, no new network calls"), §1.7 point 2 poses point-in-time-vs-derivation as an explicit human decision. The shipped `>= 15` rule is the record of that decision. |

One schema fact the review-task brief got wrong, worth recording:
`reference_band: "informational"` is **not valid**. The loader
(`soic-ladder/src/soic_ladder/rulebook.py:393`) runs every observation's
`reference_band` through `_validate_grammar`, the same `>= N / <= N / < N /
> N / between A B` grammar as `check_rule`. An observation must carry a real
band; the established idiom for "context, not verdict" is a band used as a
**display anchor** with prompt-style `display_text`
(`growth_trap_flag-001`, `cash_conversion-001` post-demotion). The draft
below follows that idiom. (Same lesson as the reassessment's standing
gotcha: read the loader, not just the YAML.)

---

## Citation 1+2 — FESTF/TFELT 00:42:09, the turnaround waiver

**The seed finding of this entire reassessment thread.**

Prior pass: verified real, then stopped at NOT-STRUCTURALLY-RESOLVABLE
(no `is_turnaround` in `RESOLVABLE_ATTRIBUTE_KEYS = {company, sector,
is_lender}`).

**My verdict: the structural analysis is correct, the stopping point is
not.** The gate-scoping half is genuinely blocked — "inflecting from a
turnaround" is a lifecycle state, not a static attribute, and none of the
three keys can carry it without lying. But the condition is real, verbatim,
stated by the source about *this exact criterion* ("ROC criteria can be
removed"), and today the rulebook is **silent** about it everywhere: not in
`capital_efficiency_gate-001`'s display_text, not in any observation. A
reader watching a turnaround-inflection name land WATCH on a G3 FAIL gets
no hint that SOIC's own material prescribes waiving that criterion. That is
precisely the information-loss `cash_conversion-001`'s demotion was
designed to prevent.

L3's synthesis (M6, `docs/reassessment/level-3/SYNTHESIS.md`) independently
documents the cost: the point-in-time gate demotes exactly the
under-earning recovery names the lectures favour (CARTRADE, JUBLINGREA)
while passing peak-economics names the lectures warn about.

### Proposed new observation (full YAML, propose-only — not applied)

To be appended under `observations:` in
`soic-ladder/rulebook/soic-ladder-rules-v1.yaml`:

```yaml
  # Added 2026-08-25 per the reassessment's gate-level lost-condition
  # second review (docs/reassessment/FABLE-REVIEW-CAPITAL-EFFICIENCY.md,
  # knowledge-toolkit repo). Same "keep the information, drop the
  # exclusion power" move as cash_conversion-001 (file header, item 4):
  # the source states the ROC>=15 screening criterion "can be removed ...
  # where the company is inflecting from the turnaround" (FESTF 00:42:09,
  # verbatim-verified), but no is_turnaround / lifecycle-stage key exists
  # in RESOLVABLE_ATTRIBUTE_KEYS, so the waiver cannot be encoded as
  # requires_attribute scoping. The reference_band is a DISPLAY ANCHOR
  # mirroring capital_efficiency_gate-001's bar (the loader's grammar
  # check forbids a bandless "informational" entry): within-band
  # (roce < 15) means the company currently fails G3 and this context is
  # live. It never changes any verdict — observations structurally
  # cannot. TFELT 00:42:09 is a duplicate recording of the same class
  # (byte-identical passage; same relationship already documented on
  # market_cap_floor-001's corroborating_refs), NOT independent
  # corroboration — and RSSER/MASTED 01:36:57 is the gate's own
  # provenance moment, so it is deliberately NOT cited here either.
  - id: turnaround_context-001
    metric: roce
    reference_band: "< 15"
    display_text: "Turnaround-inflection context for the ROCE gate: SOIC states outright that the ROC-above-15% screening criterion 'can be removed' for a company inflecting out of a turnaround — trailing capital efficiency is depressed by the turnaround itself and does not reflect the business's normalized quality. Within this band means the company currently fails capital_efficiency_gate-001 (G3 → WATCH); before discarding such a name, check for inflection evidence the source's framing implies (losses shrinking, margins recovering, ROCE rising off a trough). No resolvable is_turnaround attribute exists, so this stays context: it never waives the gate mechanically — it tells the reader when a manual waiver is what the source itself prescribes. Stated for the ROC screen, i.e. non-lenders; no equivalent turnaround waiver is stated anywhere in the corpus for the lender ROE-14 bar (roe_lender-001), and a lender's low ROCE is a denominator artifact (deposits in capital employed), not a turnaround signal — read this observation as not meaningful for banks/NBFCs."
    provenance:
      quote: "And ROC of more than 15%, ROC criteria can be removed from some people where the company is inflecting from the turnaround"
      ref: "FESTF 00:42:09"
      corroborating_refs: ["TFELT 00:42:09 (duplicate recording of FESTF, not an independent second source)"]
      source: "docs/reassessment/FABLE-REVIEW-CAPITAL-EFFICIENCY.md (knowledge-toolkit repo)"
```

Schema-checked against the actual loader: all five required observation
keys present; no forbidden `gate`/`requires_attribute`; `roce` is in
`metric-registry.yaml` (`status: fetchable`, 466/470 live rows per the
triage briefing); `"< 15"` passes the grammar; `provenance` is a free
mapping, so `corroborating_refs`/`source` are fine (same shape
`roe_lender-001` and `market_cap_floor-001` already use).

**Secondary (optional) proposal:** append one sentence to
`capital_efficiency_gate-001`'s display_text — "SOIC itself waives this
criterion for a company inflecting out of a turnaround; see
turnaround_context-001" — so the waiver is visible at the gate that
enforces the bar, not only in the observations section. Cosmetic if the
observation lands; listed separately so the owner can take one without the
other.

**The long-term fix the prior pass named** (a real `is_turnaround` /
`lifecycle_stage` resolvable attribute, or a trough-then-recovery derived
signal) remains the correct eventual gate-level answer and remains out of
scope. The observation above is not a substitute for it; it is the floor
this rulebook's own history says the finding must not fall below.

## Citation 3 — RSSER 01:36:57, "trending toward 15%"

**My verdict: no new entry warranted — because the bar this review
enforces is ALREADY met, not because the condition isn't gate-shaped.**
Justified against "keep the information," not against "can it be a gate":

1. **The information is already kept, at observation level.** The existing
   `capital_efficiency-001` observation's display_text states both bars
   *and* the softening verbatim: "...ROC/ROE above 15% 'or trending toward
   it' in the fundamentals checklist... This is a POINT-IN-TIME figure,
   not the multi-year 'sustained' reading the source describes." The
   `cash_conversion-001` move already happened here, on 2026-08-21. The
   prior pass never mentioned this entry — it is the strongest single
   reason its NOT-STRUCTURALLY-RESOLVABLE verdict happens to land in an
   acceptable place for this citation.
2. **It is not a fresh miss.** Confirmed independently (see table): the
   citation resolves to the *same lecture moment* as the gate's own MASTED
   provenance, and the triage briefing shows the trend/point-in-time
   tension was explicitly weighed, with the `roce_3y_avg`-style derived
   metric scoped as buildable and deliberately deferred.
3. **Adding it anywhere as corroboration would be self-corroboration**
   (MASTED = RSSER, proven above), the exact double-counting trap the
   rulebook already guards against on `market_cap_floor-001`'s
   FESTF/TFELT note.

What WOULD close it fully is the deferred derived metric
(`roce_3y_avg`/`roce_min_3y` from Screener's already-frozen multi-year
Ratios rows) plus either a trend-aware check grammar or a
delta-observation like `capital_structure_trend-001`. That is a small
feature in the soic-ladder repo, already scoped in the 2026-08-21 briefing
§1.5 — a deliberate backlog item with a named owner decision behind it,
which is a categorically different thing from a discarded finding.

---

## Summary

| Citation | Prior-pass verdict | This review's verdict |
|---|---|---|
| FESTF 00:42:09 (turnaround waiver) | NOT-STRUCTURALLY-RESOLVABLE, stop | Real + verified; **propose new observation `turnaround_context-001`** (YAML above) + optional gate display_text pointer. Gate-scoping fix still blocked on a missing attribute, as the prior pass correctly found. |
| TFELT 00:42:09 | duplicate of FESTF | Confirmed byte-identical duplicate; cite only as annotated corroborating_ref, never as independent evidence. |
| RSSER 01:36:57 | NOT-STRUCTURALLY-RESOLVABLE (metric-layer gap) | Condition **already preserved** in `capital_efficiency-001`'s display_text (which the prior pass missed), and the citation is the gate's own provenance moment under a second REF code (which the prior pass under-stated as "same idea"). No new entry; real remaining fix is the already-scoped `roce_3y_avg` derivation in soic-ladder. |

No rulebook file was modified by this review.
