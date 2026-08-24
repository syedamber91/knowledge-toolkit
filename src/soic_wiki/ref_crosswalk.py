"""Turn a REF code into the lecture it names.

NEVER infer a lecture from a REF code's letters. `TVGPF` reads like "TVGP
Framework" and actually resolves to "18.01.26 Part 1 Valuations"; two agents
independently guessed wrong in one session and reported a citation as broken
when it was sound. This module is the only sanctioned resolution path.

A REF code is NOT a unique key: 25 of the 221 real codes (short per-module
letter suffixes like `MODULB`, `HOWA`, `MASTEC`, `SOICA`) were assigned
independently within each module's own refs file and collide across
modules — `MODULB` alone names eight different lessons. `load_crosswalk`
therefore maps a REF to the *set* of lesson_ids it names rather than raising
on collision. The correct lesson is resolved by pairing the REF with the
citation's own timestamp: among a code's candidates, the right one is
whichever lesson's raw transcript actually contains that timestamp marker.
If zero or more than one candidate contains it, that is a genuine
unresolvable citation — `resolve()` returns None rather than guessing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from soic_method.corpus import load_corpus
from soic_method.models import LessonRecord

_TS = r"\[(\d{2}:\d{2}:\d{2})\]"


def load_crosswalk(refs_dir: Path) -> Dict[str, Set[str]]:
    """REF code -> the set of lesson_ids that code maps to.

    Does NOT raise: 25 of 221 real codes are ambiguous (e.g. MODULB maps to
    eight lessons). Collision is information for `Resolver.resolve()` to use,
    not an error condition.
    """
    out: Dict[str, Set[str]] = {}
    for f in sorted(Path(refs_dir).glob("*.json")):
        for lesson_id, ref in json.loads(f.read_text()).items():
            out.setdefault(ref, set()).add(lesson_id)
    return out


class Resolver:
    def __init__(self, refs_dir: Path, content_json: Path) -> None:
        self._xw = load_crosswalk(refs_dir)
        self._by_id = {le.lesson_id: le for le in load_corpus(content_json)}

    def candidates(self, ref: str) -> List[LessonRecord]:
        """Every lesson this REF code could name, in no particular order."""
        return [
            self._by_id[lid] for lid in self._xw.get(ref, set())
            if lid in self._by_id
        ]

    def ambiguity(self, ref: str) -> int:
        """How many lessons this REF code could name. 1 == unambiguous."""
        return len(self.candidates(ref))

    def resolve(self, ref: str, ts: str) -> Optional[LessonRecord]:
        """The single candidate whose body_text contains f"[{ts}]".

        None if no candidate contains it, or if more than one does —
        genuinely unresolvable, never picked arbitrarily.
        """
        marker = f"[{ts}]"
        hits = [le for le in self.candidates(ref) if marker in le.body_text]
        return hits[0] if len(hits) == 1 else None

    def title(self, ref: str, ts: str) -> Optional[str]:
        le = self.resolve(ref, ts)
        return le.title if le else None

    def has_timestamp(self, ref: str, ts: str) -> bool:
        return self.resolve(ref, ts) is not None

    def window(self, ref: str, start: str, end: Optional[str] = None) -> str:
        """Raw text from `start` to `end` inclusive; "" if unresolvable."""
        le = self.resolve(ref, start)
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

    def nearby_timestamps(self, ref: str, ts: str) -> List[str]:
        """Markers sharing the same MM: prefix across ALL candidates — for
        reporting a near-miss even when nothing resolves."""
        out: List[str] = []
        seen: Set[str] = set()
        for le in self.candidates(ref):
            for t in re.findall(_TS, le.body_text):
                if t[:5] == ts[:5] and t not in seen:
                    seen.add(t)
                    out.append(t)
        return out
