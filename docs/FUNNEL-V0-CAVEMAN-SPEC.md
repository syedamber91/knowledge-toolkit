# Funnel v0 — caveman spec (2026-11-04)

Status: DRAFT. Source: Fable review of Handoff B. Fable's file/number claims
are UNCHECKED by me (soic-ladder paths below not re-read here). Verify before build.
Screen shortlist only. Never buy/sell/hold.

## Task
One sector (pilot: Healthcare, 48 names). Cut down to a few names worth READING closely.
Say why each other name dropped.

## Why
Reading 48 annual reports = days. Owner wants 2-3 to read first.
Goal = save reading time, NOT predict price.

## What was wrong with old plan (Fable)
1. Gates leave ~13 of 48. Going 13 -> 2-3 had no rule. Any pick = after-the-fact.
2. Judging picks with same Screener data that chose them = circular.
3. "Hit rate vs random" is a return test. Goal is reading time. And n=3 has no power.
4. Lamps score silent management as weak. Measures how much they talk, not business.
5. council-soic / learning-vault-invest / roast-room not on this disk. Quote check can't run.
6. Plan skipped gate G3 (ROCE). Rulebook has it.

## Fix (v0: code only, offline, no model calls)
1. Input: soic-ladder `runs/nifty500-2026-08-29.db` + `docs/reports/q2-company-export/q2-company-export-2026-08-30.csv`, Industry == Healthcare.
2. Run G0, G1, G3, G8 via `judge.judge_company` (never retype thresholds).
3. Observations (CFO/PAT, D/E delta, P/E, PEG, EMA gap) = extra columns. Never filter.
4. Reading-worth rule (set BEFORE looking): CANDIDATE AND >=1 concall AND >=1 annual report on disk.
   If >3 pass, list all. No ranking.
5. Reasons table: one row per dropped name.
6. Control: base rate + seeded random_3 printed beside shortlist.
7. Qualitative step (council-soic) = separate later file, each quote flagged verified/not.

## Input
- the .db run + the q2 CSV (above)
- `rulebook/soic-ladder-rules-v1.yaml`
- docs on disk under `provenance/`

## Output
- `funnel_healthcare_<asof>.csv`: code, g0_sales, g0_pat, g1_de, g3_roce, g8_rsi, g8_adx, gate_verdict, abstain_metrics
- `reasons_healthcare_<asof>.csv`: code, first_failed_gate, rule_id, metric_value, threshold, abstain_or_fail, docs_on_disk
- short summary text with control block

## Acceptance (script checks)
- universe rows == 48; ABSTAIN names listed, count printed
- gate pass counts reproduce 15 / 14 / 13 / 13 (Fable's count; if differ, explain)
- every threshold maps to a rule_id found in the yaml
- no observation column changes gate_verdict
- reasons rows + shortlist rows + ABSTAIN rows == 48
- control block present; no return metric anywhere
- zero "buy/sell/hold" in outputs
- unverified quotes (if any) listed with count

## Numbers check (2026-11-04)
Own recount, simple script (NOT judge_company), run 1 of nifty500-2026-08-29.db:
48 Healthcare in CSV, 47 with metrics. Pass G0 15, G1 14, G3 13, G8 13. Matches Fable.
BIOCON: sales 9.99, ROCE 3.61, ADX 16.6 (matches). 3 names hit missing data.
Still to do: rerun through `judge_company` (admissibility, ABSTAIN handling) before build.

## Build result (2026-11-04)
`scripts/funnel_v0.py`, tests `tests/test_funnel_v0.py` (5 pass). Run with soic-ladder venv +
`PYTHONPATH=<soic-ladder>/src:<this repo>/src`. Real `judge_company`: G0 15, CANDIDATE 13 (matches Fable).
48 universe, 4 names with any ABSTAIN. Shortlist = ACUTAAS, NEULANDLAB. 46 reasons rows:
33 fail G0, 1 G1, 1 G3, 11 pass all gates but lack docs on disk. 2 + 46 = 48.
Control random_3 (seed 7) = CONCORDBIO, GLAND, GLENMARK. Outputs in `output/funnel/` (gitignored).
Zero buy/sell/hold in outputs. Rule-id and "observations never gate" hold by construction, not separately tested.
Caveat: the docs rule picks on what is ON DISK, not on business quality. 11 gate-passers dropped only for missing files.

## Not claimed
No proof this picks better than random. No Shariah. No lamps S1-S7 (no data for related party / auditor in DB).

## Pre-registration (2026-11-05, set before any new result is read)
Owner decisions: pilot = Healthcare. List only, alphabetical, no ranking. "Worth your time" = CANDIDATE
+ >=1 concall + >=1 annual report on disk (reading time, never return).
Done well = ALL of:
1. Every pick and every dropped name has a cited rule_id (reasons table).
2. shortlist + reasons rows == universe (48).
3. Beats seeded random_3 (seed 7, drawn from the whole universe) on one reading-time test:
   share of names that clear all gates AND have docs on disk. Funnel picks must be 100%.
4. Zero buy/sell/hold words; no return metric anywhere.
If any check fails: ship as a plain reading list, no claim.
Not claimed: any edge on returns; any ranking.

## Pre-reg result (2026-11-05, Healthcare, as of 2026-08-29)
1. Rule ids: every dropped name has one (reasons table). PASS.
2. 2 + 46 == 48. PASS.
3. Picks ACUTAAS, NEULANDLAB: 2/2 clear gates + have docs. Random_3 (whole universe, seed 7) = BLUEJET, GLAXO, JUBLPHARMA: 0/3. Base rate 2/48. PASS.
   Caveat: this test is near-circular, the picks are DEFINED by that rule. It shows the rule is applied right, not that the picks are better to read.
   Caveat: summary file prints a different control (from CANDIDATE only: CONCORDBIO, GLAND, GLENMARK). Pre-reg control is the one above.
4. Zero buy/sell/hold words; no return metric. PASS.
Verdict: all 4 pass. Ship as a reading list. Claim = "rule applied correctly", NOT "beats chance at picking good companies".

## Persona step result (2026-11-05, council-soic seat from roast-room, brain files _hot, voice, rules, checks)
Card: `output/funnel/persona_healthcare_2026-08-29.md` (gitignored). Seat given gate values from `judge_company`.
Quote check (12 quotes the seat used), two layers:
- In the seat's own brain notes: 12/12 verbatim.
- In raw SOIC transcripts (`data/content.json`): 7/12 verbatim (items 3-8, 11).
- NOT found in raw transcripts, so UNVERIFIED and not used on the sector card: item 1 (CFO/PAT 70%/60%, S036), 2 (80-90%, S470),
  9 (30-50x earnings, S430), 10 (ADX 20 line, S093), 12 (peak PE, S009). They are wording from course NOTES, not spoken words.
  Raw does contain "average directional index" nearby, so item 10 is likely a paraphrase of a real lecture, not a fake.
Seat flagged as untested: pledge %, related parties, auditor, valuation (no P/E), CFO for NEULANDLAB, PAT-growth bar past 300%.
Not done: learning-vault-invest cross-check; quote check by Fable-tier second model.
