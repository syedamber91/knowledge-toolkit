"""Part 2 (pilot-scope) orchestration: NotebookLM does the synthesis,
this module does only the mechanical plumbing around it.

Sonnet-tier per the NotebookLM-brain plan: REF-code assignment, idempotent
notebook creation/reuse, and source seeding are all deterministic string/IO
work with no judgment call, so they're plain functions with no LLM
involvement whatsoever. The judgment steps (partitioning a sector into
concepts, writing each note, consolidating NotebookLM's answer into the
gates' expected format) are deliberately NOT modeled as functions here --
they're one-off prompt/response exchanges an Opus-tier caller drives
directly via notebook_client.ask_notebook, exactly as the pilot itself was
run.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set, Union

import yaml

from soic_senses.notebook_client import add_text_source, create_notebook

_SUFFIXES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


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
        candidate = base if len(lessons) == 1 else base + _SUFFIXES[i]
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
