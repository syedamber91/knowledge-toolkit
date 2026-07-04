"""Instagram post -> media_core.MediaItem.

The extractor works on a NORMALIZED post dict so it is unit-testable without
Instaloader or a login. The crawler builds these dicts from Instaloader Post
objects (see ``crawler._normalize``). Only openly-rendered text is stored — the
caption — never the image/video file.

Normalized dict shape::

    {
      "shortcode": str,
      "url": str,                 # permalink (/p/<code>/ or /reel/<code>/)
      "caption": str,
      "owner_username": str,
      "owner_fullname": str,      # optional; falls back to username
      "taken_at": datetime | ISO-str | None,
      "is_video": bool,           # True for reels/video posts
      "video_duration": float | None,
      "likes": int | None,
      "comments": int | None,
      "hashtags": list[str],      # without the leading '#'
      "mentions": list[str],      # without the leading '@'
    }
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from media_core.models import KIND_INSTAGRAM, MediaItem
from media_core.topics import match_topics

_TITLE_MAX = 80


def _as_dt(value) -> Optional[datetime]:
    """Coerce a datetime / ISO string / None into a tz-aware datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _title_from_caption(caption: str, owner: str, dt: Optional[datetime]) -> str:
    """First line of the caption (trimmed), else '@owner · date'."""
    stripped = (caption or "").strip()
    if stripped:
        first = stripped.splitlines()[0].strip()
        if first:
            return first[:_TITLE_MAX] + ("…" if len(first) > _TITLE_MAX else "")
    date = dt.date().isoformat() if isinstance(dt, datetime) else ""
    return (f"@{owner} · {date}" if owner else date).strip(" ·") or "(untitled)"


def item_from_post(data: dict) -> MediaItem:
    """Build a MediaItem (kind=instagram) from a normalized post dict."""
    caption = data.get("caption") or ""
    owner = data.get("owner_username") or ""
    dt = _as_dt(data.get("taken_at"))
    is_video = bool(data.get("is_video"))

    # Keywords: hashtags, @mentions, and a reel/post type tag — deterministic.
    keywords: list[str] = []
    seen: set[str] = set()
    for tag in data.get("hashtags") or []:
        k = f"#{tag.lstrip('#')}"
        if k.lower() not in seen:
            seen.add(k.lower()); keywords.append(k)
    for mention in data.get("mentions") or []:
        k = f"@{mention.lstrip('@')}"
        if k.lower() not in seen:
            seen.add(k.lower()); keywords.append(k)
    keywords.append("reel" if is_video else "post")

    duration = None
    if is_video and data.get("video_duration"):
        try:
            duration = int(float(data["video_duration"]))
        except (TypeError, ValueError):
            duration = None

    item = MediaItem(
        kind=KIND_INSTAGRAM,
        title=_title_from_caption(caption, owner, dt),
        url=data.get("url") or "",
        source=owner,
        source_id=owner,
        author=data.get("owner_fullname") or owner,
        published_at=dt,
        duration_seconds=duration,
        body_markdown=caption,
        body_accessible=True,  # captions are public; empty caption is still valid
        like_count=data.get("likes"),
        comment_count=data.get("comments"),
    )
    # Topics from caption text + the hashtag words (helps the shared vocabulary match).
    hashtag_text = " ".join(t.lstrip("#") for t in (data.get("hashtags") or []))
    item.topics = match_topics(f"{caption}\n{hashtag_text}")
    item.keywords = keywords
    item.captured_at = datetime.now(timezone.utc)
    return item
