# Lost-condition adjudication: `market_cap_floor-001` and `price_to_book_deep_value-001`

Source: `out/lost_conditions_obs_digest.json` (this repo) vs. the current YAML
entries in `soic-ladder/rulebook/soic-ladder-rules-v1.yaml` (lines 317-351),
added 2026-08-25 in this same session. Both entries are `Observation`s (no
`requires_attribute`), so the only question per citation is whether
`display_text` already says what the source says.

---

## `market_cap_floor-001`

Current `display_text`: "Market capitalization (crore) -- SOIC's default
liquidity screen keeps candidates to the most-liquid tier at or above
₹1,000cr; the source explicitly allows looser ₹500cr or ₹100cr tiers at the
researcher's discretion, with added risk below ₹100cr (weaker business
models, negative cash flow more common) -- read this as a default, not an
absolute floor"

### Citation 1 — FESTF 00:42:15

> "above 100 crores, the criteria is different because a lot of times The
> businesses have very negative cash loads or poor business models"

Scope statement: near the ~100cr practical minimum, screening judgment needs
to differ from the standard 1000cr+ criteria because many such small-cap
names carry negative cash flows or weak business models.

**Bucket: ALREADY-ADEQUATELY-COVERED.**

This is not merely covered — it is the *primary* provenance quote the
`display_text` was written from (`provenance.ref: "FESTF 00:42:15"` in the
YAML entry itself). The clause "with added risk below ₹100cr (weaker business
models, negative cash flow more common)" is a direct paraphrase of this exact
quote. There is nothing left over to add.

### Citation 2 — TFELT 00:42:15

> "market capitalization, I wrote above 1000 crores because generally a lot
> of liquid names come You can do above 500 crores or 100 crores too But
> above 100 crores, the criteria is different because a lot of times The
> businesses have very negative cash loads or poor business models"

**Bucket: ALREADY-ADEQUATELY-COVERED.**

The YAML's own `corroborating_refs` already lists this exact ref+timestamp
verbatim: `"TFELT 00:42:15 (duplicate recording of FESTF, not an independent
third source)"`. The full quote is a superset of FESTF's — it adds the
₹1,000cr default and the ₹500cr/₹100cr discretionary tiers, both of which are
already present in `display_text` ("...at or above ₹1,000cr; the source
explicitly allows looser ₹500cr or ₹100cr tiers at the researcher's
discretion..."). The entry's own comment block already correctly identifies
this recording as a duplicate of FESTF, not an independent source, so no
count/confidence claim in the rulebook needs revisiting either.

---

## `price_to_book_deep_value-001`

Current `display_text`: "Price to book -- SOIC states a below-1x
price-to-book as a deep-value entry signal for cyclical companies,
corroborated across two independent lectures (Tata Steel as the worked
illustration in both). Only meaningful once P/E has already been ruled out:
the source's own sector-routing table says P/E \"will not work in life
insurance companies, will not work in banks, will not work in real estate
companies\" -- P/B (and embedded value for insurers) is what replaces it
there, also corroborated across two independent lectures. Not a signal on a
normally-priced company trading above book for ordinary quality reasons."

### Citation 1 — BVB 00:48:52

> "NBFC will value it on price to book, life insurance is on immediate
> value" (ASR-garbled — almost certainly "embedded value", matching the
> rulebook's own gloss)

Scope statement: P/E-based thresholds don't apply to NBFCs (valued on P/B)
or life insurers (valued on embedded value).

**Bucket: ALREADY-ADEQUATELY-COVERED.**

`BVB 00:48:52` is already named verbatim in the YAML's own
`corroborating_refs`: `"BVB 00:48:52 (sector-routing scope: banks -> P/B,
life insurers -> embedded value)"`. The substantive claim — P/E breaks down
for this class of financial company, P/B (or embedded value for insurers)
replaces it — is exactly what `display_text`'s second half already states.

One honest caveat worth recording, not a missing point: the rulebook's own
parenthetical gloss on this citation says "banks -> P/B", but BVB's actual
words say **NBFC**, not "banks" generically — that "banks" wording in
`display_text` is a direct quote from the *other* corroborating source
(ARTBV's sector-routing table), not from BVB. NBFC and bank are distinct
categories in Indian financial regulation. This doesn't change the bucket
because (a) the exact citation is already incorporated by ref+timestamp, (b)
the substantive point (P/E fails for this financial-company class, P/B
replaces it) is present regardless of which sub-label is used, and (c) this
rulebook's sibling gates (`leverage-001`, `capital_efficiency_gate-001`,
referenced in this entry's own header comment) already route NBFCs and banks
together under one `is_lender` attribute, so the categorization gap is not
novel or unaddressed elsewhere in the rulebook's design — it's a possible
future wording tightening, not a lost condition.

---

## Summary

| Citation (ref + ts) | Bucket | One-line reason |
|---|---|---|
| `market_cap_floor-001` — FESTF 00:42:15 | ALREADY-ADEQUATELY-COVERED | This is the entry's own primary provenance quote. |
| `market_cap_floor-001` — TFELT 00:42:15 | ALREADY-ADEQUATELY-COVERED | Already named in `corroborating_refs` as a duplicate recording; content is a superset already reflected in `display_text`. |
| `price_to_book_deep_value-001` — BVB 00:48:52 | ALREADY-ADEQUATELY-COVERED | Already named verbatim in `corroborating_refs`; substance (P/E fails for this financial-company class, P/B/embedded value replaces it) is already in `display_text`. Minor "NBFC vs. banks" label nuance noted but not bucket-changing. |

**Totals:** `market_cap_floor-001` 2/2 ALREADY-ADEQUATELY-COVERED.
`price_to_book_deep_value-001` 1/1 ALREADY-ADEQUATELY-COVERED. Zero findings
in DISPLAY-TEXT-SHOULD-BE-UPDATED, TOO-THIN-OR-COMPANY-SPECIFIC, or
CONTEXT-MISMATCH-FALSE-POSITIVE for either observation.
