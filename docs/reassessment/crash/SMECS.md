LECTURE: Class 7 | SOIC Method Explained : Valuation Part 1    REF: SMECS    (transcript: 150865 chars, 1512 lines, covered: yes)

## 1. CRUX

This lecture is trying to change how a student treats a high P/E: not as a
neutral number to look up, but as a two-part bet -- that future earnings will
be much higher AND that the multiple itself will hold -- so that "valuation
matters" stops being an abstraction and starts overriding the urge to chase a
great-looking business at any price. It is explicitly framed as basics-only
("We are doing introduction to basics in part 1" (SMECS 01:15:12)); the hard
sector-by-sector multiples come in part 2 and DCF/exit mechanics in part 3.

## 2. MECHANISM

- P/E is relabeled: "it should be not known as price to earnings ratio, it
  should be known as perception to earnings ratio, perception upon earnings
  ratio" (SMECS 01:29:56) -- perception (transactional value, what others will
  pay) sits in the numerator, earnings (intrinsic value, cash generation) in
  the denominator, and the two can move independently.
- Buying at a high P/E is framed as a compound bet: "you are betting that the
  earnings will be very high at the time of exit and B, you are betting that
  the PE ratio will sustain at 75 times and PE ratio works along with earnings
  If the earnings collapse, the PE ratio also collapses" (SMECS 00:35:45) --
  the multiple is not independent of earnings; a growth disappointment hits
  both terms of the return equation at once.
- The Alkyl Amines two-phase case study is the spine of the lecture: a
  duopoly business with "margins were always between 16-20%... and PE ratio
  was around 10-13 times" (SMECS 00:23:01) later saw "margins increased to
  20-42%... PE ratio was around 70 times" (SMECS 00:23:01) against a 22-year
  history of 16-20% margins -- the instructor's point is that paying for the
  cheap-margin/cheap-multiple phase (PEG "0.6 times" (SMECS 00:32:51)) has
  favourable odds, paying for the peak-margin/peak-multiple phase does not.
- P/E is explicitly declared unusable, unadjusted, in several situations:
  "banks, real estate companies and life insurance companies you can't see
  the PE ratio" (SMECS 02:17:50), "it is difficult to see the P ratio in
  deeply cyclicals" (SMECS 02:18:31), and businesses "sitting on operating
  leverage" or with a "one-off element" in earnings (SMECS 02:18:39) --
  in each case a different multiple or an earnings adjustment is required
  before P/E means anything.
- Returns decompose into an earnings-growth component and a P/E-re-rating
  component, and the instructor demonstrates with Pidilite that most of a
  company's headline return can come from multiple expansion, not earnings,
  which is precisely the part that reverses in a de-rating: "if the company
  is returning 24% then only 11.79% is doing EPSK Rest of it is due to price
  to earnings multiplying" (SMECS 00:50:28).
- Forward P/E is taught as a forecasting tool, not a screening threshold: fix
  the market cap, project 1-2 years of earnings, and watch the implied
  multiple compress if the earnings call is right (worked twice, on a
  hypothetical and on Zen Technologies' order book).

## 3. SIGNALS

- [SOFT] P/E cannot be meaningfully applied, unadjusted, to banks, real
  estate companies, or life insurance companies -- "banks, real estate
  companies and life insurance companies you can't see the PE ratio... these
  companies have their own multiples to assess" (SMECS 02:17:50). Requires
  knowing the business type; the ladder does have an `is_lender` attribute
  for D/E and ROCE gates but no equivalent scoping on any P/E rule.
- [SOFT] P/E is "difficult to see" for deeply cyclical businesses, illustrated
  with a microfinance company where "the P ratio was at 80x... now today the
  P ratio has fallen at 30x because quarterly pat has gone from 1 crore a
  quarter to 40 crore per quarter" (SMECS 02:18:23) -- the ratio moved
  entirely because of earnings-cycle position, not because the business got
  cheaper or dearer. Needs judgement about where in the cycle a company sits.
- [SOFT] Trailing P/E is unreliable when earnings contain a one-off element
  (e.g. a contract-termination fee) or when a business is sitting on
  operating leverage from recent capex -- "even here we cannot look at
  P-E ratios to one-off elements and operating leverage this is something
  that we'll cover very very carefully" (SMECS 02:18:39). Needs annual-report
  reading to strip one-offs, not a screener field.
- [SOFT] A cornered/low free float can make P/E look "artificially high"
  because there isn't enough tradeable stock to price-discover -- worked
  example: "93% of the float is conned" (SMECS 02:20:43) (promoter + DII +
  FII holdings), stated as the reason the stock's P/E stayed elevated until
  the promoter began selling. Promoter/DII/FII holding percentages are data
  the ladder does not currently fetch.
- [HARD] PEG below roughly 1.5-2x, with positive growth, is where the
  instructor says returns are made: "We stand to make returns if the growth
  is positive and peg is less than 1.5 to 2 times" (SMECS 02:15:42); PEG
  below 1x is called out separately as the cheap end: "Low valuation is when
  peg is below 1 times and market is not expecting any growth but the growth
  can surprise" [garbled: "e-ring to PE rating"] (SMECS 02:15:48). This
  independently corroborates the ladder's existing PEG rule (peg_ratio-001,
  target <=1.5x, sourced from INSIGN/F26/F38) with a third source, and adds a
  distinct <1x "low valuation" sub-band the ladder does not currently encode.
