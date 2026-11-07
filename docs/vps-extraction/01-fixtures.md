# T-1 — Frozen fixtures (snapshot 2026-11-04)

Rule: every "done when" in T2/T4/T5/T6 is checked against THIS snapshot, never live.
Tool: `scripts/vps_extraction/freeze_fixture.py` (`freeze`, `verify`). Tests: `tests/test_freeze_fixture.py` (3 pass).
Public repo: filing/Screener text is NOT committed here. Only hashes + pins.

## A. Pinned in git (immutable by SHA) — soic-ladder (private) @ `6f97ab9a382f9748d5aab71258d903e030858252`
Base: `docs/idea/case-study/BIOCON/`
- `annual-report/FY26/p300.md`..`p319.md` (20 pages; printed page = file page − 4)
- `data/announcements-latest.csv` (T0 says 582 rows in the handoff — UNCHECKED until counted at this SHA)
- `data/calls/call-2025-02-07-q3fy25.txt.gz` (1 call)
- `data/deck-numbers/deck-2024-05-17-q4fy24/` (1 deck's numbers)
- `DATA-LEDGER.md`, `TRUTH-TABLE.md`
Read with: `gh api repos/syedamber91/soic-ladder/contents/<path>?ref=<SHA>`

## B. Saved locally (git-ignored `data/fixtures/2026-11-04/`)
| File | Source | fetched_at | sha256 |
|---|---|---|---|
| screener-BIOCON-consolidated.html | https://www.screener.in/company/BIOCON/consolidated/ | 2026-11-04T18:10:19Z | 9b439bcf6f4ddc1e2ac1db9fde9ca6c4b50287b9ce3f95b8c1ab97cc4899cdb8 |

Values in this snapshot (for T5 test): price 344, P/E 82.3, ROE 1.40, ROCE 3.61.
Compare the handoff's 2026-11-03 view: price 343, P/E 77.0. **P/E moved 77.0 → 82.3 in one day** — proof that live pages drift; tests must use the fixture.

## C. Not captured yet
- NSE announcements JSON: API needs a cookie first. UNCHECKED. Do it on the VPS (T2).
- Licence of committing Screener/NSE text: UNCHECKED. Kept out of git until decided.
