LECTURE: How Relative Strength combined with VStop used to buy stock!    REF: RSCAR    (transcript: 20290 chars, 185 lines, covered: yes)

## 1. CRUX

This lecture is trying to change WHEN you pull the trigger on a buy (and
when you add to a winner), not what you buy — it teaches a three-signal
confluence (Relative Strength divergence + VStop turning up + rising
volume) as the technical confirmation to time an entry into a stock whose
fundamentals you already like.

## 2. MECHANISM

- Relative Strength (RS) is defined as identifying assets that "have
  performed relatively better than the other market or the relevant
  benchmark" (RSCAR 00:00:29) — computed on TradingView via the
  "comparative relative strength" (CRS) indicator plotted against a chosen
  benchmark (an index, or another stock).
- The buy signal is a three-part confluence, stated explicitly: "you can
  club the divergence of relative strength along with volumes along with V
  stop trending upwards right so these three things can be used for
  buying" (RSCAR 00:05:59) — and in the same breath he states this
  combination is purely a buy tool: "this is just an indicator of buying"
  (RSCAR 00:05:59).
- Sell/exit logic is handled by a separate tool: "For selling, I think
  Vstop works, but for buying, you can pyramid up using relative strength."
  (RSCAR 00:10:26) — i.e. RS is framed as the add-to-position / entry-timing
  layer, VStop alone as the exit tool.
- He frames three interchangeable (OR'd) entry-confirmation recipes, not
  one mandatory combined test: "either you can follow a mix of Vstop along
  with relative strength or you can just follow relative strength or you
  can just follow Vstop when it starts trending along with ADX." (RSCAR
  00:13:15).
- RS is pitched as a timing layer on top of an already-identified value or
  fundamentally-improving pick, for "whenever you are looking for basically
  the mean reversion strategies, now you have identified a value stock but
  you want to buy it when the basically business starts improving,
  fundamental start improving and also the technical start improving."
  (RSCAR 00:07:42).
- Two further, independent uses of RS are demonstrated: (1) stock-vs-stock
  comparison (not just stock-vs-index) to spot possible sector leadership
  changes, and (2) a StockEdge screener filter ("strongly outperforming
  benchmark index", "increasing relative strength") to source candidates,
  with an optional price/CRS-crossing alert.

## 3. SIGNALS

- [JUDGE] A stock's RS line diverging upward through its benchmark line,
  combined with VStop turning up/no-sell and rising volume, is read as a
  buy point — "these three things can be used for buying" (RSCAR 00:05:59).
  This is a discretionary, chart-read confluence call, not a single
  computable threshold.
- [SOFT] VStop (volatility-stop) — its trend state ("green"/"no sell")
  drives the buy/hold/sell read throughout this lecture (Equitas, South
  Indian Bank, SRF, Dixon, PB FinTech). It is a trailing-stop indicator
  computed from price action; nothing in the current rulebook computes it.
- [SOFT] Comparative Relative Strength (CRS) vs a benchmark index or vs a
  peer stock — needs a relative price-ratio series against a chosen
  benchmark, which the ladder does not currently construct.
- [SOFT] Rising/high trading volume as a confirming leg of the buy signal —
  the rulebook's own observations note volume/mix data is not fetched.
- [JUDGE] Stock-vs-stock RS crossover (e.g. HDFC Bank vs ICICI Bank) read
  as a possible "leadership shifting" event (RSCAR 00:15:23) — an
  interpretive call about competitive dynamics, not a fixed rule.
- [SOFT] Persistent multi-period membership in a "strongly outperforming
  benchmark index" screener (his examples: Varun Beverages, Carborundum
  Universal) is treated as a positive signal of durable outperformance —
  this needs historical screener-membership tracking, which the ladder does
  not have.
