# STORM Business Research Engine (MVP: `idea` mode) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the STORM multi-perspective business-research engine and its first
mode (`idea` — evaluate one business idea), so `/storm` runs a topic through
auto-cast expert lenses → contradiction map → synthesis → adversarial verify →
a graded vault note + HTML briefing.

**Architecture:** A small, unit-tested pure-Python package `storm_core` provides
the models, roster discovery, note/HTML rendering, and a CLI. A deterministic
JS **workflow** (`.claude/workflows/storm.js`) orchestrates the agent phases and
shells out to that CLI for rendering. A thin `/storm` **skill** is the front door
(picks mode, asks voice count, gathers input, invokes the workflow). The engine
writes into the non-git Business Personas iCloud vault.

**Tech Stack:** Python 3.9+, Pydantic v2 (already a dep), stdlib only otherwise;
the Workflow tool (JS orchestration script); Typer is NOT needed (the CLI is a
tiny `argparse`/`__main__`, invoked by an agent via Bash).

## Global Constraints

- Python floor **>=3.9**; use only stdlib + Pydantic v2 (already in deps). No new
  Python dependencies.
- Casting rule (verbatim from spec): **auto-cast N best-fit named voices, default
  N=3, asked each run; Mufti is always appended on top of N** (N voices + Mufti).
- Mufti is a **named, always-on, special-cased halal gate with veto power**; never
  subject to casting.
- Verdict scale is exactly **KEEP / WATCHLIST / CUT**; evidence grades exactly
  **A / B / C** (match the v2 catalog vocabulary).
- Named-voice roster is **DYNAMIC** — discovered at runtime from `.claude/agents/*.md`
  (+ Business Personas vault persona notes); never hardcode the voice list.
- Reports write to `Business Personas/Opportunity-Catalog/STORM-Reports/` (new
  notes) and a gitignored `output/storm/` (HTML). **Nothing captured is committed.**
- Each parallel agent writes its **own** scratchpad result file (never echo all
  results through one return — 64k output-cap gotcha). No large objects through
  workflow `args` — pass paths/scalars; agents read shared data from disk.
- MVP scope is **`idea` mode only**. `gap` / `rescore` / `research` and the
  marker-merge in-place editing are explicitly **out of scope** for this plan.

**Running tests (this worktree):** the project venv lives at the main checkout.
Run storm tests with the src path exported:

```bash
cd /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/bold-sammet-8c78b3
PYTHONPATH=src /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest tests/test_storm_*.py -v
```

Define once for reuse in steps below:
`PYTEST="PYTHONPATH=src /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest"`

## File Structure

- `src/storm_core/__init__.py` — package marker, exports `__all__`.
- `src/storm_core/models.py` — Pydantic models + enums (the StormReport schema).
- `src/storm_core/config.py` — filesystem paths (vault, reports dir, HTML out) w/ env overrides.
- `src/storm_core/roster.py` — dynamic persona-roster discovery.
- `src/storm_core/report.py` — assemble the Obsidian note markdown from a StormReport.
- `src/storm_core/html_render.py` — render the self-contained HTML briefing.
- `src/storm_core/__main__.py` — tiny CLI: `roster` and `build` subcommands.
- `tests/test_storm_models.py`, `tests/test_storm_config.py`, `tests/test_storm_roster.py`,
  `tests/test_storm_report.py`, `tests/test_storm_html.py`, `tests/test_storm_cli.py`.
- `.claude/workflows/storm.js` — the deterministic engine (orchestration; not pytest-tested).
- `.claude/skills/storm/SKILL.md` — the `/storm` front-door skill.
- `CLAUDE.md` — document the new asset.

---

### Task 1: `storm_core` models + config

**Files:**
- Create: `src/storm_core/__init__.py`
- Create: `src/storm_core/models.py`
- Create: `src/storm_core/config.py`
- Test: `tests/test_storm_models.py`, `tests/test_storm_config.py`

**Interfaces:**
- Produces:
  - `class Verdict(str, Enum)` → `KEEP="KEEP"`, `WATCHLIST="WATCHLIST"`, `CUT="CUT"`.
  - `class Grade(str, Enum)` → `A="A"`, `B="B"`, `C="C"`.
  - `class Evidence(BaseModel)`: `claim: str`, `source: str`, `date: str | None = None`,
    `grade: Grade`, `status: str = "confirmed"` (one of `confirmed|corrected|demoted`).
  - `class Finding(BaseModel)`: `title: str`, `detail: str`, `reliability: int` (1–10),
    `supported_by: list[str] = []`, `challenged_by: list[str] = []`, `evidence: list[Evidence] = []`.
  - `class Contradiction(BaseModel)`: `topic: str`, `positions: dict[str, str]` (lens→stance),
    `resolution: str = ""`.
  - `class StormReport(BaseModel)`: `topic: str`, `mode: str`, `summary: str`,
    `verdict: Verdict`, `lenses: list[str]`, `findings: list[Finding]`,
    `contradictions: list[Contradiction] = []`, `halal_note: str = ""`,
    `generated: str` (ISO date string, supplied by caller — never `datetime.now()` in a
    model default).
  - `config.REPORTS_DIR: Path`, `config.HTML_OUT_DIR: Path`, `config.ROSTER_DIR: Path`
    with env overrides `STORM_REPORTS_DIR`, `STORM_HTML_DIR`, `STORM_ROSTER_DIR`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_storm_models.py
