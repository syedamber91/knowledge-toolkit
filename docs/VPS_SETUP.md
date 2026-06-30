# Running `knowledge-toolkit` on a VPS

A runbook for standing the project up on a **headless Linux VPS** (no monitor),
with `root`/`sudo`. It covers **both** runnable surfaces:

1. **The CLI capture toolkits** — `soic-toolkit`, `substack-toolkit`,
   `youtube-toolkit`, `web-toolkit` (+ the learning-pack generator scripts).
2. **The webapp dashboard** — FastAPI backend (`webapp/backend`, port 8000,
   SQLite) + Next.js frontend (`webapp/frontend`, port 3000).

> **Guiding principle:** *interactive logins need a display; everything else
> does not.* SOIC and Substack open a **visible browser** for the one-time login
> (`headless=False`). Once a session is saved under `.auth/`, all crawling,
> capturing, and vault-building runs **headless** on the VPS. So the only step
> that needs special handling is the initial login.

> **Personal use only.** Keep the project's guardrails: no DRM circumvention, no
> stored passwords, polite crawl rates, and nothing captured is ever committed.

---

## 1. Provision the VPS

Assumes Ubuntu/Debian. Run a non-`root` user for the app; use `sudo` only for
package installs.

```bash
# As root / with sudo: create a run user (skip if you already have one)
adduser --disabled-password --gecos "" toolkit
usermod -aG sudo toolkit
su - toolkit

# System packages
sudo apt-get update
sudo apt-get install -y \
  git build-essential \
  python3 python3-venv python3-pip \
  xvfb                      # virtual display, only needed for on-VPS login (§5)

# Node.js 18+ (for the webapp frontend; also for optional markmap HTML)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

The Playwright Chromium **system libraries** are installed in §2 via
`playwright install --with-deps chromium` — no need to hand-list them.

---

## 2. Clone & install (CLI toolkits)

```bash
git clone https://github.com/syedamber91/knowledge-toolkit.git
cd knowledge-toolkit

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"                    # package + pytest
playwright install --with-deps chromium    # downloads Chromium + apt system libs
cp .env.example .env
```

`pip install -e ".[dev]"` installs every runtime dependency from
`pyproject.toml` (playwright, yt-dlp, trafilatura, beautifulsoup4/lxml, typer,
rich, pydantic, …) and registers the four CLI entry points:
`soic-toolkit`, `substack-toolkit`, `youtube-toolkit`, `web-toolkit`.

Smoke-test the install:

```bash
soic-toolkit --help
youtube-toolkit --help
pytest -q          # offline unit tests should pass; login/network tests self-skip
```

---

## 3. Configure `.env` for Linux

Several defaults are macOS-specific and **will not exist on a Linux VPS**. Set
real VPS paths before building any vault. Edit `.env`:

| Variable | Default | On the VPS |
|---|---|---|
| `SOIC_BASE_URL` | `https://learn.soic.in` | keep |
| `SOIC_LOGGEDIN_URL_FRAGMENT` | `/learn` | keep |
| `SOIC_CRAWL_HEADED` | `false` | **keep `false`** — headless crawl |
| `SOIC_VAULT_DIR` | repo `./vault` | fine as-is, or set e.g. `~/vaults/soic` |
| `SOIC_BUNDLE_SLUGS` | `SOIC-Course` | set to your bundle(s) |
| `SOIC_WATERMARK_LINES` | unset | optional: `you@example.com\|+910000000000` |
| `SUBSTACK_VAULT_DIR` | `~/Documents/Obsidian Vault/Substack` (macOS) | **override**, e.g. `~/vaults/substack` |
| `SUBSTACK_CRAWL_HEADED` | `true` | only affects login; irrelevant once `.auth` exists |
| `MEDIA_VAULT_DIR` | `~/Library/Mobile Documents/iCloud~md~obsidian/...` (macOS/iCloud) | **override**, e.g. `~/vaults/media` |

The crawl-delay variables (`*_MIN_DELAY` / `*_MAX_DELAY`) can stay at their
polite defaults. Vault directories are created automatically on first build.

```bash
mkdir -p ~/vaults/soic ~/vaults/substack ~/vaults/media   # if you set the paths above
```

---

## 4. Run the CLI toolkits

### 4.1 Authentication — the headless catch

SOIC and Substack login open a **visible browser** and need a display:

- `soic-toolkit login` → `src/soic_toolkit/auth.py` launches `headless=False`.
- `substack-toolkit login --handle <h>` → `src/substack_toolkit/auth.py` does the same.

YouTube and web capture need **no auth** at all. So you only need to solve login
for SOIC/Substack. Two options:

**Option A — log in on your desktop, copy the session up (recommended).**
On your laptop/desktop (which has a GUI), run the login once, then copy the
saved `.auth/` directory to the VPS:

