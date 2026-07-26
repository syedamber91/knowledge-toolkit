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
- **Every vault builder implements the index + log + cross-links routing
  pattern — this is a standing requirement, not optional.** It's what lets an
  AI agent (or a human) route to the right note efficiently instead of
  re-scanning the whole vault. Three components, all required:
  1. **Index** — `Home.md` (+ per-source MOCs): what exists and roughly where.
     Already covered by the "Obsidian output shape" bullet above.
  2. **Log** (`Log.md`) — an **append-only** running history of *when* content
     was added or removed, distinct from the index (which only reflects
     current state). Implemented once in `media_core/unified_vault.py` as
     `_last_logged_total()` + `_log_ingest()` and reused/replicated across
     every vault builder (`soic_toolkit/vault.py`, `substack_toolkit/vault.py`,
     `media_core/unified_vault.py`'s `build_vault()` and `build_unified()`).
     Contract, do not deviate: parse the last entry's `(N total` to get the
     prior count (no separate state file); word the very first-ever entry as
     a **backfill** ("N item(s) already in vault (log started here)") — never
     claim pre-existing content was "just captured"; on later builds, append
     "N new item(s) captured" or "N item(s) removed" only when the total
     actually changed (never spam a duplicate entry on an unchanged rebuild);
     link `[[Log|Ingestion Log]]` from Home.md so it's discoverable.
  3. **Cross-links** — shared `topics/<topic>.md` notes (see the topic
     vocabulary bullet above) plus inline `[[wikilinks]]` in every note.
  **If you add a new vault builder (a new toolkit, a new content kind),
  implement all three from the start** — copy the `_log_ingest` pattern
  rather than reinventing it, and add the same 4-test shape (backfill wording,
  append-on-growth, skip-on-no-change, removed-item wording) to that module's
  test file. See `docs/superpowers/specs/2026-07-05-nate-herk-jack-roberts-persona-design.md`
  and the corresponding plan for the original design discussion of this
  pattern (it was reverse-engineered from Andrej Karpathy's "LLM knowledge
  base" idea, applied to this repo's vaults). Routing (index + log +
  cross-links) is only half of that idea — the other half is that a costlier
  model should do the final answer synthesis once routing narrows the field.
  The `vault-ask` skill (see `.claude/` assets below) implements that half.
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

## SOIC persona-wiki pipeline (sector synthesis + Phase C senses)

**Read this first if you touch anything under `src/soic_wiki/`,
`src/soic_senses/`, `src/soic_method/`, `configs/course_eligibility.yaml`,
`configs/sector_notebooks.yaml`, `scripts/sector_report.py`, or
`scripts/sync_notes_to_vault.py`.** This is a separate project from the
capture toolkits above: it builds a transcript-grounded "persona wiki" of
SOIC's investing method from the `learn.soic.in` corpus (`data/content.json`,
loaded via `soic_method.corpus.load_corpus()`), gates every generated note
against the raw transcripts so it can never hallucinate a quote, and
publishes the result into a separate repo, `learning-vault-invest`
(`wiki/personas/soic/`) — **not** into this repo's own vault.

### The original pipeline: Claude does the synthesis (map → propose → write → gate)

For the first ~19 "Level 6 Become a Sectoral Expert" sector modules, a Claude
subagent did all three thinking steps per sector, dispatched by hand each
time (there is no CLI/orchestrator for this path):

