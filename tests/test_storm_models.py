import pytest
from pydantic import ValidationError
from storm_core.models import Verdict, Grade, Evidence, Finding, StormReport


def test_verdict_and_grade_values():
    assert [v.value for v in Verdict] == ["KEEP", "WATCHLIST", "CUT"]
    assert [g.value for g in Grade] == ["A", "B", "C"]


def test_storm_report_roundtrips_and_validates_verdict():
    r = StormReport(
        topic="Zakat Advisory", mode="idea", summary="s",
        verdict="KEEP", lenses=["Operator", "Mufti"],
        findings=[Finding(title="t", detail="d", reliability=9,
                          supported_by=["Operator"], challenged_by=["Skeptic"],
                          evidence=[Evidence(claim="c", source="gov.in", grade="A")])],
        generated="2026-07-06",
    )
    dumped = r.model_dump_json()
    back = StormReport.model_validate_json(dumped)
    assert back.verdict is Verdict.KEEP
    assert back.findings[0].evidence[0].grade is Grade.A


def test_invalid_verdict_rejected():
    with pytest.raises(ValidationError):
        StormReport(topic="x", mode="idea", summary="s", verdict="MAYBE",
                    lenses=[], findings=[], generated="2026-07-06")