- [JUDGE] When a long-standing outperformer flips to underperformance
  (SRF vs Nifty 50, after "outperforming Nifty for a lot of years, I think
  since 2018 till 2022, now SRF has started underperforming Nifty after
  four years of outperforming" (RSCAR 00:09:03)), that is read not as a
  sell but as "a period of time where the stock could ideally go under a
  period of consolidation" (RSCAR 00:09:16) — a judgment call about the
  difference between trend exhaustion and a pause, not a hard rule.

## 4. WHAT THE LADDER MISSES

(b) Central points with no rule at all — this is the dominant finding here:

- VStop (volatility stop) is the primary buy/sell trend tool this whole
  lecture is built around (used across every named example — Equitas,
  South Indian Bank, SRF, Dixon, PB FinTech) and the rulebook has no rule
  or observation for it anywhere. Given VStop is treated by the instructor
  as co-equal with (or, in some framings, prior to) RSI/ADX for entries,
  this is a real gap, not a peripheral miss.
- Comparative Relative Strength vs benchmark (or vs a peer stock) as a
  timing/screening signal has no rule. The ladder's only technical entry
  rules are entry_rsi-001 and entry_adx-001 (weekly RSI>=50, weekly
  ADX>=20, sourced from a different lecture, HOWB). RSCAR never once
  mentions RSI in its own entry recipes — see (a) below.
- Volume confirmation as a leg of an entry signal is entirely absent from
  the rulebook, consistent with the observations' own note that volume/mix
  isn't fetched.
- The "wait for technical confirmation on an already-identified value pick"
  philosophy (RS+VStop as a timing layer sitting on top of fundamentals,
  not a standalone screen) has no rule capturing that sequencing idea.
- Pyramiding logic (add to a winner when RS resumes outperformance after a
  pause, per the SRF example) has no rule anywhere — the rulebook is
  entirely entry/exit-gate shaped, with no "add to an existing position"
  concept at all.

(a) A rule the ladder encoded that this lecture qualifies:

- entry_adx-001 / entry_rsi-001 (G8, jointly gating on weekly RSI>=50 AND
  weekly ADX>=20, sourced from HOWB) is implicitly narrowed by this
  lecture's framing that entry confirmation is a menu of three alternative,
  OR'd recipes — "Vstop along with relative strength", "relative strength"
  alone, or "Vstop... trending along with ADX" (RSCAR 00:13:15) — and RSI
  does not appear in any of the three. This doesn't contradict G8's RSI+ADX
  combination outright (RSCAR never says RSI is wrong), but it shows the
  instructor does not treat RSI+ADX as the sole or mandatory entry test
  elsewhere in the course — it is one path among several, and his own two
  preferred paths here are RS-based and use neither RSI nor ADX alone as
  the trigger.

(c) A dated/tool-specific number that should NOT be read as a universal
threshold: the StockEdge screen he demos filters on "relative strength
going above like going above zero" (RSCAR 00:11:13) over "the over last 55
days" (RSCAR 00:11:34). That zero-cutover and 55-day lookback describe a
specific third-party screener's default settings during the recording, not
a bar he is teaching as a rule to encode.

## 5. NAMED COMPANIES

- Equitas Small Finance Bank vs Bank Nifty — POSITIVE worked example: RS
  diverged upward, VStop triggered a buy, volumes were high, around the
  time its MD-resignation overhang cleared (RSCAR 00:03:08-00:05:56). Not
  in the 38.
- South Indian Bank vs Bank Nifty — POSITIVE, same three-signal confluence:
  "this was the point of time according to both relative strength Vstop
  and high volumes during this time frame where the purchase could have
  been made." (RSCAR 00:06:50). Not in the 38.
- SRF vs Nifty 50 — MIXED/CAUTION example: outperformed Nifty for years,
  "since 2018 till 2022" (RSCAR 00:09:03), then started underperforming;
  framed as a likely consolidation phase and used to illustrate setting a
  pyramid-up alert for when RS resumes, not treated as a sell (RSCAR
  00:08:34-00:09:48). Not in the 38.
- Dixon Technologies — NEGATIVE/exit example: "reverse DCF and everything
  triggered an exit and you just see that we stopped triggered an exit."
  (RSCAR 00:10:04); "It started underperforming Nifty massively." (RSCAR
  00:10:10); with high selling volume and the reverse DCF implying the
  stock was pricing in "next 15 to 20 years of growth." (RSCAR 00:10:15).
  Not in the 38.
- Jindal Stainless — mentioned only as a name currently surfacing on the
  "strongly outperforming benchmark index" StockEdge screen (RSCAR
  00:11:52) — a bare screen mention, no evaluation given. Not in the 38.
- Mahindra CIE Automotive (transcript: "Mahindra CI auto") — mentioned as
  appearing on the same screen "for a lot of time now because it's an MNC"
  (RSCAR 00:11:52) — bare screen mention. Not in the 38.
- PB FinTech (PolicyBazaar) — MIXED/near-positive worked example: weekly
  VStop trending, and RS "outperforming nifty first time ever since
  listing" (RSCAR 00:12:16) on weekly and monthly charts, but explicitly
  flagged as "still not a buy because V-stop on a monthly basis hasn't
  given a buy signal" (RSCAR 00:13:04) — a partial-confirmation case, not a
  completed buy signal. Not in the 38.
- Varun Beverages — POSITIVE: "Varun Beverage is I think for last two,
  three years has been coming in this screen and you can always see that
  the business has been doing well." (RSCAR 00:13:51). Not in the 38.
- Carborundum Universal (transcript ASR: "Carbohydrate Universal" [likely
  "Carborundum Universal"]) — POSITIVE-leaning: "recently also covered
  Carbohydrate Universal on our channel." (RSCAR 00:14:02), and "That is
  also coming for a long period of time." (RSCAR 00:14:05) on the same
  outperformance screen — no fundamental evaluation given, just persistence
  on the RS screen. IS in the 38-name shortlist as CARBORUNIV (WATCH, fails
  G3 ROCE at 10.50%).
- HDFC Bank vs ICICI Bank — a comparison example, not a buy/sell call: HDFC
  Bank resumed outperforming ICICI Bank "after a period of 2 years" (RSCAR
  00:14:49), read as possibly "a point of again leadership shifting" (RSCAR
  00:15:23). Neither is in the 38.

## 6. AGAINST THE 38

Only one overlap: CARBORUNIV (Carborundum Universal). The lecture gives it
a mild, non-fundamental point of technical support — sustained presence on
the "strongly outperforming benchmark index" RS screen, described as
"coming for a long period of time" (RSCAR 00:14:05) — but this is thinner
than the endorsement given to Varun Beverages, where he explicitly adds
that "the business has been doing well" (RSCAR 00:13:51); for Carborundum
he only asserts screen persistence, not a business-quality judgment. This
is a real, if modest, point of technical support — he singles it out by
name and by duration, not a bare mention in a peer list — but it says
nothing about the ROCE shortfall driving its current WATCH verdict, so it
neither resolves nor contradicts that verdict, only adds an unmodeled
technical tailwind alongside it.

No other name in the 38 is raised, supported, or doubted by this lecture.
