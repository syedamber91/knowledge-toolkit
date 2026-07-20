"""Gate 1 — deterministic verification. No LLM.

What this gate DOES: makes fabricated citations impossible (offsets are sliced
from the corpus, never copied), and converts the two most damaging silent
errors — wrong value and inverted operator — into rejections.

What it does NOT do: prevent misattributed MEANING. Quote-mining, negation,
reported speech and hypotheticals all survive this gate by design; catching
them is the refuter's job.
"""

from __future__ import annotations

from typing import Dict, List

from .corpus import normalize_slice
from .models import LessonRecord, Rule, VerifyResult

MIN_SPAN_CHARS = 40

DIRECTION_TOKENS: Dict[str, List[str]] = {
    "lte": ["less than", "below", "under", "at most", "no more than",
            "not more than", "maximum", "max", "cheaper than", "within"],
    "gte": ["more than", "above", "over", "at least", "minimum", "min",
            "greater than", "north of", "upwards of", "in excess of"],
}
DIRECTION_TOKENS["lt"] = DIRECTION_TOKENS["lte"]
DIRECTION_TOKENS["gt"] = DIRECTION_TOKENS["gte"]


def _value_forms(value: float) -> List[str]:
    """Surface forms a number may take in a transcript."""
    forms = []
    if float(value).is_integer():
        forms.append(str(int(value)))
    forms.append(str(value))
    return forms


def verify_rule(rule: Rule, lessons: Dict[str, LessonRecord]) -> VerifyResult:
    reasons: List[str] = []

    if not rule.citations:
        return VerifyResult(ok=False, reasons=["no citations"])

    for cit in rule.citations:
        lesson = lessons.get(cit.lesson_id)
        if lesson is None:
            reasons.append("unknown lesson %s" % cit.lesson_id)
            continue

        # 6. corpus snapshot integrity — checked first; everything else is
        # meaningless against drifted text.
        if cit.text_hash and lesson.text_hash and cit.text_hash != lesson.text_hash:
            reasons.append("corpus hash mismatch for lesson %s" % cit.lesson_id)
            continue

        # 5. eligibility (defence in depth — the router already skipped these)
        if not lesson.eligible:
            reasons.append("ineligible lesson %s" % cit.lesson_id)
            continue

        # 1. offsets in range
        if cit.span.end > len(lesson.body_text):
            reasons.append("span out of range for lesson %s" % cit.lesson_id)
            continue

        raw = lesson.body_text[cit.span.start:cit.span.end]
        norm = normalize_slice(raw)

        # 2. minimum length — without this a fragment like "18%" matches
        # trivially somewhere in a 300KB transcript.
        if len(norm) < MIN_SPAN_CHARS:
            reasons.append("span too short (%d chars)" % len(norm))
            continue

        # 3. the claimed value must appear in the span
        if rule.value is not None:
            if not any(f in norm for f in _value_forms(rule.value)):
                reasons.append("value %s absent from span" % _value_forms(rule.value)[0])
        if rule.value_range is not None:
            for bound in (rule.value_range.min, rule.value_range.max):
                if not any(f in norm for f in _value_forms(bound)):
                    reasons.append("range bound %s absent from span" % _value_forms(bound)[0])

        # 4. comparative direction must match the operator
        if rule.operator in DIRECTION_TOKENS:
            if not any(tok in norm for tok in DIRECTION_TOKENS[rule.operator]):
                reasons.append(
                    "direction mismatch: no %s token in span" % rule.operator
                )

    return VerifyResult(ok=not reasons, reasons=reasons)
