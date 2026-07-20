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
_DIRECTION_PATTERNS: Dict[str, List[re.Pattern]] = {
    op: [re.compile(r"\b" + re.escape(tok) + r"\b") for tok in toks]
    for op, toks in DIRECTION_TOKENS.items()
}


def _direction_present(operator: str, norm: str) -> bool:
    return any(p.search(norm) for p in _DIRECTION_PATTERNS.get(operator, []))


def _value_forms(value: float) -> List[str]:
    """Display form for a number, for rejection-reason messages only.

    Purely cosmetic (renders e.g. "value 18 absent from span" instead of
    "value 18.0 absent from span"). The presence check itself no longer
    searches for a specific surface-form string -- see
    ``_extract_numbers``/``_value_present`` below.
    """
    if float(value).is_integer():
        return [str(int(value))]
    return [str(value)]


# Matches one complete numeric literal as a single unit: an optional
# leading sign, one or more digit groups optionally separated by commas
# (thousand-grouping -- the real corpus routinely writes crore/lakh
# figures this way, e.g. "1,020 crore", "2,428 crores"), and an optional
# decimal tail (e.g. "18.5"). Commas are stripped before ``float()``.
_NUMBER_RE = re.compile(r"-?\d+(?:,\d+)*(?:\.\d+)?")


def _extract_numbers(norm: str) -> List[float]:
    """Every complete numeric literal in ``norm``, parsed to float.

    Structural fix (task-5-review.md round 3) replacing boundary-anchored
    substring search (`(?<![\\d.])<form>(?![\\d.])`) with number
    extraction + float comparison. The substring approach needed one more
    excluded-adjacency character every time a new corpus construction
    surfaced -- an adjacent digit (round 1's "18" vs "118" case), an
    adjacent decimal point (round 2's "18" vs "18.5" case), and now an
    adjacent comma or leading sign (round 3's "18" vs "18,000", and "5"
    vs "-5") -- because *any* punctuation that can legitimately continue
    a digit string into a different/larger/oppositely-signed number was a
    potential bypass, and patching one more character class never closes
    the class, only the specific instance found so far. Extracting whole
    numbers up front and comparing floats closes the whole bug class at
    once: a candidate value either equals one of the numbers actually
    present in the span, or it doesn't, regardless of what punctuation
    surrounds it. Exact float equality is deliberate and sufficient here
    -- these are transcript numbers being matched against a claimed
    citation value, not computed results with rounding error.
    """
    out: List[float] = []
    for m in _NUMBER_RE.finditer(norm):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            continue
    return out


def _value_present(value: float, norm: str) -> bool:
    """Whether ``value`` equals one of the complete numeric literals in ``norm``.

    Shared by both the scalar ``rule.value`` check and the
    ``rule.value_range`` min/max bound checks in ``verify_rule`` below, so
    the number-extraction fix applies identically to both call sites.
    """
    return any(value == n for n in _extract_numbers(norm))


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
            elif rule.operator is None and rule.kind == "range":
                # A range rule has no single directional sense the way
                # lte/gte do -- "between 40 and 50" isn't "more than" or
                # "less than" anything -- so operator=None is the only
                # correct way to construct one: models.OPERATORS has no
                # range/between entry, and the design spec's own `kind:
                # range` worked example
                # (docs/superpowers/specs/2026-07-20-soic-method-spec-design.md:240-244)
                # carries no operator field at all. This is a second
                # deliberate, explicit exemption alongside "eq" above --
                # NOT a general relaxation of the fail-closed else branch
                # below. operator=None on a NON-range rule (a threshold
                # rule with a missing/malformed operator) still falls
                # through to "unhandled" and is rejected, because a
                # threshold rule genuinely needs directional language to
                # verify (task-5-review.md round 3, Round3-Critical-3).
                pass
            elif rule.operator in DIRECTION_TOKENS:
                if not _direction_present(rule.operator, norm):
                    reasons.append(
                        "direction mismatch: no %s token in span" % rule.operator
                    )
            else:
                # Any operator that is neither "eq" nor a DIRECTION_TOKENS
                # key, nor None-on-a-range-rule -- unknown, malformed, or a
                # future addition to Rule.OPERATORS this dict hasn't been
                # taught -- must FAIL CLOSED rather than silently pass with
                # no directional verification. This closes the whole
                # "unhandled case silently falls through" bug class, not
                # just today's "eq" instance.
                reasons.append(
                    "unhandled operator %r: no direction check defined" % rule.operator
                )

    return VerifyResult(ok=not reasons, reasons=reasons)
