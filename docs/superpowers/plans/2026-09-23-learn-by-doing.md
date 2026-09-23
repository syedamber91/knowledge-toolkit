# /learn-by-doing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `/learn-by-doing` skill that turns any Udemy Vault course into one course project plus one hands-on mission per section, with every lecture covered and every quoted quirk verified against the transcript.

**Architecture:** The skill (`.claude/skills/learn-by-doing/SKILL.md`) holds the judgment work: picking the project, writing missions, grading proof. One stdlib-only script (`scripts/learn_by_doing.py`) holds the checks that must not depend on judgment: coverage (`check-map`), quote provenance (`check-quirks`), and progress (`status`). The skill must run the script and get zero errors before the owner sees a note.

**Tech Stack:** Python ≥3.9 stdlib (`argparse`, `re`, `pathlib`, `collections`), pytest, Obsidian markdown.

**Spec:** `docs/superpowers/specs/2026-09-23-learn-by-doing-design.md`

## Global Constraints

- Python `>=3.9` (from `pyproject.toml`). Use `from __future__ import annotations`. No `match` statements. No new dependencies.
- Default vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault`. Override order: `--vault` flag, then env `UDEMY_VAULT_DIR`, then the default.
- Vault layout read by the script: section notes `courses/<course>/<N>-<slug>.md` (list lectures as `[[lectures/<course>/<stem>|Title]]`), lecture notes `lectures/<course>/<stem>.md` with a `## Transcript` section of `[HH:MM:SS] text` per-minute blocks.
- Practice files: `practice/<course>/00-map.md`, `00-limits.md`, `00-log.md`, `NN-<slug>.md` (two-digit mission number).
- `Kind` is exactly one of `build`, `theory`, `skip`. `skip` needs a non-empty note.
- Mission `status` frontmatter is one of `not-started`, `in-progress`, `done`.
- Where tags: `[AWS]` company dev account, `[LOCAL]` owner's Mac, `[TRIAL]` personal Snowflake trial.
- Never ask for: access keys, passwords, tokens, session cookies, full ARNs with account IDs.
- Company AWS limits: never a "create IAM role" step; allowed region only; required tags + name prefix on every resource.
- Nothing in the vault is edited except `practice/<course>/**` and one link line in `courses/<course>.md`.

## Review Focus

1. **Lecture titles containing `[` `]`** (real: `[Important] AWS Console UI Update`) — link targets must still parse. Pinned in Task 1 (`test_bracketed_title_is_expected`) and Task 2 (`test_bracketed_title_in_quirk_link`).
2. **`|` inside a wikilink in a markdown table** must be written `\|` or Obsidian splits the cell — the parser must split only on unescaped pipes, and an empty last cell must survive. Pinned in Task 1 (`test_escaped_pipe_and_empty_note`).
3. **A quote that runs across a minute boundary** (transcripts split mid-sentence) must still verify. Pinned in Task 2 (`test_quote_across_block_boundary`).
4. **Curly quotes, dashes, commas** differ between a note and its transcript — must still verify, but a shorter word must not match inside a longer one. Pinned in Task 2 (`test_curly_quotes_and_punctuation`, `test_partial_word_does_not_match`).
5. **A mission listed in the map with no file yet** (and `00-map.md` / `00-log.md` sharing the `00` prefix) — `status` must treat it as `not-started`, not crash or miscount. Pinned in Task 3 (`test_missing_mission_file_is_not_started`, `test_only_limits_file_counts_as_mission_00`).

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/learn_by_doing.py` | Parsing helpers + `check_map`, `check_quirks`, `status`, CLI |
| `tests/test_learn_by_doing.py` | Builds a tiny vault in `tmp_path`; tests every rule above |
| `.claude/skills/learn-by-doing/SKILL.md` | The skill: commands, templates, rules, the `done` loop |
| `CLAUDE.md` | One bullet in the `.claude/` assets list |

The spec named `tests/fixtures/learn_by_doing/` for the fixture vault. This plan builds the vault in code in `tmp_path` instead, so each broken-map test can show exactly what it breaks. Same coverage, no fixture files.

---

### Task 1: Coverage check (`check-map`)

**Files:**
- Create: `scripts/learn_by_doing.py`
- Test: `tests/test_learn_by_doing.py`

**Interfaces:**
- Produces:
  - `section(text: str, heading: str) -> list[str] | None` — lines under `## heading` up to the next `## `; `None` if heading absent.
  - `section_sort_key(p: Path) -> tuple[int, str]`
  - `expected_lectures(vault: Path, course: str) -> list[tuple[str, str]]` — `(section_stem, "lectures/<course>/<stem>")` in course order.
  - `parse_coverage(map_text: str) -> list[dict] | None` — dict keys `target` (str or None), `cell`, `mission`, `kind` (lowercased), `note`.
  - `listed_missions(map_text: str) -> set[str]` — two-digit numbers from `## Missions` lines starting `- NN`.
  - `check_map(vault: Path, course: str) -> list[str]` — error strings; `[]` means pass.
  - `resolve_vault(arg: str | None) -> Path`
  - `main(argv: list[str] | None = None) -> int` — subcommand `check-map <course>`; exit 0 on pass, 1 on errors.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_learn_by_doing.py`:

```python
"""Tests for scripts/learn_by_doing.py — the /learn-by-doing skill's deterministic checks."""

from __future__ import annotations

import importlib.util
import pathlib

_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "learn_by_doing.py"
_spec = importlib.util.spec_from_file_location("learn_by_doing", _PATH)
lbd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lbd)

