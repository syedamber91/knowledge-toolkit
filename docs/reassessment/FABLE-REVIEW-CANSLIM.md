# Fable second review: `canslim_sales-001` / `canslim_pat-001` lost conditions

Independent skeptical re-review of `docs/reassessment/LOST-CONDITIONS-CANSLIM.md`
(the Sonnet-tier adjudication), against `out/lost_conditions_digest.json` and the
raw transcripts. Reviewed 2026-08-25.

**Bar applied here, which the prior pass did not apply:** every real condition
must end as either a gate fix or a new/expanded observation.
"Not structurally resolvable as a gate" is not a terminal verdict on its own —
the rulebook's own header already establishes the correct move
(`cash_conversion-001`: real condition, no resolvable attribute → keep the
information as an observation, drop the exclusion power).

## Verification method

Every one of the 5 cited quotes was checked verbatim against the raw
transcripts (not just against the digest):

| Ref | Transcript file | Quote found? |
|---|---|---|
| DSEFD 01:23:16 | `l4-when-to-hold.../different-strategies-to-enter-businesses-transcript.md` line 783 | Yes, verbatim |
| SGBT2 00:27:39 + 00:28:08 | `crash-course/tvgp.../281225-part-2-spotting-growth-businesses-transcript.md` lines 285–286 | Yes, verbatim |
| VACRA 02:01:53 | `level-3.../part-1-valuation-across-industries-transcript.md` lines 972–973 | Yes, verbatim (split across two timestamped lines, 02:01:53 + 02:02:00) |
| PALLOC 01:33:32 | `level-3.../portfolio-allocation-approach-transcript.md` line 920 | Yes, verbatim ("path growth" is the ASR rendering of "PAT growth") |

No fabricated or misattributed citation found in the digest. The prior pass's
*verdicts* are a different matter — see below.

## Structural correction to the review brief itself

