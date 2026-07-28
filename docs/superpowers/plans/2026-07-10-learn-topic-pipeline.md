# `/learn-topic` Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One command per topic that (A) ingests raw captured posts + re-synthesizes a grounded persona wiki with provenance/resolution/depth gates, (B) runs the Alex learner loop → illustrated notebook, and (C) generates closed-book PDF chapters verified ≥9.0 — MVP topic: kafka.

**Architecture:** Stage A lives in the learning-vault repo's `persona_wiki` package (new `ingest.py`, `synthesize.py`, `status.py`; gates added to `qc.py`; `learn.py` gains topic-ordered curricula). Stage C lives in SOIC_Scraper (`scripts/learning_pack_wiki.py`: planner/writer prompt builders + grounding check + HTML renderer; chapters are data, not code). A thin `~/.claude/skills/learn-topic/SKILL.md` orchestrates A → gates → (B ∥ C) with stage-skip.

**Tech Stack:** Python 3.9+, Pydantic v2, Typer, PyYAML, pytest (offline, stubbed LLM `Callable[[str], str]`). Real runs use the Claude Agent tool as LLM transport.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-10-learn-topic-pipeline-design.md` (SOIC_Scraper repo).
- learning-vault repo: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault`, work in worktree `.worktrees/persona-wiki-poc`, branch `persona-wiki-poc`. Shell var used throughout: `LVWT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/learning-vault/.worktrees/persona-wiki-poc"`.
- venv OUTSIDE iCloud: `/tmp/pw-venv` (`python3 -m venv /tmp/pw-venv && /tmp/pw-venv/bin/pip install -e "$LVWT[dev]"`). Run tests as `/tmp/pw-venv/bin/python -m pytest`.
- NEVER `f"{kind}s"` — always `index.atomic_dir(kind)`.
- All wiki writes via `storage.write_note` (path-guarded to the persona root). `raw/` is append-only: ingest never overwrites an existing file.
- Tests are offline: no network, no login, LLM stubbed as `Callable[[str], str]`. NEVER call the real `claude` CLI in tests (nested `claude -p` 401s in-session).
- Real LLM transport = Claude Agent tool, one agent per unit of work.
- `sources: [persona-snapshot]` alone is INVALID provenance for a concept note; valid provenance names ≥1 `raw/` file.
- FF-merge learning-vault `persona-wiki-poc` → `main` at the end (first `rm -f "$LVMAIN/.obsidian/app.json"` — untracked file blocks the merge). SOIC_Scraper commits go on the current session branch.
- Existing interfaces consumed (do not re-implement): `storage.write_note(root, rel_path, fm, body) -> Path`, `storage.parse_note(text) -> (NoteFrontmatter, str)`, `storage.dump_note(fm, body) -> str`, `index.atomic_dir(kind) -> str`, `index.load_index/save_index/register_atomic/register_topic/has_atomic`, `log.log_ingest(log_path, total, summary, stamp) -> bool`, `models.NoteFrontmatter`, `learn.parse_json(raw) -> dict`, `config.persona_root(vault_dir, persona) -> Path`, `qc.qc_check(note_text, source_text, llm) -> (bool, str)`.

---

## Phase 1 — Stage A code (learning-vault repo)

### Task 1: `ingest.py` — raw layer feeder

**Files:**
- Create: `src/persona_wiki/ingest.py`
- Test: `tests/persona_wiki/test_ingest.py`

**Interfaces:**
- Consumes: nothing new (pure stdlib + yaml).
- Produces: `propose_include(posts_dir: Path, keywords: List[str]) -> List[str]` (sorted filenames whose name or text matches any keyword, case-insensitive); `load_include(path: Path) -> List[str]` (non-empty, non-`#` lines); `ingest(posts_dir: Path, root: Path, topic: str, include: List[str], stamp: str) -> IngestResult` with `IngestResult(copied: List[str], skipped: List[str], manifest: Path)`. Raw files land at `root/raw/<topic>/<filename>` verbatim; manifest at `root/raw/<topic>/_manifest.yaml` maps filename → `{source, copied}`.

- [ ] **Step 1: Write the failing test**

```python
# tests/persona_wiki/test_ingest.py
from pathlib import Path

import yaml

from persona_wiki.ingest import ingest, load_include, propose_include


def make_posts(tmp_path: Path) -> Path:
    posts = tmp_path / "posts"
    posts.mkdir()
    (posts / "apache-kafka-producer.md").write_text(
        "# Producer\nKafka producers batch records.", encoding="utf-8")
    (posts / "warpstream-notes.md").write_text(
        "WarpStream reimplements the Kafka protocol on S3.", encoding="utf-8")
    (posts / "50-off-promo.md").write_text("Subscribe now!", encoding="utf-8")
    return posts


def test_propose_include_matches_name_and_body(tmp_path):
    posts = make_posts(tmp_path)
    got = propose_include(posts, ["kafka"])
    assert got == ["apache-kafka-producer.md", "warpstream-notes.md"]


def test_load_include_skips_comments_and_blanks(tmp_path):
    f = tmp_path / "inc.txt"
    f.write_text("# kafka picks\napache-kafka-producer.md\n\nwarpstream-notes.md\n", encoding="utf-8")
    assert load_include(f) == ["apache-kafka-producer.md", "warpstream-notes.md"]


def test_ingest_copies_verbatim_writes_manifest(tmp_path):
    posts = make_posts(tmp_path)
    root = tmp_path / "wiki"
    res = ingest(posts, root, "kafka", ["apache-kafka-producer.md"], "2026-07-10")
    assert res.copied == ["apache-kafka-producer.md"]
    copied = root / "raw" / "kafka" / "apache-kafka-producer.md"
    assert copied.read_text(encoding="utf-8") == (posts / "apache-kafka-producer.md").read_text(encoding="utf-8")
    manifest = yaml.safe_load(res.manifest.read_text(encoding="utf-8"))
    entry = manifest["apache-kafka-producer.md"]
    assert entry["copied"] == "2026-07-10"
    assert entry["source"].endswith("posts/apache-kafka-producer.md")


def test_ingest_is_append_only(tmp_path):
    posts = make_posts(tmp_path)
    root = tmp_path / "wiki"
    ingest(posts, root, "kafka", ["apache-kafka-producer.md"], "2026-07-10")
    # source changes; re-run must NOT overwrite the already-ingested copy
    (posts / "apache-kafka-producer.md").write_text("MUTATED", encoding="utf-8")
    res = ingest(posts, root, "kafka", ["apache-kafka-producer.md"], "2026-07-11")
    assert res.copied == []
    assert res.skipped == ["apache-kafka-producer.md"]
    kept = (root / "raw" / "kafka" / "apache-kafka-producer.md").read_text(encoding="utf-8")
    assert "MUTATED" not in kept


def test_ingest_missing_include_file_errors(tmp_path):
    posts = make_posts(tmp_path)
    root = tmp_path / "wiki"
    try:
        ingest(posts, root, "kafka", ["no-such-post.md"], "2026-07-10")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "no-such-post.md" in str(e)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_ingest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'persona_wiki.ingest'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/persona_wiki/ingest.py
"""Stage A feeder: copy captured posts into the persona wiki's immutable
raw/<topic>/ layer, with an auditable manifest. Append-only by design."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml

MANIFEST = "_manifest.yaml"


@dataclass
class IngestResult:
    copied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    manifest: Path = Path()


def propose_include(posts_dir: Path, keywords: List[str]) -> List[str]:
    """Candidate post filenames whose name OR body matches any keyword."""
    kws = [k.lower() for k in keywords]
    out = []
    for p in sorted(posts_dir.glob("*.md")):
        hay = (p.name + "\n" + p.read_text(encoding="utf-8", errors="ignore")).lower()
        if any(k in hay for k in kws):
            out.append(p.name)
    return out


def load_include(path: Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def ingest(posts_dir: Path, root: Path, topic: str,
           include: List[str], stamp: str) -> IngestResult:
    """Copy each included post into root/raw/<topic>/ (never overwriting),
    recording provenance in _manifest.yaml."""
    raw_dir = root / "raw" / topic
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = raw_dir / MANIFEST
    manifest: Dict[str, dict] = {}
    if manifest_path.exists():
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}

    res = IngestResult(manifest=manifest_path)
    for name in include:
        src = posts_dir / name
        if not src.exists():
            raise ValueError(f"include-listed post not found: {name}")
        dst = raw_dir / name
        if dst.exists():
            res.skipped.append(name)          # append-only: never overwrite
            continue
        shutil.copyfile(src, dst)
        manifest[name] = {"source": str(src), "copied": stamp}
        res.copied.append(name)

    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=True, allow_unicode=True), encoding="utf-8")
    return res
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_ingest.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd "$LVWT" && git add src/persona_wiki/ingest.py tests/persona_wiki/test_ingest.py \
  && git commit -m "feat(ingest): raw/<topic> layer feeder — include-list select, verbatim copy, append-only manifest"
```