COURSE = "demo-course"
SECTIONS = {
    "1-intro": [("1-welcome-1", "Welcome"), ("1-what-is-etl-2", "What is ETL")],
    "2-storage": [("2-s3-basics-3", "S3 Basics"), ("2-important-ui-update-4", "[Important] UI Update")],
}
DEFAULT_TRANSCRIPT = "## Transcript\n\n[00:00:00] Narrator: Hello and welcome.\n"
S3_TRANSCRIPT = (
    "## Transcript\n\n"
    "[00:00:00] Narrator: S3 stores objects in buckets. Bucket names must be globally unique, "
    "you know, across every account.\n\n"
    "[00:01:00] A single object can be up to five terabytes. Watch out: the console won't\n\n"
    "[00:02:00] let you upload more than 160 gigabytes in one go.\n"
)
DEFAULT_ROWS = [
    ("1-welcome-1", "Welcome", "01", "skip", "course intro"),
    ("1-what-is-etl-2", "What is ETL", "01", "theory", ""),
    ("2-s3-basics-3", "S3 Basics", "02", "build", ""),
    ("2-important-ui-update-4", "[Important] UI Update", "02", "skip", "console notice"),
]


def make_vault(tmp_path: pathlib.Path) -> pathlib.Path:
    vault = tmp_path / "vault"
    (vault / "courses" / COURSE).mkdir(parents=True)
    (vault / "lectures" / COURSE).mkdir(parents=True)
    for sec, lectures in SECTIONS.items():
        links = "\n".join(f"- [[lectures/{COURSE}/{stem}|{title}]]" for stem, title in lectures)
        (vault / "courses" / COURSE / f"{sec}.md").write_text(f"# {sec}\n\n{links}\n")
        for stem, title in lectures:
            body = S3_TRANSCRIPT if stem == "2-s3-basics-3" else DEFAULT_TRANSCRIPT
            (vault / "lectures" / COURSE / f"{stem}.md").write_text(f"# {title}\n\n{body}")
    write_map(vault, DEFAULT_ROWS)
    return vault


def write_map(vault, rows, missions=("00", "01", "02")):
    lines = ["# Map", "", "## Missions", ""]
    lines += [f"- {n} · mission {n}" for n in missions]
    lines += ["", "## Lecture coverage", "", "| Lecture | Mission | Kind | Note |", "|---|---|---|---|"]
    for stem, title, mission, kind, note in rows:
        lines.append(f"| [[lectures/{COURSE}/{stem}\\|{title}]] | {mission} | {kind} | {note} |")
    path = vault / "practice" / COURSE / "00-map.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


# --- Task 1: check-map -------------------------------------------------------

def test_valid_map_passes(tmp_path):
    assert lbd.check_map(make_vault(tmp_path), COURSE) == []


def test_bracketed_title_is_expected(tmp_path):
    targets = [t for _, t in lbd.expected_lectures(make_vault(tmp_path), COURSE)]
    assert f"lectures/{COURSE}/2-important-ui-update-4" in targets
    assert len(targets) == 4


def test_escaped_pipe_and_empty_note():
    text = (
        "## Lecture coverage\n\n| Lecture | Mission | Kind | Note |\n|---|---|---|---|\n"
        "| [[lectures/c/x-1\\|[Important] X]] | 03 | Build | |\n"
    )
    [row] = lbd.parse_coverage(text)
    assert row["target"] == "lectures/c/x-1"
    assert (row["mission"], row["kind"], row["note"]) == ("03", "build", "")


def test_missing_lecture_reported(tmp_path):
    vault = make_vault(tmp_path)
    write_map(vault, DEFAULT_ROWS[:2] + DEFAULT_ROWS[3:])
    assert lbd.check_map(vault, COURSE) == [f"missing lecture: lectures/{COURSE}/2-s3-basics-3"]


def test_duplicate_lecture_reported(tmp_path):
    vault = make_vault(tmp_path)
    write_map(vault, DEFAULT_ROWS + [DEFAULT_ROWS[2]])
    assert lbd.check_map(vault, COURSE) == [f"duplicate lecture: lectures/{COURSE}/2-s3-basics-3"]


def test_unknown_lecture_reported(tmp_path):
    vault = make_vault(tmp_path)
    write_map(vault, DEFAULT_ROWS + [("9-ghost-9", "Ghost", "02", "build", "")])
    assert lbd.check_map(vault, COURSE) == [f"unknown lecture: lectures/{COURSE}/9-ghost-9"]


def test_bad_kind_reported(tmp_path):
    vault = make_vault(tmp_path)
    rows = list(DEFAULT_ROWS)
    rows[2] = ("2-s3-basics-3", "S3 Basics", "02", "watch", "")
    write_map(vault, rows)
    assert lbd.check_map(vault, COURSE) == [f"bad kind 'watch' for lectures/{COURSE}/2-s3-basics-3"]


def test_skip_without_note_reported(tmp_path):
    vault = make_vault(tmp_path)
    rows = list(DEFAULT_ROWS)
    rows[0] = ("1-welcome-1", "Welcome", "01", "skip", "")
    write_map(vault, rows)
    assert lbd.check_map(vault, COURSE) == [f"skip without a note: lectures/{COURSE}/1-welcome-1"]


def test_mission_not_listed_reported(tmp_path):
    vault = make_vault(tmp_path)
    write_map(vault, DEFAULT_ROWS, missions=("00", "01"))
    errors = lbd.check_map(vault, COURSE)
    assert errors == [
        f"mission '02' not in ## Missions: lectures/{COURSE}/2-s3-basics-3",
        f"mission '02' not in ## Missions: lectures/{COURSE}/2-important-ui-update-4",
    ]


def test_no_coverage_section(tmp_path):
    vault = make_vault(tmp_path)
    (vault / "practice" / COURSE / "00-map.md").write_text("# Map\n\n## Missions\n\n- 01 · x\n")
    assert lbd.check_map(vault, COURSE) == ["00-map.md has no '## Lecture coverage' section"]


def test_no_map_file(tmp_path):
    vault = make_vault(tmp_path)
    (vault / "practice" / COURSE / "00-map.md").unlink()
    [error] = lbd.check_map(vault, COURSE)
    assert error.startswith("map not found:")


