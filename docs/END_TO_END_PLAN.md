# SOIC Knowledge Toolkit — End-to-End Plan

This document is the single source of truth for what the toolkit does, how the
pieces fit together, and how to take it from a fresh clone to a populated
Obsidian vault on your own machine.

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

### Phase 2 — Confirm selectors (the one manual tuning step)
The live Learnyst DOM is only knowable once logged in. Do a tiny crawl and check
the captured text is real (not nav/boilerplate):
```bash
soic-toolkit crawl --limit 3
```
Open `data/content.json`. If `body_text` / titles look wrong or empty, adjust:
- `crawler.py` -> `SELECTORS` (how courses/lessons are discovered)
- `extract.py` -> `_TITLE_SELECTORS`, `_BODY_SELECTORS` (where lesson text lives)

Re-run the limited crawl until the captured text looks right. (Tip: in the
browser, right-click a lesson's content → Inspect to find the real CSS classes.)

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
