"""Configuration and filesystem paths.

Values come from a local ``.env`` file (see ``.env.example``) with sensible
defaults. Nothing here contains secrets — authentication is interactive and the
resulting session is stored separately under ``.auth/``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root is two levels up: src/udemy_toolkit/config.py -> repo root
ROOT_DIR = Path(__file__).resolve().parents[2]

AUTH_DIR = ROOT_DIR / ".auth"
DATA_DIR = ROOT_DIR / "data"

STATE_PATH = AUTH_DIR / "udemy_state.json"
CATALOG_PATH = DATA_DIR / "udemy.json"

DEFAULT_VAULT_DIR = (
    Path.home()
    / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault"
)


def resolve_vault_dir() -> Path:
    """Where the Obsidian notes are written; ``UDEMY_VAULT_DIR`` overrides."""
    raw = os.environ.get("UDEMY_VAULT_DIR")
    return Path(raw).expanduser() if raw else DEFAULT_VAULT_DIR


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
    base_url: str = os.environ.get("UDEMY_BASE_URL", "https://www.udemy.com")
    crawl_min_delay: float = _get_float("UDEMY_CRAWL_MIN_DELAY", 1.5)
    crawl_max_delay: float = _get_float("UDEMY_CRAWL_MAX_DELAY", 3.5)
    crawl_headed: bool = _get_bool("UDEMY_CRAWL_HEADED", False)


settings = Settings()


def ensure_dirs() -> None:
    """Create the local working directories if they don't already exist."""
    for d in (AUTH_DIR, DATA_DIR):
        d.mkdir(parents=True, exist_ok=True)
