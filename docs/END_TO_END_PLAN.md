# SOIC Knowledge Toolkit — End-to-End Plan

This document is the single source of truth for what the toolkit does, how the
pieces fit together, and how to take it from a fresh clone to a populated
Obsidian vault on your own machine.

> **Update (2026-06-20): the live portal was inspected while logged in.** It is a
> Next.js + Learnyst "Bodhi" web-component PWA — content is in Shadow DOM with no
> anchors, the hierarchy is **Bundle → Course → Section → Lesson**, and lesson
> bodies/transcripts are **protected** (sandboxed iframe + watermark + an explicit
> "Downloading or sharing content is prohibited" notice). See
> [`PORTAL_NOTES.md`](PORTAL_NOTES.md). To honor the no-circumvention / no-A-V-rip
> guardrails, the crawler captures **structure + the openly-rendered AI summaries +
> attachment flags only** — not article bodies and not verbatim transcripts.

## Goal

Log into **your own** SOIC ("School of Intrinsic Compounding") membership on the
Learnyst portal (`learn.soic.in`), collect the lesson text the platform
legitimately displays, and turn it into an **Obsidian vault** of interlinked
notes so Obsidian's graph view reveals how the topics connect.

## Guardrails (non-negotiable)

- **Personal use only.** This is for studying content you already pay for. Review
  SOIC/Learnyst's Terms of Service; run politely (the crawler self-throttles).
- **No DRM circumvention.** Never download, decrypt, or rip protected
  video/audio. Only text the authenticated page renders is captured.
- **No stored password.** Login is interactive; only the resulting session is
  saved locally (`.auth/state.json`).
- **Nothing is committed.** `.auth/`, `data/`, `output/`, `vault/` are gitignored.

## Where it runs

| Concern | Answer |
|---|---|
| Where the code runs | **Your local machine** (Mac/Windows/Linux). |
| Where notes are stored | A folder you choose — point `SOIC_VAULT_DIR` / `--vault-path` at a subfolder inside your real Obsidian vault. |
| Why not in the cloud | Interactive login needs a visible browser + your credentials; cloud sandboxes also block the Playwright browser download and `learn.soic.in`. |

## Architecture

```
src/soic_toolkit/
  config.py    # env + filesystem paths (incl. SOIC_VAULT_DIR)
  auth.py      # interactive login, save/load Playwright session, validity check
  crawler.py   # walk course -> module -> lesson; polite + resumable
  extract.py   # lesson HTML -> structured text (title/body/captions/resources/key points)
  vault.py     # catalog -> Obsidian vault: notes + MOCs + wikilinks + tags
  mindmap.py   # catalog -> Markmap markdown/HTML (optional secondary view)
  cli.py       # soic-toolkit: login | status | crawl | build-vault | build-map

data/content.json   # internal, resumable crawl cache (raw catalog)
vault/              # default vault output (override with SOIC_VAULT_DIR)
output/            # mindmap.md / mindmap.html
```

### Data model (`models.py`)
`Catalog -> Course[] -> Module[] -> Lesson{title, url, body_text, captions_url,
resource_links[], key_points[], crawled_at}`.

### Correlations in the vault (`vault.py`)
- **Structural** — each lesson links to its Module/Course MOC; `Home.md` links courses.
- **Sequential** — prev/next links along lesson order.
- **Content-based** — a *Related* section links lessons sharing the most keywords;
  derived `#tags` cluster topics in the graph view.

## End-to-end workflow

### Phase 0 — One-time setup (local)
```bash
git clone http://github.com/syedamber91/knowledge-toolkit.git
cd knowledge-toolkit
git checkout claude/eager-gates-UqFZF
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env
# Edit .env: set SOIC_VAULT_DIR to a folder inside your Obsidian vault, e.g.
#   SOIC_VAULT_DIR=~/Documents/Obsidian/MyVault/SOIC
pytest            # sanity: all tests should pass
```

### Phase 1 — Authenticate
```bash
soic-toolkit login     # Chromium opens; sign in to SOIC (incl. OTP); press Enter
soic-toolkit status    # expect: "Session looks valid"
```

### Phase 2 — Validate the crawl against the live portal
The crawler has been rewritten for the real Bodhi portal (shadow-DOM reads +
click-driven navigation; see `crawler.py` and `PORTAL_NOTES.md`). The pure
parsing/cleaning helpers are unit-tested against real captured strings
(`tests/test_portal.py`), but the live click-navigation can only be exercised
with your session, so run a small crawl and confirm:
```bash
# Optional: set your watermark identity so it's stripped from summaries
#   SOIC_WATERMARK_LINES=you@example.com|+910000000000  (in .env)
soic-toolkit crawl --limit 3
```
Open `data/content.json` and confirm it shows a Bundle→Course→Section→Lesson tree
with each lesson's `lesson_type`, `duration`, `has_attachment`, and (for videos)
a cleaned `ai_summary`. If section/lesson grouping or summary text looks off,
the things to adjust live in `crawler.py` (`_SHADOW_WALK`, `_SUMMARY_EXTRACT`,
`_course_cards`, click selectors) and `extract.py` (`parse_section_header`,
`parse_lesson_meta`, `clean_summary`).

### Phase 3 — Full crawl (resumable)
```bash
soic-toolkit crawl     # skips already-captured lessons; safe to re-run
```

### Phase 4 — Build the knowledge base
```bash
soic-toolkit build-vault   # writes notes into SOIC_VAULT_DIR (or --vault-path)
# optional secondary view:
soic-toolkit build-map     # output/mindmap.md (+ .html if Node present)
```
Open the vault folder in Obsidian (*Open folder as vault*, or it's already inside
your vault) and turn on the **graph view**.

### Phase 5 — Keep it fresh
Re-run `crawl` (captures new lessons only) then `build-vault` whenever SOIC adds
content. The session in `.auth/state.json` is reused until it expires; re-run
`login` when `status` reports it invalid.

## Verification checklist
- [ ] `pytest` passes.
- [ ] `soic-toolkit status` → valid session after `login`.
- [ ] `data/content.json` has a nested course/module/lesson tree with real text.
- [ ] Re-running `crawl` skips existing lessons.
- [ ] `build-vault` produces `<vault>/Home.md`, course/module MOCs, and lesson
      notes with frontmatter, Related links, and prev/next nav.
- [ ] Obsidian graph view shows clusters/links.

## Backlog / future enhancements
- Smarter module grouping once real section markers are confirmed.
- Optional LLM summarization for richer `key_points`.
- Scheduled headless re-crawls (only after a valid session exists).
- PDF text extraction for openly-served resource links.