```bash
# On your local machine, inside the repo:
soic-toolkit login                      # browser opens; sign in (incl. OTP/2FA)
substack-toolkit login --handle vutr    # browser opens; sign in to the publication

# Sessions are written to:
#   .auth/state.json            (SOIC)
#   .auth/substack_state.json   (Substack)

# Copy them to the VPS:
scp -r .auth/ toolkit@your-vps:~/knowledge-toolkit/
```

Sessions are long-lived and reusable; redo this only when one expires.

**Option B — drive the one-time login on the VPS over X11/VNC.**
`xvfb-run` alone is **not enough** — login is interactive, so you need to *see
and click* the browser. Forward the display for the single login, then go back
to headless:

```bash
# From your local machine, SSH with X11 forwarding (VPS needs `xauth` + sshd `X11Forwarding yes`):
ssh -X toolkit@your-vps
cd knowledge-toolkit && source .venv/bin/activate
soic-toolkit login      # the browser renders on your local X server
```

If X11 forwarding is unavailable, run a lightweight VNC desktop on the VPS for
the login, then stop it. Either way, once `.auth/` exists, nothing else needs a
display.

> **`substack-toolkit login --from-chrome` does NOT work on Linux.** It reads
> macOS Chrome's cookie store and the macOS Keychain (`security …`). Use Option A
> or B instead.

### 4.2 Capture & build (all headless)

Start with a small `--limit` to confirm the session works, then run the full
capture:

```bash
source .venv/bin/activate

# SOIC (Learnyst portal)
soic-toolkit status                 # confirm saved session is valid
soic-toolkit crawl --limit 5        # quick test
soic-toolkit crawl                  # full, resumable
soic-toolkit build-vault            # writes to SOIC_VAULT_DIR (or ./vault)
soic-toolkit build-map              # optional Markmap (.md always; .html needs Node)

# Substack
substack-toolkit crawl vutr --limit 5
substack-toolkit crawl vutr         # add --free-only for follow-only publications
substack-toolkit build-vault

# YouTube + web (shared catalog & vault, no auth)
youtube-toolkit capture "https://www.youtube.com/@SomeChannel/videos" --limit 5
web-toolkit capture "https://example.com/post"
youtube-toolkit build               # builds the unified YouTube+web vault
```

Crawlers are **resumable**: already-captured URLs are skipped on re-run, so a
scheduled job is safe to repeat.

### 4.3 Scheduling periodic crawls

A cron entry that refreshes captures nightly (sessions in `.auth/` are reused):

```cron
# crontab -e   (as the toolkit user)
0 2 * * * cd /home/toolkit/knowledge-toolkit && \
  ./.venv/bin/substack-toolkit crawl vutr >> ~/crawl.log 2>&1 && \
  ./.venv/bin/substack-toolkit build-vault >> ~/crawl.log 2>&1
```

(Equivalent systemd `.timer` units work too; cron is simplest for a personal box.)

### 4.4 Learning-pack PDFs — known limitation

`scripts/generate_learning_pack.py` and `scripts/generate_vutr_spark.py`
generate an HTML pack and then render it to PDF by shelling out to a **hardcoded
macOS Chrome path**:

```python
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

On Linux that path does not exist, so the PDF step silently fails (the HTML is
still produced). Workarounds on the VPS:

```bash
sudo apt-get install -y chromium-browser    # or: google-chrome-stable
```

Then either render the HTML manually with the Linux binary:

```bash
chromium --headless --disable-gpu \
  --print-to-pdf=output/vutr_spark.pdf --print-to-pdf-no-header output/vutr_spark.html
```

…or symlink the Linux binary to the path the script expects. A clean fix
(OS-aware binary detection) would be a code change and is out of scope for this
doc.

---

## 5. Run the webapp (production)

`webapp/start.sh` is a **dev** launcher (`uvicorn --reload`, `next dev`, bound to
localhost). For a VPS, run the backend and frontend as long-lived services.

### 5.1 Backend (FastAPI, port 8000)

```bash
cd ~/knowledge-toolkit/webapp/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py                       # seeds the SQLite DB (idempotent)
uvicorn main:app --host 0.0.0.0 --port 8000     # no --reload in production
```

The database is `webapp/backend/toolkit.db` (SQLite, created on startup). Health
check: `curl http://localhost:8000/health` → `{"status":"ok"}`.

Keep it alive with a systemd unit, e.g. `/etc/systemd/system/kt-backend.service`:

```ini
[Unit]
Description=Knowledge Toolkit API
After=network.target

[Service]
User=toolkit
WorkingDirectory=/home/toolkit/knowledge-toolkit/webapp/backend
ExecStart=/home/toolkit/knowledge-toolkit/webapp/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now kt-backend
```

### 5.2 Frontend (Next.js, port 3000)

The frontend's API base is read from `NEXT_PUBLIC_API_URL`
(`webapp/frontend/lib/api.ts`, default `http://localhost:8000`). It is baked in
at **build time**, so set it before `npm run build`.

