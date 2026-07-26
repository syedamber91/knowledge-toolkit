# SOIC Method Extraction Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `src/soic_method/` — a pipeline that extracts SOIC's investing method from 563 captured lesson transcripts into a two-tier executable rules bundle plus citation-gated judgement rubrics.

**Architecture:** Six stages — router (deterministic) → extractor (LLM) → verifier (deterministic) → refuter (LLM) → reconciler (deterministic) → publisher. The LLM stages take an injected `llm: Callable[[str], str]` so every stage is testable offline with a canned-response queue. Extraction returns **character offsets into raw `body_text`**, never copied text, so fabrication is impossible by construction.

**Tech Stack:** Python 3.9+, Pydantic v2, Typer, PyYAML, pytest.

## Global Constraints

- **Python floor is 3.9** — use `from __future__ import annotations` plus `typing.List/Dict/Optional`. No `X | Y` runtime annotations, no `match`.
- **Offsets index into raw `body_text`** (markers included). Normalization applies only to a sliced span, never globally. No global offset map.
- **No LLM call is made inside a test.** Every LLM stage takes `llm: Callable[[str], str]`; tests inject a queue.
- **Canonical corpus is `data/content.json`.** The Obsidian vault is a byte-identical derived view — never read it as a source.
- **Every `binding` ships `status: "unbound"`** until the `stock_analyzer` column inventory is verified. Never assert `bound`.
- **Unclassified eligibility defaults to ineligible** — courses and modules alike.
- **Conflict is the default classification.** Scoped-variant requires an attesting span that passes the same verifier.
- Corpus defect constants (verified 2026-07-20): `ROCE` 54× vs `ROC` 961×; `pad growth` 363× vs `PAT growth` 74×. Router lexicon must carry ASR variants.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/soic_method/__init__.py` | Package marker |
| `src/soic_method/models.py` | All Pydantic types: `Span`, `Citation`, `Rule`, `LessonRecord`, `Candidate`, `VerifyResult` |
| `src/soic_method/corpus.py` | Load `content.json` → `LessonRecord`s; hashing; slice normalization; timestamp resolution |
| `src/soic_method/eligibility.py` | Load/apply `course_eligibility.yaml` at course **and module** granularity |
| `src/soic_method/router.py` | Deterministic signal scan → `Candidate` spans |
| `src/soic_method/verify.py` | Gate 1 — six deterministic checks |
| `src/soic_method/corroborate.py` | Gate 1b — numeric corroboration across streams |
| `src/soic_method/extract.py` | Gate 2 input — LLM seam returning offsets |
| `src/soic_method/refute.py` | Gate 2 — adversarial LLM with context window |
| `src/soic_method/reconcile.py` | Gate 3 — grouping, scope attestation, conflict, merge, resolutions |
| `src/soic_method/publish.py` | Emit the bundle |
| `src/soic_method/cli.py` | Typer app |
| `configs/course_eligibility.yaml` | Course + module eligibility, `transcript_fidelity` |
| `tests/test_soic_method_*.py` | One test module per pipeline stage |

---

### Task 1: Package scaffold, models, and the PyYAML dependency

**Files:**
- Create: `src/soic_method/__init__.py`, `src/soic_method/models.py`
- Modify: `pyproject.toml` (add `pyyaml`, add CLI entry point)
- Test: `tests/test_soic_method_models.py`

**Interfaces:**
- Consumes: nothing
- Produces: `Span(start:int,end:int)`, `Citation`, `Binding`, `ValueRange`, `ScopeAttestation`, `Rule`, `LessonRecord`, `Candidate`, `VerifyResult` — every later task imports from here.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_models.py
import pytest
from pydantic import ValidationError

from soic_method.models import Binding, Rule, Span, ValueRange


def test_span_rejects_inverted_bounds():
    with pytest.raises(ValidationError):
        Span(start=100, end=50)


def test_rule_defaults_to_unbound_and_draft():
    r = Rule(tier="graded", kind="threshold", stage="screen")
    assert r.binding.status == "unbound"
    assert r.status == "draft"
    assert r.corroboration == 0
    assert r.rule_key is None


def test_rule_rejects_both_scalar_and_range():
    with pytest.raises(ValidationError):
        Rule(
            tier="graded", kind="range", stage="screen",
            value=40, value_range=ValueRange(min=40, max=50),
        )


def test_binding_never_defaults_to_bound():
    assert Binding().status == "unbound"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/__init__.py
"""SOIC method extraction pipeline.

Extracts SOIC's investing method from captured lesson transcripts into a
two-tier executable rules bundle plus citation-gated judgement rubrics.
"""
```

```python
# src/soic_method/models.py
"""Pydantic types shared across every pipeline stage.

Offsets (`Span`) always index into a lesson's RAW ``body_text`` — markers
included. Normalization is applied to a slice, never globally, so there is no
offset map to keep in sync.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

TIER_KNOCKOUT = "knockout"
TIER_GRADED = "graded"

CONVICTIONS = ("absolute", "strong", "preference")
OPERATORS = ("gte", "lte", "gt", "lt", "eq")
STATUSES = ("draft", "active", "conflicted", "unbound", "needs_audio_check")
FIDELITIES = ("verbatim", "translated")


class Span(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @model_validator(mode="after")
    def _ordered(self) -> "Span":
        if self.end <= self.start:
            raise ValueError("span end must exceed start")
        return self


class Citation(BaseModel):
    lesson_id: str
    lesson_url: str
    timestamp: str                     # "HH:MM:SS", nearest preceding marker
    span: Span
    transcript_fidelity: str = "verbatim"
    text_hash: str = ""                # sha256 of the lesson body_text


class Binding(BaseModel):
    # Never default to "bound" — the stock_analyzer column inventory is unverified.
    source: Optional[str] = None
    table: Optional[str] = None
    expr: Optional[str] = None
    status: str = "unbound"


class ValueRange(BaseModel):
    min: float
    max: float

    @model_validator(mode="after")
    def _ordered(self) -> "ValueRange":
        if self.max < self.min:
            raise ValueError("range max must be >= min")
        return self


class ScopeAttestation(BaseModel):
    lesson_id: str
    span: Span


class Rule(BaseModel):
    rule_key: Optional[str] = None     # None until the vocabulary names it
    tier: str
    kind: str                          # threshold | range | boolean
    stage: str                         # screen | sector | valuation | exit
    operator: Optional[str] = None
    value: Optional[float] = None
    value_range: Optional[ValueRange] = None
    unit: Optional[str] = None
    conviction: str = "preference"
    as_of: Optional[str] = None        # recording period, e.g. "2021-06"
    scope: Dict[str, str] = Field(default_factory=dict)
    scope_attestation: Optional[ScopeAttestation] = None
    binding: Binding = Field(default_factory=Binding)
    citations: List[Citation] = Field(default_factory=list)
    corroboration: int = 0
    status: str = "draft"

    @model_validator(mode="after")
    def _one_value_form(self) -> "Rule":
        if self.value is not None and self.value_range is not None:
            raise ValueError("rule carries both a scalar value and a range")
        return self


class LessonRecord(BaseModel):
    lesson_id: str
    course_title: str
    module_title: str
    title: str
    url: str
    body_text: str
    ai_summary: str = ""
    text_hash: str = ""
    eligible: bool = False
    transcript_fidelity: str = "verbatim"


class Candidate(BaseModel):
    lesson_id: str
    span: Span
    signals: List[str] = Field(default_factory=list)


class VerifyResult(BaseModel):
    ok: bool
    reasons: List[str] = Field(default_factory=list)
```

- [ ] **Step 4: Add the dependency and entry point**

In `pyproject.toml`, add `"pyyaml>=6.0",` to `[project].dependencies`, and add to `[project.scripts]`:

```toml
soic-method = "soic_method.cli:app"
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_models.py -v`
Expected: PASS (4 passed)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/soic_method/__init__.py src/soic_method/models.py tests/test_soic_method_models.py
git commit -m "feat(soic-method): package scaffold and core models"
```

---

### Task 2: Corpus loader, hashing, slice normalization, timestamp resolution

**Files:**
- Create: `src/soic_method/corpus.py`
- Test: `tests/test_soic_method_corpus.py`

**Interfaces:**
- Consumes: `LessonRecord`, `Span` from Task 1
- Produces:
  - `load_corpus(path: Path) -> List[LessonRecord]`
  - `hash_text(text: str) -> str` (sha256 hex)
  - `normalize_slice(text: str) -> str` (strip `[HH:MM:SS]`, collapse whitespace, casefold)
  - `resolve_timestamp(body_text: str, start: int) -> str`
  - `lesson_id_from_url(url: str) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_corpus.py
from soic_method.corpus import (
    hash_text,
    lesson_id_from_url,
    normalize_slice,
    resolve_timestamp,
)