### Task 2: provenance + resolution gates in `qc.py`

**Files:**
- Modify: `src/persona_wiki/qc.py` (append; existing `qc_check` untouched)
- Test: `tests/persona_wiki/test_gates.py`

**Interfaces:**
- Consumes: `models.NoteFrontmatter`, `index.atomic_dir`.
- Produces: `wikilinks(text: str) -> List[str]` (dedup, order-preserving, strips `|alias` and `#anchor`); `provenance_gate(fm: NoteFrontmatter) -> Tuple[bool, str]` (passes iff any source starts with `raw/`); `resolution_gate(body: str, root: Path) -> Tuple[bool, List[str]]` (fails listing wikilinks that resolve to no `concepts/entities/topics` note under `root`).

- [ ] **Step 1: Write the failing test**

```python
# tests/persona_wiki/test_gates.py
from pathlib import Path

from persona_wiki.models import NoteFrontmatter
from persona_wiki.qc import provenance_gate, resolution_gate, wikilinks


def fm(sources):
    return NoteFrontmatter(persona="vutr", kind="concept",
                           sources=sources, last_updated="2026-07-10")


def test_wikilinks_dedup_alias_anchor():
    text = "See [[rdd]] and [[rdd|the RDD]] plus [[photon#jni]] and [[aqe]]."
    assert wikilinks(text) == ["rdd", "photon", "aqe"]


def test_provenance_gate_rejects_snapshot_only():
    ok, reason = provenance_gate(fm(["persona-snapshot"]))
    assert not ok and "raw/" in reason


def test_provenance_gate_accepts_raw_source():
    ok, _ = provenance_gate(fm(["raw/kafka/apache-kafka-producer.md", "persona-snapshot"]))
    assert ok


def test_provenance_gate_rejects_empty_sources():
    ok, _ = provenance_gate(fm([]))
    assert not ok


def test_resolution_gate_flags_dangling(tmp_path):
    root = tmp_path
    (root / "concepts").mkdir()
    (root / "concepts" / "rdd.md").write_text("x", encoding="utf-8")
    ok, dangling = resolution_gate("Related: [[rdd]] · [[catalyst-optimizer]]", root)
    assert not ok
    assert dangling == ["catalyst-optimizer"]


def test_resolution_gate_passes_when_all_resolve(tmp_path):
    root = tmp_path
    (root / "concepts").mkdir()
    (root / "topics").mkdir()
    (root / "concepts" / "rdd.md").write_text("x", encoding="utf-8")
    (root / "topics" / "spark.md").write_text("x", encoding="utf-8")
    ok, dangling = resolution_gate("[[rdd]] in [[spark]]", root)
    assert ok and dangling == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_gates.py -v`
Expected: FAIL with `ImportError: cannot import name 'provenance_gate'`

- [ ] **Step 3: Write minimal implementation** (append to `src/persona_wiki/qc.py`)

```python
# --- structural gates (Stage A) -------------------------------------------
from pathlib import Path
from typing import List

from .models import NoteFrontmatter

_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def wikilinks(text: str) -> List[str]:
    """Wikilink targets in order of first appearance, aliases/anchors stripped."""
    seen, out = set(), []
    for m in _WIKILINK_RE.finditer(text):
        slug = m.group(1).strip()
        if slug and slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def provenance_gate(fm: NoteFrontmatter) -> Tuple[bool, str]:
    """A concept note must cite at least one raw/ source. 'persona-snapshot'
    alone is the exact failure that hollowed the Spark wiki — reject it."""
    if any(s.startswith("raw/") for s in fm.sources):
        return True, ""
    return False, "no raw/ source cited (persona-snapshot alone is invalid)"


def resolution_gate(body: str, root: Path) -> Tuple[bool, List[str]]:
    """Every wikilink in `body` must resolve to an existing note under root."""
    dangling = []
    for slug in wikilinks(body):
        if not any((root / d / f"{slug}.md").exists()
                   for d in ("concepts", "entities", "topics")):
            dangling.append(slug)
    return (not dangling), dangling
```

- [ ] **Step 4: Run tests to verify all pass (old qc tests too)**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_gates.py tests/persona_wiki/test_qc.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
cd "$LVWT" && git add src/persona_wiki/qc.py tests/persona_wiki/test_gates.py \
  && git commit -m "feat(qc): provenance + resolution gates — receipts required, no dangling wikilinks"
