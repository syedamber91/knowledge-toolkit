---
name: instagram-capture
description: Capture public Instagram post/reel captions + metadata (via a burner account's session) into the shared media catalog, then build the unified Obsidian vault. Use when asked to scrape/capture/archive Instagram content, pull an IG profile or hashtag into Obsidian, or sync Instagram alongside YouTube/web/Substack.
trigger: /instagram-capture
---

# Instagram Capture Skill

You capture **public** Instagram post/reel captions and metadata — never
media files, never comment text — using the `instagram_toolkit` package,
via Instaloader with all download flags off. Data lands in the SAME shared
catalog as YouTube and web captures, so it cross-links by topic in the
unified Obsidian vault.

> **Use a DEDICATED / BURNER Instagram account, never the user's primary.**
> Scraping — even read-only, even logged in — can get an account restricted
> or locked. This is a hard guardrail, not a suggestion.

## Project paths

| Path | Purpose |
|------|---------|
| `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/` | Project root |
| `.venv/bin/python` | Project virtualenv Python (run everything with this) |
| `data/media.json` | Shared resumable catalog (YouTube + web + Instagram) |
| `.auth/instagram_state.json` | Saved session cookie (gitignored, never a password) |
| `MEDIA_VAULT_DIR` (env) | Unified vault output — same vault as YouTube/web |

Run all commands from the project root. The CLI is `instagram-toolkit` (or
`.venv/bin/python -m instagram_toolkit.cli`).

---

## How it works (READ THIS FIRST)

Instaloader is configured with **every download flag off** — `download_pictures`,
`download_videos`, `download_video_thumbnails`, `download_geotags`,
`download_comments`, and `save_metadata` are all `False`. Only `caption`,
`owner_username`, `taken_at`, `likes`, `comments` (the *count*, not the text),
`hashtags`, and `mentions` are captured per post. This is a repo-wide
guardrail, not an oversight — never re-enable a download flag.

## Authentication — same Chrome-Keychain pattern as Substack

The only cookie that proves a real session is **`sessionid`** (httpOnly),
stored at `.auth/instagram_state.json`. Two ways to get one:

1. **Preferred: import from the user's Chrome** (the burner account must
   already be logged into Instagram there):
   ```bash
   instagram-toolkit login --from-chrome
   ```
   This decrypts Chrome's Instagram cookies via the macOS Keychain — **a
   Keychain approval dialog will appear; tell the user to click Allow.**
   Same decryption scheme as `substack_toolkit`: PBKDF2-HMAC-SHA1(password,
   salt `saltysalt`, 1003 iters, 16 bytes) → AES-128-CBC, IV = 16 spaces,
   strip the `v10`/`v11` prefix, PKCS7-unpad, then drop a leading 32-byte
   SHA256(domain) prefix if Chrome ≥130 added one.

2. **Fallback: `instagram-toolkit login`** — opens a real (headed) Playwright
   browser to the login page and polls for the `sessionid` cookie to appear
   (up to 300s, no keypress needed). Log in with the burner account in the
   window that opens.

`auth.load_session_into(loader)` injects the saved cookies and calls
Instaloader's `test_login()` to verify — if the session is expired/invalid,
it raises immediately rather than silently scraping unauthenticated.

## Rate limiting and blocks — Instagram is aggressive

Instagram temp-blocks fast scrapers **even when logged in**, so the default
pacing here is slower than the YouTube/web default: `INSTAGRAM_CRAWL_MIN_DELAY`
/ `INSTAGRAM_CRAWL_MAX_DELAY` default to **3–6s** between posts (vs. 1.5–3.5s
for media). Keep `--limit` small, especially on a fresh session.

The crawler recognizes known Instaloader block exceptions
(`LoginRequiredException`, `ConnectionException`, `TooManyRequestsException`,
`QueryReturnedBadRequestException`, `QueryReturnedForbiddenException`,
`ProfileNotExistsException`) plus generic 429/"too many requests"/"please
wait"/"checkpoint_required" text, and converts them into a friendly message:
progress is saved first, then it tells you to wait and re-run the same
command to resume. **Never treat a block as a fatal error — just wait and
retry later**, same handle/tag, same command.

## Standard workflow

```bash
# 1. Authenticate (burner account).
instagram-toolkit login --from-chrome
# 2. Capture a public profile's posts + reels (small limit first).
instagram-toolkit crawl <handle> --limit 10
# 3. Or discover posts by hashtag instead.
instagram-toolkit crawl-hashtag <tag> --limit 10
# 4. Build the unified vault (cross-links with YouTube/web/Substack by topic).
instagram-toolkit build            # or --vault-path <dir>
```

Both `crawl` and `crawl-hashtag` are **resumable** — already-captured URLs
(tracked in `data/media.json`) are skipped automatically, and each new item
is saved incrementally so an interrupted or blocked run never loses progress.

## Environment gotchas

- **Burner account only.** Never authenticate with the user's real Instagram
  account.
- **`.auth/`, `data/`, and the vault are gitignored** — never commit a session.
- Chrome import needs the burner account already logged into Instagram in
  that Chrome profile; the `security find-generic-password` Keychain read is
  a one-time macOS approval prompt per session.
- `pip install instaloader` is required (declared in `pyproject.toml`).
- If a block/rate-limit message appears, that is expected behavior working
  correctly — stop, wait, and resume later rather than retrying immediately
  or switching accounts.
