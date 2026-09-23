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
