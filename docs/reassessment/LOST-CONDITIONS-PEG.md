# Lost-condition adjudication: `peg_ratio-001`

Source: `out/lost_conditions_obs_digest.json` (this repo) vs. the current
YAML entry in `soic-ladder/rulebook/soic-ladder-rules-v1.yaml` (lines
240-248). `peg_ratio-001` is an `Observation` (no `requires_attribute`, no
`gate`) — it structurally cannot exclude a company. The only question per
citation is whether `display_text` already says what the source says, or is
missing a point a reader would need to interpret the PEG number correctly.

Current `display_text`: "Price/earnings to 3-year profit growth (PEG) --
SOIC states a target below 1.5x, sourced independently in two courses (F26
and F38) which the source itself cross-references as matching. Not
meaningful for negative or near-zero growth (a shrinking company has no
sensible PEG) or loss-making companies."

For each citation below I pulled the surrounding transcript (not just the
digest's short `scope_quote`) from the source `refs.json` files
(`docs/reassessment/crash/refs.json`, `docs/reassessment/l5/refs.json`) to
confirm topical fit and whether the point is company-bound or a stated
general rule.

---

## Citation 1 — BVB 00:32:26 (`250126-part-b-valuation`, TVGP course)

> "if I am buying a company with 50PEP then I have to make sure that
> earnings growth is around 35% to 40% so that the peg ratio of the company
> remains below almost 1.5 to 1.75 times below"

Fuller context: this sits inside a generic framework statement ("my process
is very simple folks... I will buy 15 to 20 companies... I won't pay too
high of a starting multiple") — no company is named; "50PEP" (50x PE) is a
round hypothetical entry multiple used to illustrate the mechanism, not a
worked example on a specific stock.

**Bucket: DISPLAY-TEXT-SHOULD-BE-UPDATED.**

The current text states a single flat number ("below 1.5x") with no mention
that the ceiling is read relative to the entry P/E, and that SOIC tolerates
a slightly wider band (up to ~1.75x) at high entry multiples as long as
growth keeps pace. This is stated as general framework, not tied to one
company, so it clears the generalization bar. It corroborates (does not
contradict) the existing 1.5x figure — it just adds the "how far above 1.5
is still tolerable, and why" texture the reader needs to not treat 1.5x as a
razor-edge cutoff.

## Citation 2 — RSSER 02:51:39 (`291224-class-5-research-a-stock-from-scratch`, Mastering FA course)

> "I will come to your case studies can take the flexibility of valuation,
> we are lenient with valuation if growth runways multi-year in such cases
> rely on technicals for confirmation."

Fuller context: this sentence comes immediately after the instructor
explicitly walks through the PEG formula and the "peg below 1.5" checklist
item in the same "valuation checklist" passage (`"...then peg below 1.5
is peg means if the company has a PE ratio of 30..."` two sentences
earlier, same transcript). It is not a separate, unrelated aside — it is the
very next qualifier on the valuation-checklist item that includes PEG.

**Bucket: DISPLAY-TEXT-SHOULD-BE-UPDATED.**

This is a real, generalizable exception SOIC states about when the PEG (and
sibling valuation) discipline doesn't need to bind strictly: a durable,
multi-year growth runway, with technical confirmation substituting for
strict valuation-band adherence. The current text gives no hint that the
1.5x figure is conditional on growth durability/confidence rather than an
unconditional bar.

## Citation 3 — SIBES 00:12:53 (`100526-screen-international-businesses`, L5 course)

> "give me a list of companies which trade at less than 1.5x peg are
> exposed to the AI theme and the earnings growth is accelerating"

Fuller context: this is the instructor live-demoing a Perplexity Finance
screener tool ("I can just type a query and it can make a screen... it's
just again a tool of like screening for stocks") by typing an example
natural-language query on the spot. The 1.5x figure here is not asserted as
a rule at all — it's borrowed as a plausible filter value inside a one-off
tool demo, scoped to AI-theme, accelerating-earnings names.

**Bucket: TOO-THIN-OR-COMPANY-SPECIFIC-TO-GENERALIZE.**

There is no stated general point here beyond "1.5x is a reasonable number to
type into a screener as an example" — it's an ad hoc demo query, not
SOIC's own general PEG guidance. Nothing to generalize into `display_text`.

## Citation 4 — SMEC2 01:07:54 (`class-8-soic-method-explained-valuation-part-2`, crash course)

> "The upper limit I make for you so that your help is that this is just a
> very broad range of valuation that if you are giving more than 2x pegged
> ratio for any businesses apart from the consumer sector... there could be
> a trouble that happens that you are overpaying for a particular stock...
> try to avoid paying more than 2x peg ratio especially when you are
> entering a stock"

**Bucket: DISPLAY-TEXT-SHOULD-BE-UPDATED.**

This is an explicit, clearly-stated, general rule: SOIC's real hard ceiling
is 2x (not 1.5x), with 1.5x being the target/comfort zone, and the
consumer sector carved out as an explicit exception (see also Citation 6,
which independently corroborates the same 2x/consumer-exception rule from a
different lecture). The current `display_text` never mentions a 2x figure
or a sector-specific exception at all — a reader relying only on the current
text would not know 2x is the real "overpaying" danger line, nor that
consumer names are treated differently.

## Citation 5 — SMEC2 02:14:45-02:14:50 (same lecture as Citation 4)

> "in exchange businesses, volume growth matters the most"

Fuller context: this sentence opens a new topic — it follows a long
EV/EBITDA and SOTP (sum-of-the-parts) valuation walkthrough for
Reliance/BSE/IEX, discussing exchange-business re-ratings driven by volume
growth. PEG is not mentioned anywhere near this passage; the topic has moved
on to a different valuation approach (EV/EBITDA-driven SOTP) and a different
business-model carve-out (exchanges).

**Bucket: CONTEXT-MISMATCH-FALSE-POSITIVE.**

The mechanical detector likely picked this up because it falls inside the
same long "valuation" lecture as the PEG discussion, but the actual claim
here is about EV/EBITDA/SOTP and volume-growth tracking for exchange
businesses, not about how to read the PEG ratio. It doesn't answer this
observation's question.

## Citation 6 — VDVUV 00:20:11 (`class-9-valuations-decoded-valuations-part-3`, crash course)

> "That is only for the consumer businesses because those are easier to
> forecast."

Fuller context (essential — the digest's `scope_quote` alone loses the
antecedent): a few lines earlier in the same passage, the instructor states
explicitly: *"the hard rule should be 1.5, you can go 2 times only when you
are looking at a consumer business"* — backed by a cited Motilal Oswal 2018
wealth-creation study showing 3-year alpha-vs-index decaying as PEG rises
through 0-0.5 / 0.5-1 / 1-1.5 / 1.5-2 / 2-3 / 3+ buckets. The cited sentence
is the *reason* for the consumer-sector exception (easier-to-forecast
earnings), not a standalone claim.

**Bucket: DISPLAY-TEXT-SHOULD-BE-UPDATED.**

Independently corroborates Citation 4's 2x/consumer-exception rule from a
separate lecture, and adds the empirical backing (the Motilal Oswal alpha
study) and the "why" (consumer earnings are easier to forecast reliably,
so a higher embedded-growth assumption is more trustworthy there). Given two
independent lectures state the identical 2x/consumer-exception rule, this
clears the bar for a real, generalizable addition — the same standard the
existing `display_text` already applies when it says F26/F38 "cross-
reference as matching."

---

## Proposed `display_text` addition

Citations 1, 2, 4, and 6 corroborate a single coherent picture that the
current text is missing: 1.5x is a *soft target*, not the real ceiling, and
there are two named conditions under which SOIC tolerates going higher.
Proposed clause to append after the existing "Not meaningful for..."
sentence:

> "1.5x is a target, not a hard ceiling: SOIC's stated upper limit before
> 'overpaying' risk is roughly 2x, with an explicit exception up to 2x for
> consumer-sector businesses specifically (their earnings are easier to
> forecast reliably) -- corroborated independently in two courses (crash
> course Class 8 and Class 9). The ceiling can also stretch modestly (to
> roughly 1.75x) at very high entry P/E multiples provided earnings growth
> keeps pace, and can be relaxed further for names with a durable,
> multi-year growth runway, where technical confirmation substitutes for
> strict valuation-band adherence."

This is a proposal only, matching this task's scope (adjudicate + propose
wording) -- the rulebook YAML itself was not edited.

---

## Summary table

| Citation (ref + ts) | Bucket | One-line reason |
|---|---|---|
| BVB 00:32:26 | DISPLAY-TEXT-SHOULD-BE-UPDATED | General (no company named) framework statement: ceiling scales with entry P/E, tolerating up to ~1.75x at high multiples if growth keeps pace. |
| RSSER 02:51:39 | DISPLAY-TEXT-SHOULD-BE-UPDATED | Immediately follows the lecture's own PEG-checklist item; states a general leniency exception for durable multi-year growth runways with technical confirmation. |
| SIBES 00:12:53 | TOO-THIN-OR-COMPANY-SPECIFIC-TO-GENERALIZE | A one-off screener-tool demo query (AI-theme filter), not a stated SOIC rule. |
| SMEC2 01:07:54 | DISPLAY-TEXT-SHOULD-BE-UPDATED | Explicit general rule: real ceiling is 2x (not 1.5x), with an explicit consumer-sector exception. |
| SMEC2 02:14:45-02:14:50 | CONTEXT-MISMATCH-FALSE-POSITIVE | About EV/EBITDA/SOTP + volume growth for exchange businesses; PEG is not the topic of this passage. |
| VDVUV 00:20:11 | DISPLAY-TEXT-SHOULD-BE-UPDATED | Independently corroborates the 2x/consumer-exception rule (Motilal Oswal alpha-decay study as backing); gives the "why" (easier-to-forecast earnings). |

**Totals: 4 DISPLAY-TEXT-SHOULD-BE-UPDATED, 0 ALREADY-ADEQUATELY-COVERED, 1
TOO-THIN-OR-COMPANY-SPECIFIC-TO-GENERALIZE, 1 CONTEXT-MISMATCH-FALSE-POSITIVE.**