import pytest
from pydantic import ValidationError
from storm_core.models import Verdict, Grade, Evidence, Finding, StormReport


def test_verdict_and_grade_values():
    assert [v.value for v in Verdict] == ["KEEP", "WATCHLIST", "CUT"]
    assert [g.value for g in Grade] == ["A", "B", "C"]


def test_storm_report_roundtrips_and_validates_verdict():
    r = StormReport(
        topic="Zakat Advisory", mode="idea", summary="s",
        verdict="KEEP", lenses=["Operator", "Mufti"],
        findings=[Finding(title="t", detail="d", reliability=9,
                          supported_by=["Operator"], challenged_by=["Skeptic"],
                          evidence=[Evidence(claim="c", source="gov.in", grade="A")])],
        generated="2026-07-06",
    )
    dumped = r.model_dump_json()
    back = StormReport.model_validate_json(dumped)
    assert back.verdict is Verdict.KEEP
    assert back.findings[0].evidence[0].grade is Grade.A


def test_invalid_verdict_rejected():
    with pytest.raises(ValidationError):
        StormReport(topic="x", mode="idea", summary="s", verdict="MAYBE",
                    lenses=[], findings=[], generated="2026-07-06")
```

```python
# tests/test_storm_config.py
import importlib


def test_reports_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("STORM_REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setenv("STORM_HTML_DIR", str(tmp_path / "html"))
    import storm_core.config as cfg
    importlib.reload(cfg)
    assert cfg.REPORTS_DIR == (tmp_path / "reports")
    assert cfg.HTML_OUT_DIR == (tmp_path / "html")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `$PYTEST tests/test_storm_models.py tests/test_storm_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'storm_core'`.

- [ ] **Step 3: Write the implementation**

```python
# src/storm_core/__init__.py
"""STORM multi-perspective business-research engine (pure helpers + CLI)."""
from storm_core.models import (
    Verdict, Grade, Evidence, Finding, Contradiction, StormReport,
)

__all__ = [
    "Verdict", "Grade", "Evidence", "Finding", "Contradiction", "StormReport",
]
```

```python
# src/storm_core/models.py
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    KEEP = "KEEP"
    WATCHLIST = "WATCHLIST"
    CUT = "CUT"


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class Evidence(BaseModel):
    claim: str
    source: str
    date: Optional[str] = None
    grade: Grade
    status: str = "confirmed"  # confirmed | corrected | demoted


class Finding(BaseModel):
    title: str
    detail: str
    reliability: int = Field(ge=1, le=10)
    supported_by: List[str] = []
    challenged_by: List[str] = []
    evidence: List[Evidence] = []


class Contradiction(BaseModel):
    topic: str
    positions: Dict[str, str] = {}
    resolution: str = ""


class StormReport(BaseModel):
    topic: str
    mode: str
    summary: str
    verdict: Verdict
    lenses: List[str] = []
    findings: List[Finding] = []
    contradictions: List[Contradiction] = []
    halal_note: str = ""
    generated: str  # ISO date supplied by caller (never a now() default)
```

```python
# src/storm_core/config.py
from __future__ import annotations

import os
from pathlib import Path

_VAULT = Path(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Business Personas/Opportunity-Catalog"
).expanduser()

REPORTS_DIR = Path(
    os.environ.get("STORM_REPORTS_DIR", _VAULT / "STORM-Reports")
).expanduser()

# Project root: src/storm_core/config.py -> repo root
_ROOT = Path(__file__).resolve().parents[2]

HTML_OUT_DIR = Path(
    os.environ.get("STORM_HTML_DIR", _ROOT / "output" / "storm")
).expanduser()

ROSTER_DIR = Path(
    os.environ.get("STORM_ROSTER_DIR", _ROOT / ".claude" / "agents")
).expanduser()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `$PYTEST tests/test_storm_models.py tests/test_storm_config.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/storm_core/__init__.py src/storm_core/models.py src/storm_core/config.py \
        tests/test_storm_models.py tests/test_storm_config.py
git commit -m "feat(storm): storm_core models + config paths"
```

---

### Task 2: Dynamic persona-roster discovery

**Files:**
- Create: `src/storm_core/roster.py`
- Test: `tests/test_storm_roster.py`

**Interfaces:**
- Consumes: `config.ROSTER_DIR`.
- Produces:
  - `class Persona(BaseModel)`: `name: str`, `slug: str`, `description: str`.
  - `discover_roster(roster_dir: Path | None = None) -> list[Persona]` — reads every
    `*.md` in the dir, parses YAML frontmatter `name:` and `description:` (falls back
    to the filename stem for `name` and `""` for `description` when absent), returns
    them sorted by `name`. Missing dir → `[]` (never raises).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_storm_roster.py
from pathlib import Path
from storm_core.roster import discover_roster, Persona


def _write_agent(d: Path, fname: str, name: str, desc: str):
    (d / fname).write_text(
        f"---\nname: {name}\ndescription: {desc}\n---\n\n# {name}\n", encoding="utf-8"
    )


def test_discovers_and_parses_agents(tmp_path):
    _write_agent(tmp_path, "buffett.md", "warren-buffett", "value investor")
    _write_agent(tmp_path, "mufti.md", "mufti-taqi-usmani", "halal compliance")
    roster = discover_roster(tmp_path)
    assert [p.name for p in roster] == ["mufti-taqi-usmani", "warren-buffett"]
    assert roster[1].description == "value investor"
    assert all(isinstance(p, Persona) for p in roster)


def test_missing_frontmatter_falls_back_to_stem(tmp_path):
    (tmp_path / "codie.md").write_text("# no frontmatter here", encoding="utf-8")
    roster = discover_roster(tmp_path)
    assert roster[0].name == "codie"
    assert roster[0].description == ""


def test_missing_dir_returns_empty(tmp_path):
    assert discover_roster(tmp_path / "does-not-exist") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `$PYTEST tests/test_storm_roster.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'storm_core.roster'`.

- [ ] **Step 3: Write the implementation**

```python
# src/storm_core/roster.py
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from storm_core import config

_FM = re.compile(r"^---\s*\n(.*?)\n---", re.S)
_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.M)
_DESC = re.compile(r"^description:\s*(.+?)\s*$", re.M)