```bash
cd ~/knowledge-toolkit/webapp/frontend
npm ci
NEXT_PUBLIC_API_URL="http://localhost:8000" npm run build
npm run start -- -p 3000             # add -H 0.0.0.0 to bind all interfaces
```

systemd unit `/etc/systemd/system/kt-frontend.service`:

```ini
[Unit]
Description=Knowledge Toolkit UI
After=network.target kt-backend.service

[Service]
User=toolkit
WorkingDirectory=/home/toolkit/knowledge-toolkit/webapp/frontend
ExecStart=/usr/bin/npm run start -- -p 3000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 5.3 Reaching the UI — CORS & exposure

The backend's CORS allow-list is **hardcoded** to `http://localhost:3000`
(`webapp/backend/main.py`). That shapes how you expose it — two no-code-change
options:

**Option A — SSH tunnel (recommended for personal use).**
Don't expose any port publicly. Tunnel both ports from your laptop:

```bash
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 toolkit@your-vps
# then browse http://localhost:3000 on your laptop
```

The browser origin stays `localhost:3000`, which matches the hardcoded CORS
allow-list, and `NEXT_PUBLIC_API_URL=http://localhost:8000` works as-is. Zero
public exposure, zero edits. (Build the frontend with the default
`NEXT_PUBLIC_API_URL`.)

**Option B — nginx reverse proxy (public access).**
Serve the frontend and proxy the backend under **one public origin** so browser
requests are **same-origin** and CORS never triggers. Set `NEXT_PUBLIC_API_URL`
to that same public origin at build time. Example `nginx` server block:

```nginx
server {
    listen 80;
    server_name kt.example.com;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
    }
    # Backend API (same origin → no CORS)
    location ~ ^/(runs|topics|pipeline|health) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

Build the frontend with `NEXT_PUBLIC_API_URL="http://kt.example.com"` so it calls
the proxied paths on the same origin. Lock down the raw ports with a firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp           # (and 443 once you add TLS)
sudo ufw deny 3000 && sudo ufw deny 8000
sudo ufw enable
```

> Because the allow-list is pinned to `localhost:3000`, a browser on a *different*
> host calling `:8000` **directly** (not through the same-origin proxy) is blocked
> by CORS. The same-origin proxy in Option B sidesteps this; a code change to make
> `allow_origins` configurable would be the clean long-term fix.

---

## 6. Persistence & backup

These directories hold sessions, captured content, and the UI database. They are
**gitignored — never commit them** — and must survive redeploys:

| Path | Contents |
|---|---|
| `.auth/` | `state.json` (SOIC) + `substack_state.json` (Substack) |
| `data/` | resumable crawl catalogs (`content.json`, `substack.json`, `media.json`) |
| `output/` | generated mind maps / learning-pack HTML & PDF |
| `vault/` (or your `*_VAULT_DIR` targets) | the built Obsidian vaults |
| `webapp/backend/toolkit.db` | the webapp's SQLite database |

Back up `.auth/` (avoid re-logins) and `data/` (preserves crawl progress). The
vaults and DB can be regenerated from `data/`, but back them up if convenient.

---

## 7. Known limitations on Linux (doc-only summary)

| Limitation | Workaround |
|---|---|
| SOIC/Substack login opens a visible browser (`headless=False`) | Log in on a desktop and copy `.auth/` (§4.1 A), or use X11/VNC for the one-time login (§4.1 B) |
| `substack-toolkit login --from-chrome` is macOS-only (Keychain + macOS cookie path) | Use the browser login flow instead (§4.1) |
| Learning-pack PDF scripts hardcode the macOS Chrome path | Install `chromium`, render the HTML manually or symlink the binary (§4.4) |
| Webapp backend CORS pinned to `http://localhost:3000` | SSH tunnel (Option A) or same-origin nginx proxy (Option B) (§5.3) |
| `MEDIA_VAULT_DIR` / `SUBSTACK_VAULT_DIR` default to macOS/iCloud paths | Override both in `.env` (§3) |

Each "proper fix" above is a code change; this guide deliberately works around
them without modifying the codebase.

---

## 8. Troubleshooting

- **Playwright errors about missing shared libraries** → re-run
  `playwright install --with-deps chromium` (the `--with-deps` flag installs the
  apt packages Chromium needs).
- **Captures come back empty / a `401`-style bounce** → the saved session in
  `.auth/` has expired. Re-login (§4.1) and copy the refreshed `.auth/` up.
- **Frontend shows "API error"** → wrong `NEXT_PUBLIC_API_URL` (remember it is
  baked in at build time — rebuild after changing it), or a CORS mismatch (use
  Option A or B in §5.3).
- **`soic-toolkit build-map` produces only `.md`, no `.html`** → the interactive
  HTML render needs Node (`npx markmap-cli`); the Markdown output is complete on
  its own.
