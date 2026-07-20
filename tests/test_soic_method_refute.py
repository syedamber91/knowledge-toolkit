import json

from soic_method.models import Citation, LessonRecord, Rule, Span
from soic_method.refute import build_refute_prompt, refute

BODY = ("[00:00:05] " + "padding " * 300 +
        "\n[00:41:12] we don't even look at a business doing less than 18% ROC\n" +
        "trailing " * 300)
QUOTE = "we don't even look at a business doing less than 18% ROC"


def _lessons():
    return {"1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                              title="t", url="u", body_text=BODY, eligible=True)}


def _rule():
    s = BODY.index(QUOTE)
    return Rule(tier="graded", kind="threshold", stage="screen", operator="lte",
                value=18,
                citations=[Citation(lesson_id="1", lesson_url="u",
                                    timestamp="00:41:12",
                                    span=Span(start=s, end=s + len(QUOTE)))])


def test_prompt_carries_surrounding_context_not_just_the_span():
    p = build_refute_prompt(_rule(), _lessons()["1"])
    assert "padding" in p and "trailing" in p


def test_prompt_lists_named_failure_modes():
    p = build_refute_prompt(_rule(), _lessons()["1"])
    for mode in ("negation", "reported speech", "hypothetical", "coheren"):
        assert mode in p.lower()


def test_survives_when_refuter_says_not_refuted():
    llm = lambda p: json.dumps({"refuted": False, "reason": "clear statement"})
    assert refute(_rule(), _lessons(), llm) is True


def test_killed_when_refuter_refutes():
    llm = lambda p: json.dumps({"refuted": True, "reason": "reported speech"})
    assert refute(_rule(), _lessons(), llm) is False


def test_fails_closed_on_malformed_output():
    # Ambiguity must fail closed — a broken refuter must not wave rules through.
    assert refute(_rule(), _lessons(), lambda p: "garbage") is False


def test_fails_closed_on_unknown_lesson():
    assert refute(_rule(), {}, lambda p: json.dumps({"refuted": False})) is False


# --- Additional fail-closed edge cases ------------------------------------

def test_fails_closed_when_refuted_key_is_not_boolean():
    # "refuted" present but not a real bool (e.g. a string) -- must not be
    # treated as truthy-falsy Python coercion; only `is False` survives.
    llm = lambda p: json.dumps({"refuted": "false", "reason": "ambiguous"})
    assert refute(_rule(), _lessons(), llm) is False


def test_fails_closed_when_refuted_key_missing():
    llm = lambda p: json.dumps({"reason": "no refuted key at all"})
    assert refute(_rule(), _lessons(), llm) is False


def test_fails_closed_when_llm_returns_non_dict_json():
    llm = lambda p: json.dumps([1, 2, 3])
    assert refute(_rule(), _lessons(), llm) is False


def test_fails_closed_when_no_citations():
    rule = Rule(tier="graded", kind="threshold", stage="screen", operator="lte",
                value=18, citations=[])
    assert refute(rule, _lessons(), lambda p: json.dumps({"refuted": False})) is False


# --- Walmart "ten years / over 30 times" construction ---------------------
# Carried forward from task-5-review.md (Round 6) / progress.md's explicit
# "CARRY FORWARD TO TASK 8" note: a real, hash-verified span from the lesson
# "Time vs Timing in the Market" was used to fabricate
# Rule(operator="gte", value=10, unit="years") -- claiming a >=10yr holding
# rule -- citing "...waited ten years after Walmart went public and made
# over 30 times your money." Both "ten"->10 and "over"->gte are literally
# present in the span, so this construction passes Gate 1 (verify.py) by
# design: Gate 1 only checks literal presence, not whether the value and
# the comparative-direction word are actually talking about the same thing.
# In the real sentence "over" governs the unrelated "30", not "10"; "ten
# years" is a holding-period aside, not a stated minimum-holding rule. This
# is precisely the failure mode Gate 2 exists to catch (spec-design.md's
# "value or direction not actually supported by context" checklist item,
# reproduced verbatim in FAILURE_MODES below).

WALMART_BODY = (
    "[00:00:05] " + "prelude " * 300 +
    "\n[00:52:30] if you bought it when they went public, you would have "
    "made five hundred times your money, but you could have waited ten "
    "years after Walmart went public and made over 30 times your money.\n" +
    "epilogue " * 300
)
WALMART_QUOTE = (
    "waited ten years after Walmart went public and made over 30 times "
    "your money"
)


def _walmart_lessons():
    return {"1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                              title="Time vs Timing in the Market", url="u",
                              body_text=WALMART_BODY, eligible=True)}


def _walmart_rule():
    s = WALMART_BODY.index(WALMART_QUOTE)
    return Rule(tier="graded", kind="threshold", stage="screen", operator="gte",
                value=10, unit="years",
                citations=[Citation(lesson_id="1", lesson_url="u",
                                    timestamp="00:52:30",
                                    span=Span(start=s, end=s + len(WALMART_QUOTE)))])


def test_walmart_construction_passes_gate1_shape_but_prompt_has_the_tell():
    # Proves the PLUMBING, not a real LLM's judgement: the prompt fed to the
    # refuter must contain both (a) enough surrounding context to see that
    # "over" modifies the unrelated "500"/"30" figures, not "10", and
    # (b) the named failure-mode checklist item that targets exactly this
    # ("the value or comparative direction is not actually supported by
    # context"), so a reasonable refuter reading it would plausibly catch
    # the disconnect a real LLM call is not made anywhere in this test.
    p = build_refute_prompt(_walmart_rule(), _walmart_lessons()["1"])
    # the true referent of "over" is visible in the surrounding context
    assert "five hundred times your money" in p
    # the claimed rule's own numbers are visible too
    assert "10" in p
    assert "years" in p
    # the specific "value/direction not connected" checklist item is present
    assert "not actually supported by context" in p.lower()


def test_walmart_construction_is_killed_when_refuter_calls_it_refuted():
    # Fake llm callback returns {"refuted": true} -- this test asserts only
    # that refute() correctly kills the rule on that response (the required
    # plumbing behaviour), not that a real LLM would say this.
    llm = lambda p: json.dumps({
        "refuted": True,
        "reason": "value and direction are not connected: 'ten years' is a "
                   "holding-period aside and 'over' modifies the unrelated "
                   "'30', not the claimed '10'",
    })
    assert refute(_walmart_rule(), _walmart_lessons(), llm) is False
