from storm_core.models import StormReport, Finding, Contradiction, Evidence
from storm_core.report import build_note_markdown


def _report():
    return StormReport(
        topic="Zakat & Islamic-Finance Advisory", mode="idea",
        summary="Strong regulated niche.", verdict="KEEP",
        lenses=["Operator", "Investor", "Mufti"],
        findings=[Finding(
            title="Underserved compliance demand", detail="MSMEs need zakat structuring.",
            reliability=9, supported_by=["Operator", "Investor"], challenged_by=["Skeptic"],
            evidence=[Evidence(claim="12% CAGR", source="rbi.org.in", date="2026-01",
                               grade="A", status="confirmed")])],
        contradictions=[Contradiction(topic="Pricing power",
                        positions={"Investor": "high", "Skeptic": "low"},
                        resolution="Retainer model resolves it.")],
        halal_note="Riba-free by construction; Mufti: PASS.",
        generated="2026-07-06",
    )


def test_note_has_frontmatter_and_all_sections():
    md = build_note_markdown(_report())
    assert md.startswith("---\n")
    assert 'title: "Zakat & Islamic-Finance Advisory"' in md
    assert "tags: [storm, idea]" in md
    assert "verdict: KEEP" in md
    assert "## Summary" in md
    assert "## Findings" in md
    assert "Underserved compliance demand" in md
    assert "(reliability 9/10)" in md
    assert "supported by: Operator, Investor" in md
    assert "12% CAGR" in md and "grade A" in md and "confirmed" in md
    assert "## Contradiction Map" in md
    assert "Pricing power" in md
    assert "## Halal Note" in md and "Mufti: PASS" in md


def test_halal_section_omitted_when_empty():
    r = _report()
    r.halal_note = ""
    assert "## Halal Note" not in build_note_markdown(r)
