# Proposed framework-file diff: F21–F24 (NOT YET APPLIED — needs human sign-off)

> **Status: PROPOSED DRAFT ONLY.** This file follows the repo's established
> `framework_evolution.py` convention: a reviewable diff a human approves (or
> rejects/edits) before anything is written to
> `wiki/personas/soic/frameworks/decision-frameworks-v1.md`. Nothing below has
> been applied to the real frameworks file. Each `## F<n>.` section is
> formatted to the file's exact existing template (`**Model.**` /
> `**Applies when.**` / `**Ask.**` / `**Live data.**` / `**Grounding.**`) so an
> approved section can be copy-pasted verbatim, appended after F20 under a new
> batch divider (suggested: `## Method-course additions (L2–L5, 2026-07-27)`).
>
> Source concept notes (all read in full, citations verbatim):
> `cash-flow-reconciliation-and-working-capital-dynamics.md`,
> `revenue-manipulation-and-recognition.md`,
> `return-on-equity-roe-and-dupont-analysis.md`,
> `stan-weinstein-s-stage-analysis-framework.md`,
> `system-based-exits-and-time-stop-losses.md`,
> `sector-specific-valuation-metrics.md`
> (in `wiki/personas/soic/concepts/`).

---

## F21. Cash-conversion / forensic red-flag safety gate

**Model.** Reported profit is an accrual opinion; cash conversion is the reality check. Healthy operators convert operating profit to operating cash at a stable rate — CFO/EBITDA "should ideally be around 70% for consumer-facing B2C businesses and 60% for B2B businesses" (MODULB 01:58:04-01:58:28). Manipulated revenue breaks this conversion through known mechanisms: channel stuffing and lenient credit trap cash in receivables — visible as "a spike in trade receivables that are delayed by more than 180 days" (MODULA 00:15:05-00:15:47) — so "the conversion of operating profit into operating cash flow begins to rapidly decline, which is a major red flag" (MODULB 00:18:31-00:18:48); diluting the mix with traded goods (core manufacturing at 10–15% margin vs ~1% on traded third-party goods) inflates the top line while producing "poor quality of revenues" (MODULB 00:16:40-00:17:34); and burying one-offs in core revenue manufactures fake growth — Aarti Industries' revenue "inclusive of contract termination [likely fees] of 631 crores" made ~7% underlying PBT growth look like 50–60% (MODULG 00:16:42-00:17:19, MODULG 00:19:38-00:20:02). This is a **veto-class gate**: a failed gate caps the verdict at AVOID regardless of how attractive valuation/growth frameworks look — it does not generate BUY signals.

**Applies when.** Any non-financial company, before any bullish framework's output is trusted. **Explicitly inapplicable to banks/NBFCs:** their operating cash flow is inherently negative, making the cash flow statement "redundant and void" for these sectors (MODULB 01:54:03-01:55:34) — lenders are gated by F12 instead.

**Ask.** What is CFO/EBITDA over 3–5 years vs the 70% (B2C) / 60% (B2B) band — and is the trend deteriorating? Are receivable days rising faster than peers', with any disclosure of receivables outstanding >180 days? Is the traded-goods share of revenue rising at the expense of manufactured margin? Does "revenue from operations" contain one-off items (termination fees, expected compensation booked before cash receipt — the SpiceJet/Boeing pattern, MODULG 00:20:35-00:21:43) that should sit in exceptional items/other income?

**Live data.** CFO, EBITDA, receivable days multi-year (screener cash-flow + ratios sections — NOTE: derived from statement tables, not the top-ratios grid `screener_client.py` currently parses; a fetch extension is required), >180-day receivables ageing and traded-vs-manufactured split (annual report/NotebookLM), one-off disclosure (results footnotes/concall).

**Grounding.** `cash-flow-reconciliation-and-working-capital-dynamics` (Module 3), `revenue-manipulation-and-recognition` (Module 4 Forensic Analysis). Legitimate exceptions the gate must respect before vetoing: B2B models holding strategic inventory (MODULA 00:21:18-00:22:08) and B2G receivables stretched by the government as a "notoriously lazy payer" (MODULA 00:22:39-00:22:56) — high WC there is business model, not fraud; and "interpreting financial statements is an 'imperfect art'" (MODULC 00:37:00-00:37:06), so a single soft quarter is a flag to investigate, not an automatic veto.

## F22. DuPont ROE-quality decomposition gate

