import pytest
from pydantic import ValidationError

from soic_method.models import Binding, Citation, Rule, Span, ValueRange


def test_span_rejects_inverted_bounds():
    with pytest.raises(ValidationError):
        Span(start=100, end=50)


def test_rule_defaults_to_unbound_and_draft():
    r = Rule(tier="graded", kind="threshold", stage="screen")
    assert r.binding.status == "unbound"
    assert r.status == "draft"
    assert r.corroboration == 0
    assert r.rule_key is None


def test_rule_rejects_both_scalar_and_range():
    with pytest.raises(ValidationError):
        Rule(
            tier="graded", kind="range", stage="screen",
            value=40, value_range=ValueRange(min=40, max=50),
        )


def test_binding_never_defaults_to_bound():
    assert Binding().status == "unbound"


# --- Enum closure (final-branch-review.md C1) --------------------------------
# The enum constants were declared and referenced by zero validators, so an
# extractor could emit any string for the two fields that decide how much
# verification a rule gets: `kind` (whether Gate 1's value/direction checks
# and Gate 1b run at all) and `tier` (whether it publishes as a hard
# exclusion). "Out of vocabulary" must be a construction error, not a route
# past the gates.

@pytest.mark.parametrize("field,bad", [
    ("tier", "banana"),
    ("kind", "wat"),
    ("stage", "nope"),
    ("operator", "ne"),
    ("conviction", "vibes"),
    ("status", "shipped"),
])
def test_rule_rejects_out_of_vocabulary_enum(field, bad):
    base = dict(tier="graded", kind="threshold", stage="screen")
    base[field] = bad
    with pytest.raises(ValidationError):
        Rule(**base)


def test_rule_accepts_every_declared_enum_value():
    # The closure must not have narrowed the vocabulary by accident.
    for kind in ("threshold", "range", "boolean"):
        Rule(tier="knockout", kind=kind, stage="exit", conviction="absolute",
             status="active")
    for op in ("gte", "lte", "gt", "lt", "eq"):
        Rule(tier="graded", kind="threshold", stage="screen", operator=op)
    Rule(tier="graded", kind="threshold", stage="screen", operator=None)


def test_citation_rejects_unknown_transcript_fidelity():
    with pytest.raises(ValidationError):
        Citation(lesson_id="1", lesson_url="u", timestamp="00:00:00",
                 span=Span(start=0, end=10), transcript_fidelity="guessed")
