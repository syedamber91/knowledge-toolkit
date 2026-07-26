"""Load the captured corpus and provide offset-safe text utilities.

``data/content.json`` is the canonical source. The Obsidian "Stock Market
Vault" is a byte-identical derived view (verified 2026-07-20) and must never be
read as a source.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import List

from .models import LessonRecord

# Transcript markers look like "[00:41:12] ".
_MARKER = re.compile(r"\[\d{2}:\d{2}:\d{2}\]")
_WS = re.compile(r"\s+")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_slice(text: str) -> str:
    """Normalize a SLICE for content comparison.

    Never applied to a whole transcript — offsets index raw ``body_text``, so
    global normalization would desynchronize them.
    """
    return _WS.sub(" ", _MARKER.sub(" ", text)).strip().casefold()


def resolve_timestamp(body_text: str, start: int) -> str:
    """Nearest PRECEDING marker before ``start``; "00:00:00" if none."""
    last = "00:00:00"
    for m in _MARKER.finditer(body_text, 0, max(start, 0) + 1):
        if m.start() <= start:
            last = m.group(0)[1:-1]
    return last


def lesson_id_from_url(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def load_corpus(path: Path) -> List[LessonRecord]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out: List[LessonRecord] = []
    for course in data.get("courses", []):
        for module in course.get("modules", []) or []:
            for lesson in module.get("lessons", []) or []:
                body = lesson.get("body_text") or ""
                if not body:
                    continue
                out.append(
                    LessonRecord(
                        lesson_id=lesson_id_from_url(lesson.get("url", "")),
                        course_title=course.get("title", ""),
                        module_title=module.get("title", ""),
                        title=lesson.get("title", ""),
                        url=lesson.get("url", ""),
                        body_text=body,
                        ai_summary=lesson.get("ai_summary") or "",
                        text_hash=hash_text(body),
                    )
                )
    return out
