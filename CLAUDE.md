# CLAUDE.md

Guidance for AI assistants working in this repository. For the human-facing
overview see [`README.md`](README.md); for deep dives see [`docs/`](docs/).

## START HERE — read the knowledge graph first

**Before exploring the codebase or planning any change, read the graphify
knowledge graph.** It is a pre-computed map of this repo — 1119 nodes / 1893
edges across 84 clustered communities — so you can orient in one read instead of
grepping around blind.

1. Read [`graphify-out/GRAPH_REPORT.md`](graphify-out/GRAPH_REPORT.md) — the
   god nodes (core abstractions like `media_core` unified vault builder,
   `MediaCatalog`, `SubstackCatalog`), community map, and cross-cutting edges.
2. For targeted lookups, query the graph instead of re-reading files:
   - `graphify query "how does substack auth work"` — BFS over `graph.json`
   - `graphify explain "MediaCatalog"` — a node and its neighbours
   - `graphify path "SOIC Crawler" "Obsidian Vault"` — shortest path between concepts
   - `graphify affected "media_core models"` — what a change would impact
3. Only after the graph has given you the lay of the land, start your actual
   reasoning/implementation.

The graph is committed (`graphify-out/graph.json` + `GRAPH_REPORT.md` +
`manifest.json`). A `.githooks/post-commit` hook (enable once per clone with
`git config core.hooksPath .githooks`) watches every commit and, when source
files change, **flags the graph as stale** (writes `graphify-out/.needs_update`
and prints a reminder) rather than auto-rebuilding — the pinned graphify's
`update` command is AST-only and would discard this curated semantic layer and
its community labels. To refresh properly, run `/graphify .` (re-extracts code
**and** docs, re-clusters, re-labels). Keep it current — it is the first thing
every session reads.

## Overview

