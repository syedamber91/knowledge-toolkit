# SOIC Machine-Actionable Decision Engine — Plan (DRAFT)

> **Status: DRAFT ONLY.** This document is a design/plan artifact, not an
> implementation task list ready to execute. No F21-F24 framework entries,
> YAML schemas, or code changes described below have been written yet.
> Produced by a Fable-model planning pass (two rounds) grounded in the
> actual current repo/vault content — see "Sources read" at the end.

**Goal:** evolve the existing SOIC persona-investment-desk system (today: a
human-readable briefing assembler) into something that can produce a
structured, fully-cited, defensible stock recommendation — verdict +
conviction + rule trail — usable as the reasoning layer for an autonomous
agent, while keeping capital-affecting action strictly human-gated.

---

## 0. Scope framing — what "an AI agent making investment decisions" means here

**Hard constraint, stated up front:** this system will **never execute
trades, move money, or act as a licensed advisor**. The end state is an
agent that produces a **structured, fully-cited, defensible
recommendation** — `verdict ∈ {BUY, HOLD, SELL, AVOID, INSUFFICIENT_DATA}`
+ conviction + the exact rule trail (which framework rules fired, on which
live values, from which source, as-of when) — **for a human to review and
act on**. The automation target is the *reasoning and evidence assembly*,
not the capital action. Every output artifact carries a standing header:
"Research output, not advice; no order was or will be placed." This
mirrors the deliberate design already in `decision_engine.py`'s docstring
("Deliberately does NOT write the verdict") — the verdict moves *into* the
machine, but the human sign-off moves to the *action* boundary instead,
and stays there permanently.

---

## 1. `decision-frameworks-v1.md` → v2: a two-layer schema (the core of the plan)

**Keep the markdown; add a machine layer beside it.** The prose (`Model:`,
`Grounding:` with verbatim citations) is the auditable "why" and must
stay. But `framework_router.py`'s parser only extracts `id/title/body` and
matches by substring; nothing today can *evaluate* a framework. Proposal:
a companion **`frameworks/decision-rules-v2.yaml`**, one entry per
F-number, generated initially by hand for a pilot subset, with the
markdown remaining the source of truth for narrative and the YAML the
source of truth for executable rules. A consistency check (Phase A gate)
asserts every YAML entry's `id` exists in the markdown and vice-versa
(frameworks may be marked `machine: false`).

**Per-framework YAML schema:**

```yaml
- id: F10
  status: machine          # machine | advisory-only | deprecated
  applies_when:
    sectors: [any]
    requires: [pe, eps_growth_3y]
  signals:
    - name: growth_above_embedded
      metric: profit_growth_3y_pct
      source: screener.top_ratios
      rule: ">= 20"
      weight: 0.6
    - name: pe_within_band
      metric: stock_pe
      rule: "between 15 35"
      weight: 0.4
  verdict_map:
    bullish: ">= 0.7"
    neutral: "0.3..0.7"
    bearish: "< 0.3"
  abstain_if:
    - missing: profit_growth_3y_pct
  human_only_questions:
    - "Is margin guidance credible vs a scaled peer?"
  calibration_expiry: 2027-07-01
```

**Key design decisions:**

- **Not every framework can be mechanized — say so explicitly.** F11
  (freshness meta-rule) becomes engine behavior, not a rule entry. F17
  (spot-premiumization checklist), F5 (cycle position), F18
  (sitting-duck) are judgment-heavy: mark them `advisory-only` — context
  the human must weigh, never a scored vote. Where SOIC gave a number
  (20-25% growth, 15-35x P/E, 75% LTV), encode it with its `Grounding:`
  citation; where it didn't ("margins healthy"), the field stays
  `human_only` until a threshold is *derived and documented*, never
  silently invented.
- **Canonical metric registry** (`frameworks/metric-registry.yaml`): maps
  metric keys → exact `screener.top_ratios` labels, plus for non-top-ratio
  metrics (WC days, GNPA, segment mix) names the source and a
  `staleness_max`. Makes explicit which rules are evaluable *today* vs.
  blocked on a fetch extension.
- **Weights across frameworks:** each framework gets a `class`
  (`safety_gate | valuation | quality | timing`). Safety gates (e.g. a
  lending-quality gate) are **vetoes**, not weighted votes — a failed gate
  caps the verdict at AVOID regardless of other scores. Valuation/quality/
  timing combine by declared weights, tunable per sector overlay (§3).
