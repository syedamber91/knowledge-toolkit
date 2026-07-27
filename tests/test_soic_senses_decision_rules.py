from pathlib import Path

import pytest

RULES_FIXTURE = Path(__file__).parent / "fixtures" / "decision_rules_sample.yaml"
REGISTRY_FIXTURE = Path(__file__).parent / "fixtures" / "metric_registry_sample.yaml"


def test_check_rule_supports_less_or_equal():
    from soic_senses.decision_rules import check_rule

    assert check_rule(90.0, "<= 90") is True
    assert check_rule(90.1, "<= 90") is False


def test_check_rule_supports_greater_or_equal():
    from soic_senses.decision_rules import check_rule

    assert check_rule(20.0, ">= 20") is True
    assert check_rule(19.9, ">= 20") is False


def test_check_rule_supports_between_inclusive():
    from soic_senses.decision_rules import check_rule

    assert check_rule(15.0, "between 15 35") is True
    assert check_rule(35.0, "between 15 35") is True
    assert check_rule(14.9, "between 15 35") is False


def test_check_rule_raises_on_unrecognized_expression():
    from soic_senses.decision_rules import check_rule

    with pytest.raises(ValueError):
        check_rule(1.0, "n/a")


def test_load_decision_rules_parses_every_entry():
    from soic_senses.decision_rules import load_decision_rules

    rules = load_decision_rules(RULES_FIXTURE)

    assert [r.id for r in rules] == ["F1", "F2", "F3", "F10"]
    f1 = rules[0]
    assert f1.cls == "safety_gate"
    assert f1.signals[0].metric == "wc_days"
    assert f1.signals[0].rule == "<= 90"
    assert f1.signals[0].weight == 1.0


def test_load_metric_registry_parses_every_entry():
    from soic_senses.decision_rules import load_metric_registry

    registry = load_metric_registry(REGISTRY_FIXTURE)

    assert registry["stock_pe"].label == "Stock P/E"
    assert registry["stock_pe"].status == "fetchable"
