"""Loads the machine-readable rule layer (decision-rules-v2.yaml +
metric-registry.yaml) that decision_engine.evaluate() scores against.

Deliberately separate from decision_engine.py: this module only parses
rule DATA and evaluates rule EXPRESSIONS (value in, bool out), with zero
knowledge of Briefing/Decision assembly -- the same single-responsibility
split as framework_router.py (parse frameworks) vs decision_engine.py
(assemble). See docs/superpowers/plans/2026-07-27-soic-decision-engine-
machine-actionable-plan.md section 1/2.1 for the full design.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union

import yaml


@dataclass
class Signal:
    name: str
    metric: str
    rule: str
    weight: float


@dataclass
class RuleEntry:
    id: str
    status: str  # machine | advisory-only | advisory-numeric | deprecated
    cls: str  # safety_gate | valuation | quality | timing | routing
    signals: List[Signal] = field(default_factory=list)


@dataclass
class MetricInfo:
    label: str
    status: str  # fetchable | not_yet_fetchable


_RULE_RE = re.compile(r"^(<=|>=|<|>)\s*(-?\d+(?:\.\d+)?)$")
_BETWEEN_RE = re.compile(r"^between\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)$")


def check_rule(value: float, rule: str) -> bool:
    """Evaluate a threshold/band rule string against a live value.

    Supports the two shapes decision-rules-v2.yaml uses: "<= 90" / ">= 20"
    / "< 5" / "> 5", and "between A B" (inclusive both ends). Raises
    ValueError on any other shape -- an unparseable rule must fail loudly,
    never silently pass or fail.
    """
    stripped = rule.strip()

    m = _BETWEEN_RE.match(stripped)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        return lo <= value <= hi

    m = _RULE_RE.match(stripped)
    if m:
        op, num = m.group(1), float(m.group(2))
        if op == "<=":
            return value <= num
        if op == ">=":
            return value >= num
        if op == "<":
            return value < num
        return value > num

    raise ValueError(f"Unrecognized rule expression: {rule!r}")


def load_decision_rules(path: Union[str, Path]) -> List[RuleEntry]:
    """Parse decision-rules-v2.yaml (a YAML list, one entry per framework)
    into RuleEntry objects."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    rules = []
    for entry in data:
        signals = [
            Signal(
                name=s["name"],
                metric=s["metric"],
                rule=s["rule"],
                weight=float(s.get("weight", 1.0)),
            )
            for s in entry.get("signals", [])
        ]
        rules.append(
            RuleEntry(
                id=entry["id"],
                status=entry.get("status", "machine"),
                cls=entry.get("class", "valuation"),
                signals=signals,
            )
        )
    return rules


def load_metric_registry(path: Union[str, Path]) -> Dict[str, MetricInfo]:
    """Parse metric-registry.yaml's `metrics:` mapping into MetricInfo,
    keyed by metric key."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    registry = {}
    for key, entry in data.get("metrics", {}).items():
        registry[key] = MetricInfo(
            label=entry["label"], status=entry.get("status", "fetchable")
        )
    return registry
