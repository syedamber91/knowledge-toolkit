# L5 Synthesis — "How to Screen & Filter Epic Stocks" vs the soic-ladder

Sources: SDBES, SIBES, LSARL, TFELT (all 4 briefs passed the quote gate at 100%).
Cross-reference: the Crash Course reader (FESTF) independently reconstructed the same
combined screen; convergence noted where it matters.

## 1. The through-line

Level 5's argument is not "here are thresholds." It is: **you cannot read 5000
companies, so use screens to decide which ~50 deserve reading time — then read.**
Every lecture ends at the same place: a screen hit is a question, never an answer.
TFELT states it as doctrine — "even screening process is probabilistic, there is
nothing certain in investing" (TFELT 00:30:44) and "Once we have a strong growth
rate, we will start reading after that" (TFELT 00:32:35-00:32:50). SDBES makes
reading the concall the third, non-optional step of its "three step framework"
(SDBES 00:39:01-00:39:09). SIBES frames screeners as tools "before we go towards
manual tools" (SIBES 00:06:29). LSARL orders it: framework → filter → "then you get
an idea which stock to study" → checklist → picking (LSARL 00:02:48-00:02:55).

The causal engine behind every screen is **inflection, not level**: something NEW
(product, geography, client, capex, acquisition) produces an earnings break, money
flows in ahead of full pricing, and "fundamentals have a momentum" — good quarters
persist "60-70% of the time" (TFELT 00:11:06). The screens are different lenses on
catching that inflection early. The ladder, by contrast, tests levels.

## 2. The screen he actually teaches, reconstructed

### The base quantitative screen (TFELT — the ladder's own origin)

The G0 provenance is confirmed and sharpened: the MASTEC 00:09:35 quote is
**word-for-word identical to TFELT 00:09:35** — this lecture (or a re-run of the
same script) is the true source. And at source, the screen is **one combined
four-part query, never two growth bars alone**:

> "Basically year on year quarterly sales growth of more than 15% Year on year
> quarterly profit growth of more than 20% ROC of more than 15% and market cap of
> more than 1000kroners." (TFELT 00:23:47)

with two attached scopes stated in the same breath:
- **ROC carve-out:** "ROC criteria can be removed from some people where the
  company is inflecting from the turnaround" (TFELT 00:42:09).
- **Market-cap tiering:** 1000cr default for liquidity; 500cr/100cr looser tiers
  explicitly riskier — sub-100cr names have "very negative cash loads or poor
  business models" (TFELT 00:42:15).
- **Optional stringency dial:** PE < 40 as a fifth filter "if you want to make it
  more stringent" (TFELT 00:42:15) → 63 names.

FESTF independently reconstructed the identical four-part query including the
market-cap floor and the turnaround carve-out. Two independent lectures, same
combined screen. The ladder encoded 2 of its 4 legs as G0, moved the ROC leg to a
separate gate (G3) without the turnaround waiver, and dropped the market-cap floor
entirely.

### The confirmation and entry layers

