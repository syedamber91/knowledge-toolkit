"""Stage C: generate a verified learning pack from a persona wiki.

Loads a topic's synthesized notes + their cited raw posts, plans chapters
(every concept mapped), writes chapters closed-book, checks grounding of
numeric claims, and renders the pack HTML. Chapters are DATA (chapters.json),
not code — the CHAPTERS-sync invariant of the hand-authored packs is gone.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

_FENCE_RE = re.compile(r"^```[a-zA-Z]*\n(.*)\n```$", re.DOTALL)
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def parse_json(raw: str):
    s = raw.strip()
    m = _FENCE_RE.match(s)
    if m:
        s = m.group(1).strip()
    return json.loads(s)


def _split_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text
    _, front, body = text.split("---", 2)
    import yaml
    return (yaml.safe_load(front) or {}), body.strip()


@dataclass
class TopicData:
    topic: str
    topic_body: str
    concepts: Dict[str, str] = field(default_factory=dict)
    sources: Dict[str, List[str]] = field(default_factory=dict)
    raw_texts: Dict[str, str] = field(default_factory=dict)


def load_topic(wiki_root: Path, topic: str) -> TopicData:
    _, tbody = _split_frontmatter(
        (wiki_root / "topics" / f"{topic}.md").read_text(encoding="utf-8"))
    td = TopicData(topic=topic, topic_body=tbody)
    first_line = tbody.splitlines()[0] if tbody else ""
    for slug in _WIKILINK_RE.findall(first_line):
        slug = slug.strip()
        cpath = wiki_root / "concepts" / f"{slug}.md"
        if not cpath.exists():
            continue
        fm, body = _split_frontmatter(cpath.read_text(encoding="utf-8"))
        td.concepts[slug] = body
        td.sources[slug] = [s for s in fm.get("sources", []) if str(s).startswith("raw/")]
        for rel in td.sources[slug]:
            if rel not in td.raw_texts and (wiki_root / rel).exists():
                td.raw_texts[rel] = (wiki_root / rel).read_text(encoding="utf-8")
    return td


def build_planner_prompt(topic: str, concepts: Dict[str, str]) -> str:
    listing = "\n".join(f"--- {s} ---\n{b}" for s, b in concepts.items())
    return (
        f"PLAN-CHAPTERS for '{topic}'. Group the concepts below into 4-6 "
        "pedagogically ordered chapters. EVERY concept slug must appear in "
        'exactly one chapter. Return STRICT JSON {"chapters": [{"title": str, '
        '"concepts": [slug]}]}.\n\n' + listing
    )


def validate_plan(plan: dict, concepts: Iterable[str]) -> List[str]:
    mapped = {s for ch in plan.get("chapters", []) for s in ch.get("concepts", [])}
    return [s for s in concepts if s not in mapped]