1. **`map_lesson`** (`soic_wiki/pipeline.py`) — one Claude call per lesson
   transcript, emitting timestamped `Beat` outlines (gist + offsets only,
   never fed forward as prose — the write stage always re-reads the raw
   `body_text` slice, so a beat's gist can never get quoted as if it were the
   instructor's own words).
2. **`propose_concepts`** (`soic_wiki/reduce.py`) — partitions a sector's
   beats into 3-7 concept slugs.
3. **Write** (`build_write_prompt` in `pipeline.py`) — one Claude call per
   concept, demanding `(REF HH:MM:SS)` / `(REF HH:MM:SS-HH:MM:SS)` citations
   for every quote/number, `"garbled"` / `"[likely X]"` annotation instead of
   silently fixing ASR errors, and a fixed `## The mechanism / ## Why it
   matters / ## Caveats and limits` structure.
4. **Gate** (`scripts/sector_report.py`, wraps `soic_wiki/gates.py`) —
   deterministic, zero-LLM: G1 (hapax/summary-inflation frequency check over
   uncited terms — informational), G2 (**cited-quote verification**: does
   each cited phrase actually appear, normalized, in the ref'd lesson's raw
   `body_text`? — the load-bearing gate, hard pass threshold **80%**), G3
   (zero citations pointing at an ineligible/guest lesson), G4 (hollow
   "excerpts don't support X" admissions — informational).

Convention per sector: intermediate artifacts (`lesson.json`, `map_prompt.txt`,
`beats_validated.json`, `propose_result.json`, `refs.json`, `write_prompts/`,
`notes/*.md`) live under `out/a5_<slug>/` — **gitignored scratch**, not
committed anywhere on its own. A REF code is a 3-6 letter mnemonic per lesson
(e.g. `PIPE`, `OILA`/`OILB` for a 2-lesson module), recorded in that sector's
`refs.json`.

### The NotebookLM-brain redesign: NotebookLM does the synthesis instead

Confirmed working end-to-end (14/14 modules passed, 2026-07-26) and now the
default approach for any new sector module. The insight: NotebookLM is
already paid for and used elsewhere in this ecosystem, so offloading the
*thinking* steps (concept partitioning + note writing) to it — while Claude
does only mechanical orchestration — cuts Claude token spend to a fraction of
the original pipeline's cost. Model tiering used for this rollout:
**Sonnet** for mechanical orchestration (REF-code assignment, notebook
creation, source upload, running the *unchanged* gates, vault sync),
**Opus-tier** for issuing the NotebookLM queries and consolidating the
freeform answer into the gates' expected format (not a blind regex parse),
**Fable** for periodic independent verification (see the pilot below).

```
Per sector module:
  1. Load lesson(s) from data/content.json (soic_method.corpus)
  2. assign_ref_codes() -- deterministic REF mnemonic per lesson, collision-
     avoiding against every REF code already used corpus-wide
     (soic_wiki.notebooklm_sector_pipeline)
  3. ensure_sector_notebook() -- create-or-reuse a NotebookLM notebook;
     configs/sector_notebooks.yaml persists slug -> notebook_id so a re-run
     never creates a duplicate
  4. seed_sector_sources() -- add_text_source() per lesson, titled
     "<REF> <lesson title>" (notebooklm_mcp has NO raw-file upload API --
     only pasted-text, URL, and Drive-doc sources exist, which is exactly
     why add_text_source with the raw transcript text is the ingestion path)
  5. ONE query: ask NotebookLM to partition the sector into 3-10 concepts,
     each with a Scope + Sources + Timestamps line (soic_senses.notebook_client
     .ask_notebook) -- consolidate the freeform answer into structured
     concepts (judgment step, not regex)
  6. ONE query PER CONCEPT: ask NotebookLM to write the note, demanding the
     exact same citation format/structure the Claude-authored pipeline used
     (see the exact wording rule below)
  7. Run the SAME UNCHANGED scripts/sector_report.py gates against
     NotebookLM's own prose -- this is the load-bearing invariant: swap the
     brain, keep the judge
  8. Bounded retry on gate failure (not yet needed in practice -- every
     module passed on the first try)
  9. scripts/sync_notes_to_vault.py -- sync + commit to the vault
     immediately per sector, not batched, so nothing sits as scratch
```

**The exact citation-format wording matters and has already bitten once.**
NotebookLM's native citation style is footnote-numbered (`[1]`, `[2-4]`), not
inline timestamps, so the write prompt must explicitly override this. Early
in the rollout one note used a malformed pattern throughout —
`(DECODA 00:01:08-DECODA 00:01:22)` (repeating the REF code before the
second timestamp) instead of `(DECODA 00:01:08-00:01:22)` — which broke the
G2 regex entirely for that file (0/13 quotes recognized as cited) even
though the underlying quotes/timestamps were genuine; a one-off `re.sub`
recovered it. Showing the model a "wrong, don't do this" example risks priming it to
reproduce exactly that pattern, so the fix was to state the correct format
more precisely instead (REF appears exactly once, immediately followed by
one or two `HH:MM:SS` values) rather than including the malformed example
in the prompt at all.

**Pilot-first discipline (already exercised, keep it for anything new).**
Before trusting this pipeline on a new corpus/course, run it on ONE small
module first and require: G2 ≥80% (the same hard threshold as every
Claude-authored batch), the citation format actually sticking, no source
upload silently truncating, and an independent second-model review (a
Fable-tier pass explicitly checking for fabricated/misattributed citations,
boilerplate "Caveats and limits" sections, and general-knowledge injection
that couldn't plausibly come from one lecture transcript) — that review
should **sign off or delegate a specific fix**, not just flag concern. The
2026-07-26 Real Estate Sector pilot (single lesson, 217K chars) hit 96% G2
and got a clean Fable sign-off before the remaining 13 modules were run;
individual module results ranged 91-100% G2 across all 14.

**Deliberately NOT built yet (Part 3, gated on human review):**
`sector_router.py` (a `framework_router.py`-style keyword index over
`configs/sector_notebooks.yaml` so `decision_engine` could auto-discover
sector context), the corresponding `decision_engine.py` extension, and
automated per-sector `decision-frameworks-v1.md` evolution. If you build
these, framework-file diffs must get **explicit human sign-off before
commit** — header-parseability alone is not a content-quality check, and a
bad framework poisons every downstream briefing.

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
- `vault-ask` (`/vault-ask <question>`) — the "presentation" half of the
  index + log + cross-links pattern below: routes a question to the right
  notes cheaply (grep over `Home.md`/`topics/*.md`/`sources/*.md`), then
  dispatches an Opus-tier subagent to synthesize the answer from only those
  routed notes. Use for ad-hoc questions against any captured vault that
  don't warrant a dedicated persona.
- `storm` (`/storm`) — STORM multi-perspective business-research engine:
  casts expert lenses (auto best-fit from the dynamic persona roster + Mufti
  halal gate), maps their contradictions, adversarially fact-checks, and
  renders a graded vault note + HTML briefing. Thin skill → the
  `storm-business-research` workflow (`.claude/workflows/storm.js`) →
  `storm_core` CLI (`python -m storm_core`). See
  `docs/superpowers/specs/2026-07-06-storm-business-research-design.md`. MVP is
  `idea` mode; `gap`/`rescore`/`research` are designed but not yet built.

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