class Persona(BaseModel):
    name: str
    slug: str
    description: str


def _field(pattern: re.Pattern, frontmatter: str) -> str:
    m = pattern.search(frontmatter)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def discover_roster(roster_dir: Optional[Path] = None) -> List[Persona]:
    d = Path(roster_dir) if roster_dir is not None else config.ROSTER_DIR
    if not d.exists():
        return []
    people: List[Persona] = []
    for md in sorted(d.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        fm_match = _FM.search(text)
        fm = fm_match.group(1) if fm_match else ""
        name = _field(_NAME, fm) or md.stem
        desc = _field(_DESC, fm)
        people.append(Persona(name=name, slug=md.stem, description=desc))
    people.sort(key=lambda p: p.name)
    return people
```

- [ ] **Step 4: Run test to verify it passes**

Run: `$PYTEST tests/test_storm_roster.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/storm_core/roster.py tests/test_storm_roster.py
git commit -m "feat(storm): dynamic persona-roster discovery"
```

---

### Task 3: Obsidian note assembly

**Files:**
- Create: `src/storm_core/report.py`
- Test: `tests/test_storm_report.py`

**Interfaces:**
- Consumes: `models.StormReport`, `models.Finding`, `models.Contradiction`.
- Produces:
  - `build_note_markdown(report: StormReport) -> str` — returns a full Obsidian note:
    YAML frontmatter (`title`, `tags: [storm, <mode>]`, `verdict`, `generated`), an
    `## Summary`, a `## Verdict` line, a `## Findings` section (each finding with its
    reliability, supported/challenged lenses, and evidence lines showing grade+status),
    a `## Contradiction Map` section, and a `## Halal Note` section (only when
    `halal_note` is non-empty).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_storm_report.py
from storm_core.models import StormReport, Finding, Contradiction, Evidence
from storm_core.report import build_note_markdown


def _report():
    return StormReport(
        topic="Zakat & Islamic-Finance Advisory", mode="idea",
        summary="Strong regulated niche.", verdict="KEEP",
        lenses=["Operator", "Investor", "Mufti"],
        findings=[Finding(
            title="Underserved compliance demand", detail="MSMEs need zakat structuring.",
            reliability=9, supported_by=["Operator", "Investor"], challenged_by=["Skeptic"],
            evidence=[Evidence(claim="12% CAGR", source="rbi.org.in", date="2026-01",
                               grade="A", status="confirmed")])],
        contradictions=[Contradiction(topic="Pricing power",
                        positions={"Investor": "high", "Skeptic": "low"},
                        resolution="Retainer model resolves it.")],
        halal_note="Riba-free by construction; Mufti: PASS.",
        generated="2026-07-06",
    )


