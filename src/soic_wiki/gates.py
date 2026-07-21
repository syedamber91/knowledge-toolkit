"""Frequency-based artifact detection. No LLM.

WHY FREQUENCY AND NOT PRESENCE
------------------------------
The obvious gate — "does this phrase appear verbatim in a transcript?" — is
worse than useless on this corpus, because the transcripts are auto-generated
and the summaries that fed the old wiki are model-generated. Measured:

    Mauboussin              0 occurrences   (TRUE: he does cite the book)
    "measuring the mode"    5 occurrences   (the ASR mangling of it)
    "diamond of profit pools"  1 occurrence (FALSE: a summarizer artifact)

A presence gate REJECTS the true claim and PASSES the false one. The previous
session hardened a presence-based verifier through six adversarial review
rounds; it could not have caught the failure that actually happened.

What separates them is distribution, not existence:

    term                      body   lessons   summary
    value chain               1198     125       384
    right to win                37      15         3
    purple patch                38       9         4
    diamond of profit pools      1       1         1   <- artifact
    niche chemistry              2       1         5   <- artifact
    industry tail event          2       1         3   <- artifact

Real terminology is said repeatedly, across many lessons, and appears in
transcripts far more than in summaries. Summarizer artifacts are hapax in the
lectures and equal-or-inflated in the summaries.

The "diamond of profit pools" case is instructive: the transcript reads
"as we saw in the lab ground diamond of profit pools" — that is "lab-GROWN
diamond" (a case study) colliding with "profit pools". The summarizer reified
the word-run into a named framework and the wiki inherited it as SOIC's own.

GATES FLAG; THEY NEVER DELETE. The Mauboussin case proves that auto-rejecting
on text evidence strips true claims. Flags go to an LLM adjudicator (L4) that
sees the raw window, where "lab ground diamond" is obvious.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional

from pydantic import BaseModel, Field

from soic_method.corpus import normalize_slice
from soic_method.models import LessonRecord
from soic_method.router import SIGNAL_TERMS

# A term must be spoken in at least this many DISTINCT eligible lessons to be
# treated as the persona's own terminology. Calibrated against the corpus: the
# rarest genuine term measured ("purple patch") appears in 9 lessons; all three
# known artifacts appear in 1.
MIN_DISTINCT_LESSONS = 2

# L2 fires when a term is no more common in the lectures than in the summaries
# AND is rare outright. Real terms invert hard (right-to-win 37:3).
INFLATION_MAX_BODY = 5

FLAG_HAPAX = "hapax"
FLAG_INFLATED = "summary_inflated"


class TermStats(BaseModel):
    term: str
    body_n: int = 0
    lesson_n: int = 0
    summary_n: int = 0
    flags: List[str] = Field(default_factory=list)
    example_lesson_id: Optional[str] = None
    example_window: str = ""      # raw ASR context, for the L4 adjudicator

    @property
    def suspect(self) -> bool:
        return bool(self.flags)


def _canonical_variants(term: str) -> List[str]:
    """Surface forms to count as the same term.

    Reuses the router's ASR-variant lexicon (ROC/ROCE, pad growth/PAT growth)
    for MATCHING ONLY. Stored text is never rewritten — canonicalising the
    corpus would destroy the evidence the citations point at.
    """
    t = normalize_slice(term)
    out = {t}
    for forms in SIGNAL_TERMS.values():
        forms_n = [normalize_slice(f) for f in forms]
        if t in forms_n:
            out.update(forms_n)
    return sorted(out)


class CorpusIndex:
    """Eligible lessons with their text normalised once.

    Normalising 20.8M chars per term made auditing many terms impractical
    (each `measure_term` call re-walked the whole corpus). Build this once and
    pass it in; raw bodies are retained because the adjudicator window must
    show the ASR as spoken.
    """

    def __init__(self, lessons: Iterable[LessonRecord]):
        self.entries = []
        for l in lessons:
            if not l.eligible:
                continue
            self.entries.append((
                l.lesson_id,
                normalize_slice(l.body_text),
                normalize_slice(l.ai_summary) if l.ai_summary else "",
                l.body_text,
            ))

    def __len__(self) -> int:
        return len(self.entries)


def measure_term(
    term: str,
    lessons: Iterable[LessonRecord],
    window: int = 800,
    index: Optional["CorpusIndex"] = None,
) -> TermStats:
    """Count a term across eligible transcripts and their portal summaries.

    Pass a prebuilt ``index`` when auditing more than a handful of terms.
    """
    variants = _canonical_variants(term)
    st = TermStats(term=term)
    idx = index if index is not None else CorpusIndex(lessons)

    for lesson_id, nbody, nsum, raw in idx.entries:
        body_n = sum(nbody.count(v) for v in variants)
        if body_n:
            st.body_n += body_n
            st.lesson_n += 1
            if st.example_lesson_id is None:
                st.example_lesson_id = lesson_id
                st.example_window = _raw_window(raw, variants, window)
        if nsum:
            st.summary_n += sum(nsum.count(v) for v in variants)

    if st.lesson_n < MIN_DISTINCT_LESSONS:
        st.flags.append(FLAG_HAPAX)
    if st.summary_n >= st.body_n and st.body_n < INFLATION_MAX_BODY:
        st.flags.append(FLAG_INFLATED)
    return st


def _raw_window(body: str, variants: List[str], window: int) -> str:
    """Raw (un-normalised) context around the first hit.

    The adjudicator needs the ASR as-spoken: normalised text hides exactly the
    debris that explains an artifact ("lab ground diamond of profit pools").
    Falls back to a normalised search when casing/spacing defeats a raw find.
    """
    low = body.lower()
    for v in variants:
        i = low.find(v)
        if i >= 0:
            return body[max(0, i - window):i + len(v) + window]
    # Normalised fallback: locate in normalised space, then return a
    # proportional raw slice. Approximate by design — it is context for a
    # human/LLM reader, never a citation.
    nbody = normalize_slice(body)
    for v in variants:
        j = nbody.find(v)
        if j >= 0:
            approx = int(j * (len(body) / max(len(nbody), 1)))
            return body[max(0, approx - window):approx + window]
    return ""


def audit_terms(
    terms: Iterable[str],
    lessons: Iterable[LessonRecord],
    index: Optional["CorpusIndex"] = None,
) -> Dict[str, TermStats]:
    lessons = list(lessons)
    idx = index if index is not None else CorpusIndex(lessons)
    return {t: measure_term(t, lessons, index=idx) for t in terms}


# --- extracting candidate terminology from a note ---------------------------

# Phrases a note presents AS terminology: double-quoted, or 'the X framework'
# style. Deliberately narrow — the gate should examine claimed coinages, not
# every noun phrase.
# Character class admits [] so the mandated ASR-correction form
# ("Sammy hotels [Samhi Hotels]") is captured as one phrase.
_QUOTED = re.compile(r"[\"“”']([a-z][a-z0-9 \-\[\]]{6,60})[\"“”']", re.I)
_NAMED = re.compile(
    r"\b(?:the|a)\s+([a-z][a-z0-9\- ]{4,50}?)\s+"
    r"(?:framework|model|principle|concept|metaphor|analysis|approach)\b",
    re.I,
)


def candidate_terms(note_text: str) -> List[str]:
    """Phrases a note asserts as named terminology."""
    found = set()
    for m in _QUOTED.finditer(note_text):
        found.add(m.group(1).strip().lower())
    for m in _NAMED.finditer(note_text):
        found.add(m.group(1).strip().lower())
    return sorted(f for f in found if len(f.split()) >= 2)


# --- cited quotes vs terminology claims --------------------------------------
#
# The frequency gates exist for UNCITED terminology — a phrase the note
# presents as the persona's recurring vocabulary. A phrase quoted WITH an
# inline citation like (TURN 00:17:39) is a different animal: it claims only
# "these words occur at this location", and the right check is presence in the
# cited lesson, not corpus-wide frequency. Auditing the first regenerated note
# proved the distinction matters: 17 of its 22 flagged "terms" were cited
# verbatim quotes, hapax BECAUSE the note cites exactly one lesson.

_CITATION_NEAR = re.compile(r"\(([A-Z][A-Z0-9]*)\s+\d{2}:\d{2}:\d{2}\)")
_CITE_WINDOW = 220     # chars after the closing quote to look for a citation


class QuoteCheck(BaseModel):
    phrase: str
    cited_ref: Optional[str] = None
    verified: bool = False       # phrase found in the cited lesson's body


def split_cited_quotes(
    note_text: str,
) -> Dict[str, List[str]]:
    """Partition a note's quoted phrases into cited vs uncited.

    A quote is "cited" when a (REF HH:MM:SS) citation appears within
    ``_CITE_WINDOW`` chars after it. Returns {"cited": [...], "uncited": [...]}
    with the ref recorded alongside cited phrases as ``phrase|ref``.
    """
    cited: List[str] = []
    uncited: List[str] = []
    for m in _QUOTED.finditer(note_text):
        phrase = m.group(1).strip().lower()
        if len(phrase.split()) < 2:
            continue
        tail = note_text[m.end():m.end() + _CITE_WINDOW]
        cm = _CITATION_NEAR.search(tail)
        if cm:
            cited.append(phrase + "|" + cm.group(1))
        else:
            uncited.append(phrase)
    return {"cited": sorted(set(cited)), "uncited": sorted(set(uncited))}


def verify_cited_quotes(
    note_text: str,
    ref_to_lesson: Dict[str, LessonRecord],
) -> List[QuoteCheck]:
    """Presence-check each cited quote against the lesson its ref names.

    Bracketed editorial corrections are stripped before matching: the write
    rules mandate "Sammy hotels [Samhi Hotels]", and the correction is the
    note's annotation, not transcript text.
    """
    out: List[QuoteCheck] = []
    parts = split_cited_quotes(note_text)
    for item in parts["cited"]:
        phrase, ref = item.rsplit("|", 1)
        clean = re.sub(r"\[[^\]]*\]", "", phrase).strip()
        lesson = ref_to_lesson.get(ref)
        ok = False
        if lesson is not None and clean:
            ok = clean in normalize_slice(lesson.body_text)
        out.append(QuoteCheck(phrase=phrase, cited_ref=ref, verified=ok))
    return out
