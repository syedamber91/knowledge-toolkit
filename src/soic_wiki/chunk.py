"""Marker-aligned chunking and fast timestamp resolution.

Every chunk boundary falls on a ``[HH:MM:SS]`` marker, so any span carved from
a transcript is citable by construction — there is no such thing as a chunk
that cannot be pointed at.

This module supports S3 (supplementary retrieval) and the frequency gates. It
is deliberately NOT used by S1, which reads whole lessons: eligible lessons are
median ~49KB and max ~290KB, so every one fits in a single context window. The
old design chunked because it reasoned per-TOPIC (~1.6MB); per-LESSON the
problem does not exist.
"""

from __future__ import annotations

import bisect
import re
from typing import List, Optional, Tuple

from pydantic import BaseModel

MARKER = re.compile(r"\[(\d{2}):(\d{2}):(\d{2})\]")

TARGET_CHARS = 6000
OVERLAP_CHARS = 1200
SNAP_WINDOW = 1500


class MarkerIndex:
    """Sorted ``[HH:MM:SS]`` offsets for one transcript, built once.

    Replaces ``soic_method.corpus.resolve_timestamp``, which re-scans from
    offset 0 on every call. That is O(n) per claim and quadratic over a
    lesson: the largest transcript is ~290KB with 1,696 markers. Behaviour is
    identical; only the cost changes.
    """

    def __init__(self, text: str):
        self._offsets: List[int] = []
        self._stamps: List[str] = []
        for m in MARKER.finditer(text):
            self._offsets.append(m.start())
            self._stamps.append(m.group(0)[1:-1])

    def __len__(self) -> int:
        return len(self._offsets)

    @property
    def offsets(self) -> List[int]:
        return self._offsets

    def timestamp_at(self, pos: int) -> str:
        """Nearest PRECEDING marker at or before ``pos``; "00:00:00" if none."""
        i = bisect.bisect_right(self._offsets, pos) - 1
        return self._stamps[i] if i >= 0 else "00:00:00"

    def next_marker_at_or_after(self, pos: int) -> Optional[int]:
        i = bisect.bisect_left(self._offsets, pos)
        return self._offsets[i] if i < len(self._offsets) else None


class Chunk(BaseModel):
    lesson_id: str
    start: int
    end: int
    ts_start: str
    ts_end: str
    text: str


def chunk_transcript(
    lesson_id: str,
    text: str,
    target: int = TARGET_CHARS,
    overlap: int = OVERLAP_CHARS,
    snap: int = SNAP_WINDOW,
) -> List[Chunk]:
    """Split into ~``target``-char chunks whose boundaries are markers.

    A cut point is moved forward to the next marker when one lies within
    ``snap`` chars. If none does (long marker-free stretch), the cut stays put
    rather than running away — an uncitable boundary is preferable to a chunk
    of unbounded size, and the span is still resolvable to the preceding
    marker.
    """
    if not text:
        return []

    idx = MarkerIndex(text)
    out: List[Chunk] = []
    pos = 0
    n = len(text)

    while pos < n:
        want = min(pos + target, n)
        if want < n:
            nxt = idx.next_marker_at_or_after(want)
            if nxt is not None and nxt - want <= snap:
                want = nxt
        out.append(Chunk(
            lesson_id=lesson_id,
            start=pos,
            end=want,
            ts_start=idx.timestamp_at(pos),
            ts_end=idx.timestamp_at(max(want - 1, pos)),
            text=text[pos:want],
        ))
        if want >= n:
            break
        # Step back for overlap, then snap forward so the next chunk also
        # begins on a marker.
        step = max(want - overlap, pos + 1)
        nxt = idx.next_marker_at_or_after(step)
        pos = nxt if (nxt is not None and nxt < want) else step

    return out
