LECTURE: How to use Trading View (Part2)    REF: TVPD2    (transcript: 76123 chars, 800 lines, covered: yes)

## 1. CRUX

Teach the mechanics of building a live TradingView stock screener/watchlist —
combining moving-average trend context, ADX, RSI, volume, and a TradingView
technical-rating filter — to find current "pockets of strength" while
repeatedly warning that the entry system is technical-only and needs a
separate V-Stop-based exit discipline plus fundamental judgement layered on
top.

## 2. MECHANISM

- Establish trend context first with the 50-day moving average (daily) and
  30-week EMA (weekly): a stock trading below/falling away from it is in
  downtrend, one riding it or pulling back to it and turning up is in an
  uptrend — demonstrated live across pairs like Balaji Amines vs Alkyl Amines
  (TVPD2 00:03:52-00:04:46) and Westlife vs Devyani vs Jubilant Foodworks
  (TVPD2 00:06:23-00:07:08).
- Stocks in the same sector tend to move together ("factors move together
  right so always remember this that factors move together" TVPD2
  00:15:42-00:15:59) because they share business economics, so scanning by
  sector is itself a screening technique, and homework is to track how far
  sector-by-sector prices sit from their 50 DMA every six months (TVPD2
  00:12:01-00:13:00).
- ADX measures the average strength/persistence of directional price moves
  (green vs red candle closes averaged over time); above 20 signals the stock
  "has gotten onto momentum" (TVPD2 00:24:04), above 40-45 signals a
  "super performing stock" (TVPD2 00:24:25).
- RSI crossing above 50 flags "Something like fundamentally different is
  happening in this company." (TVPD2 00:36:01) and is the instructor's
  preferred entry trigger; RSI above 70-80 signals overbought / a likely
  near-term cooling-off, not a sell (TVPD2 00:35:39-00:36:19,
  01:15:25-01:15:29).
- The actual entry rule combines three legs, not two: "Entry gets triggered
  when your V stop is positive." (TVPD2 01:10:30), "Your RSI goes above 50,
  right?" (TVPD2 01:10:33), and "And your ADX goes above 20." (TVPD2
  01:10:35). V-Stop (Volatility Stop) — not ADX or RSI — is the instructor's
  stated exit tool: "we stop is to be used for a selling sign" (TVPD2
  00:32:13), explicitly because "ADX isn't to be used for a like a selling
  sign" (TVPD2 00:32:09) and "High RSI does not indicate an exit." (TVPD2
  01:15:25), "Exit has to be done on Vstop." (TVPD2 01:15:27).
- The screener itself is built live by stacking filters — "outperforming
  simple moving average 50" (TVPD2 00:33:58), ADX above 20, RSI above 50,
  "volume leaders" (TVPD2 00:37:56), then optionally the TradingView
  technical-rating bucket ("strong buy" narrows ~1000+ stocks to 219, TVPD2
  00:52:05-00:52:31) and fundamental filters (PE, ROE) layered on top of the
  technical ones.

## 3. SIGNALS

- [HARD] Weekly RSI crossing above 50 is an entry trigger — "if it just
  crosses 50, that is one of the points of time when one should definitely
  look at a stock" (TVPD2 00:35:49-00:36:01). Matches existing rule
  entry_rsi-001.
- [HARD] Weekly ADX above 20 signals the stock has entered momentum (TVPD2
  00:24:04-00:24:25). Matches existing rule entry_adx-001.
- [SOFT] V-Stop (Volatility Stop indicator, length 10, multiplier 2-3 per
  risk tolerance) being positive/trending is stated as a required THIRD leg
  of entry alongside RSI and ADX (TVPD2 01:10:30-01:10:35), and is the sole
  stated exit signal (TVPD2 00:32:09-00:32:13, 01:15:25-01:15:29). Not
  screener-derivable from ratios; needs a charting-indicator computation the
  ladder does not fetch.
- [SOFT] TradingView's proprietary technical-rating category ("buy"/"strong
  buy") is used to further tighten the filtered list (TVPD2
  00:52:02-00:52:31) — a third-party composite rating, not a raw price/volume
  series the ladder ingests.
- [JUDGE] RSI above 70-75-80 signals overbought and a likely near-term
  correction, explicitly NOT a sell signal: "High RSI does not indicate an
  exit." (TVPD2 01:15:25) — "the stock might pull off in the near term that
  is what it indicates" (TVPD2 01:15:29, corroborated 00:34:41-00:35:07
  re-CDSL). This is an interpretive qualifier on the RSI reading, not a
  fresh threshold.