`knowledge-toolkit` is a **personal knowledge-capture toolkit**. It logs into
the user's own accounts, captures only the text those platforms openly render,
and builds cross-linked [Obsidian](https://obsidian.md) vaults so the material
can be explored as a graph. It also generates a database-internals "learning
pack" PDF that is verified by two persona agents.

Six independent toolkits live under `src/`, sharing a small `media_core`. Stack:
**Python 3.9+**, [Typer](https://typer.tiangolo.com/) CLIs, [Pydantic](https://docs.pydantic.dev/)
models, [Playwright](https://playwright.dev/) for browser sessions,
[Instaloader](https://instaloader.github.io/) for Instagram.

**Guardrails (non-negotiable):** no DRM circumvention (never download/decrypt
protected audio/video), no stored passwords (interactive/session-cookie auth
only), personal use only, and nothing captured is ever committed.

## Setup & commands

```bash
pip install -e ".[dev]"     # install package + dev (pytest) extras
playwright install chromium # needed for SOIC + Substack browser login
cp .env.example .env        # configure; never commit .env
pytest                      # run the test suite
```

- Tests live in `tests/` (`testpaths` set in `pyproject.toml`). The unit tests
  for extraction, parsing, topics, and vault building need **no login or
  network**; integration/e2e tests skip themselves without a live session.
- Five installed CLI entry points (`pyproject.toml` → `[project.scripts]`):
  `soic-toolkit`, `substack-toolkit`, `youtube-toolkit`, `web-toolkit`,
  `instagram-toolkit`.

> **README drift — trust the code, not the README.** The README still documents
> a `media-toolkit youtube/web` command. No such entry point exists. The real
> commands are `youtube-toolkit capture …` and `web-toolkit capture …` (each
> with a `build` subcommand). Treat `pyproject.toml` `[project.scripts]` and the
> `.claude/skills/*/SKILL.md` command blocks as authoritative for syntax.

## Repository layout

```
src/
  media_core/        # shared models, catalog store, topic vocab, unified vault builder
  soic_toolkit/      # SOIC/Learnyst portal capture
  substack_toolkit/  # Substack publication capture
  youtube_toolkit/   # YouTube transcript capture
  web_toolkit/       # readable web-article capture
  instagram_toolkit/ # Instagram caption + metadata capture (Instaloader)
tests/               # pytest suite + fixtures/ (sample HTML/JSON; mostly offline)
docs/                # END_TO_END_PLAN, PORTAL_NOTES, LEARNING_PACK_VERIFICATION_WORKFLOW
scripts/             # generate_learning_pack.py (HTML→PDF learning pack)
.claude/             # agents/ and skills/ (see "`.claude/` assets" below)
.env.example         # config template
```

## The six toolkits

| Package | Captures | Auth model | Catalog | Default vault |
|---------|----------|-----------|---------|---------------|
| `soic_toolkit/` | Learnyst portal lessons | Interactive Playwright login → `.auth/state.json` | `data/content.json` | `./vault` (or `SOIC_VAULT_DIR`) |
| `substack_toolkit/` | Free + paid Substack posts | `substack.sid` cookie (from Chrome or login) | `data/substack.json` | `~/Documents/Obsidian Vault/Substack` |
| `youtube_toolkit/` | Video transcripts | none (public, via yt-dlp) | `data/media.json` | `MEDIA_VAULT_DIR` (Obsidian iCloud) |
| `web_toolkit/` | Readable articles | none (public HTML) | `data/media.json` (shared) | `MEDIA_VAULT_DIR` (shared) |
| `instagram_toolkit/` | Public post/reel captions + metadata (no media, no comment text) | `sessionid` cookie (from Chrome or login) — **use a burner account** | `data/media.json` (shared) | `MEDIA_VAULT_DIR` (shared) |
| `media_core/` | — (shared infra) | — | `data/media.json` | builds the unified YouTube+web+Instagram vault |

Per-package files follow a consistent shape:
- `cli.py` — Typer command (the installed entry point).
- `crawler.py` / `capture.py` — fetch logic; resumable and polite.
- `extract.py` — raw HTML/JSON → structured text/Markdown.
- `vault.py` (or `media_core/unified_vault.py`) — catalog → Obsidian notes.
- `models.py` — Pydantic schemas for the catalog.
- `config.py` — env + filesystem paths.

CLI flow is the same everywhere: **login (if any) → crawl/capture → build-vault**.

```bash
# SOIC
soic-toolkit login && soic-toolkit crawl --limit 5 && soic-toolkit build-vault
# Substack
substack-toolkit login --from-chrome && substack-toolkit crawl <handle> && substack-toolkit build-vault
# YouTube + web (share one catalog & vault)
youtube-toolkit capture "https://www.youtube.com/@<handle>/videos" --limit 5
web-toolkit capture "https://example.com/post"
youtube-toolkit build
# Instagram (shares the same catalog & unified vault; USE A BURNER ACCOUNT)
instagram-toolkit login --from-chrome
instagram-toolkit crawl <username> --limit 30
instagram-toolkit crawl-hashtag <tag> --limit 30
instagram-toolkit build
```

## Key conventions (reuse, don't reinvent)

- **Topic vocabulary is canonical and centralized.** The base lives in
  `src/substack_toolkit/topics.py`; `src/media_core/topics.py` reuses and
  extends it with software/system-design/AI terms. To recognize new topics,
  edit these files and rebuild the vault — do not add ad-hoc tagging elsewhere.
  The same topic (e.g. `dbt`) resolves to one shared `topics/<topic>.md` note
  across every source.
- **Resumable + polite by default.** Crawlers track already-captured URLs and
  skip them on resume, save the catalog incrementally after each item, and
  sleep a random 1.5–3.5s between requests. Preserve this when editing capture
  code. Test first with a small `--limit`.
- **Pydantic everywhere.** Every catalog is a validated Pydantic model in the
  package's `models.py`. Add fields there, not as loose dicts.
- **Obsidian output shape.** Notes have YAML frontmatter + body, are wired with
  `[[wikilinks]]`, roll up into MOC (Map-of-Content) notes, and cross-link via
  shared `topics/<topic>.md` notes.
- **Gitignored outputs — never commit.** Per `.gitignore`: `.env`, `.auth/`,
  `data/`, `output/`, `vault/`. These hold sessions and captured content.

## Gotchas / hard-won knowledge

Each capture source has a matching skill with the full recipe — invoke it before
doing source-specific work.

- **Substack** (`/substack-capture`): only the `substack.sid` cookie proves an
  authenticated session — `substack.lli` is just a client-side hint. Paid access
  is **per publication**. A paid post returns a truncated preview marked
  `hidden: true`, so `body_accessible` is true only when the full body came back
  (non-empty body alone is not proof). Verify auth by fetching a known paid post
  with and without the cookie and comparing body length. Use `--free-only` for
  publications you only follow free.
- **YouTube** (`/youtube-capture`): transcripts use a **three-stage fallback** —
  yt-dlp VTT → pytubefix → youtube-transcript-api. Skip Shorts (≤60s) and
  no-transcript videos, marking their URLs seen so resume doesn't retry them.
  Never fabricate a transcript.
- **SOIC** (`/soic-extract`, `docs/PORTAL_NOTES.md`): the Learnyst "Bodhi"
  portal is Next.js + Web Components with **Shadow DOM** and a JS router (no
  `href` links). Pages only hydrate when authenticated, and **reloading a tab
  mid-extraction breaks hydration** — navigate with `location.href`, walk shadow
  roots, and poll for `bodhi-*` elements.
- **Instagram** (`/instagram-capture`, `docs/superpowers/specs/2026-07-04-instagram-toolkit-design.md`):
  Instaloader-backed, authenticated via the `sessionid` cookie imported from
  Chrome (same Keychain-decrypt as Substack). Captures **caption + metadata
  only** — Instaloader is configured with all `download_*` flags off, so no
  image/video/comment is ever fetched; the permalink is kept for manual visual
  review. **Use a burner account** — scraping risks a lockout. IG blocks fast
  scrapers even when logged in, so pace slowly (3–6s) and use small `--limit`;
  the crawler stops politely on a block and resumes on re-run. The
  `post_fetch` seam is injected in tests so extraction/crawl logic runs offline
  without Instaloader or a login. Requires `pip install instaloader` (in
  `pyproject.toml` deps).

## Learning packs, verification loop & Google Drive

`scripts/generate_learning_pack.py` builds an HTML learning pack on database
internals (render to PDF via headless Chrome `--print-to-pdf`, output under
`output/`).

| Script | Purpose | Output |
|--------|---------|--------|
| `scripts/generate_learning_pack.py` | Ben Dicken database-internals pack | `output/ben_dicken_phase1.pdf` |
| `scripts/generate_vutr_spark.py` | Vu Trinh Spark-internals pack (5 chapters) | `output/vutr_spark.pdf` |
| `scripts/gdrive_upload.py` | OAuth Google Drive uploader | uploads `output/*.pdf` to Drive |

**Verification loop.** Each pack's quality is validated through a multi-agent
pipeline that runs until every chapter scores ≥9.0/9.0 on both dimensions, then
requires a final tri-agent sign-off before the PDF is considered complete.

```
Per pass (pipeline over chapters):
  Stage 1 — Examiner generates 5 questions (≥2 trade-off, ≥1 WHY, ≥1 precise term)
  Stage 2 — Justin (student) answers from chapter text
          + Alex audits chapter for clarity gaps   ← parallel
  Stage 3 — Examiner scores accuracy + coverage; Alex audit attached to result

Fix round (if any chapter < 9.0):
  Fix agent applies BOTH examiner gaps AND Alex high/medium improvements → regenerate

Final sign-off (after allPassed = true):
  vutr   — technical accuracy ≥9.0 and coverage ≥9.0 confirmed
  Justin — 6/7 pedagogical criteria met (WHY hooks, recall questions, emotional framing)
  Alex   — no remaining BLOCKERS for a 15-year-old reader
  If any reject → one sign-off fix round → final PDF
```

**Critical invariant:** when a generator script changes, keep the
`CHAPTERS[n].content` strings in the verification workflow in sync — otherwise
scores won't improve even though the PDF did.

Personas/examiners (skills + agents):
- **`justin-sung`** — learning coach; reviews pedagogy (retrieval practice,
  emotional hooks, higher-order thinking, WHY→WHAT→HOW) and plays the student
  who knows only the PDF. Also signs off on pedagogical quality in the final gate.
- **`ben-dicken`** — database-internals examiner; scores accuracy + coverage.
- **`vutr`, `lucsystemdesign`, `sdcourse`** — additional examiners for
  Spark/Kafka/OLAP, system-design decisions, and distributed log processing.
  Each signs off on technical accuracy in the final gate.
- **`alex`** — 15-year-old clarity auditor; reads chapters and produces a confusion
  log + specific additive improvement requests (DEFINE / ANALOGY / BRIDGE / DIAGRAM /
  EXAMPLE / SEQUENCE). Never asks to remove content. Runs in parallel with Justin in
  every verification pass, and signs off on accessibility in the final gate.

**Google Drive upload** — final PDFs go to *My Drive → Learning Packs → Spark &
Ben Dicken PDFs* (folder ID `1G0h8cBj9ZXDlXXv97LAj9P0esFwyk5KH`) via
`scripts/gdrive_upload.py`. OAuth token lives at `~/.config/gdrive_token.json`
(scope `drive.file`); one-time auth:
`python3 scripts/gdrive_upload.py --auth <client_secrets.json>`.
Upload: `python3 scripts/gdrive_upload.py output/vutr_spark.pdf output/ben_dicken_phase1.pdf`.

See [`docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md`](docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md).

## `.claude/` assets

**Skills** (`.claude/skills/`, invoke as `/<name>`):
- `soic-extract`, `substack-capture`, `youtube-capture`, `media-capture`,
  `instagram-capture` — source-specific capture recipes.
- `justin-sung-persona`, `ben-dicken-persona` — the persona frameworks above.
- `alex-persona` — the 15-year-old clarity auditor persona (`/alex` trigger).
- `graphify` (`/graphify`) — turns any folder (code, docs, papers, images) into a
  navigable knowledge graph with community detection and an audit trail, emitting
  interactive HTML + GraphRAG-ready JSON + a plain-language `GRAPH_REPORT.md`.
  Self-bootstrapping: installs the `graphifyy` pip package at runtime if absent.
- `nate-herk-persona`, `jack-roberts-persona` — direct-mentor personas grounded
  in captured YouTube transcripts (`/nate-herk`, `/jack-roberts` triggers); see
  `docs/superpowers/specs/2026-07-05-nate-herk-jack-roberts-persona-design.md`.

**Agents** (`.claude/agents/`): `substack-capturer`, `youtube-capturer`,
`media-capturer`, `instagram-capturer` (capture orchestrators); `justin-sung`,
`ben-dicken`, `vutr`, `lucsystemdesign`, `sdcourse`, `alex` (verification/
examiner personas); `nate-herk`, `jack-roberts` (direct-mentor personas). Note:
agent files reference an absolute project root from the author's machine —
paths there are illustrative, not this repo's path.

## Pointers

- [`README.md`](README.md) — user-facing guide (mind the command drift above).
- [`docs/END_TO_END_PLAN.md`](docs/END_TO_END_PLAN.md) — full runbook & data model.
- [`docs/PORTAL_NOTES.md`](docs/PORTAL_NOTES.md) — Learnyst portal reconnaissance.
- [`docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md`](docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md) — persona verification loop.
