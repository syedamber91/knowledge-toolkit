# Persona Wiki POC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an incremental, per-persona "LLM wiki" that turns the static `vutr` persona into research-memory derivatives (entities, concepts, comparisons, open questions, synthesis) that can be revised as new sources are captured, rather than hand-rewritten.

**Architecture:** A new `persona_wiki` Python package **inside the learning-vault repo** (the `de-toolkit` project). It reads captured sources, runs a `claude`-CLI-backed derivative writer behind an injectable seam, stores atomic Obsidian notes under `wiki/personas/vutr/` (topic notes + deduplicated entity/concept notes cross-linked by `[[wikilinks]]`), tracks change-data-capture via per-note `sources`/`last_updated` frontmatter plus an append-only `log.md`, and gates each note through a single-pass QC check. A one-time bootstrap splits the existing `vutr.md` snapshot into that atomic layout.

**Tech Stack:** Python 3.9+, Pydantic v2, Typer, PyYAML, pytest. Reuses `de_toolkit.teach.run_claude` (the `claude -p` shell-out) and `de_toolkit.vault.slugify`.

## Global Constraints

- **Repo:** all code and output live in the **learning-vault repo** at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault` (its own git repo; separate from the SOIC_Scraper repo this plan is filed in). Work happens in a git worktree of that repo.
- **Python:** `requires-python = ">=3.9"` — no 3.10+ syntax (no `X | Y` type unions in annotations that execute; use `Optional[...]`/`List[...]` from `typing`, matching the existing `de_toolkit` code).
- **Pydantic:** v2 (`pydantic>=2.5`, already a dep).
- **New dependency:** add `pyyaml>=6` to `pyproject.toml` `[project.dependencies]`.
- **Offline tests:** no network, no login, no real `claude` CLI call in tests. The LLM is always injected as a stub in tests (the seam is a `Callable[[str], str]`).
- **Determinism:** any function that stamps a date takes an explicit `stamp: str` (ISO `YYYY-MM-DD`) parameter, defaulting to `date.today().isoformat()` only when omitted. Tests always pass an explicit stamp.
- **Path guard:** every write must resolve to a path under the persona-wiki root (`wiki/personas/`). Writes outside it raise `ValueError`. Never write to the authored course, `data/content.json`, or `src/de_toolkit/`.
- **`match_topics` is local:** the spec referenced `media_core`'s `match_topics`, which does **not** exist in this repo. This plan creates a minimal local `persona_wiki/topics.py` vocabulary instead.
- **Reuse, don't reinvent:** import `slugify` from `de_toolkit.vault` and `run_claude` from `de_toolkit.teach` rather than duplicating them.
- **Plan file location:** this plan lives in the SOIC_Scraper repo (with its spec); the code it describes is written in the learning-vault worktree. All `git` commands in tasks target the **learning-vault worktree**.

---

## File Structure (learning-vault repo)

```
src/persona_wiki/
  __init__.py
  config.py        # paths, PERSONA_WIKI_DIR, persona-root resolution, path-guard root
  models.py        # Pydantic: note frontmatter, DerivativeBundle (LLM output), WikiIndex
  storage.py       # frontmatter (de)serialize, write_note with path guard
  topics.py        # local match_topics + vutr vocabulary
  index.py         # read/write index.yaml; register/lookup topics & atomic notes
  log.py           # _last_logged_total + log_ingest (4-shape CDC log)
  llm.py           # injectable seam + prompt builders (derive / bootstrap-split / qc)
  derive.py        # parse DerivativeBundle -> write atomic notes + topic note (dedup)
  cdc.py           # decide CREATE vs REVISE per topic/atomic note
  qc.py            # single-pass QC check -> (passed, reason)
  pipeline.py      # orchestrate steps 1-7 over a batch of sources
  bootstrap.py     # split vutr.md snapshot -> atomic notes (step 2a)
  query.py         # step 5: index -> topic note -> follow wikilinks
  cli.py           # typer app: bootstrap / update / query
data/personas/vutr.md          # committed seed input (copied from SOIC_Scraper)
wiki/personas/vutr/            # output (created at runtime; .gitkeep committed)
tests/persona_wiki/
  test_models.py test_storage.py test_topics.py test_index.py test_log.py
  test_llm.py test_derive.py test_cdc.py test_qc.py test_pipeline.py
  test_bootstrap.py test_query.py test_cli.py
```

---

### Task 1: Worktree, package scaffold, seed input

**Files:**
- Create: `src/persona_wiki/__init__.py`
- Create: `src/persona_wiki/config.py`
- Modify: `pyproject.toml` (add `pyyaml` dep + `persona-wiki` script)
- Create: `data/personas/vutr.md` (copied seed)
- Create: `wiki/personas/.gitkeep`
- Test: `tests/persona_wiki/test_config.py`

**Interfaces:**
- Produces: `persona_wiki.config.persona_root(vault_dir: Path, persona: str) -> Path` (returns `<vault_dir>/wiki/personas/<persona>`); `persona_wiki.config.WIKI_SUBDIR = "wiki/personas"`.

- [ ] **Step 1: Create the worktree in the learning-vault repo**

Run (creates an isolated branch+worktree of the learning-vault repo):
```bash
LV=~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/learning-vault
git -C "$LV" worktree add -b persona-wiki-poc "$LV/.worktrees/persona-wiki-poc"
```
Expected: `Preparing worktree (new branch 'persona-wiki-poc')`. All subsequent steps run inside `$LV/.worktrees/persona-wiki-poc` (call it `$WT`).

- [ ] **Step 2: Copy the persona seed input**

Run (from the SOIC_Scraper repo path where `vutr.md` lives):
```bash
WT=~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/learning-vault/.worktrees/persona-wiki-poc
mkdir -p "$WT/src/persona_wiki" "$WT/data/personas" "$WT/tests/persona_wiki" "$WT/wiki/personas"
cp /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/agents/vutr.md "$WT/data/personas/vutr.md"
touch "$WT/wiki/personas/.gitkeep" "$WT/src/persona_wiki/__init__.py" "$WT/tests/persona_wiki/__init__.py"
```
Expected: no output; files exist.

- [ ] **Step 3: Write the failing test**

Create `tests/persona_wiki/test_config.py`:
```python
from pathlib import Path

from persona_wiki.config import WIKI_SUBDIR, persona_root


def test_persona_root_is_under_wiki_personas():
    root = persona_root(Path("/tmp/lv"), "vutr")
    assert root == Path("/tmp/lv/wiki/personas/vutr")
    assert WIKI_SUBDIR == "wiki/personas"
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki'`.

- [ ] **Step 5: Add the dependency and script entry**

In `pyproject.toml`, add `"pyyaml>=6"` to `[project.dependencies]` and under `[project.scripts]` add:
```toml
persona-wiki = "persona_wiki.cli:app"
```

- [ ] **Step 6: Write `config.py`**

Create `src/persona_wiki/config.py`:
```python
"""Paths and configuration for the persona wiki.

Output lives under ``<vault>/wiki/personas/<persona>/`` — the learning-vault's
existing synthesized-layer namespace. Nothing here writes outside that subtree.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

WIKI_SUBDIR = "wiki/personas"


def resolve_vault_dir(vault_dir: Optional[str] = None) -> Path:
    """Vault root: explicit arg > ``PERSONA_WIKI_DIR`` env > repo root."""
    chosen = vault_dir or os.environ.get("PERSONA_WIKI_DIR")
    if chosen:
        return Path(chosen).expanduser().resolve()
    # repo root = two levels up from src/persona_wiki/config.py
    return Path(__file__).resolve().parents[2]


def persona_root(vault_dir: Path, persona: str) -> Path:
    """Directory holding one persona's wiki (topics/, entities/, concepts/, ...)."""
    return vault_dir / WIKI_SUBDIR / persona
```

- [ ] **Step 7: Install and run the test**

Run: `cd "$WT" && pip install -e ".[dev]" && python -m pytest tests/persona_wiki/test_config.py -v`
Expected: PASS (1 passed).

- [ ] **Step 8: Commit**