- **Conviction convention:** conviction = f(coverage, agreement). HIGH
  requires coverage ≥ 0.8 AND no contradicting machine vote; any live
  contradiction caps at LOW and is listed verbatim. `INSUFFICIENT_DATA` is
  a first-class verdict when coverage < 0.5 — never a padded guess.

## 2. `decision_engine.py`: add `evaluate()` beside `build_briefing()`, don't replace it

Current signature stays untouched — it's the evidence assembler. Add:

- **`evaluate(briefing, rules_path, registry_path) -> Decision`** —
  resolves each matched framework's YAML rules against
  `briefing.live_ratios`, records per-signal outcomes `(metric, value,
  source, as_of, rule, pass/fail/abstain)`, applies veto gates then
  weighted combination, emits a `Decision` dataclass: `verdict,
  conviction, per_framework_votes, rule_trail, contradictions,
  unresolved_human_questions, data_coverage, as_of`.
- **Determinism boundary:** `evaluate()` is deterministic and LLM-free.
  Advisory frameworks and open human questions surface as *open items*;
  an LLM may draft narrative around them but can never change `verdict`
  or the rule trail. Build a `decision_consistency(decision,
  narrative_text)` tripwire from day one — don't retrofit it after prose
  has already contradicted the numbers once.
- **Conflict handling:** conflicting machine votes are *reported, not
  averaged away* — named, with values, capping conviction.
- **Failure semantics:** refuse (verdict `INSUFFICIENT_DATA`) whenever a
  data error is set — never score against nothing.

## 3. `sector_router.py`: from read-only context to parameter overlays

Each sector entry may carry an **overlay block**: sector-specific bands
(hotels on EV/EBITDA through-cycle; lenders on P/B not P/E; gold NBFC LTV
cap), framework inclusions/exclusions, and class-weight adjustments.
`evaluate()` merges overlay-over-default before scoring, and the rule
trail records which overlay applied — the "growing the YAML is the only
wiring needed" invariant stays intact. Overlays go through the same
human-approved diff flow as frameworks.

## 4. `framework_evolution.py`: structural auto-validation + regression gate, content approval stays human

- **Structural validator:** a proposal intended as `machine` must include
  a draft YAML entry; auto-validate schema completeness, that every
  metric exists in the registry, thresholds have citations, and citations
  verify. Structural failure → auto-rejected before a human reads it.
  Content/judgment approval stays human.
