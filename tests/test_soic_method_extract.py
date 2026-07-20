import json

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
