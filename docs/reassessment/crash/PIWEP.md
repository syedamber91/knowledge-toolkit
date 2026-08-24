LECTURE: Part 4: The Power of Incentives    REF: PIWEP    (transcript: 20578 chars, 218 lines, covered: yes)

## 1. CRUX

Teach the student to always ask "what is this person's incentive?" before trusting a market signal, a promoter action, a policy, or a paid product -- because incentives predictably bend behaviour (sometimes usefully, as with promoter warrants, sometimes destructively, as with fudged numbers), and reading them correctly is a filter for both idea generation and self-protection.

## 2. MECHANISM

- Promoter warrant issuance is read as a costly, verifiable signal: the promoter locks in a future price today but must fund it with real cash on a schedule (PIWEP 00:01:41), so the instructor treats a string of past warrant issues followed by large share-price gains -- APL Apollo, "HCG" [ASR garbled, unclear real name], "glass coat" [likely "HLE Glascoat"], "Moldic packaging" [likely "Moldtek Packaging"], "IOL chemical" [likely "IOL Chemicals and Pharmaceuticals"] (PIWEP 00:00:17) -- as evidence the mechanism works, not as proof any one of them will repeat.
- The same warrant logic is extended to open-market promoter buying: rising promoter shareholding paired with rising fixed assets/CWIP and expanding plant capacity is read as the promoter signalling conviction from information the market doesn't yet have (PIWEP 00:03:56).
- But the instructor immediately qualifies this with a failure case: a promoter ("HGG") buying heavily in 2017 coincided with a graphite-electrode cycle upswing that people mistook for a permanent moat ("speciality electrodes"), and the stock later fell 90% from peak once the cycle turned (PIWEP 00:01:41, PIWEP 00:03:23, PIWEP 00:03:27) -- so promoter buying is a prompt to dig into base-rate, long-term margin trends, not a standalone buy signal.
- Perverse incentives (the French Indochina rat-bounty story) generalize to a warning: when a promoter's personal incentive is tied to market cap itself (rather than to the underlying business), the predictable response is gaming the metric -- "fudging of numbers" -- so checks and balances (i.e. fundamental/forensic scrutiny) become more important precisely when incentive alignment looks strongest (PIWEP 00:05:39, PIWEP 00:05:48, PIWEP 00:06:16).
- Government/policy incentives work the same way at the macro level: South Korea's chaebol-era state concentrated support on winners and let losers fail, which the instructor contrasts with India's PLI (production-linked incentive) scheme, and teaches a multi-level ("first/second/third/fourth level") thinking chain to trace a policy incentive down to its niche, less-obvious beneficiaries (PIWEP 00:09:13, PIWEP 00:10:04, PIWEP 00:10:51).
- Finally, incentive-reading is turned on the student's own information diet: anyone selling a trading algo or "call" on social media has an incentive to sell, not to make the buyer money, so treat such offers skeptically (PIWEP 00:14:26, PIWEP 00:14:49).

## 3. SIGNALS

- [SOFT] Promoter warrant issuance (with the standard partial-upfront, price-locked-for-~18-months structure) is a positive incentive-alignment signal -- corporate-actions/warrant data is not in the ladder's fetched data (screener.in ratios, price series). "if the promoter's incentive is aligned towards market cap creation then you will see a lot of times different things happen" (PIWEP 00:01:41)
- [SOFT] Rising promoter shareholding (from open-market purchases), especially paired with rising fixed assets/CWIP and expanding capacity, is read as an insider-conviction signal -- shareholding-pattern trend data is not fetched by the ladder (the ladder currently has no promoter-holding metric at all). "the promoter holding has like increased by nearly 50 crores... promoter holding has gone from 48.46% to almost 55%... the balance sheet shows that fixed assets are doubling... the capacity of the company is tripling" (PIWEP 00:03:56)
- [JUDGE] A promoter buying heavily during a cyclical upswing can look identical to a promoter buying on durable-moat conviction; the instructor's own corrective is to check "the base rates in long term margins" rather than trust the buying alone -- this is explicitly a judgement call, not a computable rule. "it is important to see the base rates in long term margins, the company was very volatile" (PIWEP 00:01:41)
- [SOFT] When a promoter's personal incentive is tied to market-cap creation (e.g. via warrants/ESOPs), elevated risk of number-fudging follows, and "checks and balance" (fundamental/forensic scrutiny) becomes the counter-measure -- this is a narrative-level heuristic about incentive structure, not something derivable from ratios; it depends on reading corporate-action/promoter-incentive disclosures. "Perverse incentives are the reason why promoters are thinking about increasing market cap... fudging of numbers starts happening because they know they will be paid for increasing the market cap" (PIWEP 00:05:39-00:05:48)
- [JUDGE] Government policy incentives (e.g. PLI) can be traced through several levels of second-order thinking to find under-the-radar beneficiaries -- explicitly framed as a thinking process ("how you can use incentives to filter ideas"), not a screenable metric. "Full form of PLI scheme is... production linked incentive scheme" (PIWEP 00:10:04)
- [JUDGE] Products/calls/algos sold by someone whose incentive is the sale itself (not the buyer's returns) warrant skepticism -- a behavioural caution about the student's own information diet, not a company-screening signal at all. "there is a high degree of chance that you will end up losing money in Algos... this is because of incentives to sell Algo" (PIWEP 00:14:26-00:14:49)

## 4. WHAT THE LADDER MISSES

This lecture's central, load-bearing claim -- that promoter incentive structure (warrant issuance, open-market buying, and market-cap-tied compensation) is a decision-relevant signal, both bullish (conviction) and bearish (fudging risk) -- has **no counterpart anywhere in the 16-rule rulebook or the 9 observations** in CONTEXT.md. This is category (b): a central point the ladder has no rule for at all, and it is not a small omission -- promoter shareholding trend and corporate-action data (warrants, ESOPs) are not fetched or tracked by the ladder in any form.

Two more specific gaps within that:

- The ladder's G2 gate is explicitly noted in CONTEXT.md as empty ("forensic veto (no rule -> nothing can ever be REJECTED)"). This lecture's perverse-incentives argument -- "fudging of numbers starts happening because they know they will be paid for increasing the market cap" (PIWEP 00:05:48) -- is precisely the kind of promoter-incentive red flag G2 would need to encode if it were ever populated. The lecture doesn't give a testable rule itself (it's a narrative caution, correctly [SOFT]/[JUDGE]), but it is direct evidence that the empty G2 gate is a real, named gap the instructor himself flags as important ("checks and balance is very important for us to go through," PIWEP 00:06:16), not just an incidental blank.
- The existing capex_expansion-001 and fixed_asset_turnover-001 observations track capex/fixed-asset direction as neutral information with "NO stated preference either way" per CONTEXT.md's own wording. This lecture's Galaxy-wearings-style example (PIWEP 00:03:56) pairs capex expansion specifically WITH rising promoter shareholding as a combined conviction signal -- the ladder has the capex half but nothing for the promoter-holding half, so even if it wanted to reproduce this exact pattern it structurally cannot.

