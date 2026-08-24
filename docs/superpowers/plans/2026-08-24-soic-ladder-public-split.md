# soic-ladder Public/Private Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the `soic-ladder` engine as a public repo (restoring free CI) while the licensed rulebook stays private and unpublished.

**Architecture:** The engine already takes `--rules` and `--registry` as arguments, so no code change is needed to run against an external rulebook. The work is: sever the test suite's dependency on the two private files, build a guarded export that provably contains no licensed text, then publish a fresh repo with no prior history.

**Tech Stack:** Python 3.11+, pytest, `gh` CLI, git.

## Why a fresh repo rather than a history rewrite

Owner's decision. `git filter-repo` over 14+ rulebook commits is irreversible and one missed blob publishes licensed course text permanently. A fresh repo cannot leak history it never had. `soic-ladder` stays private and untouched, keeping every commit, the rulebook, and `runs/`.

## What is private and why

| File | Why private |
|---|---|
| `rulebook/soic-ladder-rules-v1.yaml` | Carries 16 `provenance.quote` fields. The file's own header states this is verbatim licensed SOIC course text kept only for internal traceability and never to appear in user-facing output. |
| `rulebook/vendor/decision-rules-v2.yaml` | Vendored from the owner's private Obsidian vault; its comments carry extended analysis of the same paid course material. |

`rulebook/vendor/metric-registry.yaml` is **public-safe** — 183 lines of metric key → screener label → fetchable status, zero course text (verified: 0 matches for quote/verbatim/"SOIC states"). It ships public because the engine and its tests need it.

`rulebook/vendor/VENDORED.md` stays private: it is a manifest of the private files, including their hashes.

## Global Constraints

- **Never copy either private file, or any text from them, into the public tree.** This is the whole point of the exercise.
- Python 3.11+ (`pyproject.toml` requires `>=3.11`; CI pins `3.11`).
- No `match`, no `X | Y` unions in code shared with the 3.9-targeting sibling repo — not applicable here, but keep imports conservative.
- The private repo `soic-ladder` must remain private and must not be rewritten or force-pushed.
- The engine's default `--rules` path may point at a file absent from the public tree; the CLI already handles a missing rulebook (`tests/test_cli.py:191-205` pins that behaviour). Do not "fix" that by inventing a default rulebook.
- Do not publish anything until Task 2's guard passes.

---

## File Structure

| File | Responsibility |
|---|---|
| `tests/private/test_shipped_rulebook.py` | **Create (private repo).** The one tripwire test that pins what the shipped rulebook contains. It is a *rulebook* test, not an *engine* test. |
| `tests/private/test_vendored_files.py` | **Create (private repo).** The vendored-file presence and hash checks currently in `test_scaffold.py`. |
| `tests/test_rulebook.py` | **Modify.** Remove the shipped-rulebook tripwire (moves to `tests/private/`). 35 synthetic-fixture tests remain. |
| `tests/test_scaffold.py` | **Modify.** Keep the pinned-dependency import test; move the two vendored-file tests out. |
| `pyproject.toml` | **Modify.** Default pytest run excludes `tests/private`. |
| `scripts/export_public.py` | **Create.** Produces the public tree from an explicit allowlist and **refuses to run** if any licensed marker is found in the output. |
| `tests/test_export_public.py` | **Create.** Proves the guard actually blocks a leak. |

---

### Task 1: Sever the engine tests from the private files

**Files:**
- Create: `tests/private/test_shipped_rulebook.py`, `tests/private/test_vendored_files.py`, `tests/private/__init__.py`
- Modify: `tests/test_rulebook.py`, `tests/test_scaffold.py`, `pyproject.toml`
- Work in: `~/Documents/workspace/Claude_Code/soic-ladder` on a new branch `feat/public-split`

**Interfaces:**
- Produces: a test suite where `pytest --ignore=tests/private` passes with **no** reference to `soic-ladder-rules-v1.yaml` or `decision-rules-v2.yaml`.

- [ ] **Step 1: Branch**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder && git checkout main && git pull && git checkout -b feat/public-split
```
Expected: `Switched to a new branch 'feat/public-split'`

- [ ] **Step 2: Write the failing guard test**

This test is the whole point of the task — it asserts the engine suite has no private-file dependency.

```python
# tests/test_no_private_deps.py
"""The public repo ships tests/ but NOT the licensed rulebook. Any engine
test that reads those files would fail for everyone outside this machine,
and would signal that licensed content is load-bearing for the engine."""
from pathlib import Path

