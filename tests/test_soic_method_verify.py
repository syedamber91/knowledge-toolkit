from soic_method.models import Citation, LessonRecord, Rule, Span, ValueRange
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


# --- Regression tests for task-5-review.md Critical-1 -----------------------
# Naive `in` substring matching (pre-fix) let a wrong claimed value pass
# because it happened to be a digit-substring of the real number, and let a
# wrong direction pass because a direction token happened to be a substring
# of an unrelated word. Both are fixed with \b-anchored regex, mirroring
# router.py's `_METRIC_PATTERNS` fix in 83d92d0.

def test_rejects_value_that_is_digit_substring_of_real_number():
    # Span genuinely says "18% ROC"; rule claims value=8, which is a true
    # substring of "18" (`"8" in "18%"`) but never appears as its own
    # number. Operator stays correct (lte) so only the value check is under
    # test. Reproduces the review's Case 1 adversarial construction.
    res = verify_rule(_rule(value=8), _lessons())
    assert not res.ok and any("value 8" in x for x in res.reasons)


def test_rejects_value_that_is_leading_digit_substring_of_real_number():
    # Same construction with the OTHER digit of "18" (review's Case 2).
    res = verify_rule(_rule(value=1), _lessons())
    assert not res.ok and any("value 1" in x for x in res.reasons)


TRAP_BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[00:12:00] we always eliminate promoters who pledge 5 percent of shares "
    "no matter what anyone says\n"
    "[00:12:20] anyway moving on to the next topic entirely.\n"
)
TRAP_QUOTE = (
    "we always eliminate promoters who pledge 5 percent of shares "
    "no matter what anyone says"
)


def _trap_lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=TRAP_BODY, text_hash=HASH, eligible=True,
        )
    }


def _trap_span():
    s = TRAP_BODY.index(TRAP_QUOTE)
    return Span(start=s, end=s + len(TRAP_QUOTE))


def test_rejects_direction_token_that_is_substring_of_unrelated_word():
    # Span contains no genuine gte language at all — the only string that
    # overlaps a DIRECTION_TOKENS["gte"] entry is "min" embedded inside
    # "eliminate" ("eli-MIN-ate"), with no word boundary around it. The
    # claimed value (5) IS genuinely present, isolating this to the
    # direction check. Reproduces the review's Case 3.
    r = _rule(
        operator="gte",
        value=5,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:12:00",
                            span=_trap_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _trap_lessons())
    assert not res.ok and any("direction" in x for x in res.reasons)


# --- Regression tests for task-5-review.md Minor findings -------------------

def test_rejects_rule_with_no_citations():
    # Minor-1: the "no citations -> reject" early return was correct but
    # untested.
    res = verify_rule(_rule(citations=[]), _lessons())
    assert not res.ok and any("no citations" in x for x in res.reasons)


def test_non_boolean_rule_with_missing_value_is_not_exempted():
    # Minor-2: the boolean exemption must key off rule.kind == "boolean",
    # not off value/operator happening to be absent. A malformed
    # kind="threshold" rule with no value and no value_range must be
    # flagged, not silently treated as "not applicable" like a real
    # boolean rule would be.
    r = _rule(kind="threshold", value=None, value_range=None)
    res = verify_rule(r, _lessons())
    assert not res.ok
    assert any("malformed" in x for x in res.reasons)


def test_rejects_when_citation_hash_is_empty():
    # Minor-3: an empty text_hash on either side must fail CLOSED (treated
    # as a mismatch), not be skipped.
    r = _rule(citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                                  span=_span_of(QUOTE), text_hash="")])
    res = verify_rule(r, _lessons())
    assert not res.ok and any("hash" in x for x in res.reasons)


def test_rejects_when_lesson_hash_is_empty():
    lessons = _lessons()
    lessons["1"] = lessons["1"].model_copy(update={"text_hash": ""})
    res = verify_rule(_rule(), lessons)
    assert not res.ok and any("hash" in x for x in res.reasons)


