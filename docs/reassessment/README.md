# SOIC lecture reassessment

Re-reading the SOIC courses **lecture by lecture, whole** to challenge the
`soic-ladder` shortlist. Design spec:
[`../superpowers/specs/2026-08-23-soic-l3-l5-crux-reassessment-design.md`](../superpowers/specs/2026-08-23-soic-l3-l5-crux-reassessment-design.md).

Why it exists: the rulebook encodes the method as numeric thresholds, but a
threshold lifted out of a lecture loses the sentence that said *when it
applies*. Only four rules can fail a company; **G2 (forensic veto) and G6
(valuation) are empty**, so nothing can ever be REJECTED.

## Method

One Fable lead per course delegates one Sonnet reader per lecture. Readers read
the `*-transcript.md` in the **Stock Market Vault** (never the AI-summary note,
never `learning-vault-invest` — both are compressions of the thing under test).
Every brief then clears `scripts/verify_briefs.py` at **>= 80% verbatim-quote
presence** before it is allowed into a synthesis.

## Status

| Course | Lectures | Briefs | Gate | Synthesis |
|---|---|---|---|---|
| Level 3 — How to Value a Company | 10 | ✅ | **10/10 pass** | ✅ |
| L4 — When to Hold, Buy & Sell | 19 | in flight | — | — |
| Level 5 — How to Screen & Filter | 4 | in flight | — | — |
| Crash Course (4 modules) | 25 | in flight | — | — |

58 lectures, ~4.3M chars of transcript in total.

## What the gate caught (keep this; it is the reason the gate exists)

Four of ten L3 briefs failed first pass. **None was an invented investment
claim**, but the re-checks they forced surfaced real defects:

- one brief had **merged and reordered three separate quotes** into a single
  continuous quotation that was never spoken that way;
- another used `...` elisions that **skipped real intervening words**;
- roughly **ten citation timestamps** pointed at the wrong moment.

**Two of the four failures were the checker's fault, not the readers'.**
(a) refs were resolved by slugified title, and four courses each contain a
lesson titled "What you will Learn in this Course? Intro", so the L3 brief was
verified against the *Technical Analysis* course — a correct brief scored 0/11.
(b) the mandated annotation convention `"garbled" [likely "Real Name"]` had its
bracketed text extracted as a separate claim, so the checker penalised
compliance with its own rule. Both fixed in `scripts/verify_briefs.py`.

**When a verifier accuses a generator, suspect the verifier first.**

## Level 3 headline

The lectures' **doubts cluster in the ladder's CANDIDATE column** and their
**endorsements cluster in WATCH**. Two causes:

1. `capital_efficiency_gate-001`'s provenance says "ROC/ROE above 15% **or
   trending toward it**"; only `>= 15` point-in-time was encoded. The gate now
   structurally prefers peak-economics companies — which ARTBV names as the
   danger zone — and demotes under-earning recovery names, which it names as
   the margin-of-safety zone.
2. No valuation gate exists, so price never disqualifies anything.

`pe_context-001` (flat 15-35 PE band) is contradicted by five lectures
independently and defended by none; 27 of the 38 names fail it.

**PALLOC** ("Portfolio Allocation Approach", 2h09m) was misclassified as a
0-char placeholder in `configs/course_eligibility.yaml` on 2026-07-27 and had
**never entered any prior synthesis pass**. The entire position-sizing layer
was missing from the frameworks.

## REF codes must begin with a letter

`gates._CITATION_NEAR` is `\(([A-Z][A-Z0-9]*)\s+\d{2}:\d{2}:\d{2}...\)`, so a
REF starting with a digit matches nothing and every quote in that brief scores
as uncited. The first generated batch produced 27 such codes, because many
lesson slugs begin with a date (`10.05.26 ...`, `1.12.24 ...`). `refs.json` is
now generated with leading numeric tokens stripped. Verify with
`re.fullmatch(r"[A-Z][A-Z0-9]*", code)` before dispatching readers, and verify
every `lesson_id` resolves against `data/content.json` in the same pass.

## Files

- `level-3/<REF>.md` — one crux brief per lecture (essence, mechanism, signals
  tagged HARD/SOFT/JUDGE, what the ladder misses, named companies, vs the 38)
- `level-3/SYNTHESIS.md` — Fable's adversarial cross-lecture synthesis
- `level-3/the-backwards-filter.html` — the plain-language reader
- `level-3/refs.json` — REF -> lesson_id map (resolution key; never title)
- `ladder-context-2026-08-22.md` — the rulebook + 38-name shortlist under test

## Not yet done

No rule has been changed. No company added or dropped. Two figures still need
source verification before use: CPPLUS's cash-conversion numbers, and whether
ASIANPAINT's G0 sales-growth snapshot and the "seven flat quarters" account
describe the same period.
