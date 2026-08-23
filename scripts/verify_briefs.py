#!/usr/bin/env python3
"""Quote gate for lecture crux briefs.

Reuses soic_wiki.gates.verify_cited_quotes -- the SAME check every prior
sector batch and the framework-evolution pass ran. Swap the brain, keep the
judge: a brief is prose written by a subagent, and the only thing standing
between a plausible-sounding invented SOIC rule and the rulebook is whether
its quoted text is actually present in the transcript it cites.

refs.json maps REF -> {"slug", "lesson_id", "title"}. Resolution is by
``lesson_id``, NOT by title: four separate courses (L1/L2/L3/L4) each contain a
lesson titled "What you will Learn in this Course? Intro", so a title- or
slug-keyed lookup silently resolves to whichever one happens to land last in the
dict. That bug made a correct VINTRO brief score 0/11 -- it was being checked
against the Technical Analysis course's intro. The lesson_id comes from the
vault note's own ``source_url`` and is unique per lesson.

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

# The write rules mandate annotating garbled ASR as:
#     "one-mebriages" [likely "Varun Beverages"]
# gates._QUOTED then extracts the ANNOTATION's own quoted text as a second,
# separate claim and presence-checks it -- so "Varun Beverages" is reported
# unverified even though the reader never claimed the transcript says it. The
# checker penalises compliance with its own convention. Strip bracketed spans
# before extraction so only the real quote is tested. gates.py itself is left
# untouched: its output is pinned byte-for-byte against committed sector data.
_BRACKETED = re.compile(r"\[[^\]]*\]")


def strip_annotations(text: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", _BRACKETED.sub("", text))

CONTENT_JSON = Path.home() / (
    "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
)
PASS_BAR = 0.80


def main(run_dir: str) -> int:
    run = Path(run_dir)
    refs = json.loads((run / "refs.json").read_text())

    by_id = {le.lesson_id: le for le in load_corpus(CONTENT_JSON)}

    ref_to_lesson, missing = {}, []
    for ref, meta in refs.items():
        le = by_id.get(meta["lesson_id"])
        if le is None:
            missing.append((ref, meta))
        else:
            ref_to_lesson[ref] = le

    if missing:
        print("!! could not resolve these refs to a corpus lesson:")
        for ref, meta in missing:
            print(f"   {ref:8s} lesson_id={meta['lesson_id']} {meta['slug']}")
        print()

    rows, failures = [], []
    for brief in sorted((run / "briefs").glob("*.md")):
        checks = verify_cited_quotes(
            strip_annotations(brief.read_text()), ref_to_lesson
        )
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
