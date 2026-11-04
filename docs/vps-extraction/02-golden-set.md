# T5b — Golden set v1 (2026-11-04)

File: `golden.jsonl` — 34 rows. Checker: `scripts/vps_extraction/verify_golden.py` (4 tests pass).
Run: `PYTHONPATH=scripts python scripts/vps_extraction/verify_golden.py docs/vps-extraction/golden.jsonl <FY26 pages dir @ soic-ladder 6f97ab9> data/fixtures/2026-11-04/screener-BIOCON-consolidated.html`

| Kind | Rows | Meaning | State |
|---|---|---|---|
| page_grep | 16 | number printed on a named FY26 page | **machine-checked: 16/16 pass** |
| derived | 7 | arithmetic on rows above | **machine-checked: 7/7 pass** |
| fixture_grep | 1 | Screener snapshot values | **1/1 pass** |
| not_in_corpus | 5 | system must REFUSE / say "not printed" | needs retrieval test (T4) |
| trap | 2 | wrong-year report; Screener vs AR profit gap | needs retrieval test |
| unchecked_source | 3 | NSE letters / calls, not in fixtures | needs VPS fetch (T2) |

## Meets Fable's bar?
- ≥30 rows: YES (34). ≥3 "not in corpus": YES (5). ≥3 unit traps: YES (G10, G14, G15, D04, D07).
- **Human opened every cited page: NO.** `human_checked` is false on all 34. The machine proves "the number is on that page", not "this is the right question/answer". Owner step: open ~10 pages, flip the flag.

## Honest limits
- Narrow: facts come from the master handoff §4 + Known errors and FY26 AR pages. The hearing's ten issues (I1–I10) and the "13 corrections" are NOT yet mined. Source exists: roast-room `sessions/2026-10-30-court-biocon-live-example/hearing.md`.
- Year order in G08 (FY26 19,940; FY25 40,612) follows the case-book heading "FY2025-26 then FY2024-25"; the page's column header line was not printed in the text read. Human: confirm.
- Rows overlap (same pages), so 34 rows ≠ 34 independent tests; T6 noise floor must use this.