PRIVATE_NAMES = ("soic-ladder-rules-v1.yaml", "decision-rules-v2.yaml", "VENDORED.md")
TESTS = Path(__file__).resolve().parent


def test_no_engine_test_references_a_private_file():
    offenders = []
    for path in sorted(TESTS.glob("*.py")):
        text = path.read_text()
        for name in PRIVATE_NAMES:
            if name in text:
                offenders.append(f"{path.name} references {name}")
    assert offenders == [], (
        "these engine tests depend on files that stay private: " + "; ".join(offenders))
```

- [ ] **Step 3: Run it to confirm it fails**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_no_private_deps.py -v`
Expected: FAIL, listing `test_rulebook.py references soic-ladder-rules-v1.yaml` and `test_scaffold.py references decision-rules-v2.yaml` (and `VENDORED.md`).

- [ ] **Step 4: Move the shipped-rulebook tripwire into `tests/private/`**

Create `tests/private/__init__.py` (empty). Then cut the `REAL_RULEBOOK` constant and the whole
`test_the_shipped_v1_rulebook_loads_with_six_rules_and_ten_observations` function out of
`tests/test_rulebook.py` and paste them into a new file, adding the imports it needs:

```python
# tests/private/test_shipped_rulebook.py
"""Tripwire on the SHIPPED rulebook — a RULEBOOK test, not an engine test.

It lives here because the rulebook it pins is licensed course material that
stays private. The public engine repo ships tests/ but not this directory.
Run it with: pytest tests/private
"""
from pathlib import Path

from soic_ladder.rulebook import load_observations, load_rulebook

REGISTRY = (Path(__file__).resolve().parents[2]
            / "rulebook" / "vendor" / "metric-registry.yaml")
REAL_RULEBOOK = (Path(__file__).resolve().parents[2]
                 / "rulebook" / "soic-ladder-rules-v1.yaml")
```

…followed by the moved test function verbatim, unchanged. Do not alter its assertions.

- [ ] **Step 5: Move the vendored-file tests into `tests/private/`**

Cut `test_vendored_rule_files_are_present`, `_parse_vendored_hashes`, and any test using it out of
`tests/test_scaffold.py` into:

```python
# tests/private/test_vendored_files.py
"""Presence and hash checks for the vendored rule files — private, because
they and their manifest are the licensed material.
"""
```

…plus the moved functions verbatim, with their `parents[1]` path references changed to `parents[2]`
(they are one directory deeper now). Leave `test_pinned_dependency_is_importable` in
`tests/test_scaffold.py` — it imports a package, touches no private file.

- [ ] **Step 6: Exclude `tests/private` from the default run**

In `pyproject.toml`, under `[tool.pytest.ini_options]`, set `testpaths` so the default run covers the
engine suite only, and add a marker note. If `testpaths` already exists, edit it; if not, add:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
norecursedirs = ["tests/private"]
```

- [ ] **Step 7: Verify both suites**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder
.venv/bin/python -m pytest -q >/dev/null 2>&1; echo "engine suite exit: $?"
.venv/bin/python -m pytest tests/private -q >/dev/null 2>&1; echo "private suite exit: $?"
```
Expected: both `0`. The engine suite should now be 289 tests minus the ones moved (report the exact
number); the private suite should hold the moved tests and pass.

- [ ] **Step 8: Confirm the guard now passes**

Run: `.venv/bin/python -m pytest tests/test_no_private_deps.py -v`
Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add tests/ pyproject.toml
git commit -m "test: separate rulebook tests from engine tests

The engine suite must run without the licensed rulebook, because the public
repo will ship tests/ but not that file. Moves the shipped-rulebook tripwire
and the vendored-file hash checks into tests/private/, excluded from the
default run. Adds a guard test that fails if any engine test regains a
dependency on a private file."
```

---

### Task 2: A guarded public export

**Files:**
- Create: `scripts/export_public.py`, `tests/test_export_public.py`

**Interfaces:**
- Consumes: nothing from Task 1 except that the engine suite passes standalone.
- Produces: `export_public(dest: Path, repo_root: Path) -> list[Path]` (files written);
  `LICENSED_MARKERS: tuple[str, ...]`; `find_licensed_text(tree: Path) -> list[str]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export_public.py
