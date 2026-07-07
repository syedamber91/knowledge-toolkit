from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from storm_core import config

_FM = re.compile(r"^---\s*\n(.*?)\n---", re.S)
_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.M)
_DESC = re.compile(r"^description:\s*(.+?)\s*$", re.M)
_TITLE = re.compile(r"^title:\s*(.+?)\s*$", re.M)
_INDUSTRY = re.compile(r"^industry:\s*(.+?)\s*$", re.M)
_SCALE = re.compile(r"^scale:\s*(.+?)\s*$", re.M)


class Persona(BaseModel):
    name: str
    slug: str
    description: str


def _field(pattern: re.Pattern, frontmatter: str) -> str:
    m = pattern.search(frontmatter)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def discover_roster(roster_dir: Optional[Path] = None) -> List[Persona]:
    d = Path(roster_dir) if roster_dir is not None else config.ROSTER_DIR
    if not d.exists():
        return []
    people: List[Persona] = []
    for md in sorted(d.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        fm_match = _FM.search(text)
        fm = fm_match.group(1) if fm_match else ""
        title = _field(_TITLE, fm)
        if title:
            title = re.sub(r"\s*\(Business Persona\)\s*$", "", title)
        name = _field(_NAME, fm) or title or md.stem
        desc = _field(_DESC, fm)
        if not desc:
            industry = _field(_INDUSTRY, fm)
            scale = _field(_SCALE, fm)
            if industry or scale:
                desc = industry
                if scale:
                    desc = f"{desc} (scale: {scale})" if desc else f"(scale: {scale})"
        people.append(Persona(name=name, slug=md.stem, description=desc))
    people.sort(key=lambda p: p.name)
    return people
