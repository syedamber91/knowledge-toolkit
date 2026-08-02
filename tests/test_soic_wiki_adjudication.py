import pytest


def test_load_adjudications_returns_empty_dict_when_file_absent(tmp_path):
    from soic_wiki.adjudication import load_adjudications

    assert load_adjudications(tmp_path / "missing.yaml") == {}


def test_record_and_load_adjudication_roundtrips(tmp_path):
    from soic_wiki.adjudication import record_adjudication, load_adjudications, VERDICT_ARTIFACT

    path = tmp_path / "adjudications.yaml"
    record_adjudication(
        path, term="diamond of profit pools", verdict=VERDICT_ARTIFACT,
        reason="ASR mangling of 'lab-grown diamond' + 'profit pools' colliding; hapax, 1 lesson",
        stamp="2026-08-02",
    )

    data = load_adjudications(path)
    assert data["diamond of profit pools"]["verdict"] == "artifact"
    assert "lab-grown diamond" in data["diamond of profit pools"]["reason"]
    assert data["diamond of profit pools"]["date"] == "2026-08-02"


def test_record_adjudication_rejects_unknown_verdict(tmp_path):
    from soic_wiki.adjudication import record_adjudication

    with pytest.raises(ValueError):
        record_adjudication(tmp_path / "a.yaml", "term", "maybe", "reason", "2026-08-02")


def test_record_adjudication_overwrites_a_prior_verdict_for_same_term(tmp_path):
    from soic_wiki.adjudication import record_adjudication, load_adjudications, VERDICT_ARTIFACT, VERDICT_REAL

    path = tmp_path / "a.yaml"
    record_adjudication(path, "purple patch", VERDICT_ARTIFACT, "first guess", "2026-07-01")
    record_adjudication(path, "purple patch", VERDICT_REAL, "confirmed real, said in 9 lessons", "2026-08-02")

    data = load_adjudications(path)
    assert len(data) == 1
    assert data["purple patch"]["verdict"] == "real"
    assert data["purple patch"]["date"] == "2026-08-02"


def test_unadjudicated_filters_out_terms_with_a_recorded_verdict():
    from soic_wiki.adjudication import unadjudicated

    flagged = {
        "diamond of profit pools": ["lgd-note"],
        "some new coinage": ["other-note"],
    }
    adjudications = {"diamond of profit pools": {"verdict": "artifact", "reason": "x", "date": "y"}}

    result = unadjudicated(flagged, adjudications)

    assert result == {"some new coinage": ["other-note"]}
