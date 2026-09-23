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
TS_LINE = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\]\s*(.*)$")
# Title part is non-greedy up to the first "]]" so titles like "[Important] X" work.
QUIRK_LINE = re.compile(
    r'^-\s*["“](?P<quote>[^"”]+)["”]\s*[—–-]\s*'
    r"\[\[(?P<target>lectures/[^|\]\\]+)(?:\\?\|.*?)?\]\]\s*@\s*"
    r"(?P<ts>\d{1,2}:\d{2}:\d{2})"
)


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
    sub.add_parser("check-quirks", help="every quoted quirk is in its transcript").add_argument("mission")
    args = ap.parse_args(argv)
    vault = resolve_vault(args.vault)
    if args.cmd == "check-map":
        return _report(check_map(vault, args.course))
    if args.cmd == "check-quirks":
        mission = Path(args.mission).expanduser()
        if not mission.is_absolute():
            mission = vault / mission
        return _report(check_quirks(vault, mission))
    return 2


if __name__ == "__main__":
    sys.exit(main())
