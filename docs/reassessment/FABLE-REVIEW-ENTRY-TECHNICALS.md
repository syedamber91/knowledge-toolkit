# Fable second review: entry_rsi-001 / entry_adx-001 (G8)

Independent, skeptical re-verification of
`docs/reassessment/LOST-CONDITIONS-ENTRY-TECHNICALS.md` (the Sonnet-tier
adjudication of `out/lost_conditions_digest.json`'s `entry_rsi-001` and
`entry_adx-001` entries), reviewed 2026-08-25. Bar applied, per the review
brief: **every real underlying condition must end as a gate fix or at least an
observation** — "not structurally resolvable" alone is not a terminal verdict
(the rulebook's own `cash_conversion-001` history is the precedent: keep the
information, drop the exclusion power).

**This review proposes; it does not edit `soic-ladder-rules-v1.yaml`.**

## What was independently verified

- **All 13 digest quotes checked verbatim against raw transcripts** at their
  exact timestamps, resolving each (REF, timestamp) pair through
  `docs/reassessment/l4/refs.json` (CSLRC, FSSDF, FSSMF, ESRLE, MAAIM, TVPD2)
  and the level-3 refs for PALLOC (path resolved manually to
  `level-3-how-to-value-a-company-portfolio-creation/.../portfolio-allocation-approach-transcript.md`,
  line 861). **All 13 quotes are genuine and correctly timestamped.** The
  digest fabricated nothing.
- **`report.py::final_verdict` read directly** (soic-ladder
  `src/soic_ladder/report.py:82`): any gate FAIL → WATCH, any ABSTAIN →
  INSUFFICIENT, forensic-gate FAIL → REJECTED. The prior doc's structural
  claim is accurate.
- **The metric registry and `judge.py` read directly** — this is where the
  prior pass goes wrong (below).

## Overall verdict: AGREE on 8 of 13 citations, DISAGREE on 5

The prior pass's quote verification and its exit-vs-entry sorting are largely
sound. It has two substantive defects:

### Defect 1 — a stale-premise error: V-Stop IS fetchable now

