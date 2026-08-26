# `sj` Udemy Persona Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a third persona, `sj` (Shrayansh Jain), to the `learning-vault-systemdesign`
hub — fed from 75 Udemy lecture transcripts, synthesized by the existing unchanged
pipeline, and deterministically cross-linked to the two personas already in that hub.

**Architecture:** Two new additive modules in `persona_wiki` — `udemy.py` (a transforming
feeder that routes each lecture into `raw/<group>/` via a checked-in `lecture_id → group`
map) and `crosslink.py` (an exact normalized-slug matcher that appends one
`**Also covered by:**` line per genuine match). Stage-A synthesis in between is the
existing `synthesize()`, called with **zero modifications** — same provenance gate, same
depth gate, same quarantine, same log. Nothing existing is edited except `cli.py`, which
gains two new subcommands.

**Tech Stack:** Python 3.11, Typer, Pydantic v2, PyYAML, pytest. No new dependencies.

**Spec:** [`docs/superpowers/specs/2026-08-23-sj-udemy-persona-design.md`](../specs/2026-08-23-sj-udemy-persona-design.md)

---

## Global Constraints

- **Three repos.** Code + tests: `learning-vault` (`$LV` below). Output: `learning-vault-systemdesign` (`$HUB`). This plan + the spec: `knowledge-toolkit` (this repo). Never write code into the hub; never write vault notes into `learning-vault`.
- **Never modify** `ingest.py`, `synthesize.py`, `qc.py`, `log.py`, `index.py`, `storage.py`, `models.py`. `cli.py` is additive-only (new commands appended; existing commands untouched).
- **Never use `f"{kind}s"` for atomic dirs.** Use `persona_wiki.index.atomic_dir(kind)`. (`"entity" + "s" == "entitys"` — this bug shipped twice in this repo.)
- **Nested `claude -p` returns HTTP 401.** `default_llm` shells to the `claude` CLI and cannot authenticate inside a Claude Code session. Any real synthesis run from a session must use the Agent tool as the LLM transport — see Task 9.
- **Venv lives outside iCloud.** `$VENV` below. An editable install inside the iCloud tree flickers off `sys.path` when iCloud evicts files.
- **Tests are offline.** No network, no login, no `conftest.py`, no `tests/fixtures/` directory — this repo has neither and must not gain one. Fixture vaults are built inline with `tmp_path`. The LLM is a plain closure of type `Callable[[str], str]`.
- **Obsidian link format for every cross-persona link:** `[[wiki/personas/<persona>/topics/<slug>|<persona>]]` — vault-root-relative and fully path-qualified. Never `../`, never a bare `[[slug]]`.
- **The raw layer is immutable.** A feeder never overwrites an existing `raw/` file.
- **Stamp format** is `YYYY-MM-DD` (`date.today().isoformat()`), matching every other writer.

### Shell variables used throughout

```bash
export LV="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault"
export HUB="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault-systemdesign"
export UDEMY="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault/lectures/system-design-lld-hld-from-basics-to-advanced"
export VENV="$HOME/.venvs/learning-vault"
export PY="$VENV/bin/python"
export PW="$VENV/bin/persona-wiki"   # cli.py has no __main__ block; `python -m persona_wiki.cli` silently no-ops
```

> **zsh trap:** `"$LV[dev]"` is array-subscript syntax in zsh and silently produces an
> empty string. Always write `"${LV}[dev]"`.

---

## File Structure

| File | Repo | Responsibility |
|---|---|---|
| `src/persona_wiki/udemy.py` | `$LV` | **New.** Parse a Udemy lecture note; load the group map; transform + write into `raw/<group>/` idempotently. |
| `src/persona_wiki/crosslink.py` | `$LV` | **New.** Normalize topic slugs; find exact cross-persona matches; append `**Also covered by:**` lines. |
| `data/sj_lecture_groups.yaml` | `$LV` | **New.** The 75-lecture `lecture_id → group` routing table. Human-reviewable; ids are the key, titles are comments. |
| `src/persona_wiki/cli.py` | `$LV` | **Modify (append only).** Two new commands: `ingest-udemy`, `crosslink`. |
| `tests/persona_wiki/test_udemy.py` | `$LV` | **New.** 6 tests: parse, reject, route, idempotency, unmapped, real-map coverage. |
| `tests/persona_wiki/test_crosslink.py` | `$LV` | **New.** 6 tests: normalize, match, **no-match**, missing-target, idempotency, ordering. |
| `scripts/sj_synthesize.py` | `$LV` | **New.** Resumable prompt-cache driver so `synthesize()` can run with the Agent tool as LLM transport. |
| `scripts/sj_collision_report.py` | `$LV` | **New.** Lists `sj` slugs colliding with sibling personas. Report only — never renames. |
| `wiki/personas/sj/**` | `$HUB` | **Output.** Written by the tools above, committed in Tasks 8/9/10. |

---

## Task 0: Environment and branches

**Files:** none created — this task only prepares the two working trees.

**Interfaces:**
- Produces: a working `$PY` that can `import persona_wiki`, and a feature branch in each of `$LV` and `$HUB`.

- [ ] **Step 1: Create the venv outside iCloud and install the package**

```bash
python3.11 -m venv "$VENV"
"$VENV/bin/pip" -q install -e "${LV}[dev]"
"$PY" -c "import persona_wiki, de_toolkit.vault as v; print(v.slugify('Adapter Pattern (Structural Design Pattern)'))"
```

Expected output: `adapter-pattern-structural-design-pattern`

- [ ] **Step 2: Record the green baseline**

```bash
cd "$LV" && "$PY" -m pytest tests -q --no-header
```

Expected: `127 passed`. If the count differs, stop and reconcile before writing any code —
every later task compares against this number.

- [ ] **Step 3: Branch both repos**

```bash
cd "$LV" && git checkout -b claude/sj-udemy-persona
cd "$HUB" && git checkout -b claude/sj-udemy-persona
```

`$LV` is on `main` with pre-existing dirty `.obsidian/*` files. Leave them alone — they are
Obsidian's own runtime noise and are not ours to commit. Never `git add -A` in `$LV`; add
named paths only.

---

## Task 1: Parse a Udemy lecture note

**Files:**
- Create: `$LV/src/persona_wiki/udemy.py`
- Test: `$LV/tests/persona_wiki/test_udemy.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `parse_lecture(text: str) -> Tuple[dict, str]` — `(frontmatter dict, transcript body)`. Raises `ValueError` when the `## Transcript` heading is absent.
  - `TRANSCRIPT_HEADING = "## Transcript"`

