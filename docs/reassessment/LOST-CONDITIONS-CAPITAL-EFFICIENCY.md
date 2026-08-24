# Lost-conditions adjudication: capital-efficiency gates (G3)

Adjudicates the mechanical lost-condition detector's findings for
`capital_efficiency_gate-001` (ROCE ≥15%, non-lenders) and `roe_lender-001`
(ROE ≥14%, lenders) in
`soic-ladder/rulebook/soic-ladder-rules-v1.yaml`. Source: `out/lost_conditions_digest.json`
entries for both rule IDs. `roe_lender-001` was added TODAY (2026-08-25) to
close a gap `capital_efficiency_gate-001` left for lenders — see its
in-file comment (lines 148–171) and
`docs/reassessment/COVERAGE-GAP-JUDGMENT.md#roe`.

**Rulebook context confirmed before judging:** `RESOLVABLE_ATTRIBUTE_KEYS =
frozenset({"company", "sector", "is_lender"})`
(`soic-ladder/src/soic_ladder/resolvable_attributes.py:19`) — the *only*
things `requires_attribute` can ever gate on. Anything a citation asks for
that isn't a static company/sector/lender-status fact cannot be encoded as
a `requires_attribute` scope today, no matter how real or well-cited it is.

There are **3 distinct citations** across the two rules (one, RSSER
01:36:57, is shared by both). Each is adjudicated once below.

---

## Citation 1 — FESTF 00:42:09 (turnaround waiver)

> "And ROC of more than 15%, ROC criteria can be removed from some people
> where the company is inflecting from the turnaround."
> — FESTF 00:42:09, *15.12.24 Class 4 How to Filter Epic Stocks*

**Verified against the raw transcript** (`151224-class-4-how-to-filter-epic-stocks-transcript.md`,
line 413): quote is verbatim and in-context — it comes immediately after the
instructor states the sales/PAT growth screen and the 15% ROC bar, in the
same breath as the market-cap line already used as provenance for
`market_cap_floor-001`. Not a mismatch, not fabricated.

**Verdict: NOT-STRUCTURALLY-RESOLVABLE.**

This is the same finding this whole reassessment thread started from, and
it survived: the citation is still present in the digest, still real, still
squarely about the ROCE 15% bar this exact gate enforces. But "a company
inflecting from a turnaround" is not a fact about `company` (an identity
key), `sector` (an industry classification), or `is_lender` (a boolean
lender flag) — it is a *lifecycle/trajectory state* that changes over time
for the same company and has no representation in the current attribute
system at all. There is no `is_turnaround` key, and none of the three
existing keys can be repurposed to mean it without lying about what they
represent.

**What a real fix would need:** a new resolvable attribute, e.g.
`is_turnaround: bool` (or a richer `lifecycle_stage` enum), sourced from
something the engine can actually determine — e.g., a multi-year earnings/ROCE
trough-then-recovery pattern, or a human-curated override list. Building
and populating that attribute is out of scope here; it is a real, named gap
in what `RESOLVABLE_ATTRIBUTE_KEYS` can express, not a defect in this
gate's YAML.

---

## Citation 2 — TFELT 00:42:09 (turnaround waiver, duplicate recording)

> "And ROC of more than 15%, ROC criteria can be removed from some people
> where the company is inflecting from the turnaround."
> — TFELT 00:42:09, *Tools To Find Epic Stocks*

**Same wording, same timestamp (00:42:09) as Citation 1.** This matches the
pattern already documented for `market_cap_floor-001`'s corroborating_refs
in the rulebook itself, where TFELT 00:42:15 is explicitly noted as "a
duplicate recording of FESTF, not an independent third source" for the
adjacent market-cap line one sentence later. TFELT 00:42:09 here is the same
duplicate-recording relationship for the ROC/turnaround sentence.

**Verdict: NOT-STRUCTURALLY-RESOLVABLE** — same reasoning as Citation 1.
Not treated as independent corroboration (it is the identical sentence from
a duplicate recording of the same class), but its presence confirms
Citation 1 was transcribed and detected consistently rather than as a
one-off artifact. Same fix path: a new `is_turnaround`-style attribute,
out of scope here.

---

## Citation 3 — RSSER 01:36:57 (trending toward the bar)

> "In profitability, we have discussed ROC and ROE at least one hour, so it
> comes that is the ROC and ROE above 15% so I have taken a mark of 15% and
> if not above 15% can it go above 15%..."
> — RSSER 01:36:57, *29.12.24 Class 5 Research a Stock from Scratch*

Appears in the digest for **both** `capital_efficiency_gate-001` and
`roe_lender-001`, since both gates share the same underlying "≥ bar, or
trending toward it" source idea (ROC for non-lenders, ROE for lenders).

