---
name: youtube-capture
description: Capture YouTube channel/video transcripts into the unified Obsidian vault. Handles full channels, single videos, playlists, and Shorts enumeration. Knows the three-stage transcript fallback chain and all guardrails. Trigger: /youtube-capture
trigger: /youtube-capture
---

# YouTube Capture Skill

Capture transcripts from YouTube channels, playlists, or single videos into the
unified Obsidian vault at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault`.

> **Personal use only.** Only text YouTube exposes (transcripts/captions) is stored.
> No audio/video is downloaded. Never fabricate a transcript.

## Project paths

| Path | Purpose |
|------|---------|
| `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/` | Project root |
| `.venv/bin/youtube-toolkit` | CLI entry point |
| `.venv/bin/python` | Venv Python (always use this, not system python3) |
| `src/youtube_toolkit/capture.py` | Core capture logic |
| `data/media.json` | Shared resumable catalog (YouTube + web, gitignored) |

## Standard workflow

```bash
# From project root:

# Single video
.venv/bin/youtube-toolkit capture "https://www.youtube.com/watch?v=<id>"

# Whole channel (all tabs — Videos, Shorts, Live flattened automatically)
.venv/bin/youtube-toolkit capture "https://www.youtube.com/@<handle>"

# Only the Videos tab (skips Shorts and Live)
.venv/bin/youtube-toolkit capture "https://www.youtube.com/@<handle>/videos"

# Only Shorts tab
.venv/bin/youtube-toolkit capture "https://www.youtube.com/@<handle>/shorts"

# Sanity-check a channel first with a small limit
.venv/bin/youtube-toolkit capture "https://www.youtube.com/@<handle>/videos" --limit 5

# Build vault after capture
.venv/bin/youtube-toolkit build
```

The capture is **resumable** — re-running skips already-captured URLs.

## Transcript fallback chain (3 stages)

YouTube blocks transcript access in various ways. The code tries three methods
in order, stopping at the first that returns text:

1. **yt-dlp VTT** (`fetch_transcript_from_info`) — extracts caption URLs from
   the yt-dlp info dict and fetches the VTT file directly. Works when YouTube
   exposes caption metadata. Fails when the PO token is required.

2. **pytubefix** (`fetch_transcript_via_pytubefix`) — uses a different HTTP
   request path that bypasses both the PO token requirement and the
   `youtube-transcript-api` IP-block. **This is the most reliable fallback**
   and was the method that successfully captured 221 Justin Sung videos.

3. **youtube-transcript-api** (`fetch_transcript`) — last resort. Effective
   but gets IP-blocked after bulk requests (~300+ videos in quick succession).
   Recovers in 24–48h.

## Active guardrails (both in `capture.py`)

| Guardrail | Logic | What happens |
|-----------|-------|-------------|
| **Skip Shorts** | `duration < 61s` | Silently skipped, URL marked seen |
| **Skip no-transcript** | All 3 stages return `""` | Silently skipped, URL marked seen |

Both guardrails mark the URL as seen so resume runs don't retry them.

## Known YouTube anti-bot issues

- **PO token (Proof of Origin)**: Required since 2024 for `yt-dlp` to populate
  `automatic_captions` in the info dict. Chrome cookies alone don't provide it.
  All `yt-dlp` clients (WEB, mweb, iOS, ANDROID) fail without it. This is why
  `fetch_transcript_from_info` often returns `""` and pytubefix is needed.
- **IP block**: `youtube-transcript-api` gets blocked after ~300+ rapid requests.
  Symptom: `TranscriptsDisabled` or `429` errors on every video. Fix: wait 24–48h,
  or use pytubefix which uses a different endpoint.
- **SABR streaming**: Some YouTube web clients trigger SABR mode which blocks
  caption metadata entirely. Not fixable without the PO token.
- **"The page needs to be reloaded." (info fetch)**: `yt-dlp`'s default web/tv
  clients intermittently fail *newer* videos with this error, silently dropping
  the most recent uploads from a channel refresh. **Fixed** in `capture.py`:
  `_ydl` now sets `extractor_args={"youtube": {"player_client": ["android",
  "web_safari", "tv"]}}` — the **android** client bypasses it for info
  extraction. Verified: `fetch_info` recovers the failing videos.
- **Rolling per-IP throttle (the real blocker on a refresh)**: after ~5 rapid
  capture runs, YouTube rate-limits *per request* — each `fetch_info` has a
  random chance of the reload error, and bulk channel crawls make it worse. It
  is NOT a hard 24–48h block; a single spaced request usually succeeds. **Drain
  strategy that works:** capture the missing videos **one URL at a time, retrying
  each until it catches a good window** (see the loop below), rather than
  re-crawling the whole channel. Failed `no info` fetches and `no transcript`
  skips are **not persisted to the catalog**, so nothing is lost — a later
  resume recovers them.

```bash
# Recover specific throttled videos: retry each until captured (or caption-less)
for id in <VIDEO_IDS>; do
  for attempt in 1 2 3 4 5; do
    out=$(.venv/bin/youtube-toolkit capture "https://www.youtube.com/watch?v=$id" 2>&1 \
          | grep -E "captured:|no info|no transcript")
    echo "$id attempt $attempt: $out"
    echo "$out" | grep -q "captured:"     && break
    echo "$out" | grep -q "no transcript" && { echo "  -> genuinely caption-less"; break; }
    sleep $((18 + RANDOM % 12))
  done
