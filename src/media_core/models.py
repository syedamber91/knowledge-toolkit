"""Pydantic models for captured media (YouTube videos and web articles).

Intentionally one flat list of ``MediaItem``: each item knows its ``kind``
("youtube" or "article") and its ``source`` (the channel name or the site
domain). The vault builder groups by kind/source for the folder layout and by
topic for the cross-linking, so a video and an article on the same topic share
one topic note.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

KIND_YOUTUBE = "youtube"
KIND_ARTICLE = "article"


class MediaItem(BaseModel):
    kind: str                       # KIND_YOUTUBE | KIND_ARTICLE
    title: str
    url: str
    source: str = ""               # channel name (YouTube) or site domain (web)
    source_id: str = ""            # channel id / bare domain — stable grouping key
    author: str = ""
    published_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None   # YouTube only
    description: str = ""           # video description / article excerpt
    # Transcript (YouTube) or readable article text (web), as Markdown.
    body_markdown: str = ""
    # False when the body could not be captured (e.g. transcript disabled).
    body_accessible: bool = True
    # Canonical topics matched from the shared vocabulary (cross-source links).
    topics: List[str] = Field(default_factory=list)
    # Secondary auto-extracted keyword tags.
    keywords: List[str] = Field(default_factory=list)
    captured_at: Optional[datetime] = None


class MediaCatalog(BaseModel):
    """Top-level container persisted to data/media.json."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    items: List[MediaItem] = Field(default_factory=list)

    def item_urls(self) -> set[str]:
        """All captured item URLs — used to make capture resumable."""
        return {it.url for it in self.items}

    def by_kind(self, kind: str) -> List[MediaItem]:
        return [it for it in self.items if it.kind == kind]
