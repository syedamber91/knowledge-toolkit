"""Sector-batch orchestration: NotebookLM does the synthesis, this module
does the plumbing AND the mechanical parts of the judgment loop.

REF-code assignment, idempotent notebook creation/reuse, and source seeding
are deterministic string/IO work with no LLM involvement. Across all 14
sectors run this session, NotebookLM's propose-concepts answer followed the
SAME parseable format every single time (### <title> / Scope: / Sources: /
Timestamps:) -- so that parsing, and the write-prompt construction, are now
modeled as real functions too. What's still deliberately NOT automated here:
judging whether NotebookLM's answer is actually good (gate PASS/FAIL is
still the real arbiter, and a human still decides whether to accept a
framework-evolution diff) -- this module gets you from "notebook exists" to
"gated notes on disk," nothing more.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import yaml

from soic_senses.notebook_client import add_text_source, ask_notebook, create_notebook

_SUFFIXES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def chunk_lessons(
    lessons: List[Dict[str, str]], max_per_batch: int
) -> List[List[Dict[str, str]]]:
    """Split a module's lessons into batches of at most max_per_batch each,
    preserving order. A module already at or under the limit comes back
    as a single batch, unchanged -- this is a ceiling, not a forced split.

    Exists because a single oversized NotebookLM notebook (31 lessons, the
    "SOIC Market Signals" module) fabricated citations that a smaller
    notebook context didn't -- see run_sector_pipeline's
    max_lessons_per_batch parameter.
    """
    if max_per_batch <= 0:
        raise ValueError(f"max_per_batch must be positive, got {max_per_batch}")
    return [lessons[i : i + max_per_batch] for i in range(0, len(lessons), max_per_batch)]


def _suffix_for(i: int) -> str:
    """Spreadsheet-column-style suffix for a 0-based lesson index: A, B, ...,
    Z, AA, AB, ..., AZ, BA, ... Unlike a fixed-length alphabet string, this
    never runs out -- a module with more than 26 real lessons (confirmed
    live for "SOIC Market Signals", 31 lessons after the 2026-07-27
    timestamp-marker re-capture) must still get a unique code per lesson
    instead of an IndexError.
    """
    if i < len(_SUFFIXES):
        return _SUFFIXES[i]
    first, second = divmod(i - len(_SUFFIXES), len(_SUFFIXES))
    return _SUFFIXES[first] + _SUFFIXES[second]


def _mnemonic(module_title: str) -> str:
    first_word = re.sub(r"[^A-Za-z]", "", module_title.split()[0]) if module_title.split() else ""
    return (first_word[:5].upper() or "SECTOR")


def assign_ref_codes(
    lessons: List[Dict[str, str]],
    module_title: str,
    existing_codes: Set[str],
) -> Dict[str, str]:
    """Assign a short REF mnemonic per lesson, matching the refs.json
    convention already used across the 18 done batches.

    A single-lesson module gets the bare mnemonic; a multi-lesson module
    gets A/B/C suffixes. Collides with an already-used corpus-wide code
    (e.g. a bare "REAL" from an earlier run) are resolved by appending a
    numeric suffix rather than silently reusing someone else's code.
    """
    base = _mnemonic(module_title)
    codes: Dict[str, str] = {}
    used = set(existing_codes)

    for i, lesson in enumerate(lessons):
        candidate = base if len(lessons) == 1 else base + _suffix_for(i)
        if candidate in used:
            n = 2
            while f"{candidate}{n}" in used:
                n += 1
            candidate = f"{candidate}{n}"
        used.add(candidate)
        codes[lesson["lesson_id"]] = candidate

    return codes


def ensure_sector_notebook(
    slug: str,
    title: str,
    registry_path: Union[str, Path],
) -> str:
    """Return this sector's notebook_id, creating one only if the slug
    isn't already registered. Persists a new entry back to the registry
    file so a re-run never creates a duplicate notebook.
    """
    registry_path = Path(registry_path)
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    data.setdefault("notebooks", {})

    existing = data["notebooks"].get(slug)
    if existing:
        return existing["notebook_id"]

    notebook_id = create_notebook(title=title)
    data["notebooks"][slug] = {"notebook_id": notebook_id, "title": title}
    registry_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return notebook_id


def seed_sector_sources(notebook_id: str, lessons_with_codes: List[Dict[str, str]]) -> None:
    """Add each lesson's raw transcript as a text source, titled
    "<REF> <lesson title>" so NotebookLM's own citations can be matched
    back to a REF code by the write-stage prompt.
    """
    for lesson in lessons_with_codes:
        add_text_source(
            notebook_id,
            lesson["body_text"],
            title=f"{lesson['ref_code']} {lesson['title']}",
        )


@dataclass
class ConceptProposal:
    title: str
    scope: str
    sources: List[str]
    timestamps: str


_CONCEPT_BLOCK = re.compile(
    r"###\s*(.+?)\s*\n"
    r"Scope:\s*(.+?)\s*\n"
    r"Sources:\s*(.+?)\s*\n"
    r"Timestamps:\s*(.+?)\s*(?=\n###|\Z)",
    re.DOTALL,
)


def build_propose_prompt(module_title: str, ref_codes: List[str], min_concepts: int = 3, max_concepts: int = 8) -> str:
    """Build the propose-concepts prompt, exactly matching the format used
    live across all 14 sectors this session -- the format NotebookLM
    reliably followed every time, which is what makes parse_propose_response
    a real parser instead of a best-effort guess.
    """
    sources_list = ", ".join(ref_codes)
    return (
        f"You have several sources loaded: lecture transcript segments from an Indian "
        f"stock-market educational series (SOIC) on {module_title}, titled with REF codes "
        f"{sources_list}. Each has inline timestamp markers like [HH:MM:SS] before each "
        f"spoken segment.\n\n"
        f"Task: partition the substantive investing content across ALL these sources into "
        f"a minimum of {min_concepts} and a maximum of {max_concepts} distinct concepts "
        f"(topics), each concept covering one coherent teaching point (a framework, a "
        f"company case study, a value-chain segment, a risk factor, etc. -- not a vague "
        f"summary). A concept may draw on more than one source if they cover the same topic.\n\n"
        f"For each concept, respond in this exact format, one block per concept:\n\n"
        f"### <short-title-in-title-case>\n"
        f"Scope: <one sentence describing what this concept covers>\n"
        f"Sources: <which REF code(s) this concept draws from>\n"
        f"Timestamps: <comma-separated list of the [HH:MM:SS] ranges where this concept is "
        f"discussed, per source>\n\n"
        f"Do not write the full note content yet -- only the concept list in the format above."
    )


def parse_propose_response(response_text: str) -> List[ConceptProposal]:
    """Parse a propose-concepts answer into structured ConceptProposals.

    Returns an empty list (not an error) if the text doesn't match the
    expected format at all -- an empty result is itself a real signal
    ("this answer wasn't usable"), for the caller to act on, not something
    to paper over with a fallback guess.
    """
    concepts = []
    for m in _CONCEPT_BLOCK.finditer(response_text):
        title, scope, sources_raw, timestamps = m.groups()
        sources = [s.strip() for s in sources_raw.split(",") if s.strip()]
        concepts.append(ConceptProposal(title=title, scope=scope, sources=sources, timestamps=timestamps.strip()))
    return concepts


def slugify_concept_title(title: str) -> str:
    """Turn a concept title into the filesystem-safe slug used for its
    note filename, matching the slug style already used across every
    committed concept note this session.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")