**Background the implementer needs.** A source lecture note looks exactly like this
(verified against a real file; the frontmatter `topics`/`topic_links`/`tags` fields are junk
from the Udemy vault's own auto-tagger and are deliberately dropped):

```markdown
---
title: "Adapter Pattern (Structural Design Pattern)"
course: "System Design (LLD + HLD) from Basics to Advanced"
section: "LLD (Low Level Design)"
url: "https://www.udemy.com/course/draft/5776816/learn/lecture/41932990"
duration: "00:16:44"
captured_at: 2026-08-22T06:02:45.870634+00:00
topics: [Career, Education]
topic_links: ["[[topics/Career|Career]]", "[[topics/Education|Education]]"]
tags: [tooling, architecture, fundamentals]
---

# Adapter Pattern (Structural Design Pattern)

Part of [[courses/system-design-...|...]] → [[courses/.../1-lld-low-level-design|...]]

[Open on Udemy](https://www.udemy.com/course/draft/5776816/learn/lecture/41932990)

## Transcript

[00:00:00] Hey guys. Welcome to Concept and Coding. ...
```

The `Part of [[courses/...]]` and `[Open on Udemy]` lines link into a **different** Obsidian
vault and would be dangling in the hub, so everything before `## Transcript` is discarded
outright. Taking the body as "everything after the `## Transcript` heading line" drops them
for free — no separate line-stripping logic is needed, and none should be written.

- [ ] **Step 1: Write the failing tests**

Create `$LV/tests/persona_wiki/test_udemy.py`:

```python
import pytest

from persona_wiki.udemy import parse_lecture

LECTURE = '''---
title: "Adapter Pattern (Structural Design Pattern)"
course: "System Design (LLD + HLD) from Basics to Advanced"
section: "LLD (Low Level Design)"
url: "https://www.udemy.com/course/draft/5776816/learn/lecture/41932990"
duration: "00:16:44"
captured_at: 2026-08-22T06:02:45.870634+00:00
topics: [Career, Education]
tags: [tooling, architecture]
---

# Adapter Pattern (Structural Design Pattern)

Part of [[courses/system-design|System Design]] → [[courses/system-design/1-lld|LLD]]

[Open on Udemy](https://www.udemy.com/course/draft/5776816/learn/lecture/41932990)

## Transcript

[00:00:00] Hey guys. Welcome to Concept and Coding.

[00:01:00] Existing interface. And another is. Expected interface.
'''


def test_parse_lecture_extracts_frontmatter_and_transcript():
    fm, body = parse_lecture(LECTURE)
    assert fm["title"] == "Adapter Pattern (Structural Design Pattern)"
    assert fm["section"] == "LLD (Low Level Design)"
    assert fm["duration"] == "00:16:44"
    assert body.startswith("[00:00:00] Hey guys.")
    assert "[00:01:00] Existing interface." in body


def test_parse_lecture_drops_vault_local_link_lines():
    _, body = parse_lecture(LECTURE)
    assert "Part of [[courses" not in body
    assert "[Open on Udemy]" not in body
    assert "# Adapter Pattern" not in body


def test_parse_lecture_rejects_missing_transcript():
    no_transcript = LECTURE.split("## Transcript")[0]
    with pytest.raises(ValueError, match="Transcript"):
        parse_lecture(no_transcript)
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_udemy.py -q --no-header
```

Expected: collection error — `ModuleNotFoundError: No module named 'persona_wiki.udemy'`.

- [ ] **Step 3: Write the minimal implementation**

Create `$LV/src/persona_wiki/udemy.py`:

```python
"""Stage A feeder for Udemy lecture notes: transform a captured lecture into the
persona wiki's immutable raw/<group>/ layer, routed by a checked-in
lecture_id -> group map. Append-only, like ingest.py, but transforming rather
than copying (ingest.py is a byte-for-byte shutil.copyfile and has no seam for
this)."""

from __future__ import annotations

from typing import Dict, Tuple

import yaml

TRANSCRIPT_HEADING = "## Transcript"


def parse_lecture(text: str) -> Tuple[dict, str]:
    """(frontmatter dict, transcript body) for one captured Udemy lecture note.

    Everything before the ``## Transcript`` heading is discarded: it is the H1,
    a ``Part of [[courses/...]]`` breadcrumb and an ``[Open on Udemy]`` link,
    all of which point into a different Obsidian vault.
    """
    if not text.startswith("---"):
        raise ValueError("lecture note has no frontmatter")
    _, front, rest = text.split("---", 2)
    fm = yaml.safe_load(front) or {}
    if TRANSCRIPT_HEADING not in rest:
        raise ValueError(f"lecture note has no '{TRANSCRIPT_HEADING}' section")
    body = rest.split(TRANSCRIPT_HEADING, 1)[1]
    return fm, body.strip()
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_udemy.py -q --no-header
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
cd "$LV"
git add src/persona_wiki/udemy.py tests/persona_wiki/test_udemy.py
git commit -m "feat(udemy): parse a captured Udemy lecture note into frontmatter + transcript"
```

---

## Task 2: The lecture → group routing table

**Files:**
- Create: `$LV/data/sj_lecture_groups.yaml`
- Modify: `$LV/src/persona_wiki/udemy.py`
- Test: `$LV/tests/persona_wiki/test_udemy.py`

**Interfaces:**
- Consumes: `parse_lecture` (Task 1).
- Produces:
  - `load_group_map(path: Path) -> Dict[str, str]` — `lecture_id → group slug`, flattened from the YAML's nested `groups:` block. Raises `ValueError` on a duplicate id.
  - `lecture_id_from_filename(name: str) -> str` — the trailing numeric id, e.g. `"1-adapter-...-41932990.md" → "41932990"`. Raises `ValueError` if absent.

**Why `lecture_id` and not the filename or title.** The id is the only field that cannot
drift when the instructor retitles a lecture upstream. The destination filename is
*derived* (`slugify(title)`), so a retitle would otherwise silently produce a second copy
under a new name.

- [ ] **Step 1: Write the failing tests**

Append to `$LV/tests/persona_wiki/test_udemy.py`:

```python
import os
from pathlib import Path

from persona_wiki.udemy import lecture_id_from_filename, load_group_map

GROUP_MAP = Path(__file__).resolve().parents[2] / "data" / "sj_lecture_groups.yaml"
UDEMY_DIR = Path(
    os.path.expanduser(
        "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault/"
        "lectures/system-design-lld-hld-from-basics-to-advanced"
    )
)


def test_lecture_id_from_filename():
    assert lecture_id_from_filename(
        "1-adapter-pattern-structural-design-pattern-41932990.md") == "41932990"


def test_lecture_id_from_filename_rejects_unnumbered():
    with pytest.raises(ValueError):
        lecture_id_from_filename("notes.md")


def test_load_group_map_flattens_groups(tmp_path):
    f = tmp_path / "m.yaml"
    f.write_text(
        'course_dir: "x"\ngroups:\n'
        "  databases:\n    - 111   # SQL vs NoSQL\n    - 222\n"
        "  case-studies:\n    - 333\n",
        encoding="utf-8")
    assert load_group_map(f) == {"111": "databases", "222": "databases",
                                 "333": "case-studies"}


def test_load_group_map_rejects_duplicate_id(tmp_path):
    f = tmp_path / "m.yaml"
    f.write_text('groups:\n  a:\n    - 111\n  b:\n    - 111\n', encoding="utf-8")
    with pytest.raises(ValueError, match="111"):
        load_group_map(f)


@pytest.mark.skipif(not UDEMY_DIR.exists(), reason="Udemy Vault not present on this machine")
def test_group_map_covers_every_lecture_exactly_once():
    """The union of all group id-lists == the ids in the real course directory."""
    mapped = set(load_group_map(GROUP_MAP))
    on_disk = {lecture_id_from_filename(p.name) for p in UDEMY_DIR.glob("*.md")}
    assert mapped - on_disk == set(), f"map lists unknown ids: {mapped - on_disk}"
    assert on_disk - mapped == set(), f"lectures missing from map: {on_disk - mapped}"
    assert len(on_disk) == 75
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_udemy.py -q --no-header
```

Expected: `ImportError: cannot import name 'lecture_id_from_filename'`.

- [ ] **Step 3: Write the implementation**

Append to `$LV/src/persona_wiki/udemy.py` (and add `import re` / `from pathlib import Path`
to the existing import block):

```python
_LECTURE_ID_RE = re.compile(r"-(\d+)\.md$")


def lecture_id_from_filename(name: str) -> str:
    """The trailing numeric Udemy lecture id: '1-adapter-...-41932990.md' -> '41932990'."""
    m = _LECTURE_ID_RE.search(name)
    if not m:
        raise ValueError(f"no lecture id in filename: {name}")
    return m.group(1)


def load_group_map(path: Path) -> Dict[str, str]:
    """lecture_id -> group slug, flattened from the YAML's nested ``groups:`` block."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: Dict[str, str] = {}
    for group, ids in (data.get("groups") or {}).items():
        for lecture_id in ids or []:
            key = str(lecture_id)
            if key in out:
                raise ValueError(
                    f"lecture id {key} listed in both '{out[key]}' and '{group}'")
            out[key] = group
    return out
```

- [ ] **Step 4: Create the real routing table**

Create `$LV/data/sj_lecture_groups.yaml` with exactly this content:

```yaml
# sj (Shrayansh Jain) -- "System Design (LLD + HLD) from Basics to Advanced"
# lecture_id -> raw/<group>/ . Titles are comments only; the id is the key.
# Verified: 75 unique ids, no duplicates, no gaps against the course directory.
course_dir: "system-design-lld-hld-from-basics-to-advanced"
groups:
  lld-foundations:
    - 53198193   # What is LLD and Pattern Categories? Difference between Is-a & Has-a relationship
    - 51802699   # SOLID Principles
    - 41932786   # Liskov Substitution Principle (LSP) Solution
    - 46258341   # MVC Design Pattern
  creational-patterns:
    - 41932808   # Builder Design Pattern (Creational Design Pattern)
    - 51802741   # Factory & Abstract Factory pattern (Creational Design Pattern)
    - 44184292   # Object Pool Design Pattern (Creational Design Pattern)
  structural-patterns:
    - 41932990   # Adapter Pattern (Structural Design Pattern)
    - 41933000   # Bridge Design Pattern (Structural Design Pattern)
    - 41933006   # Composite Pattern (Structural Design Pattern)
    - 41933010   # Decorator Design Pattern (Structural Design Pattern)
    - 41933036   # Facade Design Pattern (Structural Design Pattern)
    - 41933022   # Flyweight Design Pattern (Structural Design Pattern)
    - 51802799   # Proxy Design Pattern (Structural Pattern)
  behavioral-patterns:
    - 41932908   # Chain Of Responsibility Design Pattern (Behavioral Design Pattern)
    - 41932852   # Command Design Pattern (Behavioral Design Pattern)
    - 41932936   # Interpreter Pattern (Behavioral Design Pattern)
    - 41932884   # Iterator Design Pattern (Behavioral Design Pattern)
    - 41932918   # Mediator Design Pattern (Behavioral Design Pattern)
    - 43255956   # Memento Design Pattern (Behavioral Design Pattern)
    - 51802807   # Null Object Design Pattern (Behavioral Pattern)
    - 51802719   # Observer Pattern (Behavioral Pattern)
    - 51838767   # State Design Pattern (Behavioral) |  Design Vending Machine
    - 51802707   # Strategy Design Pattern (Behavioral Pattern)
    - 41932892   # Template Method Design Pattern (Behavioral Design Pattern)
    - 46749155   # Visitor Design Pattern (Behavioral Design Pattern)
  lld-case-studies:
    - 51802749   # Design Parking Lot
    - 51802759   # Design Tic-Tac-Toe Game
    - 41933150   # LLD of Apply Coupons on Shopping Cart Products
    - 41933106   # LLD of ATM
    - 51837383   # LLD of BookMyShow | Design Movie Ticket Booking App
    - 51802777   # LLD of Car Rental System
    - 41933114   # LLD of Cricbuzz
    - 51802773   # LLD of Elevator System
    - 41933132   # LLD of Inventory Management System
    - 46749161   # LLD of Payment Gateway
    - 51802787   # LLD of Snake n Ladder Game
    - 41933088   # LLD of Splitwise
  databases:
    - 41910228   # SQL vs NoSQL
    - 51957799   # Database Indexing: B+ Tree, Data Page, Clustered and Non-Clustered Indexing
    - 41910224   # Design a Key-Value Store || Dynamo DB
    - 51958567   # Two Phase Locking (2PL)
    - 51958517   # Concurrency Control in Distributed System | Optimistic & Pessimistic Concurrency
  distributed-fundamentals:
    - 51935679   # CAP Theorem (English Dubbed) | Better with 1.25x playback speed
    - 52075453   # Consistent Hashing (English Dubbed) | Better with 1.25x playback speed
    - 51957563   # Handle Distributed Transactions | Two-Phase Commit (2PC), 3PC and SAGA Pattern
    - 49271235   # Dual Write Problem | Event Driven Microservices Patterns
  resilience-patterns:
    - 51935789   # Circuit Breaker Introduction
    - 51768899   # Bulkhead Pattern Introduction
    - 51863813   # Retry Pattern : Fault Tolerance in Distributed Microservices
    - 45999743   # Thundering Herd Problem | Why Ticket Booking App goes down during peak traffic?
    - 41910250   # Design High Availability System || Active Passive & Active Active Architecture
  networking-and-edge:
    - 41910262   # Load Balancer and Different Algorithms
    - 41910254   # Proxy vs Reverse Proxy
    - 47703509   # How DNS works? | System Design of Domain Name System
    - 51935665   # Network Protocols (English Dubbed) | Better with 1.25x playback speed
    - 46076321   # API GATEWAY and Microservices Architecture
  authentication-and-security:
    - 51959473   # JWT: JSON Web Token
    - 41910424   # OAuth 2.0 expalined
    - 51959447   # Symmetric & Asymmetric Encryption with Explanation of AES, Diffie-Hellman
    - 48988689   # Attacks with Demo | CSRF, XSS, CORS and SQL Injection
  architecture-styles:
    - 41910180   # Introduction: Microservices (English Dubbed) | Better with 1.25x playback speed
    - 41910134   # Microservices Patterns: SAGA Pattern, Strangler Pattern (English Dubbed)
    - 47703349   # In How many Microservices we should divide Monolithic System
    - 46154991   # Service Mesh and its Architecture in Microservices
    - 51215461   # Service Discovery Introduction
  messaging-and-streaming:
    - 41910252   # Distributed Messaging Queue | Design Messaging Queue like Kafka, RabbitMQ
  case-studies:
    - 41910236   # Whatsapp System Design
    - 41910210   # Design URL Shortening Service like TinyURL
    - 52052749   # Scale from ZERO to MILLION User (English Dub) | Better with 1.25x playback speed
    - 41910216   # Back-Of-The-Envelope Estimation for System Design Interview
  caching-and-rate-limiting:
    - 51956913   # Distributed Cache & Caching Strategies | Cache-Aside, Write-Through, Write-Back
    - 41910244   # Design Rate Limiter
    - 51526791   # Rate Limiter Algorithms
    - 41910248   # Design Idempotent POST API || Handle Duplicate Request by Idempotency Handler
```

- [ ] **Step 5: Run the tests to verify they pass**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_udemy.py -q --no-header
```

Expected: `8 passed`. The coverage test is the important one — it proves all 75 lectures
are routed, none twice, none forgotten.

- [ ] **Step 6: Commit**

```bash
cd "$LV"
git add data/sj_lecture_groups.yaml src/persona_wiki/udemy.py tests/persona_wiki/test_udemy.py
git commit -m "feat(udemy): lecture_id -> group routing table for the sj course (75 lectures, 14 groups)"
```

---

## Task 3: The transforming feeder

**Files:**
- Modify: `$LV/src/persona_wiki/udemy.py`
- Test: `$LV/tests/persona_wiki/test_udemy.py`

**Interfaces:**
- Consumes: `parse_lecture`, `load_group_map`, `lecture_id_from_filename` (Tasks 1-2); `IngestResult` and `MANIFEST` from `persona_wiki.ingest`; `slugify` from `persona_wiki.storage`.
- Produces:
  - `UdemyIngestResult` — dataclass subclassing `IngestResult`, adding `unmapped: List[str]`.
  - `ingest_udemy(course_dir: Path, root: Path, group_map: Dict[str, str], stamp: str) -> UdemyIngestResult`

**Design notes the implementer must not deviate from.**

- `IngestResult`'s three fields (`copied`, `skipped`, `manifest`) **all have defaults**, so
  subclassing and adding `unmapped: List[str] = field(default_factory=list)` is safe — no
  "non-default argument follows default argument" `TypeError`.
- `result.manifest` on the base class is a single `Path`. This feeder writes one manifest
  **per group**, so it is set to the `raw/` directory instead. Do not try to make it a list —
  the CLI prints `res.manifest` and nothing else consumes it.
- **Idempotency is two-pronged**: skip if the `lecture_id` already appears in that group's
  manifest, **or** if the destination file already exists. The id check is what survives an
  upstream retitle; the file check is what matches `ingest.py`'s existing behaviour.
- **Skipped entries are keyed by lecture id, not filename** (the filename may have changed
  upstream — reporting the stable id is more useful and avoids implying a file was written).
- An unmapped id is reported in `result.unmapped` and **nothing is written**. It never raises
  and never aborts the run.
- `instructor` is a constant on this feeder: the Udemy vault records it on the *course*
  note (`instructor: "Shrayansh Jain"`), not on each lecture, so it is passed as a module
  constant rather than read from the lecture frontmatter.

- [ ] **Step 1: Write the failing tests**

Append to `$LV/tests/persona_wiki/test_udemy.py`:

```python
import yaml

from persona_wiki.udemy import ingest_udemy


def make_course(tmp_path: Path) -> Path:
    """Two fixture lectures destined for two different groups."""
    d = tmp_path / "course"
    d.mkdir()
    (d / "1-adapter-pattern-41932990.md").write_text(LECTURE, encoding="utf-8")
    (d / "2-sql-vs-nosql-41910228.md").write_text(
        LECTURE.replace("Adapter Pattern (Structural Design Pattern)", "SQL vs NoSQL")
               .replace("LLD (Low Level Design)", "HLD(High Level Design)")
               .replace("41932990", "41910228"),
        encoding="utf-8")
    return d


MAP = {"41932990": "structural-patterns", "41910228": "databases"}


def test_ingest_udemy_routes_to_group_dir(tmp_path):
    course, root = make_course(tmp_path), tmp_path / "wiki"
    res = ingest_udemy(course, root, MAP, "2026-08-23")

    assert sorted(res.copied) == [
        "adapter-pattern-structural-design-pattern.md", "sql-vs-nosql.md"]
    assert res.unmapped == []

    note = root / "raw" / "structural-patterns" / "adapter-pattern-structural-design-pattern.md"
    assert note.exists()
    assert (root / "raw" / "databases" / "sql-vs-nosql.md").exists()

    text = note.read_text(encoding="utf-8")
    assert 'lecture_id: "41932990"' in text
    assert 'instructor: "Shrayansh Jain"' in text
    assert 'section: "LLD (Low Level Design)"' in text
    assert "[00:00:00] Hey guys." in text
    assert "Part of [[courses" not in text          # vault-local links gone
    assert "topics:" not in text                    # auto-tagger junk dropped


def test_ingest_udemy_writes_manifest_per_group(tmp_path):
    course, root = make_course(tmp_path), tmp_path / "wiki"
    ingest_udemy(course, root, MAP, "2026-08-23")
    m = yaml.safe_load(
        (root / "raw" / "databases" / "_manifest.yaml").read_text(encoding="utf-8"))
    entry = m["sql-vs-nosql.md"]
    assert entry["lecture_id"] == "41910228"
    assert entry["copied"] == "2026-08-23"
    assert entry["source"].endswith("2-sql-vs-nosql-41910228.md")


def test_ingest_udemy_is_idempotent(tmp_path):
    course, root = make_course(tmp_path), tmp_path / "wiki"
    ingest_udemy(course, root, MAP, "2026-08-23")
    # upstream mutates the source; re-run must NOT overwrite the ingested copy
    (course / "1-adapter-pattern-41932990.md").write_text(
        LECTURE.replace("Hey guys", "MUTATED"), encoding="utf-8")
    res = ingest_udemy(course, root, MAP, "2026-08-24")
    assert res.copied == []
    assert sorted(res.skipped) == ["41910228", "41932990"]
    kept = (root / "raw" / "structural-patterns"
            / "adapter-pattern-structural-design-pattern.md").read_text(encoding="utf-8")
    assert "MUTATED" not in kept


def test_ingest_udemy_reports_unmapped_lecture(tmp_path):
    course, root = make_course(tmp_path), tmp_path / "wiki"
    res = ingest_udemy(course, root, {"41932990": "structural-patterns"}, "2026-08-23")
    assert res.unmapped == ["41910228"]
    assert res.copied == ["adapter-pattern-structural-design-pattern.md"]
    assert not (root / "raw" / "databases").exists()
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_udemy.py -q --no-header
```

Expected: `ImportError: cannot import name 'ingest_udemy'`.

- [ ] **Step 3: Write the implementation**

Append to `$LV/src/persona_wiki/udemy.py`, extending the import block with
`from dataclasses import dataclass, field`, `from typing import List`,
`from .ingest import MANIFEST, IngestResult`, `from .storage import slugify`:

```python
INSTRUCTOR = "Shrayansh Jain"

_FM_ORDER = ("title", "instructor", "course", "section",
             "lecture_id", "url", "duration", "captured_at")


@dataclass
class UdemyIngestResult(IngestResult):
    """IngestResult plus the lecture ids the group map does not route."""
    unmapped: List[str] = field(default_factory=list)


def render_raw_note(fm: dict, body: str, lecture_id: str) -> str:
    """The raw/ note: provenance frontmatter + the transcript, nothing else."""
    kept = {
        "title": fm.get("title", ""),
        "instructor": INSTRUCTOR,
        "course": fm.get("course", ""),
        "section": fm.get("section", ""),
        "lecture_id": lecture_id,
        "url": fm.get("url", ""),
        "duration": fm.get("duration", ""),
        "captured_at": str(fm.get("captured_at", "")),
    }
    lines = [f'{k}: "{kept[k]}"' for k in _FM_ORDER if kept[k]]
    front = "\n".join(lines)
    return f"---\n{front}\n---\n\n# {kept['title']}\n\n{body}\n"


def ingest_udemy(course_dir: Path, root: Path, group_map: Dict[str, str],
                 stamp: str) -> UdemyIngestResult:
    """Transform every lecture in ``course_dir`` into ``root/raw/<group>/``.

    Idempotent: a lecture is skipped when its id is already in the group's
    manifest OR when the destination file exists. Never overwrites — the raw
    layer is immutable. An id absent from ``group_map`` is reported, not copied.
    """
    res = UdemyIngestResult(manifest=root / "raw")
    manifests: Dict[str, Dict[str, dict]] = {}

    def manifest_for(group: str) -> Dict[str, dict]:
        if group not in manifests:
            path = root / "raw" / group / MANIFEST
            manifests[group] = (
                yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                if path.exists() else {})
        return manifests[group]

    for src in sorted(course_dir.glob("*.md")):
        lecture_id = lecture_id_from_filename(src.name)
        group = group_map.get(lecture_id)
        if group is None:
            res.unmapped.append(lecture_id)
            continue

        manifest = manifest_for(group)
        if any(e.get("lecture_id") == lecture_id for e in manifest.values()):
            res.skipped.append(lecture_id)
            continue

        fm, body = parse_lecture(src.read_text(encoding="utf-8"))
        name = f"{slugify(fm.get('title', lecture_id))}.md"
        raw_dir = root / "raw" / group
        raw_dir.mkdir(parents=True, exist_ok=True)
        dst = raw_dir / name
        if dst.exists():
            res.skipped.append(lecture_id)
            continue

        dst.write_text(render_raw_note(fm, body, lecture_id), encoding="utf-8")
        manifest[name] = {"source": str(src), "copied": stamp,
                          "lecture_id": lecture_id}
        res.copied.append(name)

    for group, manifest in manifests.items():
        (root / "raw" / group).mkdir(parents=True, exist_ok=True)
        (root / "raw" / group / MANIFEST).write_text(
            yaml.safe_dump(manifest, sort_keys=True, allow_unicode=True),
            encoding="utf-8")
    return res
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_udemy.py -q --no-header
```

Expected: `12 passed`.

- [ ] **Step 5: Run the full suite — nothing existing may break**

```bash
cd "$LV" && "$PY" -m pytest tests -q --no-header
```

Expected: `139 passed` (127 baseline + 12).

- [ ] **Step 6: Commit**

```bash
cd "$LV"
git add src/persona_wiki/udemy.py tests/persona_wiki/test_udemy.py
git commit -m "feat(udemy): transforming feeder writes lectures into raw/<group>/, idempotent by lecture_id"
```

---

## Task 4: `ingest-udemy` CLI command

**Files:**
- Modify: `$LV/src/persona_wiki/cli.py` (append a new command — do not touch existing ones)
- Test: `$LV/tests/persona_wiki/test_cli.py` (append)

**Interfaces:**
- Consumes: `ingest_udemy`, `load_group_map` (Tasks 2-3).
- Produces: the `persona-wiki ingest-udemy` command. Typer converts the function name `ingest_udemy` into the CLI name `ingest-udemy` automatically.

- [ ] **Step 1: Write the failing test**

Append to `$LV/tests/persona_wiki/test_cli.py`:

```python
LECTURE_MIN = '''---
title: "SQL vs NoSQL"
course: "System Design (LLD + HLD) from Basics to Advanced"
section: "HLD(High Level Design)"
url: "https://www.udemy.com/course/x/learn/lecture/41910228"
duration: "00:20:00"
captured_at: 2026-08-22T06:02:45+00:00
---

# SQL vs NoSQL

## Transcript

[00:00:00] Let us compare SQL and NoSQL.
'''


def test_cli_ingest_udemy_routes_and_is_idempotent(tmp_path):
    course = tmp_path / "course"; course.mkdir()
    (course / "2-sql-vs-nosql-41910228.md").write_text(LECTURE_MIN, encoding="utf-8")
    gm = tmp_path / "groups.yaml"
    gm.write_text('groups:\n  databases:\n    - 41910228\n', encoding="utf-8")

    args = ["ingest-udemy", "--persona", "sj", "--course-dir", str(course),
            "--group-map", str(gm), "--vault-dir", str(tmp_path)]
    r = runner.invoke(app, args)
    assert r.exit_code == 0, r.output
    assert (tmp_path / "wiki/personas/sj/raw/databases/sql-vs-nosql.md").exists()
    assert "copied 1" in r.output

    r2 = runner.invoke(app, args)
    assert r2.exit_code == 0, r2.output
    assert "copied 0" in r2.output and "skipped 1" in r2.output


def test_cli_ingest_udemy_reports_unmapped(tmp_path):
    course = tmp_path / "course"; course.mkdir()
    (course / "2-sql-vs-nosql-41910228.md").write_text(LECTURE_MIN, encoding="utf-8")
    gm = tmp_path / "groups.yaml"
    gm.write_text('groups:\n  databases:\n    - 99999999\n', encoding="utf-8")
    r = runner.invoke(app, ["ingest-udemy", "--persona", "sj", "--course-dir", str(course),
                            "--group-map", str(gm), "--vault-dir", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert "unmapped 1" in r.output
    assert "41910228" in r.output
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_cli.py -q --no-header -k udemy
```

Expected: FAIL — `No such command 'ingest-udemy'` (exit code 2).

- [ ] **Step 3: Append the command to `cli.py`**

Add at the end of `$LV/src/persona_wiki/cli.py`:

```python
@app.command()
def ingest_udemy(
    persona: str = typer.Option("sj", "--persona"),
    course_dir: str = typer.Option(..., "--course-dir"),
    group_map: str = typer.Option(..., "--group-map"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
) -> None:
    """Copy Udemy lecture transcripts into the persona's raw/<group>/ layer."""
    from .udemy import ingest_udemy as run_ingest_udemy, load_group_map
    root = _root(vault_dir, persona)
    gm = load_group_map(Path(group_map).expanduser())
    res = run_ingest_udemy(Path(course_dir).expanduser(), root, gm,
                           date.today().isoformat())
    typer.echo(f"copied {len(res.copied)}, skipped {len(res.skipped)}, "
               f"unmapped {len(res.unmapped)} -> {res.manifest}")
    if res.unmapped:
        typer.echo(f"unmapped lecture ids: {', '.join(sorted(res.unmapped))}", err=True)
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_cli.py -q --no-header
```

Expected: all `test_cli.py` tests pass, including the two new ones.

- [ ] **Step 5: Commit**

```bash
cd "$LV"
git add src/persona_wiki/cli.py tests/persona_wiki/test_cli.py
git commit -m "feat(cli): add ingest-udemy command"
```

---

## Task 5: Slug normalization and match-finding

**Files:**
- Create: `$LV/src/persona_wiki/crosslink.py`
- Test: `$LV/tests/persona_wiki/test_crosslink.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `normalize(slug: str) -> FrozenSet[str]`
  - `find_matches(sj_topic: str, hub_root: Path, personas: Sequence[str]) -> List[Tuple[str, str]]` — `[(persona, their_topic_slug), ...]` in the order `personas` was given.

**The match rule is exact normalized-set equality. Nothing looser.** A "shared token" or
"subset" rule was considered and rejected: `structural-patterns` and `resilience-patterns`
both contain the token `pattern`, and `caching-and-rate-limiting` vs
`storage-tiering-and-caching` share `caching`. Any looser rule fabricates links between
unrelated topics. Do not add one later "to catch more matches" — a fabricated link is worse
than a missing one.

`find_matches` enumerates **real files on disk** (`topics/*.md` under each sibling persona).
It never constructs a path from a guess, so a match can never point at a file that does not
exist.

- [ ] **Step 1: Write the failing tests**

Create `$LV/tests/persona_wiki/test_crosslink.py`:

```python
from pathlib import Path

from persona_wiki.crosslink import find_matches, normalize


def make_hub(tmp_path: Path, topics_by_persona: dict) -> Path:
    """A miniature hub: wiki/personas/<persona>/topics/<slug>.md"""
    for persona, slugs in topics_by_persona.items():
        d = tmp_path / "wiki" / "personas" / persona / "topics"
        d.mkdir(parents=True, exist_ok=True)
        for slug in slugs:
            (d / f"{slug}.md").write_text("---\nkind: topic\n---\n\nbody\n",
                                          encoding="utf-8")
    return tmp_path


def test_normalize_expands_abbreviations_and_strips_noise():
    assert normalize("hld") == normalize("high-level-design")
    assert normalize("lld") == normalize("Low_Level_Design.md")
    assert normalize("resilience-patterns") == normalize("resilience-pattern")
    assert normalize("authentication-and-security") == frozenset(
        {"authentication", "security"})


def test_normalize_keeps_unrelated_topics_apart():
    assert normalize("structural-patterns") != normalize("resilience-patterns")
    assert normalize("caching-and-rate-limiting") != normalize("storage-tiering-and-caching")


def test_find_matches_returns_persona_and_their_slug(tmp_path):
    hub = make_hub(tmp_path, {
        "sj": ["databases"],
        "lucsystemdesign": ["databases", "api-architecture"],
        "sdcourse": ["bloom-filters"],
    })
    assert find_matches("databases", hub, ["lucsystemdesign", "sdcourse"]) == [
        ("lucsystemdesign", "databases")]


def test_find_matches_returns_nothing_when_no_match(tmp_path):
    hub = make_hub(tmp_path, {
        "sj": ["structural-patterns"],
        "lucsystemdesign": ["resilience-patterns"],
    })
    assert find_matches("structural-patterns", hub, ["lucsystemdesign"]) == []


def test_find_matches_is_deterministically_ordered(tmp_path):
    hub = make_hub(tmp_path, {
        "sj": ["databases"],
        "lucsystemdesign": ["databases"],
        "sdcourse": ["databases"],
    })
    assert find_matches("databases", hub, ["lucsystemdesign", "sdcourse"]) == [
        ("lucsystemdesign", "databases"), ("sdcourse", "databases")]


def test_find_matches_skips_absent_persona(tmp_path):
    hub = make_hub(tmp_path, {"sj": ["databases"]})
    assert find_matches("databases", hub, ["lucsystemdesign"]) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_crosslink.py -q --no-header
```

Expected: `ModuleNotFoundError: No module named 'persona_wiki.crosslink'`.

- [ ] **Step 3: Write the implementation**

Create `$LV/src/persona_wiki/crosslink.py`:

```python
"""Deterministic cross-persona topic backlinks inside one hub vault.

No LLM, no shared vocabulary file. Two topic slugs match only when their
normalized token sets are EQUAL; anything looser fabricates links between
unrelated topics ('structural-patterns' and 'resilience-patterns' both contain
'pattern'). Links are written vault-root-relative and fully path-qualified,
because the hub already has slug collisions across personas and Obsidian
resolves [[bare-slugs]] in one flat namespace.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import FrozenSet, List, Sequence, Tuple

WIKI_SUBDIR = "wiki/personas"

_STOP = {"and", "or", "the", "of", "in", "a", "an", "for"}
_EXPAND = {
    "hld": ("high", "level", "design"),
    "lld": ("low", "level", "design"),
    "db": ("database",),
    "oo": ("object", "oriented"),
    "auth": ("authentication",),
}
_SPLIT_RE = re.compile(r"[-_\s]+")


def normalize(slug: str) -> FrozenSet[str]:
    """Comparable token set for a topic slug: 'High-Level-Design.md' -> {high, level, design}."""
    stem = slug[:-3] if slug.endswith(".md") else slug
    tokens: List[str] = []
    for tok in _SPLIT_RE.split(stem.lower()):
        if not tok or tok in _STOP:
            continue
        expanded = _EXPAND.get(tok, (tok,))
        for t in expanded:
            tokens.append(t[:-1] if len(t) > 3 and t.endswith("s") else t)
    return frozenset(tokens)


def topic_slugs(hub_root: Path, persona: str) -> List[str]:
    """Real topics/*.md stems for one persona — never a guessed path."""
    d = hub_root / WIKI_SUBDIR / persona / "topics"
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.md"))


def find_matches(sj_topic: str, hub_root: Path,
                 personas: Sequence[str]) -> List[Tuple[str, str]]:
    """(persona, their_slug) for every sibling topic whose normalized set is equal."""
    target = normalize(sj_topic)
    out: List[Tuple[str, str]] = []
    for persona in personas:
        for slug in topic_slugs(hub_root, persona):
            if normalize(slug) == target:
                out.append((persona, slug))
    return out
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_crosslink.py -q --no-header
```

Expected: `6 passed`.

- [ ] **Step 5: Commit**

```bash
cd "$LV"
git add src/persona_wiki/crosslink.py tests/persona_wiki/test_crosslink.py
git commit -m "feat(crosslink): exact normalized-slug matching across personas in one hub"
```

---

## Task 6: Appending the backlink lines

**Files:**
- Modify: `$LV/src/persona_wiki/crosslink.py`
- Test: `$LV/tests/persona_wiki/test_crosslink.py`

**Interfaces:**
- Consumes: `find_matches`, `topic_slugs` (Task 5).
- Produces:
  - `backlink_line(persona: str, slug: str) -> str`
  - `apply_backlinks(hub_root: Path, persona: str, personas: Sequence[str]) -> Dict[str, List[str]]` — `{sj_topic_slug: [line, ...]}` for topics that gained lines. Topics with no match are absent from the mapping.

**Sequencing note that must not be lost.** `resolution_gate` (`qc.py:56`) resolves a
wikilink only against `<root>/{concepts,entities,topics}/<slug>.md` for a **single**
persona, so a path-qualified cross-persona link would look dangling to it. This never fires
because the gate runs *inside* `synthesize()` before the topic note is written, and this
pass appends afterwards. **Always run all synthesis first, then this.** Do not weaken the
gate to accommodate the link.

This pass does **not** call `log_ingest`: no note count changes, and `log_ingest` returns
`False` without writing when the total is unchanged (`log.py:31`).

- [ ] **Step 1: Write the failing tests**

Append to `$LV/tests/persona_wiki/test_crosslink.py`:

```python
from persona_wiki.crosslink import apply_backlinks, backlink_line

BODY = ("Related: [[a]]\n\n## Comparisons\nx\n\n## Open questions\n\n"
        "## Synthesis\nA paragraph.")


def seed_topic(hub: Path, persona: str, slug: str, body: str = BODY) -> Path:
    d = hub / "wiki" / "personas" / persona / "topics"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{slug}.md"
    p.write_text(f"---\npersona: {persona}\nkind: topic\n---\n\n{body}\n",
                 encoding="utf-8")
    return p


def test_backlink_line_is_path_qualified():
    assert backlink_line("lucsystemdesign", "databases") == (
        "**Also covered by:** "
        "[[wiki/personas/lucsystemdesign/topics/databases|lucsystemdesign]]")


def test_backlink_added_on_match(tmp_path):
    note = seed_topic(tmp_path, "sj", "databases")
    seed_topic(tmp_path, "lucsystemdesign", "databases")
    got = apply_backlinks(tmp_path, "sj", ["lucsystemdesign", "sdcourse"])
    assert got == {"databases": [backlink_line("lucsystemdesign", "databases")]}
    text = note.read_text(encoding="utf-8")
    assert text.rstrip().endswith(backlink_line("lucsystemdesign", "databases"))
    assert "## Synthesis\nA paragraph." in text      # existing body preserved


def test_no_backlink_when_no_match_leaves_file_untouched(tmp_path):
    note = seed_topic(tmp_path, "sj", "structural-patterns")
    seed_topic(tmp_path, "lucsystemdesign", "resilience-patterns")
    before = note.read_text(encoding="utf-8")
    assert apply_backlinks(tmp_path, "sj", ["lucsystemdesign"]) == {}
    assert note.read_text(encoding="utf-8") == before


def test_backlink_is_idempotent(tmp_path):
    note = seed_topic(tmp_path, "sj", "databases")
    seed_topic(tmp_path, "lucsystemdesign", "databases")
    apply_backlinks(tmp_path, "sj", ["lucsystemdesign"])
    first = note.read_text(encoding="utf-8")
    assert apply_backlinks(tmp_path, "sj", ["lucsystemdesign"]) == {}
    assert note.read_text(encoding="utf-8") == first


def test_backlink_lists_both_personas_in_order(tmp_path):
    note = seed_topic(tmp_path, "sj", "databases")
    seed_topic(tmp_path, "lucsystemdesign", "databases")
    seed_topic(tmp_path, "sdcourse", "databases")
    apply_backlinks(tmp_path, "sj", ["lucsystemdesign", "sdcourse"])
    lines = [ln for ln in note.read_text(encoding="utf-8").splitlines()
             if ln.startswith("**Also covered by:**")]
    assert lines == [backlink_line("lucsystemdesign", "databases"),
                     backlink_line("sdcourse", "databases")]
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_crosslink.py -q --no-header
```

Expected: `ImportError: cannot import name 'apply_backlinks'`.

- [ ] **Step 3: Write the implementation**

Append to `$LV/src/persona_wiki/crosslink.py` (extend imports with `from typing import Dict`):

```python
BACKLINK_PREFIX = "**Also covered by:**"


def backlink_line(persona: str, slug: str) -> str:
    """A vault-root-relative, path-qualified Obsidian link. Never '../', never bare."""
    return f"{BACKLINK_PREFIX} [[{WIKI_SUBDIR}/{persona}/topics/{slug}|{persona}]]"


def apply_backlinks(hub_root: Path, persona: str,
                    personas: Sequence[str]) -> Dict[str, List[str]]:
    """Append one backlink line per genuine match to each of ``persona``'s topic notes.

    Returns {topic_slug: [lines added]} for topics that changed; topics with no
    match, or whose lines are already present, are absent. Run this AFTER all
    synthesis — resolution_gate is single-persona-scoped and would flag a
    cross-persona link as dangling if it ran over this output.
    """
    added: Dict[str, List[str]] = {}
    topics_dir = hub_root / WIKI_SUBDIR / persona / "topics"
    for slug in topic_slugs(hub_root, persona):
        matches = find_matches(slug, hub_root, personas)
        if not matches:
            continue
        path = topics_dir / f"{slug}.md"
        text = path.read_text(encoding="utf-8")
        new = [backlink_line(p, s) for p, s in matches
               if backlink_line(p, s) not in text]
        if not new:
            continue
        path.write_text(text.rstrip("\n") + "\n\n" + "\n".join(new) + "\n",
                        encoding="utf-8")
        added[slug] = new
    return added
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_crosslink.py -q --no-header
```

Expected: `11 passed`.

- [ ] **Step 5: Run the full suite**

```bash
cd "$LV" && "$PY" -m pytest tests -q --no-header
```

Expected: `152 passed` (127 baseline + 12 udemy + 2 cli + 11 crosslink).

- [ ] **Step 6: Commit**

```bash
cd "$LV"
git add src/persona_wiki/crosslink.py tests/persona_wiki/test_crosslink.py
git commit -m "feat(crosslink): append path-qualified 'Also covered by' backlinks, idempotently"
```

---

## Task 7: `crosslink` CLI command

**Files:**
- Modify: `$LV/src/persona_wiki/cli.py` (append)
- Test: `$LV/tests/persona_wiki/test_cli.py` (append)

**Interfaces:**
- Consumes: `apply_backlinks` (Task 6).
- Produces: the `persona-wiki crosslink` command.

Note this command takes `--vault-dir` as the **hub root** and does *not* go through
`_root()`, because `apply_backlinks` needs to see sibling personas — it walks
`wiki/personas/` itself.

- [ ] **Step 1: Write the failing test**

Append to `$LV/tests/persona_wiki/test_cli.py`:

```python
def test_cli_crosslink_adds_line_for_match(tmp_path):
    for persona in ("sj", "lucsystemdesign"):
        d = tmp_path / "wiki" / "personas" / persona / "topics"
        d.mkdir(parents=True)
        (d / "databases.md").write_text("---\nkind: topic\n---\n\nbody\n",
                                        encoding="utf-8")
    r = runner.invoke(app, ["crosslink", "--persona", "sj",
                            "--against", "lucsystemdesign",
                            "--vault-dir", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert "databases" in r.output
    text = (tmp_path / "wiki/personas/sj/topics/databases.md").read_text(encoding="utf-8")
    assert "[[wiki/personas/lucsystemdesign/topics/databases|lucsystemdesign]]" in text


def test_cli_crosslink_reports_nothing_when_no_match(tmp_path):
    d = tmp_path / "wiki" / "personas" / "sj" / "topics"
    d.mkdir(parents=True)
    (d / "structural-patterns.md").write_text("---\nkind: topic\n---\n\nbody\n",
                                              encoding="utf-8")
    r = runner.invoke(app, ["crosslink", "--persona", "sj",
                            "--against", "lucsystemdesign",
                            "--vault-dir", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert "0 topic(s)" in r.output
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd "$LV" && "$PY" -m pytest tests/persona_wiki/test_cli.py -q --no-header -k crosslink
```

Expected: FAIL — `No such command 'crosslink'`.

- [ ] **Step 3: Append the command to `cli.py`**

```python
@app.command()
def crosslink(
    persona: str = typer.Option("sj", "--persona"),
    against: List[str] = typer.Option(["lucsystemdesign", "sdcourse"], "--against",
                                      help="sibling personas to match against; repeatable"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
) -> None:
    """Append 'Also covered by' backlinks to a persona's topic notes."""
    from .crosslink import apply_backlinks
    hub = resolve_vault_dir(vault_dir)
    added = apply_backlinks(hub, persona, list(against))
    typer.echo(f"{len(added)} topic(s) gained backlinks")
    for slug, lines in sorted(added.items()):
        typer.echo(f"  {slug}: {len(lines)} link(s)")
```

Also extend the existing `typing` import at the top of `cli.py` from
`from typing import Optional` to `from typing import List, Optional`.

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd "$LV" && "$PY" -m pytest tests -q --no-header
```

Expected: `154 passed`.

- [ ] **Step 5: Commit**

```bash
cd "$LV"
git add src/persona_wiki/cli.py tests/persona_wiki/test_cli.py
git commit -m "feat(cli): add crosslink command"
```

---

## Task 8: Run the real feeder + collision report

**Files:**
- Create: `$LV/scripts/sj_collision_report.py`
- Output: `$HUB/wiki/personas/sj/raw/**` (75 notes across 14 groups + 14 manifests)

**Interfaces:**
- Consumes: the `ingest-udemy` CLI (Task 4).
- Produces: the populated raw layer that Task 9 synthesizes from.

- [ ] **Step 1: Run the feeder against the real course**

```bash
cd "$LV" && "$PW" ingest-udemy \
  --persona sj \
  --course-dir "$UDEMY" \
  --group-map data/sj_lecture_groups.yaml \
  --vault-dir "$HUB"
```

Expected: `copied 75, skipped 0, unmapped 0 -> .../wiki/personas/sj/raw`

- [ ] **Step 2: Verify the raw layer**

```bash
find "$HUB/wiki/personas/sj/raw" -name '*.md' | wc -l          # expect 75
ls "$HUB/wiki/personas/sj/raw"                                  # expect 14 dirs
find "$HUB/wiki/personas/sj/raw" -name '_manifest.yaml' | wc -l # expect 14
head -12 "$HUB/wiki/personas/sj/raw/structural-patterns/adapter-pattern-structural-design-pattern.md"
```

The `head` must show only the eight provenance fields, then the H1, then a timestamped
transcript line. If you see `topics: [Career, Education]` or a `Part of [[courses/...]]`
line, Task 1/3 regressed — stop and fix.

- [ ] **Step 3: Prove idempotency on real data**

```bash
cd "$LV" && "$PW" ingest-udemy \
  --persona sj --course-dir "$UDEMY" \
  --group-map data/sj_lecture_groups.yaml --vault-dir "$HUB"
```

Expected: `copied 0, skipped 75, unmapped 0`.

- [ ] **Step 4: Write the collision report script**

Create `$LV/scripts/sj_collision_report.py`:

```python
"""Report slugs a persona shares with its hub siblings. REPORT ONLY — never renames.

Obsidian resolves [[bare-slugs]] in one flat namespace, so a shared slug is
ambiguous vault-wide. The hub already ships two such collisions (bloom-filters,
redis). Every link this project writes is path-qualified, so new links are
unambiguous; this script exists so pre-existing ambiguity is visible, not silent.
"""

import sys
from pathlib import Path

KINDS = ("topics", "concepts", "entities")


def slugs(hub: Path, persona: str):
    out = {}
    for kind in KINDS:
        for p in (hub / "wiki" / "personas" / persona / kind).glob("*.md"):
            out.setdefault(p.stem, []).append(f"{persona}/{kind}")
    return out


def main(hub: Path, persona: str, siblings):
    mine = slugs(hub, persona)
    theirs = {}
    for s in siblings:
        for slug, where in slugs(hub, s).items():
            theirs.setdefault(slug, []).extend(where)
    hits = sorted(set(mine) & set(theirs))
    print(f"{persona}: {len(mine)} slugs; collisions with {', '.join(siblings)}: {len(hits)}")
    for slug in hits:
        print(f"  {slug}: {' + '.join(mine[slug] + theirs[slug])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), sys.argv[2], sys.argv[3:]))
```

- [ ] **Step 5: Commit the script and the raw layer**

```bash
cd "$LV"
git add scripts/sj_collision_report.py
git commit -m "chore(sj): slug-collision report script (report only, never renames)"

cd "$HUB"
git add wiki/personas/sj/raw
git commit -m "feat(sj): raw layer — 75 Udemy lecture transcripts across 14 topic groups"
```

---

## Task 9: Stage-A synthesis (the unchanged pipeline, driven by Agent-tool LLM)

**Files:**
- Create: `$LV/scripts/sj_synthesize.py`
- Output: `$HUB/wiki/personas/sj/{concepts,topics,index.yaml,log.md}`

**Interfaces:**
- Consumes: `persona_wiki.synthesize.synthesize` — **imported and called unmodified**.
- Produces: concept + topic notes for all 14 groups.

**Why a driver script exists at all.** `default_llm` shells out to `claude -p`, which
returns HTTP 401 when invoked inside a Claude Code session (parent credentials are not
inherited). The LLM transport must therefore be the Agent tool. `synthesize()` takes a
`Callable[[str], str]` and calls it synchronously, which an agent dispatch cannot satisfy
directly — so the driver runs `synthesize()` repeatedly against a **prompt cache**:

- A cache hit returns the stored answer.
- A cache **miss records the prompt and returns `""`**.

Returning `""` rather than raising is deliberate and exploits `synthesize()`'s existing
error handling: a `""` answer makes `parse_json_any` raise `ValueError`, which the
per-concept loop catches into `res.skipped` and the depth gate catches as fail-open. One
warm-up pass therefore collects *every* prompt of a phase at once, giving **5 rounds per
topic** instead of one round per LLM call:

| Round | Prompts collected |
|---|---|
| 1 | the `CONCEPT-LIST` prompt |
| 2 | every `CONCEPT-NOTE` prompt |
| 3 | every `DEPTH-CHECK` prompt |
| 4 | the `TOPIC-NOTE` prompt |
| 5 | none — full cache hit, real notes written |

**Warm-up rounds must not touch the real vault.** Rounds 1-4 produce partial/empty notes
and would corrupt `index.yaml` and `log.md`. The driver therefore runs warm-up rounds in a
temp root whose `raw/` is a symlink to the real one, and only performs the final,
fully-cached run against `$HUB` once `pending` is empty.

- [ ] **Step 1: Write the driver script**

Create `$LV/scripts/sj_synthesize.py`:

```python
"""Resumable driver so synthesize() can run with the Agent tool as LLM transport.

Round-based: a cache miss records the prompt and returns "" (which synthesize()
already handles gracefully), so one pass collects a whole phase of prompts.
Answer each pending prompt by writing <hash>.answer.txt next to its
<hash>.prompt.txt, then re-run. When nothing is pending, the final run writes
the real notes.

  python scripts/sj_synthesize.py <hub> <cache_dir> <topic> [--final]
"""

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

from persona_wiki.synthesize import synthesize


class CacheLLM:
    def __init__(self, cache_dir: Path):
        self.dir = cache_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.pending = []

    def __call__(self, prompt: str) -> str:
        h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        answer = self.dir / f"{h}.answer.txt"
        if answer.exists():
            return answer.read_text(encoding="utf-8")
        (self.dir / f"{h}.prompt.txt").write_text(prompt, encoding="utf-8")
        self.pending.append(h)
        return ""


def main(hub: Path, cache_dir: Path, topic: str, final: bool) -> int:
    real_root = hub / "wiki" / "personas" / "sj"
    llm = CacheLLM(cache_dir / topic)

    if final:
        root = real_root
    else:                       # warm-up: never write into the real vault
        tmp = Path(tempfile.mkdtemp(prefix=f"sj-{topic}-"))
        (tmp / "raw").symlink_to(real_root / "raw")
        root = tmp

    try:
        res = synthesize(root, topic, llm, "2026-08-23")
    except Exception as exc:    # warm-up rounds legitimately blow up on empty answers
        if final:
            raise
        res = None
        print(f"[warm-up] {topic}: {type(exc).__name__}: {exc}")

    if llm.pending:
        print(f"PENDING {len(llm.pending)} prompt(s) in {llm.dir}")
        for h in llm.pending:
            print(f"  {h}")
        return 1

    if res is not None:
        print(f"{topic}: written={len(res.written)} skipped={len(res.skipped)} "
              f"quarantined={len(res.quarantined)} "
              f"gaps={sum(len(v) for v in res.source_gaps.values())}")
    if not final:
        shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--final"]
    sys.exit(main(Path(args[0]), Path(args[1]), args[2], "--final" in sys.argv))
```

- [ ] **Step 2: Smoke-test the driver on the smallest group**

`messaging-and-streaming` has exactly one lecture — the cheapest possible end-to-end check.

```bash
cd "$LV" && "$PY" scripts/sj_synthesize.py "$HUB" /tmp/sj-cache messaging-and-streaming
```

Expected: exit code 1 and `PENDING 1 prompt(s)` — the `CONCEPT-LIST` prompt.

- [ ] **Step 3: Answer the pending prompts with Agent-tool dispatch**

For each `<hash>.prompt.txt` listed as pending, dispatch one subagent whose entire task is:
read that file, follow its instructions exactly, and write **only** the requested JSON to
`<hash>.answer.txt` in the same directory — no prose, no fence, no commentary. Dispatch all
of a round's pending prompts in parallel (one message, multiple `Agent` calls).

The prompts already carry their own strict contracts (`CONCEPT-LIST`, `CONCEPT-NOTE`,
`DEPTH-CHECK`, `TOPIC-NOTE`) built by the unchanged `synthesize.py`. Do not paraphrase,
summarize, or "improve" them, and do not let an agent invent content the transcript does not
support — the provenance gate will quarantine a concept whose cited source is not in `raw/`,
and that quarantine is a real signal, not a nuisance to work around.

- [ ] **Step 4: Re-run and repeat until nothing is pending**

```bash
cd "$LV" && "$PY" scripts/sj_synthesize.py "$HUB" /tmp/sj-cache messaging-and-streaming
```

Repeat Steps 3-4 (expect ~4 rounds). When it prints no `PENDING` line, run the final pass:

```bash
cd "$LV" && "$PY" scripts/sj_synthesize.py "$HUB" /tmp/sj-cache messaging-and-streaming --final
```

Expected: `messaging-and-streaming: written=N skipped=0 quarantined=0 gaps=...`

- [ ] **Step 5: Inspect the first real output before scaling up**

```bash
cat "$HUB/wiki/personas/sj/topics/messaging-and-streaming.md"
ls "$HUB/wiki/personas/sj/concepts/"
cat "$HUB/wiki/personas/sj/log.md"
```

Check by eye: every concept note's `sources:` cites a real
`raw/messaging-and-streaming/*.md` file; the topic note has `Related:` /
`## Comparisons` / `## Open questions` / `## Synthesis`; `log.md`'s first line is worded as
a **backfill** with `(log started here)`. If any concept landed in `_failed/`, read its
`qc_reason` before continuing — a systematic gate failure here will repeat 13 more times.

- [ ] **Step 6: Run the remaining 13 groups**

```
lld-foundations  creational-patterns  structural-patterns  behavioral-patterns
lld-case-studies  databases  distributed-fundamentals  resilience-patterns
networking-and-edge  authentication-and-security  architecture-styles
case-studies  caching-and-rate-limiting
```

Same loop per group. Run groups sequentially, not in parallel: `index.yaml` and `log.md` are
read-modify-write per group and concurrent runs would clobber each other.

- [ ] **Step 7: Verify the whole persona**

```bash
"$PY" - <<'EOF'
import os, yaml
from pathlib import Path
root = Path(os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault-systemdesign/wiki/personas/sj"))
idx = yaml.safe_load((root / "index.yaml").read_text())
print("topics:", len(idx["topics"]), "concepts:", len(idx["concepts"]))
missing = [t for t in [d.name for d in (root/"raw").iterdir() if d.is_dir()] if t not in idx["topics"]]
print("groups with no topic note:", missing)
print("quarantined:", [p.name for p in (root/"_failed").glob("*.md")] if (root/"_failed").exists() else [])
EOF
```

Expected: `topics: 14`, `groups with no topic note: []`.

- [ ] **Step 8: Run the collision report**

```bash
cd "$LV" && "$PY" scripts/sj_collision_report.py "$HUB" sj lucsystemdesign sdcourse
```

Record the output verbatim in the final summary. Do **not** rename anything in response to
it — renaming breaks the Task 5 matcher and diverges from the hub's existing convention.

- [ ] **Step 9: Commit**

```bash
cd "$LV"
git add scripts/sj_synthesize.py
git commit -m "chore(sj): resumable prompt-cache driver for Agent-tool synthesis"

cd "$HUB"
git add wiki/personas/sj
git commit -m "feat(sj): synthesize 14 topic notes + concept notes from the Udemy raw layer"
```

---

## Task 10: Cross-persona backlinks on real data, and finish

**Files:**
- Modify: `$HUB/wiki/personas/sj/topics/*.md`

**Interfaces:**
- Consumes: the `crosslink` CLI (Task 7); requires Task 9 complete for all 14 topics.

- [ ] **Step 1: Dry-check what will match, before writing**

```bash
cd "$LV" && "$PY" - <<'EOF'
import os
from pathlib import Path
from persona_wiki.crosslink import find_matches, topic_slugs
hub = Path(os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault-systemdesign"))
for slug in topic_slugs(hub, "sj"):
    print(f"{slug:32} {find_matches(slug, hub, ['lucsystemdesign', 'sdcourse'])}")
EOF
```

Expected: exactly 8 topics match `lucsystemdesign` — `architecture-styles`, `case-studies`,
`databases`, `distributed-fundamentals`, `authentication-and-security`,
`messaging-and-streaming`, `networking-and-edge`, `resilience-patterns`. The 5 LLD groups
and `caching-and-rate-limiting` must show `[]`. **If any LLD group shows a match, the
normalizer is over-matching — stop and fix Task 5 rather than accepting the link.**

- [ ] **Step 2: Apply the backlinks**

```bash
cd "$LV" && "$PW" crosslink \
  --persona sj --against lucsystemdesign --against sdcourse --vault-dir "$HUB"
```

Expected: `8 topic(s) gained backlinks`.

- [ ] **Step 3: Verify idempotency and spot-check a note**

```bash
cd "$LV" && "$PW" crosslink \
  --persona sj --against lucsystemdesign --against sdcourse --vault-dir "$HUB"
tail -3 "$HUB/wiki/personas/sj/topics/databases.md"
tail -3 "$HUB/wiki/personas/sj/topics/structural-patterns.md"
```

Expected: second run reports `0 topic(s) gained backlinks`; `databases.md` ends with the
path-qualified `**Also covered by:**` line; `structural-patterns.md` has **no** such line.

- [ ] **Step 4: Confirm no link is dangling**

```bash
cd "$LV" && "$PY" - <<'EOF'
import os, re
from pathlib import Path
hub = Path(os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault-systemdesign"))
bad = []
for p in (hub / "wiki/personas/sj/topics").glob("*.md"):
    for target in re.findall(r"\[\[(wiki/personas/[^\]|#]+)", p.read_text()):
        if not (hub / f"{target}.md").exists():
            bad.append((p.name, target))
print("dangling cross-persona links:", bad)
EOF
```

Expected: `dangling cross-persona links: []`

- [ ] **Step 5: Final full-suite run**

```bash
cd "$LV" && "$PY" -m pytest tests -q --no-header
```

Expected: `154 passed`.

- [ ] **Step 6: Commit and report**

```bash
cd "$HUB"
git add wiki/personas/sj/topics
git commit -m "feat(sj): cross-persona backlinks to lucsystemdesign (8 of 14 topics)"
```

Then report to the user: tests passed, lectures ingested, topics/concepts written, anything
quarantined to `_failed/` with its `qc_reason`, the collision-report output from Task 9
Step 8, and the 8 topics that gained backlinks. State plainly if any group under-produced.

---

## Self-Review

**Spec coverage.** Spec §0.1 (three repos) → Task 0 + Global Constraints. §0.2 (link
format) → Tasks 5-7, verified in Task 10 Step 4. §0.3 + §2 (14 groups) → Task 2, verified by
`test_group_map_covers_every_lecture_exactly_once` and Task 8 Step 1. §3 (feeder: new
module, raw shape, idempotency, CLI) → Tasks 1, 3, 4. §4 (normalization, exact-equality
rule, existence guard, placement, idempotency, gate sequencing) → Tasks 5, 6, 10. §5
(collision report) → Task 8 Step 4, run in Task 9 Step 8. §6 (all 12 tests; the 4-shape log
question) → Tasks 1-7; no new log tests, as the spec concluded. §7 (out of scope) → nothing
in this plan touches the frozen modules.

**Placeholder scan.** Every code step carries complete runnable code. The one place the
plan cannot inline content is Task 9 Step 3, where prompt text is generated at run time by
the unchanged `synthesize.py` — the step specifies exactly what the agent receives, what it
must write, and where, which is the actionable form of that instruction.

**Type consistency.** `UdemyIngestResult` fields (`copied`/`skipped`/`unmapped`/`manifest`)
are used identically in Tasks 3, 4, 8. `find_matches` returns `List[Tuple[str, str]]` in
Task 5 and is consumed as `(persona, slug)` pairs in Task 6 and Task 10 Step 1.
`backlink_line(persona, slug)` has one signature across Tasks 6, 7, 10. `apply_backlinks`
returns `Dict[str, List[str]]` in Task 6 and is consumed as such in Task 7. `load_group_map`
returns `Dict[str, str]` in Task 2 and is passed as `group_map` in Tasks 3-4.