```

### Task 3: `synthesize.py` — grounded per-concept synthesis + depth gate

**Files:**
- Create: `src/persona_wiki/synthesize.py`
- Test: `tests/persona_wiki/test_synthesize.py`

**Interfaces:**
- Consumes: `ingest.MANIFEST`; `qc.provenance_gate/resolution_gate`; `storage.write_note/parse_note`; `index.load_index/save_index/register_atomic/register_topic/atomic_dir`; `log.log_ingest`; `learn.parse_json`; `models.NoteFrontmatter`; `llm.LLMFn`.
- Produces: `load_raw(root: Path, topic: str) -> Dict[str, str]` (filename → text, `_*` files excluded); `build_concept_list_prompt(topic, raw) -> str` → LLM returns JSON `[{"slug": str, "sources": [filename]}]`; `build_concept_prompt(slug, sources: Dict[str,str]) -> str` → `{"body": str}`; `build_depth_prompt(slug, body) -> str` → `{"passed": bool, "gaps": [str]}`; `build_topic_prompt(topic, bodies: Dict[str,str]) -> str` → `{"comparisons": str, "open_questions": str, "synthesis": str}`; `synthesize(root: Path, topic: str, llm: LLMFn, stamp: str) -> SynthesisResult` with `SynthesisResult(written, skipped, quarantined: List[str], source_gaps: Dict[str, List[str]])`.

Behavioral contract: per-concept LLM/JSON failure → skip + count, never abort; gate-failing note → `root/_failed/<slug>.md` (fm `qc="failed"`, `qc_reason`), NOT into `concepts/`; depth-gate gaps appended to the topic note's Open questions as `- **source gap** ([[slug]]): <gap>`; topic note `Related:` line lists only written/existing concepts so the resolution gate passes by construction; index registered; `log_ingest` called once.

- [ ] **Step 1: Write the failing test**

```python
# tests/persona_wiki/test_synthesize.py
import json
from pathlib import Path

from persona_wiki.storage import parse_note
from persona_wiki.synthesize import (SynthesisResult, build_concept_prompt,
                                     load_raw, synthesize)


def seed_raw(root: Path):
    d = root / "raw" / "kafka"
    d.mkdir(parents=True)
    (d / "apache-kafka-producer.md").write_text(
        "Producers batch records per partition; acks=all waits for ISR.",
        encoding="utf-8")
    (d / "apache-kafka-consumer.md").write_text(
        "Consumers pull; offsets are per group.", encoding="utf-8")
    (d / "_manifest.yaml").write_text("{}", encoding="utf-8")


def scripted_llm(root: Path):
    """Stub LLM keyed on prompt markers, mirroring the real prompt contract."""
    def llm(prompt: str) -> str:
        if "CONCEPT-LIST" in prompt:
            return json.dumps([
                {"slug": "producer-batching", "sources": ["apache-kafka-producer.md"]},
                {"slug": "consumer-pull", "sources": ["apache-kafka-consumer.md"]},
                {"slug": "broken-one", "sources": ["apache-kafka-consumer.md"]},
            ])
        if "CONCEPT-NOTE" in prompt and "broken-one" in prompt:
            return "NOT JSON"                      # per-concept failure path
        if "CONCEPT-NOTE" in prompt:
            return json.dumps({"body": "Mechanism: producers accumulate a batch per partition because ..."})
        if "DEPTH-CHECK" in prompt and "producer-batching" in prompt:
            return json.dumps({"passed": True, "gaps": []})
        if "DEPTH-CHECK" in prompt:
            return json.dumps({"passed": False, "gaps": ["no rebalance mechanism in source"]})
        if "TOPIC-NOTE" in prompt:
            return json.dumps({"comparisons": "push vs pull", "open_questions": "", "synthesis": "Kafka in one thread."})
        raise AssertionError("unexpected prompt")
    return llm


def test_synthesize_end_to_end(tmp_path):
    root = tmp_path
    seed_raw(root)
    res = synthesize(root, "kafka", scripted_llm(root), "2026-07-10")
    assert isinstance(res, SynthesisResult)
    assert sorted(res.written) == ["consumer-pull", "producer-batching"]
    assert res.skipped == ["broken-one"]

    fm, body = parse_note((root / "concepts" / "producer-batching.md").read_text(encoding="utf-8"))
    assert fm.sources == ["raw/kafka/apache-kafka-producer.md"]   # receipt
    assert fm.topics == ["kafka"]
    assert "Mechanism" in body

    tfm, tbody = parse_note((root / "topics" / "kafka.md").read_text(encoding="utf-8"))
    assert "[[producer-batching]]" in tbody and "[[consumer-pull]]" in tbody
    assert "[[broken-one]]" not in tbody                          # no dangling link
    assert "**source gap** ([[consumer-pull]])" in tbody          # depth gap logged
    assert res.source_gaps == {"consumer-pull": ["no rebalance mechanism in source"]}

    assert (root / "log.md").exists()
    assert (root / "index.yaml").exists()


def test_synthesize_quarantines_gate_failure(tmp_path):
    root = tmp_path
    seed_raw(root)

    def bad_sources_llm(prompt: str) -> str:
        if "CONCEPT-LIST" in prompt:
            return json.dumps([{"slug": "ghost", "sources": ["not-a-real-file.md"]}])
        if "TOPIC-NOTE" in prompt:
            return json.dumps({"comparisons": "", "open_questions": "", "synthesis": "s"})
        return json.dumps({"body": "x", "passed": True, "gaps": []})

    res = synthesize(root, "kafka", bad_sources_llm, "2026-07-10")
    assert res.quarantined == ["ghost"]
    assert (root / "_failed" / "ghost.md").exists()
    assert not (root / "concepts" / "ghost.md").exists()


def test_load_raw_excludes_underscore(tmp_path):
    seed_raw(tmp_path)
    raw = load_raw(tmp_path, "kafka")
    assert set(raw) == {"apache-kafka-producer.md", "apache-kafka-consumer.md"}


