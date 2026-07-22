"""Acceptance report for a NEW sector module (no enrichment oracle exists).

Unlike A2's sector-analysis-framework pilot, these modules have no prior
enrichment file to check denials/span-recall against (oracle T2/T4 don't
generalize). What DOES generalize, and is checked here:

  G1  frequency gates (hapax + summary-inflation) over UNCITED phrases only
  G2  cited-quote verification: does each (REF HH:MM:SS)-cited phrase
      actually appear in the lesson it cites?
  G3  zero citations from ineligible lessons
  G4  hollow-admission count (informational -- no prior-wiki baseline exists
      for a topic that has never been synthesized before)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soic_method.corpus import load_corpus  # noqa: E402
from soic_method.eligibility import apply_eligibility, load_eligibility  # noqa: E402
from soic_wiki.gates import (CorpusIndex, audit_terms,  # noqa: E402
                             split_cited_quotes, verify_cited_quotes)

ROOT = Path(__file__).resolve().parents[1]
HOLLOW = re.compile(
    r"(source does not|excerpts do not|no (specific|worked|numeric)|"
    r"not stated in the excerpt|does not (give|provide|contain))", re.I)


def report(notes_dir: Path, refs: dict, label: str) -> bool:
    elig = load_eligibility(ROOT / "configs" / "course_eligibility.yaml")
    all_lessons = apply_eligibility(load_corpus(ROOT / "data" / "content.json"), elig)
    eligible_ids = {l.lesson_id for l in all_lessons if l.eligible}
    by_id = {l.lesson_id: l for l in all_lessons}
    ref_to_lesson = {r: by_id[lid] for lid, r in refs.items()}
    index = CorpusIndex(all_lessons)

    notes = {f.stem: f.read_text(encoding="utf-8") for f in sorted(notes_dir.glob("*.md"))}
    print("notes on disk: %d" % len(notes))

    total_cited = total_verified = 0
    flagged = {}
    hollow = 0
    bad_lesson_cites = set()
    for slug, text in notes.items():
        checks = verify_cited_quotes(text, ref_to_lesson)
        total_cited += len(checks)
        total_verified += sum(c.verified for c in checks)
        parts = split_cited_quotes(text)
        stats = audit_terms(parts["uncited"], all_lessons, index=index)
        for t, s in stats.items():
            if s.suspect:
                flagged.setdefault(t, []).append(slug)
        hollow += len(HOLLOW.findall(text))
        for m in re.finditer(r"\(([A-Z][A-Z0-9]*)\s+\d{2}:\d{2}:\d{2}", text):
            lesson = ref_to_lesson.get(m.group(1))
            if lesson is not None and lesson.lesson_id not in eligible_ids:
                bad_lesson_cites.add((slug, m.group(1)))

    g2 = total_cited == 0 or total_verified / total_cited >= 0.80
    g3 = not bad_lesson_cites

    print()
    print("=" * 66)
    print("SECTOR ACCEPTANCE REPORT — %s" % label)
    print("=" * 66)
    print("G2 cited-quote verification : %d/%d (%.0f%%) -> %s"
          % (total_verified, total_cited,
             100.0 * total_verified / max(total_cited, 1),
             "PASS" if g2 else "FAIL"))
    print("G3 ineligible-lesson cites  : %d -> %s"
          % (len(bad_lesson_cites), "PASS" if g3 else "FAIL"))
    for slug, ref in bad_lesson_cites:
        print("     BAD CITE: %s cites ineligible ref %s" % (slug, ref))
    print("G1 uncited terms flagged    : %d (informational + adjudicate)"
          % len(flagged))
    for t, slugs in sorted(flagged.items()):
        print("     %r in %s" % (t, ",".join(slugs)))
    print("G4 hollow admissions        : %d (informational, no baseline)" % hollow)

    verdict = g2 and g3
    print()
    print("VERDICT: %s" % ("PASS" if verdict else "FAIL"))
    return verdict


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("notes_dir", type=Path)
    p.add_argument("refs_json", type=Path)
    p.add_argument("--label", default="")
    args = p.parse_args()
    ok = report(args.notes_dir, json.loads(args.refs_json.read_text()), args.label)
    raise SystemExit(0 if ok else 1)
