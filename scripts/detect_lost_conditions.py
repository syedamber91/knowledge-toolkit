#!/usr/bin/env python3
# scripts/detect_lost_conditions.py
"""Report rules applying a number outside the range their source gave it.

Reports only. Applying a fix is a human decision -- every finding names the
lecture and timestamp so the source can be read directly.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.claims import load_claims                    # noqa: E402
from soic_wiki.lost_conditions import find_lost_conditions   # noqa: E402

DEFAULT_RULEBOOK = Path.home() / (
    "Documents/workspace/Claude_Code/soic-ladder/rulebook/"
    "soic-ladder-rules-v1.yaml")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", required=True, help="path to claims.json")
    parser.add_argument("--rulebook", default=str(DEFAULT_RULEBOOK))
    args = parser.parse_args()

    claims = load_claims(Path(args.claims))
    findings = find_lost_conditions(Path(args.rulebook), claims)

    print(f"{len(claims)} claims; {len(findings)} rule(s) missing a scope\n")
    for f in findings:
        print(f"{f.rule_id}")
        print(f"    source attached: {f.scope_statement}")
        print(f"    cited at:        {f.ref} {f.ts}")
        print(f"    threshold claim: {f.threshold_claim_id}\n")
    if not findings:
        print("No rule is applying a number outside its source's stated range.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