BODY = (
    "[00:00:05] Hi everyone.\n"
    "[00:41:12] we don't even look at a business doing less than 18% ROC\n"
    "[00:41:20] moving on.\n"
)


def test_normalize_strips_markers_and_collapses_space():
    assert normalize_slice("[00:41:12] less   than\n18%") == "less than 18%"


def test_normalize_casefolds():
    assert normalize_slice("Less Than 18% ROCE") == "less than 18% roce"


def test_resolve_timestamp_picks_nearest_preceding_marker():
    idx = BODY.index("we don't even")
    assert resolve_timestamp(BODY, idx) == "00:41:12"


def test_resolve_timestamp_before_any_marker_returns_zero():
    assert resolve_timestamp("no markers here", 3) == "00:00:00"


def test_hash_is_stable_and_differs_on_change():
    assert hash_text("abc") == hash_text("abc")
    assert hash_text("abc") != hash_text("abd")


def test_lesson_id_is_the_url_tail():
    url = "https://learn.soic.in/learn/home/SOIC-Course/x/section/299814/lesson/1823241"
    assert lesson_id_from_url(url) == "1823241"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_corpus.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.corpus'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/corpus.py
"""Load the captured corpus and provide offset-safe text utilities.

``data/content.json`` is the canonical source. The Obsidian "Stock Market
Vault" is a byte-identical derived view (verified 2026-07-20) and must never be
read as a source.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import List

from .models import LessonRecord

# Transcript markers look like "[00:41:12] ".
_MARKER = re.compile(r"\[\d{2}:\d{2}:\d{2}\]")
_WS = re.compile(r"\s+")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_slice(text: str) -> str:
    """Normalize a SLICE for content comparison.

    Never applied to a whole transcript — offsets index raw ``body_text``, so
    global normalization would desynchronize them.
    """
    return _WS.sub(" ", _MARKER.sub(" ", text)).strip().casefold()


def resolve_timestamp(body_text: str, start: int) -> str:
    """Nearest PRECEDING marker before ``start``; "00:00:00" if none."""
    last = "00:00:00"
    for m in _MARKER.finditer(body_text, 0, max(start, 0) + 1):
        if m.start() <= start:
            last = m.group(0)[1:-1]
    return last


def lesson_id_from_url(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def load_corpus(path: Path) -> List[LessonRecord]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out: List[LessonRecord] = []
    for course in data.get("courses", []):
        for module in course.get("modules", []) or []:
            for lesson in module.get("lessons", []) or []:
                body = lesson.get("body_text") or ""
                if not body:
                    continue
                out.append(
                    LessonRecord(
                        lesson_id=lesson_id_from_url(lesson.get("url", "")),
                        course_title=course.get("title", ""),
                        module_title=module.get("title", ""),
                        title=lesson.get("title", ""),
                        url=lesson.get("url", ""),
                        body_text=body,
                        ai_summary=lesson.get("ai_summary") or "",
                        text_hash=hash_text(body),
                    )
                )
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_corpus.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Add a real-corpus smoke test**

```python
# append to tests/test_soic_method_corpus.py
from pathlib import Path

import pytest

from soic_method.corpus import load_corpus

CONTENT = Path(__file__).resolve().parents[1] / "data" / "content.json"


@pytest.mark.skipif(not CONTENT.exists(), reason="corpus not present")
def test_load_corpus_finds_lessons_with_bodies():
    lessons = load_corpus(CONTENT)
    assert len(lessons) > 400
    assert all(l.body_text for l in lessons)
    assert all(l.text_hash for l in lessons)
```

- [ ] **Step 6: Run and commit**

Run: `python -m pytest tests/test_soic_method_corpus.py -v`
Expected: PASS (7 passed)

```bash
git add src/soic_method/corpus.py tests/test_soic_method_corpus.py
git commit -m "feat(soic-method): corpus loader, hashing, slice normalization, timestamp resolution"
```

---

### Task 3: Eligibility at course AND module granularity

**Files:**
- Create: `src/soic_method/eligibility.py`, `configs/course_eligibility.yaml`
- Test: `tests/test_soic_method_eligibility.py`

**Interfaces:**
- Consumes: `LessonRecord` from Task 1
- Produces:
  - `load_eligibility(path: Path) -> Eligibility`
  - `Eligibility.is_eligible(course_title: str, module_title: str) -> bool`
  - `Eligibility.fidelity(course_title: str) -> str`
  - `apply_eligibility(lessons: List[LessonRecord], elig: Eligibility) -> List[LessonRecord]`

**Why module granularity:** Level 6 is course-eligible but contains guest-led modules (`a-primer-to-saas-by-siddharth-bhandari`, `masterclass-on-banks-nbfcs-by-digant-haria`). Bhandari also appears in the excluded Super Investors course — course-level filtering alone would admit his rules through the L6 door.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_eligibility.py
from pathlib import Path

from soic_method.eligibility import apply_eligibility, load_eligibility
from soic_method.models import LessonRecord

CONFIG = Path(__file__).resolve().parents[1] / "configs" / "course_eligibility.yaml"


def _lesson(course, module):
    return LessonRecord(
        lesson_id="1", course_title=course, module_title=module,
        title="t", url="u", body_text="b",
    )


def test_solo_course_is_eligible():
    e = load_eligibility(CONFIG)
    assert e.is_eligible("Level 5- How to Screen & Filter Epic Stocks", "any")


def test_interview_course_is_excluded():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible("Conversation with India's Super Investors", "any")


def test_guest_module_inside_eligible_course_is_excluded():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible(
        "Level 6 Become a Sectoral Expert",
        "A Primer to SaaS by Siddharth Bhandari",
    )


def test_unknown_course_defaults_to_ineligible():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible("Some Course We Never Classified", "any")


def test_level_one_is_marked_translated():
    e = load_eligibility(CONFIG)
    assert e.fidelity("Level 1- Financial Literacy Course For All (Hindi)") == "translated"


def test_apply_eligibility_stamps_records():
    e = load_eligibility(CONFIG)
    lessons = [
        _lesson("Level 5- How to Screen & Filter Epic Stocks", "m"),
        _lesson("Conversation with India's Super Investors", "m"),
    ]
    out = apply_eligibility(lessons, e)
    assert [l.eligible for l in out] == [True, False]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_eligibility.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.eligibility'`

- [ ] **Step 3: Write the config**

```yaml
# configs/course_eligibility.yaml
# Rules-eligibility for the SOIC method extractor.
# UNLISTED COURSES AND MODULES ARE INELIGIBLE. Never infer at runtime.
#
# transcript_fidelity:
#   verbatim   - ASR of the spoken audio (may still be heavily degraded)
#   translated - text is an English rendering of non-English audio;
#                ear-verification does NOT apply
courses:
  "Level 1- Financial Literacy Course For All (Hindi)":
    eligible: true
    transcript_fidelity: translated
  "Level 2-Intensive Course (Investing from Scratch)- English":
    eligible: true
    transcript_fidelity: verbatim
  "Level 3 How to Value a Company & Portfolio Creation!":
    eligible: true
    transcript_fidelity: verbatim
  "L4- When to Hold, Buy & Sell using Technicals for Long Term!":
    eligible: true
    transcript_fidelity: verbatim
  "Level 5- How to Screen & Filter Epic Stocks":
    eligible: true
    transcript_fidelity: verbatim
  "Level 6 Become a Sectoral Expert":
    eligible: true
    transcript_fidelity: verbatim
  "Crash Course":
    eligible: true
    transcript_fidelity: verbatim
  "Ask SOIC on Saturdays at 11 a.m.":
    eligible: true
    transcript_fidelity: verbatim
  "SOIC Market Signals + StockScans":
    eligible: true
    transcript_fidelity: verbatim
  "Masterclass on Investing Using AI":
    eligible: true
    transcript_fidelity: verbatim
  "SOIC Labs: Become an AI-Powered Investor":
    eligible: true
    transcript_fidelity: verbatim
  # Guest interviews — no speaker labels, unattributable by construction.
  "Conversation with India's Super Investors":
    eligible: false
    transcript_fidelity: verbatim
  # Confirmed member/guest presentations.
  "Rising Stars":
    eligible: false
    transcript_fidelity: verbatim
  "Important Membership Updates":
    eligible: false
    transcript_fidelity: verbatim

# Modules excluded even though their course is eligible (guest-taught).
# Matched case-insensitively as a substring of the module title.
excluded_modules:
  - "by Siddharth Bhandari"
  - "by Digant Haria"
```

- [ ] **Step 4: Write the implementation**

```python
# src/soic_method/eligibility.py
"""Course- and module-level rules eligibility.

Course granularity alone is insufficient: Level 6 is eligible but contains
guest-taught modules, and one of those guests also appears in the excluded
Super Investors course.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from .models import LessonRecord


