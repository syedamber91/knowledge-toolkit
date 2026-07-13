#!/usr/bin/env python3
"""Git-backed bridge between a cloud Claude Code session and the Obsidian vault.

The cloud container cannot reach iCloud Drive (no Linux client, no public API),
so the vault is mirrored into a *separate private git repo*. On the Mac/iOS the
Obsidian Git plugin auto-commits + pushes that repo alongside iCloud sync; in the
cloud this script clones/pulls it, exposes the right folder as ``MEDIA_VAULT_DIR``
for the toolkit builders, and pushes changes back for the Mac to pull later.

See ``docs/CLOUD_VAULT_SYNC.md`` for the full setup (Mac plugin, iOS, auth scope).

Config (from the environment or ``.env``):
  VAULT_GIT_REMOTE   Clone URL of the private vault repo (required).
                     e.g. https://github.com/<you>/obsidian-vault.git
  VAULT_LOCAL_DIR    Where to clone in the container. Default: ~/obsidian-vault
  VAULT_SUBDIR       Folder *inside* the repo that is the media vault, if the
                     repo root is the whole Obsidian container. Default: "" (root).
                     Set to "Obsidian Vault" if you mirrored the iCloud container.
  VAULT_GIT_BRANCH   Branch to track. Default: main
  VAULT_GIT_TOKEN    Optional PAT injected into an https remote for auth. If the
                     repo is already in the session's GitHub scope, leave unset.

Usage:
  python scripts/vault_sync.py pull                 # clone-or-update, print vault dir
  python scripts/vault_sync.py path                 # print resolved MEDIA_VAULT_DIR
  python scripts/vault_sync.py push "capture batch"  # commit -A + push (if changes)

Typical cloud flow:
  export MEDIA_VAULT_DIR="$(python scripts/vault_sync.py pull)"
  youtube-toolkit build            # or substack/instagram/etc.
  python scripts/vault_sync.py push "youtube+web capture"
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urlunparse

try:  # keep it optional — the repo ships python-dotenv, but stdlib must suffice
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience, not a requirement
    pass


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _local_dir() -> Path:
    return Path(_env("VAULT_LOCAL_DIR", "~/obsidian-vault")).expanduser()


def _vault_dir() -> Path:
    """The folder the toolkit should treat as MEDIA_VAULT_DIR."""
    sub = _env("VAULT_SUBDIR")
    return _local_dir() / sub if sub else _local_dir()


def _branch() -> str:
    return _env("VAULT_GIT_BRANCH", "main")


def _remote() -> str:
    remote = _env("VAULT_GIT_REMOTE")
    if not remote:
        sys.exit(
            "VAULT_GIT_REMOTE is not set. Point it at your private vault repo, "
            "e.g. https://github.com/<you>/obsidian-vault.git "
            "(see docs/CLOUD_VAULT_SYNC.md)."
        )
    token = _env("VAULT_GIT_TOKEN")
    if token and remote.startswith("https://"):
        parts = urlparse(remote)
        if "@" not in parts.netloc:  # don't double-inject credentials
            netloc = f"x-access-token:{token}@{parts.netloc}"
            remote = urlunparse(parts._replace(netloc=netloc))
    return remote


def _git(args: list[str], cwd: Path | None = None, retries: int = 4) -> str:
    """Run git, retrying network verbs with exponential backoff (2s, 4s, 8s, 16s)."""
    networky = bool({"clone", "fetch", "pull", "push"} & set(args))
    delay = 2
    last: subprocess.CompletedProcess[str] | None = None
    for attempt in range(retries if networky else 1):
        last = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
        )
        if last.returncode == 0:
            return last.stdout.strip()
        if not networky or attempt == retries - 1:
            break
        sys.stderr.write(
            f"git {args[0]} failed (attempt {attempt + 1}), retrying in {delay}s...\n"
        )
        time.sleep(delay)
        delay *= 2
    detail = (last.stderr or last.stdout).strip() if last else "unknown error"
    # Never echo a token-bearing URL into logs.
    detail = detail.replace(_env("VAULT_GIT_TOKEN"), "***") if _env("VAULT_GIT_TOKEN") else detail
    sys.exit(f"git {' '.join(a for a in args if 'x-access-token' not in a)} failed:\n{detail}")


def cmd_pull() -> None:
    local = _local_dir()
    branch = _branch()
    if (local / ".git").is_dir():
        _git(["fetch", "origin", branch], cwd=local)
        _git(["checkout", branch], cwd=local)
        # Fast-forward to the remote; the Mac is the primary author of new content.
        _git(["merge", "--ff-only", f"origin/{branch}"], cwd=local)
    else:
        local.parent.mkdir(parents=True, exist_ok=True)
        _git(["clone", "--branch", branch, _remote(), str(local)])
    # Stdout is just the vault path so callers can `export MEDIA_VAULT_DIR="$(... pull)"`.
    print(_vault_dir())


def cmd_path() -> None:
    print(_vault_dir())


def cmd_push(message: str) -> None:
    local = _local_dir()
    if not (local / ".git").is_dir():
        sys.exit(f"No vault clone at {local}. Run `vault_sync.py pull` first.")
    _git(["add", "-A"], cwd=local)
    status = _git(["status", "--porcelain"], cwd=local)
    if not status:
        print("Vault unchanged — nothing to push.")
        return
    _git(["commit", "-m", message], cwd=local)
    _git(["push", "origin", _branch()], cwd=local)
    print(f"Pushed vault changes to origin/{_branch()}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("pull", help="Clone or fast-forward the vault; print its path.")
    sub.add_parser("path", help="Print the resolved MEDIA_VAULT_DIR and exit.")
    p_push = sub.add_parser("push", help="Commit all changes and push.")
    p_push.add_argument(
        "message", nargs="?", default="vault: cloud capture", help="Commit message."
    )
    args = parser.parse_args()

    if args.command == "pull":
        cmd_pull()
    elif args.command == "path":
        cmd_path()
    elif args.command == "push":
        cmd_push(args.message)


if __name__ == "__main__":
    main()
