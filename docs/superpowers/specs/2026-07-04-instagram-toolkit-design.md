# instagram_toolkit — Design

**Date:** 2026-07-04
**Status:** Approved (design), pending implementation plan
**Author:** brainstormed with the user; pressure-tested by an anti-sycophantic marketing review

## Goal

Add a fifth capture toolkit, `instagram_toolkit`, that captures **openly-rendered
text** (captions + metadata) from public Instagram profiles, reels, and hashtag
feeds into the **shared `media_core` catalog** (`data/media.json`) and the
**unified Obsidian vault**, so Instagram content cross-links with the existing
YouTube + web captures by shared topic. It is the Instagram sibling of the
`substack_toolkit` (session-cookie auth) and the `youtube_toolkit`/`web_toolkit`
(media_core consumers).

## Non-goals (explicit scope boundaries)

- **No media downloads.** Never download image or video files — repo guardrail.
  Only caption text + metadata are captured. The post **permalink** is stored so
  the user can click through to view visuals manually.
- **No comment text.** Only like/comment **counts**, not comment bodies (rate-limit
  and block risk). May be revisited later.
- **No reel transcripts.** Instagram exposes no transcript API; captions only.
- **No stored passwords.** Session-cookie auth only, same as `substack_toolkit`.
- Not a bulk exporter — small `--limit` batches, resumable, polite.

## Context: why this shape

`media_core.MediaItem` is already generic (`kind` / `source` / `topics`), and
`unified_vault.py` groups by `kind`→`source` and cross-links by topic. Adding
Instagram is therefore **one new `kind`** plus small, localized edits — not a
parallel system. `substack_toolkit/auth.py` already implements the exact
macOS-Keychain Chrome-cookie decryption we need; we generalize it for
`instagram.com` cookies and hand the session to Instaloader.

## Architecture

New package `src/instagram_toolkit/`, mirroring `substack_toolkit`:

```
src/instagram_toolkit/
  __init__.py
  config.py    # IG auth path (.auth/instagram_state.json); slower pacing (3–6s)
  auth.py      # Chrome-cookie import for instagram.com → Instaloader session
  crawler.py   # Instaloader-backed, metadata-only, resumable, polite
  extract.py   # Instaloader Post/Hashtag objects → media_core.MediaItem
  cli.py       # Typer app: login / crawl / crawl-hashtag / build
```

New CLI entry point in `pyproject.toml`:
`instagram-toolkit = "instagram_toolkit.cli:app"`. New dependency: `instaloader>=4.14`.

### media_core extensions (small, additive)

- `media_core/models.py`: add `KIND_INSTAGRAM = "instagram"`; add two optional,
  broadly-useful fields to `MediaItem`: `like_count: Optional[int]` and
  `comment_count: Optional[int]`.
- `media_core/unified_vault.py`: extend `_KIND_LABEL` (`"Instagram"`) and
  `_KIND_FOLDER` (`"instagram"`); `_item_basename` uses the IG shortcode;
  `_render_item` uses heading `## Caption`, link text `Open on Instagram`, and
  renders engagement counts; `_render_home` adds an Instagram count. Existing
  topic cross-linking and source-MOC logic already work generically.

## Auth — session-from-Chrome → Instaloader

`instagram-toolkit login --from-chrome` generalizes `substack_toolkit/auth.py`:
decrypt the IG session cookies (`sessionid`, `csrftoken`, `ds_user_id`, `mid`,
`ig_did`) from Chrome's cookie store (`host_key like '%instagram%'`), inject them
into an Instaloader session, and verify with `L.test_login()`. Store only cookies
under `.auth/instagram_state.json` — never a password. A manual `login` fallback
opens Playwright, waits for manual login, and saves cookies.

**Account-safety guardrail (from the marketing review):** scraping risks
shadowban/lockout of the authenticating account. The tool MUST warn on `login`
that the user should authenticate with a **dedicated/burner Instagram account**,
never the primary account they will use to run a business. Documented in the CLI
help and README.