**Model.** ROE alone hides *how* the return is produced. DuPont decomposes it into net profit margin × asset turnover × financial leverage (MODULE 00:19:00-00:19:35, MODULH 00:16:35-00:17:39); investors should prefer "an ROE driven by strong profit margins and efficient asset turnover rather than one inflated primarily by debt" (MODULE 00:19:37-00:20:25). Because debt is excluded from the equity denominator, leverage creates an "illusion" — a mediocre business can print a high ROE right up until "excessive debt can cause the ROE to rapidly collapse or turn negative", as Tata Motors' seemingly high ROE structurally declined while leverage expanded and margins/turns deteriorated (MODULE 00:18:16-00:23:43). The same decomposition powers peer ranking: APL Apollo's ~24.64% ROE comes from ~3× asset turnover plus better margins, while Rama Steel Tubes and Hi-Tech Pipes reach their ROEs "much more heavily [through] financial leverage" (MODULH 01:01:00-01:03:37); Vedant Fashions' 28% ROE is driven by ~31% net margins — pricing power, not leverage (MODULH 00:46:34-00:47:30).

**Applies when.** Any quality/compounder thesis resting on a headline ROE/ROCE number, and any peer comparison within a sector.

**Ask.** Decompose: what fraction of the ROE comes from margin, turnover, and leverage respectively — and which component is *trending*? Is the leverage component's contribution rising while margin/turnover flatten (the Tata Motors failure shape)? Versus peers, is this company's ROE the margin/turns kind or the debt kind? **Calibration caveat — state it, don't fake it:** SOIC states the *direction* (margin/turns good, leverage-driven bad) but no numeric leverage-share ceiling; until a follow-up calibration note derives and documents one, this framework downgrades quality conviction directionally and cannot emit a hard numeric pass/fail.

**Live data.** Net margin, sales, total assets, equity, debt (screener balance-sheet/P&L tables — beyond the current top-ratios fetch; ROE/ROCE themselves are in top-ratios), multi-year for trend.

**Grounding.** `return-on-equity-roe-and-dupont-analysis` (Module 5 Ratio Analysis). Hard limit: ROE is "highly deceptive in cyclical industries" — CEAT's ROE collapsed from peak double digits to ~6% purely on raw-material costs (MODULH 00:50:23-01:00:24) — so for sectors flagged cyclical in the sector overlay this gate must ABSTAIN rather than score, judging the cycle via F5 instead.

## F23. Weinstein Stage-Analysis timing gate (entry / exit / time-stop)

**Model.** Stan Weinstein's four stages tie price/volume structure to EPS momentum — "a stock price is ultimately a 'slave to earnings growth'" (HOWC 00:31:31, HOWC 01:14:48). Stage 1: sideways base oscillating around the 30-weekly moving average (HOWD 00:22:15-00:23:22). Stage 2 (buyable): breakout above the 30-weekly MA on high volume, fundamentally triggered by a "positive surprise" starting "EPS momentum" (HOWD 00:05:51, HOWC 01:40:19-01:41:14); screen for fresh entries with ADX crossing above 20 and weekly RSI crossing 50 (HOWB 00:01:55-00:02:23). Stage 4 (must-avoid/exit): breakdown below the 30-weekly MA aligned with "loss of EPS momentum" (HOWD 00:26:07, HOWC 01:41:14-01:41:40). The exit is systematic, not discretionary — sell when **three conditions fire together**: price breaks below the 30-weekly EMA, Relative Strength vs Nifty 50/500 (RS length 26 or 52 weeks) turns negative, and the volatility stop (ATR, length 10, multiplier 2–2.5) turns negative (FRAMEC 01:46:39-01:47:01, FRAMEC 01:52:06-01:52:35, FRAMEC 01:54:57, FRAMEC 01:55:28-01:55:30). Independently, a time stop-loss of 4–8 quarters caps how long capital waits in a fundamentally-fine-but-flat stock (FRAMEC 01:30:22-01:30:56). In a parabolic rise, when price extends more than 70% above the 30-weekly EMA, tighten to a 10-weekly (or 40-daily) MA (FRAMEC 02:01:03-02:02:51).

**Applies when.** Timing an entry into, or a systematic exit from, any stock a fundamental framework already likes — this gate never originates a thesis; it sequences it. Per the source's own scope limit, the technical exit system is "recommended primarily for 'satellite PF stocks' rather than 'core holdings'" (FRAMEC 01:56:49-01:57:42).

**Ask.** Which stage is the stock in on the weekly chart? For entry: has a Stage-2 breakout printed on high volume with ADX>20 and weekly RSI>50 — or is the stock still Stage 1 (dead capital risk) or Stage 3/4? For exit: how many of the three triggers (30w-EMA break, negative RS, negative V-stop) are currently firing? Has the position been flat past the chosen 4–8-quarter time stop? Is price >70% extended above the 30-weekly EMA (switch to the tighter MA)?

