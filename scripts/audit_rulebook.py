#!/usr/bin/env python3
"""Print a per-rule citation audit of the soic-ladder rulebook (D13).

Structural check only: does each rule's REF code resolve to a lesson (via
the (ref, timestamp) pair, never by ref alone or by guessing what the code's
letters abbreviate), and does the cited timestamp actually appear in that
lesson's transcript? The rulebook's `provenance.quote` is the author's
paraphrase, not transcript text, so this never attempts a verbatim match.

Exit code: 1 if any citation is UNRESOLVED_REF or BAD_TIMESTAMP -- a genuine
citation defect. NO_REF (no ref was ever recorded, e.g. pe_context-001)
does NOT set exit 1 on its own: it is a known, already-documented gap, not
a broken citation to a real-but-wrong place. A clean run against the
current rulebook (one NO_REF row, nothing else) exits 0.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.citation_audit import audit          # noqa: E402
from soic_wiki.ref_crosswalk import Resolver        # noqa: E402

REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
RULEBOOK = Path.home() / (
    "Documents/workspace/Claude_Code/soic-ladder/rulebook/soic-ladder-rules-v1.yaml")


def main() -> int:
    checks = audit(RULEBOOK, Resolver(REFS, CONTENT))
    width = max(len(c.rule_id) for c in checks)
    print(f"{'RULE':{width}}  {'STATUS':14}  REF -> LESSON")
    print("-" * (width + 60))
    for c in checks:
        tail = f"{c.ref or '(none)'}"
        if c.lesson_title:
            tail += f"  ->  {c.lesson_title[:44]}"
        if c.status == "BAD_TIMESTAMP" and c.nearby:
            tail += f"   nearby: {', '.join(c.nearby[:4])}"
        print(f"{c.rule_id:{width}}  {c.status:14}  {tail}")
    bad = [c for c in checks if c.status != "OK"]
    print(f"\n{len(checks) - len(bad)}/{len(checks)} citations resolve to a real "
          f"timestamp in a real lesson.")
    for c in bad:
        print(f"  {c.status:14} {c.rule_id}")
    return 1 if any(c.status in ("UNRESOLVED_REF", "BAD_TIMESTAMP") for c in bad) else 0


if __name__ == "__main__":
    raise SystemExit(main())