- [JUDGE] A P/E of "40-45 times... becomes a very risky factor" for most
  businesses -- "the P ratio of 40-45% of businesses gets tricky again, some
  consumer businesses for most of the businesses, if you are giving PE ratio
  of 40-45 times then it becomes a very risky factor" (SMECS 00:35:45)
  (garbled ASR: "40-45% of businesses" appears to mean "a P/E of 40-45x", not
  a percentage of businesses). Stated as a general risk band, not tied to one
  company, but with no stated exception list (growth rate, sector) beyond the
  "some consumer businesses" aside.
- [JUDGE] "Valuations matter is 80 to 85 percent of the times true[,] 10 15
  percent of the times it isn't true" (SMECS 01:15:16) -- the instructor
  himself flags that the whole valuation-matters thesis of this lecture has
  a stated ~15-20% exception rate, without yet specifying (in this lecture)
  what characterizes the exceptions.
- [JUDGE] Balkrishna Tires (BKT) as a single-company anecdote: "BKT stops
  making money whenever P goes beyond 40 times" (SMECS 01:13:59) -- stated as
  a specific-company pattern from "long-term cap chart digging," not
  generalized to tyres/auto-ancillary as a sector.
- [JUDGE] D-Mart as a single-company anecdote: "no retailer has traded at
  230p and has made money in the world" (SMECS 01:12:51), extended to "no
  retailer has made money whenever it has traded beyond 220 to 230p in the
  world" (SMECS 01:12:51) -- a retail-sector P/E ceiling asserted from one
  company's history, not a cross-checked sample.
- [JUDGE] Forward P/E direction as a signal: "it's a very good thing that
  forward P is contracting because it means that the earnings are growing at
  a faster rate and the market cap will get justified more quickly" (SMECS
  02:51:11) -- contracting forward P/E (holding price constant while
  consensus/estimated earnings rise) is read as a positive sign, not a
  screenable ratio (needs forward-earnings estimates the ladder doesn't
  fetch).

## 4. WHAT THE LADDER MISSES

This is the most consequential brief in the batch for G6 because G6 is
currently EMPTY -- there is no valuation rule of any kind. This lecture is
explicitly "basics" (part 1 of 3) and does not hand over a single clean
universal band the way, say, the D/E or ROCE lectures did. What it does hand
over:

(a) The ladder's existing pe_context-001 observation (P/E read against a
15-35 band, no scope restriction stated in CONTEXT.md) is directly
contradicted in its universality by this lecture: "banks, real estate
companies and life insurance companies you can't see the PE ratio" (SMECS
02:17:50) and "it is difficult to see the P ratio in deeply cyclicals"
(SMECS 02:18:31). The 38-name shortlist includes at least one deeply
cyclical/commodity name (NATIONALUM) and several pharma names whose margins
this instructor elsewhere in the corpus treats as cyclical; pe_context-001
as currently written would misapply a flat 15-35 band to any of those
without the scoping this lecture insists on. This is a real gap, not a
restatement -- the ladder has no `is_bank`/`is_realestate`/`is_insurer` or
`is_cyclical` scoping anywhere, whereas it already has `is_lender` for two
other gates.