- [SOFT] Abnormally high volume ("volume leaders" on weekly charts) is used
  as a standing filter for "which stocks are buying and selling" (TVPD2
  00:37:29-00:38:49) — needs relative-volume data the ladder does not fetch.
- [JUDGE] Sector-level relative strength (comparing same-store-sales growth
  or same-sector charts) is used to pick the strongest name within a weak
  sector, e.g. Westlife's 20% same-store-sales growth versus Devyani's 3% and
  Jubilant's 0.3% like-for-like growth (TVPD2 00:08:02-00:08:33) explaining
  why Westlife's chart held up better. This is fundamentals-informs-technicals
  judgement, not a computable rule.
- [JUDGE] Valuation is used only "to get an idea" (TVPD2 00:43:13) of "where
  will a particular stock go once a catalyst enters into play" (TVPD2
  00:43:17), attributed to Stanley Druckenmiller, never to time entry/exit
  by itself (TVPD2 00:43:01-00:43:33) — a philosophy statement, not a
  threshold.
- [SOFT] A supplementary fundamental filter is offered once, casually: "That
  P ratio of a stock should be below 30" and, in the same breath, "some
  people do not invest in a P stock which has a P ratio of more than 30
  times" (TVPD2 00:52:49) alongside "ROC or ROE of more than 14-15%" (TVPD2
  00:21:41-00:21:56) — the instructor frames both with "suppose"/"If we want
  to add" not as a mandatory bar.

## 4. WHAT THE LADDER MISSES

(b) The ladder has NO rule at all for V-Stop, despite this lecture stating it
is a required third leg of every entry ("Entry gets triggered when your V
stop is positive." TVPD2 01:10:30, "Your RSI goes above 50, right?" TVPD2
01:10:33, "And your ADX goes above 20." TVPD2 01:10:35) and the ONLY stated
exit mechanism in the entire technical framework (TVPD2 00:32:09-00:32:13,
01:15:25-01:15:29). Rules
entry_rsi-001 and entry_adx-001 currently stand alone as if RSI>=50 and
ADX>=20 were sufficient for an entry signal; per this lecture they are
necessary but explicitly not sufficient — V-Stop positivity is the third,
uncaptured condition, and it is also what should gate any exit trigger the
ladder might someday add (RSI/ADX going the other way is explicitly NOT a
sell signal per this lecture).

(b) This lecture directly qualifies entry_rsi-001 (RSI>=50) in a way the
current rule's display text doesn't capture: crossing above 50 is the entry
trigger, but RSI subsequently running high (70-80+) is reframed as an
overbought/cooling-off warning, NOT a signal to exit — "High RSI does not
indicate an exit." (TVPD2 01:15:25) "Exit has to be done on Vstop." (TVPD2
01:15:27).
If the ladder or any downstream consumer were ever to treat a fall in RSI
below 50 as a sell trigger, this lecture explicitly contradicts that.

(b) No rule captures "factors move together" (TVPD2 00:15:42-00:15:59) — the
instructor's stated core heuristic for using technicals sector-wide (scan a
sector, and if one name is showing strength, expect its peers'
charts/fundamentals to correlate). This is presented as a near-universal
observation ("write this down somewhere") but is JUDGE-tier, not a
computable screen.

(c) The PE<30 and ROE/ROC>14-15% fundamental add-ons (TVPD2
00:21:41-00:21:56, 00:52:47-00:52:49) are both introduced with "suppose"/"If
we want to add" hedges in a single live-screener demo — they read as
casual, of-the-moment screener choices during this webinar, not codified
thresholds. They roughly overlap the ladder's existing capital_efficiency_gate-001
(ROCE>=15) and pe_context-001 (15-35 band) observations already in the
rulebook, so this is corroboration at best, not a new bar, and the ladder
should not treat this lecture's "below 30" / "14-15%" as an independently
sourced threshold.

(c) The specific entry/exit price levels quoted for Laurus Labs (buy ~103,
sell at 530 rupees, TVPD2 00:27:54-00:28:09), Radico Khaitan-garbled
"Radhigo Khaitan" (entry 414, exit 960-970, TVPD2 01:06:30), Narayana
Hrudayalaya (forward PE 22, entry 690, TVPD2 01:05:42-01:05:58), and Avenue
Supermarkets/D-Mart (entry 1500, exit 3600-3700, TVPD2 00:44:35-00:44:46) are
all dated, single-company worked examples used to illustrate the V-Stop
mechanism — none are offered as universal price bars and none should be
encoded as thresholds.

No gate-level rule this lecture adds beyond what's above; the rest of the
lecture (watchlist creation, colour-coding by allocation size, CSV export,
Google Alerts for corporate-action tracking) is pure TradingView tooling
with no decision-relevant content for the ladder.

## 5. NAMED COMPANIES

