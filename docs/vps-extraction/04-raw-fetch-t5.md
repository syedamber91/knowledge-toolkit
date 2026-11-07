# T5 — Raw fetch instead of web-fetch subagents (2026-11-04)

## Result: mostly already built. Reuse, don't rebuild (ponytail).
| Need | Existing piece | Model? | State |
|---|---|---|---|
| Screener top ratios | `src/soic_senses/screener_client.py::parse_top_ratios` (this repo) | none | works on fixture: price 344, P/E 82.3, ROE 1.4, ROCE 3.61, mcap 56,078 cr |
| Screener quarters/annual tables | `parse_statement_section(html, "quarters")` same file | none | works: Sales Sep 2026 = 4,389 |
| Frozen-page → CSV | soic-ladder `scripts/case_study_screener.py` (VPS mode `screener`) | none | ran on fixture: 156 cells, 12 lines; shell page → exits "no quarterly block" |
| NSE announcements | soic-ladder `scripts/case_study_announcements_live.py` (VPS modes `announcements*`) | none | NOT run here: API needs a cookie → do on VPS (T2). UNCHECKED |

## Gap found and closed
`parse_top_ratios("<html>wait</html>")` returns an empty dict and does NOT raise. That is the "read tool that fails silently" trap from the handoff.
Fix: `scripts/vps_extraction/screener_guard.py::require_ratios` raises ValueError if price/P-E/ROE/ROCE are missing. Tests: `tests/test_screener_guard.py` (red first, then 2 pass).

## Findings that change other tasks
- The 2026-11-04 Screener page already shows the **Sep 2026 quarter** (Sales 4,389 Rs crore; Jun 2026 4,336). So Q2 FY27 numbers exist on Screener today. For T1 this means a live same-quarter replay is possible now. Golden N03 rewritten, F02 added (Screener is not the filing).
- This session's 'web-fetch subagent ~35k tokens' (CLAIMED) is replaced for Screener by a function call: 0 model tokens.

## Not done
- NSE JSON fetch (cookie) and ICRA/CRISIL letters: VPS, T2.
- Live fetch from Screener inside a script (done by hand with curl + browser UA here; soic-ladder `refresh-canonical-html` is the VPS way).