def test_note_has_frontmatter_and_all_sections():
    md = build_note_markdown(_report())
    assert md.startswith("---\n")
    assert 'title: "Zakat & Islamic-Finance Advisory"' in md
    assert "tags: [storm, idea]" in md
    assert "verdict: KEEP" in md
    assert "## Summary" in md
    assert "## Findings" in md
    assert "Underserved compliance demand" in md
    assert "(reliability 9/10)" in md
    assert "supported by: Operator, Investor" in md
    assert "12% CAGR" in md and "grade A" in md and "confirmed" in md
    assert "## Contradiction Map" in md
    assert "Pricing power" in md
    assert "## Halal Note" in md and "Mufti: PASS" in md


def test_halal_section_omitted_when_empty():
    r = _report()
    r.halal_note = ""
    assert "## Halal Note" not in build_note_markdown(r)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `$PYTEST tests/test_storm_report.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'storm_core.report'`.

- [ ] **Step 3: Write the implementation**

```python
# src/storm_core/report.py
from __future__ import annotations

from storm_core.models import StormReport


def _finding_block(f) -> str:
    lines = [f"### {f.title} (reliability {f.reliability}/10)", "", f.detail, ""]
    if f.supported_by:
        lines.append(f"- supported by: {', '.join(f.supported_by)}")
    if f.challenged_by:
        lines.append(f"- challenged by: {', '.join(f.challenged_by)}")
    for e in f.evidence:
        date = f" ({e.date})" if e.date else ""
        lines.append(
            f"- evidence: {e.claim} — {e.source}{date} · grade {e.grade.value} · {e.status}"
        )
    lines.append("")
    return "\n".join(lines)


def build_note_markdown(report: StormReport) -> str:
    fm = [
        "---",
        f'title: "{report.topic}"',
        f"tags: [storm, {report.mode}]",
        f"verdict: {report.verdict.value}",
        f"generated: {report.generated}",
        f"lenses: [{', '.join(report.lenses)}]",
        "---",
        "",
        f"# {report.topic}",
        "",
        "## Summary",
        "",
        report.summary,
        "",
        f"## Verdict: {report.verdict.value}",
        "",
        "## Findings",
        "",
    ]
    parts = ["\n".join(fm)]
    for f in report.findings:
        parts.append(_finding_block(f))

    if report.contradictions:
        parts.append("## Contradiction Map\n")
        for c in report.contradictions:
            stances = "; ".join(f"{k}: {v}" for k, v in c.positions.items())
            parts.append(f"- **{c.topic}** — {stances}. → {c.resolution}")
        parts.append("")

    if report.halal_note.strip():
        parts.append("## Halal Note\n")
        parts.append(report.halal_note)
        parts.append("")

    return "\n".join(parts)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `$PYTEST tests/test_storm_report.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/storm_core/report.py tests/test_storm_report.py
git commit -m "feat(storm): assemble graded Obsidian note from a StormReport"
```

---

### Task 4: Self-contained HTML briefing

**Files:**
- Create: `src/storm_core/html_render.py`
- Test: `tests/test_storm_html.py`

**Interfaces:**
- Consumes: `models.StormReport`.
- Produces:
  - `render_html(report: StormReport) -> str` — a single self-contained HTML document
    (inlined `<style>`, no external URLs) with the topic as `<h1>`, a verdict badge, the
    60-second summary, findings ranked by reliability (highest first), and the
    contradiction map. HTML-escapes all report text.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_storm_html.py
from storm_core.models import StormReport, Finding
from storm_core.html_render import render_html


def _report():
    return StormReport(
        topic="Zakat <Advisory>", mode="idea", summary="Strong niche.",
        verdict="KEEP", lenses=["Operator"],
        findings=[
            Finding(title="Low-rel", detail="d", reliability=4),
            Finding(title="High-rel", detail="d", reliability=9),
        ],
        generated="2026-07-06",
    )


def test_html_is_self_contained_and_ranked():
    html = render_html(_report())
    assert html.lstrip().startswith("<!doctype html>")
    assert "http://" not in html and "https://" not in html  # no external refs
    assert "<style>" in html
    # topic is HTML-escaped
    assert "Zakat &lt;Advisory&gt;" in html
    assert "KEEP" in html
    # findings ranked: High-rel (9) appears before Low-rel (4)
    assert html.index("High-rel") < html.index("Low-rel")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `$PYTEST tests/test_storm_html.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'storm_core.html_render'`.

- [ ] **Step 3: Write the implementation**

```python
# src/storm_core/html_render.py
from __future__ import annotations

from html import escape

from storm_core.models import StormReport

_STYLE = (
    "body{font:16px/1.5 -apple-system,system-ui,sans-serif;max-width:760px;"
    "margin:2rem auto;padding:0 1rem;color:#1a1a1a}"
    ".badge{display:inline-block;padding:.2rem .6rem;border-radius:.4rem;"
    "background:#e8f0e8;font-weight:600}"
    ".finding{border-left:3px solid #ccc;padding:.2rem 0 .2rem 1rem;margin:1rem 0}"
    ".rel{color:#666;font-size:.85rem}"
)


