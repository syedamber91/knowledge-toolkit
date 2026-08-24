# Lost-condition adjudication: `pe_context-001` and `growth_trap_flag-001`

Source: `out/lost_conditions_obs_digest.json` (`pe_context-001` entry, 31
`dropped_conditions` rows against one `current_entry`) vs. the current YAML
entries in `soic-ladder/rulebook/soic-ladder-rules-v1.yaml` (`pe_context-001`
at line 202, `growth_trap_flag-001` at line 276). Both entries key on
`stock_pe`, so the digest's citation list is shared between them (per the
task brief); this file adjudicates it once and assigns findings to whichever
observation (or both) each finding actually bears on.

The digest lists 31 rows, one duplicate timestamp (`FMNAF 00:46:35` appears
twice with two distinct quotes from the same moment — a positive and a
negative framing of the same point) — 30 distinct citation *locations*, 31
distinct *statements*. Both are adjudicated below; the count tables at the
end use 31 (one row per statement) since each carries its own bucket.

Both are `Observation`s: no `requires_attribute`, no `gate`, cannot exclude a
company. The only question per citation is whether `display_text` already
says what the source says, or is missing something a reader needs.

Current text, for reference:

- **`pe_context-001`**: "Price to earnings, read against a 15 to 35
  reference band"
- **`growth_trap_flag-001`**: "SOIC's growth-trap pattern: the market pays
  30-50x+ PE assuming supernormal growth continues indefinitely, and as the
  earnings base gets larger the same growth RATE gets mathematically harder
  to sustain (the base effect) -- when growth decelerates, the multiple
  derates hard, compounding the slowdown into a price fall. This is a prompt
  to check the base effect, not a verdict: the source itself warns that
  'calling a trap too early is often indistinguishable from being wrong.'
  Distinct question from pe_context-001 (which asks whether the multiple
  looks fair) -- this one asks whether the growth priced into it is
  arithmetically realistic."

---

## Theme 1 (bucket 1): P/E is sector- and earnings-quality-scoped, not a universal lens

`pe_context-001`'s current text says nothing about *when* P/E is even a
valid metric to read — it just states the band. 19 citations, independently
sourced across many different lessons and many different sectors, all make
the same underlying, generalizable, repeatedly-stated SOIC point: **P/E only
reads meaningfully on businesses with steady, already-mature earnings; it
breaks down for financials, real estate, and several other sector/earnings
situations, which need a different multiple entirely.** This is not one
instructor's one-off remark — it recurs across ARTBV, BUFF, BVB, FMNAF,
FMODB, SMEC2, SMECS, and VACRA, naming a consistent, overlapping set of
exceptions (financials, cyclicals, asset-heavy/depreciation-heavy, one-off
or capex-distorted earnings). That consistency across independent sources is
exactly what makes this a stated rule rather than a stray aside — the
opposite failure mode from a dated one-company calibration number.

Citations (grouped by the specific exception each names, all supporting the
same general point):

**Financials / real estate / insurance — P/E doesn't apply at all:**
- ARTBV 00:40:20 — "the P ratio will not work in life insurance companies,
  will not work in banks, will not work in real estate companies because
  there are different metrics to value them"
- BVB 00:48:52 — "NBFC will value it on price to book, life insurance is on
  immediate value" [embedded value]
- SMECS 02:17:50 — "banks, real estate companies and life insurance
  companies you can't see the PE ratio"

**Specific non-financial sectors with their own multiple:**
- BUFF 00:58:20 — "never ever look at price to earnings ratio, especially
  when it comes to your cement sector" (use EV/ton)
- BVB 00:49:32 — "you cannot value a hospital stock on P[E]" (use EV/EBITDA)
- FMODB 00:20:08 — "In hospitals business depreciation is overstated" (so a
  standard P/E reading understates true cost, use EV/EBITDA)
- SMEC2 02:14:45–02:14:50 — for exchange/platform businesses, "volume growth
  matters the most," standard multiple ceilings take a back seat
- SMEC2 02:46:51 — for textile/chemical names, switch to EV/EBITDA
  specifically when current earnings are depressed
- VACRA 00:28:30 — "In asset heavy businesses use EV upon EBITDA price to
  cash [flow] ratios"
- VACRA 02:01:53 — AMC/wealth-management earnings (and hence P/E) are
  distorted by mark-to-market AUM gains, inflated up-cycle, collapsed
  down-cycle — read against where the equity cycle stands

**Cyclicals — P/E moves with the cycle, not with valuation richness:**
- ARTBV 00:40:30 — "in deep pre-cyclicals, you have to look for price to
  book"