```bash
cd "$WT"
git add src/persona_wiki pyproject.toml data/personas wiki/personas tests/persona_wiki
git commit -m "feat(persona-wiki): scaffold package, seed vutr.md, config paths"
```

---

### Task 2: Models — frontmatter, LLM bundle, index

**Files:**
- Create: `src/persona_wiki/models.py`
- Test: `tests/persona_wiki/test_models.py`

**Interfaces:**
- Produces:
  - `NoteFrontmatter(persona: str, kind: str, sources: List[str], last_updated: str, qc: str = "passed", topic: Optional[str] = None, slug: Optional[str] = None, topics: List[str] = [])`
  - `EntityOut(slug: str, body: str)`, `ConceptOut(slug: str, body: str)`
  - `DerivativeBundle(entities: List[EntityOut] = [], concepts: List[ConceptOut] = [], comparisons: str = "", open_questions: str = "", synthesis: str = "")` with `classmethod parse_raw_json(text: str) -> DerivativeBundle`
  - `TopicEntry(file: str, sources: int, last_updated: str)`
  - `AtomicEntry(file: str, topics: List[str] = [], last_updated: str)`
  - `WikiIndex(topics: Dict[str, TopicEntry] = {}, entities: Dict[str, AtomicEntry] = {}, concepts: Dict[str, AtomicEntry] = {})` with `total() -> int`

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_models.py`:
```python
import pytest

from persona_wiki.models import (
    AtomicEntry,
    DerivativeBundle,
    NoteFrontmatter,
    TopicEntry,
    WikiIndex,
)


def test_bundle_parses_json_with_fence():
    raw = '```json\n{"entities": [{"slug": "lsm-tree", "body": "x"}], "synthesis": "s"}\n```'
    bundle = DerivativeBundle.parse_raw_json(raw)
    assert bundle.entities[0].slug == "lsm-tree"
    assert bundle.synthesis == "s"
    assert bundle.concepts == []


def test_bundle_parse_raises_on_garbage():
    with pytest.raises(ValueError):
        DerivativeBundle.parse_raw_json("not json at all")


def test_index_total_counts_all_kinds():
    idx = WikiIndex(
        topics={"kafka": TopicEntry(file="topics/kafka.md", sources=2, last_updated="2026-07-08")},
        entities={"lsm-tree": AtomicEntry(file="entities/lsm-tree.md", topics=["kafka"], last_updated="2026-07-08")},
        concepts={"log-compaction": AtomicEntry(file="concepts/log-compaction.md", last_updated="2026-07-08")},
    )
    assert idx.total() == 3


def test_frontmatter_defaults_qc_passed():
    fm = NoteFrontmatter(persona="vutr", kind="topic", sources=["s1"], last_updated="2026-07-08", topic="kafka")
    assert fm.qc == "passed"
    assert fm.topics == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.models'`.

- [ ] **Step 3: Write `models.py`**

Create `src/persona_wiki/models.py`:
```python
"""Pydantic models for the persona wiki: note frontmatter, the LLM's derivative
output bundle, and the on-disk index."""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

_FENCE_RE = re.compile(r"^```[a-zA-Z]*\n(.*)\n```$", re.DOTALL)


class NoteFrontmatter(BaseModel):
    persona: str
    kind: str                      # "topic" | "entity" | "concept"
    sources: List[str] = Field(default_factory=list)
    last_updated: str
    qc: str = "passed"             # "passed" | "failed"
    qc_reason: Optional[str] = None
    topic: Optional[str] = None    # topic notes
    slug: Optional[str] = None     # atomic notes
    topics: List[str] = Field(default_factory=list)  # atomic back-refs


class EntityOut(BaseModel):
    slug: str
    body: str = ""


class ConceptOut(BaseModel):
    slug: str
    body: str = ""


class DerivativeBundle(BaseModel):
    entities: List[EntityOut] = Field(default_factory=list)
    concepts: List[ConceptOut] = Field(default_factory=list)
    comparisons: str = ""
    open_questions: str = ""
    synthesis: str = ""

    @classmethod
    def parse_raw_json(cls, text: str) -> "DerivativeBundle":
        """Parse the LLM's JSON output, tolerating a ```json fence."""
        stripped = text.strip()
        m = _FENCE_RE.match(stripped)
        if m:
            stripped = m.group(1).strip()
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM did not return valid JSON: {exc}") from exc
        return cls.model_validate(data)


class TopicEntry(BaseModel):
    file: str
    sources: int = 0
    last_updated: str


class AtomicEntry(BaseModel):
    file: str
    topics: List[str] = Field(default_factory=list)
    last_updated: str


class WikiIndex(BaseModel):
    topics: Dict[str, TopicEntry] = Field(default_factory=dict)
    entities: Dict[str, AtomicEntry] = Field(default_factory=dict)
    concepts: Dict[str, AtomicEntry] = Field(default_factory=dict)

    def total(self) -> int:
        return len(self.topics) + len(self.entities) + len(self.concepts)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_models.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/models.py tests/persona_wiki/test_models.py
git commit -m "feat(persona-wiki): pydantic models for frontmatter, bundle, index"
```

---

### Task 3: Storage — frontmatter (de)serialize + path-guarded write

**Files:**
- Create: `src/persona_wiki/storage.py`
- Test: `tests/persona_wiki/test_storage.py`

**Interfaces:**
- Consumes: `NoteFrontmatter` (Task 2), `de_toolkit.vault.slugify`.
- Produces:
  - `dump_note(fm: NoteFrontmatter, body: str) -> str`
  - `parse_note(text: str) -> Tuple[NoteFrontmatter, str]`
  - `write_note(root: Path, rel_path: str, fm: NoteFrontmatter, body: str) -> Path` (path-guarded to `root`)
  - `slugify` (re-exported from `de_toolkit.vault`)

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_storage.py`:
```python
from pathlib import Path

import pytest

from persona_wiki.models import NoteFrontmatter
from persona_wiki.storage import dump_note, parse_note, write_note


def _fm():
    return NoteFrontmatter(
        persona="vutr", kind="entity", slug="lsm-tree",
        sources=["substack/vutr/kafka-internals"], last_updated="2026-07-08",
        topics=["kafka"],
    )


def test_dump_then_parse_roundtrip():
    text = dump_note(_fm(), "Vu Trinh on LSM-trees.")
    fm, body = parse_note(text)
    assert fm.slug == "lsm-tree"
    assert fm.topics == ["kafka"]
    assert body.strip() == "Vu Trinh on LSM-trees."


def test_write_note_creates_file_under_root(tmp_path):
    p = write_note(tmp_path, "entities/lsm-tree.md", _fm(), "body")
    assert p == tmp_path / "entities/lsm-tree.md"
    assert p.read_text(encoding="utf-8").startswith("---")


def test_write_note_rejects_path_outside_root(tmp_path):
    with pytest.raises(ValueError):
        write_note(tmp_path, "../escape.md", _fm(), "body")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_storage.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.storage'`.

- [ ] **Step 3: Write `storage.py`**

Create `src/persona_wiki/storage.py`:
```python
"""Read/write persona-wiki notes as YAML-frontmatter Markdown, guarded so no
write ever escapes the persona-wiki root."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import yaml

from de_toolkit.vault import slugify  # re-exported for callers

from .models import NoteFrontmatter

__all__ = ["slugify", "dump_note", "parse_note", "write_note"]


def dump_note(fm: NoteFrontmatter, body: str) -> str:
    """Serialize frontmatter + body into a Markdown note."""
    data = {k: v for k, v in fm.model_dump().items() if v not in (None, [], "")}
    front = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{front}\n---\n\n{body.strip()}\n"


def parse_note(text: str) -> Tuple[NoteFrontmatter, str]:
    """Inverse of :func:`dump_note`."""
    if not text.startswith("---"):
        raise ValueError("note has no frontmatter")
    _, front, body = text.split("---", 2)
    fm = NoteFrontmatter.model_validate(yaml.safe_load(front) or {})
    return fm, body.strip()