def render_html(report: StormReport) -> str:
    ranked = sorted(report.findings, key=lambda f: f.reliability, reverse=True)
    rows = []
    for f in ranked:
        rows.append(
            f'<div class="finding"><strong>{escape(f.title)}</strong> '
            f'<span class="rel">(reliability {f.reliability}/10)</span>'
            f"<p>{escape(f.detail)}</p></div>"
        )
    contra = ""
    if report.contradictions:
        items = "".join(
            f"<li><strong>{escape(c.topic)}</strong>: "
            + escape("; ".join(f"{k}={v}" for k, v in c.positions.items()))
            + f" → {escape(c.resolution)}</li>"
            for c in report.contradictions
        )
        contra = f"<h2>Contradiction Map</h2><ul>{items}</ul>"
    return (
        "<!doctype html>\n<html><head><meta charset='utf-8'>"
        f"<title>{escape(report.topic)}</title><style>{_STYLE}</style></head><body>"
        f"<h1>{escape(report.topic)}</h1>"
        f'<p><span class="badge">{escape(report.verdict.value)}</span></p>'
        f"<h2>Summary</h2><p>{escape(report.summary)}</p>"
        f"<h2>Findings</h2>{''.join(rows)}"
        f"{contra}"
        "</body></html>"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `$PYTEST tests/test_storm_html.py -v`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**

```bash
git add src/storm_core/html_render.py tests/test_storm_html.py
git commit -m "feat(storm): self-contained HTML briefing renderer"
```

---

### Task 5: `storm_core` CLI (`roster` + `build`)

**Files:**
- Create: `src/storm_core/__main__.py`
- Test: `tests/test_storm_cli.py`

**Interfaces:**
- Consumes: `roster.discover_roster`, `report.build_note_markdown`, `html_render.render_html`,
  `config.REPORTS_DIR`, `config.HTML_OUT_DIR`, `models.StormReport`.
- Produces two subcommands, run as `python -m storm_core <cmd>`:
  - `roster` — prints the discovered roster as JSON (`[{name,slug,description}, ...]`).
  - `build --report <path.json> [--reports-dir D] [--html-dir H]` — loads a StormReport
    JSON, writes `<reports-dir>/<slug>.md` (slug from topic) and `<html-dir>/<slug>.html`,
    and prints the two written paths (one per line). Creates dirs as needed. Slug uses the
    same rule as the rest of the repo: lowercase, non-word→removed, spaces/underscores→`-`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_storm_cli.py
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper"
            "/.claude/worktrees/bold-sammet-8c78b3")
PY = "/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python"


def _run(args, **kw):
    env = {"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"}
    return subprocess.run([PY, "-m", "storm_core", *args], cwd=REPO, env=env,
                          capture_output=True, text=True, **kw)


def test_roster_subcommand_emits_json(tmp_path, monkeypatch):
    (tmp_path / "a.md").write_text("---\nname: al\ndescription: d\n---\n", encoding="utf-8")
    env = {"PYTHONPATH": "src", "PATH": "/usr/bin:/bin", "STORM_ROSTER_DIR": str(tmp_path)}
    out = subprocess.run([PY, "-m", "storm_core", "roster"], cwd=REPO, env=env,
                         capture_output=True, text=True)
    data = json.loads(out.stdout)
    assert data == [{"name": "al", "slug": "a", "description": "d"}]


def test_build_writes_note_and_html(tmp_path):
    report = {
        "topic": "Zakat Advisory", "mode": "idea", "summary": "s", "verdict": "KEEP",
        "lenses": ["Operator"], "findings": [], "contradictions": [],
        "halal_note": "", "generated": "2026-07-06",
    }
    rj = tmp_path / "r.json"
    rj.write_text(json.dumps(report), encoding="utf-8")
    reports = tmp_path / "reports"
    html = tmp_path / "html"
    out = _run(["build", "--report", str(rj), "--reports-dir", str(reports),
                "--html-dir", str(html)])
    assert out.returncode == 0, out.stderr
    assert (reports / "zakat-advisory.md").exists()
    assert (html / "zakat-advisory.html").exists()
    assert "zakat-advisory.md" in out.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `$PYTEST tests/test_storm_cli.py -v`
Expected: FAIL (no `__main__`; `python -m storm_core` errors, assertions fail).

- [ ] **Step 3: Write the implementation**