- FMNAF 00:46:35 (quote A) — "Cyclicly, in industries, PE ratios cannot be
  used because earnings evaporate"
- FMNAF 00:46:35 (quote B) — "in mature and stable companies, it's an
  excellent tool to use P-Ratio because earnings are consistent,
  predictable" (the positive framing of the same boundary)
- SMEC2 02:31:17 — "then P[E] is a misleading metric" at the worst point of
  a cycle
- SMECS 02:18:31 — "it is difficult to see the P ratio in deeply cyclicals"
- VALU2 01:08:33 — cyclical/lumpy-earnings businesses structurally trade at
  low P/E; a low multiple there is not itself a cheapness signal

**Earnings distortions (one-offs, fresh capex, recent investment):**
- SMECS 02:18:39 — trailing P/E shouldn't be taken at face value when
  earnings include a one-off item or the business is riding operating
  leverage from recent capex
- VACRA 00:15:27 — when depreciation/new hiring from mid-capex is
  temporarily depressing reported profit, use EV/EBITDA instead
- VACRA 00:19:01 — P/E is reliable for "low-gestation" mature-earnings
  businesses like IT/FMCG; companies that "just done investments" need a
  forward/normalized P/E instead

**Proposed `display_text` addition for `pe_context-001`:**

> "...not a meaningful lens for banks, NBFCs, life insurers, real estate, or
> cement (which use sector-specific multiples like price-to-book,
> EV/EBITDA, or embedded value instead), and unreliable for cyclical
> businesses at cycle extremes, asset-heavy or capex-heavy businesses,
> and earnings with one-off items or recent operating leverage — reads
> best on mature, stable-earnings businesses (e.g. IT, FMCG)."

Note: this does not reintroduce the two-sector *restriction* the header
comment (bullet 2) deliberately removed — it adds informational scope, not
a gating exclusion. IT/FMCG is named as where the metric reads best, not as
the only place it may be shown.

---

## Theme 2 (bucket 1): the band is a joint read with growth, not a standalone bar

Three independent citations state that a P/E figure — whether inside or
outside a comfort band — should never be judged in isolation from the
company's earnings/growth trajectory. This is missing from `pe_context-001`
(which currently presents the 15–35 band with no such qualifier) and is a
genuinely separate point from Theme 1 (sector scope) and from
`growth_trap_flag-001`'s base-effect mechanism.

- BVB 00:07:58 — "in my case I have taken PEMF between 15-35 if you get
  good earnings then it works well" — the literal 15–35 band, stated as
  conditional on good earnings, not a standalone bar.
- VALUV 00:28:42 — "valuation should not be looked at in terms of P
  multiples [alone]" — must be read together with the earnings growth
  trajectory rather than as a flat standalone band.
- VALUV 00:24:34 — the ">50x excessive" framing is softened, not a hard
  cutoff: acceptable if growth is high enough, or if the investor is
  willing to hold through a multi-year correction. This is the mirror image
  of `growth_trap_flag-001`'s base-effect warning (multiple derates when
  growth decelerates) — it states the reverse condition under which a rich
  multiple is *not* a trap.

**Proposed `display_text` addition for `pe_context-001`:**

> "...this is a screening signal only when read alongside the company's
> earnings/sales growth trajectory, not a standalone pass/fail bar."

**Proposed `display_text` addition for `growth_trap_flag-001`** (append after
the existing "prompt to check the base effect, not a verdict" sentence):

> "The reverse also holds: a rich multiple can be justified rather than
> flagged as a trap if the growth rate is high enough to sustain it, or if
> the investor is prepared to hold through a multi-year price correction
> instead of treating the multiple as a fixed ceiling."

---

## Bucket 3 — too thin / personal / dated to generalize

