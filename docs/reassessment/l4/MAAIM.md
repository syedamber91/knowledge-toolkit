LECTURE: Moving Averages, ADX, RSI, Comparative Strength    REF: MAAIM    (transcript: 33550 chars, 322 lines, covered: yes)

## 1. CRUX

To teach the long-term investor how to read ADX (average directional index)
as a trend-strength filter — always paired with the "volatility stop"
trailing-stop tool from the prior class — for timing WHEN to enter a
fundamentally-selected stock, and to warn that it should NOT be relied on
alone to decide when to exit.

## 2. MECHANISM

- ADX is built from comparing each candle's high/low to the previous
  candle's: a higher high than the prior candle's high registers positive
  direction (+DI); a higher low than the prior candle's low registers
  negative direction (-DI) (MAAIM 00:02:36-00:03:51).
- "simply ADX formula is direction upon, direction upon volatility" — DX is
  the absolute difference between D plus and DI minus, and ADX is DX's own
  moving average, not a price moving average (MAAIM 00:04:07, MAAIM
  00:04:20-00:04:29).
- Reading bands are stated inconsistently across the lecture: at one point
  "whenever your ADX is between 0 to 25, so it means the trend is absent or
  it's a weak trend. Whenever the ADX crosses 25, it is known as a strong
  trend" (MAAIM 00:06:00-00:06:10); moments later, "Many people believe that
  if it is 0 to 20, even if it is 20, then again the trend starts picking
  up" (MAAIM 00:06:16); 50-75 is "very strong trend" and 75-100 "extremely
  strong trend" (MAAIM 00:06:21-00:06:30).
- ADX is explicitly framed as reliable only for entries, and only in
  combination with the volatility-stop indicator: "you have to combine
  volatility stock with ADX otherwise it won't be of a use because ADX in
  itself won't give you any right conclusiveness whether you buy the stock
  or not" (MAAIM 00:22:33). Separately: "ADX is a very good buy indicator,
  but ADX is not a good sell indicator" (MAAIM 00:12:50).
- Timeframe (weekly vs. monthly) and the volatility-stop ATR multiplier
  (lower for cyclicals, higher for compounders) are chosen per stock, not
  fixed — demonstrated with IIFL Finance, where the weekly-chart "price was
  close to 353" (MAAIM 00:24:49) but on the monthly chart "your entry comes
  close to 270 to 290 rupees" for the same stock (MAAIM 00:24:57); and "for
  compounded business, you can use volatility stop as 2.5 and for cyclical
  businesses volatility stop at 2" (MAAIM 00:27:33).
- Taught almost entirely through ~16 live TradingView chart walk-throughs of
  named stocks, matching an ADX cross of 20 or 25 against the stock's actual
  subsequent price move.

## 3. SIGNALS

[HARD] ADX crossing 20 is used by the instructor as one entry trigger in
several worked examples (Bansali Engineering Polymers, Deepak Fertilizers,
Equitas Small Finance Bank, Narayana) — "your directional index is trending
positive and adx has finally crossed 20" (MAAIM 00:10:55).

[HARD] ADX crossing 25 is used as an alternative, and per the instructor
more reliable, entry trigger in other worked examples (Navin Fluorine,
Reliance, HEG) — "25 will get you absolutely in the super trending zones
where the stock starts trending again" (MAAIM 00:13:33). The instructor
never resolves the 20-vs-25 choice to one fixed number within this lecture.

[JUDGE] Using 20 rather than 25 as the entry cutoff is explicitly flagged as
noisier: "adx above 20 is also very good indicator so you can either use 25
or 20 but 20 may be more than above or below" and "it could also be a
Wipsov [likely "whipsaw"] type meaning above or below" (MAAIM
00:21:41-00:22:22).

[SOFT] ADX alone is stated as insufficient for a buy decision — it must be
combined with the volatility-stop indicator (an ATR-based trailing stop the
ladder does not compute) (MAAIM 00:22:33, quoted above).

[JUDGE] ADX should not be used to decide exits — "ADX is a very good buy
indicator, but ADX is not a good sell indicator because sometimes when the
entire ADX came below 20, it was up to 13. Whereas, your 20 rupees, almost
180, so your 60 rupees, so your gain was only 2-3 baggers, which would have
been 8 baggers originally" (MAAIM 00:12:50-00:13:07) — i.e. waiting for ADX
itself to weaken to exit Bansali would have given a materially worse result
than the volatility-stop exit actually used.

[JUDGE] Timeframe (weekly vs. monthly) is chosen per stock's character
(cyclical, thin listing history, or compounder), not fixed to one
timeframe — e.g. Syngene: "we can also use this idea of weekly candles as
well" (MAAIM 00:14:41); Deepak Fertilizers: "because it's the cyclical
business preferably I'll use weekly because these cycles they last anywhere
between 6 to 9 months" (MAAIM 00:26:26); IIFL Finance shown on both weekly
and monthly with different entry prices (MAAIM 00:24:49-00:24:57).