```python
# src/storm_core/__main__.py
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from storm_core import config
from storm_core.html_render import render_html
from storm_core.models import StormReport
from storm_core.report import build_note_markdown
from storm_core.roster import discover_roster


def _slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "untitled"


def _cmd_roster(_args) -> int:
    data = [p.model_dump() for p in discover_roster()]
    print(json.dumps(data))
    return 0


def _cmd_build(args) -> int:
    report = StormReport.model_validate_json(Path(args.report).read_text(encoding="utf-8"))
    reports_dir = Path(args.reports_dir) if args.reports_dir else config.REPORTS_DIR
    html_dir = Path(args.html_dir) if args.html_dir else config.HTML_OUT_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(report.topic)
    note_path = reports_dir / f"{slug}.md"
    html_path = html_dir / f"{slug}.html"
    note_path.write_text(build_note_markdown(report), encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    print(note_path)
    print(html_path)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="storm_core")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("roster")
    b = sub.add_parser("build")
    b.add_argument("--report", required=True)
    b.add_argument("--reports-dir")
    b.add_argument("--html-dir")
    args = parser.parse_args(argv)
    if args.cmd == "roster":
        return _cmd_roster(args)
    return _cmd_build(args)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `$PYTEST tests/test_storm_cli.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Run the whole storm suite + commit**

```bash
$PYTEST tests/test_storm_*.py -v   # expect all green (11 tests)
git add src/storm_core/__main__.py tests/test_storm_cli.py
git commit -m "feat(storm): storm_core CLI (roster + build)"
```

---

### Task 6: The STORM engine workflow (`idea` mode)

**Files:**
- Create: `.claude/workflows/storm.js`

**Interfaces:**
- Consumes (at runtime, via agents shelling out): `python -m storm_core roster`,
  `python -m storm_core build --report <json> --reports-dir <D> --html-dir <H>`.
- `args` shape (scalars/paths only — never a large object):
  `{ mode: "idea", topic: "<business idea>", voices: 3, scratch: "<abs scratch dir>" }`.

> **Note:** this is a JS orchestration script for the Workflow tool, not pytest-tested
> code. It is validated by the dry-run in Task 8. Keep every heavy artifact on disk:
> each lens agent writes its own file under `args.scratch`; later phases read those files.

- [ ] **Step 1: Write the workflow script**

Create `.claude/workflows/storm.js` with this exact content:

```javascript
export const meta = {
  name: 'storm-business-research',
  description: 'STORM multi-lens business research: cast lenses, map contradictions, verify, render a graded note + HTML',
  phases: [
    { title: 'Scope & Cast' },
    { title: 'Lenses' },
    { title: 'Contradiction Map' },
    { title: 'Synthesis' },
    { title: 'Verify' },
    { title: 'Render' },
  ],
}

const { mode, topic, voices = 3, scratch } = args
const ROLE_LENSES = ['Operator', 'Investor', 'Customer', 'Skeptic', 'Local-Market']

// Phase 0 — Scope & cast (reads live roster via the CLI, picks best-fit voices + Mufti)
phase('Scope & Cast')
const cast = await agent(
  `You are the casting + scoping step of a STORM business-research run.\n` +
  `Business topic: "${topic}".\n` +
  `1. Run: python -m storm_core roster   (cwd is the repo root; prefix with PYTHONPATH=src and use .venv/bin/python). It prints JSON of the available named personas.\n` +
  `2. Pick the ${voices} best-fit named voices for THIS topic from that roster (by their description). ALWAYS add the Mufti persona on top as a halal gate (do not count it against the ${voices}).\n` +
  `3. Tighten the topic into a one-line research scope.\n` +
  `Return JSON only.`,
  { phase: 'Scope & Cast', schema: {
      type: 'object',
      properties: {
        scope: { type: 'string' },
        named_voices: { type: 'array', items: { type: 'string' } },
        mufti_slug: { type: 'string' },
      },
      required: ['scope', 'named_voices', 'mufti_slug'],
  } })

const lenses = [...ROLE_LENSES, ...cast.named_voices, 'Mufti']

// Phase 1 — Lenses in parallel; each writes its OWN file (output-cap guardrail)
phase('Lenses')
await parallel(lenses.map((lens, i) => () =>
  agent(
    `You are the "${lens}" lens in a STORM business-research council.\n` +
    `Scope: ${cast.scope}\n` +
    `Research this from YOUR perspective using BOTH the local Obsidian vaults (grep the ` +
    `Business Personas and AI & Development vaults first) AND live web search for current, ` +
    `dated evidence. If you are the Mufti lens, judge halal permissibility and give a clear ` +
    `PASS/FAIL with reasoning.\n` +
    `Write your findings (claims + dated sources + your stance) to the file ` +
    `${scratch}/lens-${i}-${lens.replace(/[^a-z0-9]/gi, '_')}.md . Return only the file path.`,
    { phase: 'Lenses', label: `lens:${lens}` }
  )
))

// Phase 2 — Contradiction map (reads all lens files)
phase('Contradiction Map')
await agent(
  `Read every file matching ${scratch}/lens-*.md . Produce a contradiction map: for each ` +
  `point of disagreement, name the topic, each lens's stance, and who has stronger evidence. ` +
  `Write it to ${scratch}/contradictions.md . Return only the file path.`,
  { phase: 'Contradiction Map' }
)

