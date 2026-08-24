# Fable review — observation-level lost-condition adjudication (independent second pass)

Reviewer: Fable-tier independent audit, 2026-08-25.
Scope: the three changed observation entries in
`soic-ladder/rulebook/soic-ladder-rules-v1.yaml` as applied in commit
`84c5028` (`pe_context-001`, `growth_trap_flag-001`, `peg_ratio-001`), plus
the two no-change adjudications (`market_cap_floor-001`,
`price_to_book_deep_value-001`). Method: every factual claim in the CURRENT
live `display_text` was traced to the raw transcript at the cited
(REF, timestamp) pair, resolved via `docs/reassessment/*/refs.json` against
the Stock Market Vault transcripts — not against the digest's scope_quotes
alone. This document proposes only; the rulebook was not edited.

---

## Verdict summary

| Entry | Verdict |
|---|---|
| `pe_context-001` | **SIGN OFF** (one minor wording nit, non-blocking) |
| `growth_trap_flag-001` | **SIGN OFF** |
| `peg_ratio-001` | **SIGN OFF ON SUBSTANCE, wording fix required** — no fabricated citation anywhere, the 1.5x→~2x correction is genuinely grounded, but the consolidated consumer-exception sentence garbles two real quotes into an internally contradictory rule |
| `market_cap_floor-001` (no change) | Concur — correctly left alone |
| `price_to_book_deep_value-001` (no change) | Concur — correctly left alone |

Zero fabricated or misattributed citations were found. Every quote I checked
exists verbatim (modulo ASR noise the docs already flag) at the cited
timestamp in the cited lesson. The one real problem is a synthesis error,
not a provenance error.

---

## 1. The load-bearing quote — SMEC2 01:07:54 — HOLDS UP

Independently re-read from
`crash-course/class-2-to-class-9/class-8-soic-method-explained-valuation-part-2-transcript.md`
at [01:07:54]. The transcript says, verbatim (thrice over, in the
instructor's repeat-for-emphasis style):

> "if you are giving more than 2x pegged ratio for any businesses apart
> from the consumer sector ... there could be a trouble that happens that
> you are overpaying for a particular stock ... try to avoid paying more
> than 2x peg ratio especially when you are entering a stock"

This is exactly what the correction rests on, it is a stated general rule
(no company named; framed as "the upper limit I make for you ... a very
broad range of valuation"), and it is at the right timestamp in the right
lesson. The passage even closes with "more than 2x pegged ratio ... at the
entry time, you are inviting trouble." **The citation is genuine and
correctly characterized. The 1.5x-target / ~2x-overpaying-line correction
is sound.**

Also verified in the same passage, unused by the applied text: "if you are
paying more than 2x keep tightening your V-stop multipliers as well" (see
optional addition B below).

## 2. But the applied consumer-exception sentence garbles two real sources

The live `peg_ratio-001` text says:

> "SOIC's stated upper limit before 'overpaying' risk is roughly 2x, with
> an explicit exception up to 2x for consumer-sector businesses
> specifically"

As written this is self-contradictory — if the general ceiling is 2x, an
"exception up to 2x" for consumer names grants nothing. The garble comes
from merging two verbatim-verified but non-identical statements:

- **SMEC2 [01:07:54]** (Class 8): >2x PEG is the overpaying line *for any
  business apart from the consumer sector* — i.e. ceiling ~2x for
  non-consumer, consumer exempted from that line (upper bound for consumer
  left unstated).
- **VDVUV [00:19:29–00:20:11]** (Class 9), verified verbatim: "**the hard
  rule should be 1.5, you can go 2 times only when you are looking at a
  consumer business**" ... "Even in that scenario if you are getting a
  consumer business, then sometimes we make exceptions. **That is only for
  the consumer businesses because those are easier to forecast.**" — i.e.
  ceiling 1.5x for non-consumer, up to 2x for consumer.

The adjudication doc's claim that "two independent lectures state the
identical 2x/consumer-exception rule" is an overclaim: the two lectures
draw the line differently (2x vs 1.5x for non-consumer), and they are
consecutive classes of the same Crash Course by the same instructor, so
"independently corroborated" is also generous. Relatedly, "1.5x is a
target, not a hard ceiling" sits in tension with VDVUV's literal "the hard
rule should be 1.5."

None of this reverses the correction — under BOTH readings 1.5x-as-comfort
and ~2x-as-danger-line is defensible, and the old text's implication that
1.5x was the ceiling full stop was indeed wrong. But the current sentence
should not claim a single crisp rule the sources don't share.

**Proposed replacement** for the sentence beginning "1.5x is a target...":

> "1.5x is the stated target, not the only number in the source: two Crash
> Course lectures draw the tolerance line slightly differently — one warns
> that paying more than 2x PEG for any business apart from the consumer
> sector risks overpaying (especially at entry), the other states the hard
> rule as 1.5x with permission to go to 2x only for consumer businesses
> (their earnings are easier to forecast reliably). Read ~1.5x as the
> comfort zone and ~2x as the outer danger line, with consumer names given
> the extra room."

The remaining two new clauses verify cleanly: BVB [00:32:26] ("peg ratio
... remains below almost 1.5 to 1.75 times", stated inside a generic
"my process is very simple folks" framework passage, no company bound to
the rule) supports the ~1.75x-at-high-entry-P/E stretch, and RSSER
[02:51:39] ("we are lenient with valuation if growth runways multi-year in
such cases rely on technicals for confirmation", arriving directly after
that lecture's own "peg below 1.5" checklist item) supports the
growth-runway relaxation. "Substitutes for" is a slightly stronger verb
than the source's "rely on ... for confirmation," but acceptably so.

## 3. `pe_context-001` — every claim traces; SIGN OFF

All verified verbatim at the cited locations:

- Banks / real estate / life insurers: ARTBV [00:40:22] "the P ratio will
  not work in life insurance companies, will not work in banks, will not
  work in real estate companies because there are different metrics to
  value them"; SMECS [02:17:50] "banks, real estate companies and life
  insurance companies you can't see the PE ratio".
- NBFCs and the replacement metrics: BVB [00:48:52] "you will value the
  bands [ASR: banks] on price to book ... NBFC will value it on price to
  book, life insurance is on immediate [ASR: embedded] value".
- Cement: BUFF [00:58:20] "never ever look at price to earnings ratio,
  especially when it comes to your cement sector".
- Deep cyclicals: ARTBV [00:40:30] "in deep pre-cyclicals, you have to
  look for price to book"; SMECS [02:18:31] "it is difficult to see the P
  ratio in deeply cyclicals".
- One-offs / operating leverage: SMECS [02:18:39] "...where the companies
  are sitting on operating leverage ... when earnings have a one-off
  element ... even here we cannot look at P-E ratios".
- Mature/stable + IT/FMCG + low gestation: FMNAF [00:46:35] "in mature and
  stable companies, it's an excellent tool to use P-Ratio because earnings
  are consistent, predictable"; VACRA [00:19:01] "PE ratio you can use it
  in business with low gestation period ... like IT services companies or
  you can use it in FMCG sector".
- Joint read with growth, not standalone: BVB [00:07:58] "I have taken
  PEMF between 15-35 if you get good earnings then it works well"; VALUV
  [00:28:42] "valuation should not be looked at in terms of P multiples.
  It should be looked at in terms of the growth rate of the earnings per
  share".

**Minor nit (non-blocking):** the phrase "deep-cyclical sectors like
cement" implies the source excludes cement *because* it is deep-cyclical.
BUFF's stated reason is different (high debt + high cash generation →
EV/ton as replacement cost); the deep-cyclical exclusion is a separate,
also-real point from ARTBV/SMECS. Suggested touch-up, if the file is
reopened anyway: "...real estate companies, cement (EV-based metrics
instead), or deep-cyclical sectors...". Not worth a commit on its own.