# --- Regression tests for task-5-review.md New-Critical-1 -------------------
# operator="eq" is a valid model OPERATORS value (models.py) but has no
# DIRECTION_TOKENS entry. The old `if rule.operator in DIRECTION_TOKENS:`
# gate silently skipped check 4 entirely for "eq" -- zero directional
# verification, no reason emitted either way. Fixed with an explicit
# three-way branch: eq is deliberately exempted (no natural "wrong
# direction" for equality), any OTHER unhandled operator now explicitly
# rejects instead of falling through.

def test_eq_operator_with_matching_value_passes():
    # "eq" is deliberately exempted from directional-token matching (no
    # natural "wrong direction" for equality) -- but the value check must
    # still apply and still pass for a genuine match. Span says "18% ROC"
    # (no equality language at all); claimed value=18, operator=eq should
    # still pass overall because direction checking is N/A for eq, not
    # because it was silently skipped due to a missing dict key.
    res = verify_rule(_rule(operator="eq", value=18), _lessons())
    assert res.ok


def test_unhandled_operator_is_rejected_not_silently_passed():
    # Any operator that is neither "eq" nor a DIRECTION_TOKENS key must
    # FAIL CLOSED, proving the fallback branch fires rather than silently
    # passing the way the pre-fix code did for every non-DIRECTION_TOKENS
    # operator (including "eq"). Rule.operator isn't constrained by a
    # pydantic Literal/validator to models.OPERATORS, so this exercises
    # the fallback with a value outside that tuple -- standing in for any
    # future operator this dict hasn't been taught yet. The claimed value
    # (18) is genuinely present, isolating this to the direction/operator
    # branch.
    res = verify_rule(_rule(operator="ne", value=18), _lessons())
    assert not res.ok
    assert any("unhandled operator" in x for x in res.reasons)


# --- Regression tests for task-5-review.md New-Critical-2 -------------------
# The round-1 \b-boundary fix treats "." as a valid boundary character
# (non-\w), so a claimed integer value that is a true digit-*prefix* of a
# real decimal number in the span (e.g. claimed 18 vs real "18.5") still
# matched `\b18\b`. Fixed with `(?<![\d.])`/`(?![\d.])` lookaround, which
# also excludes an adjacent decimal point, not just an adjacent digit.

DECIMAL_BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[00:15:00] we would never buy a business trading above 18.5 times earnings okay\n"
    "[00:15:20] anyway moving on to the next topic entirely.\n"
)
DECIMAL_QUOTE = (
    "we would never buy a business trading above 18.5 times earnings okay"
)


def _decimal_lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=DECIMAL_BODY, text_hash=HASH, eligible=True,
        )
    }


def _decimal_span():
    s = DECIMAL_BODY.index(DECIMAL_QUOTE)
    return Span(start=s, end=s + len(DECIMAL_QUOTE))


def test_rejects_value_that_is_decimal_prefix_of_real_number():
    # Span genuinely says "18.5 times earnings" (true value 18.5, not 18).
    # Claimed value=18 is a true digit-prefix separated only by ".", which
    # the round-1 \b fix wrongly treated as a valid boundary. Operator
    # stays a real DIRECTION_TOKENS key ("gte", matching "above") so this
    # isolates the value check specifically.
    r = _rule(
        operator="gte", value=18,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:15:00",
                            span=_decimal_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _decimal_lessons())
    assert not res.ok and any("value 18" in x for x in res.reasons)


RANGE_BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[00:20:00] historically we've paid between 15.2 and 25.9 times earnings for compounders\n"
    "[00:20:20] anyway moving on to the next topic entirely.\n"
)
RANGE_QUOTE = (
    "historically we've paid between 15.2 and 25.9 times earnings for compounders"
)


def _range_lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=RANGE_BODY, text_hash=HASH, eligible=True,
        )
    }


def _range_span():
    s = RANGE_BODY.index(RANGE_QUOTE)
    return Span(start=s, end=s + len(RANGE_QUOTE))


def test_rejects_value_range_bounds_that_are_decimal_prefixes():
    # Same construction against the value_range bound-checking path (which
    # calls the same `_value_present` helper): claimed bounds (15, 25) are
    # digit-prefixes of the real decimals (15.2, 25.9) in the span.
    r = _rule(
        kind="range", operator=None, value=None,
        value_range=ValueRange(min=15, max=25),
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:20:00",
                            span=_range_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _range_lessons())
    assert not res.ok
    assert any("range bound 15" in x for x in res.reasons)
    assert any("range bound 25" in x for x in res.reasons)