- **Regression gate:** maintain `tests/decision-fixtures/` — frozen
  `(briefing snapshot, expected Decision)` pairs. Any change to
  frameworks/rules/overlays re-runs `evaluate()` against all fixtures; any
  changed verdict must be listed in the human-review diff ("this edit
  flips KEI from HOLD to BUY"). Catches silent cross-stock verdict flips
  deterministically, for free.

## 5. Persona/wiki concept notes: minimal frontmatter, no rewrite

Add three cheap fields, incrementally: `grounds: [F3, F4]` (reverse
index), `asr_risk: true` (refuse to source a *numeric* threshold from an
ASR-risky quote — mechanisms yes, numbers no), `lecture_date:` (queryable
for freshness enforcement). Concept notes ground rules; they never become
direct decision inputs themselves.

## 6. Risks to engineer against

1. **Fabricated/garbled grounding** — never let an LLM-proposed number
   into a rule without citation verification + `asr_risk` check.
2. **Threshold rot** — every threshold carries `calibration_expiry`;
   expired ones downgrade to advisory automatically.
3. **Screener fragility** — must fail loudly on incomplete data, with
   per-metric as-of timestamps in the Decision.
4. **Keyword-routing misses** — substring matching both misses and
   false-positives; routing recall should be a measured Phase A metric,
   not assumed.
5. **False precision** — a 0.63 score looks more authoritative than the
   prose it summarizes; always render the rule trail and open human
   questions *above* the verdict.

## 7. Phased rollout (gated, smallest-scope-first)

- **Phase A — Schema + pilot rules.** See §8 for the revised pilot set.
  Done when every threshold has a citation and a human agrees with every
  cell of a manual dry-run table.
- **Phase B — `evaluate()` + fixtures.** Freeze Phase A stocks as
  regression fixtures. Done when a deliberately-broken rule edit is
  caught by the regression gate.
- **Phase C — Sector overlays + panel expansion.** ~6-8 frameworks, ~10
  stocks. Done when ≥80% of signals are evaluable, zero narrative/number
  contradictions, and human disagreement ≤2/10 (each explained by an
  advisory-only factor, not a bug).
- **Phase D — Evolution hardening.** Wire validation + regression gate
  into `evolve-frameworks`. Done when one full sector-evolution cycle
  lands through the new gates with a flip-list reviewed.
- **Phase E — Steady state.** Scheduled runs producing dated,
  human-reviewed Decision artifacts. **Explicitly out of scope forever:**
  order placement, position sizing tied to a live account, or any
  unattended write to the frameworks file.

---

## 8. Phase A delta — after reading the new L2-L5 method-course concept notes

The original Phase A pilot (F10/F13/F12) was picked from what existed in
`decision-frameworks-v1.md` before this session — built mostly from Level
6 sector modules. This session also synced ~98 new concept notes from four
method courses (Level 5 screening, L4 technicals, Level 3 valuation, Level
2 intensive/fundamentals) into the same vault directory. A second Fable
pass read the relevant files in full and found materially better pilot
candidates.

### 8.1 Revised pilot rules

**Keep F10** (growth threshold + P/E band — still the best-cited
valuation rule). **Drop F13 and F12 from the pilot** — F13 has no stated
numeric gap threshold, and F12's lending gate unnecessarily narrows the
pilot stock universe. Replace with four rules the new corpus states as
actual numbers:

**(a) Cash-conversion gate** — `cash-flow-reconciliation-and-working-capital-dynamics.md`
states CFO/EBITDA "should ideally be around 70% for consumer-facing B2C
businesses and 60% for B2B businesses" (MODULB 01:58:04-01:58:28). A
safety-gate veto; excluded for banks/NBFCs per the note's own caveat that
CFO metrics are "redundant and void" for lenders (MODULB 01:54:03).

```yaml
- id: F21-cash-conversion   # new F-number needed, see §8.2
  status: machine
  class: safety_gate
  applies_when: { excludes_sectors: [banks, nbfc] }
  signals:
    - name: cfo_ebitda_conversion
      metric: cfo_to_ebitda_pct_3y
      source: screener.cash_flow + screener.pnl   # derived, not top-ratios
      rule: ">= 60"          # B2B floor; sector overlay raises to 70 for B2C
      cite: "MODULB 01:58:04-01:58:28"
  abstain_if: [ missing: cfo_to_ebitda_pct_3y ]
```

**(b) Receivables red-flag veto** — `revenue-manipulation-and-recognition.md`:
a spike in trade receivables "delayed by more than 180 days" (MODULA
00:15:05-00:15:47) as a channel-stuffing signal, with the note's own
B2B/B2G exemptions encoded as `applies_when` context. Machine signal:
receivable-days trend rising while CFO/EBITDA falls (both from the same
note). A forensic veto layer, same shape as F12 but for any non-lender.

**(c) DuPont quality gate** — `return-on-equity-roe-and-dupont-analysis.md`:
ROE decomposed into margin x asset-turnover x leverage; "ROE driven
primarily by debt" is the stated failure mode (MODULE 00:19:37-00:20:25,
Tata Motors example). Machine rule: leverage component's share of ROE
above a documented ceiling → downgrade quality vote; the cyclicality
caveat (CEAT example) means the rule must `abstain` for sectors flagged
cyclical in the overlay. SOIC states the *direction*, not a number, so
this ships `advisory-numeric` until a threshold is derived and dated.

**(d) System-exit / Stage-4 gate — the single most fully-parameterized
rule set in the whole corpus.** `system-based-exits-and-time-stop-losses.md`
+ `stan-weinstein-s-stage-analysis-framework.md`: exit when **all
three** fire — price below the 30-weekly EMA, Relative Strength (26/52-
week, vs Nifty 50/500) negative, and V-stop (ATR length 10, multiplier
2-2.5) negative (FRAMEC 01:46:39-01:47:01); time-stop of 4-8 quarters
(FRAMEC 01:30:22-01:30:56); Stage-2 entry screen ADX crossing 20 + weekly
RSI crossing 50 (HOWB 00:01:55-00:02:23); tighten to 10-weekly EMA when
price extends >70% above the 30-weekly (FRAMEC 02:01:03-02:02:51). These
are `machine` by construction — but they need **weekly price-series data
the screener top-ratios grid doesn't carry**, so Phase A must add a price-
history fetch to the metric registry (the single biggest scope change
from this delta). The note's own caveat becomes schema: applies to
"satellite" positions, not core holdings, and false-signals in choppy
markets — encode as a conviction cap, not a hard SELL.

