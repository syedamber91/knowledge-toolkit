# VPS cheap extraction — caveman spec (draft v1, 2026-11-04)

Source: Handoff A + master handoff (BIOCON courtroom). Rule: screen, not advice. Never print NVIDIA_API_KEY. Mark unchecked things UNCHECKED.

## 0. The whole thing in 5 lines
- **Problem:** BIOCON refresh burns Claude tokens on chores a script can do.
- **Why it matters:** cloud Claude hit usage limit mid-hearing, ~20 agents died, got re-run. Money + time lost.
- **Fix:** move chores to the VPS (free) and free models. Keep Claude only for judging.
- **In:** BIOCON sources (results, calls, decks, annual report, announcements, Screener).
- **Out:** small text/CSV files in git + a search tool + a cost log. Same answers, fewer tokens.

## 1. Ground truth — what is checked, what is not
| Fact | State |
|---|---|
| This repo up to date with GitHub (main 4373f21) | CHECKED |
| soic-ladder `scripts/soic_run.sh`, `docs/CLOUD-WORKFLOW.md` on origin/main (631ddfb) | CHECKED |
| `docs/idea/case-study/BIOCON/`, `courtroom-model-trial-1-results.md`, `handoff-local-models-vps-test.md`, `case_study_fetch_urls.py` on soic-ladder origin/main | **NOT FOUND on main.** May be on a feature branch or in roast-room. UNCHECKED — T0 resolves |
| Token cost of any step | **NOT MEASURED.** Handoff says "Not counted in tokens: unchecked" |
| "Ten BIOCON issues" I1–I10 and "13 corrections" | Only I3–I9 named + 6 post-hearing findings in master. Full golden set must be rebuilt from roast-room hearing.md. UNCHECKED |
| Q2 FY27 results due 2026-11-04 | Open |

## 2. Tasks — each one: what / why / in / out / done-when

### T0. Find the stuff (new — Fable-style gap fix)
- **What:** locate the missing files (branch/repo), list exact paths + commit SHA.
- **Why:** can't move a job to the VPS if we can't find the job.
- **In:** git branches of soic-ladder, roast-room (integration/free-model-offload), learning-vault-invest.
- **Out:** `docs/vps-extraction/00-asset-map.md`: path, repo, branch, SHA, exists Y/N.
- **Done when:** every asset named in the handoffs has a row; no "probably".

### T1. Map + measure the refresh
- **What:** list every refresh step, tag it model-free / free-model / Claude, measure tokens per Claude step on ONE real refresh (Q2 FY27 is the live chance).
- **Why:** can't claim "N times cheaper" without a before number.
- **In:** one refresh run + usage numbers from the Claude session (usage tool / transcript), not guesses.
- **Out:** `cost-log.csv` (step, tier, model, in_tokens, out_tokens, wall_s, source_of_number) + `step-map.md`.
- **Done when:** every step has a tier; every Claude step has a measured token number or the word UNMEASURED with reason; total = sum of rows.
- **Trap:** hearing numbers already spent are history; estimate only if labelled ESTIMATE.

### T2. Fetch + extract + case-book build → VPS jobs
- **What:** make steps run with zero Claude: fetch-results, fetch-calls, fetch-decks, fetch-annual-reports, annual-report-pages, announcements, excerpts, case-book build.
- **Why:** these are already model-free in design; they just run in the wrong place.
- **In:** company slug (BIOCON), push to `run/<job>/<name>`.
- **Out:** small text/CSV committed to git (page files, excerpts, announcements CSV, case-book.md) with date + source URL per file.
- **Done when:** (a) VPS run ends with 0 Claude calls (log proof); (b) cloud session can `git pull` and read it; (c) file count/row count matches the last hand-run (e.g. announcements 582 rows, FY26 report p001–p559, 14 calls, 11 decks, 11 results); (d) re-run changes nothing (idempotent).
- **Trap:** NEW job name must be on main first + one other run must finish before it resolves (CLOUD-WORKFLOW.md). VPS safety: flock + steal/load refusal; heavy jobs only via `cpu_heavy_job()`.

### T3. Survey existing tools (don't build what exists)
- **What:** find GitHub/skill candidates for: PDF→tables, NSE/BSE filing fetch, concall Q&A split, hybrid retrieval, claim-vs-source check.
- **Why:** hand-built pieces cost tokens and bugs.
- **In:** search; fixed sample = 1 BIOCON annual-report page set + 1 call transcript + 1 NSE announcements pull.
- **Out:** `candidates.md`: name, licence, last commit, fit, tested Y/N, result on sample.
- **Done when:** ≥2 candidates per need tested on the SAME sample; adopt only on test result, never README. Guard: `media_core.pdf_text` is the one PDF reader here; soic-ladder's PyMuPDF exception is pilot-only.

### T4. Retrieval over the BIOCON corpus (provenance pattern)
- **What:** index calls, decks, report pages, announcements. Hybrid search (FTS5 + nomic-embed-text vectors, RRF). Answer from top-k. Check every number mechanically.
- **Why:** stops re-reading page files and hand-grepping.
- **In:** T2 outputs. Question text.
- **Out:** `ask` CLI: answer + for each number: page, file, date. Obsidian/graphify routing picks which vault notes to add.
- **Done when:** (1) `null_test_verifier.py` run BEFORE and AFTER, same result; verify.py NOT weakened; (2) ≥ N golden questions (from T5b) answered with right page cited; (3) a number not in the sources is refused, not guessed.
- **Trap:** page-doubling parse diluted retrieval — one chunk per page, page-bounded. Units: Rs million vs crore. Year of report.