def build_write_prompt(concept: ConceptProposal) -> str:
    """Build the write-concept prompt for one proposed concept, with the
    citation-format wording tightened after three real defects found this
    session: (1) the write stage must never repeat the REF code before the
    second timestamp in a range (broke G2 entirely for one file until
    fixed), (2) quotation marks must be reserved for verbatim transcript
    text (a framework-evolution run fabricated a quote inside quote marks
    before this wording was added), and (3) an explicit self-verification
    step (added 2026-07-27 after "SOIC Market Signals", a 31-lesson
    notebook -- the largest single-notebook context run this session --
    fabricated two citations whose quoted text and timestamp were both
    invented, not just mismatched; quotation-mark discipline alone wasn't
    enough once the notebook held far more source material than usual).
    Positive-only framing throughout -- never show the malformed pattern
    as a "don't do this" example.
    """
    sources_list = ", ".join(concept.sources)
    return (
        f'Write a detailed analysis note on the concept "{concept.title}" using ONLY the '
        f"loaded source transcripts. This concept draws from sources {sources_list}, roughly "
        f"at {concept.timestamps}, but you may cite anything relevant from those sources.\n\n"
        f"STRICT citation rule: every specific claim, number, or quote MUST be followed "
        f"immediately by a citation in this exact format: (REF HH:MM:SS) for a single "
        f"timestamp, or (REF HH:MM:SS-HH:MM:SS) for a range -- the REF code is written "
        f"exactly once, at the very start of the parenthetical, immediately followed by one "
        f"or two HH:MM:SS values separated by a single hyphen, where REF is the exact source "
        f"code (e.g. {concept.sources[0] if concept.sources else 'FLUORA'}) for the source "
        f"you are citing, and HH:MM:SS is an actual [HH:MM:SS] timestamp marker embedded in "
        f"that source's transcript. Do NOT use your own footnote-style citations like [1] or "
        f"[2].\n\n"
        f"Quotation marks are a promise: only put quotation marks around text you are "
        f"copying character-for-character from the transcript at the exact cited timestamp. "
        f"When you want to give your own label or paraphrase, state it in your own words "
        f"WITHOUT quotation marks, and still cite the timestamp that supports the underlying "
        f"fact. Reserve quotation marks strictly for the instructor's own exact words.\n\n"
        f"Before finalizing each citation, silently re-read the exact source text at that "
        f"timestamp in the named source and confirm the quoted words genuinely appear there. "
        f"If you cannot find the exact phrase at that timestamp, do not invent it -- search "
        f"nearby moments in the same source for the correct timestamp, or drop the quotation "
        f"marks and state the underlying fact in your own words instead.\n\n"
        f"If a passage is garbled or ambiguous in the transcript, say so explicitly (e.g. "
        f'write "garbled" or "[likely X]") rather than silently guessing or smoothing it over.\n\n'
        f"Structure the note with exactly these three headings:\n"
        f"## The mechanism\n"
        f"## Why it matters\n"
        f"## Caveats and limits\n\n"
        f"Write the mechanism section as a step-by-step explanation of HOW this concept "
        f"works, not a summary of that it exists."
    )