The prior pass rejected TVPD2 01:10:30 and MAAIM 00:22:33 (both "entry needs
V-Stop positive too") as NOT-STRUCTURALLY-RESOLVABLE on the grounds that
anything derived from `weekly_price_series` is `not_yet_fetchable` and would
poison `final_verdict` with contagious ABSTAIN. That was true when the
rulebook header was written; it is **no longer true**:

- `rulebook/vendor/metric-registry.yaml` lines 79–127: as of **2026-08-14**,
  `weekly_rsi`/`weekly_adx` are computed locally from a frozen Yahoo weekly
  OHLCV series, and `weekly_volatility_stop` (Price vs V-Stop, ATR10 x 2.5, %)
  is `status: fetchable`.
- `src/soic_ladder/judge.py` already ships code-authored F23 **exit**
  observations (`exit_vstop-001`, band `>= 0`) that read
  `weekly_volatility_stop` today. The snapshot pipeline already fetches it
  for every company.

So the "identical wall already documented in the header" the prior doc leaned
on has already been torn down by the F23 exit-signal build. An entry-side
V-Stop rule costs zero new fetch work. See Proposal P1.

### Defect 2 — FSSMF 01:53:46 is not a pure sell-side false positive

The full transcript sentence (l4 `framework-on-how-to-sell-stocks-transcript.md`
line 1212) contains, alongside the sell-into-overbought critique the prior
pass saw, two entry-side clauses it missed: the instructor says the useful
reading is "when RSI crosses **45**" via the readymade stock scans, and calls
RSI a "worst indicator" **"for buying selling"** — buying included. The 45 is
not a stray number:

- CSLRC 00:09:53 / 00:10:02 / 00:11:37 / 00:14:13 / 00:15:14 — the LTI-tool
  lecture states the RSI buy signal is **45**, repeatedly ("the bi-signal is
  always 45"; "First is RSI crossing 45").
- ESRLE 01:27:16 / 01:27:31 / 01:49:39 — entry triggers on RSI 45 cross +
  V-Stop positive; "I will leave it at 45."
- Versus **50** in TVPD2 00:35:18/00:35:49, FSSDF 00:25:47/00:26:39, and HOWB
  (the gate's own provenance).

`docs/reassessment/l4/SYNTHESIS.md` (line 28) already names this 45-vs-50
contest and notes the ladder "silently picked one source";
`DECISION-REVIEW.md` D10 sets the policy: a contested deployed threshold
**stays at its current value, flagged contested in output**. No flag exists in
the rulebook today. An observation is exactly that flag. See Proposal P2.

## Per-citation adjudication

| Citation | Prior verdict | This review | Disposition |
|---|---|---|---|
| CSLRC 00:12:07 (validate on L3) | ALREADY-CORRECTLY-SCOPED | **AGREE** | `final_verdict` verified: G8-only pass cannot reach CANDIDATE. Condition already structurally enforced — bar satisfied, no observation needed. |
| PALLOC 01:28:23 (choppy market) | NOT-STRUCTURALLY-RESOLVABLE, stop | **AGREE not gateable, DISAGREE with stopping** | Context verified (lines 858–866): it is explicitly about *averaging up using technicals* — entry-side, real, regime-conditional. Fold into P2/P3 display_text. |
| TVPD2 01:10:30 (V-Stop entry precondition) | NOT-STRUCTURALLY-RESOLVABLE | **DISAGREE — stale premise** | `weekly_volatility_stop` is fetchable and already consumed by `exit_vstop-001`. → P1. |
| FSSDF 00:29:08 (overbought ≠ sell) | CONTEXT-MISMATCH-FALSE-POSITIVE | **AGREE, stronger grounds** | Pure exit-side. The condition is already *honored*, not just irrelevant: no RSI exit rule exists anywhere, and the F23 exit observations use EMA-break/RS/V-Stop — matching TVPD2 00:32:13's "V-Stop is the selling sign" teaching. Nothing lost. |
| FSSMF 01:53:46 | CONTEXT-MISMATCH-FALSE-POSITIVE | **DISAGREE (partial)** | Contains entry-side content: RSI-crossing-45 scan + "for buying selling" dismissal. Feeds P2. |
| TVPD2 01:15:25 (high RSI ≠ exit) | CONTEXT-MISMATCH-FALSE-POSITIVE | **AGREE** | Same grounds as FSSDF 00:29:08. |
| CSLRC 00:12:24 (ADX optional) | NOT-STRUCTURALLY-RESOLVABLE, stop | **AGREE not gateable, DISAGREE with stopping** | The source treats a signal the gate hard-fails on as *discretionary*. Cash-conversion precedent applies squarely. → P3. |
| CSLRC 00:14:14 (confirmation only) | NOT-STRUCTURALLY-RESOLVABLE, stop | **same** | → P3. |
| ESRLE 01:49:29 (experiment 0/20/45) | NOT-STRUCTURALLY-RESOLVABLE, stop | **same** | → P3. |
| MAAIM 00:26:26 (weekly for cyclicals) | NOT-STRUCTURALLY-RESOLVABLE | **AGREE, with one salvage** | Verified: a timeframe preference that the rule already satisfies (it reads weekly). Not a lost condition — but worth one clause in P3 as affirmative support for the weekly reading. |
| MAAIM 00:22:33 (ADX useless without V-Stop) | NOT-STRUCTURALLY-RESOLVABLE | **DISAGREE — stale premise** | Same fix as TVPD2 01:10:30. → P1 (corroborating). |
| MAAIM 00:12:50 (buy indicator, not sell) | ALREADY-CORRECTLY-SCOPED | **AGREE** | Verified verbatim at line 152. Confirms entry-only placement. |
| TVPD2 00:32:09 (ADX ≠ selling sign) | CONTEXT-MISMATCH-FALSE-POSITIVE | **AGREE** | Exit-side; and the very next line (00:32:13) endorses V-Stop as the sell signal — which `exit_vstop-001` already implements. |

## Proposals (draft YAML — for the owner's triage, not applied)

### P1 — NEW GATE `entry_vstop-001` (G8): the missing third leg of the entry trigger

Multiple independent lectures state entry requires V-Stop positive *in the
same breath* as the RSI/ADX conditions the rulebook already gates on
(TVPD2 01:10:30; ESRLE 01:27:31; MAAIM 00:22:33; CSLRC 00:07:45's LTI
walkthrough). The metric is fetchable, already fetched per company, and
already read by the exit-side observation. Encoding two of the three stated
entry legs as hard gates while silently dropping the third is an arbitrary
partial encoding — the strongest genuine gap in this citation set.

```yaml
  # PROPOSED by docs/reassessment/FABLE-REVIEW-ENTRY-TECHNICALS.md
  # (knowledge-toolkit repo, 2026-08-25). Third leg of the F23/LTI entry
  # trigger: the same lectures that give the RSI and ADX entry bars state,
  # repeatedly, that entry triggers only once price is above the weekly
  # volatility stop. The 2026-08-14 F23 exit-signal build made
  # weekly_volatility_stop fetchable (judge.py's exit_vstop-001 already
  # reads it), so the header's original weekly_price_series exclusion no
  # longer applies to this metric.
  - id: entry_vstop-001
    gate: G8
    metric: weekly_volatility_stop
    check_rule: ">= 0"
    requires_attribute: {}
    display_text: "Price at or above the weekly volatility stop (V-Stop positive)"
    provenance:
      quote: "Entry gets triggered when your V stop is positive."
      ref: "TVPD2 01:10:30"
      corroborating_refs: ["ESRLE 01:27:16-01:27:31 (entry = RSI 45 cross + V-Stop positive)", "MAAIM 00:22:33 (ADX inconclusive for a buy unless combined with the volatility stop)", "TVPD2 00:32:09-00:32:13 (V-Stop, not ADX, carries the sell side -- its positive state is the entry-side complement)"]
      slug: f23-weekly-vstop-entry
      source_row: 300
```

Fallback if the owner declines a new hard gate (this rulebook is authored by
human triage, and a new gate tightens the screen): the identical entry as an
observation — drop `gate`/`check_rule`/`requires_attribute`, add
`reference_band: ">= 0"`, and prepend to `display_text` that the source
states this as a required entry condition the gates do not currently
enforce. Either lands the finding; silence does not.

### P2 — NEW OBSERVATION `entry_rsi_context-001`: the contested 45/50 cutoff, flagged in output

Implements DECISION-REVIEW D10's standing policy ("stays at its current
value, **flagged contested in output**") for the one gate it names as already
contested. Band deliberately `>= 45` — the looser source-taught bar — so the
report visibly identifies exactly the names excluded by the gate's 50 while
inside the course's other stated cutoff.

```yaml
  # PROPOSED by docs/reassessment/FABLE-REVIEW-ENTRY-TECHNICALS.md
  # (knowledge-toolkit repo, 2026-08-25). Flags entry_rsi-001's contested
  # threshold per DECISION-REVIEW D10: the gate keeps its 50 bar; this
  # observation surfaces the course's OTHER stated entry bar (45) so a
  # reader can see when a name is excluded on a number the source itself
  # does not agree on. Reference band is the looser 45 on purpose.
  - id: entry_rsi_context-001
    metric: weekly_rsi
    reference_band: ">= 45"
    display_text: "Weekly RSI read against the looser 45 entry cutoff -- the course states two different entry bars for this one signal: the screening recipe behind the gate above uses 50, while the LTI-tool and ranking-sheet lectures repeatedly set the buy signal at 45. A name failing the 50 gate while inside this 45 band is excluded on a threshold the source itself is split on. Two further caveats from the same corpus: in a choppy or sideways market the instructor de-weights weekly technicals entirely in favour of the business thesis, and RSI standalone (outside the crossing-scan setup, combined with relative strength) is dismissed as a poor buy/sell indicator."
    provenance:
      quote: "in RSI, the bi-signal is always 45, right?"
      ref: "CSLRC 00:09:53"
      corroborating_refs: ["CSLRC 00:11:37 (RSI crossing 45 is the first LTI condition)", "ESRLE 01:27:16-01:27:31 (entry = RSI 45 cross + V-Stop)", "ESRLE 01:49:39 (leaves the setting at 45)", "FSSMF 01:53:46 (scans read RSI crossing 45; RSI standalone called a poor buy/sell indicator)", "TVPD2 00:35:18 + FSSDF 00:26:39 (the 50-side statements -- the contest is real on both sides)", "PALLOC 01:28:23 (choppy-market de-weighting of technicals)"]
      source: "docs/reassessment/FABLE-REVIEW-ENTRY-TECHNICALS.md (knowledge-toolkit repo)"
```

### P3 — NEW OBSERVATION `entry_adx_context-001`: source-stated discretion on a hard-failed signal

Five independent statements across three lectures frame ADX as optional,
confirmation-only, or freely re-parameterised (0/20/45); the gate hard-fails
companies on the strictest available reading. Cash-conversion precedent:
keep the information, record the discretion, leave the gate's power to the
owner's D10 policy.

```yaml
  # PROPOSED by docs/reassessment/FABLE-REVIEW-ENTRY-TECHNICALS.md
  # (knowledge-toolkit repo, 2026-08-25). Records, next to entry_adx-001's
  # hard 20 bar, that the source repeatedly frames ADX as a discretionary
  # confirmation signal rather than a required trigger. The gate keeps its
  # bar (D10 policy); this observation keeps the reader honest about how
  # strict that encoding is relative to the teaching.
  - id: entry_adx_context-001
    metric: weekly_adx
    reference_band: ">= 20"
    display_text: "Weekly ADX against the 20 entry bar, with the source's own discretion recorded: the LTI-tool lectures present ADX as usable or ignorable outright, as a confirmation signal rather than an independent trigger when kept, and 20 as one adjustable setting among 0/20/45. The instructor endorses ADX for buy-side reads only, warns it is inconclusive without the volatility stop alongside, prefers the weekly timeframe for cyclical businesses (cycles of roughly 6-9 months -- which this reading already uses), and de-weights all weekly technicals in a choppy or sideways market. A name failing this gate alone is excluded on the strictest available reading of a signal the course itself treats as discretionary."
    provenance:
      quote: "you can use ADX 20 or you can choose to ignore it as well"
      ref: "CSLRC 00:12:24"
      corroborating_refs: ["CSLRC 00:14:14 (confirmation only)", "CSLRC 00:10:02 (use it or choose not to)", "ESRLE 01:49:29 (experiment with 0/45/20)", "ESRLE 01:27:16 (practitioners drop ADX, trade RSI 45 + V-Stop)", "MAAIM 00:22:33 (inconclusive without the volatility stop)", "MAAIM 00:26:26 (weekly timeframe preferred for cyclicals)", "MAAIM 00:12:50 (buy indicator only, never a sell indicator)", "PALLOC 01:28:23 (choppy-market de-weighting)"]
      source: "docs/reassessment/FABLE-REVIEW-ENTRY-TECHNICALS.md (knowledge-toolkit repo)"
```

## Citations correctly ending in no change, justified against the bar

- **CSLRC 00:12:07** — the condition (technicals must be validated against
  fundamentals) is *already enforced by construction*: `final_verdict`
  demotes any company failing any fundamentals gate to WATCH regardless of
  G8. A condition the engine already enforces needs no observation.
- **FSSDF 00:29:08, TVPD2 01:15:25, TVPD2 00:32:09** — exit-side statements
  about signals the rulebook deliberately does *not* use for exits. The
  conditions are already honored by design: no RSI/ADX exit rule exists, and
  the F23 exit observations (`exit_ema_break-001` / `exit_rs_nifty-001` /
  `exit_vstop-001` in judge.py) implement exactly the alternative the
  instructor prescribes in the adjacent lines (V-Stop as the sell signal).
  Nothing was lost, so nothing needs surfacing.
- **MAAIM 00:12:50** — affirmative confirmation of the entry-only placement;
  recorded in P3's corroborating refs rather than discarded.
- **MAAIM 00:26:26** — a timeframe preference the rule already satisfies;
  salvaged as one clause of P3's display_text rather than dropped.

## Note on loadability

All three proposals use bands/check-rules already proven in this rulebook
(`>= 0` is used by the code-authored exit observations; `>= 45`/`>= 20` are
plain grammar). Both proposed observations attach to registry metrics the
snapshot already fetches, so they can never introduce ABSTAIN contagion; the
proposed gate reads a metric already fetched for the exit observations. Per
the rulebook's provenance rule, no verbatim course text appears in any
proposed `display_text` — quotes live only in `provenance`.