def test_concept_prompt_contains_sources_verbatim():
    p = build_concept_prompt("producer-batching", {"a.md": "SOURCE TEXT HERE"})
    assert "CONCEPT-NOTE" in p and "SOURCE TEXT HERE" in p and "producer-batching" in p
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_synthesize.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'persona_wiki.synthesize'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/persona_wiki/synthesize.py
"""Stage A synthesis: mechanism-depth concept notes written FROM raw/<topic>/
posts, with provenance receipts, quarantine on gate failure, a depth gate
whose gaps are logged as source gaps, and a rebuilt topic note whose links
resolve by construction."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .index import (atomic_dir, load_index, register_atomic, register_topic,
                    save_index)
from .learn import parse_json
from .llm import LLMFn
from .log import log_ingest
from .models import NoteFrontmatter
from .qc import provenance_gate, resolution_gate
from .storage import write_note


@dataclass
class SynthesisResult:
    written: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    quarantined: List[str] = field(default_factory=list)
    source_gaps: Dict[str, List[str]] = field(default_factory=dict)


# ---------------------------------------------------------------- raw loading

def load_raw(root: Path, topic: str) -> Dict[str, str]:
    """filename -> text for every raw post of the topic (manifest excluded)."""
    d = root / "raw" / topic
    return {p.name: p.read_text(encoding="utf-8")
            for p in sorted(d.glob("*.md")) if not p.name.startswith("_")}


# ---------------------------------------------------------------- prompts

def build_concept_list_prompt(topic: str, raw: Dict[str, str]) -> str:
    listing = "\n".join(f"--- {name} ---\n{text}" for name, text in raw.items())
    return (
        f"CONCEPT-LIST for topic '{topic}'.\n"
        "Read the raw posts below. Return STRICT JSON: a list of objects "
        '{"slug": kebab-case concept slug, "sources": [post filenames that cover it]}. '
        "Cover every distinct mechanism-level concept; no invented concepts.\n\n"
        f"{listing}"
    )


def build_concept_prompt(slug: str, sources: Dict[str, str]) -> str:
    src = "\n".join(f"--- {name} ---\n{text}" for name, text in sources.items())
    return (
        f"CONCEPT-NOTE for '{slug}'. Write a mechanism-depth note (the HOW and "
        "WHY, with the numbers/case studies the sources give) grounded ONLY in "
        'the sources below. Return STRICT JSON {"body": markdown}. '
        "Never state a claim absent from the sources.\n\n"
        f"{src}"
    )


def build_depth_prompt(slug: str, body: str) -> str:
    return (
        f"DEPTH-CHECK for '{slug}'. From the note below ALONE, could a reader "
        "reconstruct the mechanism (how/why, not just keywords)? Return STRICT "
        'JSON {"passed": bool, "gaps": [missing mechanism, phrased as what the '
        "source doesn't spell out]}.\n\n"
        f"{body}"
    )


def build_topic_prompt(topic: str, bodies: Dict[str, str]) -> str:
    notes = "\n".join(f"--- {slug} ---\n{b}" for slug, b in bodies.items())
    return (
        f"TOPIC-NOTE for '{topic}'. From the concept notes below, return STRICT "
        'JSON {"comparisons": md, "open_questions": md bullet list, "synthesis": '
        "one-paragraph md threading the concepts with [[wikilinks]]}.\n\n"
        f"{notes}"
    )


# ---------------------------------------------------------------- pipeline

def synthesize(root: Path, topic: str, llm: LLMFn, stamp: str) -> SynthesisResult:
    raw = load_raw(root, topic)
    res = SynthesisResult()
    plan = parse_json(build := llm(build_concept_list_prompt(topic, raw)))  # noqa: F841
    if isinstance(plan, dict):
        plan = plan.get("concepts", [])

    bodies: Dict[str, str] = {}
    fms: Dict[str, NoteFrontmatter] = {}
    for item in plan:
        slug = item["slug"]
        srcs = {n: raw[n] for n in item.get("sources", []) if n in raw}
        fm = NoteFrontmatter(
            persona=root.name, kind="concept", slug=slug, topics=[topic],
            sources=[f"raw/{topic}/{n}" for n in item.get("sources", [])],
            last_updated=stamp)
        ok, reason = provenance_gate(fm)
        if not ok or not srcs:
            fm.qc, fm.qc_reason = "failed", reason or "cited source not in raw/"
            write_note(root, f"_failed/{slug}.md", fm, "(quarantined before synthesis)")
            res.quarantined.append(slug)
            continue
        try:
            body = parse_json(llm(build_concept_prompt(slug, srcs)))["body"]
        except (ValueError, KeyError):
            res.skipped.append(slug)            # retry next pass; never abort
            continue
        bodies[slug], fms[slug] = body, fm

    # depth gate over written bodies
    for slug, body in bodies.items():
        try:
            verdict = parse_json(llm(build_depth_prompt(slug, body)))
        except ValueError:
            verdict = {"passed": True, "gaps": []}   # fail open: gap-logging only
        gaps = [g for g in verdict.get("gaps", []) if g]
        if gaps:
            res.source_gaps[slug] = gaps

    # write concept notes
    index = load_index(root)
    for slug, body in bodies.items():
        write_note(root, f"{atomic_dir('concept')}/{slug}.md", fms[slug], body)
        register_atomic(index, "concept", slug, topic, stamp)
        res.written.append(slug)

    # topic note: links only to notes that now exist → resolution by construction
    parts = parse_json(llm(build_topic_prompt(topic, bodies)))
    related = " · ".join(f"[[{s}]]" for s in res.written)
    gap_lines = "\n".join(
        f"- **source gap** ([[{s}]]): {g}"
        for s, gaps in sorted(res.source_gaps.items()) for g in gaps)
    open_q = (parts.get("open_questions", "") + ("\n" + gap_lines if gap_lines else "")).strip()
    tbody = (
        f"Related: {related}\n\n## Comparisons\n{parts.get('comparisons', '')}\n\n"
        f"## Open questions\n{open_q}\n\n## Synthesis\n{parts.get('synthesis', '')}"
    )
    ok, dangling = resolution_gate(tbody, root)
    if not ok:                                   # belt & braces; construction should prevent
        tbody = tbody + "\n\n<!-- UNRESOLVED: " + ", ".join(dangling) + " -->"
    tfm = NoteFrontmatter(persona=root.name, kind="topic", topic=topic,
                          sources=[f"raw/{topic}"], last_updated=stamp)
    write_note(root, f"topics/{topic}.md", tfm, tbody)
    register_topic(index, topic, len(raw), stamp)
    save_index(root, index)
    log_ingest(root / "log.md", index.total(),
               f"{len(res.written)} {topic} concept(s) synthesized from raw", stamp)
    return res
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_synthesize.py -v`
Expected: 4 passed

- [ ] **Step 5: Run the whole suite (no regressions)**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki -q`
Expected: all pass

- [ ] **Step 6: Commit**

```bash
cd "$LVWT" && git add src/persona_wiki/synthesize.py tests/persona_wiki/test_synthesize.py \
  && git commit -m "feat(synthesize): grounded concept synthesis from raw/ — receipts, quarantine, depth-gap logging, resolving topic note"
```

### Task 4: topic-ordered curriculum in `learn.py`

**Files:**
- Modify: `src/persona_wiki/learn.py` (functions `concept_order`, `learn`)
- Test: `tests/persona_wiki/test_learn.py` (append)

**Interfaces:**
- Consumes: `qc.wikilinks`.
- Produces: `topic_order(root: Path, topic: str) -> List[str]` (slugs in the topic note's `Related:` line order; `[]` if no topic note); `concept_order(available: Dict[str, str], preferred: Optional[List[str]] = None) -> List[str]` (preferred-list order first, then extras sorted; defaults to `SPARK_ORDER` when `preferred` is None — existing Spark behavior unchanged). `learn(...)` now computes `preferred = topic_order(vutr_root, topic)` and passes it when non-empty.

- [ ] **Step 1: Write the failing test** (append to `tests/persona_wiki/test_learn.py`)

```python
def test_topic_order_reads_related_line(tmp_path):
    from persona_wiki.learn import topic_order
    (tmp_path / "topics").mkdir()
    (tmp_path / "topics" / "kafka.md").write_text(
        "---\npersona: vutr\nkind: topic\nlast_updated: '2026-07-10'\n---\n\n"
        "Related: [[broker-log]] · [[producer-batching]] · [[consumer-pull]]\n\n## Synthesis\nx",
        encoding="utf-8")
    assert topic_order(tmp_path, "kafka") == ["broker-log", "producer-batching", "consumer-pull"]


def test_topic_order_missing_note_is_empty(tmp_path):
    from persona_wiki.learn import topic_order
    assert topic_order(tmp_path, "kafka") == []


def test_concept_order_with_preferred():
    from persona_wiki.learn import concept_order
    avail = {"consumer-pull": "a", "broker-log": "b", "zz-extra": "c"}
    assert concept_order(avail, ["broker-log", "consumer-pull", "not-there"]) == \
        ["broker-log", "consumer-pull", "zz-extra"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -k "topic_order or preferred" -v`
Expected: FAIL with `ImportError: cannot import name 'topic_order'`

- [ ] **Step 3: Implement** — in `src/persona_wiki/learn.py`, replace `concept_order` and add `topic_order`:

```python
def topic_order(root: Path, topic: str) -> List[str]:
    """Concept slugs in the order the topic note's Related: line lists them."""
    from .qc import wikilinks
    p = root / "topics" / f"{topic}.md"
    if not p.exists():
        return []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("Related:"):
            return wikilinks(line)
    return []


