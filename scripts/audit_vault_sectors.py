#!/usr/bin/env python3
"""Re-run G1-G4 against every ALREADY-SYNCED sector in the vault, using the
persisted `refs/<sector>.json` mappings (see `sync_sector_refs`) and the
LIVE corpus -- the audit this pipeline never had.

Read-only by design, matching the same discipline as the OS-audit pattern
this review borrowed from (`nate-herk`'s "read only, never fix... just give
a report"): this script never edits a vault note. It only ever writes the
baseline file, and only when `--update-baseline` is passed explicitly.

Why this matters: citations point at (REF, timestamp) into a transcript.
If a lesson is ever re-captured (it has happened -- "SOIC Market Signals"
was re-captured 2026-07-27 with new timestamp markers), a citation that
verified at write time can silently stop verifying, and nothing before this
script would ever notice. Gates ran once, at write time, and never again.

Usage:
    # Report current gate status for every synced sector.
    python3 scripts/audit_vault_sectors.py --vault-root "/path/to/Learning Vault Invest"

    # Same, but also persist current results as the new drift baseline.
    python3 scripts/audit_vault_sectors.py --vault-root "..." --update-baseline

    # Only check specific sectors (comma-separated slugs).
    python3 scripts/audit_vault_sectors.py --vault-root "..." --only fluorine-industry-megatrend-or-fad,oil-and-gas-sector-simplified

Exit code: 0 if every checked sector currently passes G2+G3 with no drift
worse than the tolerance below; 1 if any sector currently fails, or any
sector's G2 % dropped by more than DRIFT_TOLERANCE_PCT since the baseline.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.sector_gate import run_sector_acceptance_report  # noqa: E402

DRIFT_TOLERANCE_PCT = 3.0  # a G2% drop bigger than this since baseline is reported as drift


def _sector_concepts(index_path: Path) -> Dict[str, set]:
    idx = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    out: Dict[str, set] = {}
    for slug, meta in (idx.get("concepts") or {}).items():
        for t in meta.get("topics", []):
            out.setdefault(t, set()).add(slug)
    return out


def _notes_for_sector(concepts_dir: Path, concept_slugs: set) -> Dict[str, str]:
    notes = {}
    for slug in sorted(concept_slugs):
        path = concepts_dir / f"{slug}.md"
        if path.exists():
            notes[slug] = path.read_text(encoding="utf-8")
    return notes


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vault-root", required=True)
    p.add_argument("--update-baseline", action="store_true")
    p.add_argument("--only", default=None, help="Comma-separated sector slugs to limit the run to")
    args = p.parse_args()

    vault_root = Path(args.vault_root)
    soic_root = vault_root / "wiki" / "personas" / "soic"
    concepts_dir = soic_root / "concepts"
    refs_dir = soic_root / "refs"
    index_path = soic_root / "index.yaml"
    baseline_path = soic_root / "gate_baseline.json"
    repo_root = Path(__file__).resolve().parent.parent

    sector_concepts = _sector_concepts(index_path)
    baseline = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else {}

    only = set(args.only.split(",")) if args.only else None
    ref_files = sorted(refs_dir.glob("*.json"))
    if only:
        ref_files = [f for f in ref_files if f.stem in only]

    print(f"auditing {len(ref_files)} sector(s) with persisted refs "
          f"(vault has {len(sector_concepts)} synced topics total)")
    if len(ref_files) < len(sector_concepts) and not only:
        missing = sorted(set(sector_concepts) - {f.stem for f in ref_files})
        print(f"NOTE: {len(missing)} synced topic(s) have no persisted refs yet, skipped: "
              f"{', '.join(missing)}")
    print()

    any_fail = False
    any_drift = False
    new_baseline = dict(baseline)

    for ref_file in ref_files:
        sector = ref_file.stem
        refs = json.loads(ref_file.read_text(encoding="utf-8"))
        concept_slugs = sector_concepts.get(sector, set())
        notes = _notes_for_sector(concepts_dir, concept_slugs)

        report = run_sector_acceptance_report(
            None, refs, label=sector, repo_root=repo_root, notes=notes
        )

        prior = baseline.get(sector)
        status = "PASS" if report.verdict else "FAIL"
        line = f"{sector:55s} {report.g2_verified:3d}/{report.g2_total:3d} ({report.g2_pct:5.1f}%) {status}"

        drift_note = ""
        if prior is not None:
            delta = report.g2_pct - prior["g2_pct"]
            if abs(delta) > DRIFT_TOLERANCE_PCT or prior["verdict"] != report.verdict:
                drift_note = f"  <-- DRIFT since baseline ({prior['g2_pct']:.1f}% -> {report.g2_pct:.1f}%)"
                any_drift = True
        else:
            drift_note = "  (no baseline yet)"

        print(line + drift_note)
        if report.g2_worst_notes:
            for slug, pct in report.g2_worst_notes:
                verified, total = report.g2_per_note[slug]
                print(f"     PER-NOTE FLOOR FAIL: {slug} {verified}/{total} ({pct:.0f}%)")
        if report.g3_bad_cites:
            for slug, ref in report.g3_bad_cites:
                print(f"     G3 BAD CITE: {slug} cites ineligible ref {ref}")

        if not report.verdict:
            any_fail = True

        new_baseline[sector] = {
            "g2_pct": report.g2_pct,
            "g2_verified": report.g2_verified,
            "g2_total": report.g2_total,
            "verdict": report.verdict,
        }

    print()
    print(f"VERDICT: {'FAIL' if any_fail else 'PASS'}"
          + (" (with drift flagged above)" if any_drift else ""))

    if args.update_baseline:
        baseline_path.write_text(json.dumps(new_baseline, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(f"baseline updated: {baseline_path}")
    elif not baseline_path.exists():
        print("no baseline file exists yet -- re-run with --update-baseline to establish one")

    return 1 if (any_fail or any_drift) else 0


if __name__ == "__main__":
    sys.exit(main())
