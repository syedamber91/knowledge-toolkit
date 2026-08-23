# Current soic-ladder state (the thing under test)

## The 16-entry rulebook
```yaml
rules:
  - id: canslim_sales-001
    gate: G0
    metric: sales_growth_yoy_pct
    check_rule: ">= 15"
    requires_attribute: {}
    display_text: "Quarterly sales growing at least 15% year on year"
    provenance:
      quote: "screen for >15% YoY quarterly sales growth and >20% PAT growth"
      ref: "MASTEC 00:09:35"
      slug: f25-canslim-sales-growth
      source_row: 324

  - id: canslim_pat-001
    gate: G0
    metric: pat_growth_yoy_pct
    check_rule: ">= 20"
    requires_attribute: {}
    display_text: "Quarterly profit growing at least 20% year on year"
    provenance:
      quote: "screen for >15% YoY quarterly sales growth and >20% PAT growth"
      ref: "MASTEC 00:09:35"
      slug: f25-canslim-pat-growth
      source_row: 324

  - id: leverage-001
    gate: G1
    metric: debt_to_equity
    check_rule: "<= 0.7"
    requires_attribute: {is_lender: "false"}
    display_text: "Debt to equity at or below 0.7 — not applied to lenders"
    provenance:
      quote: "D/E below 0.7x is the healthy-balance-sheet threshold"
      ref: "MASTEA 01:52:15-01:52:32"
      slug: f27-debt-to-equity
      source_row: 348

  - id: capital_efficiency_gate-001
    gate: G3
    metric: roce
    check_rule: ">= 15"
    requires_attribute: {is_lender: "false"}
    display_text: "Return on capital employed at or above 15% — not applied to lenders, whose capital employed includes deposits"
    provenance:
      quote: "ROC/ROE above 15% or trending toward it"
      ref: "MASTED 01:36:54-01:36:57"
      slug: f26-roce-fundamentals-bar
      source_row: 336
  - id: entry_rsi-001
    gate: G8
    metric: weekly_rsi
    check_rule: ">= 50"
    requires_attribute: {}
    display_text: "Weekly RSI at or above 50"
    provenance:
      quote: "screen for fresh entries with ADX crossing above 20 and weekly RSI crossing 50"
      ref: "HOWB 00:01:55-00:02:23"
      slug: f23-weekly-rsi-entry
      source_row: 300

  - id: entry_adx-001
    gate: G8
    metric: weekly_adx
    check_rule: ">= 20"
    requires_attribute: {}
    display_text: "Weekly ADX at or above 20"
    provenance:
      quote: "screen for fresh entries with ADX crossing above 20 and weekly RSI crossing 50"
      ref: "HOWB 00:01:55-00:02:23"
      slug: f23-weekly-adx-entry
      source_row: 300

# Context only. Never gates a verdict, never excludes a company, never
# appears in any gate. No `gate` key and no `requires_attribute` key exists
# on these entries — an observation that never excludes has nothing to
# scope.
observations:
  - id: pe_context-001
    metric: stock_pe
    reference_band: "between 15 35"
    display_text: "Price to earnings, read against a 15 to 35 reference band"
    provenance:
      quote: "a DCF (or reverse-PE at 15–35× band) gives intrinsic value"
      ref: null
      slug: f10-pe-band
      source_row: 122

  - id: cash_conversion-001
    metric: cfo_to_ebitda_pct_3y
    reference_band: ">= 60"
    display_text: "Operating cash conversion (CFO/EBITDA, 3-year average) — SOIC's stated bar is ~70% for B2C businesses, ~60% for B2B; read this number against whichever applies (not meaningful for banks/NBFCs — their cash-flow statement is a different shape)"
    provenance:
      quote: "should ideally be around 70% for consumer-facing B2C businesses and 60% for B2B businesses"
      ref: "MODULB 01:58:04-01:58:28"
      slug: f21-cfo-ebitda-conversion
      source_row: 276

  - id: capital_efficiency-001
    metric: roce
    reference_band: ">= 20"
    display_text: "Return on capital employed — SOIC states a sustained ROCE above 20% as the screening bar, and separately ROC/ROE above 15% 'or trending toward it' in the fundamentals checklist; read this number against whichever applies. This is a POINT-IN-TIME figure, not the multi-year 'sustained' reading the source describes. Not meaningful for banks/NBFCs — a lender's capital employed includes deposits, which structurally depresses the ratio."
    provenance:
      quote: "sustained ROCE above 20% and an operating margin near 28-29%"
      ref: "SOICA6 01:10:45"
      slug: f26-roce-screening-bar
      source_row: 394
  - id: capital_structure_trend-001
    metric: debt_to_equity_delta_3y
    reference_band: "<= 0"
    display_text: "Change in debt to equity over the last 3 years (negative = deleveraging). SOIC states a DIRECTION here, not a bar — a balance sheet strengthening over time, not a threshold to clear — so read the sign, not the size; accounting is an imprecise language and small moves are noise. Window shrinks to 2 or 1 year for short histories and the years used are shown alongside. Not meaningful for banks/NBFCs — a lender grows by borrowing, so rising leverage is its business model, not a deterioration."
    provenance:
      quote: "is the overall balance sheet getting stronger or weaker"
      ref: "MASTEA 01:52:51-01:53:22"
      slug: f27-balance-sheet-direction
      source_row: 346
  - id: peg_ratio-001
    metric: peg_ratio
    reference_band: "<= 1.5"
    display_text: "Price/earnings to 3-year profit growth (PEG) -- SOIC states a target below 1.5x, sourced independently in two courses (F26 and F38) which the source itself cross-references as matching. Not meaningful for negative or near-zero growth (a shrinking company has no sensible PEG) or loss-making companies."
    provenance:
      quote: "target a PEG below 1.5x"
      ref: "INSIGN 01:37:05"
      slug: f38-peg-target
      source_row: 494
  - id: cfo_to_pat-001
    metric: cfo_to_pat_3yr
    reference_band: "between 80 95"
    display_text: "Cash from operations as a share of net profit (CFO/PAT, 3-year average) -- corroborating range from two independently-sourced courses: F21 states 80-90%, F38 states roughly 90-95%. The source explicitly says to treat both as calibration ranges to corroborate against, not a single authoritative number -- read this alongside cash_conversion-001 (CFO/EBITDA), neither replaces the other. Not meaningful for a currently loss-making company."
    provenance:
      quote: "CFO/PAT above roughly 90-95%"
      ref: "SOICC 00:14:01"
      slug: f38-cfo-pat-corroborating-range
      source_row: 494
  - id: fixed_asset_turnover-001
    metric: fixed_asset_turnover_delta_3y
    reference_band: ">= 0"
    display_text: "Change in sales-to-fixed-assets turnover over the last 3 years (>= 0 = rising). SOIC's Ask is 'is fixed-asset turnover rising or falling', a direction with NO stated preference either way -- unlike the debt-trend observation, the source does not say rising is better than falling; it only asks whether the resulting asset-light/heavy classification matches how the market is pricing the company. Read the direction as information, not a verdict. Window shrinks to 2 or 1 year for short histories and the years used are shown alongside."
    provenance:
      quote: "Is fixed-asset turnover rising or falling -- and does the resulting asset-light/heavy classification match how the market is pricing it?"
      ref: "MASTEA 00:26:30-00:26:54"
      slug: f27-fixed-asset-turnover-direction
      source_row: 352
  - id: capex_expansion-001
    metric: capex_expansion_delta_3y
    reference_band: ">= 0"
    display_text: "Change in fixed assets plus capital work-in-progress over the last 3 years (>= 0 = expanding). SOIC's Ask is only 'is fixed-asset capex actively expanding the balance sheet', a factual question with NO stated preference for expansion over contraction -- unlike debt reduction, which the source explicitly frames as preceding 'a major up-move', nothing in F27 says expansion is good. Read the direction as information, not a verdict. This check is noisier than the debt-trend observation too: year-over-year fixed-asset reconciliation rarely ties out exactly due to depreciation and write-offs, and the source explicitly says to catch directional change, not to audit every line to the rupee. Window shrinks to 2 or 1 year for short histories and the years used are shown alongside."
    provenance:
      quote: "Is fixed-asset capex actively expanding the balance sheet?"
      ref: "MASTEA 00:26:30-00:26:54"
      slug: f27-capex-expansion-direction
      source_row: 352
  - id: growth_trap_flag-001
    metric: stock_pe
    reference_band: "< 30"
    display_text: "SOIC's growth-trap pattern: the market pays 30-50x+ PE assuming supernormal growth continues indefinitely, and as the earnings base gets larger the same growth RATE gets mathematically harder to sustain (the base effect) -- when growth decelerates, the multiple derates hard, compounding the slowdown into a price fall. This is a prompt to check the base effect, not a verdict: the source itself warns that 'calling a trap too early is often indistinguishable from being wrong.' Distinct question from pe_context-001 (which asks whether the multiple looks fair) -- this one asks whether the growth priced into it is arithmetically realistic."
    provenance:
      quote: "Growth traps form when the market pays 30-50x+ PE assuming supernormal growth continues indefinitely"
      ref: "TVGPF 00:18:39-00:19:07"
      slug: f29-growth-trap-pe-band
      source_row: 372
  - id: growth_durability-001
    metric: sales_growth_3y_pct
    reference_band: ">= 20"
    display_text: "Three-year compounded sales growth, read against a 20% reference band"
    provenance:
      quote: "growing revenues at 20-30%, well above nominal GDP growth"
      ref: "FLUORA 00:10:32-00:10:47"
      slug: f18-sitting-duck-revenue-growth
      source_row: 238
```

