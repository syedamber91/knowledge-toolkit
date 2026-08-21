"""Offline tests for the fetch seam in udemy_toolkit.fetcher.

PlaywrightFetcher talks to the network only through ``self._page.request``,
so every test here injects a fake object mimicking Playwright's
``page.request.get(url)`` interface (``.status``, ``.ok``, ``.json()``,
``.text()``). No real network call is possible.
"""

import pytest

from udemy_toolkit.crawler import SessionExpired
from udemy_toolkit.fetcher import PlaywrightFetcher

COURSE_URL = "https://www.udemy.com/course/real-slug/"


class FakeResponse:
    def __init__(self, status=200, json_data=None, text_data=""):
        self.status = status
        self.ok = 200 <= status < 300
        self._json = json_data
        self._text = text_data

    def json(self):
        return self._json

    def text(self):
        return self._text


class FakeRequest:
    """Stands in for ``page.request``; maps exact URLs to canned responses."""

    def __init__(self, responses):
        # responses: dict[url_suffix_or_exact, FakeResponse]
        self._responses = responses
        self.calls = []

    def get(self, url):
        self.calls.append(url)
        for key, response in self._responses.items():
            if url == key or url.endswith(key):
                return response
        raise AssertionError(f"Unexpected request URL: {url}")


class FakePage:
    def __init__(self, responses):
        self.request = FakeRequest(responses)


def _make_fetcher(responses):
    fetcher = PlaywrightFetcher.__new__(PlaywrightFetcher)
    fetcher._page = FakePage(responses)
    fetcher._base = "https://www.udemy.com"
    return fetcher


SEARCH_PATH = "/api-2.0/courses/?search=real-slug&fields[course]=id,title,url,visible_instructors"
CURRICULUM_PATH_SUFFIX = "/subscriber-curriculum-items/?page_size=1000&fields[lecture]=id,title,object_index,asset&fields[chapter]=id,title,object_index&fields[asset]=time_estimation,asset_type"


def test_course_meta_matches_on_url_slug():
    matching_results = FakeResponse(
        json_data={
            "results": [
                {
                    "id": 111,
                    "title": "Decoy Course",
                    "url": "/course/some-other-slug/",
                    "visible_instructors": [],
                },
                {
                    "id": 222,
                    "title": "Real Course",
                    "url": "/course/real-slug/",
                    "visible_instructors": [{"title": "Jane Doe"}],
                },
            ]
        }
    )
    curriculum = FakeResponse(json_data={"results": []})
    fetcher = _make_fetcher(
        {
            SEARCH_PATH: matching_results,
            CURRICULUM_PATH_SUFFIX: curriculum,
        }
    )

    meta = fetcher.course_meta(COURSE_URL)

    assert meta["id"] == "222"
    assert meta["title"] == "Real Course"
    assert meta["instructor"] == "Jane Doe"


def test_course_meta_rejects_suffix_match_on_a_different_course():
    """Finding 3 regression: a slug like 'python-bootcamp' must not match a
    result whose full path merely ENDS with that slug, e.g.
    '/course/complete-python-bootcamp/'. Only the exact final path segment
    counts as a match.
    """
    slug = "python-bootcamp"
    course_url = f"https://www.udemy.com/course/{slug}/"
    decoy_results = FakeResponse(
        json_data={
            "results": [
                {
                    "id": 999,
                    "title": "The Complete Python Bootcamp",
                    "url": "/course/complete-python-bootcamp/",
                    "visible_instructors": [],
                },
            ]
        }
    )
    fetcher = _make_fetcher(
        {
            f"/api-2.0/courses/?search={slug}&fields[course]=id,title,url,visible_instructors": decoy_results,
        }
    )

    with pytest.raises(RuntimeError) as excinfo:
        fetcher.course_meta(course_url)

    assert slug in str(excinfo.value)


def test_course_meta_matches_exact_slug_path():
    slug = "python-bootcamp"
    course_url = f"https://www.udemy.com/course/{slug}/"
    exact_results = FakeResponse(
        json_data={
            "results": [
                {
                    "id": 222,
                    "title": "Python Bootcamp",
                    "url": f"/course/{slug}/",
                    "visible_instructors": [{"title": "Jane Doe"}],
                },
            ]
        }
    )
    curriculum = FakeResponse(json_data={"results": []})
    fetcher = _make_fetcher(
        {
            f"/api-2.0/courses/?search={slug}&fields[course]=id,title,url,visible_instructors": exact_results,
            "/subscriber-curriculum-items/?page_size=1000&fields[lecture]=id,title,object_index,asset&fields[chapter]=id,title,object_index&fields[asset]=time_estimation,asset_type": curriculum,
        }
    )

    meta = fetcher.course_meta(course_url)

    assert meta["id"] == "222"