def test_rejects_value_digit_adjacent_to_larger_integer_still_works():
    # Confirms the ORIGINAL round-1 digit-adjacency fix still holds for a
    # two-digit claimed value after the New-Critical-2 regex change: "18"
    # embedded inside "118" (leading-digit adjacency, no decimal point
    # involved) must still be rejected. Uses operator="eq" so only the
    # value check is under test (direction is N/A for eq).
    body = (
        "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
        "[00:30:00] the promoter pledged 118 crore worth of shares last quarter\n"
        "[00:30:20] anyway moving on to the next topic entirely.\n"
    )
    quote = "the promoter pledged 118 crore worth of shares last quarter"
    s = body.index(quote)
    lessons = {
        "1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                          title="t", url="u", body_text=body, text_hash=HASH,
                          eligible=True)
    }
    r = _rule(
        operator="eq", value=18,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:30:00",
                            span=Span(start=s, end=s + len(quote)), text_hash=HASH)],
    )
    res = verify_rule(r, lessons)
    assert not res.ok and any("value 18" in x for x in res.reasons)


def test_standalone_percent_value_still_passes_no_regression():
    # No-regression check: a genuine standalone "18%" (existing QUOTE/
    # _lessons fixture) must still pass after tightening the boundary
    # regex to also exclude adjacent decimal points.
    assert verify_rule(_rule(value=18), _lessons()).ok


def test_standalone_percent_word_value_still_passes_no_regression():
    # Same, for the "18 percent" word form (space before "percent", no
    # "%" sign, no decimal point anywhere nearby).
    body = (
        "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
        "[00:40:00] we want promoter pledge below 18 percent of holding always\n"
        "[00:40:20] anyway moving on to the next topic entirely.\n"
    )
    quote = "we want promoter pledge below 18 percent of holding always"
    s = body.index(quote)
    lessons = {
        "1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                          title="t", url="u", body_text=body, text_hash=HASH,
                          eligible=True)
    }
    r = _rule(
        operator="lte", value=18,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:40:00",
                            span=Span(start=s, end=s + len(quote)), text_hash=HASH)],
    )
    assert verify_rule(r, lessons).ok


# --- Regression tests for task-5-review.md round 3 ---------------------------
# Round 3 diagnosed the boundary-anchored substring-search approach
# (`(?<![\d.])<form>(?![\d.])`) as structurally wrong -- it needs one more
# excluded-adjacency character every time a new corpus construction turns up
# (digit -> round 1, decimal point -> round 2, comma/sign -> round 3 here).
# Fixed by replacing it with number extraction (`_extract_numbers`) + float
# comparison, which closes the whole class instead of one more instance.

COMMA_BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[00:50:00] the promoter pledged 18,000 shares against a personal loan again\n"
    "[00:50:20] anyway moving on to the next topic entirely.\n"
)
COMMA_QUOTE = "the promoter pledged 18,000 shares against a personal loan again"


def _comma_lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=COMMA_BODY, text_hash=HASH, eligible=True,
        )
    }


def _comma_span():
    s = COMMA_BODY.index(COMMA_QUOTE)
    return Span(start=s, end=s + len(COMMA_QUOTE))


def test_accepts_comma_grouped_value_as_genuine_match():
    # Round3-Critical-1 (correct-value direction): the real span says
    # "18,000 shares"; the claimed value IS the correct 18000. Pre-fix,
    # `_value_forms(18000)` produced only the comma-free string "18000",
    # which is never a literal substring of "18,000" -- so the genuinely
    # correct claim was spuriously REJECTED. Number extraction parses
    # "18,000" to 18000.0 directly, so this must now PASS.
    r = _rule(
        operator="eq", value=18000,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:50:00",
                            span=_comma_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _comma_lessons())
    assert res.ok


def test_rejects_smaller_value_against_comma_grouped_real_number():
    # Round3-Critical-1 (wrong-value direction): the real span says
    # "18,000 shares"; the claimed value is 18 -- a materially different,
    # 1000x smaller number. Pre-fix, the lookaround didn't exclude a comma,
    # so `_value_present(18, "...18,000...")` spuriously matched. Number
    # extraction parses "18,000" to 18000.0, which != 18, so this must
    # REJECT.
    r = _rule(
        operator="eq", value=18,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:50:00",
                            span=_comma_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _comma_lessons())
    assert not res.ok and any("value 18" in x for x in res.reasons)