from pathlib import Path
import pytest
from scripts.export_public import find_licensed_text, LICENSED_MARKERS


def test_guard_detects_a_provenance_quote(tmp_path: Path):
    """The guard must catch the exact shape of the thing we are protecting."""
    (tmp_path / "rules.yaml").write_text(
        "rules:\n  - id: x\n    provenance:\n"
        "      quote: \"some course sentence\"\n      ref: ABC 00:01:02\n")
    hits = find_licensed_text(tmp_path)
    assert hits, "a provenance.quote field must be detected"


def test_guard_detects_a_private_filename(tmp_path: Path):
    (tmp_path / "soic-ladder-rules-v1.yaml").write_text("rules: []\n")
    assert find_licensed_text(tmp_path)


def test_guard_passes_on_a_clean_tree(tmp_path: Path):
    (tmp_path / "ok.py").write_text("def f():\n    return 1\n")
    (tmp_path / "metric-registry.yaml").write_text(
        "metrics:\n  stock_pe:\n    label: \"Stock P/E\"\n    status: fetchable\n")
    assert find_licensed_text(tmp_path) == []


def test_markers_are_not_empty():
    assert len(LICENSED_MARKERS) >= 3
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_export_public.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.export_public'`

- [ ] **Step 3: Implement the exporter and its guard**

```python
#!/usr/bin/env python3
# scripts/export_public.py
"""Build the public engine tree from an explicit allowlist, then refuse to
emit it if anything licensed slipped in.

An allowlist, not a denylist: a denylist silently ships whatever nobody
thought to exclude, and the cost of one miss here is licensed course text
public forever in a repo that cannot be un-cloned.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import List

# Directories and files that go public. Anything not named here is excluded.
ALLOW = [
    "src",
    "tests",
    "scripts",
    ".github",
    "pyproject.toml",
    "README.md",
    ".gitignore",
    "rulebook/vendor/metric-registry.yaml",
]

# Never exported, even if an ALLOW entry would otherwise sweep them in.
DENY_NAMES = {
    "soic-ladder-rules-v1.yaml",
    "decision-rules-v2.yaml",
    "VENDORED.md",
}
DENY_DIRS = {"private", "runs", ".venv", "__pycache__", ".git", ".superpowers"}

LICENSED_MARKERS = (
    r"^\s*quote:\s*\S",                 # a provenance.quote field
    r"soic-ladder-rules-v1\.yaml",
    r"decision-rules-v2\.yaml",
    r"verbatim licensed",
)


def find_licensed_text(tree: Path) -> List[str]:
    """Every reason this tree must not be published. Empty list == clean."""
    hits: List[str] = []
    for path in sorted(Path(tree).rglob("*")):
        if not path.is_file():
            continue
        if set(path.parts) & DENY_DIRS:
            continue
        if path.name in DENY_NAMES:
            hits.append(f"{path}: private file present")
            continue
        if path.suffix not in {".py", ".yaml", ".yml", ".md", ".toml", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern in LICENSED_MARKERS:
            for m in re.finditer(pattern, text, re.M):
                line = text[:m.start()].count("\n") + 1
                hits.append(f"{path}:{line}: matches {pattern!r}")
    return hits


def export_public(dest: Path, repo_root: Path) -> List[Path]:
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    written: List[Path] = []
    for entry in ALLOW:
        src = Path(repo_root) / entry
        if not src.exists():
            continue
        out = dest / entry
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(
                src, out,
                ignore=shutil.ignore_patterns(*DENY_DIRS, *DENY_NAMES))
        else:
            shutil.copy2(src, out)
        written.append(out)
    return written


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    dest = repo_root.parent / "soic-ladder-engine"
    export_public(dest, repo_root)
    hits = find_licensed_text(dest)
    if hits:
        print("REFUSING TO PUBLISH -- licensed content found in the export:")
        for h in hits:
            print("  " + h)
        shutil.rmtree(dest)
        print(f"\nExport deleted. Fix the allowlist, then re-run.")
        return 1
    n = sum(1 for p in dest.rglob("*") if p.is_file())
    print(f"Export clean: {n} files at {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_export_public.py -v`
Expected: PASS, 4 passed