def test_cli_check_map_exit_codes(tmp_path, capsys):
    vault = make_vault(tmp_path)
    assert lbd.main(["--vault", str(vault), "check-map", COURSE]) == 0
    write_map(vault, DEFAULT_ROWS[:3])
    assert lbd.main(["--vault", str(vault), "check-map", COURSE]) == 1
    assert "missing lecture" in capsys.readouterr().out


def test_section_sort_is_numeric():
    paths = [pathlib.Path(p) for p in ("10-x.md", "2-y.md", "1-z.md")]
    assert [p.stem for p in sorted(paths, key=lbd.section_sort_key)] == ["1-z", "2-y", "10-x"]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `pytest tests/test_learn_by_doing.py -v`
Expected: collection ERROR — `FileNotFoundError` / no such file `scripts/learn_by_doing.py`.

- [ ] **Step 3: Write the implementation**

Create `scripts/learn_by_doing.py`:

```python
#!/usr/bin/env python3
"""Deterministic checks for the /learn-by-doing skill. No LLM, stdlib only."""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_VAULT = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault"
KINDS = {"build", "theory", "skip"}
# Target stops at '|', ']' or '\' so aliases like "[Important] X" and escaped "\|" don't leak in.
LECTURE_TARGET = re.compile(r"\[\[(lectures/[^|\]\\]+)")
MISSION_ITEM = re.compile(r"^\s*-\s*(\d{2})\b")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def section(text: str, heading: str) -> list[str] | None:
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower() == heading.lower()
            continue
        if inside:
            out.append(line)
    return out if inside else None


def section_sort_key(p: Path) -> tuple[int, str]:
    head = p.stem.split("-", 1)[0]
    return (int(head) if head.isdigit() else 10**6, p.stem)


def expected_lectures(vault: Path, course: str) -> list[tuple[str, str]]:
    sec_dir = vault / "courses" / course
    if not sec_dir.is_dir():
        raise FileNotFoundError(f"no section notes at {sec_dir}")
    out = []
    for p in sorted(sec_dir.glob("*.md"), key=section_sort_key):
        for target in LECTURE_TARGET.findall(p.read_text(encoding="utf-8")):
            out.append((p.stem, target.strip()))
    return out


def parse_coverage(map_text: str) -> list[dict] | None:
    lines = section(map_text, "Lecture coverage")
    if lines is None:
        return None
    rows = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        # Strip exactly one outer pipe each side; str.strip("|") would eat an empty last cell.
        body = s[1:-1] if s.endswith("|") else s[1:]
        cells = [c.strip() for c in CELL_SPLIT.split(body)]
        if len(cells) < 4 or cells[0].lower() == "lecture" or set(cells[0]) <= set("-: "):
            continue
        m = LECTURE_TARGET.search(cells[0])
        rows.append({
            "target": m.group(1).strip() if m else None,
            "cell": cells[0],
            "mission": cells[1],
            "kind": cells[2].lower(),
            "note": cells[3],
        })
    return rows


def listed_missions(map_text: str) -> set[str]:
    return {m.group(1) for line in (section(map_text, "Missions") or []) if (m := MISSION_ITEM.match(line))}


def check_map(vault: Path, course: str) -> list[str]:
    map_path = vault / "practice" / course / "00-map.md"
    if not map_path.is_file():
        return [f"map not found: {map_path}"]
    text = map_path.read_text(encoding="utf-8")
    rows = parse_coverage(text)
    if rows is None:
        return ["00-map.md has no '## Lecture coverage' section"]
    expected = {t for _, t in expected_lectures(vault, course)}
    missions = listed_missions(text)
    errors: list[str] = []
    counts: Counter = Counter()
    for r in rows:
        if r["target"] is None:
            errors.append(f"row without a lecture link: {r['cell']}")
            continue
        counts[r["target"]] += 1
        if r["target"] not in expected:
            errors.append(f"unknown lecture: {r['target']}")
        if r["kind"] not in KINDS:
            errors.append(f"bad kind '{r['kind']}' for {r['target']}")
        if r["kind"] == "skip" and not r["note"]:
            errors.append(f"skip without a note: {r['target']}")
        if r["mission"] not in missions:
            errors.append(f"mission '{r['mission']}' not in ## Missions: {r['target']}")
    errors += [f"duplicate lecture: {t}" for t, n in sorted(counts.items()) if n > 1]
    errors += [f"missing lecture: {t}" for t in sorted(expected - set(counts))]
    return errors


def resolve_vault(arg: str | None) -> Path:
    return Path(arg or os.environ.get("UDEMY_VAULT_DIR") or DEFAULT_VAULT).expanduser()


def _report(errors: list[str]) -> int:
    for e in errors:
        print(e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="learn_by_doing")
    ap.add_argument("--vault", help="Udemy Vault root (default: $UDEMY_VAULT_DIR or iCloud path)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check-map", help="every lecture assigned exactly once").add_argument("course")
    args = ap.parse_args(argv)
    vault = resolve_vault(args.vault)
    if args.cmd == "check-map":
        return _report(check_map(vault, args.course))
    return 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `pytest tests/test_learn_by_doing.py -v`
Expected: 13 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/learn_by_doing.py tests/test_learn_by_doing.py
git commit -m "Add learn_by_doing check-map: every lecture assigned to a mission exactly once"
```

---

### Task 2: Quote check (`check-quirks`)

**Files:**
- Modify: `scripts/learn_by_doing.py` (add constants, functions, and the `check-quirks` subcommand)
- Test: `tests/test_learn_by_doing.py` (append)

