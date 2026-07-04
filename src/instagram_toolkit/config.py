"""Configuration and paths for the Instagram toolkit.

Instagram capture writes into the SHARED media catalog (``data/media.json``) and
the unified Obsidian vault via ``media_core`` — so its posts cross-link with the
YouTube and web captures by topic. Only the session cookie lives here, under
``.auth/`` — never a password. Instagram blocks fast scrapers aggressively, so
the default pacing is slower than the media default.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root: src/instagram_toolkit/config.py -> repo root
ROOT_DIR = Path(__file__).resolve().parents[2]

AUTH_DIR = ROOT_DIR / ".auth"
STATE_PATH = AUTH_DIR / "instagram_state.json"

# The cookie that proves an authenticated Instagram session (httpOnly).
SESSION_COOKIE = "sessionid"


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    # Instagram temp-blocks fast scrapers even when logged in — pace slowly.
    crawl_min_delay: float = _get_float("INSTAGRAM_CRAWL_MIN_DELAY", 3.0)
    crawl_max_delay: float = _get_float("INSTAGRAM_CRAWL_MAX_DELAY", 6.0)


settings = Settings()


def post_url(shortcode: str, is_reel: bool = False) -> str:
    """Canonical permalink for a shortcode, e.g. 'ABC' -> .../reel/ABC/ or /p/ABC/."""
    kind = "reel" if is_reel else "p"
    return f"https://www.instagram.com/{kind}/{shortcode}/"


def ensure_dirs() -> None:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
