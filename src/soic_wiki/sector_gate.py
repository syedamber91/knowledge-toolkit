"""Shared sector-acceptance gate logic, extracted from
scripts/sector_report.py so the CLI (soic_wiki.cli) and the standalone
script use the exact same deterministic check -- no duplicated gate logic
across two entry points.

  G1  frequency gates (hapax + summary-inflation) over UNCITED phrases only
  G2  cited-quote verification: does each (REF HH:MM:SS)-cited phrase
      actually appear in the lesson it cites?
  G3  zero citations from ineligible lessons
  G4  hollow-admission count (informational)

G2 THRESHOLDS -- raised 2026-08-02 after a review of the strategy found the
gate looser than the work it was actually gating: every batch run this
session landed at 91-100% G2, so an 80% bar was tolerating a failure rate
the pipeline had never once produced. Two thresholds now apply, not one:

  - AGGREGATE (across every cited quote in the batch) must be >= 90%.
  - PER-NOTE: no single note's own cited-quote pass rate may fall below
    60%, even when the batch-wide aggregate clears 90% -- an aggregate-only
    gate lets one badly-hallucinated note hide behind several clean ones in
    the same sector (e.g. 3 notes at 100% + 1 note at 20% still averages
    well above the old 80% floor). Both must hold for verdict to be True.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from soic_method.corpus import load_corpus
from soic_method.eligibility import apply_eligibility, load_eligibility
from soic_wiki.gates import CorpusIndex, audit_terms, split_cited_quotes, verify_cited_quotes

_HOLLOW = re.compile(
    r"(source does not|excerpts do not|no (specific|worked|numeric)|"
    r"not stated in the excerpt|does not (give|provide|contain))", re.I,
)

G2_AGGREGATE_THRESHOLD = 0.90
G2_MIN_NOTE_THRESHOLD = 0.60


@dataclass
class AcceptanceReport:
    verdict: bool
    g2_verified: int
    g2_total: int
    g3_bad_cites: List[Tuple[str, str]] = field(default_factory=list)
    g1_flagged: Dict[str, List[str]] = field(default_factory=dict)
    g4_hollow: int = 0
    g2_per_note: Dict[str, Tuple[int, int]] = field(default_factory=dict)  # slug -> (verified, total)

    @property
    def g2_pct(self) -> float:
        return 100.0 * self.g2_verified / max(self.g2_total, 1)

    @property
    def g2_worst_notes(self) -> List[Tuple[str, float]]:
        """Notes whose OWN cited-quote pass rate falls below the per-note
        floor, sorted worst-first. A note with zero citations isn't at
        risk here (nothing to verify) and is excluded."""
        out = []
        for slug, (verified, total) in self.g2_per_note.items():
            if total > 0 and (verified / total) < G2_MIN_NOTE_THRESHOLD:
                out.append((slug, round(100.0 * verified / total, 1)))
        return sorted(out, key=lambda x: x[1])

    @property
    def g2_pass(self) -> bool:
        aggregate_ok = self.g2_total == 0 or (self.g2_verified / self.g2_total) >= G2_AGGREGATE_THRESHOLD
        return aggregate_ok and not self.g2_worst_notes

    @property
    def g3_pass(self) -> bool:
        return not self.g3_bad_cites


def run_sector_acceptance_report(
    notes_dir: Union[str, Path, None],
    refs: Dict[str, str],
    label: str = "",
    repo_root: Union[str, Path, None] = None,
    notes: Optional[Dict[str, str]] = None,
) -> AcceptanceReport:
    """Run G1-G4 against a set of notes, returning a structured
    AcceptanceReport (verdict = G2 AND G3; G1/G4 informational).

    Pass ``notes_dir`` (globs every ``*.md`` in that directory) for the
    original A5-batch use (notes freshly written to `out/a5_*/notes/`, one
    directory per sector). Pass a pre-assembled ``notes`` dict of
    ``{slug: text}`` instead when the notes to check are scattered across a
    shared directory that isn't per-sector -- e.g. the live vault's flat
    `wiki/personas/soic/concepts/`, used by the drift-check audit
    (`scripts/audit_vault_sectors.py`) to re-verify one sector's already-
    synced notes without a directory boundary to glob.
    """
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    elig = load_eligibility(root / "configs" / "course_eligibility.yaml")
    all_lessons = apply_eligibility(load_corpus(root / "data" / "content.json"), elig)
    eligible_ids = {l.lesson_id for l in all_lessons if l.eligible}
    by_id = {l.lesson_id: l for l in all_lessons}
    ref_to_lesson = {r: by_id[lid] for lid, r in refs.items() if lid in by_id}
    index = CorpusIndex(all_lessons)

    if notes is None:
        notes = {f.stem: f.read_text(encoding="utf-8") for f in sorted(Path(notes_dir).glob("*.md"))}

    total_cited = total_verified = 0
    per_note: Dict[str, Tuple[int, int]] = {}
    flagged: Dict[str, List[str]] = {}
    hollow = 0
    bad_lesson_cites = set()
    for slug, text in notes.items():
        checks = verify_cited_quotes(text, ref_to_lesson)
        note_verified = sum(c.verified for c in checks)
        per_note[slug] = (note_verified, len(checks))
        total_cited += len(checks)
        total_verified += note_verified
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

    report = AcceptanceReport(
        verdict=False,  # set below, once g2_pass/g3_pass can see the full report
        g2_verified=total_verified,
        g2_total=total_cited,
        g3_bad_cites=sorted(bad_lesson_cites),
        g1_flagged=flagged,
        g4_hollow=hollow,
        g2_per_note=per_note,
    )
    report.verdict = report.g2_pass and report.g3_pass
    return report


def print_report(
    report: AcceptanceReport, label: str = "", adjudications: Optional[Dict[str, dict]] = None
) -> None:
    """Render an AcceptanceReport in the exact same format
    scripts/sector_report.py has always printed, for terminal use.

    Pass ``adjudications`` (from `soic_wiki.adjudication.load_adjudications`)
    to split G1 output into "already adjudicated" (collapsed to a count --
    no need to re-look at a term already judged real/artifact) vs
    "unadjudicated" (printed in full -- the actual triage queue).
    """
    print("=" * 66)
    print("SECTOR ACCEPTANCE REPORT — %s" % label)
    print("=" * 66)
    print("G2 cited-quote verification : %d/%d (%.0f%%) -> %s"
          % (report.g2_verified, report.g2_total, report.g2_pct, "PASS" if report.g2_pass else "FAIL"))
    if report.g2_worst_notes:
        print("     PER-NOTE FLOOR FAILURES (< %.0f%% each, aggregate can still be fine):"
              % (100 * G2_MIN_NOTE_THRESHOLD))
        for slug, pct in report.g2_worst_notes:
            verified, total = report.g2_per_note[slug]
            print("       %s: %d/%d (%.0f%%)" % (slug, verified, total, pct))
    print("G3 ineligible-lesson cites  : %d -> %s"
          % (len(report.g3_bad_cites), "PASS" if report.g3_pass else "FAIL"))
    for slug, ref in report.g3_bad_cites:
        print("     BAD CITE: %s cites ineligible ref %s" % (slug, ref))
    if adjudications is not None:
        from soic_wiki.adjudication import unadjudicated
        new_flags = unadjudicated(report.g1_flagged, adjudications)
        already = len(report.g1_flagged) - len(new_flags)
        print("G1 uncited terms flagged    : %d (%d already adjudicated, %d new -> needs a look)"
              % (len(report.g1_flagged), already, len(new_flags)))
        for t, slugs in sorted(new_flags.items()):
            print("     %r in %s  [UNADJUDICATED]" % (t, ",".join(slugs)))
    else:
        print("G1 uncited terms flagged    : %d (informational + adjudicate)" % len(report.g1_flagged))
        for t, slugs in sorted(report.g1_flagged.items()):
            print("     %r in %s" % (t, ",".join(slugs)))
    print("G4 hollow admissions        : %d (informational, no baseline)" % report.g4_hollow)
    print()
    print("VERDICT: %s" % ("PASS" if report.verdict else "FAIL"))
