"""Shared sector-acceptance gate logic, extracted from
scripts/sector_report.py so the CLI (soic_wiki.cli) and the standalone
script use the exact same deterministic check -- no duplicated gate logic
across two entry points.

  G1  frequency gates (hapax + summary-inflation) over UNCITED phrases only
  G2  cited-quote verification: does each (REF HH:MM:SS)-cited phrase
      actually appear in the lesson it cites?
  G3  zero citations from ineligible lessons
  G4  hollow-admission count (informational)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Union

from soic_method.corpus import load_corpus
from soic_method.eligibility import apply_eligibility, load_eligibility
from soic_wiki.gates import CorpusIndex, audit_terms, split_cited_quotes, verify_cited_quotes

_HOLLOW = re.compile(
    r"(source does not|excerpts do not|no (specific|worked|numeric)|"
    r"not stated in the excerpt|does not (give|provide|contain))", re.I,
)


@dataclass
class AcceptanceReport:
    verdict: bool
    g2_verified: int
    g2_total: int
    g3_bad_cites: List[Tuple[str, str]] = field(default_factory=list)
    g1_flagged: Dict[str, List[str]] = field(default_factory=dict)
    g4_hollow: int = 0

    @property
    def g2_pct(self) -> float:
        return 100.0 * self.g2_verified / max(self.g2_total, 1)

    @property
    def g2_pass(self) -> bool:
        return self.g2_total == 0 or (self.g2_verified / self.g2_total) >= 0.80

    @property
    def g3_pass(self) -> bool:
        return not self.g3_bad_cites


def run_sector_acceptance_report(
    notes_dir: Union[str, Path],
    refs: Dict[str, str],
    label: str = "",
    repo_root: Union[str, Path, None] = None,
) -> AcceptanceReport:
    """Run G1-G4 against every note in notes_dir, returning a structured
    AcceptanceReport (verdict = G2 AND G3; G1/G4 informational).
    """
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    elig = load_eligibility(root / "configs" / "course_eligibility.yaml")
    all_lessons = apply_eligibility(load_corpus(root / "data" / "content.json"), elig)
    eligible_ids = {l.lesson_id for l in all_lessons if l.eligible}
    by_id = {l.lesson_id: l for l in all_lessons}
    ref_to_lesson = {r: by_id[lid] for lid, r in refs.items() if lid in by_id}
    index = CorpusIndex(all_lessons)

    notes = {f.stem: f.read_text(encoding="utf-8") for f in sorted(Path(notes_dir).glob("*.md"))}

    total_cited = total_verified = 0
    flagged: Dict[str, List[str]] = {}
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
        hollow += len(_HOLLOW.findall(text))
        for m in re.finditer(r"\(([A-Z][A-Z0-9]*)\s+\d{2}:\d{2}:\d{2}", text):
            lesson = ref_to_lesson.get(m.group(1))
            if lesson is not None and lesson.lesson_id not in eligible_ids:
                bad_lesson_cites.add((slug, m.group(1)))

    g2 = total_cited == 0 or total_verified / total_cited >= 0.80
    g3 = not bad_lesson_cites

    return AcceptanceReport(
        verdict=g2 and g3,
        g2_verified=total_verified,
        g2_total=total_cited,
        g3_bad_cites=sorted(bad_lesson_cites),
        g1_flagged=flagged,
        g4_hollow=hollow,
    )


def print_report(report: AcceptanceReport, label: str = "") -> None:
    """Render an AcceptanceReport in the exact same format
    scripts/sector_report.py has always printed, for terminal use."""
    print("=" * 66)
    print("SECTOR ACCEPTANCE REPORT — %s" % label)
    print("=" * 66)
    print("G2 cited-quote verification : %d/%d (%.0f%%) -> %s"
          % (report.g2_verified, report.g2_total, report.g2_pct, "PASS" if report.g2_pass else "FAIL"))
    print("G3 ineligible-lesson cites  : %d -> %s"
          % (len(report.g3_bad_cites), "PASS" if report.g3_pass else "FAIL"))
    for slug, ref in report.g3_bad_cites:
        print("     BAD CITE: %s cites ineligible ref %s" % (slug, ref))
    print("G1 uncited terms flagged    : %d (informational + adjudicate)" % len(report.g1_flagged))
    for t, slugs in sorted(report.g1_flagged.items()):
        print("     %r in %s" % (t, ",".join(slugs)))
    print("G4 hollow admissions        : %d (informational, no baseline)" % report.g4_hollow)
    print()
    print("VERDICT: %s" % ("PASS" if report.verdict else "FAIL"))