[JUDGE] Position sizing is reduced during prolonged consolidation ahead of
an ADX breakout: "when the massive consolidation is going on, I actually
have low allocations in such businesses because I have my money in, so we
are tracking it" (MAAIM 00:16:32).

[SOFT] A fundamental catalyst (an operating-leverage inflection) is cited
as the reason to keep watching a stock through consolidation rather than
walk away — Syngene: "Fundamentally also, Singeen Kendal operating leverage
will be playing out." (MAAIM 00:15:33), and separately, "That is what the
bet of a Singeen investor is today." (MAAIM 00:15:37).

No RSI signal, no comparative-strength signal, and no price-based
moving-average rule appear anywhere in this transcript — see Section 4.

## 4. WHAT THE LADDER MISSES

(a) Conditions on `entry_adx-001` (gate G8, weekly ADX >= 20):

  1. Per this instructor's own practice, 20 is the noisier of the two
     thresholds he actually uses. He treats 20 and 25 as interchangeable
     across different worked examples but explicitly warns 20 is more prone
     to false/whipsaw signals than 25 (MAAIM 00:21:41-00:22:22, quoted
     above). The ladder encodes only the looser, more whipsaw-prone bound
     (>= 20) as its fixed rule, with no alternative >= 25 reading and no
     acknowledgment that the instructor himself flags 20 as noisier.
  2. More fundamentally, this lecture states plainly that ADX by itself
     "won't give you any right conclusiveness whether you buy the stock or
     not" (MAAIM 00:22:33) — it must be combined with the volatility-stop
     indicator. The ladder's G8 gate fires on weekly ADX >= 20 alone (paired
     only with weekly RSI >= 50, an unrelated indicator never discussed in
     this lecture), with no volatility-stop metric anywhere in the
     16-rule rulebook. Per this lecture, that is exactly the "not enough
     for conclusiveness" configuration the instructor warns against.
  3. The lecture also states ADX should never drive an exit decision (MAAIM
     00:12:50-00:13:07). This doesn't directly conflict with the ladder,
     since G8 is entry-only — but it does mean any future extension of G8's
     logic to an exit rule would directly contradict this lecture's central
     warning.

(b) `entry_rsi-001` (gate G8, weekly RSI >= 50) — a title/content mismatch
worth stating plainly rather than manufacturing a finding: this lecture's
own title promises RSI content — "we will talk about RSI in more detail
along with ADX" (MAAIM 00:00:16) — but the transcript contains no RSI
discussion anywhere after that one-line promise: no threshold, no
mechanism, no worked example. A full-transcript search for "RSI" turns up
only the intro promise and one aside naming Wilder as its inventor (MAAIM
00:01:19). The ladder's actual `entry_rsi-001` provenance already points to
a different lecture (HOWB), so this is not a contradiction of that rule —
but it means the one lecture titled specifically to cover RSI supplies zero
supporting or qualifying evidence for it, which is worth surfacing given the
note's instruction to check whether this lecture bears on the ladder's only
two G8 rules.

(c) Central points with no ladder rule at all:

  - Timeframe choice (weekly vs. monthly) materially changes the entry
    price/signal — demonstrated concretely with IIFL Finance: on the weekly
    chart, "price was close to 353" (MAAIM 00:24:49); on the monthly chart,
    "your entry comes close to 270 to 290 rupees" for the same stock (MAAIM
    00:24:57) — and the instructor picks the timeframe per stock's business
    type rather than using one timeframe universally. The ladder's G8 rule
    is hardcoded to "weekly" with no monthly alternative and no
    business-type-dependent selection.
  - The "volatility stop" indicator (an ATR-based trailing stop, sized
    1.5-2x for cyclicals vs. 2.5x for compounders) is presented throughout
    as ADX's mandatory co-signal for entries and the sole tool for exits.
    The ladder has no volatility-stop metric and no rule of any kind sourced
    to it.
  - Consolidation-driven position sizing (low allocation while waiting for
    an ADX breakout, MAAIM 00:16:32) — no ladder rule touches position
    sizing.

(d) Dated one-company worked examples mistaken for universal bars: none
found. The specific rupee levels quoted for Bansali Engineering Polymers
(27 -> 187), Navin Fluorine (118 -> 802 -> 1372), HEG (~205 -> ~3600-3700),
etc. are presented as illustrative outcomes of applying the ADX+
volatility-stop system, not as thresholds or bars to clear — so there is
nothing here at risk of being misread as a universal number.

## 5. NAMED COMPANIES