def write_note(root: Path, rel_path: str, fm: NoteFrontmatter, body: str) -> Path:
    """Write a note at ``root/rel_path``, rejecting any path outside ``root``."""
    root = root.resolve()
    target = (root / rel_path).resolve()
    if root != target and root not in target.parents:
        raise ValueError(f"refusing to write outside persona-wiki root: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_note(fm, body), encoding="utf-8")
    return target
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_storage.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/storage.py tests/persona_wiki/test_storage.py
git commit -m "feat(persona-wiki): note (de)serialize + path-guarded write"
```

---

### Task 4: Topics — local `match_topics`

**Files:**
- Create: `src/persona_wiki/topics.py`
- Test: `tests/persona_wiki/test_topics.py`

**Interfaces:**
- Produces: `match_topics(text: str) -> List[str]` (sorted, unique topic slugs); `VUTR_TOPICS: Dict[str, List[str]]`.

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_topics.py`:
```python
from persona_wiki.topics import match_topics


def test_matches_single_topic_whole_word():
    assert match_topics("Kafka partitions and the commit log") == ["kafka"]


def test_matches_multiple_and_dedupes_sorted():
    text = "Spark shuffle vs Kafka, and more Spark AQE"
    assert match_topics(text) == ["kafka", "spark"]


def test_no_false_positive_substring():
    # "sparkling" must not match "spark"
    assert match_topics("sparkling water") == []


def test_unknown_text_returns_empty():
    assert match_topics("gardening tips") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_topics.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.topics'`.

- [ ] **Step 3: Write `topics.py`**

Create `src/persona_wiki/topics.py`:
```python
"""Minimal, deterministic topic matcher for the vutr persona.

Local to this package: the spec referenced media_core's ``match_topics``, which
lives in a different repo. This is a small whole-word vocabulary matcher — no
LLM — so change-detection stays cheap and repeatable.
"""

from __future__ import annotations

import re
from typing import Dict, List

VUTR_TOPICS: Dict[str, List[str]] = {
    "kafka": ["kafka"],
    "spark": ["spark", "apache spark"],
    "airflow": ["airflow"],
    "dbt": ["dbt", "data build tool"],
    "iceberg": ["iceberg", "apache iceberg"],
    "parquet": ["parquet"],
    "flink": ["flink"],
}

_COMPILED = {
    slug: [re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE) for alias in aliases]
    for slug, aliases in VUTR_TOPICS.items()
}


def match_topics(text: str) -> List[str]:
    """Return sorted unique topic slugs whose vocabulary appears in ``text``."""
    hits = {
        slug
        for slug, patterns in _COMPILED.items()
        if any(p.search(text) for p in patterns)
    }
    return sorted(hits)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_topics.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/topics.py tests/persona_wiki/test_topics.py
git commit -m "feat(persona-wiki): local whole-word match_topics vocabulary"
```

---

### Task 5: Index — read/write + register/lookup

**Files:**
- Create: `src/persona_wiki/index.py`
- Test: `tests/persona_wiki/test_index.py`

**Interfaces:**
- Consumes: `WikiIndex`, `TopicEntry`, `AtomicEntry` (Task 2).
- Produces:
  - `load_index(root: Path) -> WikiIndex` (empty if `index.yaml` absent)
  - `save_index(root: Path, index: WikiIndex) -> Path`
  - `register_topic(index, slug, sources_count, stamp) -> None`
  - `register_atomic(index, kind, slug, topic, stamp) -> None` (`kind` ∈ {"entity","concept"}; merges `topic` into back-refs, dedup)
  - `has_topic(index, slug) -> bool`, `has_atomic(index, kind, slug) -> bool`

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_index.py`:
```python
from persona_wiki.index import (
    has_atomic,
    has_topic,
    load_index,
    register_atomic,
    register_topic,
    save_index,
)
from persona_wiki.models import WikiIndex


def test_register_and_lookup_topic():
    idx = WikiIndex()
    register_topic(idx, "kafka", 2, "2026-07-08")
    assert has_topic(idx, "kafka")
    assert idx.topics["kafka"].file == "topics/kafka.md"
    assert idx.topics["kafka"].sources == 2


def test_register_atomic_merges_topic_backrefs():
    idx = WikiIndex()
    register_atomic(idx, "entity", "lsm-tree", "kafka", "2026-07-08")
    register_atomic(idx, "entity", "lsm-tree", "spark", "2026-07-09")
    assert has_atomic(idx, "entity", "lsm-tree")
    assert idx.entities["lsm-tree"].topics == ["kafka", "spark"]  # deduped, ordered


def test_index_roundtrip_on_disk(tmp_path):
    idx = WikiIndex()
    register_topic(idx, "kafka", 1, "2026-07-08")
    save_index(tmp_path, idx)
    reloaded = load_index(tmp_path)
    assert has_topic(reloaded, "kafka")


def test_load_missing_index_is_empty(tmp_path):
    assert load_index(tmp_path).total() == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_index.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.index'`.

- [ ] **Step 3: Write `index.py`**

Create `src/persona_wiki/index.py`:
```python
"""The persona wiki's ``index.yaml`` — the catalog an agent reads first."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import AtomicEntry, TopicEntry, WikiIndex

INDEX_NAME = "index.yaml"


def load_index(root: Path) -> WikiIndex:
    path = root / INDEX_NAME
    if not path.exists():
        return WikiIndex()
    return WikiIndex.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


def save_index(root: Path, index: WikiIndex) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / INDEX_NAME
    path.write_text(
        yaml.safe_dump(index.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def register_topic(index: WikiIndex, slug: str, sources_count: int, stamp: str) -> None:
    index.topics[slug] = TopicEntry(
        file=f"topics/{slug}.md", sources=sources_count, last_updated=stamp
    )


def register_atomic(index: WikiIndex, kind: str, slug: str, topic: str, stamp: str) -> None:
    bucket = index.entities if kind == "entity" else index.concepts
    entry = bucket.get(slug)
    if entry is None:
        entry = AtomicEntry(file=f"{kind}s/{slug}.md", topics=[], last_updated=stamp)
        bucket[slug] = entry
    if topic and topic not in entry.topics:
        entry.topics.append(topic)
    entry.last_updated = stamp


def has_topic(index: WikiIndex, slug: str) -> bool:
    return slug in index.topics


def has_atomic(index: WikiIndex, kind: str, slug: str) -> bool:
    bucket = index.entities if kind == "entity" else index.concepts
    return slug in bucket
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_index.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/index.py tests/persona_wiki/test_index.py
git commit -m "feat(persona-wiki): index.yaml read/write + register/lookup"
```

---

### Task 6: Log — the 4-shape CDC log

**Files:**
- Create: `src/persona_wiki/log.py`
- Test: `tests/persona_wiki/test_log.py`

**Interfaces:**
- Produces:
  - `_last_logged_total(log_path: Path) -> Optional[int]`
  - `log_ingest(log_path: Path, total: int, summary: str, stamp: str) -> bool` (returns True if a line was appended)

Contract (mirrors `media_core`'s `_log_ingest`): first-ever entry is worded as a **backfill**; later entries append only when `total` changed; an unchanged rebuild appends nothing.

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_log.py`:
```python
from persona_wiki.log import _last_logged_total, log_ingest


def test_first_entry_is_backfill(tmp_path):
    log = tmp_path / "log.md"
    appended = log_ingest(log, 14, "3 topic notes, 7 entities, 4 concepts already synthesized", "2026-07-08")
    assert appended is True
    text = log.read_text(encoding="utf-8")
    assert "backfill:" in text and "log started here" in text and "(14 total)" in text


def test_append_on_growth(tmp_path):
    log = tmp_path / "log.md"
    log_ingest(log, 14, "backfill note", "2026-07-08")
    appended = log_ingest(log, 15, "kafka revised (+1 source); +1 entity", "2026-07-09")
    assert appended is True
    assert "(15 total)" in log.read_text(encoding="utf-8")


def test_skip_on_no_change(tmp_path):
    log = tmp_path / "log.md"
    log_ingest(log, 14, "backfill note", "2026-07-08")
    appended = log_ingest(log, 14, "nothing new", "2026-07-09")
    assert appended is False
    assert log.read_text(encoding="utf-8").count("total)") == 1


def test_revision_wording_written_on_change(tmp_path):
    log = tmp_path / "log.md"
    log_ingest(log, 14, "backfill note", "2026-07-08")
    log_ingest(log, 15, "spark revised (+1 source: spark-photon)", "2026-07-10")
    assert "spark revised (+1 source: spark-photon)" in log.read_text(encoding="utf-8")


def test_last_logged_total_none_when_empty(tmp_path):
    assert _last_logged_total(tmp_path / "log.md") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_log.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.log'`.

- [ ] **Step 3: Write `log.py`**

Create `src/persona_wiki/log.py`:
```python
"""Append-only CDC log for the persona wiki (the 4-shape ``_log_ingest`` contract)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

_TOTAL_RE = re.compile(r"\((\d+) total\)")
_HEADER = "# Persona Wiki Log\n\nAppend-only change history.\n"


def _last_logged_total(log_path: Path) -> Optional[int]:
    """Prior total parsed from the last logged entry, or None if no entries yet."""
    if not log_path.exists():
        return None
    matches = _TOTAL_RE.findall(log_path.read_text(encoding="utf-8"))
    return int(matches[-1]) if matches else None


def log_ingest(log_path: Path, total: int, summary: str, stamp: str) -> bool:
    """Append a log line if the total changed. Returns True when a line was written."""
    prior = _last_logged_total(log_path)
    if prior is None:
        line = f"- {stamp} — backfill: {summary} (log started here) ({total} total)\n"
        header = _HEADER + "\n" if not log_path.exists() else ""
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(header + line)
        return True
    if total == prior:
        return False
    line = f"- {stamp} — {summary} ({total} total)\n"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_log.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/log.py tests/persona_wiki/test_log.py
git commit -m "feat(persona-wiki): append-only 4-shape CDC log"
```

---

### Task 7: LLM seam + prompt builders

**Files:**
- Create: `src/persona_wiki/llm.py`
- Test: `tests/persona_wiki/test_llm.py`

**Interfaces:**
- Consumes: `de_toolkit.teach.run_claude`.
- Produces:
  - `LLMFn = Callable[[str], str]`
  - `default_llm(prompt: str) -> str` (wraps `run_claude`)
  - `build_derive_prompt(persona: str, topic: str, source_text: str, existing_note: str = "") -> str`
  - `build_bootstrap_prompt(persona: str, topic: str, section_text: str) -> str`
  - `build_qc_prompt(note_text: str, source_text: str) -> str`

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_llm.py`:
```python
from persona_wiki.llm import (
    build_bootstrap_prompt,
    build_derive_prompt,
    build_qc_prompt,
)


def test_derive_prompt_includes_source_and_json_contract():
    p = build_derive_prompt("vutr", "kafka", "Kafka is optimized for writing.")
    assert "vutr" in p and "kafka" in p
    assert "Kafka is optimized for writing." in p
    assert "entities" in p and "synthesis" in p and "JSON" in p


def test_derive_prompt_includes_existing_note_when_revising():
    p = build_derive_prompt("vutr", "kafka", "new source text", existing_note="OLD NOTE BODY")
    assert "OLD NOTE BODY" in p
    assert "revise" in p.lower()


def test_bootstrap_prompt_carries_section_text():
    p = build_bootstrap_prompt("vutr", "kafka", "### Apache Kafka\n- built by LinkedIn")
    assert "built by LinkedIn" in p and "JSON" in p


def test_qc_prompt_asks_for_verdict():
    p = build_qc_prompt("NOTE", "SOURCE")
    assert "NOTE" in p and "SOURCE" in p
    assert "passed" in p and "reason" in p
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_llm.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.llm'`.

- [ ] **Step 3: Write `llm.py`**

Create `src/persona_wiki/llm.py`:
```python
"""The LLM seam: a ``Callable[[str], str]`` so tests inject a stub, plus the
prompt builders. The default implementation shells out to the local ``claude``
CLI via de_toolkit's ``run_claude``."""

from __future__ import annotations

from typing import Callable

from de_toolkit.teach import run_claude

LLMFn = Callable[[str], str]


def default_llm(prompt: str) -> str:
    return run_claude(prompt)


_BUNDLE_CONTRACT = (
    "Return ONLY a JSON object with these keys: "
    '"entities" (list of {"slug","body"}), "concepts" (list of {"slug","body"}), '
    '"comparisons" (string), "open_questions" (string), "synthesis" (string). '
    "Slugs are lowercase-hyphenated. Bodies and sections are Markdown in the "
    "persona's grounded voice, citing only what the source supports. No prose "
    "outside the JSON."
)


def build_derive_prompt(persona: str, topic: str, source_text: str, existing_note: str = "") -> str:
    revise = ""
    if existing_note:
        revise = (
            "\nYou are revising an existing note (REVISE mode). Here is its current "
            "content — preserve what still holds, integrate the new source, do not "
            "drop correct prior material:\n<<<EXISTING\n" + existing_note + "\nEXISTING\n"
        )
    return (
        f"You are building research-memory derivatives for the '{persona}' persona "
        f"on the topic '{topic}'. Read the source below and produce the five "
        "derivative kinds (entities, concepts, comparisons, open questions, "
        "synthesis) grounded strictly in the persona's positions.\n\n"
        + _BUNDLE_CONTRACT
        + revise
        + "\n\n<<<SOURCE\n" + source_text + "\nSOURCE\n"
    )


def build_bootstrap_prompt(persona: str, topic: str, section_text: str) -> str:
    return (
        f"Split the following authored section of the '{persona}' persona on "
        f"'{topic}' into research-memory derivatives. Do not invent anything not "
        "present in the section.\n\n"
        + _BUNDLE_CONTRACT
        + "\n\n<<<SECTION\n" + section_text + "\nSECTION\n"
    )


def build_qc_prompt(note_text: str, source_text: str) -> str:
    return (
        "You are a fact-checker. Verify that every claim in the NOTE is supported "
        "by the SOURCE. Flag overreach (a conditional source claim rewritten as "
        "absolute, or any claim with no source support).\n"
        'Return ONLY JSON: {"passed": true|false, "reason": "<one sentence>"}.\n\n'
        "<<<NOTE\n" + note_text + "\nNOTE\n\n<<<SOURCE\n" + source_text + "\nSOURCE\n"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_llm.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/llm.py tests/persona_wiki/test_llm.py
git commit -m "feat(persona-wiki): injectable LLM seam + prompt builders"
```

---

### Task 8: Derive — bundle → atomic notes + topic note (with dedup)

**Files:**
- Create: `src/persona_wiki/derive.py`
- Test: `tests/persona_wiki/test_derive.py`

**Interfaces:**
- Consumes: `DerivativeBundle` (2), `storage.write_note`/`slugify` (3), `index.register_*`/`has_atomic` (5).
- Produces:
  - `render_topic_body(bundle: DerivativeBundle) -> str` (Comparisons/Open questions/Synthesis with `[[slug]]` links to every entity+concept)
  - `apply_bundle(root, persona, topic, bundle, sources, index, stamp) -> List[Path]` (writes entity/concept notes deduped, then the topic note; updates index)

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_derive.py`:
```python
from persona_wiki.derive import apply_bundle, render_topic_body
from persona_wiki.index import has_atomic, has_topic
from persona_wiki.models import ConceptOut, DerivativeBundle, EntityOut, WikiIndex


def _bundle():
    return DerivativeBundle(
        entities=[EntityOut(slug="lsm-tree", body="LSM body")],
        concepts=[ConceptOut(slug="log-compaction", body="Compaction body")],
        comparisons="SMJ vs SHJ",
        open_questions="- why?",
        synthesis="Kafka is write-optimized.",
    )


def test_render_topic_body_links_atomics():
    body = render_topic_body(_bundle())
    assert "[[lsm-tree]]" in body and "[[log-compaction]]" in body
    assert "## Comparisons" in body and "## Synthesis" in body


def test_apply_bundle_writes_notes_and_registers(tmp_path):
    idx = WikiIndex()
    written = apply_bundle(tmp_path, "vutr", "kafka", _bundle(), ["s1"], idx, "2026-07-08")
    assert (tmp_path / "topics/kafka.md").exists()
    assert (tmp_path / "entities/lsm-tree.md").exists()
    assert (tmp_path / "concepts/log-compaction.md").exists()
    assert has_topic(idx, "kafka") and has_atomic(idx, "entity", "lsm-tree")
    assert len(written) == 3


def test_shared_entity_written_once_two_topics(tmp_path):
    idx = WikiIndex()
    b1 = DerivativeBundle(entities=[EntityOut(slug="lsm-tree", body="b")], synthesis="k")
    b2 = DerivativeBundle(entities=[EntityOut(slug="lsm-tree", body="b")], synthesis="s")
    apply_bundle(tmp_path, "vutr", "kafka", b1, ["s1"], idx, "2026-07-08")
    apply_bundle(tmp_path, "vutr", "spark", b2, ["s2"], idx, "2026-07-09")
    # one entity file, referenced from both topics
    assert idx.entities["lsm-tree"].topics == ["kafka", "spark"]
    assert (tmp_path / "topics/kafka.md").exists()
    assert (tmp_path / "topics/spark.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_derive.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.derive'`.

- [ ] **Step 3: Write `derive.py`**

Create `src/persona_wiki/derive.py`:
```python
"""Turn a DerivativeBundle into atomic entity/concept notes plus a topic note,
deduplicating shared atomics and wiring wikilinks."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .index import register_atomic, register_topic
from .models import DerivativeBundle, NoteFrontmatter, WikiIndex
from .storage import write_note


def render_topic_body(bundle: DerivativeBundle) -> str:
    refs = [f"[[{e.slug}]]" for e in bundle.entities] + [f"[[{c.slug}]]" for c in bundle.concepts]
    ref_line = ("Related: " + " · ".join(refs) + "\n\n") if refs else ""
    return (
        ref_line
        + "## Comparisons\n" + (bundle.comparisons.strip() or "_none yet_") + "\n\n"
        + "## Open questions\n" + (bundle.open_questions.strip() or "_none yet_") + "\n\n"
        + "## Synthesis\n" + (bundle.synthesis.strip() or "_none yet_") + "\n"
    )


def apply_bundle(
    root: Path,
    persona: str,
    topic: str,
    bundle: DerivativeBundle,
    sources: List[str],
    index: WikiIndex,
    stamp: str,
) -> List[Path]:
    written: List[Path] = []

    for kind, items in (("entity", bundle.entities), ("concept", bundle.concepts)):
        for item in items:
            fm = NoteFrontmatter(
                persona=persona, kind=kind, slug=item.slug, sources=sources,
                last_updated=stamp, topics=[topic],
            )
            written.append(write_note(root, f"{kind}s/{item.slug}.md", fm, item.body))
            register_atomic(index, kind, item.slug, topic, stamp)

    topic_fm = NoteFrontmatter(
        persona=persona, kind="topic", topic=topic, sources=sources, last_updated=stamp,
    )
    written.append(write_note(root, f"topics/{topic}.md", topic_fm, render_topic_body(bundle)))
    register_topic(index, topic, len(sources), stamp)
    return written
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_derive.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/derive.py tests/persona_wiki/test_derive.py
git commit -m "feat(persona-wiki): derive bundle to atomic + topic notes with dedup"
```

---

### Task 9: CDC — decide CREATE vs REVISE

**Files:**
- Create: `src/persona_wiki/cdc.py`
- Test: `tests/persona_wiki/test_cdc.py`

**Interfaces:**
- Consumes: `WikiIndex`, `has_topic` (5), `storage.parse_note` (3).
- Produces:
  - `decide_topic(index: WikiIndex, topic: str) -> str` (returns `"create"` or `"revise"`)
  - `load_existing_topic_body(root: Path, topic: str) -> str` (`""` if absent)

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_cdc.py`:
```python
from persona_wiki.cdc import decide_topic, load_existing_topic_body
from persona_wiki.index import register_topic
from persona_wiki.models import NoteFrontmatter, WikiIndex
from persona_wiki.storage import write_note


def test_decide_create_when_absent():
    assert decide_topic(WikiIndex(), "kafka") == "create"


def test_decide_revise_when_present():
    idx = WikiIndex()
    register_topic(idx, "kafka", 1, "2026-07-08")
    assert decide_topic(idx, "kafka") == "revise"


def test_load_existing_topic_body(tmp_path):
    fm = NoteFrontmatter(persona="vutr", kind="topic", topic="kafka",
                         sources=["s1"], last_updated="2026-07-08")
    write_note(tmp_path, "topics/kafka.md", fm, "## Synthesis\nold body")
    assert "old body" in load_existing_topic_body(tmp_path, "kafka")


def test_load_missing_topic_body_is_empty(tmp_path):
    assert load_existing_topic_body(tmp_path, "kafka") == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_cdc.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.cdc'`.

- [ ] **Step 3: Write `cdc.py`**

Create `src/persona_wiki/cdc.py`:
```python
"""Change-data-capture: decide whether a topic note is new (create) or already
exists (revise), and load the prior body to feed the reviser."""

from __future__ import annotations

from pathlib import Path

from .index import has_topic
from .models import WikiIndex
from .storage import parse_note


def decide_topic(index: WikiIndex, topic: str) -> str:
    return "revise" if has_topic(index, topic) else "create"


def load_existing_topic_body(root: Path, topic: str) -> str:
    path = root / "topics" / f"{topic}.md"
    if not path.exists():
        return ""
    _, body = parse_note(path.read_text(encoding="utf-8"))
    return body
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_cdc.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/cdc.py tests/persona_wiki/test_cdc.py
git commit -m "feat(persona-wiki): CDC create-vs-revise decision + prior-body load"
```

---

### Task 10: QC — single-pass claim check

**Files:**
- Create: `src/persona_wiki/qc.py`
- Test: `tests/persona_wiki/test_qc.py`

**Interfaces:**
- Consumes: `llm.LLMFn`, `llm.build_qc_prompt` (7).
- Produces: `qc_check(note_text: str, source_text: str, llm: LLMFn) -> Tuple[bool, str]` (parses the QC JSON verdict; on unparseable output returns `(False, "unparseable QC verdict")`).

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_qc.py`:
```python
from persona_wiki.qc import qc_check


def _grounded_llm(prompt):
    return '{"passed": true, "reason": "all claims supported"}'


def _overreach_llm(prompt):
    return '{"passed": false, "reason": "absolute claim from conditional source"}'


def _garbage_llm(prompt):
    return "I think it is fine"


def test_grounded_note_passes():
    passed, reason = qc_check("NOTE", "SOURCE", _grounded_llm)
    assert passed is True and "supported" in reason


def test_overreach_note_fails():
    passed, reason = qc_check("NOTE", "SOURCE", _overreach_llm)
    assert passed is False and "conditional" in reason


def test_unparseable_verdict_fails_closed():
    passed, reason = qc_check("NOTE", "SOURCE", _garbage_llm)
    assert passed is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_qc.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.qc'`.

- [ ] **Step 3: Write `qc.py`**

Create `src/persona_wiki/qc.py`:
```python
"""Single-pass QC: ask the LLM whether every claim in a note traces to its
source. Fails closed on any unparseable verdict."""

from __future__ import annotations

import json
import re
from typing import Tuple

from .llm import LLMFn, build_qc_prompt

_FENCE_RE = re.compile(r"^```[a-zA-Z]*\n(.*)\n```$", re.DOTALL)


def qc_check(note_text: str, source_text: str, llm: LLMFn) -> Tuple[bool, str]:
    raw = llm(build_qc_prompt(note_text, source_text)).strip()
    m = _FENCE_RE.match(raw)
    if m:
        raw = m.group(1).strip()
    try:
        verdict = json.loads(raw)
    except json.JSONDecodeError:
        return False, "unparseable QC verdict"
    return bool(verdict.get("passed", False)), str(verdict.get("reason", ""))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_qc.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/qc.py tests/persona_wiki/test_qc.py
git commit -m "feat(persona-wiki): single-pass QC verdict, fails closed"
```

---

### Task 11: Pipeline — orchestrate steps 1–7 over a batch

**Files:**
- Create: `src/persona_wiki/pipeline.py`
- Test: `tests/persona_wiki/test_pipeline.py`

**Interfaces:**
- Consumes: `topics.match_topics` (4), `cdc.*` (9), `llm.build_derive_prompt`/`LLMFn` (7), `DerivativeBundle` (2), `derive.apply_bundle` (8), `qc.qc_check` (10), `index.*` (5), `log.log_ingest` (6).
- Produces:
  - `Source(BaseModel)` with `id: str`, `text: str`
  - `update(root, persona, sources: List[Source], llm: LLMFn, stamp: str) -> dict` (runs the full pipeline; returns `{"written": int, "failed": int, "logged": bool}`)

Behavior: per source → `match_topics` → per topic decide create/revise → derive bundle via `llm` (JSON) → `apply_bundle` → `qc_check` each written note; if QC fails, set that note's `qc: failed` frontmatter and **do not** register it in the index. An LLM/JSON error on a source is caught, counted as `failed`, leaves existing notes untouched, and does not abort the batch. Finally `log_ingest` with the new total.

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_pipeline.py`:
```python
import json

from persona_wiki.index import has_topic, load_index
from persona_wiki.pipeline import Source, update

_BUNDLE = json.dumps({
    "entities": [{"slug": "lsm-tree", "body": "LSM body"}],
    "concepts": [],
    "comparisons": "SMJ vs SHJ",
    "open_questions": "- why?",
    "synthesis": "Kafka is write-optimized.",
})


def _derive_then_pass_llm(prompt):
    # QC prompts contain the word "fact-checker"; everything else is a derive call.
    if "fact-checker" in prompt:
        return '{"passed": true, "reason": "ok"}'
    return _BUNDLE


def _derive_then_fail_llm(prompt):
    if "fact-checker" in prompt:
        return '{"passed": false, "reason": "overreach"}'
    return _BUNDLE


def _broken_llm(prompt):
    if "fact-checker" in prompt:
        return '{"passed": true, "reason": "ok"}'
    return "NOT JSON"


def test_pipeline_creates_and_registers(tmp_path):
    src = Source(id="substack/vutr/kafka-internals", text="Kafka commit log internals.")
    result = update(tmp_path, "vutr", [src], _derive_then_pass_llm, "2026-07-08")
    assert result["failed"] == 0 and result["logged"] is True
    idx = load_index(tmp_path)
    assert has_topic(idx, "kafka")
    assert (tmp_path / "topics/kafka.md").exists()


def test_qc_failure_excludes_from_index(tmp_path):
    src = Source(id="s1", text="Kafka internals.")
    update(tmp_path, "vutr", [src], _derive_then_fail_llm, "2026-07-08")
    idx = load_index(tmp_path)
    # note written to disk but not blessed into the index
    assert (tmp_path / "topics/kafka.md").exists()
    assert not has_topic(idx, "kafka")
    fm_text = (tmp_path / "topics/kafka.md").read_text(encoding="utf-8")
    assert "qc: failed" in fm_text


def test_broken_llm_counts_failure_no_partial(tmp_path):
    src = Source(id="s1", text="Kafka internals.")
    result = update(tmp_path, "vutr", [src], _broken_llm, "2026-07-08")
    assert result["failed"] == 1
    assert not (tmp_path / "topics/kafka.md").exists()


def test_idempotent_rerun_no_duplicate_log(tmp_path):
    src = Source(id="s1", text="Kafka internals.")
    update(tmp_path, "vutr", [src], _derive_then_pass_llm, "2026-07-08")
    second = update(tmp_path, "vutr", [src], _derive_then_pass_llm, "2026-07-09")
    # total unchanged -> no new log line
    assert second["logged"] is False


def test_source_without_topic_is_skipped(tmp_path):
    src = Source(id="s1", text="gardening tips and nothing technical")
    result = update(tmp_path, "vutr", [src], _derive_then_pass_llm, "2026-07-08")
    assert result["written"] == 0 and result["failed"] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_pipeline.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.pipeline'`.

- [ ] **Step 3: Write `pipeline.py`**

Create `src/persona_wiki/pipeline.py`:
```python
"""Orchestrate the 7-step persona-wiki update over a batch of sources."""

from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import BaseModel

from .cdc import decide_topic, load_existing_topic_body
from .derive import apply_bundle
from .index import load_index, save_index
from .llm import LLMFn, build_derive_prompt
from .log import log_ingest
from .models import DerivativeBundle, WikiIndex
from .qc import qc_check
from .storage import parse_note
from .topics import match_topics


class Source(BaseModel):
    id: str
    text: str


def _demote_failed(path: Path, reason: str) -> None:
    """Rewrite a note's frontmatter to qc: failed (kept on disk, not indexed)."""
    fm, body = parse_note(path.read_text(encoding="utf-8"))
    fm.qc = "failed"
    fm.qc_reason = reason
    from .storage import dump_note  # local import avoids cycle at module load
    path.write_text(dump_note(fm, body), encoding="utf-8")


def update(root: Path, persona: str, sources: List[Source], llm: LLMFn, stamp: str) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    index = load_index(root)
    written = 0
    failed = 0

    for src in sources:
        for topic in match_topics(src.text):
            decision = decide_topic(index, topic)
            existing = load_existing_topic_body(root, topic) if decision == "revise" else ""
            try:
                raw = llm(build_derive_prompt(persona, topic, src.text, existing))
                bundle = DerivativeBundle.parse_raw_json(raw)
            except ValueError:
                failed += 1
                continue

            # Derive into a throwaway index first so a QC failure doesn't leak
            # registrations; merge only the blessed notes back.
            staging = WikiIndex(**index.model_dump())
            paths = apply_bundle(root, persona, topic, bundle, [src.id], staging, stamp)

            all_passed = True
            for path in paths:
                passed, reason = qc_check(path.read_text(encoding="utf-8"), src.text, llm)
                if not passed:
                    _demote_failed(path, reason)
                    all_passed = False
            if all_passed:
                index = staging
                written += len(paths)

    save_index(root, index)
    logged = log_ingest(root / "log.md", index.total(), f"{written} note(s) written", stamp)
    return {"written": written, "failed": failed, "logged": logged}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_pipeline.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/pipeline.py tests/persona_wiki/test_pipeline.py
git commit -m "feat(persona-wiki): pipeline orchestration with QC gating + CDC log"
```

---

### Task 12: Bootstrap — split `vutr.md` into atomic notes

**Files:**
- Create: `src/persona_wiki/bootstrap.py`
- Test: `tests/persona_wiki/test_bootstrap.py`

**Interfaces:**
- Consumes: `llm.build_bootstrap_prompt`/`LLMFn` (7), `DerivativeBundle` (2), `derive.apply_bundle` (8), `index.*` (5), `log.log_ingest` (6), `topics.match_topics` (4), `storage.slugify` (3).
- Produces:
  - `parse_persona_sections(md: str) -> List[Tuple[str, str]]` (topic-title, section-text pairs from the `## TECHNICAL POSITIONS` `###` subsections)
  - `bootstrap(root, persona, persona_md, llm: LLMFn, stamp: str) -> dict` (returns `{"topics": int, "logged": bool}`)

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_bootstrap.py`:
```python
import json

from persona_wiki.bootstrap import bootstrap, parse_persona_sections
from persona_wiki.index import load_index

_MD = """\
## IDENTITY
Vu Trinh writes about data engineering.

## TECHNICAL POSITIONS

### Apache Kafka — Internals
- Kafka was built by LinkedIn.

### Apache Spark — Internals
- Spark was created at UC Berkeley.

## QUESTION GENERATION GUIDELINES
Rules here.
"""


def _bootstrap_llm(prompt):
    return json.dumps({
        "entities": [{"slug": "linkedin", "body": "built kafka"}],
        "concepts": [],
        "comparisons": "",
        "open_questions": "",
        "synthesis": "Grounded synthesis.",
    })


def test_parse_sections_finds_only_technical_positions():
    sections = parse_persona_sections(_MD)
    titles = [t for t, _ in sections]
    assert titles == ["Apache Kafka — Internals", "Apache Spark — Internals"]
    assert "built by LinkedIn" in sections[0][1]


def test_bootstrap_seeds_index_and_backfill_log(tmp_path):
    result = bootstrap(tmp_path, "vutr", _MD, _bootstrap_llm, "2026-07-08")
    assert result["topics"] == 2
    idx = load_index(tmp_path)
    assert "kafka" in idx.topics and "spark" in idx.topics
    log_text = (tmp_path / "log.md").read_text(encoding="utf-8")
    assert "backfill:" in log_text and "log started here" in log_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_bootstrap.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.bootstrap'`.

- [ ] **Step 3: Write `bootstrap.py`**

Create `src/persona_wiki/bootstrap.py`:
```python
"""One-time bootstrap: split the authored ``vutr.md`` snapshot's TECHNICAL
POSITIONS sections into the atomic note layout so existing knowledge is kept."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from .derive import apply_bundle
from .index import load_index, save_index
from .llm import LLMFn, build_bootstrap_prompt
from .log import log_ingest
from .models import DerivativeBundle
from .storage import slugify
from .topics import match_topics

_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)
_H3_RE = re.compile(r"^### (.+)$", re.MULTILINE)


def parse_persona_sections(md: str) -> List[Tuple[str, str]]:
    """Return (title, body) for each ``###`` under ``## TECHNICAL POSITIONS``."""
    h2s = list(_H2_RE.finditer(md))
    start = end = None
    for i, m in enumerate(h2s):
        if m.group(1).strip().upper().startswith("TECHNICAL POSITIONS"):
            start = m.end()
            end = h2s[i + 1].start() if i + 1 < len(h2s) else len(md)
            break
    if start is None:
        return []
    block = md[start:end]
    heads = list(_H3_RE.finditer(block))
    sections: List[Tuple[str, str]] = []
    for i, m in enumerate(heads):
        title = m.group(1).strip()
        body_start = m.end()
        body_end = heads[i + 1].start() if i + 1 < len(heads) else len(block)
        sections.append((title, block[body_start:body_end].strip()))
    return sections


def _topic_slug(title: str) -> str:
    """Map a section title to a topic slug via the vocabulary, else slugify."""
    hits = match_topics(title)
    return hits[0] if hits else slugify(title)


def bootstrap(root: Path, persona: str, persona_md: str, llm: LLMFn, stamp: str) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    index = load_index(root)
    sections = parse_persona_sections(persona_md)
    for title, text in sections:
        topic = _topic_slug(title)
        raw = llm(build_bootstrap_prompt(persona, topic, text))
        bundle = DerivativeBundle.parse_raw_json(raw)
        apply_bundle(root, persona, topic, bundle, ["persona-snapshot"], index, stamp)
    save_index(root, index)
    summary = f"{len(index.topics)} topic notes, {len(index.entities)} entities, {len(index.concepts)} concepts already synthesized"
    logged = log_ingest(root / "log.md", index.total(), summary, stamp)
    return {"topics": len(sections), "logged": logged}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_bootstrap.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/bootstrap.py tests/persona_wiki/test_bootstrap.py
git commit -m "feat(persona-wiki): bootstrap vutr.md sections into atomic notes"
```

---

### Task 13: Query — index → topic note → follow wikilinks

**Files:**
- Create: `src/persona_wiki/query.py`
- Test: `tests/persona_wiki/test_query.py`

**Interfaces:**
- Consumes: `index.load_index`/`has_topic` (5), `topics.match_topics` (4), `storage.parse_note` (3).
- Produces: `query(root: Path, question: str) -> str` (reads matching topic notes, follows `[[slug]]` links to entity/concept notes, concatenates their bodies; skips notes whose frontmatter `qc == "failed"`; returns a "no matching notes" sentinel when nothing matches).

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_query.py`:
```python
from persona_wiki.index import load_index, save_index
from persona_wiki.models import NoteFrontmatter, WikiIndex
from persona_wiki.index import register_atomic, register_topic
from persona_wiki.query import query
from persona_wiki.storage import write_note


def _seed(tmp_path):
    idx = WikiIndex()
    register_topic(idx, "kafka", 1, "2026-07-08")
    register_atomic(idx, "entity", "lsm-tree", "kafka", "2026-07-08")
    save_index(tmp_path, idx)
    write_note(tmp_path, "topics/kafka.md",
               NoteFrontmatter(persona="vutr", kind="topic", topic="kafka",
                               sources=["s1"], last_updated="2026-07-08"),
               "## Synthesis\nKafka is write-optimized. Related: [[lsm-tree]]")
    write_note(tmp_path, "entities/lsm-tree.md",
               NoteFrontmatter(persona="vutr", kind="entity", slug="lsm-tree",
                               sources=["s1"], last_updated="2026-07-08", topics=["kafka"]),
               "LSM-trees batch writes.")


def test_query_returns_topic_and_linked_atomic(tmp_path):
    _seed(tmp_path)
    out = query(tmp_path, "how does kafka handle writes?")
    assert "write-optimized" in out
    assert "LSM-trees batch writes." in out  # followed the [[lsm-tree]] link


def test_query_no_match_sentinel(tmp_path):
    _seed(tmp_path)
    assert "no matching" in query(tmp_path, "gardening").lower()


def test_query_skips_qc_failed(tmp_path):
    _seed(tmp_path)
    # demote the topic note to failed
    p = tmp_path / "topics/kafka.md"
    p.write_text(p.read_text().replace("qc: passed", "qc: failed")
                 if "qc: passed" in p.read_text() else
                 p.read_text().replace("kind: topic", "kind: topic\nqc: failed"),
                 encoding="utf-8")
    out = query(tmp_path, "kafka writes")
    assert "write-optimized" not in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_query.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.query'`.

- [ ] **Step 3: Write `query.py`**

Create `src/persona_wiki/query.py`:
```python
"""Answer-routing over the persona wiki: index -> topic note -> linked atomics.

This is deliberately mechanical retrieval (the cheap 'routing' half). It returns
the relevant note bodies; a caller/agent does the final synthesis.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from .index import load_index
from .storage import parse_note
from .topics import match_topics

_WIKILINK_RE = re.compile(r"\[\[([a-z0-9-]+)\]\]")
_NO_MATCH = "No matching notes in the persona wiki."


def _read_if_passed(path: Path) -> str:
    if not path.exists():
        return ""
    fm, body = parse_note(path.read_text(encoding="utf-8"))
    return "" if fm.qc == "failed" else body


def query(root: Path, question: str) -> str:
    index = load_index(root)
    parts: List[str] = []
    for topic in match_topics(question):
        if topic not in index.topics:
            continue
        body = _read_if_passed(root / "topics" / f"{topic}.md")
        if not body:
            continue
        parts.append(f"# {topic}\n{body}")
        for slug in _WIKILINK_RE.findall(body):
            for kind in ("entities", "concepts"):
                atomic = _read_if_passed(root / kind / f"{slug}.md")
                if atomic:
                    parts.append(f"## {slug}\n{atomic}")
    return "\n\n".join(parts) if parts else _NO_MATCH
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_query.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/query.py tests/persona_wiki/test_query.py
git commit -m "feat(persona-wiki): routing query over index + wikilinks, skips qc-failed"
```

---

### Task 14: CLI — `bootstrap` / `update` / `query`

**Files:**
- Create: `src/persona_wiki/cli.py`
- Test: `tests/persona_wiki/test_cli.py`

**Interfaces:**
- Consumes: `config.resolve_vault_dir`/`persona_root` (1), `bootstrap.bootstrap` (12), `pipeline.update`/`Source` (11), `query.query` (13), `llm.default_llm` (7).
- Produces: `app` (Typer app) with commands `bootstrap`, `update`, `query`; each accepts `--vault-dir` and `--persona` (default `vutr`); `bootstrap`/`update` accept `--dry-run` (print plan, call no LLM).

- [ ] **Step 1: Write the failing test**

Create `tests/persona_wiki/test_cli.py`:
```python
from typer.testing import CliRunner

from persona_wiki.cli import app

runner = CliRunner()


def test_help_lists_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "bootstrap" in result.output
    assert "update" in result.output
    assert "query" in result.output


def test_query_on_empty_wiki_reports_no_match(tmp_path):
    result = runner.invoke(app, ["query", "kafka", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No matching" in result.output


def test_bootstrap_dry_run_calls_no_llm(tmp_path):
    # seed a persona snapshot the dry-run can read
    (tmp_path / "data" / "personas").mkdir(parents=True)
    (tmp_path / "data" / "personas" / "vutr.md").write_text(
        "## TECHNICAL POSITIONS\n\n### Apache Kafka\n- built by LinkedIn\n",
        encoding="utf-8",
    )
    result = runner.invoke(
        app, ["bootstrap", "--vault-dir", str(tmp_path), "--dry-run"]
    )
    assert result.exit_code == 0
    assert "Apache Kafka" in result.output  # printed the section it would process
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.cli'`.

- [ ] **Step 3: Write `cli.py`**

Create `src/persona_wiki/cli.py`:
```python
"""Typer CLI for the persona wiki: bootstrap / update / query."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from .bootstrap import bootstrap as run_bootstrap
from .bootstrap import parse_persona_sections
from .config import persona_root, resolve_vault_dir
from .llm import default_llm
from .pipeline import Source, update as run_update
from .query import query as run_query

app = typer.Typer(help="Incremental research-memory wiki for a persona.")


def _root(vault_dir: Optional[str], persona: str) -> Path:
    return persona_root(resolve_vault_dir(vault_dir), persona)


@app.command()
def bootstrap(
    persona: str = typer.Option("vutr", "--persona"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Split the persona snapshot (data/personas/<persona>.md) into atomic notes."""
    vault = resolve_vault_dir(vault_dir)
    snapshot = vault / "data" / "personas" / f"{persona}.md"
    md = snapshot.read_text(encoding="utf-8")
    if dry_run:
        for title, _ in parse_persona_sections(md):
            typer.echo(f"would process section: {title}")
        return
    result = run_bootstrap(_root(vault_dir, persona), persona, md, default_llm, date.today().isoformat())
    typer.echo(f"bootstrapped {result['topics']} topic(s); logged={result['logged']}")


@app.command()
def update(
    persona: str = typer.Option("vutr", "--persona"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
) -> None:
    """(POC) update from stdin: one 'id<TAB>text' source per line."""
    sources = []
    for line in typer.get_text_stream("stdin"):
        line = line.rstrip("\n")
        if not line:
            continue
        sid, _, text = line.partition("\t")
        sources.append(Source(id=sid, text=text))
    result = run_update(_root(vault_dir, persona), persona, sources, default_llm, date.today().isoformat())
    typer.echo(f"written={result['written']} failed={result['failed']} logged={result['logged']}")


@app.command()
def query(
    question: str,
    persona: str = typer.Option("vutr", "--persona"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
) -> None:
    """Route a question to the relevant persona-wiki notes."""
    typer.echo(run_query(_root(vault_dir, persona), question))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$WT" && python -m pytest tests/persona_wiki/test_cli.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Run the full suite**

Run: `cd "$WT" && python -m pytest tests/persona_wiki -v`
Expected: PASS (all persona_wiki tests green).

- [ ] **Step 6: Commit**

```bash
cd "$WT"
git add src/persona_wiki/cli.py tests/persona_wiki/test_cli.py
git commit -m "feat(persona-wiki): typer CLI (bootstrap/update/query)"
```

---

### Task 15: End-to-end bootstrap smoke run (manual, real `claude` CLI)

**Files:**
- Modify: none (runtime verification + a short doc note)
- Create: `wiki/personas/README.md`

**Interfaces:** none (operational task).

- [ ] **Step 1: Run bootstrap dry-run against the real seed**

Run: `cd "$WT" && persona-wiki bootstrap --dry-run`
Expected: prints `would process section: …` lines for each `### ` under TECHNICAL POSITIONS in `data/personas/vutr.md` (Airflow, Spark, Kafka, …). No files written, no LLM called.

- [ ] **Step 2: Run a real bootstrap for ONE topic-limited check**

Note: this calls the local `claude` CLI (uses your subscription). If `claude` is not installed/logged in, skip this step and record that in the README.
Run: `cd "$WT" && persona-wiki bootstrap`
Expected: `bootstrapped N topic(s); logged=True`; `wiki/personas/vutr/index.yaml`, `topics/*.md`, `entities/*.md`, `log.md` now exist with a backfill log entry.

- [ ] **Step 3: Route a query against the built wiki**

Run: `cd "$WT" && persona-wiki query "how does kafka handle writes"`
Expected: prints the Kafka topic note body plus any linked entity/concept notes (or the "No matching notes" sentinel if bootstrap was skipped).

- [ ] **Step 4: Write the output-layer README**

Create `wiki/personas/README.md`:
```markdown
# Persona wikis (synthesized layer)

Incremental research-memory derivatives, one subtree per persona
(`<persona>/topics/`, `entities/`, `concepts/`, `index.yaml`, `log.md`).
Built by the `persona-wiki` CLI (`src/persona_wiki/`). This is synthesized
output — safe to regenerate. It never modifies the authored course.

- `persona-wiki bootstrap` — seed from `data/personas/<persona>.md`.
- `persona-wiki update` — fold new sources in (stdin: `id<TAB>text`).
- `persona-wiki query "<question>"` — route to the relevant notes.
```

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add wiki/personas/README.md wiki/personas/vutr 2>/dev/null || git add wiki/personas/README.md
git commit -m "docs(persona-wiki): output-layer README + first bootstrap run"
```

---

## Self-Review

**1. Spec coverage:**
- Step 1 raw capture → `Source` model + `pipeline.update` input (Task 11). ✓
- Step 2 derivative writer → `llm.build_derive_prompt` + `derive.apply_bundle` (7, 8). ✓
- Step 2a bootstrap → `bootstrap.py` (Task 12). ✓
- Step 3 CDC → `topics.match_topics` (4) + `cdc.decide_topic` (9). ✓
- Step 4 index → `index.py` (Task 5). ✓
- Step 5 query entrypoint → `query.py` + CLI `query` (13, 14). ✓
- Step 6 PARA isolation → path guard in `storage.write_note` (3); only reads `Source`/persona snapshot; never touches authored course. ✓
- Step 7 QC → `qc.py` (10), gated in `pipeline` (11). ✓
- Atomic storage + dedup → `derive.apply_bundle` + shared-entity test (8). ✓
- CDC log 4-shape → `log.py` (6). ✓
- Error handling (QC-fail demote, LLM-fail no-partial, idempotent, missing-source skip) → `pipeline` tests (11). ✓ (Missing-source-file skip is covered at the source-loading boundary; the POC feeds `Source` objects directly, and a source with no matching topic is skipped — test in Task 11.)
- Testing seam / offline → LLM injected everywhere; no test calls real `claude`. ✓

**2. Placeholder scan:** No TBD/TODO; every code step has complete code. ✓

**3. Type consistency:** `DerivativeBundle.parse_raw_json`, `apply_bundle(root, persona, topic, bundle, sources, index, stamp)`, `qc_check(note, source, llm)`, `log_ingest(path, total, summary, stamp)`, `register_atomic(index, kind, slug, topic, stamp)` are used with identical signatures across Tasks 8/11/12. `Source(id, text)` consistent (11, 14). ✓

**Note on a spec deviation folded in:** `match_topics` is implemented locally (Task 4) rather than imported from `media_core`, which is not present in the learning-vault repo. Flagged in Global Constraints.