### T5. Raw-fetch instead of web-fetch subagents
- **What:** Screener tables + NSE JSON via curl/regex/pandas; no subagent summary.
- **Why:** each web-fetch subagent ~35k tokens (handoff figure; verify in T1).
- **In:** URL list (Screener consolidated BIOCON, NSE announcements API — needs cookie first).
- **Out:** CSV/JSON with fetch date + URL.
- **Done when:** parsed values equal the 2026-11-03 Screener ones already in hand (price 343, P/E 77.0, ROE 1.40%, ROCE 3.61%); an empty page / 200-shell-page raises an error, never returns blanks.

### T5b. Golden set (new — must exist BEFORE T4/T6 are judged)
- **What:** write the answer key: ten issues + 13 corrections + known traps.
- **Why:** "same answers" is meaningless without a key.
- **In:** roast-room hearing.md, after-hearing.json, master handoff §4 + "Known errors".
- **Out:** `golden.jsonl`: id, question, expected value, unit, source page, date, trap type.
- **Done when:** each row points to a page a human can open; units stated; ≥ the 6 post-hearing findings + 3 error cases (wrong-year report, million/crore mix, 3,856m=385.6cr) present.

### T6. Pick free models per step
- **What:** run NVIDIA NIM / local Qwen on extract, classify, draft against golden set.
- **Why:** cheapest model that doesn't lose answers.
- **In:** golden.jsonl; key from `$SOIC_ROOT/.env` (never printed).
- **Out:** `model-table.md`: step → model → score range over ≥3 reps.
- **Done when:** model passes only if ≥ current output on the golden set across reps (report min–max, not one run); verifier tested before generator.

## 2b. Fixes from Fable review (v2) — these OVERRIDE the task text above

**New T-1. Freeze fixtures.** Save ONE dated snapshot in git: Screener HTML, NSE JSON, 1 call PDF, 1 deck PDF, 20 report pages. Why: live data moves daily (price, announcements), so tests on live data fail for correct code. Done when: every done-when below is checked against the snapshot, never live.

**"Same" rules (caveman: same input, same result):**
- T2 idempotent = same snapshot in → byte-identical files out. Not "live re-run".
- T2 "0 Claude" = content check, not a log line: every file has `source_url` + `fetched_at`; no model-written prose (no summary/hedge text). A VPS cron has no Claude anyway, so a log proves nothing.
- T2 counts (582 rows, p001–p559, 14 calls, 11 decks, 11 results) = pinned to a snapshot date, after T0 confirms them. New quarter = new counts.
- T4 null test: run before/after on the SAME corpus snapshot.
- T5 parse test: against saved Screener HTML (price 343 etc. as of 2026-11-03), not today's page.

**T5b golden set — stronger:**
- ≥30 rows. ≥3 are "answer NOT in corpus" (system must refuse). ≥3 unit traps (million vs crore).
- A human opens the cited page for EVERY row. Do not copy from hearing.md: it is Claude's own old output; a wrong "correction" would reward the same mistake.
- If hearing files are gone: rebuild from the master handoff §4 + Known-errors, mark rows thin.
- Unit goes in the expected value AND in the mechanical check.

**T1 measure — stronger:**
- Do NOT bet on live Q2 FY27 (due today; T0 + T5b won't be done). Use a **same-quarter replay**: run old way and new way on the same frozen quarter.
- Every cost-log row tagged MEASURED or ESTIMATE. Per-step tokens from a transcript are hard; if mostly ESTIMATE, say the ratio is a range, not a fact.
- Usage tool is per-session, not per-step: run one step per session when measuring.

**T6 noise floor:** with ≥30 rows and 3 reps, state the smallest score gap that counts (1 row = ~3 points). Gap below that = tie, pick the cheaper model.

**T3 vs T4 order:** T3 survey retrieval BEFORE locking FTS5+nomic+RRF. Provenance stays the default; a candidate must beat it on the golden set to replace it.

**New small checks (put in T2):**
- Secrets: NVIDIA key and NSE cookie live on the VPS only (.env), never in git or logs. Cookie expires → job must fail loudly, not return empty.
- VPS budget: an embed of 559 pages must fit `cpu_heavy_job()` limits. Test with 20 pages first, then extrapolate.
- Licence: before committing Screener/NSE text to a public repo, check the repo is private or the text is public filings only. UNCHECKED.
- After T4: re-run graphify and the doc→code linker script; otherwise "Obsidian routing" is a hand-wave.

## 3. Order (ponytail: smallest first)
T0 → T-1 → T5b → T1 (replay) → T5 → T2 → T3 → T4 → T6. (T3 can run beside T2.)

## 4. Success numbers
- Tokens per refresh: before (T1) vs after, ratio stated.
- Golden set: same or better.
- Every number → page + date. Zero silent memory fallback.

## 5. Out of scope
Real Shariah screen (needs Mac + NotebookLM); buy/sell advice; deleting stray artifacts; PRs unless asked.