- Bansali Engineering Polymers — positive. First worked example: ADX
  crossed 20 alongside a volatility-stop buy signal near 27 rupees, ran to
  almost 187 rupees, "close to a 87 to 8 bagger" [likely "almost an 8
  bagger"] before ADX (used alone) would have given a delayed, worse exit
  than the volatility stop actually used (MAAIM 00:08:09-00:13:07). Not in
  the 38.
- Navin Fluorine (transcript: "Navin Florin"/"Naveen Florin") — positive.
  Bought near 118 rupees in 2014 on ADX+volatility-stop signal, ran to
  "almost a journey of like almost a journey of 802" (MAAIM 00:13:57),
  re-entered on a later ADX-crosses-25 signal, and as of the stated
  recording date ("1st February," no year given) the stock was at 1372
  with "currently there is no sign of exit and we are just patiently
  riding" (MAAIM 00:14:20). In the 38 — see Section 6.
- Syngene (transcript: "Xinjin"/"Singeen"/"Xinjiang") — neutral/watching.
  In ~22 months of consolidation with ADX not sustaining above 25; the
  instructor holds a low allocation pending both an ADX breakout and an
  operating-leverage catalyst playing out fundamentally (MAAIM
  00:14:37-00:16:41). Not in the 38.
- Reliance Industries — positive. Monthly-candle consolidation breakout
  above 25, entry near 601, held to "almost close to like 600 till today
  that is 2600" (MAAIM 00:17:31). Not in the 38.
- Gujarat Ambuja Exports (transcript: "Gujarat and Buja exports limited") —
  cautionary/negative. Cited as a business hit by rising input (maize)
  prices, forming lower highs, stopped out by the volatility stop (MAAIM
  00:18:07-00:19:11). Not in the 38.
- Aarti Industries (transcript: "arathi industries") — mixed. Held from
  ~23 rupees since 13 November as a "super trending stop," but ADX and the
  directional index turned negative and the volatility stop gave an exit
  near 767-770 (MAAIM 00:20:16-00:20:59). Not in the 38.
- Deepak Nitrite (transcript: "debug nitrite") — used to illustrate the
  ADX+volatility-stop combination generally; volatility stop hit near
  1960-1967 (MAAIM 00:21:30-00:22:44). Not in the 38.
- HEG — positive, cyclical example. ADX crossed 24-25 with a volatility-stop
  buy near 200-205 rupees, ran up before exiting near 3600-3700 when ADX
  fell below 20 (MAAIM 00:22:44-00:24:12). Not in the 38.
- IIFL Finance (transcript: "IFL finance") — positive. Shown on both weekly
  (price "close to 353," MAAIM 00:24:49) and monthly ("entry comes close to
  270 to 290 rupees," MAAIM 00:24:57) timeframes to illustrate that
  timeframe choice changes entry price. Not in the 38.
- Equitas Small Finance Bank — positive/emerging. "now only now your ADX
  has crossed 20 comprehensively," weekly chart, near 56 rupees, volatility
  stop also turning up (MAAIM 00:25:18). Not in the 38.
- Surya Roshni — no signal yet. ADX still below 20 despite the directional
  index turning positive; instructor explicitly withholds a buy call:
  "currently your adx is not telling you to buy it because it hasn't
  crossed 20" (MAAIM 00:26:15). Not in the 38.
- Deepak Fertilizers — positive, cyclical example on weekly chart. Buy at
  ADX-crosses-20 near 220 rupees, volatility stop currently trailing at 711
  (MAAIM 00:26:26-00:27:20). Not in the 38.
- Ramkrishna Forgings (transcript: "Ramakrishna forging's") — homework
  suggestion only, no verdict given (MAAIM 00:28:28-00:28:35). Not in the
  38.
- Vinati Organics (transcript: "Vinnitya Organics") — homework suggestion
  only, no verdict (MAAIM 00:28:35-00:28:41). Not in the 38.
- Sun Pharma — homework suggestion only, no verdict (MAAIM 00:28:41-00:28:47).
  Not in the 38.
- Rainbow Children's Medicare (transcript: "Rainbow Hospital") — homework
  suggestion, noted only as "a new entry" (recently listed), no verdict
  (MAAIM 00:28:56-00:29:00). Not in the 38.
- Narayana Hrudayalaya (transcript: "Narayana") — positive. Broke out of
  consolidation with ADX above 20, still trending with monthly ADX "at 60
  61," entered near 433 (MAAIM 00:29:00-00:29:33). Not in the 38.

## 6. AGAINST THE 38

Only NAVINFLUOR appears among the 38, and this lecture is a real,
substantive verdict for it, not a bare mention: it is walked through as a
full worked example of the ADX+volatility-stop entry system working —
bought near 118 rupees in 2014, ridden to 802, re-entered on a later ADX
cross above 25, and "there is no sign of exit and we are just patiently
riding" as of the stated recording date (MAAIM 00:14:20). This is
consistent with, but adds nothing beyond, the ladder's own already-passing
computed values for NAVINFLUOR (weekly RSI 75.56, weekly ADX 46.58, both
comfortably above the G8 thresholds). Two caveats worth carrying forward:
the "no sign of exit" state is dated to whenever this lecture was recorded
(no year is given in the transcript), not to today, and it is a specific
historical price journey, not a restatement of any general rule — so it
should be read as illustrative support, not fresh confirmation.

No other of the 38 is named anywhere in this transcript, so this lecture
raises no doubt about, and offers no support for, any of the other 37.