- Balaji Amines, Alkyl Amines — paired 50-DMA demo; Balaji shown first, then
  Alkyl Amines introduced as the second comparison stock (TVPD2
  00:03:55-00:03:58), both illustrating "a clear downtrend" (TVPD2
  00:04:32-00:04:37) — negative/neutral teaching examples, not verdicts on
  either stock.
- Old-time transformer co., Shilchar Technologies, Apar Industries, Voltamp —
  grouped as still "showing strength" though Voltamp weaker ("I think volt
  amperage chart it is not as good the shilture and APAR industries." TVPD2
  00:06:00) — positive examples.
- Jubilant Foodworks, Devyani International, Westlife Foodworld — Westlife
  positive/outperforming (20% same-store-sales growth, 16% peak-to-trough
  drawdown), Devyani negative (3% growth, ~30% drawdown), Jubilant most
  negative (0.3% like-for-like growth, ~50% drawdown from 881 to ~441, TVPD2
  00:08:02-00:09:26).
- Sudarshan Chemicals — negative example, moving average "going down over a
  period of time" (TVPD2 00:10:00-00:10:41).
- Gujarat Fluorochemicals — turning-positive example: fell from ~4,000 to
  ~2,600 then "the 50-day moving average has basically stabilized... started
  pointing upwards" (TVPD2 00:10:51-00:11:04).
- Navin (Navin Fluorine — appears as both "Navin" TVPD2 00:11:09 and garbled
  "Navin Florin" [likely "Navin Fluorine"] TVPD2 00:24:32) — positive
  example, 50 DMA "more or less being respected by the business" (TVPD2
  00:11:09-00:11:26). **In the 38-name shortlist (NAVINFLUOR).**
- SRF — neutral, described as in "a sideways trend" Oct 2021-Mar 2023 (TVPD2
  00:11:26-00:11:43). Not in the 38.
- KEI Industries, Polycab ("poly cap"), Finolex ("phenol X") — grouped cable
  & wire strength examples (TVPD2 00:13:43-00:14:21). **Polycab is in the
  38-name shortlist.** KEI Industries reappears later as a detailed positive
  ADX/V-Stop worked example (TVPD2 00:26:16-00:27:35).
- Laurus Labs ("Laura's labs"/"Laura Slabs") — cited twice: once among
  businesses whose ADX "remained above 40 to 45 for a period of time and
  then it started going down" (TVPD2 00:24:32), and once as the specific
  V-Stop worked example where "He lost major cell top that got triggered at
  530 rupees" after entry near 103 (TVPD2 00:27:40-00:28:09) — cautionary/
  exit example, not an endorsement of current momentum. **In the 38-name
  shortlist (LAURUSLABS).**
- Sequent (life sciences peer group) — mentioned only as an "also" chart
  comparison alongside Laurus, no independent verdict (TVPD2 00:15:19-00:15:31).
- Aztec Life Sciences — negative fundamental example: "The path has gone
  from almost 18 crore to 85 lakh rupees, right?" [likely "PAT"] (TVPD2
  00:18:21), and EBITDA fell 33cr to 12cr in a quarter (TVPD2
  00:18:17-00:18:30).