**Interfaces:**
- Consumes: `section`, `resolve_vault`, `_report`, `main`, `DEFAULT_TRANSCRIPT`/`S3_TRANSCRIPT`/`make_vault` test helpers from Task 1.
- Produces:
  - `transcript_blocks(text: str) -> list[tuple[int, str]]` — `(start_seconds, text)` from the `## Transcript` section.
  - `normalize(s: str) -> str` — lowercase, every non `[a-z0-9]` run becomes one space.
  - `to_seconds(ts: str) -> int`
  - `window_text(blocks, seconds: int) -> str` — the block containing `seconds` plus one block each side.
  - `check_quirks(vault: Path, mission_path: Path) -> list[str]`
  - CLI: `check-quirks <mission>`; `<mission>` absolute or relative to the vault.

Quirk line format (only top-level `- ` lines under `## Quirks`; indented lines are free text):

```
- "<verbatim quote>" — [[lectures/<course>/<stem>|Title]] @ HH:MM:SS — what it means
```

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_learn_by_doing.py`:

```python
# --- Task 2: check-quirks ----------------------------------------------------

S3 = f"[[lectures/{COURSE}/2-s3-basics-3|S3 Basics]]"


def write_mission(vault, quirk_lines, name="01-demo.md"):
    path = vault / "practice" / COURSE / name
    path.write_text("---\nstatus: in-progress\n---\n\n## Quirks\n\n" + "\n".join(quirk_lines) + "\n\n## Cleanup\n")
    return path


def test_exact_quote_passes(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [f'- "Bucket names must be globally unique" — {S3} @ 00:00:10 — names are global'])
    assert lbd.check_quirks(vault, m) == []


def test_quote_across_block_boundary(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [f"- \"the console won't let you upload more than 160 gigabytes\" — {S3} @ 00:01:30"])
    assert lbd.check_quirks(vault, m) == []


def test_curly_quotes_and_punctuation(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [f"- “globally unique — you know — across every account” – {S3} @ 00:00:40"])
    assert lbd.check_quirks(vault, m) == []


def test_partial_word_does_not_match(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [f'- "bucket name" — {S3} @ 00:00:10'])
    assert len(lbd.check_quirks(vault, m)) == 1


def test_quote_far_from_timestamp_fails(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [f'- "Bucket names must be globally unique" — {S3} @ 00:02:30'])
    assert lbd.check_quirks(vault, m) == [
        f'quote not found near 00:02:30 in lectures/{COURSE}/2-s3-basics-3: "Bucket names must be globally unique"'
    ]


def test_invented_quote_fails(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [f'- "S3 is a relational database" — {S3} @ 00:00:10'])
    assert len(lbd.check_quirks(vault, m)) == 1


def test_bracketed_title_in_quirk_link(tmp_path):
    vault = make_vault(tmp_path)
    link = f"[[lectures/{COURSE}/2-important-ui-update-4|[Important] UI Update]]"
    m = write_mission(vault, [f'- "Hello and welcome" — {link} @ 00:00:05'])
    assert lbd.check_quirks(vault, m) == []


def test_malformed_quirk_line(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, ["- Bucket names must be unique (no quote, no link)"])
    assert lbd.check_quirks(vault, m) == ["malformed quirk line: - Bucket names must be unique (no quote, no link)"]


def test_indented_lines_are_free_text(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [
        f'- "Bucket names must be globally unique" — {S3} @ 00:00:10',
        "  - why it matters: you can't reuse a name someone else took",
    ])
    assert lbd.check_quirks(vault, m) == []


def test_lecture_without_transcript(tmp_path):
    vault = make_vault(tmp_path)
    (vault / "lectures" / COURSE / "2-s3-basics-3.md").write_text("# S3 Basics\n\nNo transcript captured.\n")
    m = write_mission(vault, [f'- "anything" — {S3} @ 00:00:10'])
    assert lbd.check_quirks(vault, m) == [f"no transcript in lectures/{COURSE}/2-s3-basics-3"]


def test_unknown_lecture_in_quirk(tmp_path):
    vault = make_vault(tmp_path)
    m = write_mission(vault, [f'- "x" — [[lectures/{COURSE}/9-ghost-9|Ghost]] @ 00:00:10'])
    assert lbd.check_quirks(vault, m) == [f"lecture not found: lectures/{COURSE}/9-ghost-9"]


def test_missing_quirks_section(tmp_path):
    vault = make_vault(tmp_path)
    path = vault / "practice" / COURSE / "01-demo.md"
    path.write_text("---\nstatus: in-progress\n---\n\n## Goal\n")
    assert lbd.check_quirks(vault, path) == ["01-demo.md has no '## Quirks' section"]


def test_cli_check_quirks_vault_relative(tmp_path):
    vault = make_vault(tmp_path)
    write_mission(vault, [f'- "Bucket names must be globally unique" — {S3} @ 00:00:10'])
    rel = f"practice/{COURSE}/01-demo.md"
    assert lbd.main(["--vault", str(vault), "check-quirks", rel]) == 0
    write_mission(vault, [f'- "made up" — {S3} @ 00:00:10'])
    assert lbd.main(["--vault", str(vault), "check-quirks", rel]) == 1
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `pytest tests/test_learn_by_doing.py -v -k "quote or quirk or transcript"`
Expected: FAIL — `AttributeError: module 'learn_by_doing' has no attribute 'check_quirks'`.

- [ ] **Step 3: Write the implementation**

In `scripts/learn_by_doing.py`, add after `CELL_SPLIT = ...`:

```python
TS_LINE = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\]\s*(.*)$")
# Title part is non-greedy up to the first "]]" so titles like "[Important] X" work.
QUIRK_LINE = re.compile(
    r'^-\s*["“](?P<quote>[^"”]+)["”]\s*[—–-]\s*'
    r"\[\[(?P<target>lectures/[^|\]\\]+)(?:\\?\|.*?)?\]\]\s*@\s*"
    r"(?P<ts>\d{1,2}:\d{2}:\d{2})"
)
```

