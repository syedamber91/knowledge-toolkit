# T0 — Asset map (2026-11-04)

Method: GitHub API trees (`gh api .../git/trees/<branch>?recursive=1`). Not local clones.

**Trap found:** local `soic-ladder` clone is stale. Its `origin/main` = `631ddfb`; real GitHub `main` = `6f97ab9` (2026-11-03). Local clone sits on `feat/idea-framework`, 68 behind, has broken ref names ("origin/main 2") that break `git log --all`. Always query GitHub, or fetch first. My first "not found" report was wrong because of this.

| Asset | Repo / branch | Path | Found |
|---|---|---|---|
| VPS runner | soic-ladder `main` 6f97ab9 | `scripts/soic_run.sh`, `docs/CLOUD-WORKFLOW.md` | YES |
| Fetch calls/results/decks | soic-ladder `main` | `scripts/case_study_fetch_urls.py` | YES |
| AR pages job | soic-ladder `main` | `scripts/case_study_annual_report_pages.py` | YES |
| Announcements | soic-ladder `main` | `scripts/case_study_announcements.py`, `_live.py` | YES |
| Excerpts | soic-ladder `main` | `scripts/case_study_excerpts.py` | YES |
| Q&A splitter | soic-ladder `main` | `scripts/case_study_qa_pairs.py`, `case_study_qa_states.py` | YES |
| Deck layout | soic-ladder `main` | `scripts/case_study_deck_layout.py` | YES |
| Deck probe reports | soic-ladder `main` | `docs/reports/deck-probe/` | YES |
| BIOCON data | soic-ladder `main` | `docs/idea/case-study/BIOCON/` (3429 files; AR pages FY22 497, FY23 518, FY24 474, FY25 559, FY26 559) | YES |
| Handoffs (master, A, B, local-models) | roast-room `integration/free-model-offload` | `docs/handoff-2026-11-04-master.md`, `handoff-A-extraction-vps.md`, `handoff-B-soic-framework.md`, `handoff-local-models-vps-test.md` | YES (not on soic-ladder; handoff said they were) |
| Model trial results | roast-room same branch | `docs/courtroom-model-trial-1-results.md`, `courtroom-model-trial-2-local-results.md` | YES (not in soic-ladder) |
| Courtroom scripts | roast-room same branch | `.claude/skills/courtroom/scripts/` (`check_hearing.py`, `add_after_panel.py`, `model_trial.py`, ...) | YES |
| BIOCON external items | roast-room same branch | `docs/company-record/biocon/external-items-2026-10-30.json` | YES |
| Provenance RAG core | provenance `main` | `src/chunker.py`, `src/embedder.py`, `src/verify.py`, `scripts/null_test_verifier.py` | YES |
| `hearing.md` (225 KB), `case-book.md` (60 KB), `external.md`, `work/judge-final*.md` | roast-room `integration/free-model-offload` | `sessions/2026-10-30-court-biocon-live-example/` | **YES — force-added to git despite .gitignore (corrected after T5b).** Handoff says hearing.md ~397 KB and a 2026-11-01 SOIC-lawyer session; that session is NOT on this branch — UNCHECKED where it is |
| `after-hearing.json` (commit 9ad6c94) | roast-room | not checked | UNCHECKED |
| Search/hybrid code in provenance (RRF, FTS5) | provenance | only chunker/embedder/verify seen by name match; search file not located | UNCHECKED |

## What this changes in the spec
- Handoff files live in **roast-room**, not soic-ladder. Fixed.
- BIOCON data IS in git: T-1 (freeze fixtures) can copy from it.
- The 2026-10-30 `hearing.md` IS in roast-room git; the 2026-11-01 SOIC-lawyer session (397 KB hearing) is not found. T5b v1 used the master handoff + AR pages; rows from the hearing's I1–I10 still to add.
- Stale-clone trap goes into every VPS-job step: fetch before reading.
