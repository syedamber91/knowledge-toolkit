"""Shared data + split for the SOIC concept-note tagging experiment (MiniLM vs Laya).

Data: wiki/personas/soic/concepts/*.md of the Learning Vault Invest hub (459 notes, 12 fixed tags,
1-3 tags each, assigned by LLM subagents -> we measure agreement with that tagger, not gold truth).
Split is by `topics` (module) so near-duplicate notes of one module never straddle train/test.
Nothing here is committed: data + models live under output/ (gitignored)."""
import json, os, re
from pathlib import Path

HUB = Path(os.environ.get("LEARNING_VAULT_INVEST",
           Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest"))
CONCEPTS = HUB / "wiki/personas/soic/concepts"
OUT = Path(__file__).resolve().parents[2] / "output" / "system_one_train"
TAGS = ["valuation", "quality-moat", "forensic", "growth-drivers", "cyclicality", "leverage-risk",
        "capital-allocation", "sector-macro", "technicals-timing", "position-sizing-portfolio",
        "behavioral-psychology", "company-case-study"]
SEED, TEST_FRAC = 7, 0.2


def load_notes():
    notes = []
    for p in sorted(CONCEPTS.glob("*.md")):
        t = p.read_text()
        m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
        if not m:
            continue
        head, body = m.groups()
        tags = re.search(r"^tags:\s*\n((?:\s*-\s*.+\n)+)", head + "\n", re.M)
        if not tags:
            continue
        tags = [x.strip() for x in re.findall(r"-\s*(.+)", tags.group(1))]
        topic = re.search(r"^topics:\s*\n\s*-\s*(.+)", head, re.M)
        title = re.search(r"^#+\s+(.+)", body, re.M)
        assert set(tags) <= set(TAGS), (p.name, tags)
        notes.append(dict(slug=p.stem, topic=topic.group(1).strip() if topic else p.stem,
                          tags=tags, title=title.group(1).strip() if title else p.stem,
                          text=body.strip()))
    return notes


def split(notes):
    """Deterministic group split by topic -> (train, test)."""
    import random
    topics = sorted({n["topic"] for n in notes})
    random.Random(SEED).shuffle(topics)
    test_topics = set(topics[: max(1, int(len(topics) * TEST_FRAC))])
    return ([n for n in notes if n["topic"] not in test_topics],
            [n for n in notes if n["topic"] in test_topics])


def y_matrix(notes):
    import numpy as np
    return np.array([[1 if t in n["tags"] else 0 for t in TAGS] for n in notes])
