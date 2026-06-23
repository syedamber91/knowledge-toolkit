---
name: media-capture
description: Capture YouTube transcripts (videos, channels, playlists, shorts) and readable web articles into the unified "Obsidian Vault" where they cross-link with Substack posts by shared topic. Use when asked to capture/scrape/archive a YouTube video or channel, pull article(s) into Obsidian, or sync video/web knowledge.
trigger: /media-capture
---

# Media Capture Skill (YouTube + Web)

Capture knowledge from YouTube and websites into the unified Obsidian vault, where
videos, articles, and Substack posts that share a topic collapse to one topic note.

> **Personal use only.** Only text the platforms expose is stored — transcripts
> and readable article text. No audio/video is downloaded; nothing is fabricated.

## Project paths

| Path | Purpose |
|------|---------|
| `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/` | Project root |
| `.venv/bin/python` | Project virtualenv Python (run everything with this) |
| `data/media.json` | Shared, resumable capture cache (YouTube + web) |
| `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault` | Unified vault (default `MEDIA_VAULT_DIR`) |

CLIs (installed via `pip install -e .`): `youtube-toolkit`, `web-toolkit`.
Run from the project root.

## Architecture (Approach A: shared core + source peers)

- **`media_core`** — `config`, `models` (`MediaItem`/`MediaCatalog`), `store`
  (shared `data/media.json`), `topics` (canonical vocabulary, see below), and
  **`unified_vault.py`** (the cross-source builder).
- **`youtube_toolkit`** — `capture.py` (yt-dlp + transcripts) + `youtube-toolkit` CLI.
- **`web_toolkit`** — `capture.py` (trafilatura) + `web-toolkit` CLI.

`youtube_toolkit` and `web_toolkit` are peers; both depend only on `media_core`
and append to the same catalog, so the unified build mixes them.

## How capture works (no API keys)

- **YouTube** (`youtube_toolkit/capture.py`):
  - `yt-dlp` with `extract_flat="in_playlist"` lists entries; `_flatten_entries`
    walks nested channel tabs (Videos / **Shorts** / Live). A `@handle/shorts`
    URL yields the shorts entries.
  - Per item: full metadata via `yt-dlp`; transcript via
    `youtube-transcript-api` (handles both legacy `get_transcript` and the newer
    instance `.fetch` API).
  - Items without captions → `body_accessible=false` + a `[!warning]` callout.
    Never fabricate a transcript.
  - Resumable (skips cached URLs), incremental save, polite random delay.
- **Web** (`web_toolkit/capture.py`): `trafilatura` strips boilerplate and returns
  the article as Markdown + metadata (title/author/date/site). Single URLs or a
  `--file` reading list. Resumable.

## Topics (the cross-linking seam)

`media_core/topics.py` reuses the Substack canonical `TOPIC_VOCABULARY` and
extends it with software / system-design / AI terms (Kubernetes, Microservices,
System Design, LLM, Caching, …). Keep aliases specific (e.g. `rest api`, not bare
`rest`). The unified builder emits ONE `topics/<slug>.md` at the vault root whose
sections are `## Substack · <handle>`, `## YouTube · <channel>`, `## Web · <domain>`.

## Standard workflow

```bash
# 1. Capture YouTube (resumable). Start with a small --limit to sanity-check.
youtube-toolkit capture "https://www.youtube.com/watch?v=<id>"
youtube-toolkit capture "https://www.youtube.com/@channel/shorts" --limit 5
youtube-toolkit capture "https://www.youtube.com/@channel"            # whole channel
# 2. Capture web articles.
web-toolkit capture "https://example.com/post"
web-toolkit capture --file urls.txt
# 3. Build the UNIFIED vault (reads data/media.json + data/substack.json).
youtube-toolkit build      # or: web-toolkit build  (identical)
```

After capture, spot-check that transcripts/bodies are non-trivial in size and
topics are populated:
```bash
.venv/bin/python -c "
from media_core.models import MediaCatalog; from media_core.config import CONTENT_PATH
c=MediaCatalog.model_validate_json(CONTENT_PATH.read_text())
for i in c.items[-5:]: print(i.kind, '|', i.title[:45], '| chars', len(i.body_markdown), '| topics', i.topics)
"
```

After build, verify link integrity (code-fence aware) in the vault root and that
a shared topic note shows multiple source sections.

## Other vaults / scope

- **SOIC lives in a separate "Stock Market Vault"** (different domain, different
  tagging) — not part of these unified topic notes. Don't write media content there.
- The first unified build removes stale `Substack/topics/` and `Substack/Home.md`
  (topics are centralized at the vault root now).

## Environment gotchas

- This Mac runs low on disk; installs/Playwright can fail under ~1 GB free.
  Reclaim with `uv cache clean` or `rm -rf ~/.cache/puppeteer` (re-downloadable).
- yt-dlp / transcript availability varies; shorts often have auto-captions but
  not always — that's handled, not an error.
- `data/media.json` and the vaults are gitignored / outside the repo.