**Live data.** **Dependency gap — flagged, not papered over:** this framework needs weekly OHLCV price series (for the 30w/10w EMA, 26/52w RS vs Nifty, ATR V-stop, ADX, weekly RSI, volume), which `screener_client.py` does NOT fetch — it parses only screener.in's top-ratios grid. Until a price-series source (e.g. NSE bhavcopy/TradingView export) is wired into the senses layer, this framework is evaluable only manually against a charting tool and must ABSTAIN in any automated run.

**Grounding.** `stan-weinstein-s-stage-analysis-framework` (How to Screen & Filter Epic Stocks), `system-based-exits-and-time-stop-losses` (Framework For Buying & Selling A Stock). Known costs and limits, from the sources themselves: the triple-trigger exit surrenders "10% to 25% from the top" (FRAMEC 01:47:39-01:47:44); choppy/sideways markets generate false breakdowns (FRAMEC 01:57:25-01:57:52); Stage 3→4 transitions are often clear only "in hindsight" (HOWD 00:11:45-00:11:50); recent IPOs lack the history for a 30-weekly EMA (FRAMEC 01:58:56-01:59:12); recovering charts face "overhead supply" resistance (HOWD 00:18:01-00:18:59).

## F24. Sector-metric-selection meta-rule (which valuation lens is even valid)

**Model.** A **routing rule, not a bullish/bearish signal**: before any valuation framework (F10, F13) runs, select the metric the sector's accounting actually supports — using one blanket P/E is like judging an aspiring engineer "by their overall report card percentage" instead of their maths marks (HOWE 00:01:25-00:02:50). The routing table: **banks/financials → P/B**, because extreme leverage (one unit of equity funding ~ten of assets) makes P/B + ROA/ROE + NPA management the real drivers (HOWC 00:45:35, HOWC 00:48:08-00:51:53); **asset-heavy (hotels, hospitals, QSR, telecom) → EV/EBITDA**, because 20–40-year assets make accounting depreciation overstate costs and depress P/E (HOWH 00:19:52-00:21:07); **cement → EV/ton (or EV/EBITDA)**, proxying replacement cost of capacity in a high-debt, cash-generative sector (HOWC 00:58:12-00:58:39); **real estate → market-cap/pre-sales or "imputed EBITDA"**, because upfront construction costs plus handover-time revenue recognition create optical losses (HOWF 00:42:42-00:44:20); **asset-light IT/FMCG → plain P/E and cash-flow metrics remain accurate** (HOWC 00:41:22-00:43:01). Output of this framework: the metric key F10's band check should evaluate for this sector — nothing more.

**Applies when.** Always — as the first step of any valuation evaluation, resolving the sector overlay before a single multiple is compared to a band.

**Ask.** Which row of the routing table does this company fall in — and if a conglomerate spans several, has a Sum-of-the-Parts split been done (complex structures carry a "conglomerate discount", HOWD 01:11:34-01:15:25; see also F19)? Is the chosen metric currently distorted by one-off earnings (bulk orders, inventory gains) that "inevitably guarantee a severe derating once the anomaly passes" (HOWH 00:32:09-00:34:12)?

**Live data.** Sector classification (sector overlay / `sector_notebooks.yaml`), then the routed metric's inputs: P/B and NPAs (screener) for financials; EV components — market cap, debt, cash (screener top-ratios + balance sheet) — and EBITDA for asset-heavy; capacity tonnage (AR/concall) for cement; pre-sales disclosures (investor PPT/NotebookLM) for real estate.

**Grounding.** `sector-specific-valuation-metrics` (How to Value a Company & Portfolio Creation, merged with the L2 SOIC Screener Sheet walkthrough). **Calibration (dated, and handle with care):** the note's IHCL trailing market-cap/EBITDA of 42 (UPDAT 00:23:59-00:24:53) is a point-in-time worked example, NOT a durable threshold — per F11 it must never be reused as a band. The UPDAT source passage also carries flagged ASR garbling ("float statement" for a flawed metric, "more depression" for depreciation — UPDAT 00:06:59, UPDAT 00:24:53-00:25:04), so no numeric threshold may be sourced from that stretch of transcript; and the sheet's own author disclaims stock-picking: "there is no recommendation here" (UPDAT 00:15:31-00:15:38). Also respect: "accounting is an imprecise language" and depreciation excluded by EV/EBITDA "remains a real and eventual expense" (HOWE 00:25:00-00:26:32).

---

*Draft prepared 2026-07-27 from the L2–L5 method-course concept notes synced 2026-07-27. Per the F21–F24 numbering, these follow F20 (Fluorine batch). Review order suggestion: F21 and F24 are the highest-leverage (veto gate + valuation routing); F23 is fully parameterized but blocked on the price-series fetch gap; F22 ships direction-only pending a leverage-share calibration note.*
