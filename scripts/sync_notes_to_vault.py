#!/usr/bin/env python3
"""CLI: sync one gated A5 sector batch's notes into the vault repo.

Usage:
    python3 scripts/sync_notes_to_vault.py \
        --notes-dir out/a5_lgd/notes \
        --refs out/a5_lgd/refs.json \
        --module-title "Lab Grown Diamonds Sector Analysis" \
        --sector-slug lgd-sector-analysis \
        --vault-root "/path/to/Learning Vault Invest" \
        --last-updated 2026-07-26

Pure orchestration around soic_wiki.vault_sync's tested functions -- no
LLM call, mechanical (Sonnet-tier per the NotebookLM-brain plan).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.vault_sync import (  # noqa: E402
    ConceptSlugCollisionError,
    build_topic_file,
    sync_sector_to_vault,
    update_index_yaml,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--notes-dir", required=True)
    p.add_argument("--refs", required=True)
    p.add_argument("--module-title", required=True)
    p.add_argument("--sector-slug", required=True)
    p.add_argument("--vault-root", required=True)
    p.add_argument("--last-updated", required=True)
    args = p.parse_args()

    vault_root = Path(args.vault_root)
    concepts_dir = vault_root / "wiki" / "personas" / "soic" / "concepts"
    topics_dir = vault_root / "wiki" / "personas" / "soic" / "topics"
    index_path = vault_root / "wiki" / "personas" / "soic" / "index.yaml"
    topics_dir.mkdir(parents=True, exist_ok=True)

    try:
        written = sync_sector_to_vault(
            notes_dir=args.notes_dir,
            refs_json_path=args.refs,
            module_title=args.module_title,
            sector_slug=args.sector_slug,
            vault_concepts_dir=concepts_dir,
            last_updated=args.last_updated,
        )
    except ConceptSlugCollisionError as exc:
        print(f"COLLISION: {exc}", file=sys.stderr)
        return 1

    concept_slugs = [path.stem for path in written]

    topic_path = topics_dir / f"{args.sector_slug}.md"
    topic_path.write_text(
        build_topic_file(
            sector_slug=args.sector_slug,
            module_title=args.module_title,
            concept_slugs=concept_slugs,
            last_updated=args.last_updated,
        ),
        encoding="utf-8",
    )

    update_index_yaml(
        index_path=index_path,
        sector_slug=args.sector_slug,
        topic_file=f"topics/{args.sector_slug}.md",
        concept_slugs=concept_slugs,
        last_updated=args.last_updated,
    )

    print(f"Synced {len(written)} concepts for {args.sector_slug!r}: "
          f"{', '.join(concept_slugs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