SIGN_BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[00:55:00] same store sales actually fell to -5 percent for the quarter okay\n"
    "[00:55:20] anyway moving on to the next topic entirely.\n"
)
SIGN_QUOTE = "same store sales actually fell to -5 percent for the quarter okay"


def _sign_lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=SIGN_BODY, text_hash=HASH, eligible=True,
        )
    }


def _sign_span():
    s = SIGN_BODY.index(SIGN_QUOTE)
    return Span(start=s, end=s + len(SIGN_QUOTE))


def test_rejects_positive_value_against_real_negative_number():
    # Round3-Critical-2: the real span says sales fell to "-5 percent"
    # (negative five); the claimed value is a positive 5 -- the opposite
    # sign, an opposite-meaning number for an investing rule. Pre-fix, the
    # lookaround didn't exclude a leading "-", so `_value_present(5,
    # "...-5...")` spuriously matched. Number extraction parses "-5" to
    # -5.0, which != 5, so this must REJECT.
    r = _rule(
        operator="eq", value=5,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:55:00",
                            span=_sign_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _sign_lessons())
    assert not res.ok and any("value 5" in x for x in res.reasons)


def test_accepts_genuine_negative_value_match():
    # Companion to the above: the claimed value IS the genuine -5. Number
    # extraction parses "-5" to -5.0, which equals the claim, so this must
    # PASS.
    r = _rule(
        operator="eq", value=-5,
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="00:55:00",
                            span=_sign_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _sign_lessons())
    assert res.ok


RANGE_NONE_BODY = (
    "[00:00:05] intro chatter here to pad the transcript out a bit.\n"
    "[01:00:00] we're happy paying a p e less than 50 or 40 times earnings okay\n"
    "[01:00:20] anyway moving on to the next topic entirely.\n"
)
RANGE_NONE_QUOTE = "we're happy paying a p e less than 50 or 40 times earnings okay"


def _range_none_lessons():
    return {
        "1": LessonRecord(
            lesson_id="1", course_title="c", module_title="m", title="t",
            url="u", body_text=RANGE_NONE_BODY, text_hash=HASH, eligible=True,
        )
    }


def _range_none_span():
    s = RANGE_NONE_BODY.index(RANGE_NONE_QUOTE)
    return Span(start=s, end=s + len(RANGE_NONE_QUOTE))


def test_range_rule_with_operator_none_is_not_unhandled_when_genuinely_cited():
    # Round3-Critical-3: kind="range" with operator=None is the ONLY
    # correct way to construct a range rule (models.OPERATORS has no
    # range/between entry, and the design spec's own kind: range example
    # carries no operator field). Pre-fix, round 2's fail-closed else
    # branch only exempted operator=="eq", so this genuinely, cleanly
    # cited range rule (both 40 and 50 literally present in the span) was
    # unconditionally rejected with "unhandled operator None: no
    # direction check defined" -- a false-reject blocking an entire
    # spec-documented rule shape. Must now PASS.
    r = _rule(
        kind="range", operator=None, value=None,
        value_range=ValueRange(min=40, max=50),
        citations=[Citation(lesson_id="1", lesson_url="u", timestamp="01:00:00",
                            span=_range_none_span(), text_hash=HASH)],
    )
    res = verify_rule(r, _range_none_lessons())
    assert res.ok


def test_threshold_rule_with_operator_none_still_rejected_as_unhandled():
    # The range/None exemption must NOT widen into a blanket
    # operator-is-None exemption: a kind="threshold" rule with a missing
    # operator still genuinely needs directional language and must still
    # fail closed via the "unhandled operator" branch. Uses the ordinary
    # QUOTE/_lessons fixture where the claimed value (18) is genuinely
    # present, isolating this to the operator branch.
    res = verify_rule(_rule(kind="threshold", operator=None, value=18), _lessons())
    assert not res.ok
    assert any("unhandled operator" in x for x in res.reasons)
