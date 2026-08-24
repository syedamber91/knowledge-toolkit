"""Which rules dropped the condition their source attached to them?

The whole point of this stage. A rule binds to the threshold claim whose
metric and bound it encodes. If that threshold has a `scopes` edge from a
condition the rule does not carry, the rule is applying a number outside the
range its source gave it.

This reports; it never edits a rulebook. Every finding carries the citation so
a human can read the source and decide.

A rule's own `requires_attribute` narrowing is surfaced alongside a finding,
never used to suppress one -- `requires_attribute` narrows by a resolvable
attribute (e.g. is_lender), and a scope claim can name a wholly unrelated
condition (e.g. a turnaround) that the same rule never carries. Deciding
whether the two overlap would mean fuzzy-matching a free-text statement
against an attribute key, which this detector deliberately does not attempt.
Put the two facts side by side; the judgement is the reader's.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel

from .claims import Claim


class RuleBinding(BaseModel):
    rule_id: str
    metric: str
    bound: str
    claim_id: str


class Finding(BaseModel):
    rule_id: str
    threshold_claim_id: str
    scope_claim_id: str
    scope_statement: str
    ref: str
    ts: str
    rule_requires_attribute: Dict[str, str] = {}


def _norm_bound(bound: str) -> str:
    return "".join((bound or "").split())


def _rule_entries(rulebook_path: Path) -> List[Dict]:
    doc = yaml.safe_load(Path(rulebook_path).read_text("utf-8")) or {}
    out: List[Dict] = []
    for section in ("rules", "observations"):
        for entry in doc.get(section) or []:
            out.append(entry)
    return out


def bind_rules(rulebook_path: Path, claims: List[Claim]) -> List[RuleBinding]:
    """A rule binds to the threshold claim carrying the same metric and bound."""
    thresholds = [c for c in claims if c.kind == "threshold"]
    bindings: List[RuleBinding] = []
    for entry in _rule_entries(rulebook_path):
        metric = entry.get("metric")
        bound = entry.get("check_rule") or entry.get("reference_band")
        if not metric or not bound:
            continue
        for claim in thresholds:
            if (claim.metric == metric
                    and _norm_bound(claim.bound) == _norm_bound(bound)):
                bindings.append(RuleBinding(
                    rule_id=entry["id"], metric=metric, bound=bound,
                    claim_id=claim.claim_id))
                break
    return bindings


def find_lost_conditions(rulebook_path: Path,
                         claims: List[Claim]) -> List[Finding]:
    by_id = {c.claim_id: c for c in claims}
    scopes_for: Dict[str, List[Claim]] = {}
    for claim in claims:
        if claim.kind == "scope":
            for governed in claim.scopes:
                scopes_for.setdefault(governed, []).append(claim)

    entries = {e["id"]: e for e in _rule_entries(rulebook_path)}
    findings: List[Finding] = []
    for binding in bind_rules(rulebook_path, claims):
        entry = entries.get(binding.rule_id, {})
        # Report every bound threshold that has a governing scope. What the
        # rule already narrows by (requires_attribute) is surfaced on the
        # finding, never used to suppress it -- see module docstring.
        rule_requires_attribute = entry.get("requires_attribute") or {}
        for scope in scopes_for.get(binding.claim_id, []):
            findings.append(Finding(
                rule_id=binding.rule_id,
                threshold_claim_id=binding.claim_id,
                scope_claim_id=scope.claim_id,
                scope_statement=scope.statement,
                ref=scope.ref, ts=scope.ts,
                rule_requires_attribute=rule_requires_attribute))
    return findings