## GATES THAT ARE EMPTY
G2 = forensic veto (no rule -> nothing can ever be REJECTED)
G6 = valuation (no rule)

## The 38-name shortlist under challenge
| Company | Verdict | G0 | SalesYoY% | PatYoY% | G1 | D/E | G3 | ROCE% | G8 | RSI | ADX | P/E | P/E-ok | CFO/EBITDA% | ROCE20-ok | D/E-3yDelta | Growth3y% | PEG | PEG-ok | CFO/PAT% | CFO/PAT-ok | FAT-3yDelta | FAT-rising | Capex-3yDelta | Capex-rising | GrowthTrap-ok | ExitTriggers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ACE | CANDIDATE | PASS | 20.55 | 21.43 | PASS | 0.00 | PASS | 31.70 | PASS | 73.06 | 27.09 | 32.30 | Y | 118.33 | Y | -0.00 | 15.00 | 0.85 | Y | 111.08 | N | -0.24 | N | 319.00 | Y | N | 0 |
| ACUTAAS | CANDIDATE | PASS | 59.42 | 70.45 | PASS | 0.02 | PASS | 31.60 | PASS | 58.22 | 57.62 | 67.20 | N | 90.33 | Y | 0.02 | 30.00 | 1.08 | Y | 136.96 | N | -0.58 | N | 788.00 | Y | N | 0 |
| AJANTPHARM | CANDIDATE | PASS | 24.79 | 30.98 | PASS | 0.06 | PASS | 34.50 | PASS | 73.42 | 42.27 | 40.00 | N | 90.00 | Y | 0.05 | 13.00 | 1.67 | N | 90.69 | Y | 0.42 | Y | 420.00 | Y | N | 0 |
| ASIANPAINT | CANDIDATE | PASS | 17.93 | 39.57 | PASS | 0.18 | PASS | 26.30 | PASS | 50.74 | 20.84 | 51.90 | N | 110.33 | Y | 0.06 | 1.00 | 25.95 | N | 130.11 | N | -2.29 | N | 4699.00 | Y | N | 0 |
| AUROPHARMA | WATCH | PASS | 16.29 | 25.24 | PASS | 0.21 | FAIL | 12.90 | PASS | 65.09 | 38.17 | 24.90 | Y | 88.33 | N | 0.02 | 11.00 | 1.08 | Y | 115.75 | N | -0.32 | N | 6207.00 | Y | Y | 0 |
| CARBORUNIV | WATCH | PASS | 17.06 | 33.33 | PASS | 0.11 | FAIL | 10.50 | PASS | 61.36 | 38.37 | 89.00 | N | 90.67 | N | 0.01 | 4.00 |  |  | 148.87 | N | -0.32 | N | 433.00 | Y | N | 0 |
| CARTRADE | WATCH | PASS | 16.18 | 21.28 | PASS | 0.06 | FAIL | 11.80 | PASS | 66.71 | 38.31 | 62.60 | N | 86.67 | N | 0.01 | 29.00 | 0.70 | Y | 101.09 | N | 0.16 | Y | 481.00 | Y | N | 0 |
| CPPLUS | CANDIDATE | PASS | 89.46 | 330.30 | PASS | 0.14 | PASS | 28.60 | PASS | 66.54 | 56.39 | 86.00 | N | -1.33 | Y | -1.23 | 23.00 | 1.79 | N | -48.43 | N | -29.96 | N | 825.00 | Y | N | 0 |
| DIVISLAB | CANDIDATE | PASS | 27.80 | 65.50 | PASS | 0.00 | PASS | 22.00 | PASS | 84.09 | 28.92 | 76.40 | N | 87.33 | Y | 0.00 | 11.00 | 5.88 | N | 86.96 | Y | -0.03 | N | 3706.00 | Y | N | 0 |
| EMCURE | CANDIDATE | PASS | 22.80 | 35.81 | PASS | 0.31 | PASS | 24.00 | PASS | 61.28 | 51.85 | 34.30 | Y | 84.00 | Y | -0.62 | 15.00 | 1.63 | N | 142.86 | N | -0.10 | N | 1034.00 | Y | N | 0 |
| EXIDEIND | WATCH | PASS | 17.74 | 27.64 | PASS | 0.11 | FAIL | 8.54 | PASS | 68.21 | 38.85 | 41.60 | N | 115.33 | N | 0.06 | 6.00 | 20.80 | N | 204.44 | N | 0.40 | Y | 3997.00 | Y | N | 0 |
| FLUOROCHEM | WATCH | PASS | 23.97 | 20.33 | PASS | 0.29 | FAIL | 9.86 | PASS | 70.52 | 29.67 | 82.30 | N | 83.67 | N | 0.02 | -4.00 |  |  | 138.86 | N | -0.79 | N | 2452.00 | Y | N | 0 |
| GLAND | CANDIDATE | PASS | 19.52 | 47.44 | PASS | 0.03 | PASS | 15.10 | PASS | 71.34 | 46.30 | 40.50 | N | 96.33 | N | 0.03 | 21.00 | 5.06 | N | 120.15 | N | -0.88 | N | 3086.00 | Y | N | 0 |
| GLENMARK | CANDIDATE | PASS | 23.10 | 927.66 | PASS | 0.06 | PASS | 39.80 | PASS | 60.40 | 20.52 | 21.00 | Y | 50.33 | Y | -0.43 | 14.00 | 0.34 | Y | 86.93 | Y | 0.73 | Y | 212.00 | Y | Y | 0 |
| GRANULES | CANDIDATE | PASS | 22.07 | 59.29 | PASS | 0.30 | PASS | 15.50 | PASS | 63.32 | 35.74 | 32.70 | Y | 89.00 | N | -0.10 | 6.00 | 6.54 | N | 138.13 | N | -0.71 | N | 1510.00 | Y | N | 0 |
| HINDCOPPER | CANDIDATE | PASS | 81.40 | 162.69 | PASS | 0.03 | PASS | 42.50 | PASS | 60.58 | 28.03 | 45.90 | N | 98.33 | Y | -0.04 | 22.00 | 0.92 | Y | 130.99 | N | 0.34 | Y | 606.00 | Y | N | 1 |
| HSCL | CANDIDATE | PASS | 28.09 | 27.37 | PASS | 0.16 | PASS | 22.10 | PASS | 58.86 | 35.76 | 41.40 | N | 70.00 | Y | -0.21 | 4.00 | 0.88 | Y | 76.56 | N | -0.35 | N | 705.00 | Y | N | 0 |
| IPCALAB | CANDIDATE | PASS | 20.74 | 81.97 | PASS | 0.10 | PASS | 17.00 | PASS | 66.29 | 36.78 | 35.30 | N | 89.67 | N | -0.15 | 16.00 | 0.95 | Y | 148.47 | N | -0.18 | N | 2509.00 | Y | N | 0 |
| JUBLINGREA | WATCH | PASS | 25.24 | 41.33 | PASS | 0.25 | FAIL | 11.40 | PASS | 55.51 | 20.91 | 36.00 | N | 111.67 | N | 0.10 | -3.00 |  |  | 208.62 | N | -1.21 | N | 966.00 | Y | N | 0 |
| KAJARIACER | CANDIDATE | PASS | 20.40 | 55.45 | PASS | 0.07 | PASS | 23.30 | PASS | 59.35 | 26.14 | 32.90 | Y | 99.33 | Y | -0.03 | 3.00 | 2.35 | N | 147.57 | N | -0.14 | N | 265.00 | Y | N | 0 |
| LAURUSLABS | CANDIDATE | PASS | 29.04 | 123.46 | PASS | 0.48 | PASS | 17.80 | PASS | 80.87 | 54.67 | 89.20 | N | 92.00 | N | -0.02 | 4.00 | 22.30 | N | 253.91 | N | -0.21 | N | 1184.00 | Y | N | 0 |
| LODHA | CANDIDATE | PASS | 43.10 | 103.41 | PASS | 0.42 | PASS | 16.40 | PASS | 63.45 | 24.87 | 30.00 | Y | 63.00 | N | -0.29 | 21.00 | 0.54 | Y | 82.06 | Y | 1.13 | Y | 823.00 | Y | N | 0 |
| MARICO | CANDIDATE | PASS | 22.85 | 27.10 | PASS | 0.13 | PASS | 47.00 | PASS | 64.36 | 27.87 | 58.70 | N | 95.67 | Y | -0.03 | 12.00 | 5.34 | N | 96.50 | N | -0.60 | N | 1405.00 | Y | N | 0 |
| MINDACORP | WATCH | PASS | 33.19 | 216.92 | PASS | 0.56 | FAIL | 12.70 | PASS | 72.83 | 31.91 | 43.20 | N | 98.67 | N | 0.11 | 13.00 | 5.40 | N | 176.20 | N | -0.33 | N | 649.00 | Y | N | 0 |
| MOTHERSON | WATCH | PASS | 16.66 | 77.56 | PASS | 0.47 | FAIL | 13.40 | PASS | 74.62 | 32.37 | 39.10 | N | 93.00 | N | -0.15 | 17.00 | 0.98 | Y | 226.14 | N | -0.12 | N | 17967.00 | Y | N | 0 |
| NATIONALUM | CANDIDATE | PASS | 39.27 | 90.94 | PASS | 0.00 | PASS | 39.60 | PASS | 56.01 | 29.25 | 10.70 | N | 108.33 | Y | -0.01 | 8.00 | 0.18 | Y | 119.35 | N | 0.41 | Y | 3374.00 | Y | Y | 2 |
| NAVINFLUOR | CANDIDATE | PASS | 44.14 | 107.69 | PASS | 0.32 | PASS | 21.00 | PASS | 75.56 | 46.58 | 53.00 | N | 138.33 | Y | -0.07 | 17.00 | 2.52 | N | 203.33 | N | -0.26 | N | 1542.00 | Y | N | 0 |
| NESTLEIND | CANDIDATE | PASS | 25.16 | 48.22 | PASS | 0.09 | PASS | 85.30 | PASS | 57.24 | 31.14 | 76.90 | N | 97.67 | Y | -0.02 |  |  |  | 117.90 | N | -0.01 | N | 1595.00 | Y | N | 0 |
| NEULANDLAB | CANDIDATE | PASS | 119.11 | 957.14 | PASS | 0.16 | PASS | 26.50 | PASS | 78.18 | 44.95 | 60.10 | N | 92.67 | Y | 0.03 | 19.00 | 2.00 | N | 101.42 | N | 0.15 | Y | 589.00 | Y | N | 0 |
| PIDILITIND | CANDIDATE | PASS | 21.29 | 30.38 | PASS | 0.04 | PASS | 31.00 | PASS | 66.90 | 25.51 | 63.30 | N | 109.67 | Y | -0.02 | 7.00 | 2.53 | N | 126.49 | N | 0.13 | Y | 783.00 | Y | N | 0 |
| POLYCAB | CANDIDATE | PASS | 39.01 | 32.83 | PASS | 0.02 | PASS | 33.20 | PASS | 56.00 | 28.63 | 47.10 | N | 91.33 | Y | -0.01 | 27.00 | 1.68 | N | 100.34 | N | 0.90 | Y | 2561.00 | Y | N | 0 |
| SAREGAMA | CANDIDATE | PASS | 27.54 | 40.54 | PASS | 0.04 | PASS | 17.80 | PASS | 70.71 | 40.66 | 42.80 | N | 85.33 | N | 0.04 | 10.00 | 8.56 | N | 85.92 | Y | -1.23 | N | 689.00 | Y | N | 0 |
| SCI | WATCH | PASS | 40.35 | 74.86 | PASS | 0.29 | FAIL | 14.30 | PASS | 52.86 | 23.62 | 8.37 | N | 57.67 | N | -0.08 | 0.00 | 0.52 | Y | 115.45 | N | 0.02 | Y | -233.00 | N | Y | 0 |
| SONACOMS | WATCH | PASS | 52.34 | 46.72 | PASS | 0.07 | FAIL | 14.20 | PASS | 78.44 | 44.31 | 70.00 | N | 90.00 | N | -0.05 | 19.00 | 3.89 | N | 122.57 | N | -0.45 | N | 2394.00 | Y | N | 0 |
| SPLPETRO | WATCH | PASS | 22.33 | 190.24 | PASS | 0.06 | ABSTAIN |  | FAIL | 48.68 | 23.75 | 26.70 | Y | 75.33 |  | -0.68 |  |  |  | 144.69 | N | -2.86 | N | 1312.00 | Y | Y | 2 |
| TMCV | CANDIDATE | PASS | 19.30 | 82.96 | PASS | 0.44 | PASS | 35.90 | PASS | 65.12 | 30.53 | 23.40 | Y | 174.00 | Y | -0.50 |  |  |  | 494.42 | N |  |  | 449.00 | Y | Y | 0 |
| USHAMART | CANDIDATE | PASS | 16.46 | 40.59 | PASS | 0.07 | PASS | 19.50 | PASS | 56.91 | 40.07 | 26.90 | Y | 96.33 | N | -0.14 | 4.00 | 2.99 | N | 116.41 | N | -1.16 | N | 623.00 | Y | Y | 0 |
| VIJAYA | CANDIDATE | PASS | 22.87 | 35.90 | PASS | 0.44 | PASS | 21.30 | PASS | 70.71 | 44.99 | 82.70 | N | 97.00 | Y | -0.01 | 21.00 | 3.06 | N | 154.90 | N | -0.12 | N | 552.00 | Y | N | 0 |
| WELSPUNLIV | WATCH | PASS | 23.62 | 83.15 | PASS | 0.47 | FAIL | 6.25 | PASS | 73.34 | 27.95 | 65.20 | N | 91.00 | N | -0.13 | 5.00 | 16.30 | N | 245.89 | N | 0.04 | Y | 765.00 | Y | N | 0 |