def concept_order(available: Dict[str, str],
                  preferred: Optional[List[str]] = None) -> List[str]:
    """Preferred order restricted to available slugs, extras appended sorted.
    Defaults to SPARK_ORDER (the original curated Spark curriculum)."""
    pref = preferred if preferred is not None else SPARK_ORDER
    ordered = [s for s in pref if s in available]
    extra = sorted(s for s in available if s not in ordered)
    return ordered + extra
```

And inside `learn(...)`, where the order is computed, change to:

```python
    preferred = topic_order(vutr_root, topic)
    ordered = concept_order(concepts, preferred or None)
```

(`Optional` is already imported in learn.py; verify `List`, `Dict` too.)

- [ ] **Step 4: Run the full learn tests**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_learn.py -v`
Expected: all pass (old Spark-order tests still green — default unchanged)

- [ ] **Step 5: Commit**

```bash
cd "$LVWT" && git add src/persona_wiki/learn.py tests/persona_wiki/test_learn.py \
  && git commit -m "feat(learn): topic-ordered curriculum from the topic note's Related line (Spark default preserved)"
```

### Task 5: `status.py` — stage-skip logic

**Files:**
- Create: `src/persona_wiki/status.py`
- Test: `tests/persona_wiki/test_status.py`

**Interfaces:**
- Consumes: `qc.resolution_gate`, `storage.parse_note`, `qc.provenance_gate`.
- Produces: `stage_status(root: Path, learner_root: Path, topic: str) -> Dict[str, str]` with keys `ingest`, `synthesize`, `learn`, each valued `"current" | "missing" | "stale"`:
  - `ingest`: `current` if `root/raw/<topic>/` has ≥1 non-`_` md file, else `missing`.
  - `synthesize`: `current` if the topic note exists, its wikilinks all resolve, and every linked concept note passes the provenance gate; `stale` if the note exists but a gate fails; else `missing`.
  - `learn`: `current` if `learner_root/<topic>/mastery.md` exists and contains `"100%"`, `stale` if it exists without, else `missing`.

- [ ] **Step 1: Write the failing test**

```python
# tests/persona_wiki/test_status.py
from pathlib import Path

from persona_wiki.status import stage_status


def note(persona, kind, slug, sources, extra=""):
    src = "\n".join(f"- {s}" for s in sources)
    return (f"---\npersona: {persona}\nkind: {kind}\nslug: {slug}\n"
            f"sources:\n{src}\nlast_updated: '2026-07-10'\n{extra}---\n\nbody")


def test_all_missing(tmp_path):
    s = stage_status(tmp_path / "vutr", tmp_path / "alex", "kafka")
    assert s == {"ingest": "missing", "synthesize": "missing", "learn": "missing"}


def test_current_pipeline(tmp_path):
    root = tmp_path / "vutr"
    (root / "raw" / "kafka").mkdir(parents=True)
    (root / "raw" / "kafka" / "post.md").write_text("x", encoding="utf-8")
    (root / "concepts").mkdir()
    (root / "concepts" / "producer-batching.md").write_text(
        note("vutr", "concept", "producer-batching", ["raw/kafka/post.md"]), encoding="utf-8")
    (root / "topics").mkdir()
    (root / "topics" / "kafka.md").write_text(
        "---\npersona: vutr\nkind: topic\ntopic: kafka\nlast_updated: '2026-07-10'\n---\n\n"
        "Related: [[producer-batching]]", encoding="utf-8")
    learner = tmp_path / "alex"
    (learner / "kafka").mkdir(parents=True)
    (learner / "kafka" / "mastery.md").write_text("Depth mastery: 100% (1/1)", encoding="utf-8")
    s = stage_status(root, learner, "kafka")
    assert s == {"ingest": "current", "synthesize": "current", "learn": "current"}


def test_stale_synthesis_on_snapshot_provenance(tmp_path):
    root = tmp_path / "vutr"
    (root / "raw" / "kafka").mkdir(parents=True)
    (root / "raw" / "kafka" / "post.md").write_text("x", encoding="utf-8")
    (root / "concepts").mkdir()
    (root / "concepts" / "producer-batching.md").write_text(
        note("vutr", "concept", "producer-batching", ["persona-snapshot"]), encoding="utf-8")
    (root / "topics").mkdir()
    (root / "topics" / "kafka.md").write_text(
        "---\npersona: vutr\nkind: topic\ntopic: kafka\nlast_updated: '2026-07-10'\n---\n\n"
        "Related: [[producer-batching]]", encoding="utf-8")
    s = stage_status(root, tmp_path / "alex", "kafka")
    assert s["synthesize"] == "stale"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_status.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# src/persona_wiki/status.py
"""Stage-skip probe for the /learn-topic orchestrator: report whether each
pipeline stage's output is current, stale, or missing."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from .qc import provenance_gate, resolution_gate, wikilinks
from .storage import parse_note


def _synthesize_status(root: Path, topic: str) -> str:
    tpath = root / "topics" / f"{topic}.md"
    if not tpath.exists():
        return "missing"
    _, body = parse_note(tpath.read_text(encoding="utf-8"))
    ok, _ = resolution_gate(body, root)
    if not ok:
        return "stale"
    for slug in wikilinks(body):
        cpath = root / "concepts" / f"{slug}.md"
        if cpath.exists():
            fm, _ = parse_note(cpath.read_text(encoding="utf-8"))
            passed, _ = provenance_gate(fm)
            if not passed:
                return "stale"
    return "current"


def stage_status(root: Path, learner_root: Path, topic: str) -> Dict[str, str]:
    raw = root / "raw" / topic
    has_raw = raw.exists() and any(
        p.suffix == ".md" and not p.name.startswith("_") for p in raw.iterdir())
    mastery = learner_root / topic / "mastery.md"
    if not mastery.exists():
        learn = "missing"
    elif "100%" in mastery.read_text(encoding="utf-8"):
        learn = "current"
    else:
        learn = "stale"
    return {
        "ingest": "current" if has_raw else "missing",
        "synthesize": _synthesize_status(root, topic),
        "learn": learn,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_status.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
cd "$LVWT" && git add src/persona_wiki/status.py tests/persona_wiki/test_status.py \
  && git commit -m "feat(status): stage-skip probe for the /learn-topic orchestrator"
```