Everything else in the lecture (policy second-order-thinking as an idea-generation method, book recommendations, warnings about paid algo/call sellers, the South Korea/chaebol digression) is genuinely a human-judgement or self-protection topic with no computable-screen analogue, and correctly so -- there is nothing here to manufacture a finding around.

No dated one-company threshold is being smuggled in as a universal screening bar in this lecture; the warrant-issue price examples and promoter-holding percentages are illustrative case studies, not stated as a bar any company must clear.

## 5. NAMED COMPANIES

- APL Apollo -- positive example, warrant issue at Rs.2000 (pre-split), cited as a case where the warrant-then-price-appreciation pattern played out (PIWEP 00:00:17). Not in the 38.
- "HCG" [ASR garbled/ambiguous, cannot confidently resolve] -- positive example, warrant issue at Rs.130 vs current ~Rs.350 (PIWEP 00:00:17). Not in the 38.
- "glass coat" [likely "HLE Glascoat"] -- positive example, warrant issue at Rs.1385 vs current ~Rs.7500 (PIWEP 00:00:17). Not in the 38.
- "Moldic packaging" [likely "Moldtek Packaging"] -- positive example, warrant issue at Rs.184 vs current ~Rs.1000 (PIWEP 00:00:17). Not in the 38.
- "IOL chemical" [likely "IOL Chemicals and Pharmaceuticals"] -- positive example, warrant issue at Rs.205 vs current ~Rs.600 (PIWEP 00:00:17). Not in the 38.
- Care Health Insurance -- named as a case study of the "bourbon family" [ASR garbled, likely a business family name] taking over the entire promoter stake at Rs.52, with the stock now around Rs.220-230, and a possible demerger flagged as speculative upside (PIWEP 00:01:08). Not in the 38.
- "HGG" -- ambivalent/cautionary example: promoter bought heavily in 2017, margins "exploded" on the graphite-electrode cycle, but the instructor frames this as a case where people mistook a cyclical upswing for a moat (PIWEP 00:01:41). Not in the 38.
- "HGN graphite India" [ASR garbled reference, likely intends the graphite-electrode maker discussed] -- negative example, down 90% from its peak after the cycle turned (PIWEP 00:03:23). Not in the 38.
- "Precolga" [ASR garbled, cannot confidently resolve] -- positive example, promoter open-market buying of ~Rs.35.52 crore and Rs.11.92 crore, holding rising from 36.53% to 38.51% (PIWEP 00:03:52-00:03:56). Not in the 38.
- "Galaxy wearings" [likely "Galaxy Surfactants"] -- positive example, promoter holding rising from 48.46% to ~55% alongside fixed assets doubling and capacity tripling (PIWEP 00:03:56). Not in the 38.
- Hyundai, Samsung, LG, Kia Motors, Sony, Honda, Acer, HTC, Taiwan Semiconductor Manufacturing Company -- named only as illustrative examples of state-incentive-driven national champions (South Korea/Japan/Taiwan), not as investable-signal case studies for the Indian screener (PIWEP 00:08:22, PIWEP 00:09:13). None in the 38, and not the kind of mention this lecture treats as a stock-picking verdict.

## 6. AGAINST THE 38

None. No company in the 38-name shortlist is named, alluded to, or specifically discussed anywhere in this transcript.
