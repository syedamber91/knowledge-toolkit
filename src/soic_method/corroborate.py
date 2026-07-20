"""Gate 1b — numeric corroboration across independent ASR streams.

Gate 1 (verify.py) checks that a citation is real and literally consistent
with the rule. It does NOT catch a confidently-wrong number: ASR routinely
corrupts digits ("499% pad growth" is almost certainly a mangled figure) and
proper nouns ("Syngenta" -> "Sinjenta") within a single rendering of the
audio, and both a proposer and Gate 1 read the same corrupted text -- there
is nothing internally inconsistent about a wrong number stated confidently.

The only defence is a second, INDEPENDENT rendering of the same underlying
audio: a different lesson that states the same value, or the same lesson's
``ai_summary`` (generated from the audio by a separate process from the
transcript). A threshold attested in only one stream is downgraded to
``needs_audio_check`` -- a human ear-verification queue -- rather than
shipped as ``active`` truth.

Matching mechanism: this module reuses ``verify._extract_numbers`` rather
than re-implementing surface-form/substring matching. Task 5's Gate 1
verifier went through six rounds of adversarial, corpus-proven review before
converging on ``_extract_numbers`` -- naive substring matching lets a short
value like "8" match inside "18%" (false positive), and naive
``\\b``-boundary matching is defeated by decimal points ("18" matching
inside "18.5") and by comma-grouped numbers ("18" vs "18,000"). Both
failure directions matter here exactly as they did for Gate 1: a false
positive would let a single corrupted stream masquerade as two independent
attestations (defeating the whole point of this gate), and a false negative
would downgrade genuinely double-attested thresholds to
``needs_audio_check`` for no reason. Re-deriving a second, simpler matcher
here would silently re-open the same bug class Task 5 spent six rounds
closing, for the exact same kind of check (does numeric value X literally
appear in text Y), so it is imported instead.
"""

from __future__ import annotations

from typing import Dict, List

from .corpus import normalize_slice
from .models import LessonRecord, Rule
from .verify import _extract_numbers

MIN_CORROBORATION = 2


def _attested_in(text: str, values: List[float]) -> bool:
    """Whether every value in ``values`` is present as a real numeric
    literal in ``text``.

    ``text`` is normalized once and every literal number in it is extracted
    once via ``_extract_numbers`` (Task 5's hardened digit/comma/decimal/
    spelled-number extractor); each claimed value is then compared against
    that set by exact float equality -- the same semantics Gate 1 uses for
    its own value-presence check (``verify._value_present``), just applied
    to a whole lesson stream instead of one cited span.
    """
    present = _extract_numbers(normalize_slice(text))
    return all(v in present for v in values)


def _rule_values(rule: Rule) -> List[float]:
    if rule.value is not None:
        return [rule.value]
    if rule.value_range is not None:
        return [rule.value_range.min, rule.value_range.max]
    return []


def corroborate(rule: Rule, lessons: Dict[str, LessonRecord]) -> Rule:
    """Return a copy of ``rule`` with ``corroboration`` and ``status`` set.

    Non-numeric (``boolean``) rules carry nothing for ASR to corrupt
    numerically, so they are exempted from this gate entirely and promoted
    straight to ``active`` (Gate 1 has already verified the citation is
    real and the span supports the claim).

    For numeric rules (``threshold``/``range``), each cited lesson counts
    as at most one independent stream via its ``body_text`` and up to one
    more via its ``ai_summary`` (a separately-generated rendering of the
    same audio) -- so a single lesson can supply at most 2 streams, and two
    different lessons citing the same value also reach the threshold. A
    lesson id is only ever counted once even if cited multiple times.
    """
    values = _rule_values(rule)
    if not values:
        return rule.model_copy(update={"corroboration": len(rule.citations),
                                       "status": "active"})

    streams = 0
    seen_lessons = set()
    for cit in rule.citations:
        lesson = lessons.get(cit.lesson_id)
        if lesson is None or lesson.lesson_id in seen_lessons:
            continue
        seen_lessons.add(lesson.lesson_id)
        if _attested_in(lesson.body_text, values):
            streams += 1
        if lesson.ai_summary and _attested_in(lesson.ai_summary, values):
            streams += 1

    status = "active" if streams >= MIN_CORROBORATION else "needs_audio_check"
    return rule.model_copy(update={"corroboration": streams, "status": status})
