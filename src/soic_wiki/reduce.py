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
import re
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


# --- fresh-concept proposal (for sector modules with no pinned wiki entry) --
#
# A2's reduce_beats forces beats onto a PINNED concept list, which is correct
# for a strict A/B against an existing wiki topic. A brand-new sector module
# (e.g. "Lab Grown Diamonds Sector Analysis") has no prior wiki entry to pin
# against -- forcing its beats onto sector-analysis-framework's 22 generic
# slugs (screening, TVGP, valuation...) would distort sector-specific content
# to fit categories that were never about this sector. Each new module instead
# gets its OWN small concept list, proposed directly from ITS beats.

PROPOSE_PROMPT = """You are naming the CONCEPTS a single sector lecture actually
covers, so each can become its own knowledge-base note.

Below is an indexed list of teaching beats extracted from a lecture on
"{sector_title}". Propose a SMALL set of concept slugs (typically 3-7 for one
lecture) that partition this material by TOPIC, not by lecture structure --
e.g. "value chain and key players", "unit economics and margins", "growth
drivers and risks", "valuation approach" are the right GRAIN. Do not invent a
concept with no beats behind it, and do not split one coherent idea into two
slugs just to hit a target count.

Return JSON only:
{{"concepts": [{{"slug": "<kebab-case>", "scope": "<one line>",
  "beat_indices": [<int>, ...]}}, ...],
  "unassigned": [<beat indices fitting no proposed concept>]}}

Every beat index 0..{max_idx} should appear in exactly one concept's list or
in "unassigned" -- do not omit or duplicate.

BEATS:
{beats}
"""


class ProposedConcept(BaseModel):
    slug: str
    scope: str
    beat_indices: List[int] = Field(default_factory=list)


class ProposeResult(BaseModel):
    concepts: List[ProposedConcept] = Field(default_factory=list)
    unassigned: List[int] = Field(default_factory=list)


def build_propose_prompt(
    sector_title: str, beats: List[Beat], refs: Dict[str, str]
) -> str:
    lines = []
    for i, b in enumerate(beats):
        ref = refs.get(b.lesson_id, b.lesson_id)
        lines.append("%d. [%s %s-%s] (%s%s) %s" % (
            i, ref, b.ts_start, b.ts_end, b.kind,
            ", numbers" if b.has_numbers else "", b.gist))
    return PROPOSE_PROMPT.format(sector_title=sector_title,
                                 max_idx=max(len(beats) - 1, 0),
                                 beats="\n".join(lines))


_SLUG_OK = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def propose_concepts(
    sector_title: str,
    beats: List[Beat],
    refs: Dict[str, str],
    llm: Callable[[str], str],
) -> ProposeResult:
    try:
        payload = json.loads(llm(build_propose_prompt(sector_title, beats, refs)))
    except (ValueError, TypeError):
        return ProposeResult()
    if not isinstance(payload, dict) or not isinstance(payload.get("concepts"), list):
        return ProposeResult()

    n = len(beats)
    seen_idx = set()
    out = ProposeResult()
    seen_slugs = set()
    for raw in payload["concepts"]:
        if not isinstance(raw, dict):
            continue
        slug = str(raw.get("slug", "")).strip().lower()
        if not slug or not _SLUG_OK.match(slug) or slug in seen_slugs:
            continue                      # drop malformed/duplicate slugs
        idxs = raw.get("beat_indices", [])
        if not isinstance(idxs, list):
            idxs = []
        clean = sorted({int(i) for i in idxs
                        if isinstance(i, (int, float)) and 0 <= int(i) < n})
        if not clean:
            continue                      # a concept with no evidence is not a concept
        seen_slugs.add(slug)
        seen_idx.update(clean)
        out.concepts.append(ProposedConcept(
            slug=slug, scope=str(raw.get("scope", ""))[:200], beat_indices=clean))

    raw_un = payload.get("unassigned", [])
    stated_un = {int(i) for i in raw_un
                if isinstance(i, (int, float)) and 0 <= int(i) < n} \
        if isinstance(raw_un, list) else set()
    # Any beat neither claimed by a concept nor stated as unassigned is still
    # unassigned -- never silently dropped.
    out.unassigned = sorted(stated_un | (set(range(n)) - seen_idx - stated_un))
    return out
