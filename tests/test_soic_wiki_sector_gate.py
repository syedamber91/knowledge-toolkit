import json
from pathlib import Path


def test_run_sector_acceptance_report_matches_real_pilot_data():
    """Regression test: run the extracted function against the actual
    Real Estate pilot's committed gate inputs and confirm it reproduces
    the exact live result already reported this session (96% G2, PASS)."""
    from soic_wiki.sector_gate import run_sector_acceptance_report

    root = Path(__file__).resolve().parents[1]
    notes_dir = root / "out" / "a5_real_estate_pilot" / "notes"
    refs_path = root / "out" / "a5_real_estate_pilot" / "refs.json"
    if not notes_dir.is_dir():
        import pytest

        pytest.skip("out/a5_real_estate_pilot is gitignored scratch, not present in this checkout")

    refs = json.loads(refs_path.read_text())
    report = run_sector_acceptance_report(notes_dir, refs, label="Real Estate Pilot")

    assert report.verdict is True
    assert report.g2_verified == 64
    assert report.g2_total == 67


def test_run_sector_acceptance_report_fails_below_80_percent_g2(tmp_path):
    from soic_wiki.sector_gate import run_sector_acceptance_report

    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    # A note whose only citation cannot be verified (ref points nowhere) --
    # forces g2_total=1, g2_verified=0, well below the 80% bar.
    (notes_dir / "concept.md").write_text('## The mechanism\n\n"a real quote here" (NOPE 00:00:01)\n')

    report = run_sector_acceptance_report(notes_dir, refs={}, label="test")

    assert report.verdict is False
    assert report.g2_total == 1
    assert report.g2_verified == 0  # NOPE isn't a registered ref -- unverifiable, correctly FAILs


def test_run_sector_acceptance_report_returns_g2_pct_property():
    from soic_wiki.sector_gate import AcceptanceReport

    report = AcceptanceReport(
        verdict=True, g2_verified=64, g2_total=67, g3_bad_cites=[], g1_flagged={}, g4_hollow=0
    )
    assert round(report.g2_pct, 1) == 95.5
