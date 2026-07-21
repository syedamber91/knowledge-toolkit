"""Reduce stage: cluster beats across lessons into concept assignments.

Beat GISTS are permitted here — reduce is selection/clustering, and gists are
selection metadata. The structural rule bars them only from the WRITE prompt,
where their prose could substitute for transcript text.

For the A2 pilot the concept list is PINNED to the 22 existing slugs so the
A/B against the summary-built wiki is like-for-like. The reducer may also
propose beats that fit NO pinned concept (returned under ``unassigned`` —
these inform future concept-list revisions, they are not silently dropped).
"""

from __future__ import annotations

import json
from typing import Callable, Dict, List

from pydantic import BaseModel, Field

from soic_wiki.pipeline import Beat

REDUCE_PROMPT = """You are the REDUCE stage of a knowledge-extraction pipeline.

Below is (a) a pinned list of concept slugs with one-line scopes, and (b) an
indexed list of teaching beats extracted from {n_lessons} full lecture
transcripts. Each beat has an index, a lesson ref, timestamps, a kind, and a
one-line gist.

Assign every beat to the pinned concepts it evidences. A beat MAY serve
multiple concepts (a worked example often evidences both a framework concept
and a valuation concept). A beat that fits no pinned concept goes to
"unassigned" — do not force-fit.

Return JSON only:
{{"assignments": {{"<slug>": [<beat indices>], ...}},
  "unassigned": [<beat indices>]}}

Every pinned slug must appear as a key (empty list allowed — an empty list is
a REAL finding: it means the transcripts do not support that concept).

PINNED CONCEPTS:
{concepts}

BEATS:
{beats}
"""


class ReduceResult(BaseModel):
    assignments: Dict[str, List[int]] = Field(default_factory=dict)
    unassigned: List[int] = Field(default_factory=list)


def build_reduce_prompt(
    concepts: Dict[str, str],           # slug -> one-line scope
    beats: List[Beat],
    refs: Dict[str, str],               # lesson_id -> short ref
) -> str:
    concept_lines = "\n".join("- %s: %s" % (s, sc) for s, sc in sorted(concepts.items()))
    beat_lines = []
    for i, b in enumerate(beats):
        ref = refs.get(b.lesson_id, b.lesson_id)
        beat_lines.append("%d. [%s %s-%s] (%s%s) %s" % (
            i, ref, b.ts_start, b.ts_end, b.kind,
            ", numbers" if b.has_numbers else "", b.gist))
    return REDUCE_PROMPT.format(
        n_lessons=len({b.lesson_id for b in beats}),
        concepts=concept_lines,
        beats="\n".join(beat_lines),
    )


def reduce_beats(
    concepts: Dict[str, str],
    beats: List[Beat],
    refs: Dict[str, str],
    llm: Callable[[str], str],
) -> ReduceResult:
    try:
        payload = json.loads(llm(build_reduce_prompt(concepts, beats, refs)))
    except (ValueError, TypeError):
        return ReduceResult()
    if not isinstance(payload, dict):
        return ReduceResult()

    n = len(beats)
    assignments: Dict[str, List[int]] = {}
    raw_assign = payload.get("assignments")
    if isinstance(raw_assign, dict):
        for slug in concepts:
            idxs = raw_assign.get(slug, [])
            if not isinstance(idxs, list):
                idxs = []
            assignments[slug] = sorted({int(i) for i in idxs
                                        if isinstance(i, (int, float))
                                        and 0 <= int(i) < n})
    else:
        assignments = {slug: [] for slug in concepts}

    raw_un = payload.get("unassigned", [])
    unassigned = sorted({int(i) for i in raw_un
                         if isinstance(i, (int, float)) and 0 <= int(i) < n}) \
        if isinstance(raw_un, list) else []
    return ReduceResult(assignments=assignments, unassigned=unassigned)
