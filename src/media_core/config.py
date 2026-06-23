"""Configuration and filesystem paths for the media (YouTube + web) toolkit.

Values come from the shared ``.env`` with sensible defaults. The vault defaults
to a NEW Obsidian vault inside the iCloud container so it syncs for free, kept
separate from the Substack vault but unified across YouTube and web within it.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root: src/media_toolkit/config.py -> repo root
ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"

# Dedicated vault for captured YouTube + web knowledge. Defaults into the Obsidian
# iCloud container (same place the Substack vault lives) so it syncs to iOS/other
# Macs without paying for Obsidian Sync.
_DEFAULT_VAULT = (
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)
VAULT_DIR = Path(os.environ.get("MEDIA_VAULT_DIR", _DEFAULT_VAULT)).expanduser()

# Resumable capture cache (the raw catalog of everything captured).
CONTENT_PATH = DATA_DIR / "media.json"


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    # Polite pacing between network captures (seconds).
    capture_min_delay: float = _get_float("MEDIA_CAPTURE_MIN_DELAY", 1.0)
    capture_max_delay: float = _get_float("MEDIA_CAPTURE_MAX_DELAY", 2.5)


settings = Settings()


def ensure_dirs() -> None:
    for d in (DATA_DIR, VAULT_DIR):
        d.mkdir(parents=True, exist_ok=True)
