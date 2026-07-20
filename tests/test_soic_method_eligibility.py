from pathlib import Path

from soic_method.eligibility import apply_eligibility, load_eligibility
from soic_method.models import LessonRecord

CONFIG = Path(__file__).resolve().parents[1] / "configs" / "course_eligibility.yaml"


def _lesson(course, module):
    return LessonRecord(
        lesson_id="1", course_title=course, module_title=module,
        title="t", url="u", body_text="b",
    )


def test_solo_course_is_eligible():
    e = load_eligibility(CONFIG)
    assert e.is_eligible("Level 5- How to Screen & Filter Epic Stocks", "any")


def test_interview_course_is_excluded():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible("Conversation with India's Super Investors", "any")


def test_guest_module_inside_eligible_course_is_excluded():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible(
        "Level 6 Become a Sectoral Expert",
        "A Primer to SaaS by Siddharth Bhandari",
    )


def test_unknown_course_defaults_to_ineligible():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible("Some Course We Never Classified", "any")


def test_level_one_is_marked_translated():
    e = load_eligibility(CONFIG)
    assert e.fidelity("Level 1- Financial Literacy Course For All (Hindi)") == "translated"


def test_apply_eligibility_stamps_records():
    e = load_eligibility(CONFIG)
    lessons = [
        _lesson("Level 5- How to Screen & Filter Epic Stocks", "m"),
        _lesson("Conversation with India's Super Investors", "m"),
    ]
    out = apply_eligibility(lessons, e)
    assert [l.eligible for l in out] == [True, False]