The brief suggested `reference_band: "informational"` for observations with no
numeric band. **That would fail the rulebook to load.**
`soic-ladder/src/soic_ladder/rulebook.py:393` runs every observation's
`reference_band` through the same `_validate_grammar` probe as rule
`check_rule`s (`<=, >=, <, >, between A B`); an unparseable band raises
`RulebookError` at load. Every draft below therefore carries the corresponding
gate's own threshold as a **display anchor** — the precedent set explicitly by
`cash_conversion-001` (header comment: "`reference_band` stays `>= 60` as a
DISPLAY ANCHOR ... no longer a gate boundary of any kind"). A rule and an
observation on the same metric already coexist in this rulebook
(`capital_efficiency_gate-001` rule + `capital_efficiency-001` observation,
both on `roce`), so the anchor-band approach introduces no novelty.

Also confirmed: observation `metric` must be a registry key
(`rulebook.py:386`), and `gate`/`requires_attribute` are rejected if present —
all drafts below respect this.

---

## Citation 1 — DSEFD 01:23:16 ("sideways market, so can slim often fails")

**Prior verdict: NOT-STRUCTURALLY-RESOLVABLE. My verdict: AGREE on the gate
question, DISAGREE with stopping there → NEW OBSERVATION.**

Verified in context (transcript lines 770–800): the instructor is walking
CANSLIM's own "M" (market direction) leg — the one leg of CANSLIM these two
gates do not encode at all. He says explicitly that in a sideways market the
strategy often fails, you get chopped out of stocks, and he adjusts patience
and expectations to the index-level trend (uptrend 18–24 months, downtrend
12–18 months, judged over ~1 year of Nifty 500). The prior pass read the quote
correctly and was right that no `company`/`sector`/`is_lender` attribute can
express a market regime. But it then stopped, which is exactly the move the
`cash_conversion-001` history forbids: the condition is real, corpus-sourced,
and applies to the ladder's only two G0 exclusion gates. An observation can
say it plainly. Draft:

```yaml
  # Added <date>, from the Fable second review of the CANSLIM lost-condition
  # adjudication (docs/reassessment/FABLE-REVIEW-CANSLIM.md, knowledge-toolkit
  # repo). An OBSERVATION, not a gate narrowing, for the structural reason the
  # first-pass adjudication correctly identified: "is the market currently
  # sideways" is a property of the market at screening time, which no
  # RESOLVABLE_ATTRIBUTE_KEYS entry can express. But the condition itself is
  # real and sourced — it is CANSLIM's own "M" (market direction) leg, which
  # the two G0 gates do not encode — so per the cash_conversion-001 precedent
  # the information is kept while the exclusion power is not. reference_band
  # mirrors canslim_sales-001's bar as a DISPLAY ANCHOR only (same device as
  # cash_conversion-001); the caveat applies equally to the PAT leg.
  - id: canslim_market_direction-001
    metric: sales_growth_yoy_pct
    reference_band: ">= 15"
    display_text: "Quarterly sales growth, read against the same 15% CANSLIM bar as the G0 gate — with the market-direction caveat the gates cannot carry: SOIC states outright that the CANSLIM growth screen (this bar and the 20% PAT bar together) often fails in a sideways/range-bound market, where stocks get whipsawed out even when the growth numbers pass. A pass is most reliable when the index itself is trending; this ladder does not measure market direction, so read any CANSLIM pass against the current index-level trend (roughly a year of Nifty 500 is SOIC's own quick check) before weighting it."
    provenance:
      quote: "Today sideways market, so can slim often fails."
      ref: "DSEFD 01:23:16"
      corroborating_refs: ["DSEFD 01:23:21-01:23:30 (sideways direction -> chopped out of stocks; pay attention to market direction)", "DSEFD 01:24:39-01:24:47 (one year of Nifty 500 as the direction check)"]
      source: "docs/reassessment/FABLE-REVIEW-CANSLIM.md (knowledge-toolkit repo)"
```

Applies to both gates; one observation suffices (display_text names both legs).

---

## Citations 2+3 — SGBT2 00:27:39 / 00:28:08 (comparison window)

**Prior verdict: ALREADY-CORRECTLY-SCOPED. My verdict: AGREE with the
outcome, but the prior pass's rationale contains a factual misreading that
should not survive into the record.**

The prior doc claims: "The digest's own `scope_statement` for the second quote
... calls the YoY comparison correct for *both* the seasonal (hotel) and
non-seasonal (IT) case, i.e. this settles into one universal comparison rule."
That is wrong twice:

1. **The digest says the opposite.** Its second `scope_statement` ends:
   "confirming the comparison window is chosen based on the business's
   seasonality **rather than applied as one fixed rule**."
2. **The transcript says something different from both.** Lines 285–288: for
   seasonal industries (hotels, gold loans) compare same-quarter YoY; then at
   00:28:10 — *immediately after* the 00:28:08 quote — "IT services industry,
   there is not so much seasonality ... because it is a stable business we are
   looking at **QQ growth**." SOIC's actual practice is seasonality-routed:
   seasonal → YoY, stable/non-seasonal → QoQ is also read. The 00:28:08 "So
   now we will see year on year, right?" closes the *seasonal* (gold-loan)
   example; it is not a universal-rule declaration.

Why the outcome still stands: the gates' `_yoy_pct` metrics are the
seasonality-**safe** window — valid for seasonal and non-seasonal companies
alike (YoY is never the wrong comparison; it is at worst the conservative
one). The protective content of the lost condition (never let a seasonal
strong quarter vs. the prior quarter manufacture fake growth) is fully
embodied in the metric definition and the gates' own display_text ("year on
year"). The residual nuance — SOIC *additionally* reads QoQ for stable
businesses — is a permissive alternative window, not a caveat on how to read
the YoY number, and no QoQ growth metric exists in the registry to observe.
Against this review's bar: this is a legitimate "already covered by existing
text" resolution, because the encoded rule already states and implements the
condition's substance. **No observation proposed.** (If the owner wants the
QoQ nuance recorded anyway, the right home is a one-clause addition to both
gates' display_text — "year on year, the seasonality-safe window" — not a new
entry; I mark that optional, not recommended.)

---

## Citation 4 — VACRA 02:01:53 (AMC growth "steroids" in up markets)

**Prior verdict: NOT-STRUCTURALLY-RESOLVABLE. My verdict: AGREE that a
sector exclusion would overstate the source, DISAGREE with stopping there →
NEW OBSERVATION.**

