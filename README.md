# SOIC Knowledge Toolkit

A small, personal-study toolkit that logs into **your own** SOIC ("School of
Intrinsic Compounding") membership on the Learnyst portal (`learn.soic.in`),
collects the lesson text the platform legitimately displays, and builds an
**interactive mind map** so you can see how the material connects.

## What it does (and doesn't)

- ✅ **Interactive login** — a real browser opens and *you* sign in (including
  OTP/MFA). The authenticated session is then saved locally for reuse.
- ✅ **Collects accessible text** — course/module/lesson structure, titles,
  descriptions, any transcript/notes panels the page renders, caption-track URLs
  *if* the portal exposes them, and links to attached documents.
- ✅ **Builds an Obsidian vault** — one linked Markdown note per lesson, so
  Obsidian's graph view shows how topics correlate.
- ✅ **Builds a mind map** — a portable Markmap Markdown file, optionally rendered
  to a zoomable, collapsible interactive HTML page.
- ❌ **No DRM circumvention** — it never downloads, decrypts, or rips protected
  video/audio.
- ❌ **No stored password** — authentication is interactive only.
- ❌ **Nothing leaves your machine** — your session and all captured content are
  written to gitignored folders and never committed.

> **Personal use & Terms of Service.** This tool is intended only for studying
> content you already have legitimate access to through your own paid
> membership. Automated access to a paid platform may be restricted by its Terms
> of Service even for your own account. Review SOIC/Learnyst's terms and use this
> at a polite rate and for personal study only.

> **Full walkthrough:** see [`docs/END_TO_END_PLAN.md`](docs/END_TO_END_PLAN.md)
> for the complete end-to-end plan, architecture, and step-by-step runbook.

## Setup

```bash
pip install -e .
playwright install chromium
cp .env.example .env   # adjust if your portal URL differs
```

Rendering the interactive HTML mind map additionally needs Node.js (for
`npx markmap-cli`). The Markdown output works without it.

## Usage

```bash
# 1. Log in once — a browser opens; sign in, then press Enter to save the session.
soic-toolkit login

# 2. Confirm the saved session is still valid.
soic-toolkit status

# 3. Capture accessible lesson text (resumable; --limit for a quick first test).
soic-toolkit crawl --limit 5
soic-toolkit crawl

# 4a. Build an Obsidian vault (one linked note per lesson).
#     Write straight into your real Obsidian vault with --vault-path (or set
#     SOIC_VAULT_DIR in .env); omit it to use a local ./vault folder.
soic-toolkit build-vault --vault-path ~/Documents/Obsidian/MyVault/SOIC

# 4b. (optional) Also build a Markmap mind map under output/.
soic-toolkit build-map
```

Open the `vault/` folder in Obsidian (**Open folder as vault**) and turn on the
**graph view** to explore the correlations between topics. Or open
`output/mindmap.html` in a browser / paste `output/mindmap.md` into
<https://markmap.js.org/repl>.

## Substack toolkit

A second source in this repo: capture posts from a Substack publication you
subscribe to into a **dedicated** Obsidian vault, with cross-channel topic
linking. Free and paywalled posts are captured via your own logged-in session;
posts are matched against a shared canonical topic vocabulary so the same topic
(e.g. `dbt`) resolves to one shared note across every channel.

```bash
substack-toolkit login --from-chrome     # reuse your existing Chrome session (recommended)
# or: substack-toolkit login --handle vutr  # open a browser and log in manually
substack-toolkit crawl vutr --limit 5    # capture a few posts to start (resumable)
substack-toolkit build-vault             # write the Obsidian vault
substack-toolkit list-topics             # see topic coverage
```

**Authentication.** The only cookie that proves an authenticated session is
`substack.sid` (httpOnly); `substack.lli` is just a client-side hint and is not
enough. `login --from-chrome` imports the Substack cookies from your everyday
Google Chrome (where you are already logged in) by decrypting Chrome's local
cookie store — macOS will ask you to approve Keychain access. This is the
reliable path; the manual browser login is a fallback. Paid posts return only a
truncated *preview* unless the session is authenticated and entitled: the API
marks a gated response with `hidden: true`, so `body_accessible` is true only
when the full body came back (a non-empty body alone does **not** prove access).

The vault is written to `SUBSTACK_VAULT_DIR` (default `~/Documents/Obsidian Vault/Substack`):

```
<vault>/Home.md                       # channels + topics index
<vault>/channels/<handle>-channel.md  # one MOC per channel
<vault>/posts/<handle>/<slug>.md      # one note per post
<vault>/topics/<topic>.md             # shared topic notes (cross-channel)
```

Personal use of your own subscription only. Only text the authenticated page
renders is captured — no media is downloaded. Your password is never stored;
only the session cookie is saved under `.auth/` (gitignored). The crawl cache
lives in `data/substack.json`. To recognise more topics, extend
`TOPIC_VOCABULARY` in `src/substack_toolkit/topics.py` and rebuild the vault.

## Where extracted knowledge is stored

```
data/content.json   # internal, resumable crawl cache (the raw catalog)
vault/              # Obsidian vault — one Markdown note per lesson + MOCs
output/             # mindmap.md / mindmap.html
```

By default the vault is written to `./vault` in the repo, but you can write the
notes **directly into your existing Obsidian vault** so they appear there
automatically — either pass `--vault-path ~/Obsidian/MyVault/SOIC` to
`build-vault`, or set `SOIC_VAULT_DIR` in `.env`. A dedicated subfolder (e.g.
`SOIC`) inside your vault keeps the imported notes tidy.

The **Obsidian vault** is the human-facing knowledge store. Each lesson is its
own note (`<vault>/<Course>/<Module>/<Lesson>.md`) with YAML frontmatter (title,
source URL, course, module, tags, crawl date), the lesson body, key points, and
resources. Notes are wired together with `[[wikilinks]]`:

- **Structural** — each lesson links up to its Module/Course *Map-of-Content*
  (MOC) note; MOCs link back down to lessons; `Home.md` links all courses.
- **Sequential** — prev/next links along lesson order.
- **Content-based** — a *Related* section links lessons sharing the most
  keywords, and derived `#tags` cluster related topics in the graph view.

All three folders are gitignored, so your session and captured content never get
committed.

## How it works

| File | Responsibility |
|------|----------------|
| `auth.py` | Interactive login + saving/loading the Playwright session (`.auth/state.json`). |
| `crawler.py` | Walks course → module → lesson, polite & resumable, writes `data/content.json`. |
| `extract.py` | Parses a lesson page's HTML into structured, legitimately-displayed text. |
| `vault.py` | Turns `content.json` into an Obsidian vault of linked lesson notes + MOCs. |
| `mindmap.py` | Turns `content.json` into Markmap Markdown and (optionally) interactive HTML. |
| `models.py` | Pydantic models for the captured catalog. |
| `cli.py` | The `soic-toolkit` command. |

### Tuning for the live portal

The Learnyst DOM is only knowable once logged in, so the discovery selectors in
`crawler.py` (`SELECTORS`) and the content selectors in `extract.py` are
best-effort starting points. After your first `login`, inspect a real lesson page
and adjust those selectors if the captured text looks thin.

## Development

```bash
pip install -e ".[dev]"
pytest          # unit tests for extract.py and mindmap.py (no login needed)
```
