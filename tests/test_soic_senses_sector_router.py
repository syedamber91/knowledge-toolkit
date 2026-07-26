from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "sector_notebooks_sample.yaml"


def test_load_sectors_parses_slug_notebook_id_title_and_keywords():
    from soic_senses.sector_router import load_sectors

    sectors = load_sectors(FIXTURE)

    real_estate = next(s for s in sectors if s.slug == "detailed-analysis-of-real-estate-sector")
    assert real_estate.notebook_id == "462f4864-4414-4e11-b8b6-548077f46a3c"
    assert real_estate.title == "SOIC L6 Pilot -- Detailed Analysis of Real Estate Sector"
    assert "real estate" in real_estate.keywords


def test_load_sectors_defaults_keywords_to_empty_list_when_absent():
    from soic_senses.sector_router import load_sectors

    sectors = load_sectors(FIXTURE)

    no_kw = next(s for s in sectors if s.slug == "no-keywords-sector")
    assert no_kw.keywords == []


def test_match_sectors_ranks_by_keyword_hits():
    from soic_senses.sector_router import load_sectors, match_sectors

    sectors = load_sectors(FIXTURE)
    matches = match_sectors(sectors, ["fluorine", "srf", "refrigerant gas"])

    assert matches[0].slug == "fluorine-industry-megatrend-or-fad"


def test_match_sectors_excludes_sectors_with_zero_keyword_hits():
    from soic_senses.sector_router import load_sectors, match_sectors

    sectors = load_sectors(FIXTURE)
    matches = match_sectors(sectors, ["something totally unrelated to any sector"])

    assert matches == []


def test_match_sectors_a_sector_with_no_keywords_never_matches():
    from soic_senses.sector_router import load_sectors, match_sectors

    sectors = load_sectors(FIXTURE)
    # keywords list is empty for no-keywords-sector, so nothing can ever hit it
    matches = match_sectors(sectors, ["real estate", "fluorine", "anything"])

    assert all(m.slug != "no-keywords-sector" for m in matches)
