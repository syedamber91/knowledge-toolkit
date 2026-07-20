import pytest
from pydantic import ValidationError

from soic_method.models import Binding, Rule, Span, ValueRange


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
