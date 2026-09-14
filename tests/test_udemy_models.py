from udemy_toolkit.models import (
    UdemyCatalog,
    UdemyCourse,
    UdemyLecture,
    UdemySection,
)


def _course(course_id="1", lecture_ids=("10",)):
    lectures = [
        UdemyLecture(id=i, title=f"Lecture {i}", url=f"https://u/{i}", section_title="S1")
        for i in lecture_ids
    ]
    return UdemyCourse(
        id=course_id,
        title="Test Course",
        url="https://www.udemy.com/course/test/",
        sections=[UdemySection(title="S1", order=1, lectures=lectures)],
    )


def test_known_ids_includes_captured_and_skipped():
    catalog = UdemyCatalog(courses=[_course(lecture_ids=("10", "11"))], seen_lecture_ids=["99"])
    assert catalog.known_ids() == {"10", "11", "99"}


def test_upsert_course_replaces_by_id_not_appends():
    catalog = UdemyCatalog(courses=[_course(lecture_ids=("10",))])
    catalog.upsert_course(_course(lecture_ids=("10", "11")))
    assert len(catalog.courses) == 1
    assert catalog.total_lectures() == 2


def test_upsert_course_appends_a_different_course():
    catalog = UdemyCatalog(courses=[_course(course_id="1")])
    catalog.upsert_course(_course(course_id="2"))
    assert len(catalog.courses) == 2


def test_round_trips_through_disk(tmp_path):
    path = tmp_path / "udemy.json"
    UdemyCatalog(courses=[_course()], seen_lecture_ids=["55"]).save(path)
    loaded = UdemyCatalog.load(path)
    assert loaded.total_lectures() == 1
    assert loaded.seen_lecture_ids == ["55"]


def test_load_returns_empty_catalog_when_file_missing(tmp_path):
    loaded = UdemyCatalog.load(tmp_path / "nope.json")
    assert loaded.courses == []
