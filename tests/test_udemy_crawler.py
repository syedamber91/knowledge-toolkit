import json
from pathlib import Path

from udemy_toolkit.crawler import crawl_course
from udemy_toolkit.models import UdemyCatalog

COURSE_URL = "https://www.udemy.com/course/test/"

CURRICULUM = {
    "results": [
        {"_class": "chapter", "id": 900, "title": "S1", "object_index": 1},
        {"_class": "lecture", "id": 10, "title": "Welcome", "asset": {"time_estimation": 60}},
        {"_class": "lecture", "id": 11, "title": "No captions here", "asset": {}},
    ]
}

VTT = "WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\nhello there\n"


class FakeFetcher:
    def __init__(self, captions_by_id):
        self._captions = captions_by_id
        self.caption_calls = []

    def course_meta(self, course_url):
        return {"id": "123", "title": "Test Course", "instructor": "Someone", "curriculum": CURRICULUM}

    def captions(self, course_id, lecture_id):
        self.caption_calls.append(lecture_id)
        return self._captions.get(lecture_id)


def _noop_sleep(_seconds):
    return None


def test_captures_transcripts_and_marks_captionless_lectures(tmp_path):
    path = tmp_path / "udemy.json"
    fetcher = FakeFetcher({"10": VTT})

    summary = crawl_course(COURSE_URL, fetcher, catalog_path=path, sleep=_noop_sleep)

    assert summary.captured == 1
    assert summary.skipped_no_captions == 1
    catalog = UdemyCatalog.load(path)
    lectures = {lec.id: lec for lec in catalog.courses[0].lectures()}
    assert lectures["10"].has_transcript is True
    assert "hello there" in lectures["10"].transcript
    assert lectures["11"].has_transcript is False
    assert lectures["11"].transcript == ""


def test_resume_does_not_refetch_known_lectures(tmp_path):
    path = tmp_path / "udemy.json"
    first = FakeFetcher({"10": VTT})
    crawl_course(COURSE_URL, first, catalog_path=path, sleep=_noop_sleep)

    second = FakeFetcher({"10": VTT})
    summary = crawl_course(COURSE_URL, second, catalog_path=path, sleep=_noop_sleep)

    assert second.caption_calls == []
    assert summary.captured == 0
    assert summary.already_seen == 2


def test_captionless_lecture_is_recorded_as_seen(tmp_path):
    path = tmp_path / "udemy.json"
    crawl_course(COURSE_URL, FakeFetcher({}), catalog_path=path, sleep=_noop_sleep)
    assert "11" in UdemyCatalog.load(path).seen_lecture_ids


def test_limit_stops_after_n_lectures(tmp_path):
    path = tmp_path / "udemy.json"
    fetcher = FakeFetcher({"10": VTT, "11": VTT})
    crawl_course(COURSE_URL, fetcher, catalog_path=path, limit=1, sleep=_noop_sleep)
    assert fetcher.caption_calls == ["10"]


def test_catalog_is_saved_after_every_lecture(tmp_path):
    path = tmp_path / "udemy.json"
    totals = []

    def spy_sleep(_seconds):
        totals.append(UdemyCatalog.load(path).total_lectures())

    crawl_course(COURSE_URL, FakeFetcher({"10": VTT, "11": VTT}), catalog_path=path, sleep=spy_sleep)
    # Saved incrementally: the catalog on disk already had lecture 1 before
    # lecture 2 was fetched.
    assert totals[0] == 1


def test_sleep_delay_is_within_configured_bounds(tmp_path):
    delays = []
    crawl_course(
        COURSE_URL,
        FakeFetcher({"10": VTT}),
        catalog_path=tmp_path / "udemy.json",
        sleep=lambda s: delays.append(s),
    )
    assert delays and all(1.5 <= d <= 3.5 for d in delays)
