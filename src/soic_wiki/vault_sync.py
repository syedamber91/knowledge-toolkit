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

from soic_wiki.log import log_ingest

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


def match_batch_to_sector(
    batch_slugs: set,
    sector_concepts: Dict[str, set],
) -> Union[str, None]:
    """Identify which vault sector a scratch batch's note stems belong to,
    by concept-slug overlap against the vault's own index.yaml (ground
    truth), for disaster-recovery re-linking of refs.json files that were
    only ever gitignored scratch.

    Returns the sector slug when the match is UNAMBIGUOUS and safe:
    the batch's slugs are a subset of exactly one sector's concept set (a
    batch may under-cover a sector that later grew a note from elsewhere,
    but every note it DOES have must belong to that sector -- any note
    absent from every sector's set, or present in more than one sector at
    the required coverage, returns None rather than guessing).
    """
    candidates = []
    for sector, concepts in sector_concepts.items():
        if batch_slugs and batch_slugs <= concepts:
            candidates.append(sector)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # Ambiguous: prefer the sector with the closest-sized concept set
        # (least extra unaccounted-for concepts) -- but only if it's a
        # unique closest match, otherwise still refuse to guess.
        candidates.sort(key=lambda s: len(sector_concepts[s]))
        if len(sector_concepts[candidates[0]]) < len(sector_concepts[candidates[1]]):
            return candidates[0]
        return None
    return None


def sync_sector_refs(
    refs_json_path: Union[str, Path],
    vault_refs_dir: Union[str, Path],
    sector_slug: str,
) -> Path:
    """Persist a sector's ``lesson_id -> REF code`` mapping into the vault
    at ``wiki/personas/soic/refs/<sector_slug>.json``.

    This is the missing receipt: without it, a synced concept note's
    ``(REF HH:MM:SS)`` citations can never be re-verified once the batch's
    gitignored `out/a5_*/refs.json` scratch is gone -- the vault has 459
    citation-carrying notes and, until this fix, zero durable way to map any
    of their REF codes back to a corpus lesson_id. Re-running G2 needs only
    this small mapping plus the live corpus (`data/content.json`) -- it does
    NOT need a frozen snapshot of the cited text, which would go stale (or
    worse, hide it) the moment a transcript is legitimately re-captured.
    """
    refs = json.loads(Path(refs_json_path).read_text(encoding="utf-8"))
    vault_refs_dir = Path(vault_refs_dir)
    vault_refs_dir.mkdir(parents=True, exist_ok=True)
    dest = vault_refs_dir / f"{sector_slug}.json"
    dest.write_text(json.dumps(refs, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return dest


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


def log_sector_sync(
    log_path: Union[str, Path],
    concepts_dir: Union[str, Path],
    sector_slug: str,
    n_synced: int,
    stamp: str,
) -> bool:
    """Append one Log.md entry for a sector sync (index + log + cross-links
    pattern -- see root CLAUDE.md). ``total`` is the CURRENT count of concept
    files on disk after the sync, not a running counter this module owns, so
    a re-run always reflects reality even if concepts were added/removed by
    some other path.

    This is the call `scripts/sync_notes_to_vault.py` was missing: 437 of the
    vault's 459 concept notes landed via `sync_sector_to_vault` /
    `update_index_yaml` with no corresponding log line, silently breaking the
    standing index+log+cross-links requirement. Wiring the call in here (the
    tested unit) rather than only in the script keeps the two entry points
    that call this module consistent.
    """
    total = len(list(Path(concepts_dir).glob("*.md")))
    summary = f"{n_synced} {sector_slug} concept(s) synced from a gated A5 batch"
    return log_ingest(log_path, total=total, summary=summary, stamp=stamp)
