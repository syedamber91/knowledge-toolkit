#!/usr/bin/env python3
"""Assemble extracted claims into a verified claims.json.

Three steps, in this order and for this reason:

1. LINK. Extractors work one brief at a time, so a scope claim cannot know the
   claim_id of a threshold stated in a different lecture. Each scope therefore
   names the METRIC it governs, and linking happens here, across the whole set.
   That is also what lets a condition stated in one lecture govern a bar stated
   in another -- which is exactly the shape this project is looking for.

2. VERIFY. Every claim's quote is checked against the RAW TRANSCRIPT via the
   (REF, timestamp) pair. Never against the brief it was extracted from:
   checking a copy against itself is how drift stays invisible.

3. DROP. A claim whose quote does not verify is discarded, not repaired. An
   unverifiable claim is not evidence, and quietly fixing one would defeat the
   only guarantee this pipeline offers.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.claims import Claim, save_claims, verify_claim   # noqa: E402
from soic_wiki.ref_crosswalk import Resolver                     # noqa: E402

REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
REPO_ROOT = Path(__file__).resolve().parent.parent
REASSESSMENT_REFS = [
    REPO_ROOT / "docs/reassessment/level-3/refs.json",
    REPO_ROOT / "docs/reassessment/l4/refs.json",
    REPO_ROOT / "docs/reassessment/l5/refs.json",
    REPO_ROOT / "docs/reassessment/crash/refs.json",
]


def main(in_dir: str, out_path: str) -> int:
    raw = []
    for path in sorted(Path(in_dir).glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        raw.extend(rows)
        print(f"  {path.name}: {len(rows)} claim(s)")
    print(f"\n{len(raw)} extracted\n")

    # 1. link scopes to thresholds by metric, across every brief
    by_metric = defaultdict(list)
    for row in raw:
        if row.get("kind") == "threshold" and row.get("metric"):
            by_metric[row["metric"]].append(row["claim_id"])

    claims, malformed = [], []
    for row in raw:
        scopes = []
        for metric in row.pop("governs_metrics", None) or []:
            scopes.extend(by_metric.get(metric, []))
        row["scopes"] = sorted(set(scopes))
        try:
            claims.append(Claim(**row))
        except Exception as exc:                       # schema rejected it
            malformed.append((row.get("claim_id", "?"), str(exc).split("\n")[0]))

    if malformed:
        print(f"{len(malformed)} rejected by the schema:")
        for cid, why in malformed:
            print(f"    {cid}: {why}")
        print()

    # 2 + 3. verify against raw transcripts; drop what does not verify
    resolver = Resolver(REFS, CONTENT, extra_refs=REASSESSMENT_REFS)
    kept, dropped = [], []
    for claim in claims:
        (kept if verify_claim(claim, resolver) else dropped).append(claim)

    print(f"{len(kept)} verified, {len(dropped)} dropped\n")
    for claim in dropped:
        print(f"    DROPPED {claim.claim_id} ({claim.ref} {claim.ts})")

    linked = sum(1 for c in kept if c.kind == "scope" and c.scopes)
    orphan = sum(1 for c in kept if c.kind == "scope" and not c.scopes)
    print(f"\nkept: {sum(1 for c in kept if c.kind == 'threshold')} threshold, "
          f"{sum(1 for c in kept if c.kind == 'scope')} scope "
          f"({linked} linked to a threshold, {orphan} governing nothing found)")

    save_claims(Path(out_path), kept)
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