class Eligibility:
    def __init__(self, courses: Dict[str, dict], excluded_modules: List[str]):
        self._courses = courses
        self._excluded = [m.casefold() for m in excluded_modules]

    def is_eligible(self, course_title: str, module_title: str) -> bool:
        entry = self._courses.get(course_title)
        if entry is None or not entry.get("eligible", False):
            return False           # unlisted defaults to ineligible
        mod = (module_title or "").casefold()
        return not any(x in mod for x in self._excluded)

    def fidelity(self, course_title: str) -> str:
        entry = self._courses.get(course_title) or {}
        return entry.get("transcript_fidelity", "verbatim")


def load_eligibility(path: Path) -> Eligibility:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Eligibility(data.get("courses") or {}, data.get("excluded_modules") or [])


def apply_eligibility(lessons: List[LessonRecord], elig: Eligibility) -> List[LessonRecord]:
    out: List[LessonRecord] = []
    for l in lessons:
        out.append(
            l.model_copy(
                update={
                    "eligible": elig.is_eligible(l.course_title, l.module_title),
                    "transcript_fidelity": elig.fidelity(l.course_title),
                }
            )
        )
    return out
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_eligibility.py -v`
Expected: PASS (6 passed)

- [ ] **Step 6: Commit**

```bash
git add src/soic_method/eligibility.py configs/course_eligibility.yaml tests/test_soic_method_eligibility.py
git commit -m "feat(soic-method): course and module eligibility with ineligible-by-default"
```

---

### Task 4: Router — ASR-aware deterministic signal scan

**Files:**
- Create: `src/soic_method/router.py`
- Test: `tests/test_soic_method_router.py`

**Interfaces:**
- Consumes: `LessonRecord`, `Candidate`, `Span`
- Produces:
  - `SIGNAL_TERMS: Dict[str, List[str]]` (metric aliases incl. ASR variants)
  - `find_candidates(lesson: LessonRecord, window: int = 400) -> List[Candidate]`
  - `route(lessons: List[LessonRecord]) -> List[Candidate]` (skips ineligible)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_router.py
from soic_method.models import LessonRecord
from soic_method.router import find_candidates, route


def _lesson(body, eligible=True):
    return LessonRecord(
        lesson_id="1", course_title="c", module_title="m", title="t",
        url="u", body_text=body, eligible=eligible,
    )


def test_matches_asr_variant_roc_not_just_roce():
    # ROCE appears 54x in the corpus; ROC 961x. Missing ROC misses ~95%.
    cands = find_candidates(_lesson("[00:01:00] we want ROC above 18% consistently"))
    assert len(cands) == 1
    assert "roc" in cands[0].signals


def test_matches_asr_variant_pad_growth():
    cands = find_candidates(_lesson("[00:01:00] look for more than 15% pad growth here"))
    assert len(cands) == 1
    assert "pat" in cands[0].signals


def test_requires_both_a_metric_and_a_comparative_number():
    assert find_candidates(_lesson("[00:01:00] ROC is a useful concept")) == []
    assert find_candidates(_lesson("[00:01:00] more than 15% of people agree")) == []


def test_span_covers_a_context_window_around_the_hit():
    body = "x" * 500 + "[00:01:00] ROC above 18% " + "y" * 500
    cand = find_candidates(_lesson(body))[0]
    assert cand.span.start < 500
    assert cand.span.end > 520


def test_route_skips_ineligible_lessons():
    good = _lesson("[00:01:00] ROC above 18%", eligible=True)
    bad = _lesson("[00:01:00] ROC above 18%", eligible=False)
    assert len(route([good, bad])) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_router.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.router'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/router.py
"""Deterministic candidate routing. No LLM.

The signal lexicon MUST carry ASR variants. Measured in the corpus on
2026-07-20: ``ROCE`` 54x vs ``ROC`` 961x; ``PAT growth`` 74x vs ``pad growth``
363x. A naive lexicon misses the overwhelming majority of the material.
"""

from __future__ import annotations

import re
from typing import Dict, List

from .models import Candidate, LessonRecord, Span

# Canonical metric -> surface forms actually present in the ASR.
SIGNAL_TERMS: Dict[str, List[str]] = {
    "roc": ["roce", "roc", "return on capital"],
    "pat": ["pat growth", "pad growth", "profit after tax", "net profit"],
    "pe": ["p/e", "pe ratio", "p e ratio", "price to earnings", "times earnings"],
    "sales": ["sales growth", "revenue growth", "topline"],
    "margin": ["operating margin", "opm", "ebitda margin", "gross margin"],
    "debt": ["debt to equity", "d/e", "debt equity", "leverage"],
    "pledge": ["pledge", "pledged"],
}

_COMPARATIVE = re.compile(
    r"\b(less than|below|under|at most|no more than|not more than|maximum|max|"
    r"more than|above|over|at least|minimum|min|greater than|north of)\b",
    re.I,
)
_NUMBER = re.compile(r"\d")


def _metric_hits(text_lower: str) -> List[str]:
    return [
        canon
        for canon, forms in SIGNAL_TERMS.items()
        if any(f in text_lower for f in forms)
    ]


def find_candidates(lesson: LessonRecord, window: int = 400) -> List[Candidate]:
    """Flag spans carrying BOTH a metric term AND a comparative-with-number."""
    body = lesson.body_text
    out: List[Candidate] = []
    for m in _COMPARATIVE.finditer(body):
        start = max(0, m.start() - window)
        end = min(len(body), m.end() + window)
        chunk = body[start:end]
        if not _NUMBER.search(chunk):
            continue
        signals = _metric_hits(chunk.lower())
        if not signals:
            continue
        out.append(Candidate(lesson_id=lesson.lesson_id,
                             span=Span(start=start, end=end),
                             signals=signals))
    return _merge_overlaps(out)


def _merge_overlaps(cands: List[Candidate]) -> List[Candidate]:
    if not cands:
        return []
    merged = [cands[0]]
    for c in cands[1:]:
        last = merged[-1]
        if c.span.start <= last.span.end:
            merged[-1] = Candidate(
                lesson_id=last.lesson_id,
                span=Span(start=last.span.start, end=max(last.span.end, c.span.end)),
                signals=sorted(set(last.signals) | set(c.signals)),
            )
        else:
            merged.append(c)
    return merged


def route(lessons: List[LessonRecord], window: int = 400) -> List[Candidate]:
    out: List[Candidate] = []
    for lesson in lessons:
        if not lesson.eligible:
            continue
        out.extend(find_candidates(lesson, window=window))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_router.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/soic_method/router.py tests/test_soic_method_router.py
git commit -m "feat(soic-method): ASR-aware deterministic router"
```

---

### Task 5: Verifier — Gate 1's six deterministic checks

**Files:**
- Create: `src/soic_method/verify.py`
- Test: `tests/test_soic_method_verify.py`

**Interfaces:**
- Consumes: `Rule`, `Citation`, `Span`, `VerifyResult`, `LessonRecord`, `normalize_slice`, `resolve_timestamp`
- Produces:
  - `MIN_SPAN_CHARS = 40`
  - `DIRECTION_TOKENS: Dict[str, List[str]]`
  - `verify_rule(rule: Rule, lessons: Dict[str, LessonRecord]) -> VerifyResult`

**This is the load-bearing gate and carries the most test weight.** It prevents fabricated *strings* (checks 1–2, 6) and the two most damaging silent errors — wrong value (3) and inverted operator (4). It does **not** prevent misattributed *meaning*; that is the refuter's job.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_verify.py
from soic_method.models import Binding, Citation, LessonRecord, Rule, Span
from soic_method.verify import verify_rule

BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[00:41:12] we don't even look at a business doing less than 18% ROC frankly\n"
    "[00:41:30] anyway moving on to the next topic entirely.\n"
)
HASH = "deadbeef"


def _lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=BODY, text_hash=HASH, eligible=True,
        )
    }


def _span_of(text):
    s = BODY.index(text)
    return Span(start=s, end=s + len(text))


QUOTE = "we don't even look at a business doing less than 18% ROC frankly"


def _rule(**over):
    base = dict(
        tier="graded", kind="threshold", stage="screen",
        operator="lte", value=18, unit="percent",
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                            span=_span_of(QUOTE), text_hash=HASH)],
    )
    base.update(over)
    return Rule(**base)


def test_valid_rule_passes():
    assert verify_rule(_rule(), _lessons()).ok


def test_rejects_span_shorter_than_minimum():
    short = Span(start=BODY.index("18%"), end=BODY.index("18%") + 3)
    r = _rule(citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                                  span=short, text_hash=HASH)])
    res = verify_rule(r, _lessons())
    assert not res.ok and any("too short" in x for x in res.reasons)


def test_rejects_offsets_out_of_range():
    bad = Span(start=99000, end=99100)
    r = _rule(citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                                  span=bad, text_hash=HASH)])
    res = verify_rule(r, _lessons())
    assert not res.ok and any("out of range" in x for x in res.reasons)