(b) A central, load-bearing point of this lecture -- that trailing P/E must
be adjusted for one-off earnings items and for businesses "sitting on
operating leverage" before it means anything (SMECS 02:18:39) -- has no
rule anywhere in the ladder. The ladder does have capex_expansion-001 and
fixed_asset_turnover-001 (both from F27, both currently framed as neutral
direction-only observations with no stated preference), but neither is
linked to a P/E-adjustment instruction; this lecture is the first to
connect "the business is expanding fixed assets ahead of earnings" to "so
trailing P/E will look artificially high, check the capex pipeline before
reading it" (the Deepak Nitrite worked example, SMECS 02:25:32 area). This
strengthens, but does not by itself fill, G6.

(c) The PEG corroboration (SIGNALS above) is a genuine third independent
source for peg_ratio-001's <=1.5x threshold, which is useful confirmation
but not new information the ladder is missing -- flagging it here mainly so
the eventual G6 rule author knows a third citation exists (SMECS 02:15:42)
alongside INSIGN and the two F26/F38 sources already in the rulebook.

(d) The 40-45x "risky" band (SMECS 00:35:45) and the 80x/70x/75x thresholds
attached to Alkyl Amines, D-Mart (230), and BKT (40x) are each either a
single dated worked example or an unscoped general statement the instructor
himself never turns into a checkable rule inside this lecture -- treating
any one of them as a universal P/E ceiling would be exactly the (c)-type
mistake this reassessment pass exists to catch. None of them come with a
stated sector scope, growth-rate condition, or exception list; part 2 (the
sector-multiple session) is where the instructor says that detail will
actually be given ("we will do it in part 2" (SMECS 02:17:57)).

