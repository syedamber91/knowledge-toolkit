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

## Run 5 - the three misses (2026-11-05)
Fixes, all general (none names a question). Honest eval now runs a real `search(k=K)` for each K.
- Quarter in the question ("Q3FY24") puts that quarter's chunks first. Fixed C05.
- Source word ("call", "deck", "press release") puts that source first. Fixed C06.
- Long words (10+ letters) also match by their first 8 letters ("capitalised" finds "capitalisation"). Fixed D03/D07 side effects; decks 7 -> 8.
- Tried and dropped: a forced slot per source (net -1), Porter stemming (AR 12 -> 11, decks 7 -> 6).
Scores hit@5 (strict gold page): calls 8/8, announcements 8/8, decks 8/8, annual report 12/16. Net 36 of 40 (was 33). Fake accepted 0.
Still missed: G01, G02, G03 (answer is on another page, p6 is a short KPI page) and G11 (gold at rank 9; page says "capitalisation", note "finance costs"). Reported, bar not moved.

## Run 6 - `ask` command (2026-11-05)
`PYTHONPATH=scripts:src python scripts/vps_extraction/ask.py "question" --data BIOCON/data --ar BIOCON/annual-report/FY26 [--number "7,245"] [-k 5]`
- Searches the AR index and the calls/decks/announcements index; each hit shows source, page/date and a snippet.
- With `--number`: OK only if those exact digits are on a retrieved hit; else REFUSE (exit 1). No memory fallback.
- Unchecked: the two indexes' BM25 scores are merged by raw score (rough; each index has its own scale). Live check: guarantee 7,245 -> OK on AR p324; fake 999,111 -> REFUSE.
- Not built: Obsidian routing (what "route to a vault" means is not defined in the spec); graphify refresh.

