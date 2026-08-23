#!/usr/bin/env python3
"""Quote gate for lecture crux briefs.

Reuses soic_wiki.gates.verify_cited_quotes -- the SAME check every prior
sector batch and the framework-evolution pass ran. Swap the brain, keep the
judge: a brief is prose written by a subagent, and the only thing standing
between a plausible-sounding invented SOIC rule and the rulebook is whether
its quoted text is actually present in the transcript it cites.

Usage:
    python3 scripts/verify_briefs.py out/reassess_l3
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_method.corpus import load_corpus          # noqa: E402
from soic_wiki.gates import verify_cited_quotes      # noqa: E402

CONTENT_JSON = Path.home() / (
    "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
)
PASS_BAR = 0.80


def slugify(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", title.lower())).strip("-")


def main(run_dir: str) -> int:
    run = Path(run_dir)
    refs = json.loads((run / "refs.json").read_text())

    lessons = load_corpus(CONTENT_JSON)
    by_slug = {slugify(le.title): le for le in lessons}

    ref_to_lesson = {}
    missing = []
    for ref, slug in refs.items():
        le = by_slug.get(slug)
        if le is None:
            missing.append((ref, slug))
        else:
            ref_to_lesson[ref] = le

    if missing:
        print("!! could not resolve these refs to a corpus lesson:")
        for ref, slug in missing:
            print(f"   {ref:8s} {slug}")
        print()

    rows, failures = [], []
    for brief in sorted((run / "briefs").glob("*.md")):
        checks = verify_cited_quotes(brief.read_text(), ref_to_lesson)
        total = len(checks)
        ok = sum(1 for c in checks if c.verified)
        pct = (ok / total) if total else 1.0
        status = "PASS" if pct >= PASS_BAR else "FAIL"
        rows.append((brief.stem, ok, total, pct, status))
        if status == "FAIL":
            failures.append(
                (brief.stem, [c.phrase for c in checks if not c.verified])
            )

    print(f"{'BRIEF':10s} {'VERIFIED':>10s} {'PCT':>7s}  STATUS")
    print("-" * 40)
    for stem, ok, total, pct, status in rows:
        print(f"{stem:10s} {ok:4d}/{total:<5d} {pct*100:6.1f}%  {status}")

    if failures:
        print("\nUNVERIFIED QUOTES IN FAILING BRIEFS")
        for stem, phrases in failures:
            print(f"\n  {stem}:")
            for p in phrases[:15]:
                print(f"    - {p!r}")

    n_fail = len(failures)
    print(f"\n{len(rows) - n_fail}/{len(rows)} briefs clear the {PASS_BAR:.0%} bar.")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "out/reassess_l3"))