Verified in context (lines 968–976): the mechanism is spelled out — mark-to-
market gains grow AUM, which grows fee income, sales, and profit together;
in a down market the same mechanism runs in reverse; and the instructor draws
the explicit practical conclusion at 02:02:14 that P/E reads break down on
these names ("low P ratio will not look high because earnings will come
down") and that the right response is caution / reduced allocation when the
market cycle peaks — while also affirming the 10–15 year structural tailwind.
The prior pass's reasoning for rejecting a `sector: asset_management`
exclusion is sound and I adopt it: the distortion is regime-dependent, so a
blanket exclusion asserts more than the source says. But that is precisely
the fact pattern an observation exists for — the same shape as
`price_to_book_deep_value-001` and `ev_to_ebitda_context-001`, both of which
carry context-conditional routing that `requires_attribute` cannot express.
Draft:

```yaml
  # Added <date>, from the Fable second review of the CANSLIM lost-condition
  # adjudication (docs/reassessment/FABLE-REVIEW-CANSLIM.md, knowledge-toolkit
  # repo). An OBSERVATION, not a sector-scoped gate exclusion, because the
  # source's distortion is regime-dependent (inflated in up markets, collapsed
  # in down markets), not a claim that growth metrics are structurally
  # meaningless for the sector — a requires_attribute exclusion would remove
  # AMCs from the CANSLIM gates unconditionally, overstating the source (the
  # same overreach the 2026-08-13 header history walked back). reference_band
  # mirrors canslim_pat-001's bar as a DISPLAY ANCHOR only; the quote names
  # profit growth, and the stated mechanism (MTM AUM -> fee income) distorts
  # the sales print identically.
  - id: amc_growth_cycle_distortion-001
    metric: pat_growth_yoy_pct
    reference_band: ">= 20"
    display_text: "Quarterly PAT growth, read against the same 20% CANSLIM bar — with a cycle caveat for AMC / wealth-management / capital-markets businesses: their reported sales and profit growth are amplified by mark-to-market gains on AUM, strongly inflated in an up market and equally deflated in a down market, so a CANSLIM growth pass (or fail) on these names says as much about where the equity cycle stands as about the business. SOIC's guidance is caution or reduced allocation when the market cycle peaks, not reading the growth print at face value — while still recognising the multi-decade structural tailwind. This is a reading instruction, not a sector exclusion: away from cycle extremes the numbers remain informative."
    provenance:
      quote: "in an up market these businesses work like steroids when it comes to profit growth. But in a down market the opposite happens."
      ref: "VACRA 02:01:53-02:02:00"
      corroborating_refs: ["VACRA 02:01:26-02:01:34 (mechanism: MTM gains grow AUM -> higher fees, higher sales growth)", "VACRA 02:02:14 (P/E unreadable on these names; be cautious / cut allocation when the market cycle peaks; 10-15 year tailwind intact)"]
      source: "docs/reassessment/FABLE-REVIEW-CANSLIM.md (knowledge-toolkit repo)"
```

Applies to both gates; anchored on the PAT metric because the verbatim quote
names profit growth, with the sales-side mechanism stated in display_text.

---

## Citation 5 — PALLOC 01:33:32 (capex ramp kills PAT, business strengthens)

**Prior verdict: CONTEXT-MISMATCH-FALSE-POSITIVE. My verdict: PARTIAL
DISAGREE → NEW OBSERVATION.**

Where I agree: no gate change. The passage is a portfolio-allocation Q&A
(core vs. satellite), not a screening-rule statement, and a G0 momentum gate
correctly failing such a company does not contradict SOIC separately liking
it on a longer horizon. The prior pass's point 2 (different tool, different
question) is correct.

Where the prior pass over-reached: it dismissed the citation as a
"single-company narrative" comparable to `embedded_growth-001`'s dated
one-company calibration. Verified in context (lines 914–926), the company is
*unnamed and hypothetical* ("Now there is a company which I find to be
interesting..."), the mechanism is stated in fully general terms (huge capex →
interest + depreciation suppress the P&L for 12–18 months while the business
itself strengthens), and the instructor generalizes it into an allocation
pattern (accumulate, apply a time stop-loss). It is a *taught scenario
pattern*, not a KEI-style dated number. And it is independently corroborated:
DSEFD 01:23:57, in a *different course*, applies the identical logic to a
wealth-management holding ("But I know that this year, there might not be a
pat growth in that company" → either trim, or sit through on a 3-year
horizon). Two independent lectures teaching the same caveat about the same
metric this gate reads is exactly what an observation should record — the
distinction between "this gate should not exclude such companies" (wrong, and
I do not propose it) and "a reader of this gate's FAIL should know SOIC's own
stated reason a FAIL can be misleading" (right). Draft:

```yaml
  # Added <date>, from the Fable second review of the CANSLIM lost-condition
  # adjudication (docs/reassessment/FABLE-REVIEW-CANSLIM.md, knowledge-toolkit
  # repo). An OBSERVATION, not a gate exception: the source teaches this in a
  # portfolio-allocation context (core vs satellite, time stop-loss), not as a
  # screening-rule exemption, and no is_mid_capex attribute exists in
  # RESOLVABLE_ATTRIBUTE_KEYS anyway. Kept because it is a generalized,
  # twice-independently-sourced caveat on reading exactly the metric
  # canslim_pat-001 gates on — not a one-company dated calibration (the
  # PALLOC company is unnamed and hypothetical, and DSEFD corroborates the
  # identical logic in a different course). provenance.quote is verbatim ASR:
  # "path growth" is the transcript's rendering of "PAT growth".
  # reference_band mirrors canslim_pat-001's bar as a DISPLAY ANCHOR only.
  - id: pat_capex_distortion-001
    metric: pat_growth_yoy_pct
    reference_band: ">= 20"
    display_text: "Quarterly PAT growth, read against the same 20% CANSLIM bar — with SOIC's own stated reason a FAIL can mislead: after a major capex programme, rising interest and depreciation can suppress reported PAT for roughly 12-18 months even while the underlying business is genuinely strengthening. A growth-screen FAIL during a known capex ramp is a momentum-screen result, not a verdict on business quality; SOIC's own stated handling of such names is to hold or accumulate on a multi-year horizon (with a time stop-loss) rather than discard them. This never changes the gate's verdict — it tells a reader why SOIC itself would sometimes still like a company that fails it."
    provenance:
      quote: "over next 18 months, the company will not see any path growth because interest, cost, depreciation will keep killing the profit and loss statement but even though business within itself will become stronger I like the long term prospects of the business"
      ref: "PALLOC 01:33:32"
      corroborating_refs: ["DSEFD 01:23:57 (independent, different course: a held wealth-management name expected to show no PAT growth this year — trim, or sit through on a ~3-year horizon)", "PALLOC 01:34:52-01:34:58 (keep increasing allocation; element of a time stop loss)"]
      source: "docs/reassessment/FABLE-REVIEW-CANSLIM.md (knowledge-toolkit repo)"
```

Applies to `canslim_pat-001` only, matching the digest.

---

## Summary vs. the prior pass

| Citation | Prior verdict | This review |
|---|---|---|
| DSEFD 01:23:16 | NOT-STRUCTURALLY-RESOLVABLE (terminal) | Agree no gate fix; **incomplete** — propose `canslim_market_direction-001` |
| SGBT2 00:27:39 + 00:28:08 | ALREADY-CORRECTLY-SCOPED | **Outcome affirmed, rationale corrected** — prior doc misstated both the digest's scope_statement and the transcript (SOIC reads QoQ for non-seasonal businesses; YoY is the safe window the gate rightly uses). No observation. |
| VACRA 02:01:53 | NOT-STRUCTURALLY-RESOLVABLE (terminal) | Agree no sector exclusion; **incomplete** — propose `amc_growth_cycle_distortion-001` |
| PALLOC 01:33:32 | CONTEXT-MISMATCH-FALSE-POSITIVE | **Partial disagree** — no gate change, but the "single-company" framing is wrong (unnamed hypothetical, generalized, independently corroborated by DSEFD 01:23:57); propose `pat_capex_distortion-001` |

Gate fixes proposed: **none** — I concur with the prior pass that neither
gate's `check_rule` or `requires_attribute` should change. New observations
proposed: **three** (drafts above). Also note for whoever applies these: the
review brief's `reference_band: "informational"` suggestion is not loadable
(`rulebook.py:393` grammar check) — the anchor-band device above is the
structurally valid equivalent.

**Not edited:** `soic-ladder/rulebook/soic-ladder-rules-v1.yaml` — proposals
only, per the review instruction.
