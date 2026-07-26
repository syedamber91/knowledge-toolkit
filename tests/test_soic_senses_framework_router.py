from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "frameworks_sample.md"


def test_load_frameworks_parses_each_numbered_framework():
    from soic_senses.framework_router import load_frameworks

    frameworks = load_frameworks(FIXTURE)

    ids = [f.id for f in frameworks]
    assert ids == ["F1", "F2", "F10"]


def test_load_frameworks_captures_title_and_body():
    from soic_senses.framework_router import load_frameworks

    frameworks = load_frameworks(FIXTURE)
    f1 = frameworks[0]

    assert f1.title == "Working-capital re-rating (mix-shift) model"
    assert "institutional/EPC" in f1.body
    assert "Grounding" in f1.body


def test_load_frameworks_does_not_include_the_intro_or_batch_header_as_a_framework():
    from soic_senses.framework_router import load_frameworks

    frameworks = load_frameworks(FIXTURE)

    assert all(f.id.startswith("F") and f.id[1:].isdigit() for f in frameworks)
    assert not any("intro text" in f.body for f in frameworks)


def test_match_frameworks_ranks_by_keyword_hits():
    from soic_senses.framework_router import load_frameworks, match_frameworks

    frameworks = load_frameworks(FIXTURE)
    matches = match_frameworks(frameworks, ["DCF", "intrinsic value", "growth"])

    assert matches[0].id == "F10"


def test_match_frameworks_excludes_frameworks_with_zero_keyword_hits():
    from soic_senses.framework_router import load_frameworks, match_frameworks

    frameworks = load_frameworks(FIXTURE)
    matches = match_frameworks(frameworks, ["something totally unrelated to any framework"])

    assert matches == []