- [ ] **Step 5: Run the real export**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python scripts/export_public.py; echo "exit=$?"`
Expected: `Export clean: <N> files at .../soic-ladder-engine`, `exit=0`.
**If it exits 1, do not proceed** — read the reported hits and fix the allowlist.

- [ ] **Step 6: Verify the exported tree independently**

```bash
cd ../soic-ladder-engine
grep -rl "provenance" . | head        # expect: no rulebook, maybe code that parses it
ls rulebook/vendor/                    # expect: metric-registry.yaml ONLY
test -f rulebook/soic-ladder-rules-v1.yaml && echo "LEAK" || echo "rules file absent: good"
ls tests/private 2>/dev/null && echo "LEAK: private tests exported" || echo "private tests absent: good"
```
Expected: `rules file absent: good` and `private tests absent: good`.

- [ ] **Step 7: Prove the exported engine suite passes standalone**

```bash
cd ../soic-ladder-engine
python3 -m venv .venv && .venv/bin/pip install -q -e ".[dev]" && .venv/bin/python -m pytest -q
```
Expected: the same engine-suite count as Task 1 Step 7, exit 0 — proving the public repo's CI will
go green without the private rulebook.

- [ ] **Step 8: Commit (in the private repo)**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder
git add scripts/export_public.py tests/test_export_public.py
git commit -m "feat: guarded public export

Allowlist, not denylist -- a denylist ships whatever nobody thought to
exclude, and one miss publishes licensed course text irreversibly. The
exporter refuses to emit and deletes its own output if any licensed marker
survives into the tree."
```

---

### Task 3: Publish

**Files:** none in either repo — this task creates a new GitHub repo and pushes the verified export.

**This task performs an irreversible, outward-facing action.** Do not run Step 3 or later until
Task 2 Step 5 exited 0 and Step 6/7 both passed. **Stop and ask the owner to confirm before Step 3.**

- [ ] **Step 1: Re-run the guard immediately before publishing**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python scripts/export_public.py; echo "exit=$?"
```
Expected: `exit=0`. Re-running here rather than trusting the earlier run means the tree being
published is the tree that was just checked.

- [ ] **Step 2: Initialise the export as a git repo**

```bash
cd ../soic-ladder-engine
git init -q && git add -A && git status --porcelain | wc -l
```
Report the file count. Confirm no `rulebook/soic-ladder-rules-v1.yaml` appears in the listing.

- [ ] **Step 3: ASK THE OWNER TO CONFIRM, then create the public repo**

Show the owner the file count and the output of `git status --porcelain | grep rulebook`. Only on an
explicit yes:

```bash
cd ../soic-ladder-engine
git commit -q -m "feat: soic-ladder engine

Citation-pinned stock screening over a local screener snapshot store.
The rulebook is supplied at run time via --rules; none ships here."
gh repo create soic-ladder-engine --public --source=. --push
```

- [ ] **Step 4: Confirm CI goes green**

```bash
cd ../soic-ladder-engine && sleep 45 && gh run list --limit 3
```
Expected: a `success` conclusion. Public repos get unlimited Actions minutes, which is the reason
this split exists.

- [ ] **Step 5: Record the split in the private repo's README**

Add a short section to `~/Documents/workspace/Claude_Code/soic-ladder/README.md` stating that the
engine is mirrored publicly at `soic-ladder-engine`, that the rulebook is deliberately not published,
and that `scripts/export_public.py` regenerates the mirror. Commit.

---

## Self-Review

**Spec coverage.** Task 1 severs the test dependency; Task 2 builds and proves the guard; Task 3
publishes behind an explicit confirmation. The owner's decision (fresh repo, no history rewrite) is
honoured — nothing rewrites `soic-ladder`, which stays private.

**Placeholders.** None: every code step carries complete code, every command carries its expected
output, and the two private files are named explicitly rather than described.

**Type consistency.** `export_public(dest, repo_root) -> List[Path]`, `find_licensed_text(tree) ->
List[str]` and `LICENSED_MARKERS` are used with those exact signatures in both the tests and
`main()`.

**Known gap, recorded not hidden.** The guard is a regex scan, not a semantic one. It catches the
shapes we know about — `provenance.quote` fields, the two private filenames, the "verbatim licensed"
marker. It would not catch licensed prose pasted into a docstring in some other form. The allowlist
is the real protection; the guard is the second line.
