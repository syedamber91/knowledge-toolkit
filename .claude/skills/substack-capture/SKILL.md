---
name: substack-capture
description: Capture posts (free AND paid) from a Substack publication you subscribe to, via the publication JSON API and your own authenticated session, then build an Obsidian vault. Use when asked to scrape/capture/archive/sync Substack content, pull a newsletter into Obsidian, or extract paid Substack posts.
trigger: /substack-capture
---

# Substack Capture Skill

You capture content from a Substack publication the user **subscribes to** and
store it as an Obsidian vault. This skill encodes the non-obvious mechanics —
especially authentication and paywall detection — that are easy to get wrong.

> **Personal use only.** Only capture content the user already has legitimate
> access to through their own paid membership, at a polite rate. Only text the
> API legitimately returns is stored — never media files, never DRM.

## Project paths

| Path | Purpose |
|------|---------|
| `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/` | Project root |
| `.venv/bin/python` | Project virtualenv Python (run everything with this) |
| `data/substack.json` | Resumable crawl cache (the raw catalog) |
| `.auth/substack_state.json` | Saved session cookies (gitignored) |
| `~/Documents/Obsidian Vault/Substack` | Default vault output (`SUBSTACK_VAULT_DIR`) |

Run all commands from the project root. The CLI is `substack-toolkit` (or
`.venv/bin/python -m substack_toolkit.cli`).

---

## How Substack works (READ THIS FIRST)

There is **no HTML scraping**. Substack exposes a clean JSON API per publication
at `https://<handle>.substack.com`:

- **List posts** (newest first, paginated):
  `/api/v1/archive?sort=new&limit=12&offset=<N>` → array of `{slug, title, …}`.
  Page by incrementing `offset` until it returns `[]`.
- **Full post**: `/api/v1/posts/<slug>` → one object with `body_html`,
  `audience`, `title`, `subtitle`, `post_date`, `publishedBylines`, etc.

`<handle>` is the **subdomain**, NOT the `@profile`. The user may give you
`https://substack.com/@vutr` — that is the profile. The publication is
`vutr.substack.com`, so the handle is `vutr`. Confirm by hitting the archive API.

## Authentication — the part everyone gets wrong

1. **The only cookie that proves an authenticated session is `substack.sid`**
   (httpOnly). `substack.lli` is a client-side "logged-in hint" that can exist
   **without** an authenticated session — never treat its presence as success.
   `auth.session_has_auth()` checks for `substack.sid` specifically.

2. **Preferred way to get a session: import from the user's everyday Chrome.**
   They are usually already logged into Substack there. Run:
   ```bash
   substack-toolkit login --from-chrome
   ```
   This decrypts the Substack cookies from Chrome's local store
   (`~/Library/Application Support/Google/Chrome/Default/Cookies`) using the
   `Chrome Safe Storage` key from the macOS Keychain. **Tell the user a Keychain
   approval dialog will appear and they must click Allow.** Decryption details
   (in `auth.py`): key = PBKDF2-HMAC-SHA1(password, salt `saltysalt`, 1003 iters,
   16 bytes); AES-128-CBC, IV = 16 spaces; strip the `v10`/`v11` prefix, then
   PKCS7 padding, then a 32-byte SHA256(domain) prefix that Chrome ≥130 prepends.

3. **Browser login (`login --handle <h>`) is the fallback, and it is flaky here.**
   Headed Playwright launches can wedge in this environment — the Node driver
   gets stuck in an uninterruptible (`UE`) state and never spawns Chrome,
   especially after disk pressure. If you must use it, the original flow blocks on
   `input()`; the `--from-chrome` path avoids all of this. Prefer it.

## ALWAYS verify auth before trusting a crawl

`bool(body_html)` is **NOT** proof you got the paid content — a paywalled preview
is also non-empty. Do the ground-truth comparison: fetch a known **paid** post
both with and without the session cookie and compare `body_html` length.

