# Stage 1 — Explain One Company Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `ladder explain <TICKER>` — show one company's whole journey through the screen: every gate, the real number, pass or fail, where it stopped, and what the lectures say about it.

**Architecture:** A pure reader. Everything it prints already exists in a stored `ladder-<as-of>.json` (verdict, four gate results, six rule outcomes, ten observations per company). It computes nothing and fetches nothing. Lecture evidence is joined from an optional vault directory; without it the gate journey still prints in full.

**Tech Stack:** Python 3.11+, pytest, the existing `soic_ladder` package.

## Why this is Stage 1

"Explain one company" and "filter Nifty 500" are the same machine at different
N. Stage 2 (the weekly short list) is this explainer applied to the handful of
companies that changed. Building the per-company view first means Stage 2 reuses
it rather than growing a second, divergent renderer.

## Global Constraints

- **Never hardcode a personal or machine-specific path.** The vault lives in one
  user's iCloud. This repo is being published publicly. A hardcoded absolute path
  is the exact defect class already fixed twice in this codebase (a stale
  worktree path in a test, a positional column index in a generator). The vault
  is supplied via `--vault` or the `SOIC_VAULT_DIR` environment variable, and the
  command works fully without either.
- Read-only. No network, no writes to `runs/`, no rulebook edits.
- Python 3.11+ (`pyproject.toml` requires `>=3.11`). No backslash inside an
  f-string expression.
- Branch off `main`, not off `feat/public-split` — that branch carries the
  unrelated public/private split.
- Output is plain text to stdout. No colour libraries, no new dependencies.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/soic_ladder/explain.py` | **Create.** Turn one company's stored record (+ optional vault evidence) into printable lines. Pure functions, no I/O beyond reading the files it is given. |
| `tests/test_explain.py` | **Create.** Synthetic records; the missing-company and missing-vault paths; the stopped-at-gate logic. |
| `src/soic_ladder/cli.py` | **Modify.** Add an `explain` subparser and dispatch. |

---

### Task 1: The explainer core

**Files:**
- Create: `src/soic_ladder/explain.py`
- Test: `tests/test_explain.py`

**Interfaces:**
- Consumes: a stored run file shaped `[{"company", "final", "gates": [{"gate", "verdict", "outcomes": [{"rule_id", "metric", "value", "check_rule", "outcome", "display_text"}]}], "observations": [{"metric", "value", "reference_band", "within_band", "display_text"}]}]`.
- Produces:
  `load_company(run_path: Path, ticker: str) -> Optional[dict]`;
  `first_failing_gate(record: dict) -> Optional[str]`;
  `render(record: dict, evidence: Optional[str] = None) -> str`;
  `GATE_ORDER: List[str]`.

- [ ] **Step 1: Branch off main**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder && git checkout main && git pull -q && git checkout -b feat/explain
```
Expected: `Switched to a new branch 'feat/explain'`

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_explain.py
import json
from pathlib import Path

from soic_ladder.explain import (
    GATE_ORDER, first_failing_gate, load_company, render)


def _record(company="AAA", final="CANDIDATE", gates=None, obs=None):
    gates = gates if gates is not None else {"G0": "PASS", "G1": "PASS",
                                             "G3": "PASS", "G8": "PASS"}
    return {
        "company": company,
        "final": final,
        "gates": [{"gate": g, "verdict": v, "outcomes": [
            {"rule_id": f"{g.lower()}_rule-001", "metric": "sales_growth_yoy_pct",
             "value": 17.5, "check_rule": ">= 15",
             "outcome": "PASS" if v == "PASS" else "FAIL",
             "display_text": f"a {g} rule"}]} for g, v in gates.items()],
        "observations": obs if obs is not None else [
            {"metric": "stock_pe", "value": 51.9, "reference_band": "between 15 35",
             "within_band": False, "display_text": "Price to earnings"}],
    }


def _write(p: Path, records):
    p.write_text(json.dumps(records))
    return p


def test_load_company_finds_and_misses(tmp_path: Path):
    run = _write(tmp_path / "r.json", [_record("AAA"), _record("BBB")])
    assert load_company(run, "BBB")["company"] == "BBB"
    assert load_company(run, "ZZZ") is None


def test_load_company_is_case_insensitive(tmp_path: Path):
    run = _write(tmp_path / "r.json", [_record("AAA")])
    assert load_company(run, "aaa")["company"] == "AAA"


