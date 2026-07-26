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

The actual gate logic lives in soic_wiki.sector_gate (shared with
soic_wiki.cli's `run-sector` command, so both entry points check output
the exact same way).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soic_wiki.sector_gate import print_report, run_sector_acceptance_report  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def report(notes_dir: Path, refs: dict, label: str) -> bool:
    """Kept for backward compatibility with any existing caller of this
    exact name/signature; delegates to the shared implementation."""
    print("notes on disk: %d" % len(list(Path(notes_dir).glob("*.md"))))
    print()
    acceptance = run_sector_acceptance_report(notes_dir, refs, label=label, repo_root=ROOT)
    print_report(acceptance, label=label)
    return acceptance.verdict


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("notes_dir", type=Path)
    p.add_argument("refs_json", type=Path)
    p.add_argument("--label", default="")
    args = p.parse_args()
    ok = report(args.notes_dir, json.loads(args.refs_json.read_text()), args.label)
    raise SystemExit(0 if ok else 1)