def test_rejects_when_value_absent_from_span():
    # Span says 18%, rule claims 15 — the silent-wrong-value case.
    res = verify_rule(_rule(value=15), _lessons())
    assert not res.ok and any("value 15" in x for x in res.reasons)


def test_rejects_inverted_operator():
    # Span says "less than", rule claims gte — the silent-inversion case.
    res = verify_rule(_rule(operator="gte"), _lessons())
    assert not res.ok and any("direction" in x for x in res.reasons)


def test_rejects_corpus_hash_mismatch():
    res = verify_rule(_rule(), {
        "1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                          title="t", url="u", body_text=BODY,
                          text_hash="different", eligible=True)
    })
    assert not res.ok and any("hash" in x for x in res.reasons)


def test_rejects_ineligible_lesson():
    lessons = _lessons()
    lessons["1"] = lessons["1"].model_copy(update={"eligible": False})
    res = verify_rule(_rule(), lessons)
    assert not res.ok and any("ineligible" in x for x in res.reasons)


def test_rejects_unknown_lesson():
    res = verify_rule(_rule(), {})
    assert not res.ok and any("unknown lesson" in x for x in res.reasons)


def test_boolean_rule_skips_value_and_direction_checks():
    r = Rule(
        tier="knockout", kind="boolean", stage="screen", conviction="absolute",
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                            span=_span_of(QUOTE), text_hash=HASH)],
    )
    assert verify_rule(r, _lessons()).ok
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_verify.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.verify'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/verify.py
"""Gate 1 — deterministic verification. No LLM.

What this gate DOES: makes fabricated citations impossible (offsets are sliced
from the corpus, never copied), and converts the two most damaging silent
errors — wrong value and inverted operator — into rejections.

What it does NOT do: prevent misattributed MEANING. Quote-mining, negation,
reported speech and hypotheticals all survive this gate by design; catching
them is the refuter's job.
"""

from __future__ import annotations

from typing import Dict, List

from .corpus import normalize_slice
from .models import LessonRecord, Rule, VerifyResult

MIN_SPAN_CHARS = 40

DIRECTION_TOKENS: Dict[str, List[str]] = {
    "lte": ["less than", "below", "under", "at most", "no more than",
            "not more than", "maximum", "max", "cheaper than", "within"],
    "gte": ["more than", "above", "over", "at least", "minimum", "min",
            "greater than", "north of", "upwards of", "in excess of"],
}
DIRECTION_TOKENS["lt"] = DIRECTION_TOKENS["lte"]
DIRECTION_TOKENS["gt"] = DIRECTION_TOKENS["gte"]


def _value_forms(value: float) -> List[str]:
    """Surface forms a number may take in a transcript."""
    forms = []
    if float(value).is_integer():
        forms.append(str(int(value)))
    forms.append(str(value))
    return forms


def verify_rule(rule: Rule, lessons: Dict[str, LessonRecord]) -> VerifyResult:
    reasons: List[str] = []

    if not rule.citations:
        return VerifyResult(ok=False, reasons=["no citations"])

    for cit in rule.citations:
        lesson = lessons.get(cit.lesson_id)
        if lesson is None:
            reasons.append("unknown lesson %s" % cit.lesson_id)
            continue

        # 6. corpus snapshot integrity — checked first; everything else is
        # meaningless against drifted text.
        if cit.text_hash and lesson.text_hash and cit.text_hash != lesson.text_hash:
            reasons.append("corpus hash mismatch for lesson %s" % cit.lesson_id)
            continue

        # 5. eligibility (defence in depth — the router already skipped these)
        if not lesson.eligible:
            reasons.append("ineligible lesson %s" % cit.lesson_id)
            continue

        # 1. offsets in range
        if cit.span.end > len(lesson.body_text):
            reasons.append("span out of range for lesson %s" % cit.lesson_id)
            continue

        raw = lesson.body_text[cit.span.start:cit.span.end]
        norm = normalize_slice(raw)

        # 2. minimum length — without this a fragment like "18%" matches
        # trivially somewhere in a 300KB transcript.
        if len(norm) < MIN_SPAN_CHARS:
            reasons.append("span too short (%d chars)" % len(norm))
            continue

        # 3. the claimed value must appear in the span
        if rule.value is not None:
            if not any(f in norm for f in _value_forms(rule.value)):
                reasons.append("value %s absent from span" % _value_forms(rule.value)[0])
        if rule.value_range is not None:
            for bound in (rule.value_range.min, rule.value_range.max):
                if not any(f in norm for f in _value_forms(bound)):
                    reasons.append("range bound %s absent from span" % _value_forms(bound)[0])

        # 4. comparative direction must match the operator
        if rule.operator in DIRECTION_TOKENS:
            if not any(tok in norm for tok in DIRECTION_TOKENS[rule.operator]):
                reasons.append(
                    "direction mismatch: no %s token in span" % rule.operator
                )

    return VerifyResult(ok=not reasons, reasons=reasons)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_verify.py -v`
Expected: PASS (9 passed)

- [ ] **Step 5: Commit**

```bash
git add src/soic_method/verify.py tests/test_soic_method_verify.py
git commit -m "feat(soic-method): Gate 1 verifier with value and direction checks"
```

---

### Task 6: Gate 1b — numeric corroboration across independent streams

**Files:**
- Create: `src/soic_method/corroborate.py`
- Test: `tests/test_soic_method_corroborate.py`

**Interfaces:**
- Consumes: `Rule`, `LessonRecord`, `normalize_slice`
- Produces: `corroborate(rule: Rule, lessons: Dict[str, LessonRecord]) -> Rule` (returns a copy with `corroboration` set and `status` promoted to `active` or set to `needs_audio_check`)

**Why:** ASR degrades digits (`"499% pad growth"`), proper nouns (`Sinjenta`, `Sumitoma`/`Sumitobho`) and whole sentences (`"the bears and BASF just in my opinion are three is Satya"`). A refuter cannot catch this — both sides read the same corrupted text. Independent attestation is the only defence.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_corroborate.py
from soic_method.corroborate import corroborate
from soic_method.models import Citation, LessonRecord, Rule, Span

QUOTE = "we don't even look at a business doing less than 18% ROC frankly"
BODY_A = "[00:41:12] " + QUOTE + "\n"
BODY_B = "[00:10:00] our bar is a minimum 18% ROC across the cycle honestly\n"


def _lesson(lid, body, summary=""):
    return LessonRecord(lesson_id=lid, course_title="c", module_title="m",
                        title="t", url="u", body_text=body,
                        ai_summary=summary, eligible=True)


def _rule(lesson_ids):
    return Rule(
        tier="graded", kind="threshold", stage="screen", operator="lte", value=18,
        citations=[
            Citation(lesson_id=i, lesson_url="u", timestamp="00:41:12",
                     span=Span(start=0, end=len(BODY_A)))
            for i in lesson_ids
        ],
    )


def test_two_lessons_corroborate_and_promote_to_active():
    lessons = {"1": _lesson("1", BODY_A), "2": _lesson("2", BODY_B)}
    out = corroborate(_rule(["1", "2"]), lessons)
    assert out.corroboration == 2
    assert out.status == "active"


def test_single_lesson_with_summary_attestation_counts_as_two():
    lessons = {"1": _lesson("1", BODY_A, summary="ROC threshold is 18% minimum")}
    out = corroborate(_rule(["1"]), lessons)
    assert out.corroboration == 2
    assert out.status == "active"


def test_single_uncorroborated_stream_needs_audio_check():
    lessons = {"1": _lesson("1", BODY_A, summary="no numbers in this summary")}
    out = corroborate(_rule(["1"]), lessons)
    assert out.corroboration == 1
    assert out.status == "needs_audio_check"


def test_boolean_rule_needs_no_numeric_corroboration():
    lessons = {"1": _lesson("1", BODY_A)}
    r = Rule(tier="knockout", kind="boolean", stage="screen", conviction="absolute",
             citations=[Citation(lesson_id="1", lesson_url="u",
                                 timestamp="00:00:00",
                                 span=Span(start=0, end=len(BODY_A)))])
    assert corroborate(r, lessons).status == "active"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_corroborate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.corroborate'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/corroborate.py
"""Gate 1b — numeric corroboration.

Any digit-bearing rule must be attested by at least two independent renderings
of the audio: two different lessons, or one lesson plus its ``ai_summary``
(which is generated from the same audio by a different process). Values with a
single stream get ``needs_audio_check`` and enter a human ear-verification
queue rather than shipping as truth.
"""

from __future__ import annotations

from typing import Dict, List

from .corpus import normalize_slice
from .models import LessonRecord, Rule

MIN_CORROBORATION = 2


def _value_forms(value: float) -> List[str]:
    forms = []
    if float(value).is_integer():
        forms.append(str(int(value)))
    forms.append(str(value))
    return forms


def _attested_in(text: str, values: List[float]) -> bool:
    norm = normalize_slice(text)
    return all(
        any(f in norm for f in _value_forms(v)) for v in values
    )


def _rule_values(rule: Rule) -> List[float]:
    if rule.value is not None:
        return [rule.value]
    if rule.value_range is not None:
        return [rule.value_range.min, rule.value_range.max]
    return []


def corroborate(rule: Rule, lessons: Dict[str, LessonRecord]) -> Rule:
    values = _rule_values(rule)
    if not values:
        # Non-numeric rule: nothing for ASR to corrupt numerically.
        return rule.model_copy(update={"corroboration": len(rule.citations),
                                       "status": "active"})

    streams = 0
    seen_lessons = set()
    for cit in rule.citations:
        lesson = lessons.get(cit.lesson_id)
        if lesson is None or lesson.lesson_id in seen_lessons:
            continue
        seen_lessons.add(lesson.lesson_id)
        if _attested_in(lesson.body_text, values):
            streams += 1
        if lesson.ai_summary and _attested_in(lesson.ai_summary, values):
            streams += 1

    status = "active" if streams >= MIN_CORROBORATION else "needs_audio_check"
    return rule.model_copy(update={"corroboration": streams, "status": status})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_corroborate.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/soic_method/corroborate.py tests/test_soic_method_corroborate.py
git commit -m "feat(soic-method): Gate 1b numeric corroboration across streams"
```

