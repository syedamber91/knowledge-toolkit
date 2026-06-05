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

# Project root is two levels up from this file: src/soic_toolkit/config.py -> repo root
ROOT_DIR = Path(__file__).resolve().parents[2]

AUTH_DIR = ROOT_DIR / ".auth"
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

# Where the Obsidian notes are written. Point SOIC_VAULT_DIR at a folder inside
# your real Obsidian vault (e.g. ~/Obsidian/MyVault/SOIC) to have the notes show
# up directly in Obsidian. Defaults to a local ./vault folder in the repo.
VAULT_DIR = Path(
    os.environ.get("SOIC_VAULT_DIR", str(ROOT_DIR / "vault"))
).expanduser()

STATE_PATH = AUTH_DIR / "state.json"
CONTENT_PATH = DATA_DIR / "content.json"
MINDMAP_MD_PATH = OUTPUT_DIR / "mindmap.md"
MINDMAP_HTML_PATH = OUTPUT_DIR / "mindmap.html"


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
    base_url: str = os.environ.get("SOIC_BASE_URL", "https://learn.soic.in")
    logged_in_fragment: str = os.environ.get("SOIC_LOGGEDIN_URL_FRAGMENT", "/learn")
    crawl_min_delay: float = _get_float("SOIC_CRAWL_MIN_DELAY", 1.5)
    crawl_max_delay: float = _get_float("SOIC_CRAWL_MAX_DELAY", 3.5)
    crawl_headed: bool = _get_bool("SOIC_CRAWL_HEADED", False)


settings = Settings()


def ensure_dirs() -> None:
    """Create the local working directories if they don't already exist."""
    for d in (AUTH_DIR, DATA_DIR, OUTPUT_DIR, VAULT_DIR):
        d.mkdir(parents=True, exist_ok=True)
