"""Sync gated A5 sector-batch notes from `out/a5_*/notes/` into the vault.

Mechanical, deterministic, no LLM call (Sonnet-tier per the NotebookLM-brain
plan) -- this is pure content migration: `out/a5_*/` is gitignored scratch,
so a note gate-passed by `scripts/sector_report.py` only becomes durable once
it lands here and gets committed in the vault repo.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Union

import yaml

_H1 = re.compile(r"^#\s+(.+?)\s*\n")


class ConceptSlugCollisionError(Exception):
    """Raised when a concept slug being synced already exists in the vault
    under a different sector -- migrating blind would silently overwrite
    someone else's committed content. Caller must resolve the collision
    (rename, merge, or confirm it's the same concept) before retrying.
    """


def _title_case_from_slug(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.replace("_", "-").split("-"))


def normalize_body(text: str, fallback_title: str) -> str:
    """Ensure the note starts with exactly one `## Title` heading.

    A5 note files are inconsistent: some have a leading `# Title` (H1),
    some start directly with `## The mechanism`. The vault's own concept
    files use a single top-level `##` heading, so this normalizes both
    shapes to that convention rather than leaving a mix.
    """
    match = _H1.match(text)
    if match:
        return "## " + match.group(1) + "\n" + text[match.end():]
    return f"## {_title_case_from_slug(fallback_title)}\n\n{text}"


def build_concept_frontmatter(
    slug: str,
    module_title: str,
    ref_code: str,
    sector_slug: str,
    last_updated: str,
) -> str:
    """Build the YAML frontmatter block for a migrated concept file.

    `sources` references the corpus module + REF code rather than a
    `raw/<slug>/*.md` path (unlike the original pilot topic) -- the A5
    sector batches' raw transcripts were never duplicated into the vault,
    only the gated concept notes are.
    """
    data = {
        "persona": "soic",
        "kind": "concept",
        "sources": [f"SOIC_Scraper corpus — {module_title} (lesson {ref_code})"],
        "last_updated": last_updated,
        "qc": "passed",
        "slug": slug,
        "topics": [sector_slug],
    }
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip() + "\n---\n"


def sync_sector_to_vault(
    notes_dir: Union[str, Path],
    refs_json_path: Union[str, Path],
    module_title: str,
    sector_slug: str,
    vault_concepts_dir: Union[str, Path],
    last_updated: str,
) -> List[Path]:
    """Copy every note in `notes_dir` into `vault_concepts_dir` with
    frontmatter prepended. Raises ConceptSlugCollisionError (naming the
    slug) rather than silently overwriting an existing vault concept file
    from a different sector.
    """
    notes_dir = Path(notes_dir)
    vault_concepts_dir = Path(vault_concepts_dir)
    refs = json.loads(Path(refs_json_path).read_text(encoding="utf-8"))
    ref_code = next(iter(refs.values())) if refs else "UNK"

    note_paths = sorted(notes_dir.glob("*.md"))
    for note_path in note_paths:
        dest = vault_concepts_dir / note_path.name
        if dest.exists():
            raise ConceptSlugCollisionError(
                f"Concept slug {note_path.stem!r} already exists in the vault at {dest} "
                "-- resolve the collision before syncing"
            )

    written = []
    for note_path in note_paths:
        slug = note_path.stem
        body = normalize_body(note_path.read_text(encoding="utf-8"), fallback_title=slug)
        frontmatter = build_concept_frontmatter(
            slug=slug,
            module_title=module_title,
            ref_code=ref_code,
            sector_slug=sector_slug,
            last_updated=last_updated,
        )
        dest = vault_concepts_dir / note_path.name
        dest.write_text(frontmatter + "\n" + body, encoding="utf-8")
        written.append(dest)

    return written


def update_index_yaml(
    index_path: Union[str, Path],
    sector_slug: str,
    topic_file: str,
    concept_slugs: List[str],
    last_updated: str,
) -> None:
    """Add/refresh one topic and its concepts in the vault's index.yaml."""
    index_path = Path(index_path)
    data = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    data.setdefault("topics", {})
    data.setdefault("entities", {})
    data.setdefault("concepts", {})

    data["topics"][sector_slug] = {
        "file": topic_file,
        "sources": len(concept_slugs),
        "last_updated": last_updated,
    }
    for slug in concept_slugs:
        data["concepts"][slug] = {
            "file": f"concepts/{slug}.md",
            "topics": [sector_slug],
            "last_updated": last_updated,
        }

    index_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def build_topic_file(
    sector_slug: str,
    module_title: str,
    concept_slugs: List[str],
    last_updated: str,
) -> str:
    """Build a topic file for a migrated sector: frontmatter + a Related
    wikilink line + a short synthesis note. Deliberately lighter than the
    original pilot topic's per-pair Comparisons/Open-questions sections --
    that richness was a one-off deep pass, not a per-sector requirement,
    and reproducing it for 18 sectors would be exactly the kind of
    heavy Claude-token synthesis this whole redesign exists to avoid.
    """
    data = {
        "persona": "soic",
        "kind": "topic",
        "sources": [f"SOIC_Scraper corpus module — {module_title}"],
        "last_updated": last_updated,
        "qc": "passed",
        "topic": sector_slug,
    }
    frontmatter = "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip() + "\n---\n"

    related = " · ".join(f"[[{slug}]]" for slug in concept_slugs)

    return (
        f"{frontmatter}\n"
        f"Related: {related}\n\n"
        "## Synthesis\n\n"
        f"Concept notes for {module_title}, migrated from a gated A5 sector-batch "
        "synthesis pass (citation-verified against the raw lecture transcripts, "
        "gate-passed via `scripts/sector_report.py`).\n"
    )
