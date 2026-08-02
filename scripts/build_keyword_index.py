#!/usr/bin/env python3
"""Generate/refresh the vault's question-shaped keyword index
(wiki/personas/soic/soic-by-keyword.md) from configs/sector_notebooks.yaml,
and make sure soic-home.md links to it.

Re-run any time sector_notebooks.yaml's keywords change or a new sector is
synced -- deterministic, no LLM call, safe to re-run (idempotent overwrite
of the one generated file; the soic-home.md link is added once and never
duplicated on a re-run).

Usage:
    python3 scripts/build_keyword_index.py \\
        --vault-root "/path/to/Learning Vault Invest" \\
        --sector-registry configs/sector_notebooks.yaml \\
        --stamp 2026-08-02
"""

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_senses.sector_router import load_sectors  # noqa: E402
from soic_wiki.keyword_index import build_keyword_index_note  # noqa: E402

_HOME_LINK_LINE = "- [[soic-by-keyword|Browse by Keyword]] -- find a sector by what you're asking about, not which course taught it."


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vault-root", required=True)
    p.add_argument("--sector-registry", default="configs/sector_notebooks.yaml")
    p.add_argument("--stamp", required=True)
    args = p.parse_args()

    vault_root = Path(args.vault_root)
    soic_root = vault_root / "wiki" / "personas" / "soic"
    index_path = soic_root / "index.yaml"

    idx = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    vault_topics = set((idx.get("topics") or {}).keys())

    sectors = load_sectors(args.sector_registry)
    body = build_keyword_index_note(sectors, vault_topics, stamp=args.stamp)

    note_path = soic_root / "soic-by-keyword.md"
    note_path.write_text(body, encoding="utf-8")
    print(f"wrote {note_path}")

    home_path = soic_root / "soic-home.md"
    home_text = home_path.read_text(encoding="utf-8")
    if "soic-by-keyword" not in home_text:
        marker = "## Frameworks"
        if marker in home_text:
            home_text = home_text.replace(
                marker, f"{_HOME_LINK_LINE}\n\n{marker}", 1
            )
        else:
            home_text = home_text.rstrip() + f"\n\n{_HOME_LINK_LINE}\n"
        home_path.write_text(home_text, encoding="utf-8")
        print(f"linked from {home_path}")
    else:
        print(f"{home_path} already links to soic-by-keyword, left unchanged")

    return 0


if __name__ == "__main__":
    sys.exit(main())