**Verified against the raw transcript** (`291224-class-5-research-a-stock-from-scratch-transcript.md`,
line 726): quote is verbatim and directly on-topic — explicitly ROC/ROE
against the 15% mark, not a different metric coinciding on a number.

**Important context found while adjudicating, not visible from the digest
alone:** `capital_efficiency_gate-001`'s own `provenance.quote` is "ROC/ROE
above 15% or trending toward it" (MASTED 01:36:54-01:36:57) — the rule's
*own* cited source already contains this "trending toward it" softening,
under a different REF code but the same idea, one second apart in
timestamp. This was not a fresh miss: `docs/superpowers/specs/2026-08-21-g3-roce-triage-briefing.md`
(§1.2 point 1, §1.7 point 2) shows the human triage session that authored
this gate on 2026-08-21 explicitly identified "sustained ROCE... trending
toward it" as a real tension against a hard `>=` gate, considered building
a multi-year `roce_3y_avg`/`roce_min_3y` derived metric from Screener's
Ratios statement (already parsed, zero new network calls — §1.5), and
**knowingly chose to ship "the honest-but-partial point-in-time rule"
instead**, deferring the trend derivation as "a small feature," not an
oversight. RSSER 01:36:57 is independent corroboration that the same idea
recurs across lectures, but it does not surface a new condition the
authoring session was unaware of.

**Verdict: NOT-STRUCTURALLY-RESOLVABLE** — but for a different structural
reason than Citations 1/2. This is not a `RESOLVABLE_ATTRIBUTE_KEYS` gap at
all: "trending toward the bar" is not a static company/sector/lender-status
fact you'd scope a rule *by* — it's a request for the **metric itself** to
be redefined as a multi-year trend rather than a single point-in-time value
(and/or for `check_rule`'s grammar to accept something richer than
`>= N` / `<= N` / `< N` / `> N` / `between A B`,
`soic_ladder/decision_rules.py` per the triage briefing). No new
`requires_attribute` key fixes this; what would actually be needed is a new
**derived metric** (e.g. `roce_3y_avg`, `roe_3y_avg`) sourced from
Screener's multi-year Ratios statement, which the 2026-08-21 briefing
already scoped as buildable but deliberately deferred. That is the same
"real gap, different layer of the system" finding as Citations 1/2, just
located in the metric/derivation layer instead of the attribute layer.

---

## Summary table

| Citation (ref + ts) | Bucket | One-line reason |
|---|---|---|
| FESTF 00:42:09 | NOT-STRUCTURALLY-RESOLVABLE | Real, verified turnaround-waiver quote on the ROC 15% bar; "turnaround" isn't `company`/`sector`/`is_lender` — needs a new `is_turnaround`-style attribute that doesn't exist yet. |
| TFELT 00:42:09 | NOT-STRUCTURALLY-RESOLVABLE | Duplicate recording of FESTF 00:42:09 (same pattern already noted for `market_cap_floor-001`'s TFELT corroboration); same reasoning, not independent evidence. |
| RSSER 01:36:57 (cited by both gates) | NOT-STRUCTURALLY-RESOLVABLE | Real, verified "trending toward 15%" quote, corroborating the gate's own MASTED provenance; the human 2026-08-21 triage session already knew this and deliberately shipped point-in-time only — the real gap is a missing multi-year `roce_3y_avg`/`roe_3y_avg` derived metric + richer `check_rule` grammar, not an attribute-resolution gap at all. |

**Buckets used: 0 GENUINE-NARROWING-NEEDED, 3 NOT-STRUCTURALLY-RESOLVABLE, 0
CONTEXT-MISMATCH-FALSE-POSITIVE, 0 ALREADY-CORRECTLY-SCOPED.**

No exact-YAML change is proposed for any of the three citations — forcing
one into GENUINE-NARROWING-NEEDED would mean inventing an attribute
(`is_turnaround`) or a metric (`roce_3y_avg`) that does not exist in this
codebase today, which is exactly the "seem thorough" trap this adjudication
was told to avoid.

**The turnaround-waiver finding (the one this reassessment thread started
from): confirmed still present, confirmed still real (verbatim-verified
against the raw transcript, in-context, twice across a duplicate
recording), and lands in NOT-STRUCTURALLY-RESOLVABLE.** It names a genuine,
still-open gap in what this rulebook's attribute system can express — no
`is_turnaround` (or equivalent lifecycle-stage) key exists in
`RESOLVABLE_ATTRIBUTE_KEYS`, so no `requires_attribute` scoping can encode
the waiver today, however clearly SOIC's own source material states it.