## 4. `growth_trap_flag-001` — the new sentence traces; SIGN OFF

The appended sentence ("The reverse also holds: a rich multiple can be
justified ... or if the investor is prepared to hold through a multi-year
price correction...") is supported verbatim by VALUV [00:24:34]:

> "The moment you start paying more than 50 times earnings ... if anything
> is wrong ... Multi-year correction and time correction can come So,
> either the growth rate should be high or you should wait for multi-year
> correction."

RSSER [02:51:39] (verified above) corroborates the leniency direction. The
pre-existing body of the entry (30-50x pattern, base effect, the "calling
a trap too early..." warning) predates this change and was not
re-adjudicated here beyond confirming it was not altered.

## 5. Bucket-3/4 drops — none wrongly dropped

I re-read each drop against the softer bar the task sets (a single strong
citation can justify a softly-worded addition, since observations carry no
exclusion risk):

- **FMODA 01:09:33** (personal 20-30 P/E buying range): the source itself
  disclaims it ("This is my case study, it can be not be yours also").
  Correctly dropped — the disclaimer argues *against* inclusion.
- **TFELT 00:33:15** (personal 15-30 comfort band, market-conditional):
  adds nothing beyond the 15-35 band already displayed. Correct drop.
- **SIBES 00:12:53** (Perplexity screener demo query): a borrowed filter
  value in a live tool demo, not a stated rule. Correct drop.
- **TFELT 00:42:15**, **VACRA 00:48:36**, **VACRA 02:12:19**, **VALU2
  01:11:31**, **WESNW 01:22:07/01:22:31**: each is genuinely about a
  different construct (a CANSLIM query leg, price-to-sales, general risk
  assessment, capital-allocation quality, investor-style taxonomy). The
  closest call is VALU2 01:11:31, but "capital allocation trumps an
  attractive multiple" belongs to a capital-allocation framework, not to
  reading `stock_pe`; folding it in would blur the observation. Concur
  with all drops.
- **SMEC2 02:14:45-02:14:50** dropped from the PEG adjudication as a
  context mismatch (exchange businesses / EV-EBITDA-SOTP passage): concur
  — note the same timestamp is legitimately *used* by `pe_context-001`'s
  sector-scoping theme, which is a different question; no conflict.
- **`market_cap_floor-001` / `price_to_book_deep_value-001`**: both
  citations are the entries' own provenance/corroborating refs restated;
  nothing to add. The MARKETCAP doc's honest "NBFC vs banks" gloss caveat
  is fair and correctly judged non-blocking.

## 6. Optional softly-worded additions (proposals only)

- **(A) — recommended:** the `peg_ratio-001` rewording in section 2 above.
  This is the one change I'd actually ask for.
- **(B) — optional, take or leave:** append to `peg_ratio-001`, from the
  same verified SMEC2 passage: "The same lecture adds a risk-management
  corollary: when entering above ~2x PEG anyway, tighten trailing-stop
  discipline so a turning earnings cycle doesn't catch the position." It
  is directly attached to the 2x rule in the source, but it is
  technicals-flavored; omitting it is defensible under the same reasoning
  that dropped RSSER's technicals angle from `pe_context-001`.

Nothing else from the 40 adjudicated citations warrants re-inclusion.

## 7. Out-of-scope observations (recorded, no action requested)

- `pe_context-001`'s provenance block still carries `ref: null` — a known,
  pre-existing gap (documented in CLAUDE.md), untouched by this change.
- `peg_ratio-001`'s pre-existing "sourced independently in two courses
  (F26 and F38)" clause and `growth_trap_flag-001`'s pre-existing TVGPF
  provenance predate this change and were not re-verified here.
