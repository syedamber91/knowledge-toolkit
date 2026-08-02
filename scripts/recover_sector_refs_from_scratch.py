#!/usr/bin/env python3
"""Disaster recovery: reconstruct a sector's lesson_id -> REF mapping from
ANY leftover `out/a5_*/refs.json` scratch that still happens to be on disk
(e.g. a stale git worktree, an old checkout), and persist it into the vault
at wiki/personas/soic/refs/<sector_slug>.json.

Why this exists: `sync_notes_to_vault.py` synced 459 concept notes into the
vault citing `(REF HH:MM:SS)` timestamps, but the `lesson_id -> REF` mapping
that makes those citations re-verifiable only ever lived in `out/a5_*/`,
which is gitignored scratch -- committed nowhere, on one machine. This
script is the one-time repair for the sectors synced before
`sync_sector_refs` was wired into the sync path (2026-08-02); every sync
from that point on persists its own refs automatically and never needs this.

Matching is via concept-slug overlap against the vault's OWN index.yaml
(ground truth of what's actually synced) -- see
soic_wiki.vault_sync.match_batch_to_sector for the exact rule (unambiguous
subset match only; refuses to guess and reports anything it can't confirm).

Usage:
    # Dry run (default): report matches/skips, write nothing.
    python3 scripts/recover_sector_refs_from_scratch.py \\
        --scratch-root /path/to/old/worktree \\
        --vault-root "/path/to/Learning Vault Invest"

    # Apply: write the recovered refs/*.json files.
    python3 scripts/recover_sector_refs_from_scratch.py \\
        --scratch-root /path/to/old/worktree \\
        --vault-root "/path/to/Learning Vault Invest" \\
        --apply
"""

import argparse
import collections
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.vault_sync import match_batch_to_sector, sync_sector_refs  # noqa: E402


def _sector_concepts(index_path: Path) -> dict:
    idx = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    out = collections.defaultdict(set)
    for slug, meta in (idx.get("concepts") or {}).items():
        for t in meta.get("topics", []):
            out[t].add(slug)
    return dict(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scratch-root", required=True, help="Root to search for out/**/refs.json")
    p.add_argument("--vault-root", required=True)
    p.add_argument("--apply", action="store_true", help="Write refs files (default: dry-run report only)")
    args = p.parse_args()

    scratch_root = Path(args.scratch_root)
    vault_root = Path(args.vault_root)
    index_path = vault_root / "wiki" / "personas" / "soic" / "index.yaml"
    refs_dir = vault_root / "wiki" / "personas" / "soic" / "refs"

    sector_concepts = _sector_concepts(index_path)
    print(f"vault has {len(sector_concepts)} topics with synced concepts")

    already = {p.stem for p in refs_dir.glob("*.json")} if refs_dir.is_dir() else set()

    notes_dirs = sorted(scratch_root.glob("**/notes"))
    matched, skipped_existing, unmatched = [], [], []

    for nd in notes_dirs:
        refs_path = nd.parent / "refs.json"
        if not refs_path.exists():
            continue
        batch_slugs = {f.stem for f in nd.glob("*.md")}
        sector = match_batch_to_sector(batch_slugs, sector_concepts)
        if sector is None:
            unmatched.append(str(nd.relative_to(scratch_root)))
            continue
        if sector in already:
            skipped_existing.append((str(nd.relative_to(scratch_root)), sector))
            continue
        matched.append((str(nd.relative_to(scratch_root)), sector, refs_path))

    print(f"\nconfident matches ready to recover: {len(matched)}")
    for rel, sector, _ in matched:
        print(f"  {rel}  ->  refs/{sector}.json")

    if skipped_existing:
        print(f"\nalready have a refs file (skipped): {len(skipped_existing)}")
        for rel, sector in skipped_existing:
            print(f"  {rel}  ->  refs/{sector}.json (exists)")

    if unmatched:
        print(f"\ncould not confidently match (left uncovered, none guessed): {len(unmatched)}")
        for rel in unmatched:
            print(f"  {rel}")

    covered = {m[1] for m in matched} | {s for _, s in skipped_existing}
    uncovered_sectors = sorted(set(sector_concepts) - covered)
    print(f"\nvault topics covered after this run: {len(covered)}/{len(sector_concepts)}")
    if uncovered_sectors:
        print("still uncovered:", ", ".join(uncovered_sectors))

    if not args.apply:
        print("\nDRY RUN -- no files written. Re-run with --apply to persist the matches above.")
        return 0

    for _, sector, refs_path in matched:
        dest = sync_sector_refs(refs_path, refs_dir, sector)
        print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