done
```

- **Genuinely caption-less videos**: some short uploads have no captions at all.
  Their info fetches fine but all 3 transcript stages return `""` → correctly
  skipped (never fabricate a transcript). Such a video always shows as "missing"
  in a channel enumeration because it is never added to the catalog — that is
  by design, not a capture failure.

## Verifying capture quality

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
from media_core.store import load_catalog
cat = load_catalog()
yt = [i for i in cat.items if i.kind == 'youtube']
print(f'{len(yt)} YouTube items')
print(f'Avg transcript: {sum(len(i.body_markdown) for i in yt) // max(len(yt),1)} chars')
print(f'All accessible: {all(i.body_accessible for i in yt)}')
for i in yt[-3:]:
    print(f'  {i.title[:50]} | {len(i.body_markdown)} chars | topics: {i.topics}')
"
```

A healthy capture has:
- Average transcript **≥ 5,000 chars** (a short video with captions is typically 10k+)
- `body_accessible=True` for all items (no-transcript videos are skipped, not stored)
- Topics populated from `media_core/topics.py`

## Topic vocabulary

`src/media_core/topics.py` contains `_EXTRA_VOCABULARY` with categories including:
`Learning`, `Productivity`, `Career`, `Education`, `AI & Future of Work` — added
to cover Justin Sung content specifically. Extend here if new channel topics
don't match.

## Vault structure after build

```
Obsidian Vault/
  youtube/
    <channel-slug>/          # one subfolder per channel
      <video-slug>-<id>.md   # individual video note (title + transcript)
  topics/
    learning.md              # cross-source: YouTube + Substack + Web
    productivity.md
    ...
  sources/
    youtube-<channel>.md     # channel-level source page
```

## Isolated vaults & catalogs (IMPORTANT — not everything goes to the default vault)

The default catalog/vault above is the **unified "Obsidian Vault"**. Topic- or
creator-specific captures use a **separate catalog + vault** via env overrides so
they don't mix in with the unified content:

| Vault | `MEDIA_CONTENT_PATH` | `MEDIA_VAULT_DIR` |
|-------|----------------------|-------------------|
| Unified (default) | `data/media.json` | `…/Documents/Obsidian Vault` |
| **AI & Development** (Nate Herk + Jack Roberts) | `data/media_ai_dev.json` | `…/Documents/AI & Development` |

**To refresh the AI & Development vault**, set both env vars for every command:

```bash
export MEDIA_CONTENT_PATH=data/media_ai_dev.json
export MEDIA_VAULT_DIR="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/AI & Development"
.venv/bin/youtube-toolkit capture "https://www.youtube.com/@nateherk/videos"
.venv/bin/youtube-toolkit capture "https://www.youtube.com/@Itssssss_Jack/videos"
.venv/bin/youtube-toolkit build     # appends a Log.md entry with the new-item count
```

The build writes into that vault's own `Home.md`/`topics/`/`sources/` **and its
append-only `Log.md`** (the index+log+cross-links pattern — see root `CLAUDE.md`).
After capture, the `/nate-herk` and `/jack-roberts` persona files can be refreshed
from the new transcripts.

## Channel capture history

| Channel | URL | Videos | Vault | Notes |
|---------|-----|--------|-------|-------|
| Justin Sung | `@JustinSung/videos` | 221 | Obsidian Vault | Captured 2026-06-26. Learning/productivity. pytubefix primary. |
| Nate Herk \| AI Automation | `@nateherk/videos` | 286 | AI & Development | 281 (2026-07-05) + 5 (2026-07-07 refresh). Folder `nate-herk-ai-automation`. |
| Jack Roberts | `@Itssssss_Jack/videos` | 155 | AI & Development | 154 + 1 (2026-07-07 refresh). Folder `jack-roberts`. |

## Environment notes

- Always use `.venv/bin/python` — system Python 3.9 lacks the dependencies
- iCloud sync after build can take 30–120s before notes appear in Obsidian app
- `data/media.json` is gitignored (contains personal viewing data)
- Run tests after any code change: `.venv/bin/python -m pytest -q`
