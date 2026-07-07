from storm_core.models import StormReport, Finding
from storm_core.html_render import render_html


def _report():
    return StormReport(
        topic="Zakat <Advisory>", mode="idea", summary="Strong niche.",
        verdict="KEEP", lenses=["Operator"],
        findings=[
            Finding(title="Low-rel", detail="d", reliability=4),
            Finding(title="High-rel", detail="d", reliability=9),
        ],
        generated="2026-07-06",
    )


def test_html_is_self_contained_and_ranked():
    html = render_html(_report())
    assert html.lstrip().startswith("<!doctype html>")
    assert "http://" not in html and "https://" not in html  # no external refs
    assert "<style>" in html
    # topic is HTML-escaped
    assert "Zakat &lt;Advisory&gt;" in html
    assert "KEEP" in html
    # findings ranked: High-rel (9) appears before Low-rel (4)
    assert html.index("High-rel") < html.index("Low-rel")
