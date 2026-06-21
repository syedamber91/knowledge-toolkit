"""Pydantic models describing captured Substack content.

A Channel (one publication) contains Posts. Only legitimately rendered text is
stored — never media files. The shape is intentionally flat (Channel -> Post)
because Substack publications are flat lists of posts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class Post(BaseModel):
    title: str
    subtitle: str = ""
    slug: str
    url: str
    author: str = ""
    published_at: Optional[datetime] = None
    # True when the post is marked subscriber-only / paid.
    is_paid: bool = False
    # True when the body text was actually captured (False = paywalled, no access).
    body_accessible: bool = True
    # Post body rendered to Markdown.
    body_markdown: str = ""
    # Canonical topics matched from the shared vocabulary (cross-channel links).
    topics: List[str] = Field(default_factory=list)
    # Secondary auto-extracted keyword tags.
    keywords: List[str] = Field(default_factory=list)
    captured_at: Optional[datetime] = None


class Channel(BaseModel):
    handle: str            # e.g. "vutr"
    name: str = ""         # display name, if known
    url: str               # e.g. https://vutr.substack.com
    posts: List[Post] = Field(default_factory=list)


class SubstackCatalog(BaseModel):
    """Top-level container persisted to data/substack.json."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    channels: List[Channel] = Field(default_factory=list)

    def post_urls(self) -> set[str]:
        """All captured post URLs — used to make crawls resumable."""
        urls: set[str] = set()
        for channel in self.channels:
            for post in channel.posts:
                urls.add(post.url)
        return urls

    def get_channel(self, handle: str) -> Optional[Channel]:
        for channel in self.channels:
            if channel.handle == handle:
                return channel
        return None