---

### Task 7: Extractor — LLM seam returning offsets, never copied text

**Files:**
- Create: `src/soic_method/extract.py`
- Test: `tests/test_soic_method_extract.py`

**Interfaces:**
- Consumes: `Candidate`, `LessonRecord`, `Rule`, `Citation`, `Span`, `resolve_timestamp`
- Produces:
  - `build_extract_prompt(lesson: LessonRecord, cand: Candidate, rule_keys: List[str]) -> str`
  - `extract_rules(lesson, cand, llm, rule_keys: Optional[List[str]] = None) -> List[Rule]`

**`rule_key` comes from a controlled vocabulary, never invented.** The model picks from `rule_keys`; anything that fits none returns `null` and stays `status: draft` for human naming. Free-text keys would silently break Gate 3's grouping — two spellings of the same rule never compare, so a real contradiction ships as two independent happy rules. When `rule_keys` is empty (the bootstrap run) every rule is a draft by design.

**Why offsets:** copied quotes invite the extractor to silently *repair* ASR while transcribing (`ROC`→`ROCE`, `pad`→`PAT`), which fails a substring match and pollutes `rejected.jsonl` — the very signal used as the fabrication alarm. Offsets remove the opportunity.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_extract.py
import json

from soic_method.extract import build_extract_prompt, extract_rules
from soic_method.models import Candidate, LessonRecord, Span

BODY = (
    "[00:00:05] some intro padding text goes here for length.\n"
    "[00:41:12] we don't even look at a business doing less than 18% ROC frankly\n"
)
QUOTE = "we don't even look at a business doing less than 18% ROC frankly"


def _lesson():
    return LessonRecord(lesson_id="1", course_title="c", module_title="m",
                        title="t", url="https://x/lesson/1", body_text=BODY,
                        text_hash="h", eligible=True)


def _cand():
    return Candidate(lesson_id="1", span=Span(start=0, end=len(BODY)), signals=["roc"])


def _llm_returning(payload):
    return lambda prompt: json.dumps(payload)


def test_prompt_includes_offset_indexed_text_and_forbids_quoting():
    p = build_extract_prompt(_lesson(), _cand())
    assert "start" in p and "end" in p
    assert "offset" in p.lower()


def test_extract_maps_offsets_to_citation_with_resolved_timestamp():
    s = BODY.index(QUOTE)
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "unit": "percent",
        "start": s, "end": s + len(QUOTE),
    }]}))
    assert len(rules) == 1
    cit = rules[0].citations[0]
    assert cit.timestamp == "00:41:12"
    assert cit.text_hash == "h"
    assert cit.lesson_url == "https://x/lesson/1"


def test_extract_drops_rules_with_out_of_range_offsets():
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "start": 0, "end": 999999,
    }]}))
    assert rules == []


def test_extract_tolerates_malformed_llm_output():
    assert extract_rules(_lesson(), _cand(), lambda p: "not json at all") == []


def test_extract_returns_empty_on_empty_rules_list():
    assert extract_rules(_lesson(), _cand(), _llm_returning({"rules": []})) == []


def test_prompt_lists_the_controlled_vocabulary():
    p = build_extract_prompt(_lesson(), _cand(), ["screen.roc.floor"])
    assert "screen.roc.floor" in p


def test_rule_key_outside_the_vocabulary_is_dropped_to_draft():
    s = BODY.index(QUOTE)
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "rule_key": "invented.key.here",
        "start": s, "end": s + len(QUOTE),
    }]}), rule_keys=["screen.roc.floor"])
    assert rules[0].rule_key is None
    assert rules[0].status == "draft"


def test_rule_key_inside_the_vocabulary_is_kept():
    s = BODY.index(QUOTE)
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "rule_key": "screen.roc.floor",
        "start": s, "end": s + len(QUOTE),
    }]}), rule_keys=["screen.roc.floor"])
    assert rules[0].rule_key == "screen.roc.floor"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_extract.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.extract'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/extract.py
"""Rule extraction — the first LLM stage.

The model never copies text. It returns ``start``/``end`` character offsets
into the raw ``body_text``; the verifier slices the corpus itself. This makes
fabrication impossible by construction and stops the model from silently
repairing ASR while transcribing.

``llm`` is injected so the stage is testable offline with a canned queue.
"""

from __future__ import annotations

import json
from typing import Callable, List, Optional

from .corpus import resolve_timestamp
from .models import Candidate, Citation, LessonRecord, Rule, Span

PROMPT_TEMPLATE = """You are extracting investing RULES from a lecture transcript.

The transcript below is annotated with character offsets. Every 100 characters a
marker of the form <<offset:N>> gives the offset of the following character.

CRITICAL: do not quote or retype any text. Identify the exact character range
that states the rule and return its `start` and `end` offsets. The system
slices the transcript itself.

Choose `rule_key` from this controlled vocabulary only. If the rule fits none
of them, return null — do not invent a key:
{vocabulary}

Return JSON only:
{{"rules": [{{"tier": "graded"|"knockout", "kind": "threshold"|"range"|"boolean",
  "stage": "screen"|"sector"|"valuation"|"exit",
  "rule_key": "<from the vocabulary above, or null>",
  "operator": "gte"|"lte"|null, "value": <number|null>,
  "value_min": <number|null>, "value_max": <number|null>,
  "unit": "<string|null>", "conviction": "absolute"|"strong"|"preference",
  "start": <int>, "end": <int>}}]}}

Return an empty list if the passage states no rule. Prefer returning nothing
over guessing. The span you return must literally contain the number and the
comparative wording.

TRANSCRIPT:
{annotated}
"""


def _annotate(text: str, start: int, every: int = 100) -> str:
    parts = []
    for i in range(0, len(text), every):
        parts.append("<<offset:%d>>%s" % (start + i, text[i:i + every]))
    return "".join(parts)


def build_extract_prompt(
    lesson: LessonRecord,
    cand: Candidate,
    rule_keys: Optional[List[str]] = None,
) -> str:
    chunk = lesson.body_text[cand.span.start:cand.span.end]
    keys = rule_keys or []
    vocabulary = "\n".join("- " + k for k in keys) if keys else "(none yet — return null)"
    return PROMPT_TEMPLATE.format(
        annotated=_annotate(chunk, cand.span.start),
        vocabulary=vocabulary,
    )