// Phase 3 — Synthesis into a StormReport JSON (schema-validated)
phase('Synthesis')
const report = await agent(
  `Read ${scratch}/lens-*.md and ${scratch}/contradictions.md . Synthesize a single ` +
  `StormReport for the business "${topic}" (mode "${mode}"). Rank findings by reliability ` +
  `(1-10). Give a verdict of exactly KEEP, WATCHLIST, or CUT (a Mufti FAIL forces CUT). ` +
  `Grade each piece of evidence A/B/C. Include the halal judgement in halal_note. ` +
  `Set generated to today's date in YYYY-MM-DD.`,
  { phase: 'Synthesis', schema: {
      type: 'object',
      properties: {
        topic: { type: 'string' }, mode: { type: 'string' }, summary: { type: 'string' },
        verdict: { type: 'string', enum: ['KEEP', 'WATCHLIST', 'CUT'] },
        lenses: { type: 'array', items: { type: 'string' } },
        findings: { type: 'array', items: { type: 'object' } },
        contradictions: { type: 'array', items: { type: 'object' } },
        halal_note: { type: 'string' }, generated: { type: 'string' },
      },
      required: ['topic', 'mode', 'summary', 'verdict', 'generated'],
  } })

// Phase 4 — Adversarial verify (top-tier model); rewrites the report file if it corrects anything
phase('Verify')
const reportPath = `${scratch}/report.json`
const verified = await agent(
  `Here is a draft StormReport JSON:\n${JSON.stringify(report)}\n\n` +
  `Adversarially fact-check its TOP findings against the local vault AND live web. For each ` +
  `piece of evidence set status to confirmed, corrected, or demoted, fixing claims/sources as ` +
  `needed. If verification weakens the case, lower the verdict. Write the final corrected ` +
  `StormReport JSON to ${reportPath} and return only that path.`,
  { phase: 'Verify', model: 'opus' }
)

// Phase 5 — Render note + HTML via the CLI
phase('Render')
const rendered = await agent(
  `Run, from the repo root with PYTHONPATH=src and .venv/bin/python:\n` +
  `python -m storm_core build --report ${reportPath}\n` +
  `Then report the two written file paths (the vault note and the HTML briefing).`,
  { phase: 'Render' }
)

return { report: reportPath, rendered }
```

- [ ] **Step 2: Syntax-check the script**

Run: `node --check .claude/workflows/storm.js`
Expected: no output, exit 0 (valid JS).

- [ ] **Step 3: Commit**

```bash
git add .claude/workflows/storm.js
git commit -m "feat(storm): idea-mode engine workflow (cast -> lenses -> verify -> render)"
```

---

### Task 7: The `/storm` front-door skill

**Files:**
- Create: `.claude/skills/storm/SKILL.md`

**Interfaces:**
- Consumes: the `storm-business-research` workflow; the `storm_core` CLI.
- Produces: a skill that, on `/storm`, (1) picks a mode (MVP: only `idea` is live —
  say so if another is asked), (2) asks for the business idea, (3) asks for the number of
  named voices (**default 3**), (4) creates a scratch dir, (5) invokes the workflow via the
  `Workflow` tool with `{mode, topic, voices, scratch}`, (6) relays the rendered note + HTML
  paths.

- [ ] **Step 1: Write the skill**

Create `.claude/skills/storm/SKILL.md`:

```markdown
---
name: storm
description: Run a STORM multi-perspective business-research pass on an idea — cast expert lenses that deliberately disagree, map their contradictions, adversarially fact-check, and produce a graded vault note + HTML briefing. Use for evaluating a business idea/opportunity, or when the user invokes /storm.
trigger: /storm
---

# Skill: STORM Business Research

**Trigger:** `/storm [business idea]`

Multi-lens business research modeled on Stanford's STORM method. It borrows
expertise you don't have — a council of lenses that contradict each other — then
verifies and grades the result. See
`docs/superpowers/specs/2026-07-06-storm-business-research-design.md`.

## Modes

Only **`idea`** (evaluate one business idea) is live in the MVP. If the user asks
for `gap` / `rescore` / `research`, say those modes are designed but not yet
built, and offer to run `idea` instead.

## Steps

1. **Get the idea.** If the user didn't name a business idea after `/storm`, ask
   for one.
2. **Ask the voice count.** "How many named expert voices should I cast? (default
   3 — Mufti is always added on top as the halal gate.)" Use 3 if they don't say.
3. **Make a scratch dir** under the session scratchpad, e.g.
   `<scratch>/storm-<slug>/`.
