"""Turn a REF code into the lecture it names.

NEVER infer a lecture from a REF code's letters. `TVGPF` reads like "TVGP
Framework" and actually resolves to "18.01.26 Part 1 Valuations"; two agents
independently guessed wrong in one session and reported a citation as broken
when it was sound. This module is the only sanctioned resolution path.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional

from soic_method.corpus import load_corpus
from soic_method.models import LessonRecord

_TS = r"\[(\d{2}:\d{2}:\d{2})\]"


def load_crosswalk(refs_dir: Path) -> Dict[str, str]:
    """REF code -> lesson_id, inverted from the per-module refs/*.json files."""
    out: Dict[str, str] = {}
    for f in sorted(Path(refs_dir).glob("*.json")):
        for lesson_id, ref in json.loads(f.read_text()).items():
            if ref in out and out[ref] != lesson_id:
                raise ValueError(
                    f"REF {ref} maps to two lessons: {out[ref]} and {lesson_id} "
                    f"({f.name}). A REF must identify exactly one lesson."
                )
            out[ref] = lesson_id
    return out


class Resolver:
    def __init__(self, refs_dir: Path, content_json: Path) -> None:
        self._xw = load_crosswalk(refs_dir)
        self._by_id = {le.lesson_id: le for le in load_corpus(content_json)}

    def lesson(self, ref: str) -> Optional[LessonRecord]:
        lid = self._xw.get(ref)
        return self._by_id.get(lid) if lid else None

    def title(self, ref: str) -> Optional[str]:
        le = self.lesson(ref)
        return le.title if le else None

    def has_timestamp(self, ref: str, ts: str) -> bool:
        le = self.lesson(ref)
        return bool(le) and f"[{ts}]" in le.body_text

    def window(self, ref: str, start: str, end: Optional[str] = None) -> str:
        """Raw text from `start` to `end` inclusive; empty string if absent."""
        le = self.lesson(ref)
        if le is None:
            return ""
        m = re.search(re.escape(f"[{start}]"), le.body_text)
        if not m:
            return ""
        if end:
            e = re.search(re.escape(f"[{end}]"), le.body_text[m.start():])
            if e:
                return le.body_text[m.start(): m.start() + e.end() + 200]
        return le.body_text[m.start(): m.start() + 800]

    def nearby_timestamps(self, ref: str, ts: str) -> list:
        """Markers sharing the same MM: prefix — for reporting a near-miss."""
        le = self.lesson(ref)
        if le is None:
            return []
        return [t for t in re.findall(_TS, le.body_text) if t[:5] == ts[:5]]
