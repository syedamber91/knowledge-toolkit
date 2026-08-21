import json
from pathlib import Path

import pytest

from udemy_toolkit import crawler
from udemy_toolkit.config import settings
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

# A curriculum with a third lecture added, simulating a course that grew
# between two crawl runs.
GROWN_CURRICULUM = {
    "results": [
        {"_class": "chapter", "id": 900, "title": "S1", "object_index": 1},
        {"_class": "lecture", "id": 10, "title": "Welcome", "asset": {"time_estimation": 60}},
        {"_class": "lecture", "id": 11, "title": "No captions here", "asset": {}},
        {"_class": "lecture", "id": 12, "title": "New lecture", "asset": {"time_estimation": 60}},
    ]
}

VTT = "WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\nhello there\n"

# A cue with timing but no actual text content (only inline markup, which
# extract.parse_cues strips down to an empty string) -- captions_to_transcript
# genuinely reduces this to "".
EMPTY_TEXT_VTT = "WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\n<i></i>\n\n"


class FakeFetcher:
    def __init__(self, captions_by_id, curriculum=None):
        self._captions = captions_by_id
        self.caption_calls = []
        self._curriculum = curriculum if curriculum is not None else CURRICULUM

    def course_meta(self, course_url):
        return {"id": "123", "title": "Test Course", "instructor": "Someone", "curriculum": self._curriculum}

    def captions(self, course_id, lecture_id):
        self.caption_calls.append(lecture_id)
        return self._captions.get(lecture_id)


class ExpiringFetcher:
    """Returns captions for lecture 10, then raises SessionExpired on 11."""

    def __init__(self):
        self.caption_calls = []

    def course_meta(self, course_url):
        return {"id": "123", "title": "Test Course", "instructor": "Someone", "curriculum": CURRICULUM}

    def captions(self, course_id, lecture_id):
        self.caption_calls.append(lecture_id)
        if lecture_id == "11":
            raise crawler.SessionExpired("session no longer valid")
        return VTT


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
    assert delays and all(
        settings.crawl_min_delay <= d <= settings.crawl_max_delay for d in delays
    )


def test_session_expired_mid_crawl_preserves_prior_work(tmp_path):
    path = tmp_path / "udemy.json"
    fetcher = ExpiringFetcher()

    with pytest.raises(crawler.SessionExpired):
        crawl_course(COURSE_URL, fetcher, catalog_path=path, sleep=_noop_sleep)

    catalog = UdemyCatalog.load(path)
    lectures = {lec.id: lec for lec in catalog.courses[0].lectures()}
    assert lectures["10"].has_transcript is True
    assert "hello there" in lectures["10"].transcript


def test_limit_persists_accurate_state_at_stop_point(tmp_path):
    path = tmp_path / "udemy.json"
    fetcher = FakeFetcher({"10": VTT, "11": VTT})

    summary = crawl_course(COURSE_URL, fetcher, catalog_path=path, limit=1, sleep=_noop_sleep)

    catalog = UdemyCatalog.load(path)
    lectures = catalog.courses[0].lectures()
    assert len(lectures) == 1
    assert lectures[0].id == "10"
    assert summary.captured == 1
    assert summary.skipped_no_captions == 0
    assert summary.already_seen == 0


def test_empty_extracted_transcript_counts_as_no_captions(tmp_path):
    path = tmp_path / "udemy.json"
    fetcher = FakeFetcher({"10": EMPTY_TEXT_VTT})

    summary = crawl_course(COURSE_URL, fetcher, catalog_path=path, sleep=_noop_sleep)

    catalog = UdemyCatalog.load(path)
    lectures = {lec.id: lec for lec in catalog.courses[0].lectures()}
    assert lectures["10"].has_transcript is False
    assert lectures["10"].transcript == ""
    assert summary.skipped_no_captions == 2
    assert summary.captured == 0
    assert "10" in catalog.seen_lecture_ids


def test_limit_on_recrawl_does_not_drop_previously_captured_lectures(tmp_path):
    """Finding 1 regression: --limit on a re-crawl must not delete lectures
    already captured in a prior run just because they sit past the cutoff.
    """
    path = tmp_path / "udemy.json"
    # First run: full crawl of a 2-lecture course, both captured.
    first = FakeFetcher({"10": VTT, "11": VTT})
    crawl_course(COURSE_URL, first, catalog_path=path, sleep=_noop_sleep)

    # Curriculum grows; re-crawl with limit=1. The limit should bound how
    # many NEW lectures get fetched (only lecture 12 is new here), not cause
    # the already-captured ones (10, 11) to be dropped from the catalog.
    second = FakeFetcher({"10": VTT, "11": VTT, "12": VTT}, curriculum=GROWN_CURRICULUM)
    summary = crawl_course(COURSE_URL, second, catalog_path=path, limit=1, sleep=_noop_sleep)

    # 10 and 11 are already known -> no refetch; exactly one new fetch (12).
    assert second.caption_calls == ["12"]
    catalog = UdemyCatalog.load(path)
    lectures = {lec.id: lec for lec in catalog.courses[0].lectures()}
    assert lectures["10"].has_transcript is True
    assert "hello there" in lectures["10"].transcript
    assert lectures["11"].id == "11"
    assert summary.already_seen == 2


def test_new_lecture_added_since_first_run_is_fetched_without_disturbing_prior(tmp_path):
    path = tmp_path / "udemy.json"
    first = FakeFetcher({"10": VTT}, curriculum=CURRICULUM)
    crawl_course(COURSE_URL, first, catalog_path=path, sleep=_noop_sleep)

    second = FakeFetcher({"10": VTT, "12": VTT}, curriculum=GROWN_CURRICULUM)
    summary = crawl_course(COURSE_URL, second, catalog_path=path, sleep=_noop_sleep)

    assert "12" in second.caption_calls
    assert "10" not in second.caption_calls

    catalog = UdemyCatalog.load(path)
    lectures = {lec.id: lec for lec in catalog.courses[0].lectures()}
    assert lectures["12"].has_transcript is True
    assert lectures["10"].has_transcript is True
    assert "hello there" in lectures["10"].transcript
    assert summary.captured == 1