- **FMODA 01:09:33** — "This is my case study, it can be not be yours also"
  (instructor's own 20-30 PE personal buying range). The source *itself*
  disclaims this as a personal anecdote, not a rule — textbook bucket 3, and
  it argues *against* adding anything, not for it.
- **TFELT 00:33:15** — "you won't get any growth stock on 5th P[E]" — a
  15-30x "comfort band," but the scope statement itself frames it as "a
  personal preference, not a hard screening criterion," tied to market
  conditions at the time of the lecture ("expensive, richly-valued market").
  Dated, personal, market-timing-conditional — not a durable universal rule
  distinct from what's already captured.

## Bucket 4 — context mismatch (different question than these two observations answer)

- **TFELT 00:42:15** — PE<40 as an optional fifth leg bolted onto a
  different, narrower screening construct (a CANSLIM-style query-builder
  exercise) — a different specific threshold in a different specific
  methodology, not a stated universal point about reading `stock_pe`.
- **RSSER 02:51:39** — valuation discipline can be relaxed for durable
  multi-year growth stories, substituting *technicals* for confirmation —
  this is a technicals-timing rule, a different topic than these two
  fundamental-valuation observations.
- **VACRA 00:48:36** — "Price to sales always has to be looked at with
  price to earnings..." — the actual rule being stated is about how to use
  *price-to-sales*; P/E is named only as one of several co-factors, not the
  subject of the claim.
- **VACRA 02:12:19** — "if I can't assess the impact... I can't value it" —
  a general risk-assessment/investment-process principle, not specific to
  reading P/E.
- **VALU2 01:11:31** — poor capital allocation overrides an attractive (low)
  multiple. The actual claim is about capital-allocation quality trumping
  valuation as a decision factor — a different framework, illustrated with
  a P/E number, not a rule about reading P/E itself.
- **WESNW 01:22:07** — deep-value investor style described (entry governed
  by valuation level). Style description, not a stated SOIC screening rule.
- **WESNW 01:22:31** — GARP investor style described (reasonable P/E + EPS
  growth), contrasted with deep value. Same as above — describing a
  different investing style, not a SOIC rule.

---

## Summary table

| Citation (ref + ts) | Bucket | Reason |
|---|---|---|
| ARTBV 00:40:20 | 1 | Financials/real estate: P/E invalid entirely |
| ARTBV 00:40:30 | 1 | Deep cyclicals: use P/B instead |
| BUFF 00:58:20 | 1 | Cement sector: use EV/ton instead |
| BVB 00:07:58 | 1 | 15-35 band conditional on good earnings |
| BVB 00:48:52 | 1 | NBFC→P/B, life insurer→embedded value |
| BVB 00:49:32 | 1 | Hospitals: use EV/EBITDA instead |
| FMNAF 00:46:35 (a) | 1 | Mature/stable earnings: P/E works well |
| FMNAF 00:46:35 (b) | 1 | Cyclical industries: P/E unusable |
| FMODA 01:09:33 | 3 | Self-disclaimed personal case study |
| FMODB 00:20:08 | 1 | Hospitals: depreciation overstated, distorts P/E |
| RSSER 02:51:39 | 4 | Technicals-timing rule, different topic |
| SMEC2 02:14:45-02:14:50 | 1 | Exchange/platform: volume > multiple ceilings |
| SMEC2 02:31:17 | 1 | Cycle trough: P/E misleading |
| SMEC2 02:46:51 | 1 | Textile/chemical, depressed earnings: EV/EBITDA |
| SMECS 02:17:50 | 1 | Banks/real estate/insurance: P/E unreadable |
| SMECS 02:18:31 | 1 | Deep cyclicals: P/E hard to read |
| SMECS 02:18:39 | 1 | One-offs/operating leverage distort trailing P/E |
| TFELT 00:33:15 | 3 | Personal comfort band, dated market condition |
| TFELT 00:42:15 | 4 | Different optional threshold, different query methodology |
| VACRA 00:15:27 | 1 | Mid-capex depressed profit: use EV/EBITDA |
| VACRA 00:19:01 | 1 | P/E best for low-gestation (IT/FMCG); else forward P/E |
| VACRA 00:28:30 | 1 | Asset-heavy: use EV/EBITDA, P/CF instead |
| VACRA 00:48:36 | 4 | Rule is about price-to-sales, not P/E |
| VACRA 02:01:53 | 1 | AMC: mark-to-market distorts earnings/P/E |
| VACRA 02:12:19 | 4 | General risk-assessment principle, not P/E-specific |
| VALU2 01:08:33 | 1 | Cyclicals structurally low P/E ≠ cheapness signal |
| VALU2 01:11:31 | 4 | Capital-allocation-quality framework, not a P/E-reading rule |
| VALUV 00:24:34 | 1 | Excessive-multiple framing softened by growth/patience |
| VALUV 00:28:42 | 1 | Multiple must be read jointly with growth trajectory |
| WESNW 01:22:07 | 4 | Deep-value investing style description |
| WESNW 01:22:31 | 4 | GARP investing style description |

**Totals:** Bucket 1 (display-text-should-be-updated): **22**. Bucket 2
(already-adequately-covered): **0**. Bucket 3 (too thin/personal/dated to
generalize): **2**. Bucket 4 (context mismatch): **7**. Total: 31.

Despite 22/31 landing in bucket 1, this collapses to just **two** proposed
`display_text` edits (Theme 1, Theme 2) plus one small addendum to
`growth_trap_flag-001` — the volume reflects how consistently the same two
points recur across independent lessons, not 22 separate new facts.
