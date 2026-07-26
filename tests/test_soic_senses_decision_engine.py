from pathlib import Path
from unittest.mock import patch

FRAMEWORKS_FIXTURE = Path(__file__).parent / "fixtures" / "frameworks_sample.md"
SECTOR_REGISTRY_FIXTURE = Path(__file__).parent / "fixtures" / "sector_notebooks_sample.yaml"


def test_build_briefing_includes_live_ratios_when_fetch_succeeds():
    from soic_senses.decision_engine import build_briefing

    fake_ratios = {"Stock P/E": 15.0, "ROCE": 63.0}
    with patch("soic_senses.decision_engine.fetch_screener_ratios", return_value=fake_ratios):
        briefing = build_briefing(
            symbol="TCS",
            keywords=["DCF", "intrinsic value"],
            frameworks_path=FRAMEWORKS_FIXTURE,
        )

    assert briefing.symbol == "TCS"
    assert briefing.live_ratios == fake_ratios
    assert briefing.data_error is None


def test_build_briefing_selects_matching_frameworks():
    from soic_senses.decision_engine import build_briefing

    with patch("soic_senses.decision_engine.fetch_screener_ratios", return_value={}):
        briefing = build_briefing(
            symbol="TCS",
            keywords=["DCF", "intrinsic value", "growth"],
            frameworks_path=FRAMEWORKS_FIXTURE,
        )

    assert [f.id for f in briefing.frameworks] == ["F10"]


def test_build_briefing_records_data_error_instead_of_crashing_when_fetch_fails():
    from soic_senses.decision_engine import build_briefing
    from soic_senses.screener_client import CompanyNotFoundError

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios",
        side_effect=CompanyNotFoundError("no page for XYZ"),
    ):
        briefing = build_briefing(symbol="XYZ", keywords=["DCF"], frameworks_path=FRAMEWORKS_FIXTURE)

    assert briefing.live_ratios is None
    assert "no page for XYZ" in briefing.data_error


def test_briefing_to_markdown_never_hides_a_data_fetch_failure():
    from soic_senses.decision_engine import build_briefing
    from soic_senses.screener_client import IncompleteRatiosError

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios",
        side_effect=IncompleteRatiosError("blank ratios"),
    ):
        briefing = build_briefing(symbol="VENUSPIPES", keywords=["BHEL"], frameworks_path=FRAMEWORKS_FIXTURE)

    md = briefing.to_markdown()
    assert "blank ratios" in md
    assert "VENUSPIPES" in md


def test_build_briefing_without_sector_registry_path_has_no_sectors():
    from soic_senses.decision_engine import build_briefing

    with patch("soic_senses.decision_engine.fetch_screener_ratios", return_value={}):
        briefing = build_briefing(symbol="TCS", keywords=["DCF"], frameworks_path=FRAMEWORKS_FIXTURE)

    assert briefing.sectors == []


def test_build_briefing_matches_sectors_when_registry_path_given():
    from soic_senses.decision_engine import build_briefing

    with patch("soic_senses.decision_engine.fetch_screener_ratios", return_value={}):
        briefing = build_briefing(
            symbol="NAVINFLUOR",
            keywords=["fluorine", "srf"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    assert [s.slug for s in briefing.sectors] == ["fluorine-industry-megatrend-or-fad"]


def test_build_briefing_sector_matching_does_not_disturb_framework_matching():
    from soic_senses.decision_engine import build_briefing

    with patch("soic_senses.decision_engine.fetch_screener_ratios", return_value={}):
        briefing = build_briefing(
            symbol="TCS",
            keywords=["DCF", "intrinsic value", "growth"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    assert [f.id for f in briefing.frameworks] == ["F10"]
    assert briefing.sectors == []


def test_briefing_to_markdown_includes_sector_context_section():
    from soic_senses.decision_engine import build_briefing

    with patch("soic_senses.decision_engine.fetch_screener_ratios", return_value={}):
        briefing = build_briefing(
            symbol="NAVINFLUOR",
            keywords=["fluorine"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    md = briefing.to_markdown()
    assert "## Applicable Sector Context" in md
    assert "Fluorine Industry" in md


def test_adding_a_second_unrelated_sector_does_not_crowd_out_the_first():
    """Evolutionary-behavior test: as configs/sector_notebooks.yaml grows,
    decision_engine needs no further code change -- each sector is still
    independently discoverable by its own keywords."""
    from soic_senses.decision_engine import build_briefing

    with patch("soic_senses.decision_engine.fetch_screener_ratios", return_value={}):
        real_estate_briefing = build_briefing(
            symbol="DLF",
            keywords=["real estate", "joint development"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )
        fluorine_briefing = build_briefing(
            symbol="NAVINFLUOR",
            keywords=["fluorine", "navin fluorine"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    assert [s.slug for s in real_estate_briefing.sectors] == ["detailed-analysis-of-real-estate-sector"]
    assert [s.slug for s in fluorine_briefing.sectors] == ["fluorine-industry-megatrend-or-fad"]
