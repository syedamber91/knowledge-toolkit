# T3 — Tool survey (2026-11-05)

Sample (same for all): Q2 FY27 results PDF `BIOCON_04112026131527_BMOutcome.pdf` (23 pages, 7.1 MB; income statement on page index 8), the NSE announcements for BIOCON, the Q2 excerpt text on soic-ladder main. Tests ran in a scratch venv outside the repo (`/private/tmp/claude-501/t3`); nothing was added to this repo's code or dependencies. Repo rule stands: `media_core.pdf_text` stays the one PDF reader in `src/`; this table only compares candidates.

Ground truth checked: Total income 44,234 | 43,905 | 43,885 | 88,139 | 84,101 | 1,72,695; PBT 548 | 1,276 | 1,713 | 1,824 | 2,682 | 4,479; Sale of products 35,312 | 35,721 | 33,848 | 71,033 | 64,518 | 1,31,453 (Rs million, Indian commas).

## Need 1: PDF to table numbers
| Candidate | Licence / last release | Result on sample | Time |
|---|---|---|---|
| pdfplumber 0.11.10 `extract_tables` | MIT-style; 2026-06 | 1 table, **11 rows, one giant row** (columns stacked in one cell): FAIL as a table | 0.1 s |
| pymupdf 2.1 `find_tables` | **AGPL or paid**; 2026-11-02 | same: 1 mega-row: FAIL as a table | 3.7 s |
| pdfplumber `extract_text()` and `(layout=True)` + line parse | same | **3/3 rows exact** | 0.1 s |
| pymupdf `get_text()` (default) | AGPL | **0/3** (reading order scrambled) | 0.0 s |
| pymupdf `get_text(sort=True)` + line parse | AGPL | **3/3 exact** | 0.0 s |
| pymupdf4llm `to_markdown` | AGPL | 2/3; **silently started Tesseract OCR** | 0.8 s |
Finding: table finders do NOT work on this filing; text lines plus a number regex do. Camelot, Tabula: not tested (Camelot needs ghostscript/opencv, Tabula needs Java; not approved). Pick: pdfplumber text (permissive licence). Caveat: ONE filing tested; other quarters' layouts UNCHECKED.

## Need 2: NSE filing fetch
| Candidate | Last release | Result | 
|---|---|---|
| `nse` 5.1.1 (NseIndiaApi) | 2026-10-30 | 1960 rows for BIOCON; **Q2 outcome URL present**; handles cookie |
| `jugaad-data` 0.37.0 `NSELive` | 2026-10-22 | 1955 rows; **Q2 outcome URL present**; same fields |
Both worked with one call each, from a Mac. Row counts differ by 5 (cause UNCHECKED). Our own `announcements-latest` job already does this on the VPS; adopting either would replace hand-written cookie code. UNCHECKED: do they survive from the VPS IP, and NSE terms of use.

## Need 3: Q&A split of call transcripts
No off-the-shelf tool found. Diarizers (tinydiarize, pyannote) need audio; we have text. Keep `case_study_qa_pairs.py`. Not tested (nothing to compare).

## Need 4: Hybrid retrieval
Found: `scrydb` (arXiv preprint, package existence UNCHECKED), DIY pattern (FTS5 + sqlite-vec + RRF, ~200 lines). Not tested here: retrieval is judged in T4 on the golden set, against provenance as the default.

## Need 5: Claim vs source number check
| Candidate | Result |
|---|---|
| `numaudit` 0.1.0, `onus` 0.1.0 | NOT installed (single release, Sep/Oct 2026; install of unvetted new packages not approved) |
| 10-line presence check (mine, scratch) | 6/6 on a made-up claim list: found 43,889 / 44,234 / 548 / 1,72,695; refused 44,000 and "4,389 crore" |
Limit, stated plainly: presence proves the digits exist in the file, NOT that they belong to the claimed line item (548 could match any 548). The page+label check is still needed.

## What this means (one line each)
- Do not trust table finders on these filings; parse text lines.
- AGPL for pymupdf: avoid in this repo unless the owner decides otherwise.
- NSE clients exist and work; worth a VPS test before replacing our fetch code.
- Nothing adopted yet. Adopt only after VPS run + owner yes.
