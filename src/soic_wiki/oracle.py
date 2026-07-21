"""L3 — the enrichment oracle. No LLM.

The Phase-0 enrichment files were written by reading 19 FULL transcripts, and
they carry real citations. They are the only independent ground truth we have
about this corpus, and they are used two ways:

**Denials.** `enrichment_valuechain.md` states outright:

    He never uses the literal phrase "diamond of profit pools" (that's
    Mauboussin/Bogle terminology from *Measuring the Moat*, which he
    explicitly cites ... [P1 00:02-00:03])

That single sentence is both halves of the problem. It DENIES a phrase the
wiki teaches as the persona's own, and it AFFIRMS a citation the corpus cannot
verbatim support — the ASR renders it "measuring the mode by Michael Mopasi",
so `Mauboussin` and `measuring the moat` both occur ZERO times. A gate that
checks text presence rejects the true claim; the oracle affirms it.

**Span recall.** Every oracle-cited span should be covered by some concept
note. This turns "the wiki is hollow" from a subjective reading into a number:
the worked valuation at TURN L165-183 is oracle-cited, and the current
`practical-valuation-approach.md` cites nothing there while explicitly saying
no worked example exists.

Citation formats, both verified against the corpus:

  enrichment_frameworks.md   (TURN L165-183)   ref + VAULT line range
  enrichment_valuechain.md   [P1 00:02-00:03]  ref + HH:MM (minute grain)
  enrichment_agrochem.md     *(file.md)*       file-level only -- NOT resolvable
                                               to a span; supports lesson-level
                                               recall only.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from soic_method.models import LessonRecord
from soic_wiki.chunk import MarkerIndex

# A vault transcript file is a ~14-line frontmatter/header block followed by
# the body. Verified empirically: enrichment's (TURN L165-183) maps to
# body_text lines [150:168] and lands exactly on the [00:17:21] worked
# valuation containing 606 / 287 / "14 times".
VAULT_HEADER_LINES = 14

_LEGEND = re.compile(r"^\s*[-*]?\s*([A-Z][A-Z0-9]*)\s*=\s*`?([^`\n]+?)`?\s*$", re.M)
_LINE_CITE = re.compile(r"\(([A-Z][A-Z0-9]*)\s+L(\d+)-(\d+)\)")
_TS_CITE = re.compile(r"\[([A-Z][A-Z0-9]*)\s+(\d{2}):(\d{2})(?:-(\d{2}):(\d{2}))?\]")

_DENIAL = re.compile(
    r"[^.\n]*\b(?:never uses|never says|does not use|doesn't use|"
    r"no evidence (?:that|of)|is not (?:his|a real))\b[^.\n]*\.",
    re.I,
)
_QUOTED_IN_DENIAL = re.compile(r"[\"“”']([^\"“”']{4,80})[\"“”']")


class OracleSpan(BaseModel):
    ref: str
    lesson_id: str
    lesson_title: str
    start: int
    end: int
    ts_start: str
    ts_end: str
    kind: str            # "line_range" | "timestamp"


class Denial(BaseModel):
    sentence: str
    phrases: List[str] = Field(default_factory=list)
    source_file: str


def parse_legend(text: str) -> Dict[str, str]:
    """`SB2 = identifying-scalable-businesses/part-2-...-transcript.md` -> stem."""
    out: Dict[str, str] = {}
    for m in _LEGEND.finditer(text):
        ref, path = m.group(1), m.group(2).strip()
        stem = path.rsplit("/", 1)[-1]
        if stem.endswith(".md"):
            stem = stem[:-3]
        if stem.endswith("-transcript"):
            stem = stem[: -len("-transcript")]
        out[ref] = stem
    return out


def resolve_line_range(
    lesson: LessonRecord, l_start: int, l_end: int
) -> Optional[OracleSpan]:
    lines = lesson.body_text.split("\n")
    i = max(l_start - VAULT_HEADER_LINES - 1, 0)
    j = min(l_end - VAULT_HEADER_LINES, len(lines))
    if i >= j:
        return None
    start = sum(len(x) + 1 for x in lines[:i])
    end = min(start + sum(len(x) + 1 for x in lines[i:j]), len(lesson.body_text))
    idx = MarkerIndex(lesson.body_text)
    return OracleSpan(ref="", lesson_id=lesson.lesson_id, lesson_title=lesson.title,
                      start=start, end=end, kind="line_range",
                      ts_start=idx.timestamp_at(start),
                      ts_end=idx.timestamp_at(max(end - 1, start)))


def resolve_timestamp_range(
    lesson: LessonRecord, hh: int, mm: int, hh2: Optional[int], mm2: Optional[int]
) -> Optional[OracleSpan]:
    """`[P1 00:02-00:03]` is HH:MM at minute granularity (verified: the
    Mauboussin citation cited as 00:02 sits at 00:02:29)."""
    idx = MarkerIndex(lesson.body_text)
    if not len(idx):
        return None
    want_start = hh * 3600 + mm * 60
    want_end = (hh2 * 3600 + mm2 * 60 + 60) if hh2 is not None else want_start + 60

    def offset_for(sec: int) -> int:
        best = 0
        for off in idx.offsets:
            ts = idx.timestamp_at(off)
            h, m, s = (int(x) for x in ts.split(":"))
            if h * 3600 + m * 60 + s <= sec:
                best = off
            else:
                break
        return best

    start, end = offset_for(want_start), offset_for(want_end)
    if end <= start:
        end = min(start + 2000, len(lesson.body_text))
    return OracleSpan(ref="", lesson_id=lesson.lesson_id, lesson_title=lesson.title,
                      start=start, end=end, kind="timestamp",
                      ts_start=idx.timestamp_at(start),
                      ts_end=idx.timestamp_at(max(end - 1, start)))


def extract_denials(text: str, source_file: str) -> List[Denial]:
    """Negative assertions the enrichment layer makes about the persona."""
    out: List[Denial] = []
    for m in _DENIAL.finditer(text):
        sentence = " ".join(m.group(0).split())
        phrases = [p.strip().lower() for p in _QUOTED_IN_DENIAL.findall(sentence)]
        if phrases:
            out.append(Denial(sentence=sentence, phrases=phrases,
                              source_file=source_file))
    return out


class DenialViolation(BaseModel):
    note_slug: str
    phrase: str
    denial: str
    source_file: str


def check_denials(
    notes: Dict[str, str], denials: List[Denial]
) -> List[DenialViolation]:
    """A note asserting a phrase the enrichment layer explicitly denies.

    This is the direct catch for "diamond of profit pools": the enrichment
    file says he never uses it; two concept notes teach it as his.
    """
    out: List[DenialViolation] = []
    for slug, text in notes.items():
        low = text.lower()
        for d in denials:
            for p in d.phrases:
                if p in low:
                    out.append(DenialViolation(note_slug=slug, phrase=p,
                                               denial=d.sentence,
                                               source_file=d.source_file))
    return out


def parse_oracle_spans(
    text: str, legend: Dict[str, str], by_slug: Dict[str, LessonRecord]
) -> List[OracleSpan]:
    spans: List[OracleSpan] = []
    for m in _LINE_CITE.finditer(text):
        ref, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        lesson = by_slug.get(legend.get(ref, ""))
        if lesson is None:
            continue
        s = resolve_line_range(lesson, a, b)
        if s:
            spans.append(s.model_copy(update={"ref": ref}))
    for m in _TS_CITE.finditer(text):
        ref = m.group(1)
        lesson = by_slug.get(legend.get(ref, ""))
        if lesson is None:
            continue
        h2 = int(m.group(4)) if m.group(4) else None
        m2 = int(m.group(5)) if m.group(5) else None
        s = resolve_timestamp_range(lesson, int(m.group(2)), int(m.group(3)), h2, m2)
        if s:
            spans.append(s.model_copy(update={"ref": ref}))
    return spans


def span_recall(oracle: List[OracleSpan], covered: List[OracleSpan]) -> float:
    """Fraction of oracle spans overlapped by at least one note span."""
    if not oracle:
        return 1.0
    hit = 0
    for o in oracle:
        for c in covered:
            if c.lesson_id == o.lesson_id and c.start < o.end and o.start < c.end:
                hit += 1
                break
    return hit / len(oracle)
