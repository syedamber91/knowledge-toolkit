# Alex the Learner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An autonomous loop where the `alex` learner persona learns Apache Spark from the `vutr` wiki (closed-book), goes 0→100 over vutr's 16 Spark concepts, and captures the learning into `wiki/personas/alex/spark/` including a human-readable transcript.

**Architecture:** A new `src/persona_wiki/learn.py` module holds the loop, prompt builders, and capture logic behind the existing injectable LLM seam (`Callable[[str], str]`). It reads the read-only vutr Spark notes, drives teach→reflect→answer→score per concept, and writes Alex's own notes (his words + optional Mermaid), Q&A notes, an open-questions list, a mastery tracker, a transcript, plus `index.yaml`/`log.md` — all through the existing `storage`/`index`/`log`/`config` helpers. A `persona-wiki learn` CLI command runs it.

**Tech Stack:** Python 3.9+, Pydantic v2, Typer, PyYAML, pytest. Reuses `persona_wiki.storage`, `.index`, `.log`, `.config`, `.models`.

## Global Constraints

- **Repo:** all code lands in the **learning-vault repo** worktree `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault/.worktrees/persona-wiki-poc` on branch `persona-wiki-poc`. (The SOIC_Scraper repo only holds this spec/plan.)
- **Python:** `>=3.9` — no 3.10+ syntax; use `Optional[...]`/`List[...]`/`Dict[...]` from `typing`.
- **Offline tests:** the LLM is always an injected stub `Callable[[str], str]`. NEVER call the real `claude` CLI in a test (a nested `claude -p` returns 401 in-session).
- **venv OUTSIDE iCloud:** `python3 -m venv /tmp/pw-venv && /tmp/pw-venv/bin/pip install -e ".[dev]"`. Run tests as `/tmp/pw-venv/bin/python -m pytest tests/persona_wiki -v`.
- **Never write `f"{kind}s"`** for atomic dirs — use `persona_wiki.index.atomic_dir(kind)` (`entity`→`entities`, `concept`→`concepts`).
- **All writes stay under `wiki/personas/alex/spark/`** (the learn root). Reuse `storage.write_note`'s path guard for notes; use the local `_safe_write` guard (Task 5) for the raw docs (mastery/open-questions/transcript).
- **Closed-book:** teach/answer/score prompts are fed ONLY the relevant vutr note text. A claim not in the source is flagged and routed to `open-questions.md`, never asserted as fact in a concept note.
- **Determinism:** every function that stamps a date takes an explicit `stamp: str`; tests pass an explicit stamp.
- **Plan file** lives in SOIC_Scraper; the code it describes is written in the learning-vault worktree. All `git` commands target that worktree.

## Existing interfaces this plan consumes (verified)

```python
# persona_wiki.storage
slugify(text) -> str
dump_note(fm: NoteFrontmatter, body: str) -> str
parse_note(text: str) -> Tuple[NoteFrontmatter, str]
write_note(root: Path, rel_path: str, fm: NoteFrontmatter, body: str) -> Path   # path-guarded
# persona_wiki.index
atomic_dir(kind) -> str
load_index(root) -> WikiIndex ; save_index(root, index) -> Path
register_atomic(index, kind, slug, topic, stamp) -> None
# persona_wiki.log
log_ingest(log_path: Path, total: int, summary: str, stamp: str) -> bool
# persona_wiki.config
persona_root(vault_dir: Path, persona: str) -> Path      # <vault>/wiki/personas/<persona>
# persona_wiki.models.NoteFrontmatter fields:
#   persona, kind, sources[], last_updated, qc="passed", qc_reason, topic, slug, topics[]
```

---

## File Structure

```
src/persona_wiki/
  models.py     # MODIFY: add optional learner/source_note/mastery fields to NoteFrontmatter
  learn.py      # CREATE: SPARK_ORDER, source loader, prompt builders, run_concept,
                #         capture (concept/qa/open-questions/mastery/transcript), learn() loop
  cli.py        # MODIFY: add the `learn` command
tests/persona_wiki/
  test_learn.py # CREATE: all learn tests
```

---

### Task 1: Frontmatter fields + Spark order + source loader

**Files:**
- Modify: `src/persona_wiki/models.py` (NoteFrontmatter)
- Create: `src/persona_wiki/learn.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Produces:
  - `NoteFrontmatter` gains `learner: Optional[str] = None`, `source_note: Optional[str] = None`, `mastery: Optional[str] = None`.
  - `SPARK_ORDER: List[str]` (the 16 slugs, pedagogical order).
  - `load_topic_concepts(vutr_root: Path, topic: str) -> Dict[str, str]` — `{slug: note_body}` for every atomic note whose frontmatter `topics` includes `topic`.
  - `concept_order(available: Dict[str, str]) -> List[str]` — `SPARK_ORDER` filtered to `available`, then any remaining available slugs appended (sorted).

- [ ] **Step 1: Write the failing test**

Add to `tests/persona_wiki/test_learn.py`:
```python
from pathlib import Path

from persona_wiki.models import NoteFrontmatter
from persona_wiki.storage import write_note
from persona_wiki.learn import SPARK_ORDER, load_topic_concepts, concept_order


def _seed_vutr(tmp_path):
    root = tmp_path / "wiki/personas/vutr"
    for slug, topics, body in [
        ("rdd", ["spark"], "An RDD is a resilient distributed dataset."),
        ("kafka-origin", ["kafka"], "Kafka came from LinkedIn."),
        ("brand-new", ["spark"], "A spark thing not in the static order."),
    ]:
        write_note(root, f"entities/{slug}.md",
                   NoteFrontmatter(persona="vutr", kind="entity", slug=slug,
                                   sources=["persona-snapshot"], last_updated="2026-07-09",
                                   topics=topics), body)
    return root