- **Relative strength vs index** (NOT RSI — "relative strength and RSI are two
  different terms," TFELT 01:52:40) making a 52-week high is "the holy grail of all
  screens" (TFELT 01:11:03), lookbacks 13/26/52 weeks. The ladder has no RS metric.
- **30-week EMA**: SIBES uses price ≥ 30-week EMA as a **third co-equal entry
  filter** alongside ADX>20 and weekly RSI>50 — "These all three are momentum
  indicators because it is just entering stage 2" (SIBES 00:04:22). LSARL uses the
  same line as the **stage-4 exit/avoid trigger**: the ideal investor sell is "when
  the stock goes below, it's 30 weekly moving average" (LSARL 00:26:07). Same
  period (30 weeks, weekly chart), both directions: above = stage-2 entry
  condition, below = falling-knife avoidance. The ladder has no moving-average
  rule anywhere.
- **Industry stage precondition** (SDBES): check the industry's own index is in
  stage 2 / at highs BEFORE screening names inside it (SDBES 00:09:53-00:10:00).
- **Sponsorship**: FII+DII stake change ≥2% (SDBES 01:00:20; TFELT's recipe
  2-3% + optional promoter 1-2%) — with SDBES's own backtest showing only ~25 of
  54 outperformed (SDBES 01:01:10): explicitly a weak standalone signal.

### Order of application

(1) industry/stage context → (2) quantitative combined screen (sales/PAT/ROC/mcap,
optional PE) → (3) technical + volume + RS confirmation → (4) sponsorship check →
(5) **read** (concall, press release, DRHP, interviews) to classify the trigger
real/fake, cyclical/structural (TFELT 00:32:19-00:32:33).

### Side-by-side vs the ladder

| | Lectures | Ladder |
|---|---|---|
| Sales ≥15% / PAT ≥20% YoY qtr | leg 1-2 of a 4-part query | G0, encoded, but as the whole screen |
| ROC ≥15% | leg 3, waived for turnarounds | G3 ≥15, only lender exemption |
| Market cap ≥1000cr | leg 4, load-bearing | **absent** |
| 30-wk EMA (entry & exit) | SIBES entry / LSARL exit | **absent** |
| Relative strength vs index | "holy grail" | **absent** |
| RSI≥50 / ADX≥20 | SIBES corroborates both, as 2 of 3 | G8 encodes 2 of 3 |
| D/E ≤0.7 | never stated in L5 | G1 (other course) |
| "New" catalyst (CANSLIM N) | master organizing idea | **absent**, even as observation |
| Post-screen reading step | mandatory step 5 | no concept of downstream work |

What the ladder added that L5 never says: nothing contradicted — G1 and most
observations come from other courses and are simply out of L5's frame.

## 3. What the ladder misses, ranked

1. **[HARD] Market-cap floor ≥1000cr (map: G0).** A required leg of the very query
   G0 cites. Two independent lectures. Cheapest, best-provenanced fix available.
2. **[HARD] Turnaround carve-out on the ROCE gate (map: G3).** TFELT 00:42:09 +
   FESTF concur; also matches G3's own provenance "or trending toward it." Real
   bar with a real exemption class — encodable as an attribute like `is_lender`,
   though *detecting* "turnaround" is itself borderline JUDGE.
3. **[HARD] 30-week EMA rule (map: G8 for entry; a NEW technical-avoid gate for
   exit — explicitly NOT G2).** Computable from weekly prices already fetched.
   Entry: price ≥ 30wk EMA joins RSI/ADX (SIBES). Exit/avoid: price < 30wk EMA =
   stage-4 (LSARL 00:26:07).
4. **[HARD-ish] Relative strength vs index, 52-week high, 13/26/52-wk lookbacks
   (map: G8 or new).** Needs an index series the ladder doesn't currently compute
   against, but it is price data. His single most-praised screen.
5. **[JUDGE] The post-screen reading discipline (map: structural).** The ladder
   hands back 38 names as an endpoint; every lecture says that is where work
   starts. Not encodable as a bar — encodable as output framing: CANDIDATE =
   "read next," never "buy."
6. **[SOFT] The "new"/inflection lens (map: none).** Shape-of-curve patterns —
   SDBES's flat-3-4-quarters-then->30% breakout (SDBES 00:14:52) is an inflection
   detector, not a level test; needs multi-quarter PAT trajectories (fetchable in
   principle) plus concall reading (not).
7. **[SOFT] Sponsorship screens (FII/DII/promoter deltas) (map: none)** — with the
   built-in warning that ~half underperform (SDBES 01:01:10); observation-grade
   at best, never a gate.
8. **[JUDGE] Industry stage-2 precondition (map: none).** Most-repeated idea in
   SDBES; chart reading, no crisp number given.

Numbers to quarantine as dated/one-off: Wolfspeed 3-4x forward FCF (SIBES
00:25:39, one distressed company); Laurus 600→520 price band (LSARL 00:25:26);
TFELT's personal 15-30x PE excitement band — scoped to growth names in an
expensive market, and NOT the same thing as pe_context-001's 15-35 band or the
optional <40 dial. Three different PE numbers with three different scopes; none
should merge.

**On G2:** LSARL's falling-knife material is technical, not forensic — nothing on
pledging, RPTs, auditors, or accounting. It populates a technical-avoid rule, not
the forensic veto. Combined with the Crash Course finding that the cash-flow
lecture frames every cross-statement check as caution rather than veto, L5 gives
**no basis for filling G2 with a numeric rule**. Leaving it empty remains the
defensible choice; the honest fix for "nothing can be REJECTED" is the 30-wk-EMA
technical avoid (a new gate), not a fake forensic bar.

## 4. Contradictions

- **Steady-grower vs inflection.** G0 admits consistent 20%+ growers; SDBES's
  earnings-breakout scan requires prior quarters FLAT then a >30% break — it would
  *exclude* many G0 passers, and G0 would miss his breakout cohort's scoping
  (1000-20,000cr window). Same numbers-family, different pattern.
- **TFELT vs G8's own vocabulary.** TFELT never mentions ADX and only mentions RSI
  to disclaim it; his preferred entry screen is relative strength. SIBES, though,
  corroborates RSI 50 / ADX 20 exactly. Both are him. Resolution: different tools
  for different markets/sessions — but the ladder encodes only the SIBES/HOWB pair
  and none of the TFELT lens.
- **LSARL's internal duration slip:** consolidation bullish after "two to three
  months" and "three to five weeks" in one sentence (LSARL 00:08:54) — a fuzzy
  window, do not hard-code.
- **Sponsorship signal vs its own backtest:** taught as a screen, then shown to
  underperform ~half the time (SDBES 01:01:10). Any encoding must carry the caveat
  or is misrepresentation.

## 5. First cut at the 38

- **USHAMART (CANDIDATE)** — [company] SUPPORTED twice: SDBES's flagship worked
  example (concall: margin guidance raised 18→19-20%, ROC 20.6%, WC cycle 194
  days, SDBES 00:36:32); LSARL adds technical color — in stage 2 "for last 2 to 2
  and a half years" (LSARL 00:24:53). Both are lecture-date claims, not current
  verdicts, but this is the strongest lecture-backed name on the list.
- **NAVINFLUOR (CANDIDATE)** — [company] SUPPORTED: clears margin-expansion, PAT-
  consistency, institutional and volume scans simultaneously with a concall-level
  HPP/CDMO mix story (SDBES 00:47:01, 00:51:24).
- **CARTRADE (WATCH)** — [rule] tension, both directions. TFELT cites it as a
  clean positive of his preferred RS + loss-to-profit inflection screen (TFELT
  01:48:32) while the ladder's G3 (ROCE 11.8) holds it at WATCH — and the
  turnaround carve-out (miss #2) is *exactly* the exemption that would apply to a
  company swinging from -24cr to +40cr PAT. SDBES separately confirms its margin
  expansion is real (SDBES 00:45:12). This is the test case for miss #2: the
  verdict is untrustworthy because the rule lacks its stated waiver, not because
  the lecture endorses the business unconditionally.
- **LAURUSLABS (CANDIDATE)** — [company, historical only] LSARL's stage-4 worked
  example at 600-620→520 (LSARL 00:25:26) is a past chart episode, far below its
  current range. No live doubt; do not downgrade on it.
- **SCI (WATCH)** — bare name-list mention in SDBES (SDBES 00:48:26). Not a verdict.
- **[rule] applying miss #1 to the whole list:** every one of the 38 should be
  checked against the ≥1000cr floor the source screen always carried; any
  sub-1000cr name passed G0 under a rule its own provenance never ran unaccompanied.
- **[rule] applying miss #3:** any of the 38 currently below its 30-week EMA is,
  by LSARL's one computable rule, a name the course would refuse to study —
  RSI/ADX passing notwithstanding.

The other 33 names are unmentioned across all four lectures — L5 neither supports
nor doubts them individually; it doubts the *process* that stamped them CANDIDATE
without a market-cap leg, a turnaround-aware ROCE, an RS/EMA layer, or any
downstream reading step.
