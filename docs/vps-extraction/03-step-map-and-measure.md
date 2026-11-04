# T1 — Step map + cost log (2026-11-04)

Data: `cost-log.csv`. Status words: MEASURED (a tool printed it), ESTIMATE (worked from a measured ratio), CLAIMED (a handoff says so, not checked), UNMEASURED (no number exists).

## What the numbers say
1. **Fetch/extract steps are probably already model-free.** `soic_run.sh` has one job `case-study` with modes: fetch-results, fetch-gap, announcements, announcements-latest, excerpts, screener, price-panel, fetch-calls, fetch-decks, deck-numbers, management-text, fetch-annual-reports, annual-report-pages, qa-pairs. Job comments say "no model". **I read the comments, not each mode's code → UNVERIFIED.** So spec T2 is mostly "run what exists + commit small outputs", not "write new jobs". The "new job name must be on main first" trap does NOT apply: `case-study` is already in JOBS.
2. **The big Claude cost is the hearing, not the fetching.** One convict turn prompt is 227,531 chars ≈ 67–71k tokens; a 15-turn pass ≈ 1.0–1.07M input tokens (ESTIMATE). This is where retrieval (T4) can bite: trial-2 says a prompt ~10x shorter (6–8k tokens) would be needed for local models.
3. **Free models already failed this step.** Trial 1: all 8 hosted free models FAIL pre-registered bars (best: Nemotron 3 Ultra + retry loop matched Sonnet's guard-fail count but invented 1 quote and missed the state bar). Trial 2: local qwen3.5 4B/9B cannot read one 70k prompt in 330 s on the VPS (CPU-bound). So T6 should not re-run the same test; it should test **short, retrieved prompts**, after T4.
4. **Nothing else has a number.** No billed-token record exists for hearing, closings, web-fetch subagents (35k is CLAIMED), or page re-reads.

## How to measure (replay protocol — needs the owner's go-ahead, it spends tokens)
- Pick ONE frozen quarter (T-1 fixtures). Run each Claude step in its OWN fresh session.
- Before and after the step call `get_usage` (reports session context tokens, plus % of the 5-hour/weekly window). Log delta.
- Caveats: it shows context size, not billed in+out, and ignores cache pricing. Treat as a floor/proxy; label rows MEASURED-CONTEXT. Subagent usage lines (like X1) are exact for subagents.
- Run old way and new way on the SAME quarter. Report the ratio as a range if any row is ESTIMATE.
- First candidate to replay: S10a (one convict turn) — old prompt vs retrieved prompt — because it is the biggest row and the cheapest to run once.

## Acceptance (T1)
- [x] every step has a tier or UNKNOWN: yes (21 rows)
- [x] every Claude step has a number or UNMEASURED with reason: yes
- [ ] a real before/after replay: NOT done (needs go-ahead)
