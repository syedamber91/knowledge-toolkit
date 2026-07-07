from __future__ import annotations

import os
from pathlib import Path

_VAULT = Path(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Business Personas/Opportunity-Catalog"
).expanduser()

REPORTS_DIR = Path(
    os.environ.get("STORM_REPORTS_DIR", _VAULT / "STORM-Reports")
).expanduser()

# Project root: src/storm_core/config.py -> repo root
_ROOT = Path(__file__).resolve().parents[2]

HTML_OUT_DIR = Path(
    os.environ.get("STORM_HTML_DIR", _ROOT / "output" / "storm")
).expanduser()

_PERSONAS = Path(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Business Personas/Personas"
).expanduser()

ROSTER_DIR = Path(
    os.environ.get("STORM_ROSTER_DIR", _PERSONAS)
).expanduser()