- Anthem Biosciences (garbled "Then simply says code." TVPD2 00:16:46,
  "That is in my industries." TVPD2 00:16:47) and Bharat Rasayan ("Bharath
  Rasai") — mentioned as chart-only observation targets with no stated
  verdict (TVPD2 00:16:36-00:17:05).
- PI Industries — positive: "The Pat has gone from 1 to 11 cr to 352 cr."
  (TVPD2 00:17:54), consistent 18%/30%/16%-range growth since 2019 (TVPD2
  00:17:16-00:17:59).
- Hiranba ("Hiramba") — negative: "margins have gone for a toss" (TVPD2
  00:17:59), PAT 48cr
  to 14cr (TVPD2 00:17:59-00:18:04).
- Pricol ("Precall") — positive: "showing immense strength versus the rest
  of the auto pack" (TVPD2 00:18:41-00:19:09).
- Shivalik Bimetal — positive but weaker slope than Pricol (TVPD2
  00:19:15-00:19:30).
- Craftsmen Automation — positive: "showing immense strength" (TVPD2
  00:19:34-00:19:40).
- CCL Products — detailed positive worked example: 30-week EMA pointing up,
  weekly RSI above 50, ADX above 20 all confirmed live as the entry criteria
  triggering around 53-54 rupees (TVPD2 00:39:54-00:48:47).
- Avenue Supermarkets (D-Mart) — cautionary valuation example: "people were
  buying at 200 PEOP" [likely "200 PE"] (TVPD2 00:42:09), entry cited at
  1500, V-Stop exit at 3600-3700 (TVPD2 00:42:42-00:44:46) — used to argue
  exits must stay disciplined even on admittedly overvalued long-term
  compounders.
- CDSL — overbought/correction example: RSI above 70 preceded "two weeks or
  three weeks maximum correction" and then "stock price double even from
  there" [likely "doubled"] (TVPD2 00:34:41) — mixed, not a negative
  verdict.
- Equitas Small Finance Bank — positive, instructor discloses ownership
  ("this will start coming over here because the reverse merger is happening
  and micro finance cycle is playing out" TVPD2 00:55:28).
- Godfrey Phillips, APL Apollo, KSB Pumps ("KSV pumps"), Sera Sanitaryware
  ("Sera Sanitary where") — named only as names appearing in the live
  screener output, no individual verdict given (TVPD2 00:45:12-00:45:20).
- ISMT — positive fundamental+technical overlap: merger between two entities
  and steel capacity doubling cited as the reason it shows up in the
  screener (TVPD2 00:54:01-00:54:48).
- Kovai Medical Center — positive: debt reduction plus a medical college
  contributing to revenue (TVPD2 00:54:48-00:55:11).
- Gujarat Gas, IGL, MGL — grouped positive on a gas-price-reform tailwind,
  "margins will reward back to mean" (TVPD2 00:53:55-00:53:58).
- Wonderla / an amusement-park business referred to as "magic world" —
  turnaround/mixed example: "went under debt restructuring" (TVPD2 00:56:01),
  amusement parks sold, new owner, "debt restructuring has happened" (TVPD2
  00:56:01-00:56:21).
- Narayana Hrudayalaya — detailed positive fundamentals+technicals worked
  example: forward PE ~22, "30% ROE, 25% ROC, forward at 22p." (TVPD2
  01:05:50), entry 414/690, exit 960-970, re-entry noted (TVPD2
  01:05:29-01:06:29).
- Radico Khaitan (garbled "Radhigo Khaitan") — positive: entry 414, exit
  960-970, then re-entered (TVPD2 01:06:29-01:06:53).
- Sterling Tools — named only as a "stage two" list example, no verdict
  (TVPD2 00:39:46-00:39:52).
- Relaxo Footwear ("relax") — negative worked example: two V-Stop sell
  signals in six years, margin contraction, rising rubber/input prices,
  falling ROC/ROE, and the instructor's rhetorical question "was it cheap to
  start with or was it an expensive stock" (TVPD2 00:31:32) implying it was
  expensive (TVPD2 00:29:44-00:31:47).
- South Indian Bank — mixed: instructor discloses ownership, RSI above 70
  preceded "some correction" / "cooling off in the near term" (TVPD2
  01:14:19-01:14:54).
- HDFC Bank — positive long-horizon example: "last 25 years may there have
  been only two cell signs which got triggered that too during a great
  crisis" on monthly V-Stop (TVPD2 01:19:16).
- Jindal Stainless — mentioned only re: tracking corporate-action news (a
  merger), no chart/investment verdict given (TVPD2 01:09:00-01:09:09).
- Nvidia — mentioned only in passing: "Nvidia may we stop recently got
  triggered." (TVPD2 01:21:15), "it looks very interesting." (TVPD2
  01:21:17), no verdict given.

## 6. AGAINST THE 38

- NAVINFLUOR — specific support: cited as a positive 50-DMA-respecting
  example in the fluorination sector (TVPD2 00:11:09-00:11:26), and again
  among businesses whose ADX "remained above 40 to 45 for a period of time"
  (TVPD2 00:24:32-00:24:46, garbled "Navin Florin"). Real verdict, not a bare
  mention.
- POLYCAB — specific support, grouped with KEI Industries and Finolex as a
  cable-and-wire-sector strength example (TVPD2 00:13:43-00:14:21). A brief
  positive mention (part of a 3-company group observed together), not a
  detailed worked example — weaker support than NAVINFLUOR.
- LAURUSLABS — specific doubt raised, not support: cited as an ADX momentum
  name that "started going down" (TVPD2 00:24:32-00:24:46), then used as the
  worked example for where a V-Stop SELL was triggered at 530 rupees after
  entry near 103 (TVPD2 00:27:40-00:28:09) — i.e. this lecture's own
  technical framework says Laurus Labs was a stock to have already exited,
  not one to be freshly screening into today.
- FLUOROCHEM (Gujarat Fluorochemicals) — specific support: cited as a
  stabilizing/turning-up 50-DMA example after a fall from ~4,000 to ~2,600
  (TVPD2 00:10:51-00:11:04).
- All other 34 names in the shortlist: none.
