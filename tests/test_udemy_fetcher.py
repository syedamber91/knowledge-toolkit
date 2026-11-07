"""Offline tests for the fetch seam in udemy_toolkit.fetcher.

PlaywrightFetcher talks to api-2.0 only through ``self._page.goto`` + reading
the rendered JSON (a real top-level navigation is not blocked by Udemy's
Cloudflare protection the way an XHR-style request is -- see fetcher.py's
module docstring), and fetches the caption file itself via a plain
``self._page.request.get`` against its CDN host. Every test here injects a
fake page mimicking both interfaces. No real network call is possible.
"""

import pytest

from udemy_toolkit.crawler import SessionExpired
from udemy_toolkit.fetcher import PlaywrightFetcher

COURSE_URL = "https://www.udemy.com/course/real-slug/"


class FakeResponse:
    def __init__(self, status=200, text_data=""):
        self.status = status
        self.ok = 200 <= status < 300
        self._text = text_data

    def text(self):
        return self._text


class FakeRequest:
    """Stands in for ``page.request``; maps exact URLs to canned responses."""

    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def get(self, url):
        self.calls.append(url)
        for key, response in self._responses.items():
            if url == key or url.endswith(key):
                return response
        raise AssertionError(f"Unexpected request URL: {url}")


class FakePage:
    """Mimics the two navigation primitives ``PlaywrightFetcher`` uses.

    ``navigations``: dict mapping a URL (or suffix) to either a JSON-able
    value (200 assumed) or a bare int status code (for error-path tests).
    """

    def __init__(self, navigations, cdn_responses=None):
        self._navigations = navigations
        self.request = FakeRequest(cdn_responses or {})
        self.goto_calls = []
        self._last_json = None

    def goto(self, url, wait_until=None, timeout=None):
        self.goto_calls.append(url)
        # Exact matches (e.g. a full pagination "next" URL) win outright --
        # only fall back to a substring match, longest first, when nothing
        # matches exactly. Otherwise a generic base-path key can wrongly
        # shadow a more specific full-URL key that happens to contain it.
        if url in self._navigations:
            value = self._navigations[url]
        else:
            candidates = [(k, v) for k, v in self._navigations.items() if k in url]
            if not candidates:
                raise AssertionError(f"Unexpected navigation URL: {url}")
            _key, value = max(candidates, key=lambda pair: len(pair[0]))
        if isinstance(value, int):
            self._last_json = None
            return FakeResponse(status=value)
        self._last_json = value
        return FakeResponse(status=200)

    def evaluate(self, _script):
        return self._last_json


def _make_fetcher(navigations, cdn_responses=None):
    fetcher = PlaywrightFetcher.__new__(PlaywrightFetcher)
    fetcher._page = FakePage(navigations, cdn_responses)
    fetcher._base = "https://www.udemy.com"
    return fetcher


SUBSCRIBED_PATH = "/api-2.0/users/me/subscribed-courses/"
CURRICULUM_PATH_SUFFIX = (
    "/subscriber-curriculum-items/?page_size=1000&fields[lecture]=id,title,object_index,asset"
    "&fields[chapter]=id,title,object_index&fields[asset]=time_estimation,asset_type"
)


def _subscribed(results, next_url=None):
    return {"results": results, "next": next_url}


def test_course_meta_matches_on_url_slug():
    courses = _subscribed(
        [
            {"id": 111, "title": "Decoy Course", "url": "/course/some-other-slug/learn/", "visible_instructors": []},
            {
                "id": 222,
                "title": "Real Course",
                "url": "/course/real-slug/learn/",
                "visible_instructors": [{"title": "Jane Doe"}],
            },
        ]
    )
    fetcher = _make_fetcher(
        {
            SUBSCRIBED_PATH: courses,
            CURRICULUM_PATH_SUFFIX: {"results": []},
        }
    )

    meta = fetcher.course_meta(COURSE_URL)

    assert meta["id"] == "222"
    assert meta["title"] == "Real Course"
    assert meta["instructor"] == "Jane Doe"


def test_course_meta_paginates_through_subscribed_courses():
    """A real enrolled-courses list can span multiple pages; every page must
    be walked before concluding no match exists."""
    page1 = _subscribed(
        [{"id": 1, "title": "A", "url": "/course/aaa/learn/", "visible_instructors": []}],
        next_url="https://www.udemy.com/api-2.0/users/me/subscribed-courses/?page=2",
    )
    page2 = _subscribed(
        [{"id": 222, "title": "Real Course", "url": "/course/real-slug/learn/", "visible_instructors": []}]
    )
    fetcher = _make_fetcher(
        {
            SUBSCRIBED_PATH: page1,
            "https://www.udemy.com/api-2.0/users/me/subscribed-courses/?page=2": page2,
            CURRICULUM_PATH_SUFFIX: {"results": []},
        }
    )

    meta = fetcher.course_meta(COURSE_URL)

    assert meta["id"] == "222"


