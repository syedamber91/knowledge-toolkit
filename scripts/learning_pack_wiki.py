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


_NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
_BEYOND_RE = re.compile(r'<div class="beyond">.*?</div>', re.DOTALL)


def build_writer_prompt(chapter: dict, concepts: Dict[str, str], raw: str) -> str:
    bodies = "\n".join(f"--- {s} ---\n{concepts[s]}" for s in chapter["concepts"])
    return (
        f"WRITE-CHAPTER '{chapter['title']}'. Write expert exposition HTML "
        "(h2 sections, p, tables where the data calls for them) covering the "
        "concepts below. This is CLOSED-BOOK: every claim and every number "
        "must appear in the concept notes or raw sources provided; anything "
        'beyond them goes ONLY inside <div class="beyond">...</div> boxes or is '
        'dropped. Return STRICT JSON {"html": str}.\n\n'
        f"CONCEPT NOTES:\n{bodies}\n\nRAW SOURCES:\n{raw}"
    )


def grounding_check(chapter_html: str, sources_text: str) -> List[str]:
    """Numeric tokens in the chapter (outside 'beyond' boxes) missing from sources."""
    body = _BEYOND_RE.sub("", chapter_html)
    src_nums = {n.replace(",", "") for n in _NUM_RE.findall(sources_text)}
    flagged = []
    for n in _NUM_RE.findall(body):
        canon = n.replace(",", "")
        if len(canon) == 1:                    # single digits: prose, not claims
            continue
        if canon not in src_nums:
            flagged.append(n)
    return sorted(set(flagged))


def render_pack_html(title: str, chapters: List[dict]) -> str:
    toc = "\n".join(f'<li><a href="#ch{i}">{c["title"]}</a></li>'
                    for i, c in enumerate(chapters, 1))
    secs = "\n".join(
        f'<section id="ch{i}"><h1>Chapter {i}: {c["title"]}</h1>\n{c["html"]}</section>'
        for i, c in enumerate(chapters, 1))
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title>
<style>
body{{font-family:Georgia,serif;max-width:820px;margin:2rem auto;line-height:1.55;color:#1c1c2e}}
h1{{border-bottom:2px solid #1c1c2e;padding-bottom:.3rem}}
section{{page-break-before:always}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #999;padding:.4rem}}
.beyond{{border:2px dashed #b45309;background:#fffbeb;padding:.6rem;margin:.8rem 0}}
.beyond::before{{content:"Beyond the source";font-weight:700;display:block;color:#b45309}}
</style></head><body>
<h1>{title}</h1><ol>{toc}</ol>
{secs}
</body></html>"""


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wiki-root", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--chapters", help="chapters.json path (render input)")
    ap.add_argument("--stage", choices=["plan", "render"], required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    td = load_topic(Path(a.wiki_root).expanduser(), a.topic)
    if a.stage == "plan":
        print(build_planner_prompt(a.topic, td.concepts))
    else:
        data = json.loads(Path(a.chapters).read_text(encoding="utf-8"))
        html = render_pack_html(data["title"], data["chapters"])
        out = Path(a.out or f"output/packs/{a.topic}/pack.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
