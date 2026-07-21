import json

import pytest

from soic_method.extract import build_extract_prompt, extract_rules
from soic_method.models import Candidate, LessonRecord, Span

BODY = (
    "[00:00:05] some intro padding text goes here for length.\n"
    "[00:41:12] we don't even look at a business doing less than 18% ROC frankly\n"
)
QUOTE = "we don't even look at a business doing less than 18% ROC frankly"


def _lesson():
    return LessonRecord(lesson_id="1", course_title="c", module_title="m",
                        title="t", url="https://x/lesson/1", body_text=BODY,
                        text_hash="h", eligible=True)


def _cand():
    return Candidate(lesson_id="1", span=Span(start=0, end=len(BODY)), signals=["roc"])


def _llm_returning(payload):
    return lambda prompt: json.dumps(payload)


def test_prompt_includes_offset_indexed_text_and_forbids_quoting():
    p = build_extract_prompt(_lesson(), _cand())
    assert "start" in p and "end" in p
    assert "offset" in p.lower()


def test_extract_maps_offsets_to_citation_with_resolved_timestamp():
    s = BODY.index(QUOTE)
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "unit": "percent",
        "start": s, "end": s + len(QUOTE),
    }]}))
    assert len(rules) == 1
    cit = rules[0].citations[0]
    assert cit.timestamp == "00:41:12"
    assert cit.text_hash == "h"
    assert cit.lesson_url == "https://x/lesson/1"


def test_extract_drops_rules_with_out_of_range_offsets():
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "start": 0, "end": 999999,
    }]}))
    assert rules == []


def test_extract_tolerates_malformed_llm_output():
    assert extract_rules(_lesson(), _cand(), lambda p: "not json at all") == []


def test_extract_returns_empty_on_empty_rules_list():
    assert extract_rules(_lesson(), _cand(), _llm_returning({"rules": []})) == []


def test_prompt_lists_the_controlled_vocabulary():
    p = build_extract_prompt(_lesson(), _cand(), ["screen.roc.floor"])
    assert "screen.roc.floor" in p


def test_rule_key_outside_the_vocabulary_is_dropped_to_draft():
    s = BODY.index(QUOTE)
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "rule_key": "invented.key.here",
        "start": s, "end": s + len(QUOTE),
    }]}), rule_keys=["screen.roc.floor"])
    assert rules[0].rule_key is None
    assert rules[0].status == "draft"


def test_rule_key_inside_the_vocabulary_is_kept():
    s = BODY.index(QUOTE)
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [{
        "tier": "graded", "kind": "threshold", "stage": "screen",
        "operator": "lte", "value": 18, "rule_key": "screen.roc.floor",
        "start": s, "end": s + len(QUOTE),
    }]}), rule_keys=["screen.roc.floor"])
    assert rules[0].rule_key == "screen.roc.floor"


def test_extract_returns_empty_when_llm_returns_bare_json_array():
    assert extract_rules(_lesson(), _cand(), lambda p: "[]") == []


def test_extract_returns_empty_when_llm_returns_json_null():
    assert extract_rules(_lesson(), _cand(), lambda p: "null") == []


def test_extract_returns_empty_when_rules_key_is_not_a_list_int():
    assert extract_rules(_lesson(), _cand(), lambda p: '{"rules": 123}') == []


def test_extract_returns_empty_when_rules_key_is_not_a_list_bool():
    assert extract_rules(_lesson(), _cand(), lambda p: '{"rules": true}') == []


# --- Enum closure degrades gracefully (final-branch-review.md C1) -------------
# Rule's enum fields are now closed, so an LLM emitting an unrecognised
# `tier`/`kind`/`stage`/`conviction` raises at construction. extract_rules
# must DROP that rule and keep going, not crash the stage -- and must not
# fall back to a default that publishes the rule anyway.

def _span():
    s = BODY.index(QUOTE)
    return {"start": s, "end": s + len(QUOTE)}


def _raw(**over):
    base = {"tier": "graded", "kind": "threshold", "stage": "screen",
            "operator": "lte", "value": 18}
    base.update(over)
    base.update(_span())
    return base


@pytest.mark.parametrize("field,bad", [
    ("tier", "knockout_but_spelled_wrong"),
    ("stage", "portfolio"),
    ("conviction", "very sure"),
])
def test_extract_drops_rules_with_out_of_vocabulary_enums(field, bad):
    rules = extract_rules(_lesson(), _cand(),
                          _llm_returning({"rules": [_raw(**{field: bad})]}))
    assert rules == []


def test_extract_drops_only_the_bad_rule_from_a_mixed_batch():
    # A misbehaving extractor must not take the whole span's output with it.
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [
        _raw(tier="banana"),
        _raw(),
    ]}))
    assert len(rules) == 1
    assert rules[0].tier == "graded"


# --- kind is derived from the value shape (final-branch-review.md I4) ---------

def test_range_values_force_kind_range_and_null_operator():
    # The model mislabels a band as a threshold. Previously this built a
    # kind="threshold" rule carrying a value_range, which verify.py then
    # rejected as "unhandled operator None" -- a schema-shape fault
    # reported as an operator fault, polluting rejected.jsonl (the spec's
    # calibration signal).
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [
        _raw(kind="threshold", operator=None, value=None,
             value_min=40, value_max=50),
    ]}))
    assert len(rules) == 1
    assert rules[0].kind == "range"
    assert rules[0].operator is None
    assert (rules[0].value_range.min, rules[0].value_range.max) == (40, 50)


def test_scalar_value_forces_kind_threshold():
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [
        _raw(kind="range", value=18, operator="lte"),
    ]}))
    assert len(rules) == 1
    assert rules[0].kind == "threshold"
    assert rules[0].value_range is None


def test_threshold_without_an_operator_is_dropped_not_published():
    # A cutoff with no comparative direction cannot be verified: "18% ROC"
    # alone does not say floor or ceiling.
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [
        _raw(operator=None),
    ]}))
    assert rules == []


def test_rule_with_no_values_at_all_is_dropped_unless_declared_boolean():
    assert extract_rules(_lesson(), _cand(), _llm_returning({"rules": [
        _raw(kind="threshold", value=None, operator=None),
    ]})) == []


def test_declared_boolean_with_no_values_survives():
    rules = extract_rules(_lesson(), _cand(), _llm_returning({"rules": [
        _raw(kind="boolean", value=None, operator=None),
    ]}))
    assert len(rules) == 1
    assert rules[0].kind == "boolean"
    assert rules[0].value is None and rules[0].value_range is None