def test_course_meta_rejects_suffix_match_on_a_different_course():
    """A slug like 'python-bootcamp' must not match a course whose path
    merely ENDS with that slug, e.g. '/course/complete-python-bootcamp/'.
    Only the exact course-path segment counts as a match.
    """
    slug = "python-bootcamp"
    course_url = f"https://www.udemy.com/course/{slug}/"
    courses = _subscribed(
        [{"id": 999, "title": "The Complete Python Bootcamp", "url": "/course/complete-python-bootcamp/learn/", "visible_instructors": []}]
    )
    fetcher = _make_fetcher({SUBSCRIBED_PATH: courses})

    with pytest.raises(RuntimeError) as excinfo:
        fetcher.course_meta(course_url)

    assert slug in str(excinfo.value)


def test_course_meta_matches_exact_slug_segment():
    courses = _subscribed(
        [
            {"id": 999, "title": "Complete Python Bootcamp", "url": "/course/complete-python-bootcamp/learn/", "visible_instructors": []},
            {"id": 111, "title": "Python Bootcamp", "url": "/course/python-bootcamp/learn/", "visible_instructors": []},
        ]
    )
    fetcher = _make_fetcher(
        {
            SUBSCRIBED_PATH: courses,
            CURRICULUM_PATH_SUFFIX: {"results": []},
        }
    )

    meta = fetcher.course_meta("https://www.udemy.com/course/python-bootcamp/")

    assert meta["id"] == "111"
    assert meta["title"] == "Python Bootcamp"


def test_course_meta_raises_instead_of_guessing_when_no_slug_matches():
    courses = _subscribed(
        [
            {"id": 111, "title": "Unrelated Course A", "url": "/course/other-a/learn/", "visible_instructors": []},
            {"id": 333, "title": "Unrelated Course B", "url": "/course/other-b/learn/", "visible_instructors": []},
        ]
    )
    fetcher = _make_fetcher({SUBSCRIBED_PATH: courses})

    with pytest.raises(RuntimeError) as excinfo:
        fetcher.course_meta(COURSE_URL)

    message = str(excinfo.value)
    assert "real-slug" in message
    assert "Unrelated Course A" in message
    assert "Unrelated Course B" in message


def test_course_meta_raises_clear_error_on_no_enrolled_courses():
    fetcher = _make_fetcher({SUBSCRIBED_PATH: _subscribed([])})

    with pytest.raises(RuntimeError) as excinfo:
        fetcher.course_meta(COURSE_URL)

    assert "Could not resolve course" in str(excinfo.value)


@pytest.mark.parametrize("status", [401, 403])
def test_json_via_navigation_raises_session_expired_on_401_403(status):
    fetcher = _make_fetcher({"/some/path": status})

    with pytest.raises(SessionExpired):
        fetcher._json_via_navigation("/some/path")


def test_json_via_navigation_raises_runtime_error_on_other_non_ok_status():
    fetcher = _make_fetcher({"/some/path": 500})

    with pytest.raises(RuntimeError):
        fetcher._json_via_navigation("/some/path")


def test_captions_returns_none_when_no_captions_present():
    fetcher = _make_fetcher(
        {
            "/lectures/1/?fields[lecture]=asset&fields[asset]=captions&fields[caption]=url,locale_id,title": {
                "asset": {"captions": []}
            },
        }
    )

    assert fetcher.captions("123", "1") is None


def test_captions_returns_text_when_present():
    fetcher = _make_fetcher(
        navigations={
            "/lectures/1/?fields[lecture]=asset&fields[asset]=captions&fields[caption]=url,locale_id,title": {
                "asset": {
                    "captions": [
                        {"url": "https://cdn.udemy.com/caption.vtt", "locale_id": "en_US", "title": "English"}
                    ]
                }
            },
        },
        cdn_responses={
            "https://cdn.udemy.com/caption.vtt": FakeResponse(
                status=200, text_data="WEBVTT\n\n1\n00:00:01.000 --> 00:00:02.000\nhi\n"
            ),
        },
    )

    result = fetcher.captions("123", "1")

    assert result == "WEBVTT\n\n1\n00:00:01.000 --> 00:00:02.000\nhi\n"