Net assessment: this lecture is necessary context for G6 (it establishes the
*logic* a valuation gate should encode -- P/E as a compound bet, PEG as the
better single number, and P/E's inapplicability to whole sectors) but it does
not by itself supply a defensible universal G6 threshold. The strongest
concrete, corroborated, cross-source number to carry forward is the PEG
<=1.5-2x band; the strongest concrete gap to flag for the ladder author is
the missing bank/real-estate/insurer/cyclical scoping on any P/E-based
observation.

## 5. NAMED COMPANIES

- Alkyl Amines -- central worked case study, both a positive example (bought
  cheap at PEG 0.6x, PE 10-13x, duopoly margins 16-20%) and a cautionary one
  (same business later at PE 70x on unsustainably high 42% margins) (SMECS
  00:22:39-00:24:07). Not in the 38-name shortlist.
- Balaji Amines -- named as Alkyl Amines' duopoly peer, mentioned only as
  context, not separately evaluated (SMECS 00:31:22). Not in shortlist.
- Dish TV -- negative example of failed pricing power ("They had to shut it
  down") (SMECS 00:15:07). Not in shortlist.
- PVR -- positive aside: "only one fellow has been able to increase prices
  and get away that is PVR" (SMECS 00:15:31). Not in shortlist.
- D-Mart -- negative/cautionary anecdote on a P/E ceiling for retail (230x)
  and separately shown as a stock that under-participated in a small-cap bull
  run after de-rating (SMECS 00:16:37, 01:12:51). Not in shortlist.
- Pidilite (PIDILITIND, IN SHORTLIST) -- used as a cautionary case study on a
  "fantastic" business: 10-year return 24% CAGR but "only 11.79% is doing
  EPSK Rest of it is due to price to earnings multiplying" (SMECS 00:50:28),
  and P/E CAGR "has become negative" in the last 3 years, i.e. de-rating has
  begun (SMECS 00:51:35). This is a specific, negative-leaning point about a
  shortlisted company -- see section 6.
- Trent -- named as "only one anomaly from 5,000 stocks" of extreme high
  valuation, discussed only as an aside that SOTP treatment will follow in a
  later part; no verdict given here (SMECS 01:14:52). Not in shortlist.
- Tata Technologies -- positive governance/trust example (IPO priced fairly
  at "32-32 times earnings" rather than maximized) (SMECS 01:25:22). Not in
  shortlist.
- Tips vs. Sare Gama (SAREGAMA, IN SHORTLIST) -- comparative case study:
  "tips is growing faster in the near term because licensing reprise[.] Sare
  Gama, many entertainment businesses have misallocated capital allocation"
  (SMECS 01:32:53-01:32:58), stock "20% down from like 2-3 years but it is
  still like 10-11x" (SMECS 01:33:04). A specific, negative-leaning point
  (capital misallocation, slower near-term growth vs. Tips) about a
  shortlisted company -- see section 6.
- Rajesh Exports -- strongly negative governance case study: missing cash
  flow statements, stage-4 chart on high distribution volumes, promoter
  selling down (SMECS 01:35:04-01:36:59). Not in shortlist.
- Lincoln Pharma / an unnamed company tied to "Blue Minergy" (garbled;
  possibly "Vinergy") -- negative governance case: single-customer
  concentration ("one customer contributes 80% to the business"), and that
  customer is itself the subject of a short-seller report (SMECS
  01:38:40-01:39:33). Neither in shortlist; too garbled to map confidently.
- IRCTC -- negative cautionary example of 2021 narrative-driven euphoria that
  became a multi-year underperformer/flat stock (SMECS 01:06:28-01:07:57).
  Not in shortlist.
- Tattva Chintan -- named as "one of the businesses which is a good business
  But growth didn't come" after trading at "70 people" (70x P/E) (SMECS
  01:12:34). Not in shortlist.
- Dr. Lal PathLabs -- neutral aside via the blood-checkup analogy for margin
  of safety at high multiples, no explicit verdict (SMECS 01:12:51). Not in
  shortlist.
- Nike -- negative IPO-pricing anecdote: bankers priced the IPO at 4-4.5bn
  versus a fair ~1-1.5bn, "value on the table" was not left for investors
  (SMECS 01:13:37-01:13:50). Not in shortlist (not an Indian stock).
- Balkrishna Tires (BKT) -- cautionary single-company P/E-ceiling anecdote,
  "stops making money whenever P goes beyond 40 times" (SMECS 01:13:59). Not
  in shortlist.
- Infosys -- extended cautionary case study: PE of "206 times" in 2000 led
  to -5% CAGR over the next 5 years despite genuine ~30% earnings growth;
  entering in 2001 (lower PE) gave 12% CAGR; entering in 2002 (PE ~30x) gave
  "a decent 18% CAGR" (SMECS 02:13:33-02:14:05). Not in shortlist.
- IEX -- negative cautionary aside on a long-term holder "on 110B" (implying
  ~110x P/E) called out as taking excessive de-rating risk (SMECS
  02:15:13-02:15:27). Not in shortlist.
- Tata Tech (repeat mention) -- see above.
- Divgi Torqtransfer ("Divgi Talk" in transcript, garbled) -- low-float case
  study: PE looked sustained near "131-200" while ~90-93% of float was
  cornered by promoters/DII/FII, and it began correcting once the promoter
  (via Blackrock stake) started selling (SMECS 02:19:04-02:21:40). Not in
  shortlist.
- Sona BLW -- named only as an aspirational comparison ("Everyone says that
  we have to make a company like Sonaw BLW") in the Divgi Torqtransfer
  discussion, no direct verdict (SMECS 02:20:43). Not in shortlist.
- RTI Industries -- one-off-earnings case study: apparent PE of ~19-23x was
  actually ~45x once an ~800cr contract-termination-fee one-off was stripped
  from PAT (SMECS 02:22:00-02:24:49). Not in shortlist (SRF is referenced
  later as a sector comparator, also not in shortlist as this specific name).
- Natco Pharma -- extended forward-P/E and one-off-earnings case study: PAT
  grew from "170 to 1127 crore" on first-to-file exclusivity revenue the
  instructor calls temporary/"one of earnings", and the market is correctly
  not re-rating it because "it is not sustainable" (SMECS 02:38:04-02:39:43).
  Not in shortlist.
- Zen Technologies -- positive forward-P/E worked example: trailing PE ~72x
  but order-book-driven 2-year-forward PE estimated at "15 to 16 times, 17
  times" (SMECS 02:29:08-02:29:19), framed as an example of why forward
  earnings matter more than trailing multiples for an order-book business.
  Not in shortlist.
- Deepak Nitrite -- positive capex/operating-leverage case study: PE looked
  like "81 times" in 2018 but the stock later went "almost 11 X" once the
  phenol-plant capex converted to earnings (SMECS 02:25:18-02:26:27). Not in
  shortlist.
- Sandhar, Narayana -- named only as further "operating leverage" examples in
  a list, no specifics given (SMECS 02:25:18). Neither in shortlist.
- Metro Brands -- low-float cautionary aside: "at 100 P you are really
  betting that things hit the like well up there are Accidents which can
  happen" (SMECS 02:54:39), float scarcity flagged as the reason the multiple
  looks high; no clean verdict, explicitly framed as a risk to watch. Not in
  shortlist.
- Campus -- brief negative-leaning aside: "earnings have eroded like
  anything," questioned on stage-4 chart and whether its valuation is even
  reasonable (SMECS 02:56:15-02:56:31). Not in shortlist.
- RHI Magnesita -- extended cautionary worked example: refractory business,
  quarterly EBITDA annualized implies ~37x EV/EBITDA and PAT-based PE "60P"
  against an industry-wide growth rate of only "10-12%", explicitly
  questioned: "should we be paying 60 times P ratio?" (SMECS 03:01:00-
  03:03:04). Not in shortlist.
- Vesuvius India -- named as RHI's sector comparator, instructor's stated
  preference ("Vesuvius is what I like when I look at both of them") but
  explicitly caveated as not a recommendation (SMECS 03:03:16-03:03:32). Not
  in shortlist.
- Titan, D-Mart (repeat), V-Mart -- long-horizon comparison aside: "Titan is
  actually a relatively better stock if you take all these things and sit
  for 20 years," framed as a 20-year-horizon opinion, not a valuation call
  (SMECS 03:04:11). Titan and V-Mart not in shortlist.
- Steel Cast -- case study on management honesty during a down-cycle:
  management pre-announced no growth for FY22-23, later delivered on that
  guidance, framed positively for candor (SMECS 03:05:26-03:07:28). Not in
  shortlist.
- MCX -- one-off-cost adjustment aside, "remove one of costs from that one,
  60, 170 crores" (garbled), no clean verdict given, cut off by session
  wrap-up (SMECS 03:08:19-03:08:37). Not in shortlist.
- Insecticides India -- neutral pedagogical example only, used purely to
  demonstrate the P/E = market cap / TTM PAT calculation (28.5x), no verdict
  (SMECS 01:21:53-01:22:39). Not in shortlist.
- NCC, Ahluwalia (Lilo), ITD Cementation -- named as infra contractors
  re-rating on 20-35% earnings growth guidance, aside only, no individual
  verdicts (SMECS 01:31:06-01:31:14). None in shortlist.
- SIGACHI -- brief clarifying aside ("SIGACHI is not a chemical company...
  it's a more of a pharma proxy company"), not a valuation verdict (SMECS
  02:59:52-03:00:14). Not in shortlist.

## 6. AGAINST THE 38

- PIDILITIND: this lecture raises a specific, dated concern -- most of its
  headline 10-year 24% CAGR return came from P/E multiple expansion rather
  than the 11.79% EPS CAGR, and "Price to earnings CAGR has become negative"
  in the trailing 3 years, i.e. it is mid de-rating at lecture time (SMECS
  00:50:28, 00:51:35). This is a real verdict-adjacent point (watch whether
  the multiple keeps compressing), not a neutral mention, though the
  instructor never calls it a sell and explicitly reiterates it's "a very
  good business, no doubt fantastic franchisee" (SMECS 00:49:37).
- SAREGAMA: specific doubt raised via direct comparison to Tips -- "many
  entertainment businesses have misallocated capital allocation" attributed
  to Sare Gama by name, plus slower near-term growth than Tips at the same
  multiple, and the stock is noted as "20% down from like 2-3 years"
  (SMECS 01:32:58-01:33:04). This is a real, named, negative-leaning point,
  not a bare mention.
- The remaining 36 names on the shortlist are not mentioned anywhere in this
  transcript -- none.