def test_course_meta_raises_instead_of_guessing_when_no_slug_matches():
    no_match_results = FakeResponse(
        json_data={
            "results": [
                {"id": 111, "title": "Unrelated Course A", "url": "/course/other-a/", "visible_instructors": []},
                {"id": 333, "title": "Unrelated Course B", "url": "/course/other-b/", "visible_instructors": []},
            ]
        }
    )
    fetcher = _make_fetcher({SEARCH_PATH: no_match_results})

    with pytest.raises(RuntimeError) as excinfo:
        fetcher.course_meta(COURSE_URL)

    message = str(excinfo.value)
    assert "real-slug" in message
    # Must not have silently fallen back to the first result's title only --
    # both candidate titles should be surfaced so a human can tell what Udemy
    # actually returned.
    assert "Unrelated Course A" in message
    assert "Unrelated Course B" in message


def test_course_meta_raises_on_slug_suffix_collision_instead_of_wrong_match():
    """Finding 3 regression: a suffix match like 'python-bootcamp' must not
    wrongly match '/course/complete-python-bootcamp/' -- only the exact final
    URL segment counts as a match.
    """
    suffix_collision_results = FakeResponse(
        json_data={
            "results": [
                {
                    "id": 999,
                    "title": "Complete Python Bootcamp",
                    "url": "/course/complete-python-bootcamp/",
                    "visible_instructors": [],
                },
            ]
        }
    )
    fetcher = _make_fetcher(
        {
            "/api-2.0/courses/?search=python-bootcamp&fields[course]=id,title,url,visible_instructors": (
                suffix_collision_results
            ),
        }
    )

    with pytest.raises(RuntimeError):
        fetcher.course_meta("https://www.udemy.com/course/python-bootcamp/")


def test_course_meta_matches_exact_slug_segment():
    exact_results = FakeResponse(
        json_data={
            "results": [
                {
                    "id": 999,
                    "title": "Complete Python Bootcamp",
                    "url": "/course/complete-python-bootcamp/",
                    "visible_instructors": [],
                },
                {
                    "id": 111,
                    "title": "Python Bootcamp",
                    "url": "/course/python-bootcamp/",
                    "visible_instructors": [],
                },
            ]
        }
    )
    curriculum = FakeResponse(json_data={"results": []})
    fetcher = _make_fetcher(
        {
            "/api-2.0/courses/?search=python-bootcamp&fields[course]=id,title,url,visible_instructors": (
                exact_results
            ),
            "/subscriber-curriculum-items/?page_size=1000&fields[lecture]=id,title,object_index,asset&fields[chapter]=id,title,object_index&fields[asset]=time_estimation,asset_type": (
                curriculum
            ),
        }
    )

    meta = fetcher.course_meta("https://www.udemy.com/course/python-bootcamp/")

    assert meta["id"] == "111"
    assert meta["title"] == "Python Bootcamp"


def test_course_meta_raises_clear_error_on_empty_results():
    empty_results = FakeResponse(json_data={"results": []})
    fetcher = _make_fetcher({SEARCH_PATH: empty_results})

    with pytest.raises(RuntimeError) as excinfo:
        fetcher.course_meta(COURSE_URL)

    assert "Could not resolve course" in str(excinfo.value)


@pytest.mark.parametrize("status", [401, 403])
def test_json_raises_session_expired_on_401_403(status):
    fetcher = _make_fetcher({"/some/path": FakeResponse(status=status)})

    with pytest.raises(SessionExpired):
        fetcher._json("/some/path")


def test_json_raises_runtime_error_on_other_non_ok_status():
    fetcher = _make_fetcher({"/some/path": FakeResponse(status=500)})

    with pytest.raises(RuntimeError):
        fetcher._json("/some/path")


def test_captions_returns_none_when_no_captions_present():
    payload = FakeResponse(json_data={"asset": {"captions": []}})
    fetcher = _make_fetcher(
        {
            "/lectures/1/?fields[lecture]=asset&fields[asset]=captions&fields[caption]=url,locale_id,title": payload,
        }
    )

    assert fetcher.captions("123", "1") is None


def test_captions_returns_text_when_present():
    caption_payload = FakeResponse(
        json_data={
            "asset": {
                "captions": [
                    {"url": "https://cdn.udemy.com/caption.vtt", "locale_id": "en_US", "title": "English"}
                ]
            }
        }
    )
    caption_text = FakeResponse(status=200, text_data="WEBVTT\n\n1\n00:00:01.000 --> 00:00:02.000\nhi\n")
    fetcher = _make_fetcher(
        {
            "/lectures/1/?fields[lecture]=asset&fields[asset]=captions&fields[caption]=url,locale_id,title": caption_payload,
            "https://cdn.udemy.com/caption.vtt": caption_text,
        }
    )

    result = fetcher.captions("123", "1")

    assert result == "WEBVTT\n\n1\n00:00:01.000 --> 00:00:02.000\nhi\n"
