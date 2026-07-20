"""Gate 3 — grouping, scope attestation, conflict detection, merge.

CONFLICT IS THE DEFAULT. A scoped-variant classification requires the scope
distinction to carry its own attesting span that passes the same verifier. The
earlier design made "variant" the free outcome and "conflict" the expensive
one, which biased an LLM toward always finding a distinguishing context and
laundering real contradictions into two happily-active rules.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .corroborate import corroborate
from .models import LessonRecord, Rule
from .verify import verify_rule


class ReconcileOutput(BaseModel):
    rules: List[Rule] = Field(default_factory=list)
    drafts: List[Rule] = Field(default_factory=list)
    conflicts: List[List[Rule]] = Field(default_factory=list)


def _values_of(rule: Rule) -> List[float]:
    if rule.value is not None:
        return [rule.value]
    if rule.value_range is not None:
        return [rule.value_range.min, rule.value_range.max]
    return []


def resolution_key(rule: Rule) -> str:
    """Content-stable join key: (rule_key, sorted value set).

    Deliberately independent of quotes, spans and generated ids so a re-run
    that shifts offsets does not silently orphan a human resolution.
    """
    vals = ",".join(str(v) for v in sorted(_values_of(rule)))
    return "%s|%s" % (rule.rule_key, vals)


def merge_agreeing(rules: List[Rule], lessons: Dict[str, LessonRecord]) -> Rule:
    """One rule, many citations, re-corroborated (not re-counted) after merge.

    corroboration has exactly one definition: Task 6's corroborate(), which
    counts independent ATTESTING STREAMS (body_text and ai_summary count
    separately). Recomputing it here as len(distinct lesson_ids) would
    silently disagree with that definition and would DOWNGRADE a rule Task 6
    already correctly rated 2/active (one lesson + its own corroborating
    ai_summary) down to 1 -- the digit-error defence failing open at the
    moment two agreeing extractions combine. So merge only merges citations;
    corroborate() re-derives the count and status from the merged result.
    """
    base = rules[0]
    cits = list(base.citations)
    for r in rules[1:]:
        cits.extend(r.citations)
    merged = base.model_copy(update={"citations": cits})
    return corroborate(merged, lessons)


def _scope_is_attested(rule: Rule, lessons: Dict[str, LessonRecord]) -> bool:
    """Whether the rule's scope claim carries its own real, eligible span.

    The probe deliberately sets ``kind="boolean"`` alongside clearing
    value/value_range/operator: verify_rule's checks 3/4 (value-presence,
    comparative-direction) are about the rule's NUMERIC claim, which is not
    what this span is attesting -- the scope span supports a qualitative
    distinction ("capital light businesses"), not the ROC number itself.
    Leaving kind at its original "threshold"/"range" value here made
    verify_rule fall into its own "malformed rule: kind has neither value
    nor value_range" branch (value/value_range are None on the probe) and
    reject every attestation outright, which would make classify_group
    always return "conflict" -- kind="boolean" routes the probe through
    verify_rule's own explicit boolean exemption instead, so only the
    checks that actually apply to a scope span (real span, in range,
    minimum length, eligible lesson, matching corpus hash) run.
    """
    att = rule.scope_attestation
    if att is None or not rule.scope or not rule.citations:
        return False
    probe = rule.model_copy(update={
        "citations": [rule.citations[0].model_copy(update={"span": att.span})],
        "value": None, "value_range": None, "operator": None, "kind": "boolean",
    })
    return verify_rule(probe, lessons).ok


def classify_group(
    rules: List[Rule], lessons: Dict[str, LessonRecord]
) -> Tuple[str, List[Rule]]:
    distinct = {tuple(sorted(_values_of(r))) for r in rules}
    if len(distinct) <= 1:
        return "merged", [merge_agreeing(rules, lessons)]
    if all(_scope_is_attested(r, lessons) for r in rules):
        return "variants", rules
    return "conflict", rules


def reconcile(
    rules: List[Rule],
    lessons: Dict[str, LessonRecord],
    resolutions: Dict[str, dict],
) -> ReconcileOutput:
    out = ReconcileOutput()
    groups: Dict[str, List[Rule]] = defaultdict(list)

    for r in rules:
        if r.rule_key is None:
            out.drafts.append(r)      # unnamed rules never group
        else:
            groups[r.rule_key].append(r)

    for _key, group in sorted(groups.items()):
        verdict, result = classify_group(group, lessons)
        if verdict != "conflict":
            out.rules.extend(result)
            continue

        resolved = _apply_resolution(group, resolutions)
        if resolved is not None:
            out.rules.append(resolved)
        else:
            out.conflicts.append(group)
    return out


def _apply_resolution(
    group: List[Rule], resolutions: Dict[str, dict]
) -> Optional[Rule]:
    for r in group:
        entry = resolutions.get(resolution_key(r))
        if entry and entry.get("keep") in _values_of(r):
            return r
    return None
