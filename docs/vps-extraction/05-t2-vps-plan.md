# T2 — Run the existing BIOCON jobs on the VPS (plan, 2026-11-04). NOT RUN YET.

## Correction to the handoff
Handoff A says trigger with `git push origin HEAD:run/<job>/<name>`. **That cannot select a case-study mode.** Read from soic-ladder `.github/workflows/soic-run.yml` @ main (6f97ab9): a `run/**` push "carries no inputs"; the case-study MODE comes from the `companies` input; blank mode → `soic_run.sh` exits 1 ("There is no default mode"). So use workflow dispatch:

```bash
gh workflow run soic-run.yml --repo syedamber91/soic-ladder --ref main \
  -f job=case-study -f companies=<mode> [-f as_of=<YYYY-MM-DD>]
```
- `case-study` is already a dispatch choice (workflow line 109) → the "new job name" trap does not apply.
- Company is hard-coded `CASE_STUDY_COMPANY="BIOCON"` (soic_run.sh line 9013).
- Default snapshot date is `2026-08-30`. A run with no `as_of` regenerates the 2026-08-30 files → perfect for the idempotence test (T2 done-when d).
- Each run ends as a PR titled `results: case-study <date>` on soic-ladder (private). Merging it is a separate decision. Never merge without the owner.
- Never run from the stale local clone; dispatch uses GitHub `main`, which is right.

## Order (cheapest, offline first)
| # | mode | network? | model? | proves |
|---|---|---|---|---|
| 1 | excerpts | no | no (per comments) | idempotence: expect EMPTY diff vs committed files |
| 2 | management-text | no | no | same |
| 3 | qa-pairs | no | no | same |
| 4 | screener | no | no | same |
| 5 | announcements-latest | yes | no | new rows since 2026-08-30; NSE cookie handled by the script (UNCHECKED) |
| 6 | fetch-results / fetch-calls / fetch-decks | yes | no | new Q2 FY27 filing/call/deck if published |

Stop after #1 and read the result before running #2+.

## Done-when for each run (from spec §2b)
1. Output files carry source_url + fetched_at (where the mode fetches).
2. No model-written prose: grep outputs for hedge/summary words; read the run log for any API call.
3. Offline modes: PR diff empty (byte-identical) at default as_of.
4. Counts at the pinned SHA match: announcements 582 rows? (UNCHECKED), FY26 pages 559 ✓ (counted), calls 14? decks 11? results 11? (UNCHECKED).

## Owner decision needed
Dispatching = a real run on the owner's VPS + a PR on a private repo. Needs an explicit yes. Public repo note: outputs stay in private soic-ladder, not in this public repo.
