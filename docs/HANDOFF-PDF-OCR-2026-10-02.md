# Handoff: PDF reading + OCR (2026-10-02)

Read this first if you touch PDFs, OCR, or are asked "does llama-index / Jev / Laya help with document extraction?".
Status: **done and merged** (PR #29, merge commit `18c1c2b`). Nothing in flight.

## TL;DR
- Question: does run-llama tooling (plus Jev/Laya) improve extraction from transcripts, annual reports and financial PDFs?
- Answer: **only LiteParse, and only on pages with no text layer.** Page-finders (MiniLM, zero-shot Laya) in front of Claude made results worse.
- Built: `src/media_core/pdf_text.py`, the **single PDF reader** (pypdf first, LiteParse OCR only on image-only pages), plus a guard test and a CLAUDE.md rule so nothing else reads PDFs.
- Installed: local Mac env `~/.venvs/soic` (Py 3.13) and VPS env `~/venvs/pdf-text` (`hostinger_vps`, Py 3.12). OCR verified on both.

## What was measured (6 real public PDFs, 58 facts + 12 "not in the doc" traps, answer key read off page images)
| Setup | Facts right | Notes |
|---|---|---|
| pypdf -> Claude | 40/58 | scanned filing 0/9, chart deck 0/9; never raised an error |
| LiteParse on every page -> Claude | 53/58 | but 907 s on a 196-page annual report |
| MiniLM top-4 pages -> Claude | 36/58 | recall@4 only 0.40-0.55 on the long reports |
| MiniLM + zero-shot Laya -> Claude | 10/37 (small docs) | Laya recall worse than MiniLM on all 4 docs; base checkpoint better than typed-decisions but still below MiniLM |
| **Shipped hybrid (pypdf + OCR on empty pages)** | text coverage 52/58 | = LiteParse-everywhere; ~15 s on that report, 11 s on a 527-page one |

Other facts: no arm ever invented a value (0 wrong, 0 invented on null questions); Claude + grep got 21/21 on two long born-digital annual reports; OCR still misses numbers drawn inside chart images (4 of the 5 remaining misses).
Full report + raw tables + scripts (git-ignored, throwaway): `output/llama_extraction_spike/SPIKE_REPORT.md` in the worktree `llama-index-document-extraction-fc8963` (may be gone; the numbers above are the durable copy).

## What is in the repo now
- `src/media_core/pdf_text.py` - `extract_pdf_text(path)` returns per-page text with `source` = `native` / `ocr` / `empty`. Raises `OcrUnavailable` (pages need OCR, LiteParse missing) or `PdfTextError` (unreadable / no text at all). A page needs OCR if it has < 20 non-space chars.
- CLI for agents/scripts: `python -m media_core.pdf_text doc.pdf --out DIR` writes `DIR/p001.txt, p002.txt, ...`; then grep those files (the layout that scored 100% on the annual reports).
- `tests/test_pdf_text.py` (19 tests) and `tests/test_pdf_ingest_guard.py` (guard). `pyproject.toml`: `pypdf` core dep, `ocr` extra (`liteparse`, Python >= 3.10).
- `CLAUDE.md` -> Key conventions: "PDFs are read ONLY through `media_core.pdf_text`".

## Where to use it (the rule: every PDF goes through it)
- Company filings for stock work: annual reports, results filings, investor decks, concall transcripts. These were the test set.
- Candidates I saw on this Mac but did not run (unverified): `~/Downloads/SOIC/Growth Triggers Prompt.pdf` (16 pp, almost no native text, so image-based); the 56 Asian Paints filings under the Nau-Tabaq `projects/stock-screener/downloads` folder; investing research PDFs in `~/Downloads/Investing Research/`.
- Any capture/skill that ingests a PDF (course slides, dossiers, learning packs as *inputs*). Generating PDFs (`scripts/_pdf_export.py`) is unrelated.
- Not covered: the separate Nau-Tabaq repo has its own code and is not under this guard.
- OCR is local only: documents never leave the machine. Sending a filing to LlamaParse/LlamaExtract is a separate explicit decision (public docs only).

## How it is enforced
1. Single entry point; fails loudly instead of returning blanks.
2. `tests/test_pdf_ingest_guard.py` fails if anything under `src/ scripts/ mcp_servers/ webapp/backend/ .claude/` imports a PDF/OCR library (pypdf, pdfplumber, fitz, liteparse, pytesseract, llama_parse, ...) or shells out to `pdftotext`/`tesseract`, except `pdf_text.py`. One reasoned exemption: vendored `.claude/skills/last30days/` (never point it at a financial filing).
3. CLAUDE.md rule for agents. **Not enforced by code:** an agent using its own PDF-read tool or a raw shell `pdftotext`. A PreToolUse hook could block that; not built.

## Environments
- **Mac:** `~/.venvs/soic` (Py 3.13), editable install pointing at the *worktree*. If the worktree is deleted, re-install from the main checkout: `uv pip install --python ~/.venvs/soic/bin/python -e ".[dev,ocr]"`. The project's own `.venv` is Py 3.9, which cannot run LiteParse (needs >= 3.10) and was left untouched.
- **VPS** (`ssh hostinger_vps`, Ubuntu 24.04, Py 3.12): isolated `~/venvs/pdf-text` (pypdf, pydantic, liteparse + `--no-deps` install of a `git archive` of main in `~/pdf-text-src`). Real OCR check: 17 scanned pages in 18 s, ~480 MB peak. Update after reader changes:
  `git archive origin/main pyproject.toml README.md src | ssh hostinger_vps 'tar -x -C ~/pdf-text-src' && ssh hostinger_vps '~/venvs/pdf-text/bin/pip install --no-deps --force-reinstall ~/pdf-text-src'`
- `~/soic` on the VPS is the soic-ladder Actions runners, **not this repo**; `system-one.service` also runs there. Neither was touched.

## Known limits / not tested
- Chart images: OCR drops some numbers. Needs a vision pass or LlamaParse's chart handling (untested). Cloud LlamaParse/LlamaExtract were never run (needs a LlamaCloud key; public PDFs only).
- Hosted Jev was unavailable that session; Laya was only tested as a zero-shot page-finder (not fine-tuned, not on classification/triage, not on the two long reports). Do not read "Laya was bad here" as "Laya is bad".
- The `<20 chars -> OCR` rule is tested on 6 docs, not broadly. A chart slide with a long native title would skip OCR.
- Python 3.9 compatibility of the new module was not run (no 3.9 here).
- Small sample (58 facts, 4 of 6 docs Asian Paints), one run per cell, one extractor model.
- LlamaIndex's own leaderboards are vendor-published; this spike neither confirms nor refutes them.

## Gotchas learned
- macOS is case-insensitive: `report.md` and `REPORT.md` are one file; `cat a >> A` made a 16 GB file and froze the shell tools (`pkill -x cat`, then delete). Use distinct names.
- A guard that skips paths containing `/worktrees/` silently scans nothing when the repo itself lives under `.claude/worktrees/`. Judge paths relative to the repo root (fixed + tested).
- LiteParse `is_complex()` flags nearly every page of image-rich annual reports (193/196) - not a usable router; use pypdf's empty-page signal instead.
- Subagent token counts include ~90k fixed overhead; do not compare arms by tokens.
- This 8 GB Mac swaps when Laya (MPS) and LiteParse OCR run together: run them one at a time.
- Parallel subagents told to write `DIR/answers.json` once wrote to the parent folder and overwrote each other: give each an absolute output path.

## Open items (all optional)
- Run `/graphify .` (graph flagged stale after the commit).
- Existing, unrelated: `tests/test_citation_audit.py::test_known_citation_defects_are_still_reported` hangs; 9 other tests need git-ignored `data/` or a sibling worktree.
- Maybe: test LlamaParse on the chart deck + scanned filing only; add a PreToolUse hook; script the VPS update.

## Suggested skills for the next session
`test-driven-development` (the repo's tests are the spec), `verification-before-completion`, `system-one` (tier ladder: code -> embeddings -> Jev/Laya -> Sonnet -> Opus), `karpathy-guidelines`/`ponytail` (keep it small).

## References
- PR: https://github.com/syedamber91/knowledge-toolkit/pull/29
- Code: `src/media_core/pdf_text.py`, `tests/test_pdf_text.py`, `tests/test_pdf_ingest_guard.py`, `CLAUDE.md` (Key conventions)
- Source repos evaluated: run-llama/liteparse, run-llama/jev_vs_oss (the Jev/Laya + LiteParse recipe), run-llama/ExtractBench, run-llama/ParseBench
- Memory notes: `llama-index-extraction-spike.md`, `feedback-macos-case-collision-cat.md`