def test_frontmatter_has_learner_fields():
    fm = NoteFrontmatter(persona="alex", kind="concept", slug="rdd",
                         last_updated="2026-07-09", learner="alex",
                         source_note="rdd", mastery="mastered")
    assert fm.learner == "alex" and fm.source_note == "rdd" and fm.mastery == "mastered"


def test_load_topic_concepts_only_that_topic(tmp_path):
    root = _seed_vutr(tmp_path)
    got = load_topic_concepts(root, "spark")
    assert set(got) == {"rdd", "brand-new"}
    assert "resilient distributed dataset" in got["rdd"]


def test_concept_order_uses_static_then_appends_unknowns(tmp_path):
    root = _seed_vutr(tmp_path)
    order = concept_order(load_topic_concepts(root, "spark"))
    assert order[0] == "rdd"              # rdd is early in SPARK_ORDER; brand-new is not
    assert order[-1] == "brand-new"       # unknown slug appended at the end
    assert "spark-origin" not in order    # not available in this fixture


def test_spark_order_is_16_unique_slugs():
    assert len(SPARK_ORDER) == 16 and len(set(SPARK_ORDER)) == 16
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_wiki.learn'`.

- [ ] **Step 3: Add the frontmatter fields**

In `src/persona_wiki/models.py`, inside `NoteFrontmatter`, after the `topics` field add:
```python
    learner: Optional[str] = None       # learner-persona notes (Alex)
    source_note: Optional[str] = None   # the vutr slug this understanding came from
    mastery: Optional[str] = None       # "learning" | "familiar" | "mastered"
```

- [ ] **Step 4: Create `learn.py` with order + loader**

Create `src/persona_wiki/learn.py`:
```python
"""Alex the learner: an autonomous loop that learns a vutr topic (Spark) from the
vutr wiki, closed-book, and captures the learning into Alex's own growing wiki."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .index import atomic_dir
from .storage import parse_note

SPARK_ORDER: List[str] = [
    "spark-origin", "rdd", "lazy-evaluation", "catalyst-optimizer",
    "adaptive-query-execution", "executor-memory-model", "shuffle-writes-to-disk",
    "data-skew-oom", "sort-merge-join", "shuffle-hash-join", "data-locality",
    "jvm-object-overhead", "pyspark", "spark-structured-streaming", "photon",
    "remote-shuffle-service",
]


def load_topic_concepts(vutr_root: Path, topic: str) -> Dict[str, str]:
    """Return {slug: note_body} for every vutr atomic note tagged with ``topic``."""
    out: Dict[str, str] = {}
    for kind in ("entity", "concept"):
        d = vutr_root / atomic_dir(kind)
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            fm, body = parse_note(p.read_text(encoding="utf-8"))
            if topic in (fm.topics or []):
                out[p.stem] = body
    return out


def concept_order(available: Dict[str, str]) -> List[str]:
    """SPARK_ORDER restricted to available slugs, then any extra slugs appended."""
    ordered = [s for s in SPARK_ORDER if s in available]
    extra = sorted(s for s in available if s not in SPARK_ORDER)
    return ordered + extra
```