4. **Invoke the engine.** Call the `Workflow` tool:
   `Workflow({ name: "storm-business-research", args: { mode: "idea", topic: "<idea>", voices: <n>, scratch: "<abs scratch dir>" } })`.
   The workflow casts lenses (auto best-fit + Mufti), runs them on vault+web,
   maps contradictions, adversarially verifies, and renders outputs.
5. **Relay results.** Report the verdict (KEEP/WATCHLIST/CUT) and the two written
   paths: the graded vault note in the Opportunity-Catalog `STORM-Reports/` folder
   and the HTML briefing under `output/storm/`. Note that the vault note is not in
   git (personal vault) — that's expected.

## Guardrails

- Mufti's halal judgement is a hard gate — a FAIL forces a CUT verdict.
- Never fabricate evidence; an unverifiable claim is demoted, not dressed up.
- Nothing captured is committed — reports live in the iCloud vault / gitignored
  `output/`.
```

- [ ] **Step 2: Verify frontmatter parses**

Run: `head -5 .claude/skills/storm/SKILL.md`
Expected: shows the `---` frontmatter with `name: storm` and `trigger: /storm`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/storm/SKILL.md
git commit -m "feat(storm): /storm front-door skill (idea mode)"
```

---

### Task 8: End-to-end dry-run + docs

**Files:**
- Modify: `CLAUDE.md` (add `storm` to the `.claude/` assets skills list)

**Interfaces:** none (integration validation + docs).

- [ ] **Step 1: Full offline suite still green**

Run: `PYTHONPATH=src /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest -q`
Expected: all prior tests + 11 new storm tests pass.

- [ ] **Step 2: Live dry-run of `idea` mode**

Invoke the skill on one known catalog business:
`/storm Zakat & Islamic-Finance Advisory` — accept the default of 3 voices.

Expected: the workflow completes all six phases; then verify the outputs exist and
are grounded:

```bash
ls -1 output/storm/*.html
V="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Business Personas/Opportunity-Catalog/STORM-Reports"
ls -1 "$V"/*.md
```

Eyeball the note: it must have a KEEP/WATCHLIST/CUT verdict, findings with
reliability scores, a contradiction map, dated evidence with A/B/C grades, and a
Mufti halal note. If any lens fabricated a source, that's a verify-phase failure —
fix the verify prompt before proceeding.

- [ ] **Step 3: Document the asset in CLAUDE.md**

Add to the `**Skills**` list under `## `.claude/` assets` in `CLAUDE.md`:

```markdown
- `storm` (`/storm`) — STORM multi-perspective business-research engine: casts
  expert lenses (auto best-fit from the dynamic persona roster + Mufti halal
  gate), maps their contradictions, adversarially fact-checks, and renders a
  graded vault note + HTML briefing. Thin skill → `storm-business-research`
  workflow → `storm_core` CLI. See
  `docs/superpowers/specs/2026-07-06-storm-business-research-design.md`. MVP is
  `idea` mode; `gap`/`rescore`/`research` are designed but not yet built.
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(storm): document the /storm skill in CLAUDE.md assets"
```

---

## Self-Review

**Spec coverage:**
- STORM 6-phase engine → Task 6 workflow (all six phases present). ✓
- Configurable role lenses + dynamic named voices → Task 2 (roster) + Task 6 (ROLE_LENSES + cast). ✓
- Casting: N best-fit default 3 asked each run, +Mufti always → Task 7 step 2 (skill asks) + Task 6 Phase 0 (cast). ✓
- Verdict KEEP/WATCHLIST/CUT + A/B/C grades → Task 1 enums, enforced in Task 6 synthesis schema. ✓
- Hybrid evidence (vault + web) → Task 6 lens prompt. ✓
- Adversarial verify on top tier → Task 6 Phase 4 (`model: 'opus'`). ✓
- Outputs: graded vault note + HTML → Tasks 3, 4, 5 (CLI writes both). ✓
- Reports to `STORM-Reports/`, HTML to gitignored `output/storm/` → Task 1 config. ✓
- Guardrails (own-file per agent, no big args objects, Mufti hard veto, nothing committed) →
  Task 6 notes + Task 7 guardrails. ✓
- MVP = idea only; other modes out of scope → stated in header + Task 7. ✓

**Placeholder scan:** no TBD/TODO; every code + test step has complete content. ✓

**Type consistency:** `StormReport` fields identical across Tasks 1/3/4/5; CLI `build`
signature (`--report/--reports-dir/--html-dir`) matches Task 6 render call and Task 5 test;
`discover_roster` return (`Persona{name,slug,description}`) matches the CLI `roster` JSON and
Task 6 casting. ✓

**Out-of-scope guard:** marker-merge / in-place editing intentionally deferred (belongs to
the future `rescore` plan), so it is not referenced by any MVP task. ✓
```
