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

import re
from typing import Dict, List, Optional, Pattern

from .corpus import normalize_slice
from .models import LessonRecord, Rule
from .router import _METRIC_PATTERNS
from .verify import _extract_numbers

MIN_CORROBORATION = 2

# Half-width of the attesting window, in normalized characters, either side
# of the metric term. ~300 chars is roughly a spoken paragraph in this ASR
# (the transcripts run ~1,000 chars per timestamped minute), so it is wide
# enough to hold "we want ROC ... of at least fifteen percent" split across
# a garbled clause, and narrow enough that an unrelated number elsewhere in
# the same 100KB lesson cannot reach it. See the measurement note below.
ATTEST_WINDOW_CHARS = 300

_ALL_METRIC_PATTERNS: List[Pattern] = [
    p for pats in _METRIC_PATTERNS.values() for p in pats
]

# rule_key is dotted+underscored ("screen.pat_growth.floor"); split it into
# bare tokens so the canonical metric name inside it ("pat") can be matched
# against router.SIGNAL_TERMS' keys.
_KEY_TOKENS = re.compile(r"[^a-z0-9]+")


def metric_patterns_for(rule: Rule) -> List[Pattern]:
    """The metric vocabulary an attesting occurrence must sit next to.

    Deliberately reuses ``router.SIGNAL_TERMS`` via its precompiled
    ``_METRIC_PATTERNS`` rather than introducing a second, drifting metric
    lexicon: the router's forms are the ones measured against this corpus's
    ASR (``ROC`` 961x, ``pad growth`` 363x), and a rule that was routed by
    one vocabulary should be corroborated against the same one.

    When the rule names a metric its ``rule_key`` recognises, only that
    metric's surface forms count -- a "15" next to a P/E discussion does not
    attest a ROC floor. When the key names no known metric (or the rule is
    still unnamed), any metric term counts: the window bound alone is still
    a large improvement over the whole-body scan, and failing closed here
    would silently downgrade every draft rule.
    """
    tokens = set(_KEY_TOKENS.split((rule.rule_key or "").casefold()))
    for canon, patterns in _METRIC_PATTERNS.items():
        if canon in tokens:
            return patterns
    return _ALL_METRIC_PATTERNS


def _attested_in(
    text: str,
    values: List[float],
    patterns: Optional[List[Pattern]] = None,
) -> bool:
    """Whether ``values`` are attested by a CONTEXTUALLY RELEVANT occurrence.

    An attesting occurrence must satisfy two conditions at once, inside a
    single +/-``ATTEST_WINDOW_CHARS`` window: every claimed value appears as
    a real numeric literal, AND the window also contains a metric term the
    rule is about.

    Mere presence anywhere in the lesson is not evidence. Measured on the
    pilot's own transcripts, 52-56 of the integers 1..100 appear SOMEWHERE
    in each ~100KB lesson body, so the unbounded scan this replaced promoted
    41/100 arbitrary values to ``status="active"`` on two citations --
    i.e. Gate 1b, the only defence the design has against a corrupted digit,
    was close to a coin flip (final-branch-review.md C2). The window makes
    the check ask the question it was always meant to ask: does a second
    rendering of the audio state this number *about this metric*.

    The numeric comparison itself is still ``verify._extract_numbers`` +
    float equality, applied per window instead of per whole body. That
    matcher converged over six adversarial rounds against real corpus
    constructions (digit substrings, decimal prefixes, comma grouping,
    dash-ranges vs negative signs); regressing to substring matching here
    would re-open the whole class. Only the SCOPE of the text it reads has
    changed, not how it reads it.

    Requiring all of a range's bounds inside ONE window (rather than
    anywhere in the stream) is deliberate: "between 15 and 30 times
    earnings" is a single utterance, and a lesson that says "15" in one
    place and "30" in another has not attested the band.
    """
    if not values:
        return False
    norm = normalize_slice(text)
    for pattern in (patterns if patterns is not None else _ALL_METRIC_PATTERNS):
        for m in pattern.finditer(norm):
            lo = max(0, m.start() - ATTEST_WINDOW_CHARS)
            hi = min(len(norm), m.end() + ATTEST_WINDOW_CHARS)
            present = _extract_numbers(norm[lo:hi])
            if all(v in present for v in values):
                return True
    return False


def rule_values(rule: Rule) -> List[float]:
    """The values a rule asserts. ONE definition, shared with reconcile.

    Three separate invariants key on this: Gate 1b's attestation set
    (below), Gate 3's merged/variants/conflict decision, and
    ``reconcile.resolution_key`` -- the content-stable join key that must
    never drift, or accumulated human resolutions are silently orphaned.
    Two byte-identical copies could diverge and make a group corroborate
    under one definition while conflicting under the other, so reconcile
    imports this one (final-branch-review.md I5).
    """
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
    values = rule_values(rule)
    if not values:
        return rule.model_copy(update={"corroboration": len(rule.citations),
                                       "status": "active"})

    patterns = metric_patterns_for(rule)
    streams = 0
    seen_lessons = set()
    for cit in rule.citations:
        lesson = lessons.get(cit.lesson_id)
        if lesson is None or lesson.lesson_id in seen_lessons:
            continue
        seen_lessons.add(lesson.lesson_id)
        if _attested_in(lesson.body_text, values, patterns):
            streams += 1
        if lesson.ai_summary and _attested_in(lesson.ai_summary, values, patterns):
            streams += 1

    status = "active" if streams >= MIN_CORROBORATION else "needs_audio_check"
    return rule.model_copy(update={"corroboration": streams, "status": status})