**Explicitly NOT pilot material despite looking numeric:**
`intrinsic-compounding-and-incremental-returns-roic-roiic.md` (ROIIC x
reinvestment-rate = intrinsic compounding rate) is a real formula but its
caveats (QIP distortion, maintenance capex, backward-integration hits)
make it Phase C `machine` at best; `sector-specific-valuation-metrics.md`'s
IHCL EV/EBITDA of 42 is a **dated calibration example, not a threshold**
(and the same note carries flagged ASR garbling — "float statement",
"more depression" — plus the sheet author's own "no recommendation here"
disclaimer, which should be quoted in the safety framing in §0);
`capital-light-compounders.md` and `distinct-sources-of-economic-moats.md`
are mechanism taxonomies with no evaluable rule — `advisory-only`.

**Revised pilot:** rules = F10 + (a)(b)(c)(d); stocks = KEI + one B2C
consumer name (to exercise the 70% vs 60% overlay split) — the gold NBFC
drops out with F12.

### 8.2 New framework candidates (no F-number exists today)

| Candidate | Source note(s) | Type |
|---|---|---|
| Cash-conversion / forensic red-flag veto layer (CFO/EBITDA bands, >180d receivables, traded-goods mix dilution, one-offs-in-revenue) | `cash-flow-reconciliation…`, `revenue-manipulation-and-recognition`, Module-4 siblings | **machine** (veto class) |
| DuPont ROE-quality decomposition gate | `return-on-equity-roe-and-dupont-analysis` | machine (direction) / advisory (threshold) |
| Weinstein Stage-Analysis timing gate (entry + exit + time-stop) | `stan-weinstein-s-stage-analysis-framework`, `system-based-exits-and-time-stop-losses`, `technical-entry-patterns-and-canslim` | **machine** — the most parameterized rules SOIC states anywhere |
| Sector-metric selection meta-rule (which valuation metric is even valid: P/B for banks, EV/EBITDA asset-heavy, EV/ton cement, mcap/pre-sales real estate) | `sector-specific-valuation-metrics` | machine as a *routing* rule — slots directly into the §3 overlay design |
| Intrinsic-compounding rate (ROIIC x reinvestment) | `intrinsic-compounding-…-roic-roiic` | machine-later (Phase C), advisory in Phase A |
| Moat taxonomy / capital-light classification | `distinct-sources-of-economic-moats`, `capital-light-compounders` | advisory-only |

### 8.3 Net changes to Phase A (only Phase A — Phases B-E unchanged)

1. Pilot rule set becomes F10 + four new-corpus rules above; F12/F13
   deferred.
2. Phase A must draft **F21-F24 entries in `decision-frameworks-v1.md`
   first** (via the existing human-approved evolution flow) — the YAML
   schema requires every rule to anchor to an F-entry, and these
   mechanisms currently have none.
3. Metric registry gains two fetch extensions: derived cash-flow ratios,
   and weekly price history (30w-EMA/RS/ATR) — flagged "required for
   pilot," not deferred.
4. Sector overlays arrive *earlier* than originally planned (the 70/60
   CFO split and the metric-selection meta-rule both need them), pulled
   forward from Phase C in minimal form.
5. "Done" gate unchanged, plus one addition: every threshold in the
   pilot YAML must carry a verbatim citation from these notes — all four
   new rules already can.

---

## Sources read (both Fable planning passes)

**Round 1 (original plan, §0-7):**
- `wiki/personas/soic/frameworks/decision-frameworks-v1.md` (vault)
- `src/soic_senses/decision_engine.py`, `framework_router.py`,
  `sector_router.py`, `screener_client.py` (SOIC_Scraper)
- `src/soic_wiki/framework_evolution.py` (SOIC_Scraper)
- `configs/sector_notebooks.yaml` (SOIC_Scraper)

**Round 2 (§8 delta):**
- `wiki/personas/soic/index.yaml` (vault) — to resolve topic->file
  mappings for the four newly-synced method courses
- ~98 concept notes under `wiki/personas/soic/concepts/*.md` tagged with
  topics `how-to-screen-and-filter-epic-stocks`,
  `technical-analysis-masterclass`, `additional-classes`,
  `framework-for-buying-selling-a-stock`,
  `how-to-value-a-company-and-portfolio-creation`,
  `how-to-navigate-and-take-best-out-of-soic-membership`,
  `module-1-the-need-for-compounding` through
  `module-8-all-about-competitive-advantages`,
  `updated-soic-screener-sheet` — full text read for the notes named
  explicitly in §8.1/§8.2