- [ ] **Step 5: Run — expect pass**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -v`
Expected: PASS (4 passed).

- [ ] **Step 6: Commit**

```bash
cd "$WT"
git add src/persona_wiki/models.py src/persona_wiki/learn.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): frontmatter learner fields + Spark concept order + source loader"
```

---

### Task 2: Prompt builders + tolerant JSON parse

**Files:**
- Modify: `src/persona_wiki/learn.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `build_teach_prompt(slug, note_text) -> str`
  - `build_reflect_prompt(slug, explanation) -> str`
  - `build_answer_prompt(slug, note_text, questions: List[str]) -> str`
  - `build_score_prompt(slug, note_text, restatement) -> str`
  - `parse_json(raw: str) -> dict` (strips a ```json fence; raises `ValueError` on non-JSON)

- [ ] **Step 1: Write the failing test**

Append to `tests/persona_wiki/test_learn.py`:
```python
import pytest
from persona_wiki.learn import (
    build_teach_prompt, build_reflect_prompt, build_answer_prompt,
    build_score_prompt, parse_json,
)


def test_teach_prompt_is_closed_book_and_15yo():
    p = build_teach_prompt("rdd", "An RDD has 5 properties.")
    assert "An RDD has 5 properties." in p
    assert "15-year-old" in p or "15 year old" in p
    assert "only" in p.lower() and "mermaid" in p.lower()


def test_reflect_prompt_asks_for_restatement_and_questions_json():
    p = build_reflect_prompt("rdd", "EXPLANATION HERE")
    assert "EXPLANATION HERE" in p
    assert "restatement" in p and "questions" in p and "mermaid" in p


def test_answer_prompt_carries_questions_and_note():
    p = build_answer_prompt("rdd", "NOTE TEXT", ["why lazy?", "what is a DAG?"])
    assert "NOTE TEXT" in p and "why lazy?" in p and "gaps" in p


def test_score_prompt_asks_for_level_and_unverified():
    p = build_score_prompt("rdd", "NOTE", "RESTATEMENT")
    assert "RESTATEMENT" in p and "NOTE" in p
    assert "mastered" in p and "unverified" in p


def test_parse_json_tolerates_fence_and_raises_on_garbage():
    assert parse_json('```json\n{"level": "mastered"}\n```')["level"] == "mastered"
    with pytest.raises(ValueError):
        parse_json("not json")
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "prompt or parse_json" -v`
Expected: FAIL (ImportError on the new names).

- [ ] **Step 3: Implement the builders + parser**

Add to `src/persona_wiki/learn.py` (imports at top: add `import json`, `import re`):
```python
import json
import re

_FENCE_RE = re.compile(r"^```[a-zA-Z]*\n(.*)\n```$", re.DOTALL)


def parse_json(raw: str) -> dict:
    """Parse a JSON object from LLM output, tolerating a ```json fence."""
    s = raw.strip()
    m = _FENCE_RE.match(s)
    if m:
        s = m.group(1).strip()
    try:
        data = json.loads(s)
    except json.JSONDecodeError as exc:
        raise ValueError(f"expected JSON, got: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    return data


def build_teach_prompt(slug: str, note_text: str) -> str:
    return (
        f"You are Vu Trinh teaching a curious 15-year-old about '{slug}'. Explain it "
        "in plain language a 15-year-old could follow, using ONLY the facts in the "
        "NOTE below — do not add outside facts. Add a simple ```mermaid diagram ONLY "
        "if it genuinely clarifies a flow or structure; otherwise omit it. Return the "
        "explanation as Markdown (no JSON).\n\n<<<NOTE\n" + note_text + "\nNOTE\n"
    )


def build_reflect_prompt(slug: str, explanation: str) -> str:
    return (
        f"You are Alex, a 15-year-old learner, hearing about '{slug}'. In your own "
        "voice ('wait, so… okay but then why…'), restate what you understood and note "
        "what still confuses you. Return ONLY JSON: "
        '{"restatement": "<your words>", "questions": ["<1-2 follow-ups>"], '
        '"mermaid": "<a simple mermaid diagram of your mental model, or empty string>"}'
        ".\n\n<<<EXPLANATION\n" + explanation + "\nEXPLANATION\n"
    )


def build_answer_prompt(slug: str, note_text: str, questions: List[str]) -> str:
    qs = "\n".join(f"- {q}" for q in questions) or "- (none)"
    return (
        f"You are Vu Trinh answering Alex's follow-ups about '{slug}', using ONLY the "
        "NOTE below. If a question cannot be answered from the NOTE, put it in gaps "
        "instead of guessing. Return ONLY JSON: "
        '{"answers": ["<grounded answer>"], "gaps": ["<question the note cannot answer>"]}'
        "\n\n<<<QUESTIONS\n" + qs + "\nQUESTIONS\n\n<<<NOTE\n" + note_text + "\nNOTE\n"
    )


def build_score_prompt(slug: str, note_text: str, restatement: str) -> str:
    return (
        f"You are Vu Trinh judging whether Alex has learned '{slug}'. Compare his "
        "RESTATEMENT against the NOTE. Level is 'mastered' if it covers the note's key "
        "points, 'familiar' if partial, 'learning' if shallow. Also list any claim in "
        "the restatement that is NOT supported by the NOTE. Return ONLY JSON: "
        '{"level": "mastered|familiar|learning", "reason": "<one sentence>", '
        '"unverified": ["<unsupported claim>"]}'
        "\n\n<<<RESTATEMENT\n" + restatement + "\nRESTATEMENT\n\n<<<NOTE\n"
        + note_text + "\nNOTE\n"
    )
```

- [ ] **Step 4: Run — expect pass**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "prompt or parse_json" -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/learn.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): closed-book teach/reflect/answer/score prompts + json parse"
```

---

### Task 3: `run_concept` — one concept's LLM exchange

**Files:**
- Modify: `src/persona_wiki/learn.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Consumes: prompt builders + `parse_json` (Task 2); `LLMFn` from `.llm`.
- Produces:
  - `@dataclass ConceptResult` with: `slug, explanation, restatement, questions(List[str]), mermaid, answers(List[str]), gaps(List[str]), unverified(List[str]), level, reason`.
  - `run_concept(slug, note_text, llm) -> ConceptResult` — runs teach→reflect→answer→score; raises `ValueError` if any structured step returns non-JSON.

- [ ] **Step 1: Write the failing test**

Append to `tests/persona_wiki/test_learn.py`:
```python
import json as _json
from persona_wiki.learn import run_concept, ConceptResult


def _fake_llm(explanation="RDDs are lazy.", level="mastered", questions=("why lazy?",),
              mermaid="graph TD; A-->B", gaps=(), unverified=()):
    def llm(prompt):
        if "judging whether Alex" in prompt:                      # score
            return _json.dumps({"level": level, "reason": "covered it",
                                "unverified": list(unverified)})
        if "answering Alex's follow-ups" in prompt:               # answer
            return _json.dumps({"answers": ["because it builds a DAG"], "gaps": list(gaps)})
        if "You are Alex" in prompt:                              # reflect
            return _json.dumps({"restatement": "RDD = lazy dataset",
                                "questions": list(questions), "mermaid": mermaid})
        return explanation                                        # teach (plain text)
    return llm


def test_run_concept_assembles_result():
    r = run_concept("rdd", "An RDD is lazy.", _fake_llm())
    assert isinstance(r, ConceptResult)
    assert r.level == "mastered" and r.restatement == "RDD = lazy dataset"
    assert r.questions == ["why lazy?"] and r.mermaid == "graph TD; A-->B"
    assert r.answers == ["because it builds a DAG"]


def test_run_concept_raises_on_bad_json():
    def llm(prompt):
        if "You are Alex" in prompt:
            return "NOT JSON"     # reflect step returns garbage
        return "explanation"
    with pytest.raises(ValueError):
        run_concept("rdd", "note", llm)
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k run_concept -v`
Expected: FAIL (ImportError on `run_concept`/`ConceptResult`).

- [ ] **Step 3: Implement**

Add to `src/persona_wiki/learn.py` (add `from dataclasses import dataclass, field` and `from .llm import LLMFn` to imports):
```python
from dataclasses import dataclass, field
from .llm import LLMFn


@dataclass
class ConceptResult:
    slug: str
    explanation: str
    restatement: str
    questions: List[str] = field(default_factory=list)
    mermaid: str = ""
    answers: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    unverified: List[str] = field(default_factory=list)
    level: str = "learning"
    reason: str = ""


def run_concept(slug: str, note_text: str, llm: LLMFn) -> ConceptResult:
    explanation = llm(build_teach_prompt(slug, note_text))
    reflect = parse_json(llm(build_reflect_prompt(slug, explanation)))
    questions = [str(q) for q in reflect.get("questions", [])]
    answer = parse_json(llm(build_answer_prompt(slug, note_text, questions)))
    score = parse_json(llm(build_score_prompt(slug, note_text, reflect.get("restatement", ""))))
    return ConceptResult(
        slug=slug,
        explanation=explanation,
        restatement=str(reflect.get("restatement", "")),
        questions=questions,
        mermaid=str(reflect.get("mermaid", "") or ""),
        answers=[str(a) for a in answer.get("answers", [])],
        gaps=[str(g) for g in answer.get("gaps", [])],
        unverified=[str(u) for u in score.get("unverified", [])],
        level=str(score.get("level", "learning")),
        reason=str(score.get("reason", "")),
    )
```

- [ ] **Step 4: Run — expect pass**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k run_concept -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/learn.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): run_concept ties teach/reflect/answer/score into a result"
```

---

### Task 4: Render + write the concept note and Q&A note

**Files:**
- Modify: `src/persona_wiki/learn.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Consumes: `ConceptResult` (Task 3); `NoteFrontmatter`, `storage.write_note`, `index.register_atomic`.
- Produces:
  - `render_concept_body(r: ConceptResult) -> str` — Alex's restatement + a fenced ```mermaid block iff `r.mermaid` is non-empty + a `Source: [[<slug>]]` line.
  - `write_concept_note(learn_root, topic, r, stamp) -> Path`
  - `write_qa_note(learn_root, order_idx, r, stamp) -> Path` — file `qa/<nnn>-<slug>.md` (nnn zero-padded).

- [ ] **Step 1: Write the failing test**

Append:
```python
from persona_wiki.learn import render_concept_body, write_concept_note, write_qa_note
from persona_wiki.storage import parse_note as _pn


def _result(mermaid="graph TD; A-->B"):
    return ConceptResult(slug="rdd", explanation="e", restatement="An RDD is a lazy dataset.",
                         questions=["why lazy?"], mermaid=mermaid, answers=["builds a DAG"],
                         gaps=[], unverified=[], level="mastered", reason="ok")


def test_concept_body_includes_mermaid_and_source():
    body = render_concept_body(_result())
    assert "An RDD is a lazy dataset." in body
    assert "```mermaid" in body and "graph TD; A-->B" in body
    assert "[[rdd]]" in body


def test_concept_body_omits_empty_mermaid_fence():
    body = render_concept_body(_result(mermaid=""))
    assert "```mermaid" not in body     # no empty fence when Alex drew no diagram
    assert "[[rdd]]" in body


def test_write_concept_note_frontmatter_provenance(tmp_path):
    p = write_concept_note(tmp_path, "spark", _result(), "2026-07-09")
    assert p == tmp_path / "concepts/rdd.md"
    fm, _ = _pn(p.read_text(encoding="utf-8"))
    assert fm.learner == "alex" and fm.source_note == "rdd" and fm.mastery == "mastered"
    assert fm.persona == "alex" and fm.kind == "concept" and fm.topics == ["spark"]


def test_write_qa_note_is_numbered(tmp_path):
    p = write_qa_note(tmp_path, 2, _result(), "2026-07-09")
    assert p == tmp_path / "qa/002-rdd.md"
    text = p.read_text(encoding="utf-8")
    assert "why lazy?" in text and "builds a DAG" in text
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "concept_body or concept_note or qa_note" -v`
Expected: FAIL (ImportError).

- [ ] **Step 3: Implement**

Add to `src/persona_wiki/learn.py` (add `from .models import NoteFrontmatter`, `from .index import register_atomic`, `from .storage import write_note`):
```python
from .models import NoteFrontmatter
from .index import register_atomic
from .storage import write_note


def render_concept_body(r: ConceptResult) -> str:
    parts = [r.restatement.strip()]
    if r.mermaid.strip():
        parts.append("```mermaid\n" + r.mermaid.strip() + "\n```")
    parts.append(f"*Source: [[{r.slug}]] (vutr)*")
    return "\n\n".join(parts) + "\n"


def write_concept_note(learn_root: Path, topic: str, r: ConceptResult, stamp: str) -> Path:
    fm = NoteFrontmatter(
        persona="alex", kind="concept", slug=r.slug, sources=[f"vutr/{r.slug}"],
        last_updated=stamp, topics=[topic], learner="alex", source_note=r.slug,
        mastery=r.level,
    )
    return write_note(learn_root, f"{atomic_dir('concept')}/{r.slug}.md", fm, render_concept_body(r))


def write_qa_note(learn_root: Path, order_idx: int, r: ConceptResult, stamp: str) -> Path:
    qa_lines = ["## Follow-up questions"]
    for i, q in enumerate(r.questions):
        a = r.answers[i] if i < len(r.answers) else "(the wiki does not cover this — see open questions)"
        qa_lines.append(f"\n**Alex:** {q}\n\n**vutr:** {a}")
    body = (
        f"*What Alex understood:* {r.restatement.strip()}\n\n"
        + "\n".join(qa_lines) + "\n"
    )
    fm = NoteFrontmatter(
        persona="alex", kind="concept", slug=f"{order_idx:03d}-{r.slug}",
        sources=[f"vutr/{r.slug}"], last_updated=stamp, topics=["spark"],
        learner="alex", source_note=r.slug, mastery=r.level,
    )
    return write_note(learn_root, f"qa/{order_idx:03d}-{r.slug}.md", fm, body)
```

- [ ] **Step 4: Run — expect pass**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "concept_body or concept_note or qa_note" -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/learn.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): render+write concept note (mermaid-gated) and numbered qa note"
```

---

### Task 5: Open-questions, mastery tracker, safe raw writer

**Files:**
- Modify: `src/persona_wiki/learn.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Produces:
  - `_safe_write(root: Path, rel: str, text: str) -> Path` — path-guarded raw write (for non-note docs).
  - `append_open_questions(learn_root, r: ConceptResult, stamp) -> None` — appends `r.gaps` (as "wiki gap") and `r.unverified` (as "unverified — not in vutr wiki") under a per-concept heading; creates the file with a header if missing.
  - `write_mastery(learn_root, order: List[str], levels: Dict[str, str], stamp) -> Path` — renders `mastery.md`: a table (`concept | level`) + `Overall: X% (m mastered / n)`.

- [ ] **Step 1: Write the failing test**

Append:
```python
from persona_wiki.learn import _safe_write, append_open_questions, write_mastery


def test_safe_write_rejects_escape(tmp_path):
    with pytest.raises(ValueError):
        _safe_write(tmp_path, "../escape.md", "x")


def test_append_open_questions_records_gaps_and_unverified(tmp_path):
    r = ConceptResult(slug="rdd", explanation="e", restatement="r",
                      gaps=["what tunes shuffle partitions?"],
                      unverified=["RDDs are always cached"], level="familiar")
    append_open_questions(tmp_path, r, "2026-07-09")
    text = (tmp_path / "open-questions.md").read_text(encoding="utf-8")
    assert "what tunes shuffle partitions?" in text
    assert "unverified" in text.lower() and "RDDs are always cached" in text


def test_write_mastery_table_and_percent(tmp_path):
    order = ["spark-origin", "rdd", "lazy-evaluation", "catalyst-optimizer"]
    levels = {"spark-origin": "mastered", "rdd": "mastered",
              "lazy-evaluation": "familiar", "catalyst-optimizer": "mastered"}
    p = write_mastery(tmp_path, order, levels, "2026-07-09")
    text = p.read_text(encoding="utf-8")
    assert "| rdd | mastered |" in text
    assert "75%" in text and "3 mastered / 4" in text
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "safe_write or open_questions or mastery" -v`
Expected: FAIL (ImportError).

- [ ] **Step 3: Implement**

Add to `src/persona_wiki/learn.py`:
```python
def _safe_write(root: Path, rel: str, text: str) -> Path:
    root = root.resolve()
    target = (root / rel).resolve()
    if root != target and root not in target.parents:
        raise ValueError(f"refusing to write outside learn root: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def append_open_questions(learn_root: Path, r: ConceptResult, stamp: str) -> None:
    if not r.gaps and not r.unverified:
        return
    path = learn_root / "open-questions.md"
    text = path.read_text(encoding="utf-8") if path.exists() else \
        "# Alex's open questions\n\nThings the wiki didn't answer, and claims to double-check.\n"
    lines = [f"\n## {r.slug} ({stamp})"]
    for g in r.gaps:
        lines.append(f"- wiki gap: {g}")
    for u in r.unverified:
        lines.append(f"- unverified (not in vutr wiki): {u}")
    _safe_write(learn_root, "open-questions.md", text.rstrip() + "\n" + "\n".join(lines) + "\n")


def write_mastery(learn_root: Path, order: List[str], levels: Dict[str, str], stamp: str) -> Path:
    n = len(order)
    mastered = sum(1 for s in order if levels.get(s) == "mastered")
    pct = round(100 * mastered / n) if n else 0
    rows = "\n".join(f"| {s} | {levels.get(s, 'not started')} |" for s in order)
    text = (
        "# Alex's Spark mastery\n\n"
        f"**Overall: {pct}% ({mastered} mastered / {n})** — updated {stamp}\n\n"
        "| concept | level |\n|---|---|\n" + rows + "\n"
    )
    return _safe_write(learn_root, "mastery.md", text)
```

- [ ] **Step 4: Run — expect pass**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "safe_write or open_questions or mastery" -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/learn.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): open-questions append + mastery tracker + guarded raw writer"
```

---

### Task 6: Transcript upsert (ordered, no duplicates)

**Files:**
- Modify: `src/persona_wiki/learn.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Produces:
  - `upsert_transcript(learn_root, order_idx: int, r: ConceptResult) -> Path` — appends (or replaces in place) a `## <n>. <slug>  (<level>)` dialogue section in `transcript.md`; a second call for the same concept replaces its section rather than duplicating.

- [ ] **Step 1: Write the failing test**

Append:
```python
from persona_wiki.learn import upsert_transcript


def test_transcript_section_and_no_duplicate(tmp_path):
    r = ConceptResult(slug="rdd", explanation="RDDs are lazy.", restatement="RDD = lazy",
                      questions=["why lazy?"], answers=["builds a DAG"], mermaid="graph TD;A-->B",
                      level="mastered", reason="covered it")
    upsert_transcript(tmp_path, 2, r)
    upsert_transcript(tmp_path, 2, r)   # re-run same concept
    text = (tmp_path / "transcript.md").read_text(encoding="utf-8")
    assert text.count("## 2. rdd") == 1                 # not duplicated
    assert "RDDs are lazy." in text and "RDD = lazy" in text
    assert "builds a DAG" in text and "Verdict:" in text
    assert "Diagram added: yes" in text
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k transcript -v`
Expected: FAIL (ImportError).

- [ ] **Step 3: Implement**

Add to `src/persona_wiki/learn.py`:
```python
_TRANSCRIPT_HEADER = (
    "# Alex learns Apache Spark — transcript\n\n"
    "*Full dialogue of the learning run, in order. See [[mastery]].*\n"
)


def _transcript_section(order_idx: int, r: ConceptResult) -> str:
    followups = " ".join(r.questions) if r.questions else "(no follow-ups)"
    answers = " ".join(r.answers) if r.answers else "(the wiki did not cover the follow-ups)"
    diagram = "yes" if r.mermaid.strip() else "no"
    return (
        f"## {order_idx}. {r.slug}  ({r.level})\n\n"
        f"**vutr teaches:** {r.explanation.strip()}\n\n"
        f"**Alex:** {r.restatement.strip()}  {followups}\n\n"
        f"**vutr answers:** {answers}\n\n"
        f"**Verdict:** {r.level} — {r.reason.strip()}  ·  Diagram added: {diagram}\n"
    )


def upsert_transcript(learn_root: Path, order_idx: int, r: ConceptResult) -> Path:
    path = learn_root / "transcript.md"
    text = path.read_text(encoding="utf-8") if path.exists() else _TRANSCRIPT_HEADER
    section = _transcript_section(order_idx, r)
    pat = re.compile(rf"(?ms)^## {order_idx}\. {re.escape(r.slug)}\b.*?(?=^## |\Z)")
    if pat.search(text):
        text = pat.sub(section.rstrip() + "\n\n", text)
    else:
        text = text.rstrip() + "\n\n" + section
    return _safe_write(learn_root, "transcript.md", text.rstrip() + "\n")
```

- [ ] **Step 4: Run — expect pass**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k transcript -v`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/learn.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): ordered transcript upsert with no duplicate sections"
```

---

### Task 7: `learn()` orchestrator — the loop

**Files:**
- Modify: `src/persona_wiki/learn.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Consumes: everything above; `index.load_index/save_index`, `log.log_ingest`.
- Produces:
  - `learn(learn_root, vutr_root, topic, llm, stamp, max_retries=2) -> dict` returning `{"total", "mastered", "pct", "failed"}`. Runs the loop over `concept_order`; per concept runs `run_concept`, captures (concept/qa/open-questions/transcript), tracks level; a concept below `mastered` re-enters up to `max_retries` extra passes; an already-`mastered` concept (from a prior run's concept-note frontmatter) is skipped with no LLM call; a `ValueError` from `run_concept` counts as `failed` and is retried next pass; writes `mastery.md`, updates `index.yaml` + `log.md` at the end.

- [ ] **Step 1: Write the failing test**

Append:
```python
from persona_wiki.learn import learn


def _vutr_two(tmp_path):
    root = tmp_path / "wiki/personas/vutr"
    for slug in ("rdd", "spark-origin"):
        write_note(root, f"entities/{slug}.md",
                   NoteFrontmatter(persona="vutr", kind="entity", slug=slug,
                                   sources=["persona-snapshot"], last_updated="2026-07-09",
                                   topics=["spark"]), f"Note about {slug}.")
    return root


def _llm_all_mastered():
    def llm(prompt):
        if "judging whether Alex" in prompt:
            return _json.dumps({"level": "mastered", "reason": "ok", "unverified": []})
        if "answering Alex's follow-ups" in prompt:
            return _json.dumps({"answers": ["a"], "gaps": []})
        if "You are Alex" in prompt:
            return _json.dumps({"restatement": "got it", "questions": ["why?"], "mermaid": ""})
        return "explanation"
    return llm


def test_learn_masters_all_and_writes_artifacts(tmp_path):
    vutr = _vutr_two(tmp_path)
    learn_root = tmp_path / "wiki/personas/alex/spark"
    res = learn(learn_root, vutr, "spark", _llm_all_mastered(), "2026-07-09")
    assert res == {"total": 2, "mastered": 2, "pct": 100, "failed": 0}
    assert (learn_root / "concepts/rdd.md").exists()
    assert (learn_root / "concepts/spark-origin.md").exists()
    assert (learn_root / "mastery.md").exists() and (learn_root / "transcript.md").exists()
    assert (learn_root / "index.yaml").exists() and (learn_root / "log.md").exists()
    # spark-origin is earlier in SPARK_ORDER, so it's transcript section 1
    tr = (learn_root / "transcript.md").read_text(encoding="utf-8")
    assert tr.index("## 1. spark-origin") < tr.index("## 2. rdd")


def test_learn_retry_cap_records_best_level(tmp_path):
    vutr = _vutr_two(tmp_path)
    learn_root = tmp_path / "wiki/personas/alex/spark"

    def stubborn(prompt):     # never masters
        if "judging whether Alex" in prompt:
            return _json.dumps({"level": "familiar", "reason": "partial", "unverified": []})
        if "answering Alex's follow-ups" in prompt:
            return _json.dumps({"answers": ["a"], "gaps": []})
        if "You are Alex" in prompt:
            return _json.dumps({"restatement": "sort of", "questions": [], "mermaid": ""})
        return "explanation"

    res = learn(learn_root, vutr, "spark", stubborn, "2026-07-09", max_retries=1)
    assert res["mastered"] == 0 and res["total"] == 2 and res["pct"] == 0
    assert "familiar" in (learn_root / "mastery.md").read_text(encoding="utf-8")


def test_learn_skips_already_mastered_on_rerun(tmp_path):
    vutr = _vutr_two(tmp_path)
    learn_root = tmp_path / "wiki/personas/alex/spark"
    learn(learn_root, vutr, "spark", _llm_all_mastered(), "2026-07-09")

    calls = {"n": 0}
    def counting(prompt):
        calls["n"] += 1
        return _llm_all_mastered()(prompt)
    res = learn(learn_root, vutr, "spark", counting, "2026-07-10")
    assert calls["n"] == 0 and res["mastered"] == 2      # all skipped, no LLM calls


def test_learn_counts_failure_and_continues(tmp_path):
    vutr = _vutr_two(tmp_path)
    learn_root = tmp_path / "wiki/personas/alex/spark"

    def flaky(prompt):
        if "spark-origin" in prompt and "You are Alex" in prompt:
            return "NOT JSON"      # reflect fails for spark-origin every time
        return _llm_all_mastered()(prompt)
    res = learn(learn_root, vutr, "spark", flaky, "2026-07-09", max_retries=1)
    assert res["failed"] >= 1 and res["mastered"] == 1   # rdd still masters
    assert (learn_root / "concepts/rdd.md").exists()
    assert not (learn_root / "concepts/spark-origin.md").exists()
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "test_learn" -v`
Expected: FAIL (ImportError on `learn`).

- [ ] **Step 3: Implement**

Add to `src/persona_wiki/learn.py` (add `from .index import load_index, save_index`, `from .log import log_ingest`, `from .storage import parse_note` already imported):
```python
from .index import load_index, save_index
from .log import log_ingest


def _prior_levels(learn_root: Path) -> Dict[str, str]:
    """Levels recovered from existing concept-note frontmatter (idempotent re-run)."""
    levels: Dict[str, str] = {}
    d = learn_root / atomic_dir("concept")
    if not d.exists():
        return levels
    for p in d.glob("*.md"):
        fm, _ = parse_note(p.read_text(encoding="utf-8"))
        if fm.mastery:
            levels[p.stem] = fm.mastery
    return levels


def learn(learn_root: Path, vutr_root: Path, topic: str, llm: LLMFn, stamp: str,
          max_retries: int = 2) -> dict:
    learn_root.mkdir(parents=True, exist_ok=True)
    concepts = load_topic_concepts(vutr_root, topic)
    order = concept_order(concepts)
    idx_of = {slug: i + 1 for i, slug in enumerate(order)}
    levels = _prior_levels(learn_root)
    index = load_index(learn_root)
    failed = 0

    for _pass in range(max_retries + 1):
        for slug in order:
            if levels.get(slug) == "mastered":
                continue
            try:
                r = run_concept(slug, concepts[slug], llm)
            except ValueError:
                failed += 1
                continue
            levels[slug] = r.level
            write_concept_note(learn_root, topic, r, stamp)
            write_qa_note(learn_root, idx_of[slug], r, stamp)
            append_open_questions(learn_root, r, stamp)
            upsert_transcript(learn_root, idx_of[slug], r)
            register_atomic(index, "concept", slug, topic, stamp)
        if all(levels.get(s) == "mastered" for s in order):
            break

    save_index(learn_root, index)
    write_mastery(learn_root, order, levels, stamp)
    total = len(order)
    mastered = sum(1 for s in order if levels.get(s) == "mastered")
    pct = round(100 * mastered / total) if total else 0
    log_ingest(learn_root / "log.md", index.total(),
               f"{mastered}/{total} Spark concepts mastered", stamp)
    return {"total": total, "mastered": mastered, "pct": pct, "failed": failed}
```

- [ ] **Step 4: Run — expect pass**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "test_learn" -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/learn.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): learn() loop — mastery, retries, idempotent skip, index+log"
```

---

### Task 8: CLI `learn` command + full suite

**Files:**
- Modify: `src/persona_wiki/cli.py`
- Test: `tests/persona_wiki/test_learn.py`

**Interfaces:**
- Consumes: `learn.learn`, `learn.load_topic_concepts`, `learn.concept_order`, `config.resolve_vault_dir`, `config.persona_root`, `llm.default_llm`.
- Produces: `learn` Typer command: `persona-wiki learn --learner alex --from vutr --topic spark [--vault-dir …] [--max-retries N] [--dry-run]`. `--dry-run` prints the concept order and calls no LLM.

- [ ] **Step 1: Write the failing test**

Append:
```python
from typer.testing import CliRunner
from persona_wiki.cli import app

_runner = CliRunner()


def test_cli_learn_dry_run_lists_order_no_llm(tmp_path):
    root = tmp_path / "wiki/personas/vutr"
    for slug in ("rdd", "spark-origin"):
        write_note(root, f"entities/{slug}.md",
                   NoteFrontmatter(persona="vutr", kind="entity", slug=slug,
                                   sources=["persona-snapshot"], last_updated="2026-07-09",
                                   topics=["spark"]), f"Note {slug}.")
    res = _runner.invoke(app, ["learn", "--from", "vutr", "--topic", "spark",
                               "--vault-dir", str(tmp_path), "--dry-run"])
    assert res.exit_code == 0
    assert "spark-origin" in res.output and "rdd" in res.output
    # dry-run writes nothing
    assert not (tmp_path / "wiki/personas/alex/spark/mastery.md").exists()


def test_cli_learn_help_lists_command():
    res = _runner.invoke(app, ["--help"])
    assert res.exit_code == 0 and "learn" in res.output
```

- [ ] **Step 2: Run — expect fail**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k cli_learn -v`
Expected: FAIL (no `learn` command).

- [ ] **Step 3: Implement the CLI command**

In `src/persona_wiki/cli.py`, add imports near the top:
```python
from datetime import date
from .learn import learn as run_learn, load_topic_concepts, concept_order
```
(If `from datetime import date` is already imported, don't duplicate it.)

Then add the command (after the existing `query` command):
```python
@app.command()
def learn(
    learner: str = typer.Option("alex", "--learner"),
    source: str = typer.Option("vutr", "--from"),
    topic: str = typer.Option("spark", "--topic"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
    max_retries: int = typer.Option(2, "--max-retries"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Have a learner persona learn a topic from a source persona's wiki."""
    vault = resolve_vault_dir(vault_dir)
    vutr_root = persona_root(vault, source)
    learn_root = persona_root(vault, learner) / topic
    if dry_run:
        order = concept_order(load_topic_concepts(vutr_root, topic))
        typer.echo(f"{learner} would learn {len(order)} '{topic}' concepts from {source}:")
        for i, slug in enumerate(order, 1):
            typer.echo(f"  {i}. {slug}")
        return
    result = run_learn(learn_root, vutr_root, topic, default_llm, date.today().isoformat(),
                       max_retries=max_retries)
    typer.echo(f"{learner} mastered {result['mastered']}/{result['total']} "
               f"({result['pct']}%); failed={result['failed']}")
```

- [ ] **Step 4: Run the learn test then the FULL suite**

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k cli_learn -v`
Expected: PASS (2 passed).

Run: `cd "$WT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki -q`
Expected: PASS (all persona_wiki tests green — the prior 61 plus the new learn tests).

- [ ] **Step 5: Commit**

```bash
cd "$WT"
git add src/persona_wiki/cli.py tests/persona_wiki/test_learn.py
git commit -m "feat(alex): persona-wiki learn CLI command (with --dry-run)"
```

---

### Task 9: Real run (manual, via Claude agents) + integrate

**Files:** none (operational) — produces `wiki/personas/alex/spark/*` content and merges the branch.

**Interfaces:** none.

- [ ] **Step 1: Dry-run against the real vutr wiki**

Run: `cd "$WT" && /tmp/pw-venv/bin/persona-wiki learn --from vutr --topic spark --vault-dir "$PWD" --dry-run`
Expected: lists the 16 Spark concepts in pedagogical order. No files written.

- [ ] **Step 2: Real learning run**

The real teach/reflect/answer/score is fulfilled by Claude **agents** (nested `claude -p` 401s inside a Claude Code session). Drive `learn()` with an injected `llm` backed by agent calls (one agent per step, closed-book on the concept's vutr note), exactly as the vutr wiki was built. Alternatively, run `persona-wiki learn --from vutr --topic spark --vault-dir "$PWD"` in a **plain terminal** where `claude` is logged in. This writes `wiki/personas/alex/spark/` (concepts, qa, mastery, transcript, index, log).

Expected: `mastery.md` at (near) 100%; `transcript.md` present with the full dialogue; every `concepts/<slug>.md` links `[[<vutr slug>]]`.

- [ ] **Step 3: Verify connectivity + integrity**

Run: `cd "$WT" && /tmp/pw-venv/bin/persona-wiki query "how does spark handle skew" --persona alex --vault-dir "$PWD"` is NOT applicable (query is vutr-shaped); instead open `wiki/personas/alex/spark/` in Obsidian and confirm the concept notes link back to vutr. Confirm 0 unresolved wikilinks with a quick scan.

- [ ] **Step 4: Commit the produced wiki, merge, push**

```bash
cd "$WT"
git add wiki/personas/alex
git commit -m "demo(alex): Alex's Spark learning wiki + transcript (0->100)"
git push origin persona-wiki-poc
LV=~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/learning-vault
# clear any untracked collision, then fast-forward main and push (see prior integration)
git -C "$LV" merge persona-wiki-poc --ff-only
git -C "$LV" push origin main
```

---

## Self-Review

**1. Spec coverage:**
- Closed-book grounded teach/answer/score → prompt builders (Task 2), `run_concept` (Task 3). ✓
- 16-concept pedagogical order + append unknowns → `SPARK_ORDER`/`concept_order` (Task 1). ✓
- Alex's concept notes in his voice + provenance frontmatter → Task 4. ✓
- Diagram policy (one optional mermaid, gated, no empty fence) → prompt (Task 2) + `render_concept_body` + tests (Task 4). ✓
- Q&A notes → Task 4. ✓
- open-questions (gaps + unverified) → Task 5. ✓
- mastery.md 0→100 tracker → Task 5. ✓
- transcript.md (ordered, no dupes) → Task 6. ✓
- index.yaml + 4-shape log → Task 7 (`register_atomic`, `save_index`, `log_ingest`). ✓
- Mastery math, retry cap, honest partials → Task 7. ✓
- Idempotent skip of already-mastered → Task 7 (`_prior_levels`). ✓
- Grounding guard routes unverified to open-questions → Task 3 (captures `unverified`) + Task 5 (append). ✓
- LLM/JSON failure skips concept, counts, retries, never aborts → Task 7. ✓
- Path guard confined to learn root → `storage.write_note` (notes) + `_safe_write` (Task 5). ✓
- CLI `learn` + `--dry-run` → Task 8. ✓
- Real run via agents + git integration → Task 9. ✓

**2. Placeholder scan:** none — every step has complete code and exact commands.

**3. Type consistency:** `ConceptResult` fields (Task 3) are used identically in Tasks 4/5/6/7. `learn_root` is `persona_root(vault, learner)/topic` in both the CLI (Task 8) and tests (Task 7). `atomic_dir('concept')` used for all concept-dir paths (never `f"{kind}s"`). `register_atomic(index, "concept", slug, topic, stamp)` matches the verified signature. `log_ingest(path, total, summary, stamp)` matches. `write_note(root, rel, fm, body)` matches.

**Note on a deliberate reuse:** Alex's Q&A notes are stored with `kind="concept"` frontmatter (so `parse_note`/`NoteFrontmatter` validate) but live under `qa/` and are not registered in the index as concepts — only the `concepts/<slug>.md` notes are indexed. This keeps the index a clean catalog of mastered concepts.