def test_first_failing_gate_reports_where_it_stopped():
    rec = _record(gates={"G0": "PASS", "G1": "FAIL", "G3": "FAIL", "G8": "PASS"})
    assert first_failing_gate(rec) == "G1"


def test_first_failing_gate_is_none_when_all_pass():
    assert first_failing_gate(_record()) is None


def test_gate_order_is_the_screens_order():
    assert GATE_ORDER == ["G0", "G1", "G3", "G8"]


def test_render_shows_every_gate_with_its_number():
    out = render(_record())
    assert "AAA" in out and "CANDIDATE" in out
    for gate in GATE_ORDER:
        assert gate in out
    assert "17.5" in out          # the actual measured value
    assert ">= 15" in out         # the bar it was measured against


def test_render_names_the_stopping_gate():
    out = render(_record(final="WATCH",
                         gates={"G0": "PASS", "G1": "FAIL", "G3": "PASS", "G8": "PASS"}))
    assert "G1" in out
    assert "stopped" in out.lower()


def test_render_marks_an_observation_outside_its_band():
    out = render(_record())
    assert "stock_pe" in out
    assert "51.9" in out
    assert "between 15 35" in out


def test_render_without_evidence_still_shows_the_journey():
    out = render(_record(), evidence=None)
    assert "G0" in out
    assert "no lecture evidence" in out.lower()


def test_render_includes_evidence_when_given():
    out = render(_record(), evidence="DIVISLAB is doubted by PALLOC")
    assert "PALLOC" in out
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_explain.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_ladder.explain'`

- [ ] **Step 4: Write the implementation**

```python
# src/soic_ladder/explain.py
"""One company's whole journey through the screen, in plain text.

A pure reader. Everything printed here already exists in a stored run file --
the verdict, the four gate results, each rule's measured value and the bar it
was measured against, and the observations with their reference bands. This
module computes nothing and fetches nothing; it makes an existing record
legible.

Stage 2 (the weekly short list) is this renderer applied to the few companies
that changed between runs, so the per-company view lives here once rather than
being reimplemented per caller.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

# The screen's own order. G2/G4/G5/G6/G7 are deliberately unoccupied, so a
# company is only ever measured by these four.
GATE_ORDER: List[str] = ["G0", "G1", "G3", "G8"]


def load_company(run_path: Path, ticker: str) -> Optional[Dict]:
    """One company's record from a stored run, or None. Ticker match is
    case-insensitive so `ladder explain navinfluor` works."""
    want = ticker.strip().upper()
    for record in json.loads(Path(run_path).read_text(encoding="utf-8")):
        if str(record.get("company", "")).upper() == want:
            return record
    return None


def _gate_verdicts(record: Dict) -> Dict[str, str]:
    return {g["gate"]: g["verdict"] for g in record.get("gates") or []}


def first_failing_gate(record: Dict) -> Optional[str]:
    """The gate a company stopped at, in the screen's own order -- the single
    most useful fact when asking why a company is not on the list."""
    verdicts = _gate_verdicts(record)
    for gate in GATE_ORDER:
        if verdicts.get(gate) not in (None, "PASS"):
            return gate
    return None


def _fmt(value) -> str:
    if value is None:
        return "no data"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def render(record: Dict, evidence: Optional[str] = None) -> str:
    """The full journey, plus lecture evidence when a vault was supplied."""
    lines: List[str] = []
    company = record.get("company", "?")
    final = record.get("final", "?")
    lines.append(f"{company} — {final}")
    lines.append("=" * max(24, len(company) + len(final) + 3))
    lines.append("")

    stopped = first_failing_gate(record)
    if stopped:
        lines.append(f"Stopped at {stopped}.")
    else:
        lines.append("Cleared every gate.")
    lines.append("")

    by_gate = {g["gate"]: g for g in record.get("gates") or []}
    lines.append("GATES")
    for gate in GATE_ORDER:
        block = by_gate.get(gate)
        if block is None:
            lines.append(f"  {gate}  (not evaluated)")
            continue
        mark = "PASS" if block["verdict"] == "PASS" else block["verdict"]
        flag = "  <-- stopped here" if gate == stopped else ""
        lines.append(f"  {gate}  {mark}{flag}")
        for outcome in block.get("outcomes") or []:
            lines.append(
                f"       {outcome.get('metric','?')} = "
                f"{_fmt(outcome.get('value'))}  "
                f"needs {outcome.get('check_rule','?')}  "
                f"-> {outcome.get('outcome','?')}")
    lines.append("")

    observations = record.get("observations") or []
    if observations:
        lines.append("OBSERVATIONS (context only — these never change a verdict)")
        for obs in observations:
            within = obs.get("within_band")
            state = ("within band" if within is True
                     else "OUTSIDE band" if within is False else "not measurable")
            lines.append(
                f"  {obs.get('metric','?')} = {_fmt(obs.get('value'))}  "
                f"(band {obs.get('reference_band','?')}) — {state}")
        lines.append("")

    lines.append("WHAT THE LECTURES SAY")
    lines.append(evidence.rstrip() if evidence
                 else "  no lecture evidence available "
                      "(pass --vault or set SOIC_VAULT_DIR)")
    return "\n".join(lines)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_explain.py -v`
