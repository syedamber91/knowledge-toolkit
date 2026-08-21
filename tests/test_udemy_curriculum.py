import json
from pathlib import Path

import pytest

from udemy_toolkit.curriculum import course_slug, parse_curriculum

FIXTURE = Path(__file__).parent / "fixtures" / "udemy" / "sample_curriculum.json"


def _parse():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parse_curriculum(
        payload,
        course_id="123",
        course_title="Test Course",
        course_url="https://www.udemy.com/course/test/",
        instructor="Someone",
    )


def test_course_slug_from_various_urls():
    assert course_slug("https://www.udemy.com/course/test-course/") == "test-course"
    assert course_slug("https://www.udemy.com/course/test-course/learn/lecture/42") == "test-course"


def test_course_slug_rejects_a_non_course_url():
    with pytest.raises(ValueError):
        course_slug("https://www.udemy.com/home/my-courses/")


def test_sections_and_lectures_are_grouped_in_order():
    course = _parse()
    assert [s.title for s in course.sections] == ["Getting Started", "Going Deeper"]
    assert [s.order for s in course.sections] == [1, 2]
    assert [lec.title for lec in course.sections[0].lectures] == ["Welcome", "Setup"]


def test_non_lecture_items_are_dropped():
    course = _parse()
    assert all(lec.title != "Quiz 1" for lec in course.lectures())


def test_lecture_fields_are_populated():
    lecture = _parse().sections[0].lectures[0]
    assert lecture.id == "10"
    assert lecture.duration_seconds == 125
    assert lecture.section_title == "Getting Started"
    assert lecture.url == "https://www.udemy.com/course/test/learn/lecture/10"
    assert lecture.has_transcript is False
    assert lecture.transcript == ""


def test_lecture_before_any_chapter_lands_in_introduction():
    course = parse_curriculum(
        {"results": [{"_class": "lecture", "id": 5, "title": "Orphan", "asset": {}}]},
        course_id="123",
        course_title="T",
        course_url="https://www.udemy.com/course/test/",
    )
    assert course.sections[0].title == "Introduction"
    assert course.sections[0].order == 1