## Capture — metadata-only, resumable, polite

`crawler.py` drives Instaloader configured to fetch **no media**:
`download_pictures=False, download_videos=False, download_video_thumbnails=False,
download_geotags=False, download_comments=False, save_metadata=False`.

- `crawl <handle> --limit N`: iterate a public profile's posts + reels.
- `crawl-hashtag <tag> --limit N`: iterate a hashtag feed for discovery.
- Resumable via `catalog.item_urls()` (skip already-captured permalinks).
- Polite: random 3–6s sleeps (IG-specific, slower than the media default).
- Small default `--limit` (e.g. 30); stop cleanly and save progress on
  `LoginRequired` / `ConnectionException` / HTTP 429, telling the user to wait.

## Data model mapping (Instaloader `Post` → `MediaItem`)

| MediaItem field | Instagram source |
|---|---|
| `kind` | `KIND_INSTAGRAM` |
| `title` | first line of caption, else `"@{owner} · {date}"` |
| `url` | permalink (`https://www.instagram.com/p/<shortcode>/` or `/reel/`) |
| `source` / `source_id` | owner username |
| `author` | owner full name |
| `published_at` | `post.date_utc` |
| `duration_seconds` | reel video duration (if reel) |
| `body_markdown` | caption text |
| `like_count` / `comment_count` | `post.likes` / `post.comments` |
| `keywords` | hashtags + mentions + `reel`/`post` tag |
| `topics` | matched from shared vocabulary (`media_core.topics`) |

Hashtag crawls produce a `sources/hashtag-<tag>.md` MOC listing the discovered items.

## Vault output

`instagram/<username>/<shortcode>.md` — one note per post/reel: frontmatter
(`kind`, `source`, `author`, `published_at`, `like_count`, `comment_count`,
`topics`), `## Caption` body, engagement line, an **Open on Instagram** permalink,
and topic `[[wikilinks]]`. Source MOC `sources/instagram-<username>.md`; Home note
gains an Instagram count. Default vault is the shared `MEDIA_VAULT_DIR` (iCloud
Obsidian container), so it syncs to iOS for free.

## Error handling

- No saved session → clear message pointing to `login --from-chrome`.
- Login/rate-limit walls → stop politely, persist catalog, instruct to wait.
- Private/nonexistent profile → skip with a logged warning, continue.
- Never retry aggressively; never download media; never commit captured data.

## Testing (offline, no network/login)

- `extract.py`: saved Instaloader-object fixtures (JSON) → assert `MediaItem`
  shape (caption, counts, keywords, permalink, kind).
- `unified_vault`: assert the Instagram note + source MOC layout renders.
- Live crawl/auth tests skip themselves without a session, like existing
  integration tests. Full suite stays green and offline-runnable.

## Risks & honest tradeoffs (recorded from the anti-sycophantic review)

1. **Text-only in a visual category.** For visual research (e.g. premium gifting),
   captions+counts miss the images and comment-voice that matter most. Mitigation:
   permalinks in every note for one-click manual visual review. Accepted because
   this toolkit's purpose is completing the text-capture suite, not being the sole
   marketing-intelligence source.
2. **Account risk.** Mitigated by the burner-account guardrail above.
3. **Maintenance.** Instagram breaks scrapers; Instaloader absorbs most endpoint
   churn, but this is not a fire-and-forget tool. Accepted.
4. **Opportunity cost.** For business decisions, manual competitor teardown +
   customer conversations remain higher-value than this tool; the tool is a
   knowledge-capture convenience, not a substitute for market fieldwork.

## Files created / modified

- **Create:** `src/instagram_toolkit/{__init__,config,auth,crawler,extract,cli}.py`
- **Create:** `tests/test_instagram_extract.py`, `tests/fixtures/instagram_*.json`
- **Modify:** `src/media_core/models.py` (KIND_INSTAGRAM + 2 fields),
  `src/media_core/unified_vault.py` (render Instagram),
  `pyproject.toml` (dependency + script entry), `README.md` / `CLAUDE.md` (docs).
