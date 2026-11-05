# T4 — Retrieval over the BIOCON pages (2026-11-05)

## What was built (smallest first)
`scripts/vps_extraction/page_index.py`: one page = one chunk, SQLite FTS5 (BM25), no model, no network.
`answer_or_refuse(conn, question, number)`: cites the page only if the number's digits are on a retrieved page as a WHOLE number (999 is not found inside 11,999); else refuses.
`scripts/vps_extraction/eval_page_index.py`: scores the 16 golden `page_grep` rows. Tests: `tests/test_page_index.py` (6, written first; red, then green).

## Result on the FY26 annual report (558 pages), 16 rows
| Method | hit@1 | hit@3 | hit@5 | hit@10 |
|---|---|---|---|---|
| FTS5 only | 9 | 11 | 11 | 13 |
| Vectors only (ollama nomic-embed-text, local) | 3 | 6 | 8 | 9 |
| Hybrid (FTS5 + vectors, RRF k=60) | 5 | 9 | 12 | 14 |
- One row = 6 points, so hybrid vs FTS5 is a **tie** within noise (spec rule: tie, pick the cheaper). Hybrid is worse at the top ranks (hit@1: 5 vs 9).
- Embedding 558 pages took 117 s on this Mac (local, free); not tried on the VPS.
- Fabricated-number test: each row's number swapped for same-shape wrong digits; 0 of the 15 testable rows were accepted (G12's token "Nil" has no digits, skipped). Before the whole-number rule, a substring match let one through only because of that skipped row; the whole-number rule is still tested separately.
- FTS5 misses at k=5: G01, G02, G03 (all gold page 6), G08, G11. Cause UNCHECKED; the question words ("total income") are generic and the number is on a highlights page.

## Honest limits
- 16 rows, one report, questions written by me in the same session: easy to over-read. Not yet tested: calls, decks, announcements, other years, the 3 not-in-corpus refusals through retrieval.
- Digits found on the page do NOT prove the number belongs to the asked line item. A human or a label check is still required.
- Provenance `null_test_verifier.py` could NOT be run here: its `index_full.db` is empty in the local checkout (and that checkout has uncommitted changes in retrieve/generate/run_gem). It only guards edits to `provenance/src/verify.py`; this work did not touch provenance, so acceptance (1) holds by not modifying it. UNCHECKED: the null test itself.
- Not built: the `ask` CLI, an index over calls/decks/announcements, Obsidian routing.

## Correction to earlier notes
Page counts are FY22 496, FY23 517, FY24 473, FY25 558, FY26 558. The handoff's 497/518/474/559/559 counted `manifest.json` as a page. Pages were made by `pymupdf4llm` (per each year's manifest.json), which is AGPL; this is the existing pipeline, not mine.

## Next, if continued
1. Add calls, decks, announcements to the same index and add golden rows for them.
2. Look at why G01-G03 miss (page 6) before adding vectors; vectors did not fix them.
3. Decide with the owner on AGPL (`pymupdf4llm`) for the page files.

## Run 2 (2026-11-05): year fix + calls/decks/announcements in one index
- Year spellings (26FY, FY 2026, FY2025-26 -> FY26) normalised in index and query (`page_index.normalize_years`). AR hit@5 11 -> 12 of 16; fake accepted 0. G01-G03 (page 6) and G11 still miss: long pages out-score the short highlights page. Reported as a limit, no question-specific tweak.
- `multi_index.py`: calls cut at form feeds (all 8 calls have them; only 6 have "Page N of M" footers; page numbers NOT checked against printed footers), decks from decks-layout page headers, announcements one row per chunk. 566 chunks (197 call, 209 deck, 160 announcement). Derived files not indexed.
- New golden rows `golden_new.jsonl` (C01-C08, A01-A08), drafted by a subagent, token-in-chunk checked, `human_checked=false`. Zero deck rows yet.
- Results (`eval_multi_index.py`): announcements hit@5 8/8; calls hit@5 6/8 (75%, below the 80% bar -- C01, C05 miss; not tuned). Fake accepted 0. Sample is 8 rows, 1 row = 12.5 points.
- 2026-11-05: owner opened source PDFs and confirmed 10 of 16 new rows (C01-C06, A01, A03, A05, A07) -> human_checked=true. C07, C08, A02, A04, A06, A08 still unchecked.
- Diagnosis of call misses C01, C05: (1) OR-matching counts filler words (what/was/the/for/in/s); (2) the quarter tag (Q2FY23) is in the file name, not the page text, so the right call is not singled out. Fixes proposed (stopwords; index label with text), NOT applied or tested.
- Deck rows D01-D08 added (subagent-drafted, token-on-page checked, human_checked=false). Deck hit@5 = 1/8. Same cause: every quarter's deck has the same slide titles and the quarter lives only in the file name.

## Run 3 (2026-11-05): two general fixes, applied
`query_terms` drops filler words; chunk label + quarter tag (from file name) are indexed with the text. hit@5 before -> after: decks 1/8 -> 7/8; calls 6/8 -> 6/8 (C01 fixed, C06 newly missed: decks of the same quarter now out-rank its call page); announcements 8/8 -> 8/8; annual report 12/16 -> 12/16. Fake accepted 0 everywhere. C05 and D06, G01-G03, G11 still miss. One row regressed (C06); kept because net 27 -> 33 of 40, but flagged. Rows are not tuned to individual questions.

## Run 4 (2026-11-05): the still-missing six
Tried two general rerankers over the top 60 (scratch `exp_rerank.py`, not committed): term coverage, and adjacent-pair phrase bonus, alone and together. Totals of 40 (baseline 33): coverage 32, phrase 31, both 31. None beat the baseline, so search is unchanged.
Strict misses (gold page not in top 5) vs answer text anywhere in the top 5: D06 -- answer is on the same deck's p10 (gold lists p8); G01 -- on AR p347/p241; G02 -- p413/p241/p70; G03 -- p241; G11, C05, C06 -- not in top 5 at all. So 4 of 6 strict misses did surface the right numbers on another page; 3 are real misses. The strict score is kept as the bar; the looser reading is reported beside it.
- 2026-11-05: owner opened source links for the remaining 14 new rows (A02, A04, A06, A08, C07, C08, D01-D08): all confirmed. golden_new.jsonl now 24/24 human_checked. The 16 annual-report rows in golden.jsonl remain unchecked.

- 2026-11-05: owner opened the FY26 annual report PDF and confirmed all 16 annual-report rows (G01-G16). All 40 golden rows are now human-checked. Page numbers remain my own file counts, not checked against printed pages.
