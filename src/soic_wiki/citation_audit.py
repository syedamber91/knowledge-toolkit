"""D13 -- is each rulebook citation real?

The rulebook's `provenance.quote` fields are the author's PARAPHRASE, not
transcript text, so a verbatim presence check cannot work on them. The check
that does work is structural: does the REF resolve to a lesson, and does the
cited timestamp actually exist in that lesson's transcript? Nothing here
judges whether the rule itself is a good rule; it only reports whether the
citation points at something real.

A REF code is NOT a unique key (see soic_wiki.ref_crosswalk) -- 25 of 221
real codes map to more than one lesson. Resolution is always done on the
(ref, timestamp) PAIR via Resolver.resolve()/candidates(), never on the ref
alone, and never by guessing what a code's letters abbreviate.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from pydantic import BaseModel, Field

_REF = re.compile(
    r"^([A-Z][A-Z0-9]*)\s+(\d{2}:\d{2}:\d{2})(?:-(\d{2}:\d{2}:\d{2}))?$")


def parse_ref(ref: Optional[str]) -> Tuple[Optional[str], Optional[str],
                                           Optional[str]]:
    """'MASTEC 00:09:35' -> ('MASTEC', '00:09:35', None);
    'HOWB 00:01:55-00:02:23' -> ('HOWB', '00:01:55', '00:02:23');
    None/''/unparseable -> (None, None, None)."""
    if not ref:
        return (None, None, None)
    m = _REF.match(ref.strip())
    if not m:
        return (None, None, None)
    return (m.group(1), m.group(2), m.group(3))


class CitationCheck(BaseModel):
    rule_id: str
    kind: str
    ref: Optional[str] = None
    ts_start: Optional[str] = None
    ts_end: Optional[str] = None
    resolved: bool = False
    lesson_title: Optional[str] = None
    timestamp_present: bool = False
    ambiguity: int = 0
    nearby: List[str] = Field(default_factory=list)
    status: str = "NO_REF"


def audit(rulebook_path: Path, resolver) -> List[CitationCheck]:
    doc = yaml.safe_load(Path(rulebook_path).read_text())
    out: List[CitationCheck] = []
    for kind in ("rules", "observations"):
        for e in doc.get(kind) or []:
            raw = (e.get("provenance") or {}).get("ref")
            code, start, end = parse_ref(raw)
            c = CitationCheck(rule_id=e["id"], kind=kind[:-1], ref=raw,
                               ts_start=start, ts_end=end)
            if code is None:
                c.status = "NO_REF"
                out.append(c)
                continue

            c.ambiguity = resolver.ambiguity(code)
            if c.ambiguity == 0:
                # No candidate lesson exists for this REF code at all --
                # genuinely unresolvable, distinct from a code that has
                # candidates but none containing the cited timestamp.
                c.status = "UNRESOLVED_REF"
                out.append(c)
                continue

            c.timestamp_present = resolver.has_timestamp(code, start)
            if c.timestamp_present:
                c.resolved = True
                c.lesson_title = resolver.title(code, start)
                c.status = "OK"
            else:
                # Candidates exist, but the timestamp isn't in any of them:
                # a mis-cited timestamp, not a missing lesson.
                c.status = "BAD_TIMESTAMP"
                c.nearby = resolver.nearby_timestamps(code, start)
            out.append(c)
    return out
