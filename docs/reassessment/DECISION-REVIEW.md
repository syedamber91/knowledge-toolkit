# Adversarial review of D1-D12 (+D7b)

Reviewed against the owner's stated target: a weekly loop that outputs companies to
research. Evidence checked on disk: `docs/reassessment/*/refs.json`, the soic-ladder
rulebook (`rulebook/soic-ladder-rules-v1.yaml`), and `runs/out_v4/` outputs.

## 0. The finding that breaks the design as scoped

**Phase 1 cannot audit the rulebook. Verified, not argued.** Every one of the
rulebook's 15 provenance refs (`MASTEA`, `MASTEC`, `MASTED`, `FLUORA`, `HOWB`,
`INSIGN`, `MODULB`, `SOICA6`, `SOICC`, `TVGPF`, plus one `ref: null`) points into the
**decision-frameworks-v1.md / L6 REF space**. I intersected them against all four
`docs/reassessment/*/refs.json` files: **the intersection is empty**. Not one rulebook
citation resolves inside the 58-lecture corpus D8 admits.

So D1 declares the graph's job is "is its citation real?", and D8 defers the only
corpus in which that question can be answered. Phase 1 as scoped produces a graph of
58 lectures that cannot verify a single citation of its audit target. The
`rule -encodes-> claim` edges (D5) can then only be built by semantic matching of
rule text to *similar* claims from a different corpus — which is exactly how you get
manufactured provenance: the corpus visibly contains both "ROCE >= 15 or trending
toward it" (the gate's source) and "sustained ROCE above 20%" (the screening bar,
quoted in the ladder's own observation text). A fuzzy match between them makes a rule
look verified against a number its source never stated — the precise defect class
this project exists to remove, now produced by the audit tool itself.

The rulebook header confirms it was authored from `decision-frameworks-v1.md`
("Opus-prepared provenance quotes... against decision-frameworks-v1.md (the canonical
SOIC prose)"). The frameworks file and the ~13 L6/Masterclass lessons it cites are
not optional phase-2 enrichment; they are the audit target's actual source chain.

## 1. Verdicts

- **D1 — KEEP.** Rule audit is the right job for *this artifact*, because company
  triage already has an engine: soic-ladder runs Nifty 500 weekly-capable
  (snapshot → judge → synthesise, frozen auditable inputs, 236 tests). Building the
  graph for triage would duplicate a working screener with a worse one. But D1's
  "company triage is a downstream consumer" is doing unearned work — the consumer
  exists as a repo, not as a loop anyone runs weekly. See gap analysis.
- **D2 — KEEP.** Claim-as-atom with scope as a first-class field is correct; all
  three known defects are scope-loss shaped. Requires stable claim IDs (see D6).
- **D3 — CHANGE.** Six types fine. But the claim "promoting an example to a rule
  becomes a type error the graph can refuse" is **false under D9**: a propose-only
  graph refuses nothing. The rulebook is hand-authored YAML in another repo; nothing
  stops a human writing a worked_example number into a gate tomorrow. The type
  system only bites if a validator in *soic-ladder's CI* checks the rulebook against
  `claims.json` on every rulebook change. That validator is nowhere in D1-D12.
- **D4 — KEEP.** Mint from briefs, verify against `data/content.json`, resolve REF
  by `lesson_id` — sound, reuses proven machinery. One addition forced by finding 0:
  rulebook citations must also verify directly against raw transcripts, since they
  bypass the briefs entirely.
- **D5 — CHANGE.** Edge set is right; the corroboration COUNT is broken as defined.
  The Crash refs.json shows five multi-part pairs — TVGPT/TVGP2, VALU2/VALUV,
  SGBTS/SGBT2, SMEC2/SMECS, FMNAF/FMNA2 — that are **one session split in two, not
  independent sources**. D12 makes corroboration count the rule-grade test; without
  a session/module identity field and dedupe, a threshold reaches "rule-grade" by
  being said once in a lecture that was recorded in two files. Define independence
  (distinct module, distinct date where known) before the count carries weight.
