"""Map → reduce → write plumbing for the transcript-grounded rebuild.

The one structural rule, enforced here in CODE and not in a prompt: **beat
prose never reaches the write stage.** Beats carry offsets; the write prompt
is assembled by slicing the RAW ``body_text`` at those offsets. If beats were
allowed to carry their summaries into the write prompt, they would become the
new AI-summaries — the exact failure this rebuild exists to fix, one level up.

LLM stages take an injected ``llm: Callable[[str], str]`` (codebase
convention) so everything is testable offline.
"""

from __future__ import annotations

import json
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from soic_method.models import LessonRecord
from soic_wiki.chunk import MarkerIndex

BEAT_KINDS = ("framework", "worked_example", "heuristic", "caveat", "sector_fact")


class Beat(BaseModel):
    lesson_id: str
    gist: str                       # selection metadata ONLY — never shown to S4
    kind: str
    char_start: int
    char_end: int
    ts_start: str = ""
    ts_end: str = ""
    has_numbers: bool = False


MAP_PROMPT = """You are indexing one full lecture transcript for a knowledge base
about an investing instructor's method.

The transcript below is RAW auto-generated ASR: numbers, names and grammar are
sometimes corrupted. Do not correct anything — your job is to POINT, not to
paraphrase.

Identify every distinct teaching beat: a framework being explained, a worked
example with numbers, a heuristic/rule of thumb, a caveat/warning, or a
sector-specific fact. For each, return the character offsets of the span that
contains it. Offsets are given by the <<offset:N>> markers interleaved every
1000 characters.

Return JSON only:
{{"beats": [{{"gist": "<ONE short line, selection metadata only>",
  "kind": "framework"|"worked_example"|"heuristic"|"caveat"|"sector_fact",
  "char_start": <int>, "char_end": <int>,
  "has_numbers": true|false}}]}}

Aim for completeness over granularity: 15-40 beats for a typical lecture.
Spans may be generous (a few hundred to ~2000 chars); they will be sliced
from the raw transcript later, so precision of MEANING matters more than
tight boundaries.

TRANSCRIPT ({title}, {nchars} chars):
{annotated}
"""


def _annotate(text: str, every: int = 1000) -> str:
    parts = []
    for i in range(0, len(text), every):
        parts.append("<<offset:%d>>%s" % (i, text[i:i + every]))
    return "".join(parts)


def build_map_prompt(lesson: LessonRecord) -> str:
    return MAP_PROMPT.format(title=lesson.title, nchars=len(lesson.body_text),
                             annotated=_annotate(lesson.body_text))


def map_lesson(lesson: LessonRecord, llm: Callable[[str], str]) -> List[Beat]:
    """One agent call over one FULL transcript → timestamped beats."""
    try:
        payload = json.loads(llm(build_map_prompt(lesson)))
    except (ValueError, TypeError):
        return []
    if not isinstance(payload, dict) or not isinstance(payload.get("beats"), list):
        return []

    idx = MarkerIndex(lesson.body_text)
    out: List[Beat] = []
    for raw in payload["beats"]:
        if not isinstance(raw, dict):
            continue
        try:
            a, b = int(raw["char_start"]), int(raw["char_end"])
        except (KeyError, TypeError, ValueError):
            continue
        if a < 0 or b > len(lesson.body_text) or b <= a:
            continue
        kind = raw.get("kind", "")
        if kind not in BEAT_KINDS:
            continue
        out.append(Beat(
            lesson_id=lesson.lesson_id,
            gist=str(raw.get("gist", ""))[:200],
            kind=kind,
            char_start=a, char_end=b,
            ts_start=idx.timestamp_at(a),
            ts_end=idx.timestamp_at(max(b - 1, a)),
            has_numbers=bool(raw.get("has_numbers", False)),
        ))
    return out


WRITE_PROMPT = """You are writing one concept note for a knowledge base about an
investing instructor's method (persona: SOIC / Ishmohit Arora).

Your ONLY source material is the raw transcript excerpts below. Each excerpt
is prefixed with a citation header like:

  === {ref} {ts_start}-{ts_end} ({lesson_title}) ===

Rules:
- Every numeric claim and every quoted phrase MUST carry an inline citation
  of the form ({ref} HH:MM:SS) pointing into one of the excerpts.
- The transcripts are auto-generated ASR: numbers, names and grammar are
  sometimes corrupted. Quote what is there; where a name is obviously garbled
  you may note the likely intended name in brackets, e.g. "Sammy hotels
  [Samhi Hotels]", but never silently correct.
- Do NOT attribute named terminology to the instructor unless the excerpts
  show him actually using the phrase.
- Structure: ## The mechanism (HOW it works, step by step, with the worked
  numbers), ## Why it matters (the reasoning given), ## Caveats and limits
  (stated by the instructor, plus ASR-quality caveats where relevant).
- Write mechanism-depth prose, not a summary. If the excerpts contain a
  worked numeric example, reproduce its arithmetic faithfully with citations.

Concept: {concept_title}
Concept scope: {concept_scope}

EXCERPTS:
{excerpts}

Return ONLY the markdown body of the note (no frontmatter).
"""


class WriteJob(BaseModel):
    concept_title: str
    concept_scope: str
    slug: str
    beats: List[Beat]
    refs: Dict[str, str] = Field(default_factory=dict)   # lesson_id -> short ref


def build_write_prompt(
    job: WriteJob, lessons: Dict[str, LessonRecord]
) -> str:
    """Assemble the write prompt from RAW slices. Beat gist is NOT included.

    This is the structural enforcement: the only lesson-derived text in the
    prompt is ``body_text[span]``, verbatim.
    """
    excerpts = []
    for b in sorted(job.beats, key=lambda x: (x.lesson_id, x.char_start)):
        lesson = lessons.get(b.lesson_id)
        if lesson is None:
            continue
        ref = job.refs.get(b.lesson_id, "SRC")
        header = "=== %s %s-%s (%s) ===" % (ref, b.ts_start, b.ts_end, lesson.title)
        excerpts.append(header + "\n" + lesson.body_text[b.char_start:b.char_end])
    return WRITE_PROMPT.format(
        concept_title=job.concept_title,
        concept_scope=job.concept_scope,
        excerpts="\n\n".join(excerpts),
        ref="{ref}", ts_start="{ts_start}", ts_end="{ts_end}",
        lesson_title="{lesson_title}",
    )


def write_note(
    job: WriteJob,
    lessons: Dict[str, LessonRecord],
    llm: Callable[[str], str],
) -> Optional[str]:
    body = llm(build_write_prompt(job, lessons))
    return body.strip() if isinstance(body, str) and body.strip() else None
