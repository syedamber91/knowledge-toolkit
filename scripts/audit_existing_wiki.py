"""Increment 0: audit the EXISTING persona wiki. Zero LLM calls.

Runs the frequency gates against the 22 concept notes currently live in
`learning-vault-invest`, using the real corpus as ground truth. Establishes
the before-numbers for the rebuild's A/B and proves the detector works on real
notes before a single token is spent on regeneration.

Notes are read via `gh` rather than the local iCloud clone, so this runs in
sandboxed, remote and cloud sessions too.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soic_method.corpus import load_corpus
from soic_method.eligibility import apply_eligibility, load_eligibility
from soic_wiki.gates import CorpusIndex, audit_terms, candidate_terms

REPO = "syedamber91/learning-vault-invest"
CONCEPTS = "wiki/personas/soic/concepts"
TOPIC_NOTE = "wiki/personas/soic/topics/sector-analysis-framework.md"
ROOT = Path(__file__).resolve().parents[1]


def gh(path: str) -> str:
    out = subprocess.run(
        ["gh", "api", "repos/%s/contents/%s" % (REPO, path), "--jq", ".content"],
        capture_output=True, text=True, check=True,
    ).stdout
    import base64
    return base64.b64decode(out).decode("utf-8")


def gh_list(prefix: str):
    out = subprocess.run(
        ["gh", "api", "repos/%s/git/trees/HEAD?recursive=1" % REPO,
         "--jq", '.tree[] | select(.type=="blob") | .path'],
        capture_output=True, text=True, check=True,
    ).stdout
    return [p for p in out.splitlines() if p.startswith(prefix) and p.endswith(".md")]


def main() -> int:
    print("Loading corpus + eligibility ...")
    elig = load_eligibility(ROOT / "configs" / "course_eligibility.yaml")
    lessons = apply_eligibility(load_corpus(ROOT / "data" / "content.json"), elig)
    index = CorpusIndex(lessons)
    print("  eligible lessons: %d" % len(index))

    print("Fetching existing concept notes ...")
    paths = gh_list(CONCEPTS)
    notes = {p.rsplit("/", 1)[-1][:-3]: gh(p) for p in paths}
    print("  notes: %d" % len(notes))

    # --- baseline: source-gap markers in the topic note --------------------
    topic = gh(TOPIC_NOTE)
    gap_markers = len(re.findall(r"source gap", topic, re.I))

    # --- gate every candidate term in every note ---------------------------
    per_note = {}
    all_terms = set()
    for slug, text in notes.items():
        terms = candidate_terms(text)
        per_note[slug] = terms
        all_terms.update(terms)
    print("  candidate terms: %d unique across all notes" % len(all_terms))

    print("Auditing terms against the corpus ...")
    stats = audit_terms(sorted(all_terms), lessons, index=index)

    flagged = {t: s for t, s in stats.items() if s.suspect}

    print()
    print("=" * 78)
    print("INCREMENT 0 BASELINE — existing wiki audited against the real corpus")
    print("=" * 78)
    print("eligible lessons          : %d" % len(index))
    print("concept notes             : %d" % len(notes))
    print("source-gap markers        : %d   (topic note)" % gap_markers)
    print("candidate terms           : %d" % len(all_terms))
    print("FLAGGED as likely artifact: %d" % len(flagged))
    print()

    if flagged:
        print("%-38s %5s %8s %8s  %s" % ("term", "body", "lessons", "summary", "flags"))
        print("-" * 78)
        for t, s in sorted(flagged.items(), key=lambda kv: (kv[1].lesson_n, kv[0])):
            owners = [n for n, ts in per_note.items() if t in ts]
            print("%-38s %5d %8d %8d  %s" % (t, s.body_n, s.lesson_n, s.summary_n,
                                             ",".join(s.flags)))
            print("%-38s   in: %s" % ("", ", ".join(owners[:3])))

    out = ROOT / "out" / "inc0-baseline.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "eligible_lessons": len(index),
        "notes": len(notes),
        "source_gap_markers": gap_markers,
        "candidate_terms": len(all_terms),
        "flagged": {t: s.model_dump(exclude={"example_window"})
                    for t, s in flagged.items()},
        "per_note_terms": per_note,
    }, indent=2), encoding="utf-8")
    print()
    print("baseline written to %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
