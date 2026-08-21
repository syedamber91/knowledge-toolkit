# Udemy Toolkit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture lecture transcripts from one purchased Udemy course at a time, using the user's own interactive browser session, and build a standalone "Udemy Vault" Obsidian vault from them.

**Architecture:** A new `src/udemy_toolkit/` package that mirrors `src/soic_toolkit/`: interactive Playwright login saves a session to `.auth/udemy_state.json`; a crawler reads the course curriculum and fetches each lecture's caption asset over that session; a pure-function extractor turns caption cues into timestamped prose; a vault builder writes one note per lecture with the mandatory index + append-only log + topic cross-links. Every network boundary goes through an injected callable seam so the whole test suite runs offline.

**Tech Stack:** Python 3.9+, Typer (CLI), Pydantic (models), Playwright (login + authenticated requests), Rich (console), pytest.

## Global Constraints

- **No video or audio is ever downloaded or decrypted.** Caption/transcript text only. Any code that fetches a media stream is a plan violation.
- **No stored passwords.** Login is manual in a real browser window; only `storage_state` is persisted, to `.auth/udemy_state.json`.
- **Never fabricate a transcript.** A lecture with no captions is recorded with `has_transcript=False` and an empty `transcript`.
- Captured content is never committed: `data/` and the vault directory are already in `.gitignore` — verify, do not re-add.
- Crawls are resumable and polite: save the catalog after **every** lecture; sleep a random 1.5–3.5s between network calls.
- Topic tagging uses the existing centralized vocabulary only — `from media_core.topics import match_topics`. Do not add an ad-hoc tagger.
- Python 3.9 compatible: use `from __future__ import annotations`, and `List[...]`/`Optional[...]` from `typing` in Pydantic model fields (matching `src/soic_toolkit/models.py`).
- Vault default: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault`, overridable with `UDEMY_VAULT_DIR`.
- Spec: `docs/superpowers/specs/2026-08-22-udemy-toolkit-design.md`.

## File Structure

| File | Responsibility |
|---|---|
| `src/udemy_toolkit/__init__.py` | Package marker + docstring. |
| `src/udemy_toolkit/config.py` | Env vars, paths, `Settings`, `ensure_dirs()`. |
| `src/udemy_toolkit/models.py` | Pydantic: `UdemyLecture`, `UdemySection`, `UdemyCourse`, `UdemyCatalog`. |
| `src/udemy_toolkit/extract.py` | Pure functions: caption text -> timestamped prose. No I/O. |
| `src/udemy_toolkit/curriculum.py` | Pure functions: course URL -> slug; curriculum JSON -> `UdemyCourse` tree. No I/O. |
| `src/udemy_toolkit/crawler.py` | Orchestration: walks lectures, calls an injected fetch seam, saves incrementally. |
| `src/udemy_toolkit/fetcher.py` | The only file that touches the network. Implements the seam using the saved Playwright session. |
| `src/udemy_toolkit/auth.py` | Interactive login + session validity check. |
| `src/udemy_toolkit/vault.py` | Catalog -> Obsidian notes, MOCs, `Home.md`, append-only `Log.md`, `topics/*.md`. |
| `src/udemy_toolkit/cli.py` | Typer app: `login`, `status`, `crawl`, `build-vault`. |
| `tests/test_udemy_extract.py` | Caption extraction tests. |
| `tests/test_udemy_curriculum.py` | Curriculum parsing tests. |
| `tests/test_udemy_crawler.py` | Resume / skip / incremental-save tests with a fake seam. |
| `tests/test_udemy_vault.py` | Note shape, MOCs, cross-links, and the 4 log tests. |
| `tests/fixtures/udemy/` | Sample caption + curriculum JSON fixtures. |

`curriculum.py` and `fetcher.py` are split out of the spec's single `crawler.py` so that parsing and network access each have one responsibility and the crawler stays offline-testable. Everything else matches the spec exactly.

---

### Task 1: Package scaffold, config, and CLI entry point

**Files:**
- Create: `src/udemy_toolkit/__init__.py`
- Create: `src/udemy_toolkit/config.py`
- Create: `tests/test_udemy_config.py`
- Modify: `pyproject.toml` (`[project.scripts]` block)
- Modify: `.env.example`

**Interfaces:**
- Consumes: nothing.
- Produces: `config.ROOT_DIR`, `config.AUTH_DIR`, `config.DATA_DIR`, `config.STATE_PATH` (`Path`), `config.CATALOG_PATH` (`Path`), `config.VAULT_DIR` (`Path`), `config.settings` (a frozen `Settings` dataclass with `base_url: str`, `crawl_min_delay: float`, `crawl_max_delay: float`, `crawl_headed: bool`), `config.ensure_dirs() -> None`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_udemy_config.py`:

```python
from pathlib import Path

from udemy_toolkit import config


def test_paths_are_under_repo_root():
    assert config.STATE_PATH == config.AUTH_DIR / "udemy_state.json"
    assert config.CATALOG_PATH == config.DATA_DIR / "udemy.json"
    assert config.AUTH_DIR.name == ".auth"


def test_default_vault_is_the_icloud_udemy_vault(monkeypatch):
    monkeypatch.delenv("UDEMY_VAULT_DIR", raising=False)
    resolved = config.resolve_vault_dir()
    assert resolved.name == "Udemy Vault"
    assert "iCloud~md~obsidian" in str(resolved)


def test_vault_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("UDEMY_VAULT_DIR", str(tmp_path / "elsewhere"))
    assert config.resolve_vault_dir() == Path(tmp_path / "elsewhere")


def test_settings_defaults():
    assert config.settings.base_url == "https://www.udemy.com"
    assert config.settings.crawl_min_delay == 1.5
    assert config.settings.crawl_max_delay == 3.5
    assert config.settings.crawl_headed is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_udemy_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'udemy_toolkit'`

- [ ] **Step 3: Write minimal implementation**

Create `src/udemy_toolkit/__init__.py`:

```python
"""Personal capture toolkit for courses you have purchased on Udemy.

Captures lecture *transcript text only* — never video or audio, which are
DRM protected. Authentication is interactive; no password is ever stored.
"""

__all__ = ["config"]
```

Create `src/udemy_toolkit/config.py`:

```python
"""Configuration and filesystem paths.

Values come from a local ``.env`` file (see ``.env.example``) with sensible
defaults. Nothing here contains secrets — authentication is interactive and the
resulting session is stored separately under ``.auth/``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root is two levels up: src/udemy_toolkit/config.py -> repo root
ROOT_DIR = Path(__file__).resolve().parents[2]

AUTH_DIR = ROOT_DIR / ".auth"
DATA_DIR = ROOT_DIR / "data"

STATE_PATH = AUTH_DIR / "udemy_state.json"
CATALOG_PATH = DATA_DIR / "udemy.json"

DEFAULT_VAULT_DIR = (
    Path.home()
    / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault"
)


def resolve_vault_dir() -> Path:
    """Where the Obsidian notes are written; ``UDEMY_VAULT_DIR`` overrides."""
    raw = os.environ.get("UDEMY_VAULT_DIR")
    return Path(raw).expanduser() if raw else DEFAULT_VAULT_DIR


VAULT_DIR = resolve_vault_dir()


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _get_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str = os.environ.get("UDEMY_BASE_URL", "https://www.udemy.com")
    crawl_min_delay: float = _get_float("UDEMY_CRAWL_MIN_DELAY", 1.5)
    crawl_max_delay: float = _get_float("UDEMY_CRAWL_MAX_DELAY", 3.5)
    crawl_headed: bool = _get_bool("UDEMY_CRAWL_HEADED", False)


settings = Settings()


def ensure_dirs() -> None:
    """Create the local working directories if they don't already exist."""
    for d in (AUTH_DIR, DATA_DIR):
        d.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_udemy_config.py -v`
Expected: 4 passed

- [ ] **Step 5: Register the CLI entry point**

In `pyproject.toml`, add one line to the existing `[project.scripts]` block, after `instagram-toolkit`:

```toml
udemy-toolkit = "udemy_toolkit.cli:app"
```

Append to `.env.example`:

```
# --- Udemy toolkit ---
# Standalone Obsidian vault for captured Udemy lecture transcripts.
UDEMY_VAULT_DIR=/Users/you/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault
UDEMY_BASE_URL=https://www.udemy.com
UDEMY_CRAWL_MIN_DELAY=1.5
UDEMY_CRAWL_MAX_DELAY=3.5
UDEMY_CRAWL_HEADED=false
```

Note: the `udemy-toolkit` console script will not resolve until Task 7 creates `cli.py`. That is expected; `pip install -e .` is re-run at the end of Task 7.

- [ ] **Step 6: Verify the gitignore already covers the outputs**

Run: `git check-ignore -v data/udemy.json`
Expected: a line naming `.gitignore` and the `data/` pattern. If it prints nothing, stop and report — do not add new ignore rules without checking why.

- [ ] **Step 7: Commit**

```bash
git add src/udemy_toolkit/__init__.py src/udemy_toolkit/config.py tests/test_udemy_config.py pyproject.toml .env.example
git commit -m "feat(udemy): package scaffold, config paths, and CLI entry point"
```

---

### Task 2: Pydantic models

**Files:**
- Create: `src/udemy_toolkit/models.py`
- Create: `tests/test_udemy_models.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `UdemyLecture(id: str, title: str, url: str, duration_seconds: Optional[int], section_title: str, transcript: str = "", has_transcript: bool = False, captured_at: Optional[datetime] = None)`
  - `UdemySection(title: str, order: int, lectures: List[UdemyLecture])`
  - `UdemyCourse(id: str, title: str, url: str, instructor: str = "", sections: List[UdemySection])`
  - `UdemyCatalog(courses: List[UdemyCourse], seen_lecture_ids: List[str], generated_at: datetime)` with methods `known_ids() -> set[str]`, `upsert_course(course: UdemyCourse) -> None`, `total_lectures() -> int`, `load(path: Path) -> UdemyCatalog` (classmethod), `save(path: Path) -> None`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_udemy_models.py`:

```python
from udemy_toolkit.models import (
    UdemyCatalog,
    UdemyCourse,
    UdemyLecture,
    UdemySection,
)


def _course(course_id="1", lecture_ids=("10",)):
    lectures = [
        UdemyLecture(id=i, title=f"Lecture {i}", url=f"https://u/{i}", section_title="S1")
        for i in lecture_ids
    ]
    return UdemyCourse(
        id=course_id,
        title="Test Course",
        url="https://www.udemy.com/course/test/",
        sections=[UdemySection(title="S1", order=1, lectures=lectures)],
    )


def test_known_ids_includes_captured_and_skipped():
    catalog = UdemyCatalog(courses=[_course(lecture_ids=("10", "11"))], seen_lecture_ids=["99"])
    assert catalog.known_ids() == {"10", "11", "99"}


def test_upsert_course_replaces_by_id_not_appends():
    catalog = UdemyCatalog(courses=[_course(lecture_ids=("10",))])
    catalog.upsert_course(_course(lecture_ids=("10", "11")))
    assert len(catalog.courses) == 1
    assert catalog.total_lectures() == 2


def test_upsert_course_appends_a_different_course():
    catalog = UdemyCatalog(courses=[_course(course_id="1")])
    catalog.upsert_course(_course(course_id="2"))
    assert len(catalog.courses) == 2


def test_round_trips_through_disk(tmp_path):
    path = tmp_path / "udemy.json"
    UdemyCatalog(courses=[_course()], seen_lecture_ids=["55"]).save(path)
    loaded = UdemyCatalog.load(path)
    assert loaded.total_lectures() == 1
    assert loaded.seen_lecture_ids == ["55"]


def test_load_returns_empty_catalog_when_file_missing(tmp_path):
    loaded = UdemyCatalog.load(tmp_path / "nope.json")
    assert loaded.courses == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_udemy_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'udemy_toolkit.models'`

- [ ] **Step 3: Write minimal implementation**

Create `src/udemy_toolkit/models.py`:

```python
"""Pydantic models describing a captured Udemy course.

Only transcript text and openly-rendered metadata are stored — never media.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class UdemyLecture(BaseModel):
    id: str
    title: str
    url: str
    duration_seconds: Optional[int] = None
    section_title: str = ""
    # Cleaned, timestamped transcript text. Empty when no captions exist.
    transcript: str = ""
    # False means "we looked and there were no captions" — never "not checked".
    has_transcript: bool = False
    captured_at: Optional[datetime] = None


class UdemySection(BaseModel):
    title: str
    order: int = 0
    lectures: List[UdemyLecture] = Field(default_factory=list)


class UdemyCourse(BaseModel):
    id: str
    title: str
    url: str
    instructor: str = ""
    sections: List[UdemySection] = Field(default_factory=list)

    def lectures(self) -> List[UdemyLecture]:
        return [lec for section in self.sections for lec in section.lectures]


class UdemyCatalog(BaseModel):
    """Top-level container persisted to data/udemy.json."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    courses: List[UdemyCourse] = Field(default_factory=list)
    # Lectures we've already dealt with, including ones that had no captions,
    # so a resumed crawl doesn't retry them forever.
    seen_lecture_ids: List[str] = Field(default_factory=list)

    def known_ids(self) -> set:
        ids = set(self.seen_lecture_ids)
        for course in self.courses:
            for lecture in course.lectures():
                ids.add(lecture.id)
        return ids

    def total_lectures(self) -> int:
        return sum(len(course.lectures()) for course in self.courses)

    def upsert_course(self, course: UdemyCourse) -> None:
        for index, existing in enumerate(self.courses):
            if existing.id == course.id:
                self.courses[index] = course
                return
        self.courses.append(course)

    @classmethod
    def load(cls, path: Path) -> "UdemyCatalog":
        if not Path(path).exists():
            return cls()
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def save(self, path: Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(
            json.dumps(json.loads(self.model_dump_json()), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_udemy_models.py -v`
Expected: 5 passed

If `model_validate_json` / `model_dump_json` raise `AttributeError`, the repo is on Pydantic v1 — check with `python -c "import pydantic; print(pydantic.VERSION)"` and use `parse_raw` / `json()` instead. Check the other toolkits' models for which style they use and match it.

- [ ] **Step 5: Commit**

```bash
git add src/udemy_toolkit/models.py tests/test_udemy_models.py
git commit -m "feat(udemy): pydantic catalog models with resumable seen-id tracking"
```

---

### Task 3: Caption extraction

**Files:**
- Create: `src/udemy_toolkit/extract.py`
- Create: `tests/test_udemy_extract.py`
- Create: `tests/fixtures/udemy/sample_captions.vtt`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `parse_cues(raw: str) -> List[Tuple[int, str]]` — `(start_seconds, text)` pairs, in file order, with markup and cue settings stripped and blank cues dropped.
  - `format_seconds(total: int) -> str` — `"HH:MM:SS"`.
  - `captions_to_transcript(raw: str, paragraph_seconds: int = 60) -> str` — cues merged into paragraphs, each paragraph prefixed with `[HH:MM:SS] `, paragraphs separated by a blank line. Returns `""` for empty or cue-less input.

- [ ] **Step 1: Create the fixture**

Create `tests/fixtures/udemy/sample_captions.vtt`:

```
WEBVTT

1
00:00:01.000 --> 00:00:04.000
first line here

2
00:00:04.000 --> 00:00:08.000 align:start position:10%
<v Instructor>second line here</v>

3
00:00:08.000 --> 00:00:09.000


4
01:02:03.500 --> 01:02:06.000
much later line
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_udemy_extract.py`:

```python
from pathlib import Path

from udemy_toolkit.extract import (
    captions_to_transcript,
    format_seconds,
    parse_cues,
)

FIXTURE = Path(__file__).parent / "fixtures" / "udemy" / "sample_captions.vtt"


def test_format_seconds():
    assert format_seconds(0) == "00:00:00"
    assert format_seconds(3723) == "01:02:03"


def test_parse_cues_reads_starts_strips_markup_and_drops_blanks():
    cues = parse_cues(FIXTURE.read_text(encoding="utf-8"))
    assert cues == [
        (1, "first line here"),
        (4, "second line here"),
        (3723, "much later line"),
    ]


def test_parse_cues_on_empty_input():
    assert parse_cues("") == []
    assert parse_cues("WEBVTT\n\n") == []


def test_transcript_groups_cues_into_timestamped_paragraphs():
    text = captions_to_transcript(FIXTURE.read_text(encoding="utf-8"))
    paragraphs = text.split("\n\n")
    assert paragraphs[0] == "[00:00:00] first line here second line here"
    assert paragraphs[1] == "[01:02:00] much later line"


def test_transcript_of_captionless_input_is_empty_string():
    assert captions_to_transcript("") == ""
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_udemy_extract.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'udemy_toolkit.extract'`

- [ ] **Step 4: Write minimal implementation**

Create `src/udemy_toolkit/extract.py`:

```python
"""Caption text -> readable, timestamped transcript.

Pure functions over strings: no network, no filesystem, no browser. This is
the only place caption markup is interpreted, so it is also the only place
that needs to change when a caption format shifts.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# "00:00:04.000 --> 00:00:08.000 align:start position:10%"
_TIMING_RE = re.compile(
    r"^(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})[.,]\d{1,3}\s*-->\s*\d{2}:\d{2}:\d{2}"
)
# Inline caption markup such as <v Speaker> ... </v> or <i> ... </i>.
_TAG_RE = re.compile(r"<[^>]+>")


def format_seconds(total: int) -> str:
    """Seconds -> ``HH:MM:SS``."""
    hours, remainder = divmod(int(total), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def parse_cues(raw: str) -> List[Tuple[int, str]]:
    """Caption file text -> ``(start_seconds, text)`` pairs, blanks dropped."""
    cues: List[Tuple[int, str]] = []
    start: int = 0
    buffer: List[str] = []
    have_timing = False

    def flush() -> None:
        text = " ".join(part.strip() for part in buffer if part.strip()).strip()
        if text:
            cues.append((start, text))
        buffer.clear()

    for line in (raw or "").splitlines():
        stripped = line.strip()
        match = _TIMING_RE.match(stripped)
        if match:
            if have_timing:
                flush()
            start = (
                int(match.group("h")) * 3600
                + int(match.group("m")) * 60
                + int(match.group("s"))
            )
            have_timing = True
            continue
        if not have_timing:
            # Header ("WEBVTT"), metadata, or a cue index before any timing line.
            continue
        if not stripped:
            flush()
            have_timing = False
            continue
        buffer.append(_TAG_RE.sub("", stripped))

    if have_timing:
        flush()
    return cues


def captions_to_transcript(raw: str, paragraph_seconds: int = 60) -> str:
    """Merge cues into ``[HH:MM:SS]``-prefixed paragraphs, one per time bucket."""
    cues = parse_cues(raw)
    if not cues:
        return ""
    paragraphs: List[str] = []
    current_bucket = None
    words: List[str] = []
    for start, text in cues:
        bucket = start // paragraph_seconds
        if current_bucket is None:
            current_bucket = bucket
        elif bucket != current_bucket:
            paragraphs.append(
                f"[{format_seconds(current_bucket * paragraph_seconds)}] " + " ".join(words)
            )
            words = []
            current_bucket = bucket
        words.append(text)
    if words:
        paragraphs.append(
            f"[{format_seconds(current_bucket * paragraph_seconds)}] " + " ".join(words)
        )
    return "\n\n".join(paragraphs)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_udemy_extract.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add src/udemy_toolkit/extract.py tests/test_udemy_extract.py tests/fixtures/udemy/sample_captions.vtt
git commit -m "feat(udemy): caption cue parsing and timestamped transcript formatting"
```

---

### Task 4: Curriculum parsing

**Files:**
- Create: `src/udemy_toolkit/curriculum.py`
- Create: `tests/test_udemy_curriculum.py`
- Create: `tests/fixtures/udemy/sample_curriculum.json`

**Interfaces:**
- Consumes: `models.UdemyCourse`, `models.UdemySection`, `models.UdemyLecture`.
- Produces:
  - `course_slug(url: str) -> str` — pulls the slug out of a `/course/<slug>/...` URL; raises `ValueError` on a URL that is not a Udemy course URL.
  - `parse_curriculum(payload: dict, course_id: str, course_title: str, course_url: str, instructor: str = "") -> UdemyCourse` — turns Udemy's `subscriber-curriculum-items` response into the section/lecture tree. Non-lecture items (quizzes, practice tests, coding exercises) are dropped; a lecture appearing before any chapter goes into a section titled `"Introduction"` with `order=1`.

- [ ] **Step 1: Create the fixture**

Create `tests/fixtures/udemy/sample_curriculum.json`:

```json
{
  "results": [
    {"_class": "chapter", "id": 900, "title": "Getting Started", "object_index": 1},
    {"_class": "lecture", "id": 10, "title": "Welcome", "asset": {"asset_type": "Video", "time_estimation": 125}},
    {"_class": "quiz", "id": 77, "title": "Quiz 1"},
    {"_class": "lecture", "id": 11, "title": "Setup", "asset": {"asset_type": "Video", "time_estimation": 300}},
    {"_class": "chapter", "id": 901, "title": "Going Deeper", "object_index": 2},
    {"_class": "lecture", "id": 12, "title": "Internals", "asset": {"asset_type": "Video", "time_estimation": 640}}
  ]
}
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_udemy_curriculum.py`:

```python
import json
from pathlib import Path

import pytest

from udemy_toolkit.curriculum import course_slug, parse_curriculum

FIXTURE = Path(__file__).parent / "fixtures" / "udemy" / "sample_curriculum.json"


def _parse():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parse_curriculum(
        payload,
        course_id="123",
        course_title="Test Course",
        course_url="https://www.udemy.com/course/test/",
        instructor="Someone",
    )


def test_course_slug_from_various_urls():
    assert course_slug("https://www.udemy.com/course/test-course/") == "test-course"
    assert course_slug("https://www.udemy.com/course/test-course/learn/lecture/42") == "test-course"


def test_course_slug_rejects_a_non_course_url():
    with pytest.raises(ValueError):
        course_slug("https://www.udemy.com/home/my-courses/")


def test_sections_and_lectures_are_grouped_in_order():
    course = _parse()
    assert [s.title for s in course.sections] == ["Getting Started", "Going Deeper"]
    assert [s.order for s in course.sections] == [1, 2]
    assert [lec.title for lec in course.sections[0].lectures] == ["Welcome", "Setup"]


def test_non_lecture_items_are_dropped():
    course = _parse()
    assert all(lec.title != "Quiz 1" for lec in course.lectures())


def test_lecture_fields_are_populated():
    lecture = _parse().sections[0].lectures[0]
    assert lecture.id == "10"
    assert lecture.duration_seconds == 125
    assert lecture.section_title == "Getting Started"
    assert lecture.url == "https://www.udemy.com/course/test/learn/lecture/10"
    assert lecture.has_transcript is False
    assert lecture.transcript == ""


def test_lecture_before_any_chapter_lands_in_introduction():
    course = parse_curriculum(
        {"results": [{"_class": "lecture", "id": 5, "title": "Orphan", "asset": {}}]},
        course_id="123",
        course_title="T",
        course_url="https://www.udemy.com/course/test/",
    )
    assert course.sections[0].title == "Introduction"
    assert course.sections[0].order == 1
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_udemy_curriculum.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'udemy_toolkit.curriculum'`

- [ ] **Step 4: Write minimal implementation**

Create `src/udemy_toolkit/curriculum.py`:

```python
"""Course URL and curriculum-payload parsing.

Pure functions: given the JSON a curriculum request returned, build the
section/lecture tree. No network access lives here, which is what lets the
crawler be tested entirely offline.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .models import UdemyCourse, UdemyLecture, UdemySection

_SLUG_RE = re.compile(r"/course/(?P<slug>[^/?#]+)")


def course_slug(url: str) -> str:
    """Extract the course slug from any Udemy course URL."""
    match = _SLUG_RE.search(url or "")
    if not match:
        raise ValueError(
            f"Not a Udemy course URL: {url!r}. "
            "Expected something like https://www.udemy.com/course/<slug>/"
        )
    return match.group("slug")


def _lecture_url(course_url: str, lecture_id: str) -> str:
    return f"{course_url.rstrip('/')}/learn/lecture/{lecture_id}"


def parse_curriculum(
    payload: Dict[str, Any],
    course_id: str,
    course_title: str,
    course_url: str,
    instructor: str = "",
) -> UdemyCourse:
    """Curriculum response -> ``UdemyCourse``; non-lecture items are dropped."""
    sections: List[UdemySection] = []
    current: Optional[UdemySection] = None

    for item in (payload or {}).get("results", []) or []:
        kind = item.get("_class")
        if kind == "chapter":
            current = UdemySection(
                title=item.get("title") or "Untitled section",
                order=int(item.get("object_index") or len(sections) + 1),
            )
            sections.append(current)
            continue
        if kind != "lecture":
            # Quizzes, practice tests, and coding exercises are out of scope.
            continue
        if current is None:
            current = UdemySection(title="Introduction", order=1)
            sections.append(current)
        asset = item.get("asset") or {}
        duration = asset.get("time_estimation")
        lecture_id = str(item.get("id"))
        current.lectures.append(
            UdemyLecture(
                id=lecture_id,
                title=item.get("title") or f"Lecture {lecture_id}",
                url=_lecture_url(course_url, lecture_id),
                duration_seconds=int(duration) if duration is not None else None,
                section_title=current.title,
            )
        )

    return UdemyCourse(
        id=str(course_id),
        title=course_title,
        url=course_url,
        instructor=instructor,
        sections=sections,
    )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_udemy_curriculum.py -v`
Expected: 6 passed

- [ ] **Step 6: Commit**

```bash
git add src/udemy_toolkit/curriculum.py tests/test_udemy_curriculum.py tests/fixtures/udemy/sample_curriculum.json
git commit -m "feat(udemy): parse course URLs and curriculum payloads into a section tree"
```

---

### Task 5: Crawler with an injected fetch seam

**Files:**
- Create: `src/udemy_toolkit/crawler.py`
- Create: `tests/test_udemy_crawler.py`

**Interfaces:**
- Consumes: `models.UdemyCatalog`, `models.UdemyCourse`, `extract.captions_to_transcript`, `curriculum.parse_curriculum`, `config.CATALOG_PATH`, `config.settings`.
- Produces:
  - `class CourseFetcher(Protocol)` with two methods: `course_meta(course_url: str) -> dict` returning `{"id": str, "title": str, "instructor": str}`, and `captions(course_id: str, lecture_id: str) -> Optional[str]` returning raw caption text or `None` when the lecture has none.
  - `crawl_course(course_url: str, fetcher: CourseFetcher, catalog_path: Path = CATALOG_PATH, limit: Optional[int] = None, sleep: Callable[[float], None] = time.sleep) -> CrawlSummary`
  - `@dataclass CrawlSummary(course_title: str, captured: int, skipped_no_captions: int, already_seen: int)`
  - `class SessionExpired(RuntimeError)` — raised by fetchers; `crawl_course` lets it propagate after saving.

Note: `course_meta` must also return the raw curriculum payload under key `"curriculum"`, so one seam covers both calls. Exact returned dict: `{"id": str, "title": str, "instructor": str, "curriculum": dict}`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_udemy_crawler.py`:

```python
import json
from pathlib import Path

from udemy_toolkit.crawler import crawl_course
from udemy_toolkit.models import UdemyCatalog

COURSE_URL = "https://www.udemy.com/course/test/"

CURRICULUM = {
    "results": [
        {"_class": "chapter", "id": 900, "title": "S1", "object_index": 1},
        {"_class": "lecture", "id": 10, "title": "Welcome", "asset": {"time_estimation": 60}},
        {"_class": "lecture", "id": 11, "title": "No captions here", "asset": {}},
    ]
}

VTT = "WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\nhello there\n"


class FakeFetcher:
    def __init__(self, captions_by_id):
        self._captions = captions_by_id
        self.caption_calls = []

    def course_meta(self, course_url):
        return {"id": "123", "title": "Test Course", "instructor": "Someone", "curriculum": CURRICULUM}

    def captions(self, course_id, lecture_id):
        self.caption_calls.append(lecture_id)
        return self._captions.get(lecture_id)


def _noop_sleep(_seconds):
    return None


def test_captures_transcripts_and_marks_captionless_lectures(tmp_path):
    path = tmp_path / "udemy.json"
    fetcher = FakeFetcher({"10": VTT})

    summary = crawl_course(COURSE_URL, fetcher, catalog_path=path, sleep=_noop_sleep)

    assert summary.captured == 1
    assert summary.skipped_no_captions == 1
    catalog = UdemyCatalog.load(path)
    lectures = {lec.id: lec for lec in catalog.courses[0].lectures()}
    assert lectures["10"].has_transcript is True
    assert "hello there" in lectures["10"].transcript
    assert lectures["11"].has_transcript is False
    assert lectures["11"].transcript == ""


def test_resume_does_not_refetch_known_lectures(tmp_path):
    path = tmp_path / "udemy.json"
    first = FakeFetcher({"10": VTT})
    crawl_course(COURSE_URL, first, catalog_path=path, sleep=_noop_sleep)

    second = FakeFetcher({"10": VTT})
    summary = crawl_course(COURSE_URL, second, catalog_path=path, sleep=_noop_sleep)

    assert second.caption_calls == []
    assert summary.captured == 0
    assert summary.already_seen == 2


def test_captionless_lecture_is_recorded_as_seen(tmp_path):
    path = tmp_path / "udemy.json"
    crawl_course(COURSE_URL, FakeFetcher({}), catalog_path=path, sleep=_noop_sleep)
    assert "11" in UdemyCatalog.load(path).seen_lecture_ids


def test_limit_stops_after_n_lectures(tmp_path):
    path = tmp_path / "udemy.json"
    fetcher = FakeFetcher({"10": VTT, "11": VTT})
    crawl_course(COURSE_URL, fetcher, catalog_path=path, limit=1, sleep=_noop_sleep)
    assert fetcher.caption_calls == ["10"]


def test_catalog_is_saved_after_every_lecture(tmp_path):
    path = tmp_path / "udemy.json"
    totals = []

    def spy_sleep(_seconds):
        totals.append(UdemyCatalog.load(path).total_lectures())

    crawl_course(COURSE_URL, FakeFetcher({"10": VTT, "11": VTT}), catalog_path=path, sleep=spy_sleep)
    # Saved incrementally: the catalog on disk already had lecture 1 before
    # lecture 2 was fetched.
    assert totals[0] == 1


def test_sleep_delay_is_within_configured_bounds(tmp_path):
    delays = []
    crawl_course(
        COURSE_URL,
        FakeFetcher({"10": VTT}),
        catalog_path=tmp_path / "udemy.json",
        sleep=lambda s: delays.append(s),
    )
    assert delays and all(1.5 <= d <= 3.5 for d in delays)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_udemy_crawler.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'udemy_toolkit.crawler'`

- [ ] **Step 3: Write minimal implementation**

Create `src/udemy_toolkit/crawler.py`:

```python
"""Walk one course's lectures and capture their transcripts.

Resumable and polite by design: the catalog is saved after every single
lecture, already-handled lectures are skipped on a re-run, and a random delay
separates network calls. All network access arrives through the injected
``fetcher`` seam, so this module is fully testable offline.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from .config import CATALOG_PATH, settings
from .curriculum import parse_curriculum
from .extract import captions_to_transcript
from .models import UdemyCatalog


class SessionExpired(RuntimeError):
    """Raised when the saved Udemy session no longer authenticates."""


@dataclass
class CrawlSummary:
    course_title: str
    captured: int = 0
    skipped_no_captions: int = 0
    already_seen: int = 0


def crawl_course(
    course_url: str,
    fetcher,
    catalog_path: Path = CATALOG_PATH,
    limit: Optional[int] = None,
    sleep: Callable[[float], None] = time.sleep,
) -> CrawlSummary:
    """Capture transcripts for one course, resuming from any previous run."""
    catalog = UdemyCatalog.load(catalog_path)
    known = catalog.known_ids()

    meta = fetcher.course_meta(course_url)
    fresh = parse_curriculum(
        meta["curriculum"],
        course_id=meta["id"],
        course_title=meta["title"],
        course_url=course_url,
        instructor=meta.get("instructor", ""),
    )

    # Start from what we already have for this course so a resumed run keeps
    # previously captured transcripts instead of blanking them.
    existing = next((c for c in catalog.courses if c.id == fresh.id), None)
    previous = {lec.id: lec for lec in existing.lectures()} if existing else {}
    for section in fresh.sections:
        for index, lecture in enumerate(section.lectures):
            if lecture.id in previous:
                section.lectures[index] = previous[lecture.id]

    catalog.upsert_course(fresh)
    summary = CrawlSummary(course_title=fresh.title)
    processed = 0

    for section in fresh.sections:
        for lecture in section.lectures:
            if lecture.id in known:
                summary.already_seen += 1
                continue
            if limit is not None and processed >= limit:
                catalog.save(catalog_path)
                return summary

            raw = fetcher.captions(fresh.id, lecture.id)
            processed += 1
            if raw:
                lecture.transcript = captions_to_transcript(raw)
                lecture.has_transcript = bool(lecture.transcript)
            if lecture.has_transcript:
                summary.captured += 1
            else:
                # Looked, found nothing. Record it so a resume never retries.
                lecture.transcript = ""
                summary.skipped_no_captions += 1
                if lecture.id not in catalog.seen_lecture_ids:
                    catalog.seen_lecture_ids.append(lecture.id)
            lecture.captured_at = datetime.now(timezone.utc)

            catalog.save(catalog_path)
            sleep(random.uniform(settings.crawl_min_delay, settings.crawl_max_delay))

    catalog.save(catalog_path)
    return summary
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_udemy_crawler.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/udemy_toolkit/crawler.py tests/test_udemy_crawler.py
git commit -m "feat(udemy): resumable, polite course crawler over an injected fetch seam"
```

---

### Task 6: Vault builder (index + log + cross-links)

**Files:**
- Create: `src/udemy_toolkit/vault.py`
- Create: `tests/test_udemy_vault.py`

**Interfaces:**
- Consumes: `models.UdemyCatalog`, `config.resolve_vault_dir`, `media_core.topics.match_topics`.
- Produces:
  - `build_vault(catalog: UdemyCatalog, vault_dir: Optional[Path] = None) -> Path` — writes the whole vault and returns the target directory.
  - `slugify(text: str) -> str`
  - `note_filename(section_order: int, lecture_title: str) -> str` — `"<order>-<slug>.md"`.

Vault layout produced:

```
<vault>/Home.md
<vault>/Log.md
<vault>/courses/<course-slug>.md          # course MOC, links its sections
<vault>/courses/<course-slug>/<order>-<section-slug>.md   # section MOC
<vault>/lectures/<course-slug>/<order>-<lecture-slug>.md  # one note per lecture
<vault>/topics/<topic>.md
```

- [ ] **Step 1: Write the failing test**

Create `tests/test_udemy_vault.py`:

```python
from pathlib import Path

from udemy_toolkit.models import UdemyCatalog, UdemyCourse, UdemyLecture, UdemySection
from udemy_toolkit.vault import build_vault, note_filename, slugify


def _catalog(lecture_titles=("Welcome",), transcript="Talking about kafka and spark streaming."):
    lectures = [
        UdemyLecture(
            id=str(index),
            title=title,
            url=f"https://www.udemy.com/course/test/learn/lecture/{index}",
            duration_seconds=120,
            section_title="Getting Started",
            transcript=transcript,
            has_transcript=bool(transcript),
        )
        for index, title in enumerate(lecture_titles, start=1)
    ]
    return UdemyCatalog(
        courses=[
            UdemyCourse(
                id="123",
                title="Test Course",
                url="https://www.udemy.com/course/test/",
                instructor="Someone",
                sections=[UdemySection(title="Getting Started", order=1, lectures=lectures)],
            )
        ]
    )


def test_slugify_and_note_filename():
    assert slugify("Hello, World! Part 2") == "hello-world-part-2"
    assert note_filename(3, "Hello, World!") == "3-hello-world.md"


def test_writes_one_note_per_lecture_with_frontmatter(tmp_path):
    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    notes = sorted((tmp_path / "lectures" / "test-course").glob("*.md"))
    assert [n.name for n in notes] == ["1-setup.md", "1-welcome.md"]
    body = (tmp_path / "lectures" / "test-course" / "1-welcome.md").read_text(encoding="utf-8")
    assert body.startswith("---\n")
    assert 'title: "Welcome"' in body
    assert 'course: "Test Course"' in body
    assert "Talking about kafka" in body


def test_index_and_mocs_are_linked(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    home = (tmp_path / "Home.md").read_text(encoding="utf-8")
    assert "[[courses/test-course|Test Course]]" in home
    assert "[[Log|Ingestion Log]]" in home
    section_moc = (tmp_path / "courses" / "test-course" / "1-getting-started.md").read_text(encoding="utf-8")
    assert "[[lectures/test-course/1-welcome|Welcome]]" in section_moc


def test_topic_notes_cross_link_lectures(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    topic_notes = list((tmp_path / "topics").glob("*.md"))
    assert topic_notes, "expected at least one topic note from the transcript text"
    assert any("[[lectures/test-course/1-welcome|Welcome]]" in n.read_text(encoding="utf-8") for n in topic_notes)


# --- the four required Log.md tests ---

def test_log_first_entry_is_worded_as_a_backfill(tmp_path):
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    log = (tmp_path / "Log.md").read_text(encoding="utf-8")
    assert "2 item(s) already in vault (log started here)" in log
    assert "captured" not in log


def test_log_appends_on_growth(tmp_path):
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    lines = [l for l in (tmp_path / "Log.md").read_text(encoding="utf-8").splitlines() if l.startswith("- **")]
    assert len(lines) == 2
    assert "1 new item(s) captured" in lines[1]
    assert "(2 total" in lines[1]


def test_log_does_not_append_on_unchanged_rebuild(tmp_path):
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    lines = [l for l in (tmp_path / "Log.md").read_text(encoding="utf-8").splitlines() if l.startswith("- **")]
    assert len(lines) == 1


def test_log_records_removals(tmp_path):
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    lines = [l for l in (tmp_path / "Log.md").read_text(encoding="utf-8").splitlines() if l.startswith("- **")]
    assert "1 item(s) removed" in lines[1]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_udemy_vault.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'udemy_toolkit.vault'`

- [ ] **Step 3: Write minimal implementation**

Create `src/udemy_toolkit/vault.py`. The `_last_logged_total` / `_log_ingest` pair below is the contract copied from `src/media_core/unified_vault.py:323-361` — do not invent a variant.

```python
"""Catalog -> Obsidian notes for the standalone Udemy Vault.

Implements the repo's standing three-part routing pattern:
  1. Index      — Home.md plus per-course and per-section MOC notes.
  2. Log        — append-only Log.md recording when items arrived or left.
  3. Cross-links— shared topics/<topic>.md notes plus inline [[wikilinks]].
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from media_core.topics import match_topics

from .config import resolve_vault_dir
from .extract import format_seconds
from .models import UdemyCatalog

_LOG_TOTAL_RE = re.compile(r"\((\d+) total")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug or "untitled"


def note_filename(section_order: int, lecture_title: str) -> str:
    return f"{section_order}-{slugify(lecture_title)}.md"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _last_logged_total(log_path: Path) -> int:
    """Total item count recorded in the log's last entry, or 0 with no log yet."""
    if not log_path.exists():
        return 0
    for line in reversed(log_path.read_text(encoding="utf-8").splitlines()):
        m = _LOG_TOTAL_RE.search(line)
        if m:
            return int(m.group(1))
    return 0


def _log_ingest(target: Path, total: int, breakdown: str) -> None:
    """Append one line to Log.md recording the delta since the last build."""
    log_path = target / "Log.md"
    is_first_entry = not log_path.exists()
    delta = total - _last_logged_total(log_path)
    if delta == 0:
        return
    if is_first_entry:
        action = f"{total} item(s) already in vault (log started here)"
    else:
        action = f"{delta} new item(s) captured" if delta > 0 else f"{-delta} item(s) removed"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if is_first_entry:
        header = (
            "---\ntitle: \"Ingestion Log\"\ntags: [log]\n---\n\n"
            "# Ingestion Log\n\n"
            "A running history of what was added to (or removed from) this "
            "vault and when — append-only, never rewritten.\n\n"
        )
        _write(log_path, header)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"- **{stamp}** — {action} ({total} total: {breakdown})\n")


def _lecture_note(course, section, lecture, topics) -> str:
    duration = format_seconds(lecture.duration_seconds) if lecture.duration_seconds else ""
    topic_links = ", ".join(f'"[[topics/{t}|{t}]]"' for t in topics)
    frontmatter = [
        "---",
        f'title: "{lecture.title}"',
        f'course: "{course.title}"',
        f'section: "{section.title}"',
        f'url: "{lecture.url}"',
        f'duration: "{duration}"',
        f"captured_at: {lecture.captured_at.isoformat() if lecture.captured_at else ''}",
        f"topics: [{', '.join(topics)}]",
        f"topic_links: [{topic_links}]",
        "---",
        "",
    ]
    body = [
        f"# {lecture.title}",
        "",
        f"Part of [[courses/{slugify(course.title)}|{course.title}]] → "
        f"[[courses/{slugify(course.title)}/{section.order}-{slugify(section.title)}|{section.title}]]",
        "",
        f"[Open on Udemy]({lecture.url})",
        "",
        "## Transcript",
        "",
        lecture.transcript or "_No transcript available for this lecture._",
        "",
    ]
    return "\n".join(frontmatter + body)


def build_vault(catalog: UdemyCatalog, vault_dir: Optional[Path] = None) -> Path:
    """Write the whole Udemy Vault; returns the target directory."""
    target = Path(vault_dir).expanduser() if vault_dir else resolve_vault_dir()
    target.mkdir(parents=True, exist_ok=True)

    topic_index = defaultdict(list)  # topic -> [(note_link, title)]
    total = 0

    for course in catalog.courses:
        course_slug = slugify(course.title)
        section_links = []

        for section in course.sections:
            lecture_links = []
            for lecture in section.lectures:
                topics = match_topics(f"{lecture.title}\n{lecture.transcript}")
                filename = note_filename(section.order, lecture.title)
                note_link = f"lectures/{course_slug}/{filename[:-3]}"
                _write(
                    target / "lectures" / course_slug / filename,
                    _lecture_note(course, section, lecture, topics),
                )
                lecture_links.append(f"- [[{note_link}|{lecture.title}]]")
                for topic in topics:
                    topic_index[topic].append((note_link, lecture.title))
                total += 1

            section_file = f"{section.order}-{slugify(section.title)}.md"
            _write(
                target / "courses" / course_slug / section_file,
                "\n".join(
                    [
                        "---",
                        f'title: "{section.title}"',
                        "---",
                        "",
                        f"# {section.title}",
                        "",
                        f"Section of [[courses/{course_slug}|{course.title}]]",
                        "",
                        *lecture_links,
                        "",
                    ]
                ),
            )
            section_links.append(
                f"- [[courses/{course_slug}/{section_file[:-3]}|{section.title}]]"
            )

        _write(
            target / "courses" / f"{course_slug}.md",
            "\n".join(
                [
                    "---",
                    f'title: "{course.title}"',
                    f'instructor: "{course.instructor}"',
                    f'url: "{course.url}"',
                    "---",
                    "",
                    f"# {course.title}",
                    "",
                    f"[Open on Udemy]({course.url})",
                    "",
                    "## Sections",
                    "",
                    *section_links,
                    "",
                ]
            ),
        )

    for topic, entries in topic_index.items():
        lines = sorted({f"- [[{link}|{title}]]" for link, title in entries})
        _write(
            target / "topics" / f"{topic}.md",
            "\n".join(
                ["---", f'title: "{topic}"', "tags: [topic]", "---", "", f"# {topic}", "", *lines, ""]
            ),
        )

    course_lines = [
        f"- [[courses/{slugify(c.title)}|{c.title}]] — {len(c.lectures())} lecture(s)"
        for c in catalog.courses
    ]
    _write(
        target / "Home.md",
        "\n".join(
            [
                "---",
                'title: "Udemy Vault"',
                "---",
                "",
                "# Udemy Vault",
                "",
                "Lecture transcripts captured from courses on Udemy. Transcript text only "
                "— no video or audio is stored here.",
                "",
                "## Courses",
                "",
                *course_lines,
                "",
                "## Meta",
                "",
                "- [[Log|Ingestion Log]]",
                "",
            ]
        ),
    )

    _log_ingest(
        target,
        total,
        f"{len(catalog.courses)} course(s), {len(topic_index)} topic(s)",
    )
    return target
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_udemy_vault.py -v`
Expected: 9 passed

If `test_topic_notes_cross_link_lectures` fails, print `match_topics("Talking about kafka and spark streaming.")` and change the fixture transcript to text that the existing vocabulary actually matches — do **not** add new vocabulary to satisfy a test.

- [ ] **Step 5: Commit**

```bash
git add src/udemy_toolkit/vault.py tests/test_udemy_vault.py
git commit -m "feat(udemy): vault builder with Home index, append-only log, and topic cross-links"
```

---

### Task 7: Auth, live fetcher, CLI, and docs

**Files:**
- Create: `src/udemy_toolkit/auth.py`
- Create: `src/udemy_toolkit/fetcher.py`
- Create: `src/udemy_toolkit/cli.py`
- Create: `tests/test_udemy_cli.py`
- Modify: `CLAUDE.md` (the six-toolkits table and the CLI flow block)
- Modify: `README.md`

**Interfaces:**
- Consumes: everything from Tasks 1-6.
- Produces:
  - `auth.login() -> None`, `auth.has_saved_session() -> bool`, `auth.session_is_valid() -> bool`, `auth.authenticated_context(headed: bool = False)` (context manager yielding a Playwright `BrowserContext`).
  - `fetcher.PlaywrightFetcher(context)` implementing `course_meta` and `captions`, raising `crawler.SessionExpired` on an auth failure.
  - `cli.app` — Typer app with `login`, `status`, `crawl`, `build-vault`.

- [ ] **Step 1: Write `auth.py`**

This mirrors `src/soic_toolkit/auth.py` — read that file first and keep the same structure and wording.

```python
"""Interactive authentication and session persistence.

Login is deliberately *manual*: a real browser window opens, you sign in with
your own credentials (including any OTP/MFA), and only then is the session
saved to ``.auth/udemy_state.json`` for reuse. Your password is never read or
stored by this tool.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import BrowserContext, sync_playwright
from rich.console import Console

from .config import STATE_PATH, ensure_dirs, settings

console = Console()


def login() -> None:
    """Open a browser, let the user log in manually, then save the session."""
    ensure_dirs()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login_url = settings.base_url.rstrip("/")
        console.print(f"[bold]Opening[/bold] {login_url}")
        page.goto(login_url, wait_until="domcontentloaded")

        console.print(
            "\n[bold yellow]Log in to your Udemy account in the browser window.[/bold yellow]\n"
            "Complete any OTP/2FA step until you reach My Learning.\n"
        )
        input("Once you are fully logged in, return here and press Enter to save the session... ")

        context.storage_state(path=str(STATE_PATH))
        console.print(f"[green]Session saved to[/green] {STATE_PATH}")
        browser.close()


def has_saved_session() -> bool:
    return STATE_PATH.exists()


@contextmanager
def authenticated_context(headed: bool = False) -> Iterator[BrowserContext]:
    """Yield a browser context restored from the saved session."""
    if not has_saved_session():
        raise RuntimeError("No saved session. Run `udemy-toolkit login` first.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        context = browser.new_context(storage_state=str(STATE_PATH))
        try:
            yield context
        finally:
            browser.close()


def session_is_valid() -> bool:
    """Best-effort check that the saved session still resolves to a logged-in page."""
    if not has_saved_session():
        return False
    with authenticated_context(headed=False) as context:
        page = context.new_page()
        page.goto(
            f"{settings.base_url.rstrip('/')}/api-2.0/users/me/",
            wait_until="domcontentloaded",
        )
        return "anonymous" not in page.content().lower()
```

- [ ] **Step 2: Write `fetcher.py`**

The only file that touches the network. It issues Udemy's own JSON API calls from inside the authenticated browser context — the same requests the site makes for you — and never requests a media stream.

```python
"""The live implementation of the crawler's fetch seam.

This is the only module that performs network access. It asks for the course's
curriculum and for each lecture's *caption* asset. It never requests a video or
audio stream, and never touches DRM.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .config import settings
from .crawler import SessionExpired
from .curriculum import course_slug

_CURRICULUM_FIELDS = (
    "?page_size=1000"
    "&fields[lecture]=id,title,object_index,asset"
    "&fields[chapter]=id,title,object_index"
    "&fields[asset]=time_estimation,asset_type"
)
_CAPTION_FIELDS = "?fields[lecture]=asset&fields[asset]=captions&fields[caption]=url,locale_id,title"


class PlaywrightFetcher:
    """Implements ``course_meta`` and ``captions`` over an authenticated context."""

    def __init__(self, context):
        self._page = context.new_page()
        self._base = settings.base_url.rstrip("/")

    def _json(self, path: str) -> Dict[str, Any]:
        response = self._page.request.get(f"{self._base}{path}")
        if response.status in (401, 403):
            raise SessionExpired(
                "Udemy rejected the saved session. Run `udemy-toolkit login` again."
            )
        if not response.ok:
            raise RuntimeError(f"Udemy returned HTTP {response.status} for {path}")
        return response.json()

    def course_meta(self, course_url: str) -> Dict[str, Any]:
        slug = course_slug(course_url)
        found = self._json(
            f"/api-2.0/courses/?search={slug}&fields[course]=id,title,visible_instructors"
        )
        results = found.get("results") or []
        match = next((r for r in results if r.get("url", "").strip("/").endswith(slug)), None)
        if match is None and results:
            match = results[0]
        if match is None:
            raise RuntimeError(f"Could not resolve course from URL: {course_url}")
        course_id = str(match["id"])
        instructors = match.get("visible_instructors") or []
        curriculum = self._json(
            f"/api-2.0/courses/{course_id}/subscriber-curriculum-items/{_CURRICULUM_FIELDS}"
        )
        return {
            "id": course_id,
            "title": match.get("title") or slug,
            "instructor": ", ".join(i.get("title", "") for i in instructors),
            "curriculum": curriculum,
        }

    def captions(self, course_id: str, lecture_id: str) -> Optional[str]:
        payload = self._json(
            f"/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}/{_CAPTION_FIELDS}"
        )
        captions = ((payload or {}).get("asset") or {}).get("captions") or []
        if not captions:
            return None
        chosen = next(
            (c for c in captions if str(c.get("locale_id", "")).lower().startswith("en")),
            captions[0],
        )
        url = chosen.get("url")
        if not url:
            return None
        response = self._page.request.get(url)
        return response.text() if response.ok else None
```

Note for the implementer: these API paths are Udemy's current internal endpoints and may drift. Verify them against a real logged-in session on the first live run (Step 6). If a path 404s, open the course in a browser with DevTools' Network tab and read the actual request the page makes — then fix the constant here. This is the only file that should ever need that fix.

- [ ] **Step 3: Write `cli.py`**

```python
"""Command-line interface for the Udemy transcript toolkit.

Subcommands:
    login        Open a browser and save your authenticated session.
    status       Report whether a saved session exists and is still valid.
    crawl        Capture transcripts for one course, by URL.
    build-vault  Build the Obsidian Udemy Vault from the catalog.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from . import auth as auth_mod
from . import crawler as crawler_mod
from . import vault as vault_mod
from .config import CATALOG_PATH, STATE_PATH, resolve_vault_dir, settings
from .models import UdemyCatalog

app = typer.Typer(
    help="Capture transcripts from courses you have purchased on Udemy.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def login() -> None:
    """Open a browser, log in manually, and save the session."""
    auth_mod.login()


@app.command()
def status() -> None:
    """Show whether a saved session exists and appears valid."""
    if not auth_mod.has_saved_session():
        console.print("[yellow]No saved session.[/yellow] Run `udemy-toolkit login`.")
        raise typer.Exit(code=1)
    console.print(f"Saved session: {STATE_PATH}")
    if auth_mod.session_is_valid():
        console.print("[green]Session looks valid.[/green]")
    else:
        console.print("[yellow]Session appears expired.[/yellow] Run `udemy-toolkit login` again.")
        raise typer.Exit(code=1)


@app.command()
def crawl(
    course_url: str = typer.Argument(..., help="Full URL of a course you own."),
    limit: Optional[int] = typer.Option(None, help="Stop after N lectures. Use a small value first."),
) -> None:
    """Capture lecture transcripts for one course."""
    from .fetcher import PlaywrightFetcher

    try:
        with auth_mod.authenticated_context(headed=settings.crawl_headed) as context:
            summary = crawler_mod.crawl_course(
                course_url, PlaywrightFetcher(context), limit=limit
            )
    except crawler_mod.SessionExpired as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    console.print(
        f"[green]{summary.course_title}[/green]: {summary.captured} captured, "
        f"{summary.skipped_no_captions} without captions, {summary.already_seen} already known."
    )
    console.print(f"Catalog: {CATALOG_PATH}")


@app.command("build-vault")
def build_vault() -> None:
    """Build the Obsidian Udemy Vault from the captured catalog."""
    catalog = UdemyCatalog.load(CATALOG_PATH)
    if not catalog.courses:
        console.print("[yellow]Nothing captured yet.[/yellow] Run `udemy-toolkit crawl <url>` first.")
        raise typer.Exit(code=1)
    target = vault_mod.build_vault(catalog, vault_dir=resolve_vault_dir())
    console.print(f"[green]Vault built:[/green] {target} ({catalog.total_lectures()} lecture note(s))")
```

- [ ] **Step 4: Write the CLI test**

Create `tests/test_udemy_cli.py`:

```python
from typer.testing import CliRunner

from udemy_toolkit.cli import app

runner = CliRunner()


def test_help_lists_every_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("login", "status", "crawl", "build-vault"):
        assert command in result.stdout


def test_build_vault_exits_nonzero_with_an_empty_catalog(tmp_path, monkeypatch):
    monkeypatch.setattr("udemy_toolkit.cli.CATALOG_PATH", tmp_path / "empty.json")
    result = runner.invoke(app, ["build-vault"])
    assert result.exit_code == 1
    assert "Nothing captured yet" in result.stdout
```

- [ ] **Step 5: Run the whole suite**

Run: `pip install -e ".[dev]" && pytest tests -q -k udemy`
Expected: all udemy tests pass (32 total across Tasks 1-7).

Then run the full suite to confirm nothing else broke:
Run: `pytest -q`
Expected: same pass/fail counts as before this branch. If a pre-existing failure appears, note it and do not "fix" unrelated code.

- [ ] **Step 6: Live smoke test (needs the user)**

```bash
udemy-toolkit login
udemy-toolkit status
udemy-toolkit crawl "<a course URL you own>" --limit 3
udemy-toolkit build-vault
```

Verify by hand: `data/udemy.json` has 3 lectures; the vault has `Home.md`, `Log.md`, one note per lecture, and at least one `topics/*.md`. Confirm the log's first line uses the **backfill** wording. If any API path 404s, fix only `fetcher.py` (see the note in Step 2).

Per the design decision, run this bulk fetch step by dispatching a **Sonnet** subagent — the work is mechanical.

- [ ] **Step 7: Update the docs**

In `CLAUDE.md`:
- Add a row to the toolkits table: `| `udemy_toolkit/` | Udemy lecture transcripts (transcript text only — never video) | Interactive Playwright login → `.auth/udemy_state.json` | `data/udemy.json` | `UDEMY_VAULT_DIR` (standalone iCloud "Udemy Vault") |`
- Add to the CLI flow block:
  ```bash
  # Udemy (one course at a time; transcripts only, never video)
  udemy-toolkit login && udemy-toolkit crawl "<course-url>" --limit 5 && udemy-toolkit build-vault
  ```
- Change the "Six independent toolkits" wording to "Seven independent toolkits".

In `README.md`, add the same command block to the commands section.

- [ ] **Step 8: Commit**

```bash
git add src/udemy_toolkit/auth.py src/udemy_toolkit/fetcher.py src/udemy_toolkit/cli.py tests/test_udemy_cli.py CLAUDE.md README.md
git commit -m "feat(udemy): interactive login, live caption fetcher, CLI, and docs"
```

- [ ] **Step 9: Refresh the knowledge graph**

The post-commit hook will have flagged `graphify-out/.needs_update`. Run `/graphify .` to re-extract and re-cluster, then commit the refreshed graph.

---

### Task 8: Machine-routable layer (so an agent can learn from the vault)

**Files:**
- Modify: `src/udemy_toolkit/vault.py`
- Modify: `tests/test_udemy_vault.py`
- Modify: `src/udemy_toolkit/cli.py` (`build-vault` prints the manifest path)

**Why this task exists:** Tasks 1-7 produce a vault that is *linked* (wikilinks, MOCs, topic notes). This task makes it *routable* — an agent can find the right notes cheaply without reading the whole vault, which is the precondition for generating a wiki or learning materials from it. It follows the pattern the repo already proved in the vault cross-linking pass (see CLAUDE.md, "Vault cross-linking pass (2026-07-28)"): a fixed tag vocabulary, a parallel `topic_links:` field, and one verification script that reads the whole set rather than trusting per-file self-reports.

**Interfaces:**
- Consumes: everything in `vault.py` from Task 6.
- Produces:
  - `TAG_VOCABULARY: tuple[str, ...]` — the fixed, closed tag list.
  - `classify_tags(text: str) -> List[str]` — 1-3 tags from that vocabulary only, keyword-matched, deterministic; falls back to `["uncategorized"]` when nothing matches.
  - `write_manifest(target: Path, catalog: UdemyCatalog) -> Path` — writes `index.yaml`.
  - `verify_vault(target: Path) -> dict` — reads the whole built vault and returns `{"notes": int, "dangling_links": [str], "orphan_notes": [str], "untagged": [str], "unknown_tags": [str]}`.
  - `build_vault(...)` additionally writes `index.yaml` and a `tags/<tag>.md` note per used tag.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_udemy_vault.py`:

```python
from udemy_toolkit.vault import TAG_VOCABULARY, classify_tags, verify_vault


def test_classify_tags_only_returns_vocabulary_members():
    tags = classify_tags("This lecture covers testing, debugging and deployment pipelines.")
    assert tags
    assert all(t in TAG_VOCABULARY for t in tags)
    assert len(tags) <= 3


def test_classify_tags_falls_back_rather_than_inventing():
    assert classify_tags("") == ["uncategorized"]


def test_manifest_lists_every_note_with_routing_metadata(tmp_path):
    import yaml

    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    manifest = yaml.safe_load((tmp_path / "index.yaml").read_text(encoding="utf-8"))
    assert manifest["vault"] == "Udemy Vault"
    assert manifest["counts"]["lectures"] == 2
    entry = manifest["courses"][0]["sections"][0]["lectures"][0]
    for key in ("title", "note", "url", "tags", "topics", "has_transcript", "words"):
        assert key in entry


def test_every_lecture_note_has_tags_frontmatter(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    body = (tmp_path / "lectures" / "test-course" / "1-welcome.md").read_text(encoding="utf-8")
    assert "\ntags: [" in body


def test_verify_vault_reports_a_clean_build(tmp_path):
    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    report = verify_vault(tmp_path)
    assert report["dangling_links"] == []
    assert report["orphan_notes"] == []
    assert report["untagged"] == []
    assert report["unknown_tags"] == []
    assert report["notes"] > 0


def test_verify_vault_catches_a_dangling_link(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    home = tmp_path / "Home.md"
    home.write_text(home.read_text(encoding="utf-8") + "\n- [[courses/does-not-exist|Ghost]]\n", encoding="utf-8")
    assert "courses/does-not-exist" in verify_vault(tmp_path)["dangling_links"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_udemy_vault.py -v`
Expected: FAIL — `ImportError: cannot import name 'TAG_VOCABULARY'`

- [ ] **Step 3: Add the tag vocabulary and classifier to `vault.py`**

Insert after `note_filename`:

```python
# A CLOSED vocabulary. Never invent a tag outside this tuple — a fixed list is
# what makes tags a reliable routing index rather than free-text noise.
TAG_VOCABULARY = (
    "fundamentals",
    "setup-install",
    "hands-on-demo",
    "architecture",
    "data",
    "testing",
    "debugging",
    "deployment-ops",
    "security",
    "performance",
    "tooling",
    "career-meta",
)

_TAG_CUES = {
    "fundamentals": ("introduction", "overview", "basics", "what is", "fundamental", "concept"),
    "setup-install": ("install", "setup", "set up", "environment", "prerequisite", "configure"),
    "hands-on-demo": ("demo", "walkthrough", "let's build", "hands on", "hands-on", "exercise", "project"),
    "architecture": ("architecture", "design pattern", "system design", "component", "structure"),
    "data": ("database", "sql", "schema", "dataset", "query", "storage", "pipeline"),
    "testing": ("test", "unit test", "assertion", "coverage", "pytest", "mock"),
    "debugging": ("debug", "error", "exception", "troubleshoot", "stack trace", "bug"),
    "deployment-ops": ("deploy", "docker", "ci/cd", "pipeline", "production", "kubernetes", "monitor"),
    "security": ("security", "auth", "token", "encryption", "vulnerab", "permission"),
    "performance": ("performance", "optimiz", "latency", "throughput", "cache", "benchmark"),
    "tooling": ("ide", "cli", "editor", "extension", "plugin", "git", "terminal"),
    "career-meta": ("career", "interview", "resume", "course wrap", "next steps", "congratulations"),
}


def classify_tags(text: str) -> List[str]:
    """1-3 tags drawn ONLY from ``TAG_VOCABULARY``, scored by cue frequency."""
    lowered = (text or "").lower()
    scored = []
    for tag in TAG_VOCABULARY:
        score = sum(lowered.count(cue) for cue in _TAG_CUES[tag])
        if score:
            scored.append((score, tag))
    if not scored:
        return ["uncategorized"]
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [tag for _score, tag in scored[:3]]
```

Add `List` to the `typing` import at the top of the file.

- [ ] **Step 4: Emit tags, tag notes, and the manifest**

In `_lecture_note`, change the signature to `_lecture_note(course, section, lecture, topics, tags)` and add one frontmatter line immediately after the `topic_links:` line:

```python
        f"tags: [{', '.join(tags)}]",
```

In `build_vault`, inside the lecture loop, immediately after `topics = match_topics(...)`:

```python
                tags = classify_tags(f"{lecture.title}\n{lecture.transcript}")
```

pass `tags` into `_lecture_note(...)`, and after the `for topic in topics:` block add:

```python
                for tag in tags:
                    tag_index[tag].append((note_link, lecture.title))
                manifest_lectures.append(
                    {
                        "title": lecture.title,
                        "note": note_link,
                        "url": lecture.url,
                        "section": section.title,
                        "tags": tags,
                        "topics": topics,
                        "has_transcript": lecture.has_transcript,
                        "words": len(lecture.transcript.split()),
                    }
                )
```

Declare `tag_index = defaultdict(list)` next to `topic_index`, and build `manifest_lectures` per section so it nests under its section entry.

After the topic-note loop, write one note per used tag with the same shape as a topic note, into `target / "tags" / f"{tag}.md"`.

Add a `## Tags` section to `Home.md` listing `- [[tags/<tag>|<tag>]] — N lecture(s)`, and one line under `## Meta`: `- [[index.yaml|Machine-readable index]]`.

- [ ] **Step 5: Write the manifest and the verifier**

Add to `vault.py`:

```python
def write_manifest(target: Path, manifest: dict) -> Path:
    """Write index.yaml — the cheap routing layer an agent reads first."""
    import yaml

    path = target / "index.yaml"
    path.write_text(
        "# Machine-readable index of this vault. Read this BEFORE grepping notes:\n"
        "# it maps every lecture to its note path, tags, and topics.\n"
        + yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def verify_vault(target: Path) -> dict:
    """Read the WHOLE built vault and report link/tag defects.

    Deliberately a single pass over every file — never trust per-note
    self-reports that each piece was written correctly.
    """
    target = Path(target)
    notes = sorted(p for p in target.rglob("*.md"))
    stems = {str(p.relative_to(target)).removesuffix(".md") for p in notes}

    dangling, linked_to, untagged, unknown_tags = [], set(), [], []
    for note in notes:
        text = note.read_text(encoding="utf-8")
        for raw in _WIKILINK_RE.findall(text):
            link = raw.strip()
            linked_to.add(link)
            if link not in stems and not link.endswith(".yaml"):
                dangling.append(link)
        if note.parent.name and note.parent.parent.name == "lectures":
            match = re.search(r"^tags: \[(.*)\]$", text, re.MULTILINE)
            found = [t.strip() for t in match.group(1).split(",") if t.strip()] if match else []
            if not found:
                untagged.append(str(note.relative_to(target)))
            unknown_tags.extend(
                t for t in found if t not in TAG_VOCABULARY and t != "uncategorized"
            )

    orphans = [
        str(p.relative_to(target))
        for p in notes
        if str(p.relative_to(target)).removesuffix(".md") not in linked_to
        and p.name not in {"Home.md", "Log.md"}
    ]
    return {
        "notes": len(notes),
        "dangling_links": sorted(set(dangling)),
        "orphan_notes": sorted(orphans),
        "untagged": sorted(untagged),
        "unknown_tags": sorted(set(unknown_tags)),
    }
```

Call `write_manifest(target, manifest)` at the end of `build_vault`, where `manifest` is:

```python
    manifest = {
        "vault": "Udemy Vault",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": (
            "Lecture transcripts captured from purchased Udemy courses. "
            "Transcript text only — no video or audio. Route via tags/ and topics/, "
            "then read the named lecture notes."
        ),
        "tag_vocabulary": list(TAG_VOCABULARY),
        "counts": {
            "courses": len(catalog.courses),
            "lectures": total,
            "topics": len(topic_index),
            "tags": len(tag_index),
        },
        "courses": manifest_courses,
    }
```

`removesuffix` is Python 3.9+; if the repo's floor is lower, use `p[:-3]` slicing instead.

- [ ] **Step 6: Run the tests**

Run: `pytest tests/test_udemy_vault.py -v`
Expected: 15 passed

If `import yaml` fails, `pyyaml` is already a transitive dependency of this repo — confirm with `python -c "import yaml"` before adding anything to `pyproject.toml`.

- [ ] **Step 7: Surface the verifier from the CLI**

In `cli.py`'s `build_vault`, after the existing success line:

```python
    report = vault_mod.verify_vault(target)
    problems = {k: v for k, v in report.items() if k != "notes" and v}
    if problems:
        console.print(f"[yellow]Vault verification found issues:[/yellow] {problems}")
        raise typer.Exit(code=1)
    console.print(f"[green]Verified:[/green] {report['notes']} note(s), no dangling links, all tagged.")
    console.print(f"Routing index: {target / 'index.yaml'}")
```

- [ ] **Step 8: Run the full suite and commit**

Run: `pytest -q -k udemy`
Expected: all udemy tests pass.

```bash
git add src/udemy_toolkit/vault.py src/udemy_toolkit/cli.py tests/test_udemy_vault.py
git commit -m "feat(udemy): routable vault layer - index.yaml manifest, fixed tag vocabulary, whole-vault verifier"
```

---

## Self-Review

**Spec coverage:** Task 8 was added after the spec, at the user's request, to make the vault machine-routable (index.yaml + closed tag vocabulary + whole-vault verifier); the spec's "Note shape" section is extended by it, not contradicted.

**Original spec coverage:** guardrails → Global Constraints + Task 5/7; scope decisions → Tasks 4-6; package layout → all tasks (with `curriculum.py`/`fetcher.py` split documented in File Structure); note shape → Task 6; error handling table → Tasks 5 and 7; testing section → the test file in every task.

**Placeholders:** none — every code step carries complete code, every run step an exact command and expected output.

**Type consistency:** `UdemyLecture.id` is `str` everywhere (curriculum stringifies it, the fake fetcher keys on `"10"`); `course_meta` returns the same four keys in Task 5's protocol, Task 5's fake, and Task 7's real fetcher; `note_filename` / `slugify` are used consistently in Task 6's implementation and tests.
