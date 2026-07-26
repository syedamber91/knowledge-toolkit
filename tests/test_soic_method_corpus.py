from soic_method.corpus import (
    hash_text,
    lesson_id_from_url,
    normalize_slice,
    resolve_timestamp,
)

BODY = (
    "[00:00:05] Hi everyone.\n"
    "[00:41:12] we don't even look at a business doing less than 18% ROC\n"
    "[00:41:20] moving on.\n"
)


def test_normalize_strips_markers_and_collapses_space():
    assert normalize_slice("[00:41:12] less   than\n18%") == "less than 18%"


def test_normalize_casefolds():
    assert normalize_slice("Less Than 18% ROCE") == "less than 18% roce"


def test_resolve_timestamp_picks_nearest_preceding_marker():
    idx = BODY.index("we don't even")
    assert resolve_timestamp(BODY, idx) == "00:41:12"


def test_resolve_timestamp_before_any_marker_returns_zero():
    assert resolve_timestamp("no markers here", 3) == "00:00:00"


def test_hash_is_stable_and_differs_on_change():
    assert hash_text("abc") == hash_text("abc")
    assert hash_text("abc") != hash_text("abd")


def test_lesson_id_is_the_url_tail():
    url = "https://learn.soic.in/learn/home/SOIC-Course/x/section/299814/lesson/1823241"
    assert lesson_id_from_url(url) == "1823241"


from pathlib import Path

import pytest

from soic_method.corpus import load_corpus

CONTENT = Path(__file__).resolve().parents[1] / "data" / "content.json"


@pytest.mark.skipif(not CONTENT.exists(), reason="corpus not present")
def test_load_corpus_finds_lessons_with_bodies():
    lessons = load_corpus(CONTENT)
    assert len(lessons) > 400
    assert all(l.body_text for l in lessons)
    assert all(l.text_hash for l in lessons)
