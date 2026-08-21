from pathlib import Path

import pytest
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
    assert note_filename(3, "42", "Hello, World!") == "3-hello-world-42.md"


def test_writes_one_note_per_lecture_with_frontmatter(tmp_path):
    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    notes = sorted((tmp_path / "lectures" / "test-course").glob("*.md"))
    assert [n.name for n in notes] == ["1-setup-2.md", "1-welcome-1.md"]
    body = (tmp_path / "lectures" / "test-course" / "1-welcome-1.md").read_text(encoding="utf-8")
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
    assert "[[lectures/test-course/1-welcome-1|Welcome]]" in section_moc


def test_topic_notes_cross_link_lectures(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    topic_notes = list((tmp_path / "topics").glob("*.md"))
    assert topic_notes, "expected at least one topic note from the transcript text"
    assert any("[[lectures/test-course/1-welcome-1|Welcome]]" in n.read_text(encoding="utf-8") for n in topic_notes)


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
    filename = note_filename(1, "1", tricky_title)
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

    stale_note = tmp_path / "lectures" / "test-course" / note_filename(1, "2", "B")
    assert stale_note.exists()

    build_vault(_catalog(("A",)), vault_dir=tmp_path)

    assert not stale_note.exists()

    log_after = (tmp_path / "Log.md").read_text(encoding="utf-8")
    assert "2 item(s) already in vault (log started here)" in log_after
    assert log_after.startswith(log_before)
    lines = [l for l in log_after.splitlines() if l.startswith("- **")]
    assert len(lines) == 2
    assert "1 item(s) removed" in lines[1]


from udemy_toolkit.vault import TAG_VOCABULARY, classify_tags, verify_vault


def test_classify_tags_only_returns_vocabulary_members():
    tags = classify_tags("This lecture covers testing, debugging and deployment pipelines.")
    assert tags
    assert all(t in TAG_VOCABULARY for t in tags)
    assert len(tags) <= 3


def test_classify_tags_falls_back_rather_than_inventing():
    assert classify_tags("") == ["uncategorized"]


def test_manifest_lists_every_note_with_routing_metadata(tmp_path):
    import yaml

    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    manifest = yaml.safe_load((tmp_path / "index.yaml").read_text(encoding="utf-8"))
    assert manifest["vault"] == "Udemy Vault"
    assert manifest["counts"]["lectures"] == 2
    entry = manifest["courses"][0]["sections"][0]["lectures"][0]
    for key in ("title", "note", "url", "tags", "topics", "has_transcript", "words"):
        assert key in entry


def test_every_lecture_note_has_tags_frontmatter(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    body = (tmp_path / "lectures" / "test-course" / "1-welcome-1.md").read_text(encoding="utf-8")
    assert "\ntags: [" in body


def test_verify_vault_reports_a_clean_build(tmp_path):
    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    report = verify_vault(tmp_path)
    assert report["dangling_links"] == []
    assert report["orphan_notes"] == []
    assert report["untagged"] == []
    assert report["unknown_tags"] == []
    assert report["notes"] > 0


def test_verify_vault_catches_a_dangling_link(tmp_path):
    build_vault(_catalog(), vault_dir=tmp_path)
    home = tmp_path / "Home.md"
    home.write_text(home.read_text(encoding="utf-8") + "\n- [[courses/does-not-exist|Ghost]]\n", encoding="utf-8")
    assert "courses/does-not-exist" in verify_vault(tmp_path)["dangling_links"]


# --- Finding 2: duplicate lecture titles must not overwrite each other ---


def test_duplicate_lecture_titles_in_one_section_produce_distinct_notes(tmp_path):
    catalog = _catalog(("Intro", "Intro"))
    build_vault(catalog, vault_dir=tmp_path)

    notes = sorted((tmp_path / "lectures" / "test-course").glob("*.md"))
    assert len(notes) == 2
    assert notes[0].name != notes[1].name

    manifest = yaml.safe_load((tmp_path / "index.yaml").read_text(encoding="utf-8"))
    note_paths = {
        lec["note"] for lec in manifest["courses"][0]["sections"][0]["lectures"]
    }
    assert len(note_paths) == 2
    for note_path in note_paths:
        assert (tmp_path / f"{note_path}.md").exists()


def test_verify_vault_reports_manifest_mismatch_when_note_count_disagrees(tmp_path):
    build_vault(_catalog(("Welcome", "Setup")), vault_dir=tmp_path)
    # Simulate a lost/overwritten note: manifest still claims 2 lectures but
    # only 1 note file remains on disk.
    notes = sorted((tmp_path / "lectures" / "test-course").glob("*.md"))
    notes[0].unlink()

    report = verify_vault(tmp_path)
    assert report["manifest_mismatch"]


# --- Finding 5: a zero-lecture build must not dangle-link to Log.md ---


def test_zero_lecture_build_has_no_dangling_log_link(tmp_path):
    empty_catalog = UdemyCatalog(
        courses=[
            UdemyCourse(
                id="123",
                title="Empty Course",
                url="https://www.udemy.com/course/empty/",
                instructor="Someone",
                sections=[],
            )
        ]
    )
    build_vault(empty_catalog, vault_dir=tmp_path)

    assert (tmp_path / "Log.md").exists()
    report = verify_vault(tmp_path)
    assert "Log" not in report["dangling_links"]


# --- destructive-rebuild guard ---


def test_build_refuses_to_prune_a_foreign_directory(tmp_path):
    (tmp_path / "topics").mkdir()
    foreign_file = tmp_path / "topics" / "someone-elses-note.md"
    foreign_file.write_text("not ours", encoding="utf-8")

    with pytest.raises(RuntimeError):
        build_vault(_catalog(), vault_dir=tmp_path)

    # The foreign content must survive the refused build.
    assert foreign_file.exists()
    assert foreign_file.read_text(encoding="utf-8") == "not ours"


def test_build_into_empty_directory_works(tmp_path):
    target = tmp_path / "fresh"
    build_vault(_catalog(), vault_dir=target)
    assert (target / "Home.md").exists()
    assert (target / ".udemy-vault").exists()


def test_rebuild_of_already_built_udemy_vault_works(tmp_path):
    build_vault(_catalog(("A",)), vault_dir=tmp_path)
    # Rebuilding must not raise, even without relying solely on the marker.
    build_vault(_catalog(("A", "B")), vault_dir=tmp_path)
    assert (tmp_path / "Home.md").exists()


def test_rebuild_works_via_marker_even_if_courses_dir_absent(tmp_path):
    (tmp_path / ".udemy-vault").touch()
    (tmp_path / "topics").mkdir()
    (tmp_path / "topics" / "stray.md").write_text("x", encoding="utf-8")
    # Marker present -> treated as ours, no RuntimeError.
    build_vault(_catalog(), vault_dir=tmp_path)
    assert (tmp_path / "Home.md").exists()