```bash
.venv/bin/python - <<'PY'
import json, urllib.request
from substack_toolkit.crawler import _load_cookie_header
from substack_toolkit.config import channel_url
slug = "<a-known-paid-slug>"; url = f"{channel_url('<handle>')}/api/v1/posts/{slug}"
def fetch(cookie):
    h={"User-Agent":"Mozilla/5.0 (personal-knowledge-archive)","Accept":"application/json"}
    if cookie: h["Cookie"]=cookie
    with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=30) as r:
        return json.loads(r.read().decode())
a=len(fetch(None).get("body_html") or ""); b=len(fetch(_load_cookie_header()).get("body_html") or "")
print("anon:",a,"authed:",b,"-> AUTHENTICATED" if b>a else "-> NOT AUTHENTICATED (identical)")
PY
```

If `anon == authed`, EITHER the session is not authenticated OR you are only a
**free subscriber** to that publication. Distinguish them: if the authed response
has reader keys (`is_saved`, `read_progress`, …) the session IS recognized, so
`anon == authed` means you simply lack a paid subscription to that channel — its
paid posts will only ever be previews. (Auth is account-wide via `substack.sid`,
but paid *entitlement* is per-publication.)

### Free subscribers: use `--free-only`

When you only follow a publication for free, crawling its paid posts just yields
truncated previews. Skip them entirely — they are filtered at the archive-listing
stage using the `audience` field, so their bodies are never even fetched:

```bash
substack-toolkit crawl <handle> --free-only
```

Check the split first so you know what you'll get:
`/api/v1/archive?sort=new&limit=12&offset=N` reports each post's `audience`
(`everyone`/`only_free` = free; anything else = paid). Note the archive endpoint
can cap a large `limit` server-side, so to COUNT the full catalogue, page with a
modest limit until you get an empty page rather than trusting one big request.

## Paywall detection (how the code decides `body_accessible`)

- A post is **paid** when `audience` is not in `{"", "everyone", "only_free"}`.
- A paid post returns only a **truncated preview** unless authenticated+entitled.
  The gated response is marked **`hidden: True`**; with access, `hidden` is absent
  and the response also gains reader keys (`is_saved`, `read_progress`, …).
- **`truncated_body_text` is a red herring** — it is the listing snippet and is
  present in BOTH the full and the preview responses. Do not key off it.
- So `body_accessible = bool(body_md) and not (is_paid and data.get("hidden") is True)`.
  See `extract._is_truncated_preview`.

## Standard workflow

```bash
# 0. Confirm the handle (subdomain) and that the archive API responds.
# 1. Get an authenticated session (preferred).
substack-toolkit login --from-chrome
# 2. VERIFY auth with the anon-vs-authed comparison above. Do not skip this.
# 3. Crawl (resumable; start small). is_paid posts must come back full-size.
#    Add --free-only if you are a free subscriber to this publication.
substack-toolkit crawl <handle> --limit 10
# 4. Build the Obsidian vault (cross-channel topic notes).
substack-toolkit build-vault            # or --vault-path <dir>
# 5. Sanity-check: paid notes should be large; 0 broken [[wikilinks]].
substack-toolkit list-topics
```

After a crawl, spot-check that `is_paid` posts have realistic body sizes (paid
deep-dives are typically 20k–40k chars; a few-hundred-char "body" on a paid post
means you captured a preview — recheck auth).

## Environment gotchas

- **Disk pressure breaks Playwright.** If a browser launch hangs, check
  `df -h /`. Clearing re-downloadable caches helps a lot (`uv cache clean` freed
  ~9.5 GB here). The Chromium download also needs `playwright install chromium`.
- **`.auth/`, `data/`, and the vault are gitignored** — never commit a session.
- Be polite: the crawler sleeps a random 1.5–3.5s between posts and saves
  incrementally so an interrupted run never loses captured posts.
