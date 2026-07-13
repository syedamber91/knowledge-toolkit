# Cloud vault sync — reaching the Obsidian vault when the laptop is off

**Goal:** let a *cloud* Claude Code session (spawned from the web/app, running in
an ephemeral Linux container) read and write your Obsidian vault even when your
Mac is asleep or off.

## The constraint (read this first)

The cloud container **cannot connect to iCloud Drive** — not when the laptop is
off, and not when it's on. iCloud Drive has no Linux client and no public file
API; the vault only exists at
`~/Library/Mobile Documents/iCloud~md~obsidian/…` on your Apple devices, and
iCloud only syncs *through a running Apple device*.

So "connect to the iCloud vault" is really: **keep an always-on mirror of the
vault that both your Mac and the cloud container can reach.** A private git repo
is that mirror. iCloud stays your device↔device sync; git adds a third,
always-on replica (GitHub) that survives the laptop being off.

```
   Mac / iPhone  ──iCloud sync──►  vault on disk
         │
         │  Obsidian Git plugin: auto-commit + push
         ▼
   Private GitHub repo  ◄────────►  Cloud Claude Code container
      (always on)          clone / pull / build / push  (scripts/vault_sync.py)
```

**Inherent limitation, stated plainly:** while *every* Apple device is off,
nothing pushes *new* iCloud edits anywhere. The cloud sees the **last state the
Mac/iOS pushed to git** before going idle, and writes changes back for the Mac
to pull when it next wakes. That's the best any cloud setup can do — it's a
property of iCloud, not of this toolkit.

> ⚠️ **Guardrail:** captured content is gitignored in *this* repo and must never
> be committed here. The vault mirror is a **separate, private** repo. Keep
> captured material out of `knowledge-toolkit`.

## One-time setup

### 1. Create a private vault repo

Make an **empty private** GitHub repo, e.g. `obsidian-vault`. You can mirror
either:
- **Just the media vault** (the `Obsidian Vault` folder) — simplest; leave
  `VAULT_SUBDIR` unset and make the repo root the vault.
- **The whole iCloud container** — then the media vault is the `Obsidian Vault`
  subfolder, so set `VAULT_SUBDIR="Obsidian Vault"`.

### 2. Mac: Obsidian Git plugin

1. Obsidian → Settings → Community plugins → install **Obsidian Git**.
2. In the vault folder, `git init`, add the private repo as `origin`, push once.
3. Obsidian Git settings: enable **auto commit-and-sync** every N minutes (e.g.
   10) and **push on commit**. Now every change iCloud brings in also lands on
   GitHub automatically.

### 3. iOS (optional)

Obsidian Git works on iOS too, or use **Working Copy** + the Obsidian **Shell
commands**/URI to commit-push. This keeps the mirror fresh even when only your
phone is on.

### 4. Give the cloud session access to the vault repo

The container can only clone repos in the session's GitHub scope. Either:
- **Add it to the session** with `add_repo` (ask Claude: *"add
  `<you>/obsidian-vault` to this session"*), or grant access in the Claude
  GitHub settings (https://claude.ai/admin-settings/claude-in-slack), **or**
- Set `VAULT_GIT_TOKEN` to a fine-grained PAT with access to just that repo and
  use the https clone URL.

### 5. Configure `.env`

```bash
VAULT_GIT_REMOTE=https://github.com/<you>/obsidian-vault.git
# VAULT_SUBDIR="Obsidian Vault"   # only if the repo is the whole iCloud container
# VAULT_LOCAL_DIR=~/obsidian-vault
# VAULT_GIT_BRANCH=main
# VAULT_GIT_TOKEN=...             # only if not using the session's GitHub scope
```

## Using it in a cloud session

`scripts/vault_sync.py` is stdlib-only (no extra installs). Typical flow:

```bash
# 1. Pull the latest vault and point the toolkit at it:
export MEDIA_VAULT_DIR="$(python scripts/vault_sync.py pull)"

# 2. Capture + build as usual (writes into the cloned vault):
youtube-toolkit capture "https://www.youtube.com/@<handle>/videos" --limit 5
youtube-toolkit build          # or substack/instagram/web build

# 3. Push the new notes back so the Mac picks them up on its next pull:
python scripts/vault_sync.py push "youtube+web capture"
```

Subcommands:
- `pull` — clone the repo (or fast-forward it) and print the resolved vault path
  on stdout (so you can `export MEDIA_VAULT_DIR="$(… pull)"`). Fast-forward only,
  because the Mac is the primary author — see conflicts below.
- `path` — just print the resolved `MEDIA_VAULT_DIR` (no network).
- `push "<msg>"` — `git add -A`, commit if there are changes, push (no-op when
  clean). Network verbs retry with exponential backoff (2s/4s/8s/16s).

### Auto-pull on session start (optional)

To have every cloud session start with a fresh vault, add a SessionStart hook
that runs `python scripts/vault_sync.py pull`. See the `session-start-hook`
skill and `.claude/settings.json`.

## Conflicts

`pull` is **fast-forward only**. If both the Mac and a cloud session edited the
vault since the last sync, the ff will refuse rather than silently clobber. That
is deliberate — captured notes are append-heavy so conflicts are rare, but when
one happens, resolve it on the Mac (in Obsidian Git) or `cd` into the clone and
merge/rebase by hand. Don't force-push the vault from the cloud.

## Why git and not Google Drive / an always-on Mac

- **Google Drive / Dropbox** have Linux-reachable APIs, but Obsidian on the Mac
  lives in *iCloud*, so you'd need a second Mac-side tool bridging iCloud→Drive,
  and text merge/history is worse than git.
- **An always-on Mac mini / iOS device** can bridge live iCloud, but that
  reintroduces the "a device must be on" dependency you're trying to remove.

Git gives you an always-on mirror, real history, and native two-way sync with a
code agent — the best fit for a Markdown vault.
