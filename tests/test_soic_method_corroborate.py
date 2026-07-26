from soic_method.corroborate import (
    ATTEST_WINDOW_CHARS,
    _attested_in,
    corroborate,
    metric_patterns_for,
)
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
#
# Every fixture below deliberately CONTAINS a metric term, so the window
# gate (added for final-branch-review.md C2) is satisfied and each
# assertion still turns on the numeric matcher, not on the text trivially
# having no metric context. A fixture without one would pass these tests
# for the wrong reason.

def test_attested_in_rejects_value_that_is_digit_substring_of_real_number():
    # "8" is a literal substring of "18%" -- a plain `in` check (the
    # brief's `_value_forms`/`_attested_in`) reports this as attested;
    # `_extract_numbers` correctly extracts only 18.0, not 8.0.
    text = "our roc threshold is 18% across the board honestly"
    assert _attested_in(text, [8]) is False


def test_attested_in_rejects_value_that_is_decimal_prefix_of_real_number():
    # "18" is a literal substring of "18.5" -- same bug class, decimal
    # form. Mirrors verify.py's round-3 fix
    # (test_rejects_value_that_is_decimal_prefix_of_real_number).
    text = "the roc was 18.5 percent last quarter frankly"
    assert _attested_in(text, [18]) is False


def test_attested_in_accepts_comma_grouped_value_as_genuine_match():
    # "18,000" is a genuine attestation of 18000 despite the thousands
    # comma -- a naive digit-string membership check without comma
    # stripping would miss this (false negative), same corpus shape as
    # verify.py's round-4 fix (~21 real corpus occurrences of
    # comma-grouped crore/lakh figures).
    text = "revenue growth took us past 18,000 crore this year in the call"
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


# --- Gate 1b attests CONTEXTUALLY, not anywhere in the lesson ----------------
# final-branch-review.md C2. On the real corpus 52-56 of the integers 1..100
# appear somewhere in each ~100KB lesson body, so a whole-body scan promoted
# 41/100 arbitrary values to "active" on two citations. An attesting
# occurrence must sit within +/-ATTEST_WINDOW_CHARS of a metric term the
# rule is about. Re-measured after this change: 1/100.

FILLER = "and then we talked about something else entirely for a while. "


def test_number_far_from_any_metric_term_does_not_attest():
    # The value is present in the text -- just nowhere near the metric.
    text = ("our roc bar is a hard one across the cycle honestly. "
            + FILLER * 40 + "the flight was delayed by 15 minutes that day.")
    assert len(text) > 2 * ATTEST_WINDOW_CHARS
    assert _attested_in(text, [15], metric_patterns_for(
        Rule(tier="graded", kind="threshold", stage="screen",
             operator="gte", value=15, rule_key="screen.roc.floor"))) is False


def test_number_next_to_the_metric_term_does_attest():
    text = "our roc bar is at least 15 percent across the cycle honestly."
    assert _attested_in(text, [15], metric_patterns_for(
        Rule(tier="graded", kind="threshold", stage="screen",
             operator="gte", value=15, rule_key="screen.roc.floor"))) is True


def test_a_value_beside_the_WRONG_metric_does_not_attest():
    # "15" here is a P/E number; the rule is about ROC. This is the ASR
    # failure the gate exists for: a corrupted digit finding an unrelated
    # match elsewhere in the corpus.
    text = "we are happy paying a pe ratio of 15 times for this business."
    roc_rule = Rule(tier="graded", kind="threshold", stage="screen",
                    operator="gte", value=15, rule_key="screen.roc.floor")
    assert _attested_in(text, [15], metric_patterns_for(roc_rule)) is False


def test_metric_patterns_fall_back_to_any_metric_for_an_unnamed_rule():
    # A draft rule with no rule_key still gets the window bound, but cannot
    # be pinned to one metric -- failing closed there would downgrade every
    # unnamed rule for a reason unrelated to its evidence.
    unnamed = Rule(tier="graded", kind="threshold", stage="screen",
                   operator="gte", value=15)
    text = "we are happy paying a pe ratio of 15 times for this business."
    assert _attested_in(text, [15], metric_patterns_for(unnamed)) is True


def test_corroborate_does_not_promote_on_a_distant_coincidental_number():
    # End-to-end: two lessons that both contain "15" far from any ROC talk.
    body = ("[00:01:00] our roc discipline has never wavered honestly.\n"
            + FILLER * 40 + "\n[00:40:00] it rained for 15 days straight.\n")
    lessons = {"1": _lesson("1", body), "2": _lesson("2", body)}
    rule = Rule(
        tier="graded", kind="threshold", stage="screen", operator="gte",
        value=15, rule_key="screen.roc.floor",
        citations=[Citation(lesson_id=lid, lesson_url="u",
                            timestamp="00:01:00", span=Span(start=0, end=50))
                   for lid in ("1", "2")],
    )
    out = corroborate(rule, lessons)
    assert out.corroboration == 0
    assert out.status == "needs_audio_check"


def test_range_bounds_must_be_attested_by_a_SINGLE_window():
    # "between 15 and 30 times earnings" is one utterance. A lesson saying
    # 15 in one place and 30 in another has not attested the band. This
    # pins the `all()` semantics the review flagged as untested (Minor 6),
    # for the exact rule shape the pilot's only conflict is made of.
    split = ("[00:01:00] a pe ratio of 15 is where we like to buy.\n"
             + FILLER * 40 + "\n[00:40:00] a pe ratio of 30 is the top end.\n")
    together = "[00:01:00] we want a pe ratio of 15 to 30 times, no higher.\n"
    band = Rule(tier="graded", kind="range", stage="screen",
                rule_key="screen.pe.ceiling",
                value_range={"min": 15, "max": 30},
                citations=[Citation(lesson_id="1", lesson_url="u",
                                    timestamp="00:01:00",
                                    span=Span(start=0, end=50))])
    assert corroborate(band, {"1": _lesson("1", split)}).corroboration == 0
    assert corroborate(band, {"1": _lesson("1", together)}).corroboration == 1
