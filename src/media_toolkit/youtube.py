"""Capture YouTube videos (transcript + metadata) into the media catalog.

Metadata comes from yt-dlp (no API key; resolves single videos, channels, and
playlists). Transcripts come from youtube-transcript-api. Both network seams are
injectable so the capture logic is unit-testable without hitting YouTube. Only
text the platform exposes is stored — no audio/video is downloaded.
"""

from __future__ import annotations

import random
import re
import time
from datetime import datetime, timezone
from typing import Callable, Optional

from rich.console import Console

from .config import settings
from .models import KIND_YOUTUBE, MediaCatalog, MediaItem
from .store import load_catalog as _load_catalog
from .store import save_catalog as _save_catalog
from .topics import keywords, match_topics

console = Console()

_VIDEO_ID_RE = re.compile(r"(?:v=|/shorts/|/embed/|youtu\.be/)([0-9A-Za-z_-]{11})")


# --- network seams (overridable in tests) -----------------------------------

def _ydl(extra: Optional[dict] = None):
    import yt_dlp

    opts = {"quiet": True, "skip_download": True, "no_warnings": True,
            "ignoreerrors": True}
    opts.update(extra or {})
    return yt_dlp.YoutubeDL(opts)


def fetch_info(url: str) -> dict:
    """Full metadata for a single video (yt-dlp)."""
    with _ydl() as y:
        return y.extract_info(url, download=False) or {}


def enumerate_entries(url: str) -> list[dict]:
    """Flat list of {id,url,title} entries for a channel or playlist (yt-dlp)."""
    with _ydl({"extract_flat": "in_playlist"}) as y:
        info = y.extract_info(url, download=False) or {}
    entries: list[dict] = []

    def _walk(node):
        for e in node.get("entries") or []:
            if not e:
                continue
            if e.get("entries"):           # nested tab (Videos/Shorts/Live)
                _walk(e)
            elif e.get("id"):
                entries.append(e)

    if info.get("entries"):
        _walk(info)
    elif info.get("id"):
        entries.append(info)
    return entries


def fetch_transcript(video_id: str) -> str:
    """Plain-text transcript for a video, or "" if none is available.

    Handles both the legacy static ``get_transcript`` API and the newer
    instance ``fetch`` API of youtube-transcript-api.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception:
        return ""
    try:
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            segs = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join(s["text"] for s in segs).strip()
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        return " ".join(getattr(s, "text", "") for s in fetched).strip()
    except Exception as exc:  # noqa: BLE001 - transcripts are often disabled
        console.print(f"  [yellow]no transcript for {video_id}: {exc}[/yellow]")
        return ""


# --- helpers -----------------------------------------------------------------

def video_id_of(url: str) -> str:
    m = _VIDEO_ID_RE.search(url or "")
    if m:
        return m.group(1)
    # bare 11-char id?
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url or ""):
        return url
    return ""


def _parse_upload_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw or not re.fullmatch(r"\d{8}", str(raw)):
        return None
    try:
        return datetime.strptime(str(raw), "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def item_from_info(info: dict, transcript: str) -> MediaItem:
    """Build a MediaItem (kind=youtube) from yt-dlp info + a transcript string."""
    vid = info.get("id") or ""
    url = info.get("webpage_url") or (f"https://www.youtube.com/watch?v={vid}" if vid else "")
    item = MediaItem(
        kind=KIND_YOUTUBE,
        title=info.get("title") or "(untitled)",
        url=url,
        source=info.get("channel") or info.get("uploader") or "",
        source_id=info.get("channel_id") or info.get("uploader_id") or "",
        author=info.get("uploader") or info.get("channel") or "",
        published_at=_parse_upload_date(info.get("upload_date")),
        duration_seconds=info.get("duration"),
        description=(info.get("description") or "").strip(),
        body_markdown=transcript,
        body_accessible=bool(transcript),
    )
    text = f"{item.title}\n{item.description}\n{item.body_markdown}"
    item.topics = match_topics(text)
    item.keywords = keywords(text)
    item.captured_at = datetime.now(timezone.utc)
    return item


# --- public capture ----------------------------------------------------------

InfoFetch = Callable[[str], dict]
TranscriptFetch = Callable[[str], str]
EntriesFetch = Callable[[str], list]


def capture(
    url: str,
    limit: Optional[int] = None,
    *,
    info_fetch: Optional[InfoFetch] = None,
    transcript_fetch: Optional[TranscriptFetch] = None,
    entries_fetch: Optional[EntriesFetch] = None,
) -> MediaCatalog:
    """Capture a single video, or every video of a channel/playlist (resumable).

    A plain ``watch?v=`` / ``youtu.be`` / 11-char id is treated as one video;
    anything else (channel, @handle, playlist) is enumerated first.
    """
    info_fetch = info_fetch or fetch_info
    transcript_fetch = transcript_fetch or fetch_transcript
    entries_fetch = entries_fetch or enumerate_entries

    catalog = _load_catalog()
    existing = catalog.item_urls()

    vid = video_id_of(url)
    if vid:
        targets = [f"https://www.youtube.com/watch?v={vid}"]
    else:
        targets = []
        for e in entries_fetch(url):
            eid = e.get("id")
            if eid:
                targets.append(f"https://www.youtube.com/watch?v={eid}")
        if limit:
            targets = targets[:limit]

    new_count = 0
    for target in targets:
        if target in existing:
            continue
        info = info_fetch(target)
        if not info:
            console.print(f"  [yellow]skipped {target}: no info[/yellow]")
            continue
        transcript = transcript_fetch(info.get("id") or video_id_of(target))
        item = item_from_info(info, transcript)
        if item.url in existing:
            continue
        catalog.items.append(item)
        existing.add(item.url)
        new_count += 1
        _save_catalog(catalog)  # incremental — survive interruption
        flag = "" if item.body_accessible else " [no transcript]"
        console.print(f"  captured: {item.title}{flag}")
        time.sleep(random.uniform(settings.capture_min_delay, settings.capture_max_delay))

    _save_catalog(catalog)
    console.print(f"[green]Done.[/green] {new_count} new YouTube item(s).")
    return catalog
