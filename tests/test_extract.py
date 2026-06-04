from pathlib import Path

from soic_toolkit.extract import extract_lesson

FIXTURE = Path(__file__).parent / "fixtures" / "sample_lesson.html"
BASE = "https://learn.soic.in/learn/lesson-1"


def _data():
    html = FIXTURE.read_text(encoding="utf-8")
    return extract_lesson(html, BASE)


def test_title_extracted():
    assert _data()["title"] == "Understanding Intrinsic Value"


def test_body_contains_key_text_without_noise():
    body = _data()["body_text"]
    assert "Intrinsic value is the true worth" in body
    assert "margin of safety" in body
    # Noise (nav/footer/script) should be stripped.
    assert "tracking" not in body
    assert "© SOIC" not in body


def test_captions_url_made_absolute():
    assert _data()["captions_url"] == "https://learn.soic.in/media/captions/lesson1.vtt"


def test_resource_links_only_documents():
    links = _data()["resource_links"]
    assert "https://learn.soic.in/resources/intrinsic-value-notes.pdf" in links
    assert all("next-lesson" not in link for link in links)


def test_key_points_derived():
    points = _data()["key_points"]
    assert len(points) >= 1
    assert any("intrinsic value" in p.lower() for p in points)
