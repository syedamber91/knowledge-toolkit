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

from media_core.config import settings
from media_core.models import KIND_YOUTUBE, MediaCatalog, MediaItem
from media_core.store import load_catalog as _load_catalog
from media_core.store import save_catalog as _save_catalog
from media_core.topics import keywords, match_topics

console = Console()

_VIDEO_ID_RE = re.compile(r"(?:v=|/shorts/|/embed/|youtu\.be/)([0-9A-Za-z_-]{11})")

# Maximum duration (seconds) allowed for capture. YouTube Shorts are ≤60s and
# almost never have accessible transcripts — skip them to keep the vault clean.
MAX_DURATION_SECONDS = 61


# --- network seams (overridable in tests) -----------------------------------

def _ydl(extra: Optional[dict] = None):
    import yt_dlp

    opts = {"quiet": True, "skip_download": True, "no_warnings": True,
            "ignoreerrors": True}
    opts.update(extra or {})
    return yt_dlp.YoutubeDL(opts)


def fetch_info(url: str) -> dict:
    """Full metadata for a single video (yt-dlp), including caption URLs."""
    with _ydl({"writeautomaticsub": True, "subtitleslangs": ["en", "en-orig"]}) as y:
        return y.extract_info(url, download=False) or {}


def _flatten_entries(info: dict) -> list[dict]:
    """Flatten a yt-dlp info dict into a flat list of video entry dicts.

    Handles nested channel tabs (Videos/Shorts/Live), skips null entries, and
    treats a bare single-video info dict (has ``id``, no ``entries``) as one item.
    """
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


def enumerate_entries(url: str) -> list[dict]:
    """Flat list of {id,url,title} entries for a channel or playlist (yt-dlp)."""
    with _ydl({"extract_flat": "in_playlist"}) as y:
        info = y.extract_info(url, download=False) or {}
    return _flatten_entries(info)


def _vtt_to_text(vtt: str) -> str:
    """Strip VTT cue headers/tags and deduplicate repeated lines → plain text."""
    import re as _re
    lines, seen, prev = [], set(), ""
    for line in vtt.splitlines():
        line = line.strip()
        if not line or line.startswith("WEBVTT") or "-->" in line or line.isdigit():
            continue
        # strip inline tags like <00:00:01.000><c>word</c>
        clean = _re.sub(r"<[^>]+>", "", line).strip()
        if clean and clean != prev and clean not in seen:
            lines.append(clean)
            seen.add(clean)
            prev = clean
    return " ".join(lines)


def fetch_transcript_from_info(info: dict) -> str:
    """Extract plain-text transcript from a yt-dlp info dict via caption URLs.

    Prefers manual English captions; falls back to auto-generated ones.
    Downloads the VTT directly — no youtube-transcript-api, no IP issues.
    """
    import urllib.request
    for caption_dict in (info.get("subtitles") or {}, info.get("automatic_captions") or {}):
        for lang in ("en", "en-orig", "en-US"):
            formats = caption_dict.get(lang) or []
            for fmt in formats:
                if fmt.get("ext") in ("vtt", "srv3", "ttml"):
                    url = fmt.get("url")
                    if not url:
                        continue
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=15) as r:
                            raw = r.read().decode("utf-8", errors="replace")
                        text = _vtt_to_text(raw)
                        if text:
                            return text
                    except Exception:
                        continue
    return ""


def fetch_transcript_via_pytubefix(video_id: str) -> str:
    """Extract transcript via pytubefix captions (second fallback after yt-dlp VTT).

    pytubefix uses a different request path than youtube-transcript-api,
    avoiding the IP-block issue from bulk requests.
    """
    try:
        from pytubefix import YouTube
    except Exception:
        return ""
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        caps = yt.captions
        caption = caps.get("a.en") or caps.get("en") or (next(iter(caps.values())) if caps else None)
        if not caption:
            return ""
        vtt = caption.generate_srt_captions()
        return _vtt_to_text(vtt) if vtt else ""
    except Exception as exc:
        console.print(f"  [yellow]pytubefix failed for {video_id}: {exc}[/yellow]")
        return ""


def fetch_transcript(video_id: str) -> str:
    """Plain-text transcript via youtube-transcript-api (last resort fallback).

    Prefer fetch_transcript_from_info() then fetch_transcript_via_pytubefix().
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
        # Guardrail 1: skip Shorts (≤60s) — they rarely have transcripts
        duration = info.get("duration") or 0
        if duration and duration < MAX_DURATION_SECONDS:
            console.print(f"  [dim]skipped (short {duration}s): {info.get('title', target)}[/dim]")
            existing.add(target)  # mark seen so resume skips it too
            continue
        # Try yt-dlp caption URLs first; then pytubefix; finally transcript API
        vid_id = info.get("id") or video_id_of(target)
        transcript = fetch_transcript_from_info(info)
        if not transcript:
            transcript = fetch_transcript_via_pytubefix(vid_id)
        if not transcript:
            transcript = transcript_fetch(vid_id)
        # Guardrail 2: skip videos with no accessible transcript
        if not transcript:
            console.print(f"  [dim]skipped (no transcript): {info.get('title', target)}[/dim]")
            existing.add(target)
            continue
        item = item_from_info(info, transcript)
        if item.url in existing:
            continue
        catalog.items.append(item)
        existing.add(item.url)
        new_count += 1
        _save_catalog(catalog)  # incremental — survive interruption
        console.print(f"  captured: {item.title}")
        time.sleep(random.uniform(settings.capture_min_delay, settings.capture_max_delay))

    _save_catalog(catalog)
    console.print(f"[green]Done.[/green] {new_count} new YouTube item(s).")
    return catalog
