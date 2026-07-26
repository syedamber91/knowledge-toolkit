"""Deterministic candidate routing. No LLM.

The signal lexicon MUST carry ASR variants. Measured in the corpus on
2026-07-20: ``ROCE`` 54x vs ``ROC`` 961x; ``PAT growth`` 74x vs ``pad growth``
363x. A naive lexicon misses the overwhelming majority of the material.
"""

from __future__ import annotations

import re
from typing import Dict, List

from .models import Candidate, LessonRecord, Span

# Canonical metric -> surface forms actually present in the ASR.
SIGNAL_TERMS: Dict[str, List[str]] = {
    "roc": ["roce", "roc", "return on capital"],
    "pat": ["pat growth", "pad growth", "profit after tax", "net profit"],
    "pe": ["p/e", "pe ratio", "p e ratio", "price to earnings", "times earnings"],
    "sales": ["sales growth", "revenue growth", "topline"],
    "margin": ["operating margin", "opm", "ebitda margin", "gross margin"],
    "debt": ["debt to equity", "d/e", "debt equity", "leverage"],
    "pledge": ["pledge", "pledged"],
}

_COMPARATIVE = re.compile(
    r"\b(less than|below|under|at most|no more than|not more than|maximum|max|"
    r"more than|above|over|at least|minimum|min|greater than|north of)\b",
    re.I,
)
_NUMBER = re.compile(r"\d")

# Word-boundary regex per surface form, precompiled once. Short ASR-variant
# forms like "roc" or "min" are real corpus signal but also common substrings
# of unrelated words ("ferocious", "Rochit") — \b confines a match to the
# form appearing as its own word/phrase, not embedded inside a longer token.
# SIGNAL_TERMS itself is untouched; only the matching mechanism changed.
_METRIC_PATTERNS: Dict[str, List["re.Pattern"]] = {
    canon: [re.compile(r"\b" + re.escape(form) + r"\b") for form in forms]
    for canon, forms in SIGNAL_TERMS.items()
}


def _metric_hits(text_lower: str) -> List[str]:
    return [
        canon
        for canon, patterns in _METRIC_PATTERNS.items()
        if any(p.search(text_lower) for p in patterns)
    ]


def find_candidates(lesson: LessonRecord, window: int = 400) -> List[Candidate]:
    """Flag spans carrying BOTH a metric term AND a comparative-with-number."""
    body = lesson.body_text
    out: List[Candidate] = []
    for m in _COMPARATIVE.finditer(body):
        start = max(0, m.start() - window)
        end = min(len(body), m.end() + window)
        chunk = body[start:end]
        if not _NUMBER.search(chunk):
            continue
        signals = _metric_hits(chunk.lower())
        if not signals:
            continue
        out.append(Candidate(lesson_id=lesson.lesson_id,
                             span=Span(start=start, end=end),
                             signals=signals))
    return _merge_overlaps(out)


def _merge_overlaps(cands: List[Candidate]) -> List[Candidate]:
    if not cands:
        return []
    merged = [cands[0]]
    for c in cands[1:]:
        last = merged[-1]
        if c.span.start <= last.span.end:
            merged[-1] = Candidate(
                lesson_id=last.lesson_id,
                span=Span(start=last.span.start, end=max(last.span.end, c.span.end)),
                signals=sorted(set(last.signals) | set(c.signals)),
            )
        else:
            merged.append(c)
    return merged


def route(lessons: List[LessonRecord], window: int = 400) -> List[Candidate]:
    out: List[Candidate] = []
    for lesson in lessons:
        if not lesson.eligible:
            continue
        out.extend(find_candidates(lesson, window=window))
    return out
