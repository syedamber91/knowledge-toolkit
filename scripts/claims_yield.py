#!/usr/bin/env python3
"""Report per-brief claim yield across the extracted corpus.

Reads the raw per-brief extractor output in a directory of ``<REF>.json``
files and prints how many threshold and scope claims each brief produced,
plus corpus totals. Purely descriptive -- it never writes, verifies, or
drops anything; ``assemble_claims.py`` remains the only path into a
verified ``claims.json``.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_dir(path: Path) -> dict[str, list[dict]]:
    """Return {REF: raw claim list} for every ``<REF>.json`` in *path*.

    ``claims.json`` is the assembled output, not a per-brief extraction, so
    it is skipped rather than counted as a 59th brief.
    """
    out: dict[str, list[dict]] = {}
    for f in sorted(path.glob("*.json")):
        if f.stem == "claims":
            continue
        out[f.stem] = json.loads(f.read_text())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims-dir", type=Path, default=Path("out/stage3_claims"))
    ap.add_argument("--empty", action="store_true", help="list only the empty briefs")
    args = ap.parse_args()

    briefs = load_dir(args.claims_dir)
    kinds: Counter[str] = Counter()
    metrics: Counter[str] = Counter()
    empty = []

    rows = []
    for ref, claims in briefs.items():
        c = Counter(x.get("kind") for x in claims)
        kinds.update(c)
        for x in claims:
            if x.get("metric"):
                metrics[x["metric"]] += 1
            for m in x.get("governs_metrics") or []:
                metrics[m] += 1
        if not claims:
            empty.append(ref)
        rows.append((ref, c.get("threshold", 0), c.get("scope", 0)))

    if args.empty:
        print(f"{len(empty)} brief(s) yielded nothing:")
        print("  " + " ".join(empty))
        return 0

    rows.sort(key=lambda r: (-(r[1] + r[2]), r[0]))
    print(f"{'brief':10s} {'thresh':>6s} {'scope':>6s}")
    for ref, t, s in rows:
        if t or s:
            print(f"{ref:10s} {t:6d} {s:6d}")
    print()
    print(f"{len(briefs)} briefs -- {kinds.get('threshold', 0)} threshold, "
          f"{kinds.get('scope', 0)} scope, {len(empty)} brief(s) empty")
    print("\nmetrics touched (claim count):")
    for m, n in metrics.most_common():
        print(f"  {n:4d}  {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