def extract_rules(
    lesson: LessonRecord,
    cand: Candidate,
    llm: Callable[[str], str],
    rule_keys: Optional[List[str]] = None,
) -> List[Rule]:
    allowed = set(rule_keys or [])
    try:
        payload = json.loads(llm(build_extract_prompt(lesson, cand, rule_keys)))
    except (ValueError, TypeError):
        return []

    out: List[Rule] = []
    for raw in payload.get("rules", []) or []:
        try:
            start, end = int(raw["start"]), int(raw["end"])
        except (KeyError, TypeError, ValueError):
            continue
        if start < 0 or end > len(lesson.body_text) or end <= start:
            continue

        # Controlled vocabulary: an invented key is discarded, not accepted.
        key = raw.get("rule_key")
        if key not in allowed:
            key = None

        fields = {
            "rule_key": key,
            "tier": raw.get("tier", "graded"),
            "kind": raw.get("kind", "threshold"),
            "stage": raw.get("stage", "screen"),
            "operator": raw.get("operator"),
            "unit": raw.get("unit"),
            "conviction": raw.get("conviction", "preference"),
            "citations": [
                Citation(
                    lesson_id=lesson.lesson_id,
                    lesson_url=lesson.url,
                    timestamp=resolve_timestamp(lesson.body_text, start),
                    span=Span(start=start, end=end),
                    transcript_fidelity=lesson.transcript_fidelity,
                    text_hash=lesson.text_hash,
                )
            ],
        }
        if raw.get("value") is not None:
            fields["value"] = raw["value"]
        elif raw.get("value_min") is not None and raw.get("value_max") is not None:
            fields["value_range"] = {"min": raw["value_min"], "max": raw["value_max"]}

        try:
            out.append(Rule(**fields))
        except ValueError:
            continue
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_extract.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/soic_method/extract.py tests/test_soic_method_extract.py
git commit -m "feat(soic-method): offset-based LLM extractor with injectable seam"
```

---

### Task 8: Refuter — one well-fed adversary with a failure-mode checklist

**Files:**
- Create: `src/soic_method/refute.py`
- Test: `tests/test_soic_method_refute.py`

**Interfaces:**
- Consumes: `Rule`, `LessonRecord`
- Produces:
  - `CONTEXT_CHARS = 1500`
  - `FAILURE_MODES: List[str]`
  - `build_refute_prompt(rule: Rule, lesson: LessonRecord) -> str`
  - `refute(rule: Rule, lessons: Dict[str, LessonRecord], llm: Callable[[str], str]) -> bool` (True = survives)

**Design note:** one refuter with real context, not three votes. Three same-model refuters are correlated — the majority mostly measures sampling temperature. The budget buys ±1500 chars of surrounding transcript instead, which is what actually makes negation, reported speech and hypotheticals visible.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_refute.py
import json

from soic_method.models import Citation, LessonRecord, Rule, Span
from soic_method.refute import build_refute_prompt, refute

BODY = ("[00:00:05] " + "padding " * 300 +
        "\n[00:41:12] we don't even look at a business doing less than 18% ROC\n" +
        "trailing " * 300)
QUOTE = "we don't even look at a business doing less than 18% ROC"


def _lessons():
    return {"1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                              title="t", url="u", body_text=BODY, eligible=True)}


def _rule():
    s = BODY.index(QUOTE)
    return Rule(tier="graded", kind="threshold", stage="screen", operator="lte",
                value=18,
                citations=[Citation(lesson_id="1", lesson_url="u",
                                    timestamp="00:41:12",
                                    span=Span(start=s, end=s + len(QUOTE)))])


def test_prompt_carries_surrounding_context_not_just_the_span():
    p = build_refute_prompt(_rule(), _lessons()["1"])
    assert "padding" in p and "trailing" in p


def test_prompt_lists_named_failure_modes():
    p = build_refute_prompt(_rule(), _lessons()["1"])
    for mode in ("negation", "reported speech", "hypothetical", "coheren"):
        assert mode in p.lower()


def test_survives_when_refuter_says_not_refuted():
    llm = lambda p: json.dumps({"refuted": False, "reason": "clear statement"})
    assert refute(_rule(), _lessons(), llm) is True


def test_killed_when_refuter_refutes():
    llm = lambda p: json.dumps({"refuted": True, "reason": "reported speech"})
    assert refute(_rule(), _lessons(), llm) is False


def test_fails_closed_on_malformed_output():
    # Ambiguity must fail closed — a broken refuter must not wave rules through.
    assert refute(_rule(), _lessons(), lambda p: "garbage") is False


def test_fails_closed_on_unknown_lesson():
    assert refute(_rule(), {}, lambda p: json.dumps({"refuted": False})) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_refute.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.refute'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/refute.py
"""Gate 2 — adversarial refutation.

ONE refuter, well fed. Three same-model refuters are correlated rather than
independent, so a majority vote largely measures sampling temperature; the
budget is better spent on context, which is what makes quote-mining visible.

Fails CLOSED: any malformed response, missing lesson or ambiguity refutes.
"""

from __future__ import annotations

import json
from typing import Callable, Dict, List

from .models import LessonRecord, Rule

CONTEXT_CHARS = 1500

FAILURE_MODES: List[str] = [
    "negation or retraction — the speaker states the rule only to reject it",
    "reported speech — the speaker describes what OTHER people do or believe",
    "hypothetical or arithmetic illustration rather than a stated rule",
    "company-specific aside being generalised into a universal rule",
    "a read-aloud member question rather than the instructor's own view",
    "the value or comparative direction is not actually supported by context",
    "incoherence — the span is too ASR-garbled to support any rule at all",
]

PROMPT_TEMPLATE = """You are trying to REFUTE a proposed investing rule.

PROPOSED RULE:
{rule}

THE SPAN IT CLAIMS AS EVIDENCE:
{span}

SURROUNDING TRANSCRIPT (the span is inside this):
{context}

Argue against the rule. Check each failure mode:
{modes}

Note the transcript is auto-generated and degraded: numbers, company names and
whole sentences are sometimes corrupted. If the span is too garbled to clearly
support the rule, refute it.

Default to refuted when uncertain.

Return JSON only: {{"refuted": true|false, "reason": "<short>"}}
"""


def build_refute_prompt(rule: Rule, lesson: LessonRecord) -> str:
    cit = rule.citations[0]
    span = lesson.body_text[cit.span.start:cit.span.end]
    lo = max(0, cit.span.start - CONTEXT_CHARS)
    hi = min(len(lesson.body_text), cit.span.end + CONTEXT_CHARS)
    summary = rule.model_dump(include={"tier", "kind", "stage", "operator",
                                       "value", "value_range", "unit",
                                       "conviction"})
    return PROMPT_TEMPLATE.format(
        rule=json.dumps(summary, default=str),
        span=span,
        context=lesson.body_text[lo:hi],
        modes="\n".join("- " + m for m in FAILURE_MODES),
    )


def refute(
    rule: Rule,
    lessons: Dict[str, LessonRecord],
    llm: Callable[[str], str],
) -> bool:
    """Return True if the rule SURVIVES refutation."""
    if not rule.citations:
        return False
    lesson = lessons.get(rule.citations[0].lesson_id)
    if lesson is None:
        return False
    try:
        payload = json.loads(llm(build_refute_prompt(rule, lesson)))
    except (ValueError, TypeError):
        return False           # fail closed
    if not isinstance(payload, dict) or "refuted" not in payload:
        return False           # fail closed
    return payload.get("refuted") is False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_refute.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add src/soic_method/refute.py tests/test_soic_method_refute.py
git commit -m "feat(soic-method): Gate 2 refuter with context window, fails closed"
```

---

### Task 9: Reconciler — grouping, scope attestation, conflict-by-default, merge, resolutions

**Files:**
- Create: `src/soic_method/reconcile.py`
- Test: `tests/test_soic_method_reconcile.py`

**Interfaces:**
- Consumes: `Rule`, `LessonRecord`, `verify_rule`
- Produces:
  - `resolution_key(rule: Rule) -> str` — `"<rule_key>|<sorted values>"`, quote-independent
  - `merge_agreeing(rules: List[Rule]) -> Rule`
  - `classify_group(rules: List[Rule], lessons) -> Tuple[str, List[Rule]]` → `("merged"|"variants"|"conflict", rules)`
  - `reconcile(rules, lessons, resolutions: Dict[str, dict]) -> ReconcileOutput`

**Two decisions this encodes:**
1. **Conflict is the default.** Scoped-variant requires the scope claim to carry its own attesting span that passes `verify_rule`. Previously "variant" was free and "conflict" cost a human, so an LLM would always find a distinguishing context and launder a real contradiction into two active rules.
2. **The resolutions join key is `(rule_key, sorted value set)`** — content-stable. Keying on quotes or generated ids would break the join whenever a re-run shifted a span, silently discarding accumulated human judgement.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_reconcile.py
from soic_method.models import Citation, LessonRecord, Rule, ScopeAttestation, Span
from soic_method.reconcile import (
    classify_group,
    merge_agreeing,
    reconcile,
    resolution_key,
)

BODY = ("[00:00:05] padding padding padding padding padding padding padding\n"
        "[00:41:12] we don't even look at a business doing less than 18% ROC ok\n"
        "[00:50:00] in capital light businesses like exchanges we want much more\n")
QUOTE = "we don't even look at a business doing less than 18% ROC ok"
SCOPE_QUOTE = "in capital light businesses like exchanges we want much more"


def _lessons():
    return {"1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                              title="t", url="u", body_text=BODY,
                              text_hash="h", eligible=True)}


def _cit(text):
    s = BODY.index(text)
    return Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                    span=Span(start=s, end=s + len(text)), text_hash="h")


def _rule(value, key="screen.roc.floor", scope=None, attest=None):
    return Rule(tier="graded", kind="threshold", stage="screen", operator="lte",
                value=value, rule_key=key, scope=scope or {},
                scope_attestation=attest, citations=[_cit(QUOTE)])


def test_resolution_key_is_quote_independent():
    a = _rule(18)
    b = _rule(18)
    b.citations[0].span = Span(start=0, end=60)   # span moved
    assert resolution_key(a) == resolution_key(b)


