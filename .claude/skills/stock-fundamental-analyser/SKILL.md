---
name: stock-fundamental-analyser
description: Full 12-step fundamentals report on one Indian (NSE/BSE) listed stock for a long-term investor, rendered as an 8-tab interactive HTML report (Snapshot, Valuation, Growth, Health, Returns, Peers, Ownership, View). Asks for the stock and the investment horizon first. Never a buy/sell/hold call. Use when the user names an Indian stock and wants a full fundamental report, or says "stock research", "fundamental analyser" or "analyse TCS for 5 years".
---

<!-- Source: Google Doc "STOCK RESEARCH USING CLAUDE" (id 1cB3JQJ0KE_raEA5HF6YRgrW0rBr_AyuYUzu_idqhn6s),
     a prompt written for Claude.ai. Turned into a skill 2026-11-04.
     Changes from the doc: split into SKILL.md + report-template.html; the doc's text was cut off
     inside the final <script>, so show() was rewritten (it only swaps CSS classes); mojibake emoji
     restored; neutral colour tokens and a mobile-friendly table wrapper added to the template;
     rendering rule adapted for Claude Code (Artifact tool). Thresholds below are the doc's own. -->

# Indian Stock Fundamental Analyser

For long-term investors. Fundamentals only. Output is a VIEW, never a recommendation.

This is a different skill from `stock-analyzer` (that one has five quick modes). Use this one when the user wants the full 8-tab report with a stated horizon.

## Files in this skill

| File | What it is |
|---|---|
| `SKILL.md` | The rules and the 12 steps (this file) |
| `report-template.html` | The exact HTML to fill in with real data. Read it in full before Step 12. |

## Operating rules (every run)

1. **Do not go past Step 1 until BOTH answers are in** (stock + horizon).
2. **Historical data only.** No "this stock should..." or "expected to...". The Step 7 scenarios are illustrations of past trends continuing, and the report must label them that way.
3. **Every metric cites its source.** If it cannot be found, write `🚩 DATA UNAVAILABLE — verify at [source URL]`. Never estimate or fill from memory.
4. **Search live data first.** If live search is impossible, say so plainly: "Live data unavailable. Figures below are from training data and may be outdated. Verify independently before investing."
5. **No buy, sell, hold or target price. Ever.** You give a VIEW. The user decides.
6. **Run the steps in order.** Do not skip or merge them.
7. **Plain English.** Explain jargon in one short line the first time. Write for a smart beginner.

## Step 1 — Input (ask both, then wait)

Ask exactly this and nothing else on the first message:

---
📊 Tell me two things and I'll build your full fundamental report:

**1. Which stock?**
Company name or NSE/BSE ticker — e.g. TCS · RELIANCE · HDFCBANK

**2. Investment horizon?**
How many years are you planning to stay invested?
3 Years · 5 Years · 10 Years · or type your own
---

If the user already gave both in their message, skip the question and go to Step 2. If the company name matches several listings, ask which one. Nothing else.

## Step 2 — Silent research (never narrate it)

Use WebSearch and WebFetch. Cross-check each data point in at least 2 sources where possible. Never mention this step to the user.

Source priority: NSE India → BSE India → Screener.in → Tickertape → Moneycontrol → annual reports → earnings call transcripts → Tijori Finance. (NSE and BSE often block automated fetches. Lean on Screener.in and Tickertape, and say which you used.)

Checklist:

- Live CMP, 52W high, 52W low, market cap, face value
- P/E, P/B, EV/EBITDA: current, sector average, and the stock's own 5-year average
- Revenue, net profit and EPS CAGR: 3-year and 5-year
- EBITDA margin and net profit margin trend: 5 years
- EPS for the last 8 quarters, with YoY change
- Free cash flow: last 3 to 5 years
- Debt-to-equity: 5-year trend
- Interest coverage ratio and current ratio
- ROE and ROCE: current, 3-year average, 5-year average
- Dividend history and payout ratio
- Promoter holding for the last 8 to 12 quarters, and promoter pledging
- FII and DII holding trend for the last 8 quarters
- Competitive moat: pricing power, brand, switching costs, market share
- Sector tailwinds and headwinds, 5 to 10 year outlook
- Regulatory risks
- Management track record: guidance vs delivery, governance flags
- Latest quarterly earnings call: key management commentary
- 3 closest peers: P/E, P/B, ROE, revenue growth, D/E
- Top 5 recent news items relevant to long-term investors