## Run 7 - `ask --note` (2026-11-05)
`--note VAULT/BIOCON.md` appends one dated section (question, OK/REFUSE, cited hits) to an Obsidian note; creates it with frontmatter if missing; never overwrites.
BIOCON note: iCloud vault "Stock Framework" -> `ask-notes/BIOCON.md` (own folder, so the vault builder's `companies/` is untouched). Two real runs logged (AR p324 guarantee; call 2024-02-09 p7 Syngene).
Not done: no `Home.md` / `Log.md` link to the note (those are builder-owned in that vault); tests 27 pass.

## Run 8 - T6 harness (2026-11-05, built here, NOT yet run)
`scripts/vps_extraction/t6_models.py`: retrieves top-k hits per golden row (ask, 900-char excerpts), shows a model ONLY those, demands JSON `{answer, cite}` or `{refuse}`, scores by code (number in answer AND on the cited hit AND cite was shown; unanswerable rows pass only on refusal). 3 reps, min-max, noise floor = 100/N points. Scorer tested offline (9 tests, incl. made-up number, wrong cite, never-retrieved cite).
- Ceiling: with k=5 only 33 of 40 answerable rows even show their numbers to the model (31 at k=3); no model can beat that.
- Run it on the VPS (key in `$SOIC_ROOT/.env`, never printed): see the usage block at the top of the file. Needs NIM model ids (not chosen yet).
- Unchecked: the real NIM call (`nim_call`) has never run; endpoint/response shape taken from the OpenAI-compatible NIM docs from memory.

## Run 9 - T6 combination: Nemotron + Jev + Laya (2026-11-05, built here; run results in Run 10)
`scripts/vps_extraction/t6_combo.py`. Nemotron answers from the short hits; Jev (typesafe_sdk noul question, hosted) and Laya (local noul question) act as gates that can only turn an answer into a refusal; fail closed, errors counted. One set of Nemotron replies is shared by four arms (`nemotron`, `+jev`, `+laya`, `+jev+laya`) so arms differ only by the gate. Table adds "blocked right" (good answers a gate wrongly stopped) and "caught wrong" (bad answers it stopped). 11 offline tests; scorer is code.
- Unverified: `jev_verify` result shape (parser accepts any dict with `verdict`; unknown shape = counted error); Laya zero-shot is overconfident (noul 0.6-0.9), so `--laya-min 0.5` is a weak gate - tune on a held-out split, not these 40 rows.
- Advisory only: measures the tiers; gates nothing in the repo (G2 / verify_briefs unaffected).
- Needs on the VPS: `NVIDIA_API_KEY` and `TYPESAFE_API_KEY` as project environment variables (read from the environment; `--env` file is optional), `LAYA_DIR`, and the Nemotron NIM model id (`--model`).

Run path found (2026-11-05): the keys are GitHub Actions secrets of `syedamber91/soic-ladder` (`NVIDIA_API_KEY` 2026-09-12, `TYPESAFE_API_KEY` 2026-09-21; checked by name with `gh secret list`, values never read). soic-ladder's `soic-run` workflow runs jobs on the self-hosted VPS runner; a job must be added to `scripts/soic_run.sh` (10,077 lines, JOBS list at line 61) and the `job:` choice list in `.github/workflows/soic-run.yml`, merged to `main`, then dispatched (the workflow header notes the first trigger after a merge can still hit "unknown job"). Existing precedent: job `jev-vs-nemotron`. Nemotron id used by the repo's briefs: `nvidia/nemotron-3-super-120b-a12b` (404s on this account today; the only callable one found is `nvidia/nemotron-3-ultra-550b-a55b`, pass it with `-f companies=<id>`). No new secret is needed.

## Run 10 - T6 combination results (2026-11-05/06, soic-ladder job `t6-combo`, Nemotron Ultra)
Model `nvidia/nemotron-3-ultra-550b-a55b`, 44 rows x 3 reps, top-5 hits, 2000 max tokens. One row = 2.3 points (noise floor).

| Run | Nemotron alone | +Jev | +Laya | +Jev+Laya | Note |
|---|---|---|---|---|---|
| 42068847813 (before fix) | 9-14% | 9-14% | 9-11% | 9-11% | Scorer bug, see below. Ignore. |
| 42080207585 | 64-71% | 64-71% | 43-55% | 43-55% | 8 of 132 calls with no usable reply |
| 42102477040 (+ threshold sweep) | 52-64% | 52-64% | 46-50% | 46-50% | 29 of 132 replies had no JSON |

- **Bug found and fixed (PR 1302):** the prompt shows labels as `[AR p347]`; the model copied the brackets; the scorer rejected 96 of 132 replies as "cite is not a shown label". `parse_reply` now strips them.
- **Threshold sweep (PR 1304):** each gate's cutoff picked on even rows, scored on odd rows (no extra model calls). Result for BOTH Jev and Laya: best cutoff = 0.0 (never block). Held-out gain +0. Jev is +0 at every cutoff up to 0.9 (-18 at 0.95). Laya is +0 up to 0.25, then loses answers (-9 at the old 0.5, -34 at 0.8+).
- **Why they cannot help here:** a gate can only turn an answer into a refusal. "Caught wrong" was 0 in every run, so blocking only removes right answers. On this exam the wrong answers are mostly format/JSON/cite problems, not claims the excerpt contradicts.
- **Unstable baseline:** plain Nemotron moved from 64-71% to 52-64% between runs (no-JSON replies 9 -> 29). That swing is larger than any gate effect. Fix the empty/non-JSON replies before comparing anything else.
- **Not tried:** other callable Nemotron ids; other Jev question wordings; a bigger exam (44 rows, 22 per half); grep-only baseline on the same rows.
- **Verdict (advisory, gates nothing):** on this fact-lookup exam Jev and Laya add nothing as answer filters. Do not wire them in.

## Run 11 - after the timeout fix (2026-11-06, run 42204763812, PR 1306)
Cause of the empty replies: 29 of 132 Ultra calls died on the client's 120 s read timeout (not retried). Fix: 300 s wait, 3 tries; job limit 240 min. Result: empty replies 29 -> 11 of 132.

| Nemotron alone | +Jev | +Laya | +Jev+Laya |
|---|---|---|---|
| 63.6-72.7% | 63.6-72.7% | 52.3-54.5% (19 right answers blocked) | 52.3-54.5% |

Sweep again: best cutoff for Jev and Laya = 0.0 (never block); held-out gain +0. Wrong plain replies (39 of 132): 13 cite not a shown label, 11 no usable reply, 10 refused an answerable row, 5 number missing from the answer. Baseline is now steady across runs 2 and 4 (64-71% vs 64-73%). Conclusion unchanged: Jev and Laya add nothing here.

## Correction after an Opus adversarial review (2026-11-06)

Runs 10 and 11 said "Jev and Laya add nothing". That was **not proven**. What the review found, and what was measured offline (same 44 rows, no model calls):

- **The old scorer gave a gate no way to earn a point.** A refusal on an answerable row counted as wrong, so a gate could only gain on the 4 refusal rows, which the model already refused. "Caught wrong = 0" and "best cutoff = never block" were built into the scorer. They say nothing about Jev or Laya.
- **Some misses were the exam's fault.** Two rows (A06, A07) have no digits and could never pass; six rows (G07, G08, G10, G14, G15, C04) had the number on the retrieved page but outside the 900-char excerpt. 13 correct-looking replies failed on cite format.
- **The "timeouts" story fits only run 3's drop (120 s read timeouts).** Run 11's 11 remaining empty replies were `finish=length`: the model spent its 2,000 tokens thinking.
- **"Steady baseline" rested on 2 runs**, each swinging about 9 points between reps.
- **Grep was never compared.** Measured: the right number is on the retrieved pages for 37 of 40 answerable rows. Picking the right line scores 19 of 44 (43%) with the old 900-char excerpts; best possible with those excerpts was 35 (80%); Nemotron got 28-32. Grep matches the best possible on announcements (6 of 6), loses on annual-report tables (3 of 10) and decks (2 of 8). So the model is needed for tables, not for prose.

Fixes (soic-ladder PR #1308): three-way scoring (right +1, refused 0, wrong -1), loose cite match, the model sees and the scorer checks up to 6,000 chars of page text (offline ceiling 35 -> 41 of 44), words-based check for rows without digits, `grep-only` and `grep-first` arms. Offline with the wider text, grep-only scores 24 right / 1 refused / 19 wrong. Not yet re-run with the model: runs 10-11 numbers above are from the old exam and are not comparable.

## Run 12-13: the fair exam, and Claude's own BIOCON tables as the answer key (2026-11-06/07)

Same model (Nemotron Ultra), fixed exam: right +1 / refused 0 / wrong -1, loose cite match, up to 6,000 chars of page text shown and scored, gate finds cites the same loose way (a first fair run had a gate bug that blocked 20 right answers itself). Reports: soic-ladder PRs #1315 (golden) and #1316 (truth table).

**Golden exam, 44 rows x 3 reps (PR #1315):**

| arm | right % | right / refused / wrong / none | utility |
|---|---|---|---|
| Nemotron alone | 86.4-88.6 | 116 / 5 / 6 / 5 | +110 |
| + Jev | 84.1-88.6 | 115 / 7 / 5 / 5 | +110 |
| + Laya | 72.7-77.3 | 99 / 24 / 4 / 5 | +95 |
| grep, model on tables | 79.5-81.8 | 107 / 5 / 16 / 4 | +91 |
| grep alone | 54.5 | 72 / 3 / 57 / 0 | +15 |

**Truth-table exam, 117 questions, 1 rep (PR #1316)** - one question per cell of `docs/idea/case-study/BIOCON/truth-table.csv` (Claude's finished table, values >= 1,000), searched in the quarterly-filing statement excerpts (`data/excerpts/consolidated-*.txt`, source `filing`):

| arm | right | refused | wrong | none | utility |
|---|---|---|---|---|---|
| Nemotron alone | 91 (77.8%) | 20 | 2 | 4 | +89 |
| + Jev | 91 | 20 | 2 | 4 | +89 |
| + Laya | 8 | 105 | 0 | 4 | +8 |
| grep alone | 6 | 0 | 111 | 0 | -105 |

Read: the model is worth keeping for table cells (grep finds the page, cannot pick the column or quarter). Jev is neutral, Laya hurts, on both exams; neither caught a wrong answer. Sweeps on unseen rows: Jev +0 to -3, Laya +0 to -39.

**The 20 truth-table refusals, looked into:** the model was right to refuse in all 20 - the gold number was on no excerpt it was shown (checked offline against the saved replies, `t6-truth-2026-08-30.replies.json`). Cause 1 (15 rows): a filing is only 4-5k chars, the window was centred on the first query word (late in the text) and cut the number off. Cause 2 (5 rows): the wrong quarter's filing ranked first (an ISO date in the question did not rank that date's chunks first). Fix (soic-ladder PR #1317): a page that fits the cap is shown whole; a date in the question ranks that date first. Offline ceiling on the truth rows 93 -> 117 of 117, golden 41 -> 43 of 44 (G11 is the one that stays missed). **Not yet re-run with the model** - Run 13's refusal count is the old window's.

**Not verified:** the scorer only checks the number is on the cited filing (a prior-quarter number in the same table would also pass); the truth table is Claude's work, tied to XBRL for some quarters only, so a mismatch is "check", not "wrong"; one rep on the truth rows.