def test_agreeing_rules_merge_into_one_with_many_citations():
    merged = merge_agreeing([_rule(18), _rule(18)])
    assert len(merged.citations) == 2
    assert merged.value == 18


def test_same_value_group_is_merged():
    verdict, rules = classify_group([_rule(18), _rule(18)], _lessons())
    assert verdict == "merged"
    assert len(rules) == 1


def test_different_values_without_attested_scope_is_a_conflict():
    verdict, _ = classify_group([_rule(18), _rule(15)], _lessons())
    assert verdict == "conflict"


def test_different_values_with_unattested_scope_is_still_a_conflict():
    # Scope claimed but with no evidence span — the laundering path.
    a = _rule(18, scope={"business_type": "capital_light"})
    b = _rule(15, scope={"business_type": "cyclical"})
    verdict, _ = classify_group([a, b], _lessons())
    assert verdict == "conflict"


def test_different_values_with_verified_scope_attestation_are_variants():
    s = BODY.index(SCOPE_QUOTE)
    attest = ScopeAttestation(lesson_id="1",
                              span=Span(start=s, end=s + len(SCOPE_QUOTE)))
    a = _rule(18, scope={"business_type": "capital_light"}, attest=attest)
    b = _rule(15, scope={"business_type": "cyclical"}, attest=attest)
    verdict, rules = classify_group([a, b], _lessons())
    assert verdict == "variants"
    assert len(rules) == 2


def test_reconcile_routes_conflicts_to_the_queue():
    out = reconcile([_rule(18), _rule(15)], _lessons(), {})
    assert len(out.conflicts) == 1
    assert out.rules == []


def test_resolutions_are_applied_and_survive_span_shifts():
    a, b = _rule(18), _rule(15)
    a.citations[0].span = Span(start=0, end=60)     # spans differ from build time
    key = resolution_key(a)
    out = reconcile([a, b], _lessons(), {key: {"keep": 18}})
    assert out.conflicts == []
    assert len(out.rules) == 1
    assert out.rules[0].value == 18


def test_rules_without_a_key_never_group():
    out = reconcile([_rule(18, key=None), _rule(15, key=None)], _lessons(), {})
    assert out.conflicts == []
    assert len(out.drafts) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_reconcile.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.reconcile'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_method/reconcile.py
"""Gate 3 — grouping, scope attestation, conflict detection, merge.

CONFLICT IS THE DEFAULT. A scoped-variant classification requires the scope
distinction to carry its own attesting span that passes the same verifier. The
earlier design made "variant" the free outcome and "conflict" the expensive
one, which biased an LLM toward always finding a distinguishing context and
laundering real contradictions into two happily-active rules.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .models import LessonRecord, Rule
from .verify import verify_rule


class ReconcileOutput(BaseModel):
    rules: List[Rule] = Field(default_factory=list)
    drafts: List[Rule] = Field(default_factory=list)
    conflicts: List[List[Rule]] = Field(default_factory=list)


def _values_of(rule: Rule) -> List[float]:
    if rule.value is not None:
        return [rule.value]
    if rule.value_range is not None:
        return [rule.value_range.min, rule.value_range.max]
    return []


def resolution_key(rule: Rule) -> str:
    """Content-stable join key: (rule_key, sorted value set).

    Deliberately independent of quotes, spans and generated ids so a re-run
    that shifts offsets does not silently orphan a human resolution.
    """
    vals = ",".join(str(v) for v in sorted(_values_of(rule)))
    return "%s|%s" % (rule.rule_key, vals)


def merge_agreeing(rules: List[Rule]) -> Rule:
    """One rule, many citations, corroboration = distinct attesting lessons."""
    base = rules[0]
    cits = list(base.citations)
    for r in rules[1:]:
        cits.extend(r.citations)
    lessons = {c.lesson_id for c in cits}
    return base.model_copy(update={"citations": cits, "corroboration": len(lessons)})


def _scope_is_attested(rule: Rule, lessons: Dict[str, LessonRecord]) -> bool:
    att = rule.scope_attestation
    if att is None or not rule.scope or not rule.citations:
        return False
    probe = rule.model_copy(update={
        "citations": [rule.citations[0].model_copy(update={"span": att.span})],
        "value": None, "value_range": None, "operator": None,
    })
    return verify_rule(probe, lessons).ok


def classify_group(
    rules: List[Rule], lessons: Dict[str, LessonRecord]
) -> Tuple[str, List[Rule]]:
    distinct = {tuple(sorted(_values_of(r))) for r in rules}
    if len(distinct) <= 1:
        return "merged", [merge_agreeing(rules)]
    if all(_scope_is_attested(r, lessons) for r in rules):
        return "variants", rules
    return "conflict", rules


def reconcile(
    rules: List[Rule],
    lessons: Dict[str, LessonRecord],
    resolutions: Dict[str, dict],
) -> ReconcileOutput:
    out = ReconcileOutput()
    groups: Dict[str, List[Rule]] = defaultdict(list)

    for r in rules:
        if r.rule_key is None:
            out.drafts.append(r)      # unnamed rules never group
        else:
            groups[r.rule_key].append(r)

    for _key, group in sorted(groups.items()):
        verdict, result = classify_group(group, lessons)
        if verdict != "conflict":
            out.rules.extend(result)
            continue

        resolved = _apply_resolution(group, resolutions)
        if resolved is not None:
            out.rules.append(resolved)
        else:
            out.conflicts.append(group)
    return out


def _apply_resolution(
    group: List[Rule], resolutions: Dict[str, dict]
) -> Optional[Rule]:
    for r in group:
        entry = resolutions.get(resolution_key(r))
        if entry and entry.get("keep") in _values_of(r):
            return r
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_soic_method_reconcile.py -v`
Expected: PASS (9 passed)

- [ ] **Step 5: Commit**

```bash
git add src/soic_method/reconcile.py tests/test_soic_method_reconcile.py
git commit -m "feat(soic-method): Gate 3 reconciler, conflict-by-default with attested scope"
```

---

### Task 10: Publisher and CLI

**Files:**
- Create: `src/soic_method/publish.py`, `src/soic_method/cli.py`
- Test: `tests/test_soic_method_publish.py`

**Interfaces:**
- Consumes: `ReconcileOutput`, `Rule`, `LessonRecord`
- Produces:
  - `write_bundle(out: ReconcileOutput, lessons, dest: Path) -> None`
  - Typer app with `route`, `verify`, `publish` commands

- [ ] **Step 1: Write the failing test**

```python
# tests/test_soic_method_publish.py
import yaml

from soic_method.models import Citation, LessonRecord, Rule, Span
from soic_method.publish import write_bundle
from soic_method.reconcile import ReconcileOutput


def _rule(tier, value=18):
    return Rule(tier=tier, kind="threshold", stage="screen", operator="lte",
                value=value, rule_key="screen.roc.floor", status="active",
                citations=[Citation(lesson_id="1", lesson_url="u",
                                    timestamp="00:41:12",
                                    span=Span(start=0, end=60), text_hash="h")])


def _lessons():
    return {"1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                              title="t", url="u", body_text="b", text_hash="h")}


def test_tiers_are_written_to_separate_files(tmp_path):
    out = ReconcileOutput(rules=[_rule("knockout"), _rule("graded", 15)])
    write_bundle(out, _lessons(), tmp_path)
    knock = yaml.safe_load((tmp_path / "knockouts.yaml").read_text())
    graded = yaml.safe_load((tmp_path / "graded.yaml").read_text())
    assert len(knock) == 1 and len(graded) == 1


def test_snapshot_records_corpus_hashes(tmp_path):
    write_bundle(ReconcileOutput(rules=[_rule("graded")]), _lessons(), tmp_path)
    snap = yaml.safe_load((tmp_path / "SNAPSHOT").read_text())
    assert snap["1"] == "h"


def test_conflicts_are_written_for_review(tmp_path):
    out = ReconcileOutput(conflicts=[[_rule("graded", 18), _rule("graded", 15)]])
    write_bundle(out, _lessons(), tmp_path)
    conflicts = yaml.safe_load((tmp_path / "conflicts.open.yaml").read_text())
    assert len(conflicts) == 1
    assert len(conflicts[0]) == 2


def test_gaps_lists_unbound_rules(tmp_path):
    write_bundle(ReconcileOutput(rules=[_rule("graded")]), _lessons(), tmp_path)
    assert "screen.roc.floor" in (tmp_path / "gaps.md").read_text()


def test_bundle_never_emits_a_bound_binding(tmp_path):
    write_bundle(ReconcileOutput(rules=[_rule("graded")]), _lessons(), tmp_path)
    text = (tmp_path / "graded.yaml").read_text()
    assert "bound" in text            # the word appears as "unbound"
    assert "status: bound" not in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_soic_method_publish.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_method.publish'`

- [ ] **Step 3: Write the publisher**

```python
# src/soic_method/publish.py
"""Emit the spec bundle.