- **D6 — CHANGE.** Derived graph + committed `adjudications.yaml` is the right
  architecture. Missing and load-bearing: **what keys a ruling to a claim across
  rebuilds**. If claim IDs derive from extraction output, a re-extraction that
  rephrases a claim orphans its adjudication, and D10's "contested, barred" ruling
  silently stops applying. Specify stable IDs and make rebuild **fail loudly** if
  any adjudication fails to attach. Without that, the overlay is a slow leak.
- **D7 — KEEP.** JSON + generated views + query script at ~1k claims. Correct
  scale call.
- **D7b — KEEP.** Verified by inspection; graphify's untyped repo map cannot host
  this schema.
- **D8 — KILL as stated, re-scope.** The provenance-purity rationale ("mixing
  provenance strengths would undermine corroboration") is backwards: the corpus you
  excluded is the one the rulebook cites (finding 0). Phase 1 must be **58 briefs +
  rulebook + decision-frameworks-v1.md + the specific L6/Masterclass lessons the
  rulebook refs resolve to**. Keep the other ~209 sector notes and uncaptured
  courses in phase 2 — that part of D8 was right. Provenance strength is already a
  per-claim field (D12 verification status); track it, don't amputate the corpus.
- **D9 — KEEP.** Propose-only is right; the fabricated-quote precedent is real.
  But note the proposal payload promises "what the change would do to the 38-name
  shortlist," which requires executing the soic-ladder engine cross-repo — feasible,
  currently unowned, and the current run actually has 49 CANDIDATE verdicts, not 38.
- **D10 — CHANGE.** Keep-all-values and never-auto-resolve is right (the RSI 45/50
  case proves it). Two defects: (a) "barred from becoming a gate" has **no
  enforcement path** — the graph proposes, the ladder loads whatever the YAML says;
  barred-in-graph is not barred-in-ladder without the D3 validator. (b) No standing
  policy for gates that are *already* contested: G8 gates on RSI >= 50 today. Strict
  barring hollows the screen — G2 and G6 are already deliberately unoccupied; strip
  G8 pending adjudication and the "screen" approaches pass-through. Policy needed:
  a contested threshold already deployed **stays at its current value, flagged
  contested in output**, until adjudicated — removal is a proposal like any other.
- **D11 — KEEP.** Honest about the 15/58 limit; `crawled_at` proxy correctly banned.
- **D12 — CHANGE.** Inputs 2-4 are sound; input 1 inherits D5's independence bug, so
  the whole confidence number is inflated for anything the Crash Course said in a
  two-part session. Fix D5's dedupe and D12 follows.

Tally: 7 KEEP, 5 CHANGE, 1 KILL-and-rescope.

## 2. Gap analysis — what the weekly loop needs that no decision covers

The graph is a static artifact over a corpus that never changes. What changes weekly
is prices (RSI/ADX/stage), quarterly results, and screener ratios — all of which
live in **soic-ladder**, none in this graph. The loop's skeleton already exists
(`/soic-ladder-screen`: snapshot → judge → synthesise; Shariah screen; read-only Kite
for held positions). Missing entirely:

1. **Cadence and ownership.** Nothing schedules a weekly run. No decision names who
   or what triggers snapshot → judge → synthesise → Shariah each week.
2. **Week-over-week diff.** The single most valuable weekly artifact is "what
   entered CANDIDATE, what left, which held position fired an exit trigger since
   last week." The ladder emits absolute state per run; nothing compares runs.
   Without a diff, the owner re-reads ~500 verdicts weekly or stops looking.
3. **Shortlist digestion.** The current run has **49 CANDIDATEs** (27 after Shariah).
   A non-quant cannot research 27-49 names a week. Nothing ranks or caps the list.
   Ironically the corpus's own answer exists in the graph design — D3's `procedure`
   claims ("after the screen fires read the concall/DRHP/guidance-vs-delivered") —
   but no decision turns those claims into the checklist the weekly output hands
   the owner for the top handful of *new* names.
4. **The graph→ladder contract.** The audit only pays off if rulebook edits flow:
   graph proposes → human applies → ladder CI validates against `claims.json` →
   next weekly run uses the corrected rule. Steps 3 and 4 exist nowhere.
5. **Data-quality flags reaching the loop.** CPPLUS sits in CANDIDATE with
   CFO/EBITDA -1.33% and CFO/PAT -48% — the capture itself flags these as
   unverified. G2 (forensic veto) is unoccupied, so nothing structural catches it.
   The open flags list has no route into weekly output.

## 3. The single most dangerous decision

**D8.** Not because pilot-first is wrong, but because it scopes the audit corpus to
exclude the audit target's actual sources. Three months of phase 1 yields a
beautifully verified claim graph of L3/L4/L5/Crash — and every `rule -encodes->`
edge is a semantic guess, every rulebook citation still unverifiable, the three
known defects still fixed by hand or not at all. The weekly loop keeps running on an
unaudited rulebook while the graph looks finished. **Instead:** phase 1 =
58 briefs + rulebook + `decision-frameworks-v1.md` + the ~13 lessons its refs
resolve to, with provenance strength recorded per-claim rather than enforced by
exclusion.

## 4. How this fails silently

- **Corroboration inflation:** TVGP Part 1 and Part 2 count as two independent
  sources; a once-stated threshold reaches "rule-grade" confidence; the owner trusts
  a number as multi-sourced that one lecture said once.
- **Fuzzy `encodes` matching:** rule "ROCE >= 15" matches the "ROCE >= 20 sustained"
  claim (or vice versa); the audit stamps the rule verified against a number its
  source never attached to it. Provenance manufactured by the provenance tool.
- **Orphaned adjudications:** a rebuild re-mints claim IDs; the LAURUSLABS/DIVISLAB
  rulings and every `contested` bar silently fail to re-attach; the graph reverts to
  un-adjudicated without any error.
- **Unenforced barring:** D10 marks RSI contested in the graph; the ladder YAML
  still gates at 50; the weekly output looks audit-blessed because "the graph
  exists."

## 5. Revised decision set (deltas only)

- **D8':** Phase 1 ingests 58 briefs + rulebook + decision-frameworks-v1.md + the
  lessons its refs resolve to. Everything else stays phase 2.
- **D5'/D12':** Add a `session` identity to claims; corroboration counts distinct
  sessions, not files. Multi-part lectures share a session.
- **D6':** Stable claim IDs (REF + timestamp + metric, not prose hash); rebuild
  fails if any adjudication does not attach.
- **D13 (new):** A rulebook validator lives in soic-ladder CI: every rule must
  `encode` a claim in `claims.json` by exact citation, no gate on a `contested` or
  `worked_example` claim. This is what makes D3's "type error" true and D10's
  "barred" real.
- **D14 (new):** The weekly loop is a decision, not a consumer: scheduled
  snapshot → judge → Shariah → **diff against last run** → ranked new-entrant list
  (cap ~5) each carrying the corpus's `procedure` checklist. Contested-but-deployed
  thresholds stay at current values, flagged, until adjudicated.

---

## Correction (2026-08-24) — D8's diagnosis was right, its conclusion was not

This review named **D8 the most dangerous decision**, on the evidence that the
rulebook's provenance REF codes and this corpus's 58 brief REF codes have an
**empty intersection** — therefore phase 1 as scoped "cannot verify a single
rulebook citation".

**The evidence is correct.** The two code sets genuinely do not overlap.

**The conclusion is now falsified.** A crosswalk already exists —
`Learning Vault Invest/wiki/personas/soic/refs/*.json`, 221 REF codes mapped to
lesson ids — which resolves the rulebook's codes to real lessons in
`data/content.json` without needing the frameworks file at all.
`scripts/audit_rulebook.py` was built on it and reports **15 of 16 citations
sound**, with `pe_context-001` (`ref: null`) the only defect.

So D8' (rescope phase 1 to pull in `decision-frameworks-v1.md`) is **no longer
required for citation auditing**. It may still be worth doing for coverage — the
frameworks file holds 40 frameworks and 207 citations — but that is a
scope-and-value decision, not the blocking dependency this review made it.

**What the review could not have known**, and what makes its central worry sound
even so: two of the three citation defects it inherited from the controller's
framing were themselves controller errors (`ERRATA.md` E1). The review reasoned
correctly from a premise that was wrong. That is exactly the failure mode it was
commissioned to catch, arriving one level up from where it looked.
