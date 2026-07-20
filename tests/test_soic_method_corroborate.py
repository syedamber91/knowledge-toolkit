from soic_method.corroborate import _attested_in, corroborate
from soic_method.models import Citation, LessonRecord, Rule, Span

QUOTE = "we don't even look at a business doing less than 18% ROC frankly"
BODY_A = "[00:41:12] " + QUOTE + "\n"
BODY_B = "[00:10:00] our bar is a minimum 18% ROC across the cycle honestly\n"


def _lesson(lid, body, summary=""):
    return LessonRecord(lesson_id=lid, course_title="c", module_title="m",
                        title="t", url="u", body_text=body,
                        ai_summary=summary, eligible=True)


def _rule(lesson_ids):
    return Rule(
        tier="graded", kind="threshold", stage="screen", operator="lte", value=18,
        citations=[
            Citation(lesson_id=i, lesson_url="u", timestamp="00:41:12",
                     span=Span(start=0, end=len(BODY_A)))
            for i in lesson_ids
        ],
    )


def test_two_lessons_corroborate_and_promote_to_active():
    lessons = {"1": _lesson("1", BODY_A), "2": _lesson("2", BODY_B)}
    out = corroborate(_rule(["1", "2"]), lessons)
    assert out.corroboration == 2
    assert out.status == "active"


def test_single_lesson_with_summary_attestation_counts_as_two():
    lessons = {"1": _lesson("1", BODY_A, summary="ROC threshold is 18% minimum")}
    out = corroborate(_rule(["1"]), lessons)
    assert out.corroboration == 2
    assert out.status == "active"


def test_single_uncorroborated_stream_needs_audio_check():
    lessons = {"1": _lesson("1", BODY_A, summary="no numbers in this summary")}
    out = corroborate(_rule(["1"]), lessons)
    assert out.corroboration == 1
    assert out.status == "needs_audio_check"


def test_boolean_rule_needs_no_numeric_corroboration():
    lessons = {"1": _lesson("1", BODY_A)}
    r = Rule(tier="knockout", kind="boolean", stage="screen", conviction="absolute",
             citations=[Citation(lesson_id="1", lesson_url="u",
                                 timestamp="00:00:00",
                                 span=Span(start=0, end=len(BODY_A)))])
    assert corroborate(r, lessons).status == "active"


# --- Regression tests: _attested_in must reuse verify._extract_numbers,
# not the brief's simpler substring/`in` check, or it silently re-opens the
# exact bug class Task 5 spent six review rounds closing (task-6-brief.md's
# own reference `_attested_in` is substring-based and would misjudge every
# case below -- confirmed directly against the brief's own snippet before
# writing these). Both failure directions matter here: a false POSITIVE
# would let one corrupted ASR stream masquerade as two independent
# attestations (defeating the whole point of Gate 1b); a false NEGATIVE
# would wrongly downgrade a genuinely double-attested threshold to
# needs_audio_check.

def test_attested_in_rejects_value_that_is_digit_substring_of_real_number():
    # "8" is a literal substring of "18%" -- a plain `in` check (the
    # brief's `_value_forms`/`_attested_in`) reports this as attested;
    # `_extract_numbers` correctly extracts only 18.0, not 8.0.
    text = "our threshold is 18% across the board honestly"
    assert _attested_in(text, [8]) is False


def test_attested_in_rejects_value_that_is_decimal_prefix_of_real_number():
    # "18" is a literal substring of "18.5" -- same bug class, decimal
    # form. Mirrors verify.py's round-3 fix
    # (test_rejects_value_that_is_decimal_prefix_of_real_number).
    text = "the number was 18.5 percent last quarter frankly"
    assert _attested_in(text, [18]) is False


def test_attested_in_accepts_comma_grouped_value_as_genuine_match():
    # "18,000" is a genuine attestation of 18000 despite the thousands
    # comma -- a naive digit-string membership check without comma
    # stripping would miss this (false negative), same corpus shape as
    # verify.py's round-4 fix (~21 real corpus occurrences of
    # comma-grouped crore/lakh figures).
    text = "revenue crossed 18,000 crore this year in the call frankly"
    assert _attested_in(text, [18000]) is True


def test_corroborate_does_not_promote_on_decimal_prefix_false_match():
    # End-to-end version of the decimal-boundary case above: two lessons
    # both state 18.5, never the bare 18 the rule claims. A substring-based
    # _attested_in would (wrongly) count both as attesting to 18 and
    # promote to active; the hardened version correctly leaves this
    # uncorroborated.
    body1 = "[00:01:00] our cutoff has always been 18.5 percent honestly\n"
    body2 = "[00:02:00] we hold the line at 18.5 percent across the cycle\n"
    lessons = {
        "1": _lesson("1", body1),
        "2": _lesson("2", body2),
    }
    rule = Rule(
        tier="graded", kind="threshold", stage="screen", operator="lte", value=18,
        citations=[
            Citation(lesson_id=lid, lesson_url="u", timestamp="00:01:00",
                     span=Span(start=0, end=len(body1)))
            for lid in ("1", "2")
        ],
    )
    out = corroborate(rule, lessons)
    assert out.corroboration == 0
    assert out.status == "needs_audio_check"