Two tiers land in separate files because they execute differently: knockouts
are hard exclusions, graded rules rank and flag but never exclude.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from .models import LessonRecord, Rule
from .reconcile import ReconcileOutput

GAPS_HEADER = """# Data gaps

Rules SOIC states and the verifier accepted, which cannot execute because the
platform has no field to run them against. Sourced from the method, not guessed.

"""


def _dump(rules: List[Rule]) -> str:
    return yaml.safe_dump(
        [r.model_dump(mode="json", exclude_none=True) for r in rules],
        sort_keys=False, allow_unicode=True,
    )


def write_bundle(
    out: ReconcileOutput, lessons: Dict[str, LessonRecord], dest: Path
) -> None:
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    knockouts = [r for r in out.rules if r.tier == "knockout"]
    graded = [r for r in out.rules if r.tier != "knockout"]

    (dest / "knockouts.yaml").write_text(_dump(knockouts), encoding="utf-8")
    (dest / "graded.yaml").write_text(_dump(graded), encoding="utf-8")
    (dest / "drafts.yaml").write_text(_dump(out.drafts), encoding="utf-8")

    (dest / "conflicts.open.yaml").write_text(
        yaml.safe_dump(
            [[r.model_dump(mode="json", exclude_none=True) for r in g]
             for g in out.conflicts],
            sort_keys=False, allow_unicode=True,
        ),
        encoding="utf-8",
    )

    # Corpus integrity: a re-capture with drifted ASR must hard-fail rather
    # than silently re-point citations at moved audio.
    (dest / "SNAPSHOT").write_text(
        yaml.safe_dump({lid: l.text_hash for lid, l in sorted(lessons.items())},
                       sort_keys=False),
        encoding="utf-8",
    )

    unbound = [r for r in out.rules if r.binding.status != "bound"]
    lines = [GAPS_HEADER]
    for r in unbound:
        lines.append("- `%s` (%s) — %s\n" % (r.rule_key, r.tier, r.binding.status))
    (dest / "gaps.md").write_text("".join(lines), encoding="utf-8")
```

- [ ] **Step 4: Write the CLI**

```python
# src/soic_method/cli.py
"""Typer CLI for the SOIC method extraction pipeline."""

from __future__ import annotations

from pathlib import Path

import typer

from .corpus import load_corpus
from .eligibility import apply_eligibility, load_eligibility
from .publish import write_bundle
from .reconcile import ReconcileOutput
from .router import route

app = typer.Typer(help="Extract SOIC's investing method into an executable spec.")

DEFAULT_CORPUS = Path("data/content.json")
DEFAULT_CONFIG = Path("configs/course_eligibility.yaml")


@app.command("route")
def route_cmd(
    corpus: Path = typer.Option(DEFAULT_CORPUS, help="content.json path"),
    config: Path = typer.Option(DEFAULT_CONFIG, help="eligibility config"),
) -> None:
    """Report candidate spans per eligible lesson."""
    lessons = apply_eligibility(load_corpus(corpus), load_eligibility(config))
    eligible = [l for l in lessons if l.eligible]
    cands = route(lessons)
    typer.echo("lessons=%d eligible=%d candidates=%d"
               % (len(lessons), len(eligible), len(cands)))


@app.command("publish")
def publish_cmd(
    dest: Path = typer.Option(..., help="bundle output directory"),
    corpus: Path = typer.Option(DEFAULT_CORPUS),
    config: Path = typer.Option(DEFAULT_CONFIG),
) -> None:
    """Write an (empty-until-extracted) bundle skeleton plus the SNAPSHOT."""
    lessons = apply_eligibility(load_corpus(corpus), load_eligibility(config))
    write_bundle(ReconcileOutput(), {l.lesson_id: l for l in lessons}, dest)
    typer.echo("wrote bundle to %s" % dest)


if __name__ == "__main__":
    app()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_soic_method_publish.py -v`
Expected: PASS (5 passed)

- [ ] **Step 6: Verify the CLI is wired**

Run: `pip install -e . && soic-method route`
Expected: a line like `lessons=437 eligible=NNN candidates=NNN`

- [ ] **Step 7: Commit**

```bash
git add src/soic_method/publish.py src/soic_method/cli.py tests/test_soic_method_publish.py
git commit -m "feat(soic-method): bundle publisher and Typer CLI"
```

---

### Task 11: Pilot run and report

**Files:**
- Create: `docs/reviews/soic-method-pilot-report.md` (undated — it is revised in place across pilot iterations rather than superseded)
- Create: `configs/rule_keys.yaml` (produced by the bootstrap in Step 3)
- Modify: `configs/course_eligibility.yaml` (add the 40 L6 module classifications)

**Interfaces:**
- Consumes: every prior task
- Produces: the pilot report, and the go/no-go on full-corpus extraction

**Pilot slice:** Level 5's 4 lessons **plus** the L6 lessons backing `part-2-scalable-businesses`. Course-title-driven scoping is abandoned — the one existing wiki concept about screening cites a Level 6 module, not Level 5.

- [ ] **Step 1: Classify the 40 Level 6 modules**

Run:

```bash
python3 -c "
import json
d=json.load(open('data/content.json'))
for c in d['courses']:
    if c['title'].startswith('Level 6'):
        for m in c['modules']:
            print(m.get('title'))
"
```

For each module title, decide eligible/ineligible. The `-by-<person>` slug is a hint, not a guarantee — read all 40. Add every ineligible one to `excluded_modules` in `configs/course_eligibility.yaml`.

- [ ] **Step 2: Seed a synthetic conflict**

Before running, hand-write two rules with the same `rule_key`, different values, and no scope attestation into the extraction input. Pilot criterion 3 requires at least one conflict to flow end-to-end into `conflicts.open.yaml` — otherwise Gate 3 ships untested.

- [ ] **Step 3: Run the vocabulary bootstrap**

The first run has a near-empty `rule_keys.yaml`, so nearly everything lands as a draft and conflict detection would run over an empty set. Bootstrap explicitly:

1. Run extraction key-free; inspect `drafts.yaml`.
2. Cluster drafts by metric vocabulary.
3. Name the clusters; commit `configs/rule_keys.yaml`.
4. Re-run against the vocabulary.

- [ ] **Step 4: Record results against the falsifiable criteria**

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Ear-verification | n=10, oversampling digit-bearing rules, **verbatim courses only**. Zero failures. |
| 2 | Rejection rate | Reported **and** within 5–40%. |
| 3 | Gate 3 exercised | ≥1 seeded conflict reached `conflicts.open.yaml`. |
| 4 | Attribution | Zero rules from ineligible courses **or modules**. |
| 5 | Bindings | Bound/unbound split reported; `gaps.md` non-empty. |
| 6 | Acceptance | Human reads the draft rubric and recognizes the method. |

- [ ] **Step 5: Write the report and state the go/no-go**

Include actual token spend. State plainly if the honest conclusion is that a large `rules.yaml` is not extractable at acceptable fidelity, and that the real deliverable is a small knockout set plus well-cited rubrics — the pilot is designed to surface that rather than hide it.

- [ ] **Step 6: Commit**

```bash
git add configs/ docs/reviews/
git commit -m "docs(soic-method): pilot report and Level 6 module eligibility"
```

---

## Deferred to a follow-up plan

These are specified in the design but not built here, because the pipeline must prove itself on the pilot slice first:

- **Rubric generation and its citation gate** (citation per claim, 20% sampled span verification). Depends on pilot output telling us which stages have enough surviving material to write a rubric from.
- **`scopes.yaml` controlled vocabulary content.** The mechanism is built in Task 9; the vocabulary itself must be derived from what the pilot actually surfaces rather than invented up front.
- **The shoehorn tripwire** — flagging rules within a `rule_key` group whose spans share no metric vocabulary, catching the opposite bias to the bootstrap problem (once a vocabulary exists, models satisfice into the nearest key instead of returning null). Deferred because the "shares no metric vocabulary" threshold needs calibrating against real grouped output; guessing it now produces either noise or silence.
- **Full-corpus extraction.** Gated on the pilot go/no-go.
- **Publishing into `stock_analyzer` `configs/soic-method/`.** Requires the column inventory so bindings can move off `unbound`.

## Known limits of this plan

- **Gate 1 cannot catch misattributed meaning** — quote-mining, negation, reported speech and hypotheticals all pass it by design. That protection lives entirely in Task 8's refuter, which is a single LLM call. If the pilot shows the refuter missing these, the answer is a better failure-mode checklist, not more refuters.
- **`as_of` is never populated.** The schema carries it (Task 1) and the spec argues it is load-bearing for distinguishing regime-shift from contradiction, but the corpus has no reliable per-lesson recording date. Populating it needs a capture-side change to record lesson publication dates — out of scope here, and until then two rules from different market regimes will present as a conflict.