def propose_concepts_via_notebook(
    notebook_id: str,
    module_title: str,
    ref_codes: List[str],
    min_concepts: int = 3,
    max_concepts: int = 8,
) -> Tuple[List[ConceptProposal], Optional[str]]:
    """Fire the propose-concepts query and parse the answer. Returns
    (concepts, conversation_id) so the caller can thread the same
    conversation through the write-concept queries that follow.
    """
    prompt = build_propose_prompt(module_title, ref_codes, min_concepts, max_concepts)
    result = ask_notebook(notebook_id, prompt, timeout=180.0)
    concepts = parse_propose_response(result["answer"])
    return concepts, result.get("conversation_id")


def write_concept_via_notebook(
    notebook_id: str,
    concept: ConceptProposal,
    conversation_id: Optional[str] = None,
) -> str:
    """Fire the write-concept query for one concept, returning the raw
    note text (not yet gated -- the caller runs the existing deterministic
    gates against it, exactly as scripts/sector_report.py already does).
    """
    prompt = build_write_prompt(concept)
    result = ask_notebook(notebook_id, prompt, conversation_id=conversation_id, timeout=180.0)
    return result["answer"]


@dataclass
class SectorRunResult:
    slug: str
    notebook_id: str
    ref_codes: Dict[str, str]
    concepts: List[ConceptProposal]
    notes: Dict[str, str]


