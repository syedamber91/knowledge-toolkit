"""Caption text -> readable, timestamped transcript.

Pure functions over strings: no network, no filesystem, no browser. This is
the only place caption markup is interpreted, so it is also the only place
that needs to change when a caption format shifts.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# "00:00:04.000 --> 00:00:08.000 align:start position:10%"
_TIMING_RE = re.compile(
    r"^(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})[.,]\d{1,3}\s*-->\s*\d{2}:\d{2}:\d{2}"
)
# Inline caption markup such as <v Speaker> ... </v> or <i> ... </i>.
_TAG_RE = re.compile(r"<[^>]+>")


def format_seconds(total: int) -> str:
    """Seconds -> ``HH:MM:SS``."""
    hours, remainder = divmod(int(total), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def parse_cues(raw: str) -> List[Tuple[int, str]]:
    """Caption file text -> ``(start_seconds, text)`` pairs, blanks dropped."""
    cues: List[Tuple[int, str]] = []
    start: int = 0
    buffer: List[str] = []
    have_timing = False

    def flush() -> None:
        text = " ".join(part.strip() for part in buffer if part.strip()).strip()
        if text:
            cues.append((start, text))
        buffer.clear()

    for line in (raw or "").splitlines():
        stripped = line.strip()
        match = _TIMING_RE.match(stripped)
        if match:
            if have_timing:
                flush()
            start = (
                int(match.group("h")) * 3600
                + int(match.group("m")) * 60
                + int(match.group("s"))
            )
            have_timing = True
            continue
        if not have_timing:
            # Header ("WEBVTT"), metadata, or a cue index before any timing line.
            continue
        if not stripped:
            flush()
            have_timing = False
            continue
        buffer.append(_TAG_RE.sub("", stripped))

    if have_timing:
        flush()
    return cues


def captions_to_transcript(raw: str, paragraph_seconds: int = 60) -> str:
    """Merge cues into ``[HH:MM:SS]``-prefixed paragraphs, one per time bucket."""
    cues = parse_cues(raw)
    if not cues:
        return ""
    paragraphs: List[str] = []
    current_bucket = None
    words: List[str] = []
    for start, text in cues:
        bucket = start // paragraph_seconds
        if current_bucket is None:
            current_bucket = bucket
        elif bucket != current_bucket:
            paragraphs.append(
                f"[{format_seconds(current_bucket * paragraph_seconds)}] " + " ".join(words)
            )
            words = []
            current_bucket = bucket
        words.append(text)
    if words:
        paragraphs.append(
            f"[{format_seconds(current_bucket * paragraph_seconds)}] " + " ".join(words)
        )
    return "\n\n".join(paragraphs)