Add after `check_map`:

```python
def transcript_blocks(text: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    for line in section(text, "Transcript") or []:
        s = line.strip()
        m = TS_LINE.match(s)
        if m:
            h, mi, sec, rest = m.groups()
            blocks.append((int(h) * 3600 + int(mi) * 60 + int(sec), rest))
        elif blocks and s:
            start, body = blocks[-1]
            blocks[-1] = (start, f"{body} {s}")
    return blocks


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def to_seconds(ts: str) -> int:
    h, m, s = (int(x) for x in ts.split(":"))
    return h * 3600 + m * 60 + s


def window_text(blocks: list[tuple[int, str]], seconds: int) -> str:
    # Blocks are per-minute and split mid-sentence, so search the block plus one each side.
    idx = 0
    for i, (start, _) in enumerate(blocks):
        if start <= seconds:
            idx = i
    lo, hi = max(0, idx - 1), min(len(blocks), idx + 2)
    return " ".join(body for _, body in blocks[lo:hi])


def check_quirks(vault: Path, mission_path: Path) -> list[str]:
    lines = section(mission_path.read_text(encoding="utf-8"), "Quirks")
    if lines is None:
        return [f"{mission_path.name} has no '## Quirks' section"]
    errors: list[str] = []
    for line in lines:
        if not line.startswith("- "):
            continue
        m = QUIRK_LINE.match(line)
        if not m:
            errors.append(f"malformed quirk line: {line.strip()}")
            continue
        target = m.group("target").strip()
        lecture = vault / f"{target}.md"
        if not lecture.is_file():
            errors.append(f"lecture not found: {target}")
            continue
        blocks = transcript_blocks(lecture.read_text(encoding="utf-8"))
        if not blocks:
            errors.append(f"no transcript in {target}")
            continue
        near = normalize(window_text(blocks, to_seconds(m.group("ts"))))
        if f" {normalize(m.group('quote'))} " not in f" {near} ":
            errors.append(f'quote not found near {m.group("ts")} in {target}: "{m.group("quote")}"')
    return errors
```

In `main`, after the `check-map` subparser line add:

```python
    sub.add_parser("check-quirks", help="every quoted quirk is in its transcript").add_argument("mission")
```

and after the `check-map` branch add:

```python
    if args.cmd == "check-quirks":
        mission = Path(args.mission).expanduser()
        if not mission.is_absolute():
            mission = vault / mission
        return _report(check_quirks(vault, mission))
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `pytest tests/test_learn_by_doing.py -v`
Expected: 26 passed.

- [ ] **Step 5: Try it on one real lecture (sanity, no file written)**

Run:
```bash
python3 -c "
import importlib.util,pathlib
s=importlib.util.spec_from_file_location('l','scripts/learn_by_doing.py');l=importlib.util.module_from_spec(s);s.loader.exec_module(l)
p=l.DEFAULT_VAULT/'lectures/aws-certified-data-engineer-associate-2026-hands-on/2-managing-and-orchestrating-etl-pipelines-40392846.md'
b=l.transcript_blocks(p.read_text()); print(len(b), b[0][0], b[-1][0])"
```
Expected: `5 0 240` (five per-minute blocks, last one at 00:04:00).

- [ ] **Step 6: Commit**

```bash
git add scripts/learn_by_doing.py tests/test_learn_by_doing.py
git commit -m "Add learn_by_doing check-quirks: quoted quirks must appear near their timestamp"
```

---

### Task 3: Progress (`status`)

**Files:**
- Modify: `scripts/learn_by_doing.py`
- Test: `tests/test_learn_by_doing.py` (append)

**Interfaces:**
- Consumes: `parse_coverage`, `listed_missions`, `expected_lectures`, `main` from Task 1.
- Produces:
  - `frontmatter(text: str) -> str`
  - `mission_statuses(vault: Path, course: str) -> dict[str, str]` — `"00"` comes only from `00-limits.md`; `00-map.md`/`00-log.md` ignored.
  - `status(vault: Path, course: str) -> str` — one line per section `"<section_stem>: D/T lectures practiced"`, then `"Current mission: NN (<status>)"` or `"All missions done"`. Raises `FileNotFoundError` if the map is missing.
  - CLI: `status <course>`; exit 1 with a message if the map is missing.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_learn_by_doing.py`:

