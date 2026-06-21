"""Configuration and filesystem paths for the Substack toolkit.

Values come from the local ``.env`` (shared with the rest of the repo) with
sensible defaults. Nothing here contains secrets: login is interactive and the
resulting session cookie is stored separately under ``.auth/``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root is two levels up: src/substack_toolkit/config.py -> repo root
ROOT_DIR = Path(__file__).resolve().parents[2]

AUTH_DIR = ROOT_DIR / ".auth"
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

# Dedicated Substack-only Obsidian vault. Point SUBSTACK_VAULT_DIR at a folder
# inside your real Obsidian vault to have notes show up directly in Obsidian.
VAULT_DIR = Path(
    os.environ.get("SUBSTACK_VAULT_DIR", "~/Documents/Obsidian Vault/Substack")
).expanduser()

STATE_PATH = AUTH_DIR / "substack_state.json"
CONTENT_PATH = DATA_DIR / "substack.json"


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _get_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    crawl_min_delay: float = _get_float("SUBSTACK_CRAWL_MIN_DELAY", 1.5)
    crawl_max_delay: float = _get_float("SUBSTACK_CRAWL_MAX_DELAY", 3.5)
    crawl_headed: bool = _get_bool("SUBSTACK_CRAWL_HEADED", True)


settings = Settings()


def channel_url(handle: str) -> str:
    """Base URL for a publication handle, e.g. 'vutr' -> https://vutr.substack.com."""
    return f"https://{handle}.substack.com"


def ensure_dirs() -> None:
    """Create the local working directories if they don't already exist."""
    for d in (AUTH_DIR, DATA_DIR, OUTPUT_DIR, VAULT_DIR):
        d.mkdir(parents=True, exist_ok=True)
