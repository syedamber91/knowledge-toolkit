# Funnel design, Healthcare pilot (2026-11-05)

Step 1 of the sector funnel. Paper only. Screen for READING order, never buy/sell/hold.
Owner answers + pre-registered bars: `docs/FUNNEL-V0-CAVEMAN-SPEC.md` ("Pre-registration").
Rules read from `soic-ladder/rulebook/soic-ladder-rules-v1.yaml`. Thresholds are never retyped here;
the code reads them through `judge_company`.

| Stage | What it does | Cited source | Built? |
|---|---|---|---|
| 0. Universe | Industry == Healthcare in the q2 export (48 names) | `soic-ladder/docs/reports/q2-company-export/q2-company-export-2026-08-30.csv` | yes |
| 1. G0 growth | sales growth, PAT growth | `canslim_sales-001`, `canslim_pat-001` | yes |
| 2. G1 leverage | debt to equity | `leverage-001` | yes |
| 3. G3 returns | ROCE; ROE (lenders only) | `capital_efficiency_gate-001`, `roe_lender-001` | yes |
| 4. G8 entry timing | weekly RSI, weekly ADX | `entry_rsi-001`, `entry_adx-001` | yes |
| 5. Reading-worth | CANDIDATE and >=1 concall and >=1 annual report on disk | owner answer Q3 | yes |
| 6. Lamps (cash, debt, related party, auditor) | extra forensic look | none: G2 slot is empty, no data in DB | NO (not built) |
| 7. Persona questions | council-soic + learning vault, quote checked | not on this disk | NO (later) |

Observations (CFO/PAT, D/E delta, P/E, PEG, EMA gap) = extra columns only. They never change a verdict.

Output: shortlist (alphabetical, no rank) + one reasons row per dropped name (first failed gate + rule_id).

## Known risks
- Mixed years (sales up, profit down) can score like a weak company. G0 uses two metrics, but nothing flags "mixed".
- Stage 5 picks by files on disk, not business quality (11 gate-passers dropped only for missing docs).
- Peer group = NSE bucket, not true rivals. Screener fields may differ from filings. Today's index members only.
- Stages 6 and 7 are not built. The card must say so.

## Next (step 2 done; step 3 = run)
Run `scripts/funnel_v0.py`, then do pre-reg check 3 (funnel picks vs seeded random 3 on "clears gates AND has docs").