### Task 6: CLI — `ingest`, `synthesize`, `status` commands

**Files:**
- Modify: `src/persona_wiki/cli.py` (append three commands)
- Test: `tests/persona_wiki/test_cli.py` (append)

**Interfaces:**
- Consumes: Tasks 1, 3, 5 functions; `config.resolve_vault_dir/persona_root`.
- Produces: `persona-wiki ingest --persona vutr --topic kafka --posts-dir <dir> --include <file> [--vault-dir] [--propose "kw1,kw2"]` (with `--propose`, prints candidates and exits — no copy); `persona-wiki synthesize --persona vutr --topic kafka [--vault-dir]` (uses `llm.claude_llm` by default — the existing real-LLM seam used by `update`); `persona-wiki status --persona vutr --learner alex --topic kafka [--vault-dir]` (prints one `stage: value` line each).

- [ ] **Step 1: Write the failing test** (append to `tests/persona_wiki/test_cli.py`; follow the file's existing `CliRunner` pattern)

```python
def test_cli_ingest_propose_and_copy(tmp_path):
    posts = tmp_path / "posts"; posts.mkdir()
    (posts / "apache-kafka-producer.md").write_text("kafka", encoding="utf-8")
    inc = tmp_path / "inc.txt"; inc.write_text("apache-kafka-producer.md\n", encoding="utf-8")
    r = runner.invoke(app, ["ingest", "--persona", "vutr", "--topic", "kafka",
                            "--posts-dir", str(posts), "--include", str(inc),
                            "--vault-dir", str(tmp_path)])
    assert r.exit_code == 0, r.output
    assert (tmp_path / "wiki/personas/vutr/raw/kafka/apache-kafka-producer.md").exists()
    r2 = runner.invoke(app, ["ingest", "--persona", "vutr", "--topic", "kafka",
                             "--posts-dir", str(posts), "--propose", "kafka",
                             "--vault-dir", str(tmp_path)])
    assert "apache-kafka-producer.md" in r2.output


def test_cli_status(tmp_path):
    r = runner.invoke(app, ["status", "--persona", "vutr", "--learner", "alex",
                            "--topic", "kafka", "--vault-dir", str(tmp_path)])
    assert r.exit_code == 0
    assert "ingest: missing" in r.output
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_cli.py -k "ingest or status" -v`
Expected: FAIL (`No such command 'ingest'`)

- [ ] **Step 3: Implement** (append to `src/persona_wiki/cli.py`)

```python
@app.command()
def ingest(
    persona: str = typer.Option("vutr", "--persona"),
    topic: str = typer.Option(..., "--topic"),
    posts_dir: str = typer.Option(..., "--posts-dir"),
    include: Optional[str] = typer.Option(None, "--include"),
    propose: Optional[str] = typer.Option(None, "--propose", help="comma keywords; print candidates and exit"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
):
    """Copy captured posts into the persona's raw/<topic>/ layer."""
    from .ingest import ingest as run_ingest, load_include, propose_include
    root = _root(vault_dir, persona)
    posts = Path(posts_dir).expanduser()
    if propose:
        for name in propose_include(posts, [k.strip() for k in propose.split(",")]):
            typer.echo(name)
        raise typer.Exit(0)
    if not include:
        typer.echo("either --propose or --include is required", err=True)
        raise typer.Exit(2)
    stamp = date.today().isoformat()
    res = run_ingest(posts, root, topic, load_include(Path(include)), stamp)
    typer.echo(f"copied {len(res.copied)}, skipped {len(res.skipped)} → {res.manifest.parent}")


@app.command()
def synthesize(
    persona: str = typer.Option("vutr", "--persona"),
    topic: str = typer.Option(..., "--topic"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
):
    """Synthesize mechanism-depth concept notes from raw/<topic>/."""
    from .llm import claude_llm
    from .synthesize import synthesize as run_synthesize
    root = _root(vault_dir, persona)
    stamp = date.today().isoformat()
    res = run_synthesize(root, topic, claude_llm, stamp)
    typer.echo(f"written={len(res.written)} skipped={len(res.skipped)} "
               f"quarantined={len(res.quarantined)} gaps={sum(len(v) for v in res.source_gaps.values())}")


@app.command()
def status(
    persona: str = typer.Option("vutr", "--persona"),
    learner: str = typer.Option("alex", "--learner"),
    topic: str = typer.Option(..., "--topic"),
    vault_dir: Optional[str] = typer.Option(None, "--vault-dir"),
):
    """Report current/stale/missing per pipeline stage (for stage-skip)."""
    from .status import stage_status
    root = _root(vault_dir, persona)
    learner_root = _root(vault_dir, learner)
    for stage, val in stage_status(root, learner_root, topic).items():
        typer.echo(f"{stage}: {val}")
```

(Match the file's existing imports: `date` from `datetime`, `Path`, `Optional`, and reuse `_root`. If `llm.claude_llm` is named differently, use the same LLM factory the existing `update` command uses.)

- [ ] **Step 4: Run all CLI tests**

Run: `cd "$LVWT" && /tmp/pw-venv/bin/python -m pytest tests/persona_wiki/test_cli.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
cd "$LVWT" && git add src/persona_wiki/cli.py tests/persona_wiki/test_cli.py \
  && git commit -m "feat(cli): ingest / synthesize / status commands for the learn-topic pipeline"
```

---

## Phase 2 — Stage C code (SOIC_Scraper repo)

### Task 7: `scripts/learning_pack_wiki.py` — loader, planner, validation

**Files:**
- Create: `scripts/learning_pack_wiki.py`
- Test: `tests/test_learning_pack_wiki.py`

**Interfaces:**
- Consumes: wiki layout from Phase 1 (frontmatter via a local minimal parser — SOIC_Scraper must NOT import persona_wiki).
- Produces: `TopicData(topic: str, topic_body: str, concepts: Dict[str, str], sources: Dict[str, List[str]], raw_texts: Dict[str, str])`; `load_topic(wiki_root: Path, topic: str) -> TopicData` (wiki_root = the persona dir, e.g. `.../wiki/personas/vutr`); `build_planner_prompt(topic: str, concepts: Dict[str, str]) -> str` → LLM JSON `{"chapters": [{"title": str, "concepts": [slug]}]}`; `validate_plan(plan: dict, concepts: Iterable[str]) -> List[str]` (returns unmapped slugs; empty = valid); `parse_json(raw: str) -> dict|list` (fence-tolerant, local copy).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_learning_pack_wiki.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from learning_pack_wiki import (build_planner_prompt, load_topic, parse_json,
                                validate_plan)


def seed_wiki(tmp_path: Path) -> Path:
    root = tmp_path / "vutr"
    (root / "raw" / "kafka").mkdir(parents=True)
    (root / "raw" / "kafka" / "post-a.md").write_text("acks=all waits for ISR.", encoding="utf-8")
    (root / "concepts").mkdir()
    (root / "concepts" / "producer-batching.md").write_text(
        "---\npersona: vutr\nkind: concept\nslug: producer-batching\nsources:\n"
        "- raw/kafka/post-a.md\nlast_updated: '2026-07-10'\ntopics:\n- kafka\n---\n\n"
        "Producers batch per partition.", encoding="utf-8")
    (root / "topics").mkdir()
    (root / "topics" / "kafka.md").write_text(
        "---\npersona: vutr\nkind: topic\ntopic: kafka\nlast_updated: '2026-07-10'\n---\n\n"
        "Related: [[producer-batching]]\n\n## Synthesis\nKafka.", encoding="utf-8")
    return root


def test_load_topic(tmp_path):
    td = load_topic(seed_wiki(tmp_path), "kafka")
    assert td.topic == "kafka"
    assert list(td.concepts) == ["producer-batching"]
    assert td.sources["producer-batching"] == ["raw/kafka/post-a.md"]
    assert "acks=all" in td.raw_texts["raw/kafka/post-a.md"]
    assert "Synthesis" in td.topic_body


def test_validate_plan_flags_unmapped():
    plan = {"chapters": [{"title": "Ch1", "concepts": ["producer-batching"]}]}
    assert validate_plan(plan, ["producer-batching", "consumer-pull"]) == ["consumer-pull"]
    assert validate_plan(plan, ["producer-batching"]) == []


def test_planner_prompt_and_fence_parse():
    p = build_planner_prompt("kafka", {"producer-batching": "body"})
    assert "PLAN-CHAPTERS" in p and "producer-batching" in p
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
```

- [ ] **Step 2: Run to verify failure**

Run: `cd <SOIC_Scraper worktree> && python3 -m pytest tests/test_learning_pack_wiki.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'learning_pack_wiki'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/learning_pack_wiki.py
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
    tfm, tbody = _split_frontmatter(
        (wiki_root / "topics" / f"{topic}.md").read_text(encoding="utf-8"))
    td = TopicData(topic=topic, topic_body=tbody)
    for slug in _WIKILINK_RE.findall(tbody.splitlines()[0] if tbody else ""):
        slug = slug.strip()
        cpath = wiki_root / "concepts" / f"{slug}.md"
        if not cpath.exists():
            continue
        fm, body = _split_frontmatter(cpath.read_text(encoding="utf-8"))
        td.concepts[slug] = body
        td.sources[slug] = [s for s in fm.get("sources", []) if s.startswith("raw/")]
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_learning_pack_wiki.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/learning_pack_wiki.py tests/test_learning_pack_wiki.py \
  && git commit -m "feat(pack): wiki loader + chapter planner + coverage validation for generated learning packs"
```

### Task 8: writer prompt + grounding check + renderer

**Files:**
- Modify: `scripts/learning_pack_wiki.py` (append)
- Test: `tests/test_learning_pack_wiki.py` (append)

**Interfaces:**
- Produces: `build_writer_prompt(chapter: dict, concepts: Dict[str, str], raw: str) -> str` → LLM JSON `{"html": str}` (closed-book instruction: claims only from provided text; out-of-source material only inside `<div class="beyond">`); `grounding_check(chapter_html: str, sources_text: str) -> List[str]` (numeric tokens — e.g. `1.42`, `42,920`, `10MB`, `95%`, `200` — present in the chapter but absent from sources AND outside any `class="beyond"` div; single digits 0–9 ignored); `render_pack_html(title: str, chapters: List[dict]) -> str` (self-contained pack HTML: cover, TOC, one `<section>` per chapter; reuses the visual language of `generate_vutr_spark.py` — serif body, boxed key-insight callouts); `main()` argparse CLI: `--wiki-root`, `--topic`, `--chapters` (chapters.json path), `--stage plan|render`, `--out`.

- [ ] **Step 1: Write the failing test** (append)

```python
from learning_pack_wiki import build_writer_prompt, grounding_check, render_pack_html


def test_writer_prompt_closed_book():
    ch = {"title": "Producers", "concepts": ["producer-batching"]}
    p = build_writer_prompt(ch, {"producer-batching": "batch per partition"}, "acks=all")
    assert "WRITE-CHAPTER" in p and "closed-book" in p.lower() and "acks=all" in p


def test_grounding_check_flags_unsourced_numbers():
    sources = "The threshold is 10MB and the default is 200 partitions."
    ok_chapter = "<p>Default is 200 partitions; broadcast under 10MB.</p>"
    assert grounding_check(ok_chapter, sources) == []
    bad = "<p>A 2.6GB file inflates 1.42x in memory.</p>"
    flagged = grounding_check(bad, sources)
    assert "1.42" in "".join(flagged) and "2.6" in "".join(flagged)


def test_grounding_check_allows_beyond_box():
    sources = "nothing numeric"
    ch = '<div class="beyond">industry rule of thumb: 1.5x</div><p>plain text</p>'
    assert grounding_check(ch, sources) == []


def test_render_pack_html_structure():
    html = render_pack_html("Kafka Pack", [
        {"title": "Producers", "concepts": ["producer-batching"], "html": "<p>ch1</p>"}])
    assert "Kafka Pack" in html and "<p>ch1</p>" in html and "Producers" in html
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/test_learning_pack_wiki.py -v`
Expected: new tests FAIL with ImportError

- [ ] **Step 3: Implement** (append to `scripts/learning_pack_wiki.py`)

```python
_NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
_BEYOND_RE = re.compile(r'<div class="beyond">.*?</div>', re.DOTALL)


def build_writer_prompt(chapter: dict, concepts: Dict[str, str], raw: str) -> str:
    bodies = "\n".join(f"--- {s} ---\n{concepts[s]}" for s in chapter["concepts"])
    return (
        f"WRITE-CHAPTER '{chapter['title']}'. Write expert exposition HTML "
        "(h2 sections, p, tables where the data calls for them) covering the "
        "concepts below. This is CLOSED-BOOK: every claim and every number "
        "must appear in the concept notes or raw sources provided; anything "
        'beyond them goes ONLY inside <div class="beyond">…</div> boxes or is '
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
        if len(canon) == 1:          # single digits: prose, not claims
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
    ap.add_argument("--chapters", help="chapters.json path (plan output / render input)")
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
```

(The plan/write LLM calls happen via Claude agents in the live run — the script only builds prompts, validates, checks grounding, and renders. `chapters.json` shape: `{"title": str, "chapters": [{"title", "concepts", "html"}]}`.)

- [ ] **Step 4: Run all pack tests**

Run: `python3 -m pytest tests/test_learning_pack_wiki.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/learning_pack_wiki.py tests/test_learning_pack_wiki.py \
  && git commit -m "feat(pack): closed-book writer prompt, numeric grounding check, pack HTML renderer + CLI"
```

### Task 9: verification workflow doc update

**Files:**
- Modify: `docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md` (add a "Generated packs (chapters.json)" subsection)

- [ ] **Step 1: Append the subsection** stating: for wiki-generated packs, the verification loop's per-chapter content comes from `output/packs/<topic>/chapters.json` (single source for both PDF and examiner prompts — the CHAPTERS-in-code sync invariant does not apply); fix rounds edit `chapters.json` and re-render; grounding_check runs after every fix round; a chapter stuck <9.0 after 3 fix rounds halts with a report naming the failing dimension.

- [ ] **Step 2: Commit**

```bash
git add docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md \
  && git commit -m "docs(verification): chapters.json as single content source for generated packs"
```

---

## Phase 3 — Orchestrator skill

### Task 10: `~/.claude/skills/learn-topic/SKILL.md`

**Files:**
- Create: `~/.claude/skills/learn-topic/SKILL.md`

No unit test (markdown recipe); verify by reading back and by the live run (Phase 4). The skill must document, in order:

1. **Frontmatter**: `name: learn-topic`; description triggering on "learn topic X end to end / build notebook+PDF for topic / run the learning pipeline".
2. **Stage-skip probe**: run `persona-wiki status --persona <p> --learner alex --topic <t> --vault-dir <learning-vault>` first; skip any `current` stage.
3. **Stage A**: `persona-wiki ingest --propose "<keywords>"` → review/edit include list at `data/ingest/<persona>-<topic>.txt` (commit it) → `persona-wiki ingest --include …` → synthesis via **Claude agents** (one per concept batch; the CLI `synthesize` uses the built-in LLM seam; for agent-driven runs, drive `persona_wiki.synthesize` functions with the Agent tool as transport — never nested `claude -p`). Gates: provenance + resolution enforced in-code; depth gaps land in the topic note's Open questions.
4. **Stage B**: `persona-wiki learn --learner alex --from <p> --topic <t>` (agent transport), then `/learning-notebook` on the transcript (author `diagram_specs/<topic>.json` first — same shape as spark.json).
5. **Stage C**: `python3 scripts/learning_pack_wiki.py --stage plan …` → agent plans chapters → `validate_plan` (unmapped = re-plan) → agents write chapters closed-book → `grounding_check` per chapter (flags = fix round) → verification loop per `docs/LEARNING_PACK_VERIFICATION_WORKFLOW.md` (≥9.0 + tri-agent sign-off, halt after 3 failed fix rounds) → `--stage render` → PDF via headless Chrome `--print-to-pdf` → optional `scripts/gdrive_upload.py`.
6. **Paths**: learning-vault worktree, SOIC_Scraper repo, venv `/tmp/pw-venv`, vault-dir env `PERSONA_WIKI_DIR`.

- [ ] **Step 1: Write the SKILL.md** with the above content, concrete commands, and the two repos' absolute paths.
- [ ] **Step 2: Verify frontmatter loads** — `head -10 ~/.claude/skills/learn-topic/SKILL.md` shows `name:` + `description:`.

---

## Phase 4 — Live kafka run (MVP proof, agent-driven)

### Task 11: ingest kafka raw layer

- [ ] Propose: `persona-wiki ingest --persona vutr --topic kafka --posts-dir "$HOME/Documents/Obsidian Vault/Substack/posts/vutr" --propose "kafka,warpstream,bufstream,automq,diskless" --vault-dir <learning-vault>` 
- [ ] Review candidates; drop junk (promos/polls); write include list to learning-vault `data/ingest/vutr-kafka.txt`; commit it.
- [ ] Ingest with `--include`; verify `raw/kafka/` file count matches the include list; commit the raw layer? **No** — wiki content under `wiki/` is vault data; it is committed in the learning-vault repo as the existing wikis are. Commit.

### Task 12: synthesize kafka wiki (agents)

- [ ] Run synthesis with Claude agents as transport over `persona_wiki.synthesize` (one agent per concept for `build_concept_prompt`, one for the list, one for depth checks, one for the topic note), or `persona-wiki synthesize` if the built-in seam is used.
- [ ] Verify: every `concepts/*.md` with `topics: [kafka]` cites ≥1 `raw/kafka/` source (`grep -L "raw/kafka" …` is empty); `persona-wiki status … --topic kafka` reports `synthesize: current`; source gaps present in topic note if any.
- [ ] Commit the kafka wiki.

### Task 13: Alex learns kafka + notebook

- [ ] `persona-wiki learn --learner alex --from vutr --topic kafka` with agent transport; mastery must reach 100% (depth-graded) with NO side-channel source.
- [ ] Author `diagram_specs/kafka.json` (one entry per concept: diagram/table + aha + margins + hi).
- [ ] Render via the learning-notebook skill: `python3 ~/.claude/skills/learning-notebook/render_learning_artifact.py --transcript <vault>/wiki/personas/alex/kafka/transcript.md --learner Alex --topic kafka --specs diagram_specs/kafka.json --out kafka_notebook.html`.
- [ ] Publish as Artifact; upload to gdrive. Commit Alex's kafka wiki + specs.

### Task 14: kafka PDF pack (plan → write → verify → render)

- [ ] `--stage plan` → agent returns chapter plan → `validate_plan` (must be `[]`).
- [ ] Agents write chapters (closed-book prompts) → `grounding_check` per chapter must be `[]` (or claims moved to beyond-boxes) → save `output/packs/kafka/chapters.json`.
- [ ] Run the verification loop (examiner=vutr + sdcourse, Justin, Alex) to ≥9.0/chapter + tri-agent sign-off; fix rounds edit chapters.json; halt-with-report if any chapter <9.0 after 3 rounds.
- [ ] `--stage render` → `output/packs/kafka/pack.html` → headless Chrome `--print-to-pdf=output/packs/kafka/kafka_pack.pdf`.
- [ ] Upload PDF to gdrive. Commit chapters.json + doc updates in SOIC_Scraper.

### Task 15: merge + close out

- [ ] learning-vault: `rm -f "$LVMAIN/.obsidian/app.json"`; FF-merge `persona-wiki-poc` → `main`; push both.
- [ ] SOIC_Scraper: push session branch; merge to main branch per repo flow.
- [ ] Update memory (`learn-topic` pipeline memory note) and run `/graphify .` refresh if requested.
- [ ] Success-criteria audit against spec §7 (all four criteria), then `claude_goal.py complete`.