## Step 3 — Valuation

Compare current P/E, P/B and EV/EBITDA with the sector average and the stock's own 5-year average.

| Signal | Rule |
|---|---|
| CHEAP | meaningfully below both sector average and own history |
| FAIR | in line with both (within 10%) |
| EXPENSIVE | meaningfully above both |

Overall: UNDERVALUED / FAIRLY VALUED / OVERVALUED / MIXED.

## Step 4 — Growth

Look at revenue, net profit, EPS and margin trends. Classify: ACCELERATING / STEADY / SLOWING / DECLINING.

## Step 5 — Financial health

| Metric | Bands |
|---|---|
| Debt / Equity | below 1 = SAFE · 1 to 2 = MODERATE · above 2 = LEVERAGED |
| Interest coverage | above 3x = HEALTHY · 1.5 to 3x = WATCH · below 1.5x = RISK |
| Current ratio | above 1.5 = COMFORTABLE · 1 to 1.5 = WATCH · below 1 = RISK |
| Free cash flow | positive and growing = STRONG · positive but flat = STABLE · negative = CONCERN |

## Step 6 — Return quality

| Metric | Bands |
|---|---|
| ROE | above 15% = GOOD · 10 to 15% = AVERAGE · below 10% = WEAK |
| ROCE | above 15% = GOOD · 10 to 15% = AVERAGE · below 10% = WEAK |

Also judge dividend consistency and whether the payout is sustainable.

## Step 7 — Past-trend scenarios (for the stated horizon)

Build three scenarios from historical CAGR trends only:

- **Bear:** growth slows, margins compress
- **Base:** current trajectory continues
- **Bull:** growth picks up, margins expand

Show estimated revenue, net profit and EPS at the end of the horizon. Always label them: "Illustrations of historical CAGR trends continuing — not guarantees or predictions." If the inputs for a scenario are missing, mark it DATA UNAVAILABLE instead of inventing inputs.

## Step 8 — Peers

Pick the 3 closest competitors. Compare P/E, P/B, ROE, revenue growth, D/E. Classify the stock: LEADING / MID-PACK / LAGGING.

## Step 9 — Ownership

- Promoter: BUYING / STABLE / SELLING
- FII: INCREASING / STABLE / DECREASING
- DII: INCREASING / STABLE / DECREASING
- Pledging: flag it if above 10%

## Step 10 — Fundamental view (for the stated horizon)

Combine Steps 3 to 9 into:

- one sentence on what the fundamentals show
- 3 strengths
- 2 risks or watch points
- 1 thing to track going forward
- overall quality: STRONG / MODERATE / WEAK

## Step 11 — Data confidence

Count the 12 key sections of the report that were filled from live, named sources (the rest are DATA UNAVAILABLE).

| Live sections | Rating | Confidence-bar class |
|---|---|---|
| 9 to 12 | HIGH | `high` |
| 6 to 8 | MODERATE | `moderate` |
| 1 to 5 | LOW (warn the user) | `low` |
| 0 | VERY LOW | `vlow` |

(The source doc said "9 to 10 = HIGH" against a 12-section bar. 11 and 12 were left out, so they count as HIGH here.)

## Step 12 — Render

1. Read `report-template.html` in this folder, in full.
2. Fill every `[PLACEHOLDER]` with real researched data. Use the exact class names from the template. Flag any missing metric inline as `🚩 DATA UNAVAILABLE — verify at [source URL]`. Remove the flag-card block if there are no flags. Repeat the EPS chip 8 times and the news block 5 times.
3. **The View tab (index 7) must be the active tab on load.** It already is in the template: keep `class="tab-btn active"` on the View button and `class="panel on"` on `p7`, and no other tab or panel may carry `active` or `on`.
4. Output:
   - **Claude Code:** save the filled HTML as a `.html` file and publish it with the Artifact tool (title: the company name, for example "TCS Fundamentals"). Load the artifact-design skill first if it is listed. Give the user the link.
   - **Claude.ai or no Artifact tool:** output the raw HTML directly, with no markdown, no code fence, no DOCTYPE, no html/head/body tags. It starts with `<style>` and then `<div class="wrap">`.
5. After the report, add one line: "This is a view of the fundamentals only, not advice. Decision is yours."

Do not leave any `[` placeholder in the final HTML. Search the file for `[` before publishing.
