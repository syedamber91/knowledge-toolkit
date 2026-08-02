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


def test_g2_pass_requires_90_percent_aggregate_not_80(tmp_path):
    # A batch at 85% aggregate -- would have PASSED under the old 80% bar,
    # must FAIL under the raised 90% bar (real batches this session ran
    # 91-100%, so 80% was tolerating a failure rate never actually produced).
    from soic_wiki.sector_gate import AcceptanceReport

    report = AcceptanceReport(
        verdict=False, g2_verified=17, g2_total=20, g3_bad_cites=[], g1_flagged={}, g4_hollow=0,
        g2_per_note={"a": (17, 20)},
    )
    assert round(report.g2_pct, 1) == 85.0
    assert report.g2_pass is False


def test_g2_pass_fails_on_one_bad_note_even_with_a_healthy_aggregate():
    # 3 clean notes (100%) + 1 note at 20% (1/5) averages 84% -- still would
    # have failed the old 80% bar here, so use numbers that clear 90%
    # aggregate while still hiding one bad note: 27/30 = 90% aggregate, but
    # one note (2/10 = 20%) is well under the 60% per-note floor.
    from soic_wiki.sector_gate import AcceptanceReport

    report = AcceptanceReport(
        verdict=False, g2_verified=27, g2_total=30, g3_bad_cites=[], g1_flagged={}, g4_hollow=0,
        g2_per_note={"clean-a": (10, 10), "clean-b": (10, 10), "bad-note": (2, 5), "clean-c": (5, 5)},
    )
    assert round(report.g2_pct, 1) == 90.0
    assert report.g2_pass is False  # aggregate clears 90% but bad-note is 40%
    assert report.g2_worst_notes == [("bad-note", 40.0)]


def test_g2_worst_notes_ignores_notes_with_no_citations():
    from soic_wiki.sector_gate import AcceptanceReport

    report = AcceptanceReport(
        verdict=False, g2_verified=10, g2_total=10, g3_bad_cites=[], g1_flagged={}, g4_hollow=0,
        g2_per_note={"cited-clean": (10, 10), "uncited-note": (0, 0)},
    )
    assert report.g2_worst_notes == []
    assert report.g2_pass is True


def test_print_report_collapses_adjudicated_g1_flags(capsys):
    from soic_wiki.sector_gate import AcceptanceReport, print_report

    report = AcceptanceReport(
        verdict=True, g2_verified=10, g2_total=10, g3_bad_cites=[], g4_hollow=0,
        g1_flagged={"known artifact term": ["note-a"], "brand new coinage": ["note-b"]},
    )
    adjudications = {"known artifact term": {"verdict": "artifact", "reason": "x", "date": "y"}}

    print_report(report, label="test", adjudications=adjudications)

    out = capsys.readouterr().out
    assert "1 already adjudicated, 1 new -> needs a look" in out
    assert "brand new coinage" in out
    assert "[UNADJUDICATED]" in out
    assert "known artifact term" not in out  # collapsed, not reprinted every run


def test_run_sector_acceptance_report_accepts_a_prebuilt_notes_dict():
    # The vault's concepts/ dir is flat (no per-sector subfolder to glob) --
    # the drift-check audit assembles a {slug: text} dict itself and must be
    # able to pass it directly instead of a notes_dir.
    from soic_wiki.sector_gate import run_sector_acceptance_report

    notes = {"good-note": '## The mechanism\n\nplain prose, no citations.\n'}
    report = run_sector_acceptance_report(None, refs={}, label="test", notes=notes)

    assert report.g2_per_note == {"good-note": (0, 0)}
    assert report.verdict is True  # nothing cited, nothing to fail


def test_run_sector_acceptance_report_populates_per_note_breakdown(tmp_path):
    from soic_wiki.sector_gate import run_sector_acceptance_report

    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "good-note.md").write_text(
        '## The mechanism\n\n"a real quote here" (NOPE 00:00:01)\n'
    )
    (notes_dir / "another-note.md").write_text(
        '## The mechanism\n\nplain prose, no citations at all.\n'
    )

    report = run_sector_acceptance_report(notes_dir, refs={}, label="test")

    assert report.g2_per_note["good-note"] == (0, 1)      # unverifiable ref -> fails
    assert report.g2_per_note["another-note"] == (0, 0)   # no citations to check
    assert report.verdict is False
