"""Gate 1 — deterministic verification. No LLM.

What this gate DOES: makes fabricated citations impossible (offsets are sliced
from the corpus, never copied), and converts the two most damaging silent
errors — wrong value and inverted operator — into rejections.

What it does NOT do: prevent misattributed MEANING. Quote-mining, negation,
reported speech and hypotheticals all survive this gate by design; catching
them is the refuter's job.
"""

from __future__ import annotations

import re
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

# Word-boundary regex per direction token, precompiled once — mirrors
# router.py's `_METRIC_PATTERNS` fix (83d92d0). Short tokens like "min" are
# real comparative language ("minimum") but also common substrings of
# unrelated words ("eliminate"); \b confines a match to the token appearing
# as its own word/phrase, not embedded inside a longer token.
# DIRECTION_TOKENS itself is untouched; only the matching mechanism changed.
_DIRECTION_PATTERNS: Dict[str, List["re.Pattern"]] = {
    op: [re.compile(r"\b" + re.escape(tok) + r"\b") for tok in toks]
    for op, toks in DIRECTION_TOKENS.items()
}


def _direction_present(operator: str, norm: str) -> bool:
    return any(p.search(norm) for p in _DIRECTION_PATTERNS.get(operator, []))


def _value_forms(value: float) -> List[str]:
    """Surface forms a number may take in a transcript."""
    forms = []
    if float(value).is_integer():
        forms.append(str(int(value)))
    forms.append(str(value))
    return forms


def _value_present(value: float, norm: str) -> bool:
    """Whether any surface form of ``value`` appears as its own token.

    Boundary excludes adjacent digits AND decimal points on both sides
    (task-5-review.md New-Critical-2, second round). A plain `\\b`
    boundary treats "." as a valid boundary character (it is non-`\\w`),
    so a claimed integer value that is a true digit-*prefix* of a real
    decimal number in the span -- e.g. claimed 18 against a real span
    saying "18.5 times earnings" -- would still match `\\b18\\b` (the
    transition from "8" to "." is a `\\w`-to-non-`\\w` boundary). Using
    `(?<![\\d.])`/`(?![\\d.])` instead rejects a digit *or* a decimal
    point immediately adjacent, so "18" embedded in "18.5" or "118" is
    correctly excluded, while a genuine standalone "18" -- including
    followed by "%" or a space -- still matches. This is deliberately
    NOT applied to `_direction_present`'s word-token matching above,
    which is about words, not numbers, and isn't affected by this
    decimal-adjacency issue.
    """
    return any(
        re.search(r"(?<![\d.])" + re.escape(form) + r"(?![\d.])", norm)
        for form in _value_forms(value)
    )


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
        # meaningless against drifted text. Fail CLOSED: a missing hash on
        # either side is treated as a mismatch, not skipped — an empty
        # text_hash proves nothing about drift, so it cannot be trusted to
        # pass this check.
        if not cit.text_hash or not lesson.text_hash or cit.text_hash != lesson.text_hash:
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

        # 3/4. value + direction checks — exempted ONLY for kind == "boolean"
        # (a boolean rule carries no numeric claim to verify). This is an
        # explicit kind check, not inferred from value/operator being absent,
        # so a malformed non-boolean rule missing its value is caught below
        # rather than silently treated as "not applicable".
        if rule.kind != "boolean":
            # 3. the claimed value must appear in the span
            if rule.value is not None:
                if not _value_present(rule.value, norm):
                    reasons.append("value %s absent from span" % _value_forms(rule.value)[0])
            elif rule.value_range is not None:
                for bound in (rule.value_range.min, rule.value_range.max):
                    if not _value_present(bound, norm):
                        reasons.append("range bound %s absent from span" % _value_forms(bound)[0])
            else:
                reasons.append(
                    "malformed rule: kind %r has neither value nor value_range" % rule.kind
                )

            # 4. comparative direction must match the operator. Explicit
            # allow-list decision (task-5-review.md New-Critical-1), not
            # implicit dict-membership fallthrough: the old
            # `if rule.operator in DIRECTION_TOKENS:` silently skipped this
            # entire check -- no reason emitted either way -- for any
            # operator the dict didn't cover, and "eq" (a first-class,
            # model-valid value in `models.OPERATORS`) was exactly such an
            # operator, so every eq-operator rule got zero directional
            # verification for free.
            if rule.operator == "eq":
                # Equality has no natural "wrong direction" the way
                # lte/gte do -- a wrong eq value is just a wrong value,
                # already caught by the value-presence check above. This
                # is a deliberate, explicit exemption, NOT a fallthrough:
                # it exists because we decided eq needs no directional
                # language, not because "eq" happens to be absent from
                # DIRECTION_TOKENS.
                pass
            elif rule.operator in DIRECTION_TOKENS:
                if not _direction_present(rule.operator, norm):
                    reasons.append(
                        "direction mismatch: no %s token in span" % rule.operator
                    )
            else:
                # Any operator that is neither "eq" nor a DIRECTION_TOKENS
                # key -- unknown, malformed, or a future addition to
                # Rule.OPERATORS this dict hasn't been taught -- must FAIL
                # CLOSED rather than silently pass with no directional
                # verification. This closes the whole "unhandled case
                # silently falls through" bug class, not just today's "eq"
                # instance.
                reasons.append(
                    "unhandled operator %r: no direction check defined" % rule.operator
                )

    return VerifyResult(ok=not reasons, reasons=reasons)
