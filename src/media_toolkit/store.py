"""Load/save the single shared media catalog (data/media.json).

Both the YouTube and web capture paths read and append to the same catalog, so a
video and an article live in one file and share the same topic notes.
"""

from __future__ import annotations

from .config import CONTENT_PATH
from .models import MediaCatalog


def load_catalog() -> MediaCatalog:
    if CONTENT_PATH.exists():
        return MediaCatalog.model_validate_json(CONTENT_PATH.read_text())
    return MediaCatalog()


def save_catalog(catalog: MediaCatalog) -> None:
    CONTENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTENT_PATH.write_text(catalog.model_dump_json(indent=2))
