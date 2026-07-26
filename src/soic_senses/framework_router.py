"""Route a company/situation to the applicable SOIC decision framework(s).

Parses `decision-frameworks-v1.md` (the durable-mechanism layer distilled
from the gated sector notes) into a queryable registry, and does simple
deterministic keyword matching -- no LLM call, so it's fast, free, and
auditable. This is deliberately not "smart" routing: the judgment of which
framework applies is still made by whoever calls this (a human or an LLM
reasoning step), the router just surfaces candidates so that judgment isn't
starting from a blank page of 17+ frameworks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union


@dataclass
class Framework:
    id: str
    title: str
    body: str


_HEADER = re.compile(r"^## (F\d+)\.\s+(.+)$", re.MULTILINE)


def load_frameworks(path: Union[str, Path]) -> List[Framework]:
    """Parse every `## F<n>. <title>` section into a Framework.

    Non-framework headers (the doc title, section dividers like
    "## Batch-4 additions") are ignored since they don't match the
    `F<digits>.` pattern.
    """
    text = Path(path).read_text(encoding="utf-8")
    matches = list(_HEADER.finditer(text))

    frameworks = []
    for i, m in enumerate(matches):
        fid, title = m.group(1), m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        frameworks.append(Framework(id=fid, title=title, body=body))
    return frameworks


def match_frameworks(frameworks: List[Framework], keywords: List[str]) -> List[Framework]:
    """Rank frameworks by how many of the given keywords appear in their body.

    Case-insensitive substring match. Frameworks with zero hits are dropped
    entirely rather than returned in an arbitrary tail -- an empty result
    is a real finding ("none of these frameworks look relevant"), not a
    ranking failure to paper over.
    """
    scored = []
    for fw in frameworks:
        haystack = (fw.title + " " + fw.body).lower()
        score = sum(1 for kw in keywords if kw.lower() in haystack)
        if score > 0:
            scored.append((score, fw))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [fw for _, fw in scored]
