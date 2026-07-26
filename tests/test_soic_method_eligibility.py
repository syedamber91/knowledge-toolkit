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


# --- Optional per-course module allow-list ----------------------------------
# final-branch-review.md I3. Module eligibility was a pure deny-list, so an
# unlisted module inside an eligible course was eligible by default --
# inverting the constraint that unclassified eligibility defaults to
# ineligible for courses AND modules alike. A course that HAS been
# module-classified can now opt into individual approval; courses that have
# not keep the previous behaviour rather than silently losing their lessons.

from soic_method.eligibility import Eligibility  # noqa: E402

L6 = "Level 6 Become a Sectoral Expert"


def test_allowlisted_course_admits_a_listed_module():
    e = load_eligibility(CONFIG)
    assert e.is_eligible(L6, "Decode EV Ecosystem In India")


def test_allowlisted_course_rejects_an_unlisted_module():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible(L6, "Some Module Nobody Ever Classified")


def test_allowlist_does_not_override_the_deny_list():
    # The two guest modules appear in the allow-list for completeness of the
    # classification record; exclusion still wins.
    e = load_eligibility(CONFIG)
    assert not e.is_eligible(L6, "A Primer To SAAS by Siddharth Bhandari")
    assert not e.is_eligible(L6, "Masterclass on Banks & NBFCs by Digant Haria")


def test_course_without_an_allowlist_keeps_deny_list_behaviour():
    # Level 5 declares no modules_allowlist, so any non-denied module passes.
    e = load_eligibility(CONFIG)
    assert e.is_eligible("Level 5- How to Screen & Filter Epic Stocks",
                         "A Module Nobody Classified")


def test_allowlist_matching_is_case_insensitive():
    e = Eligibility({"C": {"eligible": True, "modules_allowlist": ["Alpha Mod"]}},
                    excluded_modules=[])
    assert e.is_eligible("C", "alpha mod")
    assert not e.is_eligible("C", "beta mod")


def test_empty_allowlist_means_no_module_is_eligible():
    # Distinct from an ABSENT allow-list: [] is "classified, none approved".
    e = Eligibility({"C": {"eligible": True, "modules_allowlist": []}},
                    excluded_modules=[])
    assert not e.is_eligible("C", "anything")


def test_lesson_level_exclusion_inside_an_otherwise_eligible_module():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible(
        "SOIC Labs: Become an AI-Powered Investor",
        "SOIC Labs: Become an AI-Powered Investor",
        "Stocks Dashboard with Dr. Shashank",
    )


def test_sibling_lessons_in_the_same_module_stay_eligible():
    e = load_eligibility(CONFIG)
    assert e.is_eligible(
        "SOIC Labs: Become an AI-Powered Investor",
        "SOIC Labs: Become an AI-Powered Investor",
        "AI For The Intelligent Investor",
    )


def test_lesson_title_omitted_does_not_break_module_level_checks():
    # apply_eligibility always passes lesson_title, but is_eligible must
    # still work when called without one (backward compatible).
    e = load_eligibility(CONFIG)
    assert e.is_eligible("Level 5- How to Screen & Filter Epic Stocks", "any")


def test_defensive_lesson_exclusion_matches_even_with_no_content_yet():
    e = load_eligibility(CONFIG)
    assert not e.is_eligible(
        "Ask SOIC on Saturdays at 11 a.m.",
        "SOIC Exclusive Newsletter",
        "Interview with Mr.Rohit Chauhan (RC Capital)",
    )


def test_apply_eligibility_passes_lesson_title_through():
    e = load_eligibility(CONFIG)
    lessons = [
        _lesson("SOIC Labs: Become an AI-Powered Investor",
                "SOIC Labs: Become an AI-Powered Investor"),
    ]
    lessons[0] = lessons[0].model_copy(
        update={"title": "Stocks Dashboard with Dr. Shashank"})
    out = apply_eligibility(lessons, e)
    assert out[0].eligible is False
