from soic_method.models import Citation, LessonRecord, Rule, ScopeAttestation, Span
from soic_method.reconcile import (
    classify_group,
    merge_agreeing,
    reconcile,
    resolution_key,
)

BODY = ("[00:00:05] padding padding padding padding padding padding padding\n"
        "[00:41:12] we don't even look at a business doing less than 18% ROC ok\n"
        "[00:50:00] in capital light businesses like exchanges we want much more\n")
QUOTE = "we don't even look at a business doing less than 18% ROC ok"
SCOPE_QUOTE = "in capital light businesses like exchanges we want much more"


def _lessons():
    return {"1": LessonRecord(lesson_id="1", course_title="c", module_title="m",
                              title="t", url="u", body_text=BODY,
                              text_hash="h", eligible=True)}


def _cit(text):
    s = BODY.index(text)
    return Citation(lesson_id="1", lesson_url="u", timestamp="00:41:12",
                    span=Span(start=s, end=s + len(text)), text_hash="h")


def _rule(value, key="screen.roc.floor", scope=None, attest=None):
    return Rule(tier="graded", kind="threshold", stage="screen", operator="lte",
                value=value, rule_key=key, scope=scope or {},
                scope_attestation=attest, citations=[_cit(QUOTE)])


def test_resolution_key_is_quote_independent():
    a = _rule(18)
    b = _rule(18)
    b.citations[0].span = Span(start=0, end=60)   # span moved
    assert resolution_key(a) == resolution_key(b)


def test_agreeing_rules_merge_into_one_with_many_citations():
    merged = merge_agreeing([_rule(18), _rule(18)], _lessons())
    assert len(merged.citations) == 2
    assert merged.value == 18


def test_merge_calls_corroborate_not_a_second_lesson_count():
    # Two rules citing the SAME lesson (not two different lessons) should
    # merge to corroboration=1 (one attesting stream) per corroborate()'s
    # own definition -- NOT 2, which a naive len(distinct lesson_ids) count
    # would wrongly produce by counting citations instead of streams.
    merged = merge_agreeing([_rule(18), _rule(18)], _lessons())
    assert merged.corroboration == 1
    assert merged.status == "needs_audio_check"


def test_same_value_group_is_merged():
    verdict, rules = classify_group([_rule(18), _rule(18)], _lessons())
    assert verdict == "merged"
    assert len(rules) == 1


def test_different_values_without_attested_scope_is_a_conflict():
    verdict, _ = classify_group([_rule(18), _rule(15)], _lessons())
    assert verdict == "conflict"


def test_different_values_with_unattested_scope_is_still_a_conflict():
    # Scope claimed but with no evidence span — the laundering path.
    a = _rule(18, scope={"business_type": "capital_light"})
    b = _rule(15, scope={"business_type": "cyclical"})
    verdict, _ = classify_group([a, b], _lessons())
    assert verdict == "conflict"


def test_different_values_with_verified_scope_attestation_are_variants():
    s = BODY.index(SCOPE_QUOTE)
    attest = ScopeAttestation(lesson_id="1",
                              span=Span(start=s, end=s + len(SCOPE_QUOTE)))
    a = _rule(18, scope={"business_type": "capital_light"}, attest=attest)
    b = _rule(15, scope={"business_type": "cyclical"}, attest=attest)
    verdict, rules = classify_group([a, b], _lessons())
    assert verdict == "variants"
    assert len(rules) == 2


def test_reconcile_routes_conflicts_to_the_queue():
    out = reconcile([_rule(18), _rule(15)], _lessons(), {})
    assert len(out.conflicts) == 1
    assert out.rules == []


def test_resolutions_are_applied_and_survive_span_shifts():
    a, b = _rule(18), _rule(15)
    a.citations[0].span = Span(start=0, end=60)     # spans differ from build time
    key = resolution_key(a)
    out = reconcile([a, b], _lessons(), {key: {"keep": 18}})
    assert out.conflicts == []
    assert len(out.rules) == 1
    assert out.rules[0].value == 18


def test_rules_without_a_key_never_group():
    out = reconcile([_rule(18, key=None), _rule(15, key=None)], _lessons(), {})
    assert out.conflicts == []
    assert len(out.drafts) == 2
