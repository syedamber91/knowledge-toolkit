"""Mirror `configs/sector_notebooks.yaml`'s human-curated `keywords:` lists
-- the SAME registry `soic_senses.sector_router` uses for live routing --
into a vault note, so a human reading the vault directly gets the
question-shaped front door too, not just the course-level one.

`wiki/personas/soic/soic-home.md` groups every topic by COURSE LEVEL (Level
2 Intensive, Level 3 Valuation, L4 Technicals, ...) -- the shape of the
curriculum. Nobody asks "what's in Level 4?"; they ask "what should I check
before buying an NBFC?" or "what does he say about backward integration?".
The sector_notebooks.yaml keyword lists already answer exactly that
question for `decision_engine.build_briefing`'s live routing -- this module
just renders the SAME data as a second, question-shaped index note.

Never invents a keyword: only renders what's already curated. Also reports
(does not fix) two gaps this surfaces as a byproduct of cross-referencing
the registry against the vault's own index.yaml (ground truth of what's
actually synced):

  - vault topics with NO entry in the registry at all (undiscoverable by
    sector_router no matter what keywords you'd search for)
  - registry entries THAT DO map to a real vault topic but have an empty
    `keywords:` list (present, but unreachable by any query)

Both are content-curation decisions for a human, not something this module
guesses on their behalf -- `keywords:` is explicitly human-curated per the
sector_notebooks.yaml header comment.
"""

from __future__ import annotations

from typing import Dict, List, Set

from soic_senses.sector_router import Sector


def build_keyword_index_note(sectors: List[Sector], vault_topics: Set[str], stamp: str) -> str:
    """Render the question-shaped index note's full markdown body
    (frontmatter + keyword browse table + a gaps-found section)."""
    keyword_to_slugs: Dict[str, List[str]] = {}
    for s in sectors:
        if s.slug not in vault_topics or not s.keywords:
            continue
        for kw in s.keywords:
            keyword_to_slugs.setdefault(kw, []).append(s.slug)

    registry_slugs = {s.slug for s in sectors}
    covered_slugs = sorted(
        {s.slug for s in sectors if s.slug in vault_topics and s.keywords}
    )
    uncovered_vault_topics = sorted(vault_topics - registry_slugs)
    zero_keyword_entries = sorted(
        s.slug for s in sectors if s.slug in vault_topics and not s.keywords
    )
    stale_registry_entries = sorted(registry_slugs - vault_topics)

    lines = [
        "---",
        "persona: soic",
        "kind: moc",
        "slug: soic-by-keyword",
        f"last_updated: '{stamp}'",
        "---",
        "",
        "## SOIC -- Browse by Keyword",
        "",
        "Question-shaped front door: find a sector by what you're actually asking "
        "about, rather than by which course level taught it "
        "(see [[soic-home|the course-level index]] for that view). Mirrors the "
        "SAME human-curated `keywords:` registry "
        "(`configs/sector_notebooks.yaml`) that `soic_senses.sector_router` uses "
        f"for live briefing routing -- {len(covered_slugs)} of {len(vault_topics)} "
        "vault topics have curated keywords as of this generation.",
        "",
        "## Browse by keyword",
        "",
    ]
    for kw in sorted(keyword_to_slugs, key=str.casefold):
        slugs = sorted(set(keyword_to_slugs[kw]))
        links = " · ".join(f"[[{slug}]]" for slug in slugs)
        lines.append(f"- **{kw}** — {links}")

    lines += [
        "",
        "## Gaps found (reported, not fixed -- `keywords:` is human-curated)",
        "",
        f"- **{len(uncovered_vault_topics)} vault topic(s) have no registry entry at all** "
        "(undiscoverable by sector_router regardless of query): "
        + (", ".join(f"`{s}`" for s in uncovered_vault_topics) if uncovered_vault_topics else "none"),
        f"- **{len(zero_keyword_entries)} registry entries map to a real vault topic but have "
        "an empty `keywords:` list** (present in the registry, unreachable by any query): "
        + (", ".join(f"`{s}`" for s in zero_keyword_entries) if zero_keyword_entries else "none"),
        f"- **{len(stale_registry_entries)} registry entries have no matching vault topic** "
        "(likely superseded/renamed batches): "
        + (", ".join(f"`{s}`" for s in stale_registry_entries) if stale_registry_entries else "none"),
    ]
    return "\n".join(lines) + "\n"
