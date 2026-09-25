"""The live implementation of the crawler's fetch seam.

This is the only module that performs network access. It asks for the course's
curriculum and for each lecture's *caption* asset. It never requests a video or
audio stream, and never touches DRM.

Verified live against a real Udemy account (2026-08-22). Two things learned
that shaped this implementation, both about how requests are made rather than
what is requested:

* Udemy's Cloudflare bot-management protection 403s ("Just a moment...")
  ``page.request.get(...)``/XHR-style calls to ``/api-2.0/...`` even from a
  fully authenticated, headed, real-Chrome session -- and it 403s the SPA's
  *own* internal XHR calls too, not just ones this tool makes. Full top-level
  page navigations (``page.goto``) to the same JSON endpoints are NOT blocked
  and return the real payload. Every ``/api-2.0/`` call here therefore goes
  through ``page.goto`` + reading the rendered JSON, exactly like the working
  pattern in ``auth.session_is_valid()`` -- not a bot-detection bypass, just
  using the same request shape a human's page load already uses.
* The public course-search endpoint (``/api-2.0/courses/?search=...``) 500s
  regardless of query. Course resolution instead lists the user's own
  enrolled courses (``/api-2.0/users/me/subscribed-courses/``) and matches
  the slug locally -- which is also a better fit than a marketplace search,
  since it can only ever resolve to a course the user actually owns.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .config import settings
from .crawler import SessionExpired
from .curriculum import course_slug

_CURRICULUM_FIELDS = (
    "?page_size=1000"
    "&fields[lecture]=id,title,object_index,asset"
    "&fields[chapter]=id,title,object_index"
    "&fields[asset]=time_estimation,asset_type"
)
_CAPTION_FIELDS = "?fields[lecture]=asset&fields[asset]=captions&fields[caption]=url,locale_id,title"
_SUBSCRIBED_COURSES_PATH = (
    "/api-2.0/users/me/subscribed-courses/"
    "?fields[course]=id,title,url,visible_instructors&page_size=100"
)
_MAX_SUBSCRIBED_PAGES = 50  # backstop against a runaway "next" chain


class PlaywrightFetcher:
    """Implements ``course_meta`` and ``captions`` over an authenticated context."""

    def __init__(self, context):
        self._page = context.new_page()
        self._base = settings.base_url.rstrip("/")

    def _json_via_navigation(self, path_or_url: str) -> Dict[str, Any]:
        """GET a ``/api-2.0/`` endpoint via a real page navigation.

        A top-level navigation is not blocked by Udemy's Cloudflare
        protection the way an XHR/fetch-style request is (see module
        docstring) -- this is the load-bearing reason ``page.goto`` is used
        here instead of ``page.request.get``.
        """
        url = path_or_url if path_or_url.startswith("http") else f"{self._base}{path_or_url}"
        response = self._page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        status = response.status if response else 0
        if status in (401, 403):
            raise SessionExpired(
                "Udemy rejected the saved session. Run `udemy-toolkit login` again."
            )
        if status and not (200 <= status < 300):
            raise RuntimeError(f"Udemy returned HTTP {status} for {path_or_url}")
        try:
            return self._page.evaluate("() => JSON.parse(document.body.innerText)")
        except Exception as exc:
            raise RuntimeError(f"Udemy returned a non-JSON response for {path_or_url}") from exc

    def _list_subscribed_courses(self) -> List[Dict[str, Any]]:
        """All courses the user is enrolled in, following pagination."""
        courses: List[Dict[str, Any]] = []
        next_url: Optional[str] = _SUBSCRIBED_COURSES_PATH
        pages = 0
        while next_url and pages < _MAX_SUBSCRIBED_PAGES:
            payload = self._json_via_navigation(next_url)
            courses.extend(payload.get("results") or [])
            next_url = payload.get("next")
            pages += 1
        return courses

    def course_meta(self, course_url: str) -> Dict[str, Any]:
        slug = course_slug(course_url)
        courses = self._list_subscribed_courses()
        if not courses:
            raise RuntimeError(
                f"Could not resolve course from URL: {course_url} "
                "(your account has no enrolled courses)"
            )

        def _slug_of(url: str) -> Optional[str]:
            parts = [p for p in (url or "").strip("/").split("/") if p]
            return parts[1] if len(parts) >= 2 and parts[0] == "course" else None

        match = next((c for c in courses if _slug_of(c.get("url", "")) == slug), None)
        if match is None:
            titles = ", ".join(repr(c.get("title", "")) for c in courses)
            raise RuntimeError(
                f"Could not find an enrolled course matching slug {slug!r} "
                f"(requested via {course_url!r}). Refusing to guess -- your "
                f"enrolled courses are: {titles}."
            )
        course_id = str(match["id"])
        instructors = match.get("visible_instructors") or []
        curriculum = self._json_via_navigation(
            f"/api-2.0/courses/{course_id}/subscriber-curriculum-items/{_CURRICULUM_FIELDS}"
        )
        return {
            "id": course_id,
            "title": match.get("title") or slug,
            "instructor": ", ".join(i.get("title", "") for i in instructors),
            "curriculum": curriculum,
        }

    def captions(self, course_id: str, lecture_id: str) -> Optional[str]:
        payload = self._json_via_navigation(
            f"/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}/{_CAPTION_FIELDS}"
        )
        captions = ((payload or {}).get("asset") or {}).get("captions") or []
        if not captions:
            return None
        chosen = next(
            (c for c in captions if str(c.get("locale_id", "")).lower().startswith("en")),
            captions[0],
        )
        url = chosen.get("url")
        if not url:
            return None
        # The caption file itself lives on a CDN host (not www.udemy.com), and
        # a plain request there is not subject to the same bot-management
        # wall as the api-2.0 host -- verified live.
        response = self._page.request.get(url)
        return response.text() if response.ok else None
