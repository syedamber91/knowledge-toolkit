"""Gate 2 — adversarial refutation.

ONE refuter, well fed. Three same-model refuters are correlated rather than
independent, so a majority vote largely measures sampling temperature; the
budget is better spent on context, which is what makes quote-mining visible.

Fails CLOSED: any malformed response, missing lesson or ambiguity refutes.
"""

from __future__ import annotations

import json
from typing import Callable, Dict, List

from .models import LessonRecord, Rule

CONTEXT_CHARS = 1500

FAILURE_MODES: List[str] = [
    "negation or retraction — the speaker states the rule only to reject it",
    "reported speech — the speaker describes what OTHER people do or believe",
    "hypothetical or arithmetic illustration rather than a stated rule",
    "company-specific aside being generalised into a universal rule",
    "a read-aloud member question rather than the instructor's own view",
    "the value or comparative direction is not actually supported by context",
    "incoherence — the span is too ASR-garbled to support any rule at all",
]

PROMPT_TEMPLATE = """You are trying to REFUTE a proposed investing rule.

PROPOSED RULE:
{rule}

THE SPAN IT CLAIMS AS EVIDENCE:
{span}

SURROUNDING TRANSCRIPT (the span is inside this):
{context}

Argue against the rule. Check each failure mode:
{modes}

Note the transcript is auto-generated and degraded: numbers, company names and
whole sentences are sometimes corrupted. If the span is too garbled to clearly
support the rule, refute it.

Default to refuted when uncertain.

Return JSON only: {{"refuted": true|false, "reason": "<short>"}}
"""


def build_refute_prompt(rule: Rule, lesson: LessonRecord) -> str:
    cit = rule.citations[0]
    span = lesson.body_text[cit.span.start:cit.span.end]
    lo = max(0, cit.span.start - CONTEXT_CHARS)
    hi = min(len(lesson.body_text), cit.span.end + CONTEXT_CHARS)
    summary = rule.model_dump(include={"tier", "kind", "stage", "operator",
                                       "value", "value_range", "unit",
                                       "conviction"})
    return PROMPT_TEMPLATE.format(
        rule=json.dumps(summary, default=str),
        span=span,
        context=lesson.body_text[lo:hi],
        modes="\n".join("- " + m for m in FAILURE_MODES),
    )


def refute(
    rule: Rule,
    lessons: Dict[str, LessonRecord],
    llm: Callable[[str], str],
) -> bool:
    """Return True if the rule SURVIVES refutation."""
    if not rule.citations:
        return False
    lesson = lessons.get(rule.citations[0].lesson_id)
    if lesson is None:
        return False
    try:
        payload = json.loads(llm(build_refute_prompt(rule, lesson)))
    except (ValueError, TypeError):
        return False           # fail closed
    if not isinstance(payload, dict) or "refuted" not in payload:
        return False           # fail closed
    refuted = payload.get("refuted")
    if not isinstance(refuted, bool):
        return False           # fail closed: ambiguous non-boolean response
    return refuted is False
