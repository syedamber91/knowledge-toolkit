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