Expected: PASS, 10 passed

- [ ] **Step 6: Commit**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder
git add src/soic_ladder/explain.py tests/test_explain.py
git commit -m "feat: explain one company's journey through the screen

A pure reader over a stored run: every gate, the measured value, the bar it
was measured against, and where the company stopped. Stage 2's weekly brief
will reuse this rather than growing a second renderer."
```

---

### Task 2: Vault evidence and the CLI

**Files:**
- Modify: `src/soic_ladder/explain.py` (add the vault reader)
- Modify: `tests/test_explain.py` (add its tests)
- Modify: `src/soic_ladder/cli.py` (add the `explain` subparser and dispatch)

**Interfaces:**
- Consumes: `render()`, `load_company()` from Task 1.
- Produces: `vault_evidence(vault_dir: Optional[Path], ticker: str) -> Optional[str]`;
  `resolve_vault(explicit: Optional[str]) -> Optional[Path]`.

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_explain.py
import pytest
from soic_ladder.explain import resolve_vault, vault_evidence


def test_vault_evidence_reads_the_company_note(tmp_path: Path):
    companies = tmp_path / "companies"
    companies.mkdir()
    (companies / "AAA.md").write_text(
        "---\nticker: AAA\n---\n\n# AAA\n\n"
        "**Lecture verdicts:** **doubt** 2 · **support** 1\n\n"
        "## What the lectures say\n\n### PALLOC\n\nnamed as a cautionary case\n")
    out = vault_evidence(tmp_path, "AAA")
    assert out is not None
    assert "PALLOC" in out
    assert "cautionary" in out


def test_vault_evidence_is_none_when_the_note_is_absent(tmp_path: Path):
    (tmp_path / "companies").mkdir()
    assert vault_evidence(tmp_path, "ZZZ") is None


def test_vault_evidence_is_none_when_no_vault_given():
    assert vault_evidence(None, "AAA") is None


def test_vault_evidence_survives_a_missing_companies_dir(tmp_path: Path):
    assert vault_evidence(tmp_path, "AAA") is None


def test_resolve_vault_prefers_the_explicit_argument(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SOIC_VAULT_DIR", str(tmp_path / "from_env"))
    assert resolve_vault(str(tmp_path)) == tmp_path


def test_resolve_vault_falls_back_to_the_environment(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SOIC_VAULT_DIR", str(tmp_path))
    assert resolve_vault(None) == tmp_path


def test_resolve_vault_is_none_when_neither_is_set(monkeypatch):
    monkeypatch.delenv("SOIC_VAULT_DIR", raising=False)
    assert resolve_vault(None) is None
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_explain.py -v`
Expected: FAIL — `ImportError: cannot import name 'resolve_vault'`

- [ ] **Step 3: Add the vault reader**