```python
# --- Task 3: status ----------------------------------------------------------

def set_status(vault, name, value):
    (vault / "practice" / COURSE / name).write_text(f"---\nmission: x\nstatus: {value}\n---\n\n# x\n")


def test_status_counts_done_missions(tmp_path):
    vault = make_vault(tmp_path)
    set_status(vault, "00-limits.md", "done")
    set_status(vault, "01-foundations.md", "done")
    assert lbd.status(vault, COURSE).splitlines() == [
        "1-intro: 2/2 lectures practiced",
        "2-storage: 0/2 lectures practiced",
        "Current mission: 02 (not-started)",
    ]


def test_missing_mission_file_is_not_started(tmp_path):
    vault = make_vault(tmp_path)
    set_status(vault, "00-limits.md", "done")
    set_status(vault, "01-foundations.md", "in-progress")
    assert lbd.status(vault, COURSE).splitlines()[-1] == "Current mission: 01 (in-progress)"
    assert lbd.mission_statuses(vault, COURSE).get("02") is None


def test_only_limits_file_counts_as_mission_00(tmp_path):
    vault = make_vault(tmp_path)
    set_status(vault, "00-log.md", "done")  # must be ignored
    assert lbd.status(vault, COURSE).splitlines()[-1] == "Current mission: 00 (not-started)"


def test_all_missions_done(tmp_path):
    vault = make_vault(tmp_path)
    for name in ("00-limits.md", "01-a.md", "02-b.md"):
        set_status(vault, name, "done")
    assert lbd.status(vault, COURSE).splitlines()[-1] == "All missions done"


def test_cli_status(tmp_path, capsys):
    vault = make_vault(tmp_path)
    assert lbd.main(["--vault", str(vault), "status", COURSE]) == 0
    assert "Current mission: 00 (not-started)" in capsys.readouterr().out
    (vault / "practice" / COURSE / "00-map.md").unlink()
    assert lbd.main(["--vault", str(vault), "status", COURSE]) == 1
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `pytest tests/test_learn_by_doing.py -v -k status`
Expected: FAIL — `AttributeError: module 'learn_by_doing' has no attribute 'status'`.

- [ ] **Step 3: Write the implementation**

In `scripts/learn_by_doing.py`, add after `QUIRK_LINE`:

```python
STATUS_LINE = re.compile(r"^status:\s*(\S+)\s*$", re.M)
```

Add after `check_quirks`:

```python
def frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def mission_statuses(vault: Path, course: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in (vault / "practice" / course).glob("[0-9][0-9]-*.md"):
        num = p.name[:2]
        if num == "00" and p.name != "00-limits.md":
            continue
        m = STATUS_LINE.search(frontmatter(p.read_text(encoding="utf-8")))
        out[num] = m.group(1) if m else "not-started"
    return out


def status(vault: Path, course: str) -> str:
    map_path = vault / "practice" / course / "00-map.md"
    if not map_path.is_file():
        raise FileNotFoundError(f"map not found: {map_path}")
    text = map_path.read_text(encoding="utf-8")
    statuses = mission_statuses(vault, course)
    mission_of = {r["target"]: r["mission"] for r in parse_coverage(text) or [] if r["target"]}
    per: dict[str, list[int]] = {}
    for sec, target in expected_lectures(vault, course):
        counts = per.setdefault(sec, [0, 0])
        counts[0] += statuses.get(mission_of.get(target, ""), "not-started") == "done"
        counts[1] += 1
    lines = [f"{sec}: {d}/{t} lectures practiced" for sec, (d, t) in per.items()]
    current = next((n for n in sorted(listed_missions(text)) if statuses.get(n, "not-started") != "done"), None)
    lines.append(f"Current mission: {current} ({statuses.get(current, 'not-started')})" if current else "All missions done")
    return "\n".join(lines)
```

In `main`, add the subparser:

```python
    sub.add_parser("status", help="progress per section").add_argument("course")
```

and the branch:

```python
    if args.cmd == "status":
        try:
            print(status(vault, args.course))
        except FileNotFoundError as e:
            print(e)
            return 1
        return 0
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `pytest tests/test_learn_by_doing.py -v`
Expected: 31 passed.

- [ ] **Step 5: Run the full suite (nothing else broke)**

Run: `pytest -q`
Expected: same pass count as before this branch + 31, no new failures.

- [ ] **Step 6: Commit**

```bash
git add scripts/learn_by_doing.py tests/test_learn_by_doing.py
git commit -m "Add learn_by_doing status: lectures practiced per section + current mission"
```

---

### Task 4: The skill

**Files:**
- Create: `.claude/skills/learn-by-doing/SKILL.md`
- Modify: `CLAUDE.md` (the `**Skills**` list under "`.claude/` assets")

**Interfaces:**
- Consumes: CLI from Tasks 1-3: `python3 scripts/learn_by_doing.py [--vault V] check-map <course> | check-quirks <mission> | status <course>`.

- [ ] **Step 1: Load `superpowers:writing-skills`** and follow its format rules while writing the file below. Its pressure testing is covered by the Task 5 pilot run.

- [ ] **Step 2: Write `.claude/skills/learn-by-doing/SKILL.md`**

````markdown
---
name: learn-by-doing
description: Learn a Udemy Vault course by BUILDING — one course project plus one hands-on mission per section, every lecture covered, instructor quirks kept and verified, and the owner's proof checked before a step counts. Use when the user wants to practice or learn a course by doing, asks for labs/missions/hands-on tasks from a course, wants to continue their missions, or invokes /learn-by-doing. For reading notes use /deep-notes instead.
trigger: /learn-by-doing
---

# /learn-by-doing

The owner learns by building. You plan, coach and check. You never build it for them.

## Commands

```
/learn-by-doing <course> map      # course project + missions + lecture coverage + Mission 0
/learn-by-doing <course> next     # build the next mission, give the first step
/learn-by-doing <course> done     # owner reports; ask for proof; grade; log
/learn-by-doing <course> status   # progress
```

`<course>` = folder name under `courses/` in the vault, or a fuzzy title. Match against `index.yaml` `courses:`. More than one match → ask.

## Paths

- Vault: `$UDEMY_VAULT_DIR`, else `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Udemy Vault`.
- Section notes: `courses/<course>/<N>-<slug>.md`, lecture list as `[[lectures/<course>/<stem>|Title]]`.
- Lectures: `lectures/<course>/<stem>.md`, `## Transcript` in `[HH:MM:SS]` per-minute blocks.
- Practice: `practice/<course>/00-map.md`, `00-limits.md`, `00-log.md`, `NN-<slug>.md`.
- Checks (run from the repo root):
  ```bash
  python3 scripts/learn_by_doing.py check-map <course>
  python3 scripts/learn_by_doing.py check-quirks practice/<course>/NN-<slug>.md
  python3 scripts/learn_by_doing.py status <course>
  ```

## Hard rules

1. **The owner builds.** Steps are goals + "done when" rules, not copy-paste solutions. Give hints only when asked, smallest hint first.
2. **Where tag on every step:**
   | Tag | Runs on | Needs |
   |---|---|---|
   | `[AWS]` | company dev AWS account, office VPN — you cannot see it | cost note, cleanup, proof the owner pastes |
   | `[LOCAL]` | owner's Mac (Docker if a server is needed) | free; you may check files / run their tests yourself, read-only, **say so first** |
   | `[TRIAL]` | owner's personal Snowflake trial | cost note (credits), XS warehouse, auto-suspend on, proof pasted |
   Course defaults: AWS courses → `[AWS]`. dbt, DuckDB, Spark, Kafka, Iceberg → `[LOCAL]`. Snowflake → `[TRIAL]`. A step may override (DuckDB reading S3 = `[AWS]`).
3. **Company limits, from `00-limits.md`, in every `[AWS]` step:** use only the IAM roles listed there — **never write a "create an IAM role" step**; if a service needs a role that isn't listed, say so and make it a question for the owner's platform team. Allowed region only. Required tags + name prefix on every resource.
4. **Never ask for** access keys, secret keys, passwords, tokens, session cookies, or full ARNs with account IDs. Tell the owner to blank account IDs as `123456789012`. If they paste a secret anyway, tell them to rotate it and do not repeat it.
5. **Every `[AWS]`/`[TRIAL]` step has a cost note and a cleanup.** A mission is not `done` until cleanup is proven.
6. **Quirks are quoted word for word** and must pass `check-quirks`. If a quote fails, copy the exact transcript text or drop the quirk. Never loosen a quote to make it pass.
7. **Nothing skipped.** Every lecture is in the map exactly once, and `check-map` must pass.
8. **Obsidian tables:** a wikilink alias inside a table cell must be written `[[target\|Title]]`, or the table breaks.
9. Edit only `practice/<course>/**` and the one link line in `courses/<course>.md`.

## `map`

1. Resolve the course. Read `courses/<course>.md` and every `courses/<course>/*.md` section note in order.
2. Read every lecture title. If a title doesn't say what the lecture teaches, open its transcript and skim it.
3. Pick **one course project**: a realistic build that needs every section. Sections that don't fit become **side quests** (still built and checked).
4. Missions: `00` = limits, then one per section in course order (`01`, `02`, …). A section with only intro/outro/admin lectures can share a neighbour's mission.
5. Label every lecture `build` (a step makes the owner do it), `theory` (quick "why" check), or `skip` (only intro, outro, course admin, or "UI changed" notices, and always with a note saying why).
6. Write `00-map.md`, `00-limits.md`, `00-log.md` from the templates below.
7. Add this line at the end of `courses/<course>.md` if it isn't already there. A vault rebuild can remove it, so check again on every command:
   `Practice: [[practice/<course>/00-map|Learn by doing]]`
8. Run `check-map`. Fix every error and re-run until you get `OK`.
9. Tell the owner: the project in two lines, the number of missions, and that Mission 0 comes first.

### `00-map.md` template

```markdown
---
course: <course>
project: <one line>
---

# <Course title> — learn by doing

## Course project
<3-6 lines: what gets built, end to end, and which section adds which piece.>

## Missions
- 00 · [[practice/<course>/00-limits|Mission 0 — your limits]]
- 01 · [[practice/<course>/01-<slug>|<title>]] — section <N> — adds <piece>
- 07 · [[practice/<course>/07-<slug>|<title>]] — section <N> — side quest

## Lecture coverage
| Lecture | Mission | Kind | Note |
|---|---|---|---|
| [[lectures/<course>/<stem>\|<title>]] | 01 | build | |
| [[lectures/<course>/<stem>\|<title>]] | 01 | skip | section intro |
```

### `00-limits.md` template (Mission 0)

```markdown
---
course: <course>
mission: "00"
status: not-started
---

# Mission 0 — your limits

Read-only checks. Nothing here costs money or creates anything.

## Steps
1. [AWS] Who am I? Run `aws sts get-caller-identity`. **Send:** the output with the account ID blanked.
2. [AWS] Allowed region(s). **Send:** the region list your company allows.
3. [AWS] Roles you may use. Run `aws iam list-roles --query "Roles[].RoleName"` (if it's denied, ask your platform team). **Send:** the role names you're allowed to pass to Glue / Lambda / EMR / Redshift, etc.
4. [AWS] Required tags + name prefix. **Send:** the tag keys and the prefix.
5. [TRIAL] Snowflake trial (only for Snowflake courses). **Send:** the trial end date and credits left.
6. [LOCAL] Tools. Run `docker --version; python3 --version` plus the course's own tools (`dbt --version`, `duckdb --version`, …). **Send:** the output.

## Your limits
- Region:
- Roles allowed:
- Required tags:
- Name prefix:
- Snowflake trial ends:
- Local tools:

## Your log
```

Fill in `## Your limits` from the owner's answers, then set `status: done`.

### `00-log.md`

Append-only. One line per event, newest last. Never rewrite old lines.
```markdown
# Log — <course>

- 2026-09-23 — map built: 17 missions, 317 lectures (check-map OK)
- 2026-09-24 — Mission 00 done
- 2026-09-25 — Mission 01 built (check-quirks OK)
- 2026-09-26 — Mission 01 step 2 pass
- 2026-09-27 — Mission 01 cleanup verified — done
```

## `next`

1. If `00-limits.md` is not `done`, do Mission 0 first.
2. Take the lowest mission that is not `done` (run `status`). If it's already `in-progress`, just show its next open step.
3. **Read every transcript of that mission's lectures in full.** No skimming. For a big section, send Sonnet subagents in parallel (about 10 lectures each). Ask each one to return, per lecture: what can be built, the key facts, and **quirk candidates copied word for word with their `[HH:MM:SS]`**. Hunt for: "watch out", "be careful", "gotcha", "common mistake", "exam", "remember", limits and numbers, defaults, "new"/"changed"/"deprecated", cost warnings, "don't".
4. Write `NN-<slug>.md` from the template below. Where you can, turn a quirk into a step that lets the owner **see it happen**.
5. Run `check-quirks`. Fix it until you get `OK`.
6. Set `status: in-progress`, add a line to `00-log.md`, and give the owner Step 1 only.

### Mission template

```markdown
---
course: <course>
mission: "NN"
section: <section title>
where: AWS | LOCAL | TRIAL
status: not-started
---

# Mission NN — <title>

Map: [[practice/<course>/00-map|Course map]] · Limits: [[practice/<course>/00-limits|Your limits]]

## Goal
<What you build, and where it plugs into the course project.>

## Steps
### 1. <name> [AWS]
- Teaches: [[lectures/<course>/<stem>|<title>]]
- Do: <the goal, not the code. Use the prefix, tags, region and allowed role from your limits.>
- Done when: <a rule you can check, e.g. "the crawler made 1 table with 3 partitions">
- Cost: <what bills, a rough size, and how to keep it small>
- Send: <exact command(s), e.g. `aws glue get-table --database-name <prefix>_raw --name events --query "Table.PartitionKeys"`>

## Quirks
- "<verbatim quote>" — [[lectures/<course>/<stem>|<title>]] @ HH:MM:SS — <what it means for you>

## Theory checks
- [[lectures/<course>/<stem>|<title>]]: <why-question>

## Cleanup
- Delete: <every resource this mission made>
- Send: <a list/describe command that shows it's gone>

## Your log
```

## `done`

1. The owner says which step(s) they finished. If they didn't send the proof the step asks for, ask for exactly that and nothing more.
2. Check the proof against the step's **Done when**. Your verdict:
   - **pass**
   - **almost**: name the one fix
   - **redo**: say what went wrong and which lecture (+ timestamp) covers it
3. Theory checks: the owner answers in their own words. Grade against the lecture text. On a miss, name the lecture + timestamp to rewatch.
4. Under `## Your log`, add: date, step, a short proof summary (never secrets), verdict. Add one line to `00-log.md`.
5. Give the next open step. When every step, theory check and the cleanup has passed, set `status: done`, add it to the log, and offer `next`.
6. `[LOCAL]` steps: you may check the result yourself. Say what you'll run first, read only.

## `status`

Run `status`. Print its output as is, then give the current mission's next open step in one line.
````

- [ ] **Step 3: Add the skill to `CLAUDE.md`**

In `CLAUDE.md`, in the `**Skills** (`.claude/skills/`, invoke as `/<name>`):` list, add after the `vault-ask` bullet:

```markdown
- `learn-by-doing` (`/learn-by-doing <course> map|next|done|status`) — learn a
  Udemy Vault course by building: one course project + one mission per section,
  every lecture assigned (`scripts/learn_by_doing.py check-map`), every quoted
  quirk verified against its transcript (`check-quirks`). `[AWS]` steps run in
  the owner's company dev account (Claude can't see it: proof is pasted, no IAM
  role creation, region/tags/prefix from `practice/<course>/00-limits.md`),
  `[LOCAL]` on the Mac, `[TRIAL]` on a personal Snowflake trial. Progress lives
  in the Udemy Vault under `practice/<course>/`. Spec:
  `docs/superpowers/specs/2026-09-23-learn-by-doing-design.md`.
```

- [ ] **Step 4: Check the commands in the skill still run**

Run: `python3 scripts/learn_by_doing.py --help`
Expected: usage text listing `check-map`, `check-quirks`, `status`.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/learn-by-doing/SKILL.md CLAUDE.md
git commit -m "Add /learn-by-doing skill: build-to-learn missions over the Udemy Vault"
```

---

### Task 5: Pilot on AWS Certified Data Engineer Associate

This task writes to the Udemy Vault (not git). Only the repo changes get committed. The `done` loop needs the owner, so this task ends when the owner has Mission 0 in hand.

**Files:**
- Create (vault): `practice/aws-certified-data-engineer-associate-2026-hands-on/00-map.md`, `00-limits.md`, `00-log.md`, `01-<slug>.md`
- Modify (vault): `courses/aws-certified-data-engineer-associate-2026-hands-on.md` (one link line)
- Modify (repo, only if the pilot finds a gap): `.claude/skills/learn-by-doing/SKILL.md`, `scripts/learn_by_doing.py` + tests

- [ ] **Step 1: Run `map`** by following `SKILL.md` `## map` for course `aws-certified-data-engineer-associate-2026-hands-on`.

- [ ] **Step 2: Coverage gate**

Run: `python3 scripts/learn_by_doing.py check-map aws-certified-data-engineer-associate-2026-hands-on`
Expected: `OK`. The table has 317 rows. The row for `3-important-aws-console-ui-update-47890711` has its alias escaped as `\|`.

- [ ] **Step 3: Build Mission 01** by following `SKILL.md` `## next`. Mission 0 isn't done yet, so write Mission 01 as the preview the owner gets after Mission 0.

- [ ] **Step 4: Quote gate**

Run: `python3 scripts/learn_by_doing.py check-quirks practice/aws-certified-data-engineer-associate-2026-hands-on/01-<slug>.md`
Expected: `OK`.

- [ ] **Step 5: Status gate**

Run: `python3 scripts/learn_by_doing.py status aws-certified-data-engineer-associate-2026-hands-on`
Expected: 17 section lines, all `0/…`, and last line `Current mission: 00 (not-started)`.

- [ ] **Step 6: Fold gaps back.** For anything the pilot showed the skill or script got wrong: fix it in `SKILL.md`, or fix the script with a new failing test first. Then run `pytest tests/test_learn_by_doing.py -q` and commit:

```bash
git add .claude/skills/learn-by-doing/SKILL.md scripts/learn_by_doing.py tests/test_learn_by_doing.py
git commit -m "learn-by-doing: fixes from the AWS Data Engineer pilot"
```
(Skip this commit if the pilot found nothing.)

- [ ] **Step 7: Hand over.** Tell the owner: the course project in two lines, the mission count, and Mission 0's steps. The spec's last pilot criterion (one step through `done`) is finished live with the owner.
