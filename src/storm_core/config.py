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

# --- Agent Reach retrieval breadth layer (optional, off by default) ---------
# See docs/superpowers/specs/2026-08-03-agent-reach-evaluation.md.
REACH_CONFIG = Path(
    os.environ.get("STORM_REACH_CONFIG", _ROOT / "configs" / "reach_channels.yaml")
).expanduser()

# Per-channel subprocess timeout, seconds. A hung scraper must never wedge a run.
REACH_TIMEOUT_SEC = int(os.environ.get("STORM_REACH_TIMEOUT", "60"))


def reach_enabled() -> bool:
    """The whole reach layer is opt-in. Absent/unset env => disabled."""
    return os.environ.get("STORM_REACH_ENABLED", "").strip().lower() in {
        "1", "true", "yes", "on",
    }
