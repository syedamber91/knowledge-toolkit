from pathlib import Path

import yaml

from udemy_toolkit.models import UdemyCatalog, UdemyCourse, UdemyLecture, UdemySection
from udemy_toolkit.vault import build_vault, note_filename, slugify


def _catalog(lecture_titles=("Welcome",), transcript="Talking about kafka and spark streaming."):
    lectures = [
        UdemyLecture(
            id=str(index),
            title=title,
            url=f"https://www.udemy.com/course/test/learn/lecture/{index}",
            duration_seconds=120,
            section_title="Getting Started",
            transcript=transcript,
            has_transcript=bool(transcript),
        )
        for index, title in enumerate(lecture_titles, start=1)
    ]
    return UdemyCatalog(
        courses=[
            UdemyCourse(
                id="123",
                title="Test Course",
                url="https://www.udemy.com/course/test/",
                instructor="Someone",
                sections=[UdemySection(title="Getting Started", order=1, lectures=lectures)],
            )
        ]
    )


def test_slugify_and_note_filename():
    assert slugify("Hello, World! Part 2") == "hello-world-part-2"
    assert note_filename(3, "Hello, World!") == "3-hello-world.md"


def test_writes_one_note_per_lecture_with_frontmatter(tmp_path):
    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    notes = sorted((tmp_path / "lectures" / "test-course").glob("*.md"))
    assert [n.name for n in notes] == ["1-setup.md", "1-welcome.md"]
    body = (tmp_path / "lectures" / "test-course" / "1-welcome.md").read_text(encoding="utf-8")
    assert body.startswith("---\n")
    assert 'title: "Welcome"' in body
    assert 'course: "Test Course"' in body
    assert "Talking about kafka" in body


def test_index_and_mocs_are_linked(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    home = (tmp_path / "Home.md").read_text(encoding="utf-8")
    assert "[[courses/test-course|Test Course]]" in home
    assert "[[Log|Ingestion Log]]" in home
    section_moc = (tmp_path / "courses" / "test-course" / "1-getting-started.md").read_text(encoding="utf-8")
    assert "[[lectures/test-course/1-welcome|Welcome]]" in section_moc


def test_topic_notes_cross_link_lectures(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    topic_notes = list((tmp_path / "topics").glob("*.md"))
    assert topic_notes, "expected at least one topic note from the transcript text"
    assert any("[[lectures/test-course/1-welcome|Welcome]]" in n.read_text(encoding="utf-8") for n in topic_notes)


# --- the four required Log.md tests ---

def test_log_first_entry_is_worded_as_a_backfill(tmp_path):
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    log = (tmp_path / "Log.md").read_text(encoding="utf-8")
    assert "2 item(s) already in vault (log started here)" in log
    assert "captured" not in log


def test_log_appends_on_growth(tmp_path):
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    lines = [l for l in (tmp_path / "Log.md").read_text(encoding="utf-8").splitlines() if l.startswith("- **")]
    assert len(lines) == 2
    assert "1 new item(s) captured" in lines[1]
    assert "(2 total" in lines[1]


def test_log_does_not_append_on_unchanged_rebuild(tmp_path):
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    lines = [l for l in (tmp_path / "Log.md").read_text(encoding="utf-8").splitlines() if l.startswith("- **")]
    assert len(lines) == 1


def test_log_records_removals(tmp_path):
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    lines = [l for l in (tmp_path / "Log.md").read_text(encoding="utf-8").splitlines() if l.startswith("- **")]
    assert "1 item(s) removed" in lines[1]


def test_frontmatter_survives_quotes_and_colons_in_titles(tmp_path):
    tricky_title = 'Setup: "the basics"'
    catalog = _catalog(("Welcome",))
    catalog.courses[0].title = 'Test Course: "Advanced" Edition'
    catalog.courses[0].sections[0].title = 'Getting Started: "Prep"'
    catalog.courses[0].sections[0].lectures[0].title = tricky_title

    build_vault(catalog, vault_dir=tmp_path)

    course_slug = slugify(catalog.courses[0].title)
    filename = note_filename(1, tricky_title)
    note_path = tmp_path / "lectures" / course_slug / filename
    body = note_path.read_text(encoding="utf-8")

    assert body.startswith("---\n")
    end = body.index("\n---\n", 4)
    frontmatter_block = body[4:end]
    parsed = yaml.safe_load(frontmatter_block)

    assert parsed["title"] == tricky_title
    assert parsed["course"] == catalog.courses[0].title
    assert parsed["section"] == catalog.courses[0].sections[0].title


def test_rebuild_prunes_stale_notes_but_never_touches_log(tmp_path):
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    log_before = (tmp_path / "Log.md").read_text(encoding="utf-8")

    stale_note = tmp_path / "lectures" / "test-course" / note_filename(1, "B")
    assert stale_note.exists()

    build_vault(_catalog(("A",)), vault_dir=tmp_path)

    assert not stale_note.exists()

    log_after = (tmp_path / "Log.md").read_text(encoding="utf-8")
    assert "2 item(s) already in vault (log started here)" in log_after
    assert log_after.startswith(log_before)
    lines = [l for l in log_after.splitlines() if l.startswith("- **")]
    assert len(lines) == 2
    assert "1 item(s) removed" in lines[1]
