from soic_method.models import Binding, Citation, LessonRecord, Rule, Span
from soic_method.verify import verify_rule

BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[00:41:12] we don't even look at a business doing less than 18% ROC frankly\n"
    "[00:41:30] anyway moving on to the next topic entirely.\n"
)
HASH = "deadbeef"


def _lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=BODY, text_hash=HASH, eligible=True,
        )
    }


def _span_of(text):
    s = BODY.index(text)
    return Span(start=s, end=s + len(text))


QUOTE = "we don't even look at a business doing less than 18% ROC frankly"


def _rule(**over):
    base = dict(
        tier="graded", kind="threshold", stage="screen",
        operator="lte", value=18, unit="percent",
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                            span=_span_of(QUOTE), text_hash=HASH)],
    )
    base.update(over)
    return Rule(**base)


def test_valid_rule_passes():
    assert verify_rule(_rule(), _lessons()).ok


def test_rejects_span_shorter_than_minimum():
    short = Span(start=BODY.index("18%"), end=BODY.index("18%") + 3)
    r = _rule(citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                                  span=short, text_hash=HASH)])
    res = verify_rule(r, _lessons())
    assert not res.ok and any("too short" in x for x in res.reasons)


def test_rejects_offsets_out_of_range():
    bad = Span(start=99000, end=99100)
    r = _rule(citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                                  span=bad, text_hash=HASH)])
    res = verify_rule(r, _lessons())
    assert not res.ok and any("out of range" in x for x in res.reasons)


def test_rejects_when_value_absent_from_span():
    # Span says 18%, rule claims 15 — the silent-wrong-value case.
    res = verify_rule(_rule(value=15), _lessons())
    assert not res.ok and any("value 15" in x for x in res.reasons)


def test_rejects_inverted_operator():
    # Span says "less than", rule claims gte — the silent-inversion case.
    res = verify_rule(_rule(operator="gte"), _lessons())
    assert not res.ok and any("direction" in x for x in res.reasons)


def test_rejects_corpus_hash_mismatch():
    res = verify_rule(_rule(), {
        "1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                          title="t", url="u", body_text=BODY,
                          text_hash="different", eligible=True)
    })
    assert not res.ok and any("hash" in x for x in res.reasons)


def test_rejects_ineligible_lesson():
    lessons = _lessons()
    lessons["1"] = lessons["1"].model_copy(update={"eligible": False})
    res = verify_rule(_rule(), lessons)
    assert not res.ok and any("ineligible" in x for x in res.reasons)


def test_rejects_unknown_lesson():
    res = verify_rule(_rule(), {})
    assert not res.ok and any("unknown lesson" in x for x in res.reasons)


def test_boolean_rule_skips_value_and_direction_checks():
    r = Rule(
        tier="knockout", kind="boolean", stage="screen", conviction="absolute",
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                            span=_span_of(QUOTE), text_hash=HASH)],
    )
    assert verify_rule(r, _lessons()).ok
