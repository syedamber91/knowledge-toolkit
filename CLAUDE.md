# SOIC Scraper / Knowledge Toolkit

## What This Repo Does

Generates learning-pack PDFs from Obsidian vault Substack posts (vutr, luc, sdcourse, ben_dicken), runs multi-agent verification loops to score chapter quality, and uploads the final PDFs to Google Drive.

## Key Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/generate_vutr_spark.py` | Spark internals PDF (5 chapters) | `python3 scripts/generate_vutr_spark.py` → `output/vutr_spark.pdf` |
| `scripts/generate_learning_pack.py` | Ben Dicken learning pack | `python3 scripts/generate_learning_pack.py` → `output/ben_dicken_phase1.pdf` |
| `scripts/gdrive_upload.py` | OAuth Google Drive uploader | `python3 scripts/gdrive_upload.py output/vutr_spark.pdf output/ben_dicken_phase1.pdf` |

## Google Drive

- **Folder path:** My Drive → Learning Packs → Spark & Ben Dicken PDFs
- **Folder ID:** `1G0h8cBj9ZXDlXXv97LAj9P0esFwyk5KH`
- **OAuth token:** `~/.config/gdrive_token.json` (scope: `drive.file`)
- **Client secrets:** `/tmp/gdrive_client.json` (project: `knowledge-toolkit-500817`)
- **One-time auth:** `python3 scripts/gdrive_upload.py --auth /tmp/gdrive_client.json`

## PDF Generation → Verification Loop

1. Run the generator script to produce HTML + PDF
2. Run the Workflow verification loop (Ben/Luc/sdcourse agent questions → Justin student answers → examiner scores accuracy + coverage)
3. Any chapter below 9.0/9.0: fix generator script, regenerate PDF, **update CHAPTERS[n].content in the workflow** to match, rerun
4. Iterate until all chapters ≥9.0/9.0

**Critical invariant:** `CHAPTERS[n].content` in the workflow script must be kept in sync with the generator script after every edit. If you fix the PDF but forget to update the workflow strings, scores will not improve.

## Personas / Agents

- `.claude/agents/vutr.md` — Vu Trinh examiner (Spark, Kafka, OLAP, table formats)
- `.claude/agents/lucsystemdesign.md` — Luc examiner (system design decisions)
- `.claude/agents/sdcourse.md` — sdcourse examiner (distributed log processing)
- `.claude/agents/ben-dicken.md` — Ben Dicken examiner (database internals)

## Vault Paths

- Substack posts: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Substack/posts/`
- Output PDFs: `output/` (gitignored intermediate HTML; PDFs committed)

## Branch

Working branch: `claude/eager-gates-UqFZF`
