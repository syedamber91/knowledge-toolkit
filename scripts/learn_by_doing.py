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
