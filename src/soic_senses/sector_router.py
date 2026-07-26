"""Route a company/situation to the applicable sector-notebook context.

Structurally mirrors framework_router.py: parses configs/sector_notebooks.yaml
into a queryable registry and does simple deterministic keyword matching --
no LLM call. This is the piece that lets decision_engine discover a newly
seeded sector notebook with zero code changes: growing sector_notebooks.yaml
(and giving each entry a human-curated `keywords:` list) is the only wiring
required for that sector to become discoverable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

import yaml


@dataclass
class Sector:
    slug: str
    notebook_id: str
    title: str
    keywords: List[str] = field(default_factory=list)


def load_sectors(path: Union[str, Path]) -> List[Sector]:
    """Parse configs/sector_notebooks.yaml into a list of Sector.

    A sector entry with no `keywords:` field gets an empty list -- it is
    parseable but can never be matched by match_sectors (zero possible
    keyword hits), rather than raising or guessing keywords on its behalf.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    sectors = []
    for slug, entry in data.get("notebooks", {}).items():
        sectors.append(
            Sector(
                slug=slug,
                notebook_id=entry["notebook_id"],
                title=entry["title"],
                keywords=list(entry.get("keywords", [])),
            )
        )
    return sectors


def match_sectors(sectors: List[Sector], keywords: List[str]) -> List[Sector]:
    """Rank sectors by how many of the given keywords appear in their own
    keyword list. Case-insensitive substring match in both directions
    (a query keyword matching part of a sector keyword, or vice versa),
    same as framework_router's title+body substring match. Sectors with
    zero hits are dropped entirely -- ranked, not padded.
    """
    scored = []
    for sector in sectors:
        haystack = " ".join(sector.keywords).lower()
        score = sum(1 for kw in keywords if kw.lower() in haystack)
        if score > 0:
            scored.append((score, sector))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [s for _, s in scored]