```python
# append to src/soic_ladder/explain.py
import os

# The vault is one user's Obsidian directory, typically inside iCloud. It is
# NEVER hardcoded: this package is published publicly, and a machine-specific
# absolute path is the defect class already fixed twice in this codebase.
VAULT_ENV = "SOIC_VAULT_DIR"


def resolve_vault(explicit: Optional[str]) -> Optional[Path]:
    """Explicit --vault wins; otherwise the environment; otherwise nothing."""
    if explicit:
        return Path(explicit).expanduser()
    from_env = os.environ.get(VAULT_ENV)
    return Path(from_env).expanduser() if from_env else None


def vault_evidence(vault_dir: Optional[Path], ticker: str) -> Optional[str]:
    """The company note's body, if a vault was supplied and holds one.

    Returns None rather than raising for every absent case -- no vault, no
    companies directory, no note. The gate journey is useful on its own and
    must never be blocked by missing optional evidence.
    """
    if vault_dir is None:
        return None
    note = Path(vault_dir) / "companies" / f"{ticker.strip().upper()}.md"
    if not note.is_file():
        return None
    text = note.read_text(encoding="utf-8")
    if text.startswith("---"):          # drop YAML frontmatter
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return "\n".join("  " + line if line.strip() else line
                     for line in text.strip().splitlines())
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_explain.py -v`
Expected: PASS, 17 passed

- [ ] **Step 5: Add the CLI subcommand**

In `src/soic_ladder/cli.py`, after the `diff` subparser block, add:

```python
    exp = sub.add_parser("explain", help="one company's journey through the screen")
    exp.add_argument("ticker")
    exp.add_argument("--run", required=True, help="path to a stored ladder-<as-of>.json")
    exp.add_argument("--vault", default=None,
                     help="Stock Framework vault dir (or set SOIC_VAULT_DIR)")
```

and in the dispatch, beside the `diff` branch (the same early position, before
any snapshot-store setup):

```python
    if args.command == "explain":
        from .explain import load_company, render, resolve_vault, vault_evidence
        record = load_company(Path(args.run), args.ticker)
        if record is None:
            print(f"ERROR: {args.ticker} is not in {args.run}", file=sys.stderr)
            return 1
        evidence = vault_evidence(resolve_vault(args.vault), args.ticker)
        print(render(record, evidence))
        return 0
```

- [ ] **Step 6: Run it against real data, without a vault**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder
.venv/bin/ladder explain CPPLUS --run runs/out/ladder-2026-08-22.json
```
Expected: `CPPLUS — CANDIDATE`, all four gates PASS with their measured values,
the observations block showing its cash-conversion figures outside band, and the
"no lecture evidence available" line. Exit 0.

- [ ] **Step 7: Run it with the vault**

```bash
.venv/bin/ladder explain NAVINFLUOR --run runs/out/ladder-2026-08-22.json \
  --vault ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/Stock\ Framework
```
Expected: the same journey plus a WHAT THE LECTURES SAY section naming real
lectures. Report what it shows.

- [ ] **Step 8: Confirm the unknown-ticker path**

```bash
.venv/bin/ladder explain NOTAREALTICKER --run runs/out/ladder-2026-08-22.json; echo "exit=$?"
```
Expected: a clear error naming the ticker and the run file, `exit=1`.

- [ ] **Step 9: Run the full suite**

Run: `.venv/bin/python -m pytest -q >/dev/null 2>&1; echo "exit=$?"`
Expected: `0`.

- [ ] **Step 10: Commit**

```bash
git add src/soic_ladder/explain.py tests/test_explain.py src/soic_ladder/cli.py
git commit -m "feat: ladder explain <TICKER>

Joins the stored gate journey to the vault's per-company lecture evidence.
The vault is optional and never hardcoded -- --vault or SOIC_VAULT_DIR, and
the journey prints fully without either, because this package is published
publicly and a machine-specific path is the defect class already fixed twice
here."
```

---

## Self-Review

**Spec coverage.** Stage 1 of `docs/reassessment/ROADMAP.md` asks for one
command that shows a company's whole journey and joins the lecture evidence.
Task 1 renders the journey; Task 2 adds the evidence and the CLI. Nothing in
Stage 1 is left unimplemented.

**Placeholders.** None: every code step carries complete code, every run step an
exact command and its expected output.

**Type consistency.** `load_company -> Optional[dict]`, `first_failing_gate ->
Optional[str]`, `render(record, evidence=None) -> str`, `resolve_vault(explicit)
-> Optional[Path]`, `vault_evidence(vault_dir, ticker) -> Optional[str]` are
used with those exact signatures in the tests, the module and the CLI branch.

**Deliberately not here.** Ranking, capping, and the weekly brief are Stage 2.
The `procedure` checklist that would tell a reader what to *do* about a surfaced
company needs the claims graph and is Stage 3.