def run_sector_pipeline(
    module_title: str,
    slug: str,
    lessons: List[Dict[str, str]],
    sector_registry_path: Union[str, Path],
    existing_codes: Set[str],
    min_concepts: int = 3,
    max_concepts: int = 8,
    reseed: bool = True,
    max_lessons_per_batch: Optional[int] = None,
) -> SectorRunResult:
    """Run steps 1-6 of the NotebookLM-brain loop for one sector module:
    assign REF codes, ensure/reuse the notebook, seed sources (unless
    reseed=False, e.g. a re-run against an already-seeded notebook),
    propose concepts, then write each one.

    max_lessons_per_batch is a ceiling, not a forced split: a module at or
    under the limit runs exactly as before, one notebook. A module over the
    limit is split (via chunk_lessons) into several smaller batches, each
    with its OWN notebook (slug suffixed "-batchN") so no single NotebookLM
    context ever holds more than max_lessons_per_batch lessons' worth of
    source material -- added 2026-07-27 after "SOIC Market Signals" (31
    lessons, this session's largest single-notebook context) fabricated
    two citations that a smaller notebook didn't. REF codes stay globally
    unique across batches (existing_codes threads forward batch to batch,
    same collision discipline as a single-batch run), and results
    (ref_codes, concepts, notes) are merged into one SectorRunResult so the
    caller (the CLI, the gate script, the vault sync) sees one module's
    worth of output regardless of how many notebooks it took to produce.

    Deliberately does NOT run the gates or sync to the vault -- those need
    a real notes directory / vault path and are already one-line calls
    (scripts/sector_report.py, scripts/sync_notes_to_vault.py); keeping
    them out of this function keeps its own testing simple and keeps the
    "did NotebookLM's output actually pass" judgment where it belongs, in
    the deterministic gate script, not buried inside this orchestrator.
    """
    batches = (
        chunk_lessons(lessons, max_lessons_per_batch)
        if max_lessons_per_batch and len(lessons) > max_lessons_per_batch
        else [lessons]
    )
    single_batch = len(batches) == 1

    all_ref_codes: Dict[str, str] = {}
    all_concepts: List[ConceptProposal] = []
    all_notes: Dict[str, str] = {}
    used_codes = set(existing_codes)
    first_notebook_id: Optional[str] = None

    for batch_index, batch in enumerate(batches):
        batch_slug = slug if single_batch else f"{slug}-batch{batch_index + 1}"
        batch_ref_codes = assign_ref_codes(batch, module_title=module_title, existing_codes=used_codes)
        used_codes.update(batch_ref_codes.values())
        all_ref_codes.update(batch_ref_codes)

        notebook_id = ensure_sector_notebook(
            slug=batch_slug, title=f"SOIC L6 -- {module_title}", registry_path=sector_registry_path
        )
        if first_notebook_id is None:
            first_notebook_id = notebook_id

        if reseed:
            lessons_with_codes = [
                {**lesson, "ref_code": batch_ref_codes[lesson["lesson_id"]]} for lesson in batch
            ]
            seed_sector_sources(notebook_id, lessons_with_codes)

        concepts, conversation_id = propose_concepts_via_notebook(
            notebook_id, module_title=module_title, ref_codes=list(set(batch_ref_codes.values())),
            min_concepts=min_concepts, max_concepts=max_concepts,
        )
        all_concepts.extend(concepts)

        for concept in concepts:
            note_text = write_concept_via_notebook(notebook_id, concept, conversation_id=conversation_id)
            concept_slug = slugify_concept_title(concept.title)
            if concept_slug in all_notes:
                n = 2
                while f"{concept_slug}-{n}" in all_notes:
                    n += 1
                concept_slug = f"{concept_slug}-{n}"
            all_notes[concept_slug] = note_text

    return SectorRunResult(
        slug=slug,
        notebook_id=first_notebook_id,
        ref_codes=all_ref_codes,
        concepts=all_concepts,
        notes=all_notes,
    )
