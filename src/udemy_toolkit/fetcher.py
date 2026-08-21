"""The live implementation of the crawler's fetch seam.

This is the only module that performs network access. It asks for the course's
curriculum and for each lecture's *caption* asset. It never requests a video or
audio stream, and never touches DRM.

CAUTION -- unverified against a live account: the API paths below are Udemy's
current internal endpoints as of this writing and may have drifted by the time
you run this for real. They have NOT been exercised against a live logged-in
session as part of this change (that requires a human to complete interactive
login, which is out of scope here). Verify them on the first live run; if a
path 404s, open the course in a browser with DevTools' Network tab, read the
actual request the page makes, and fix the constant here. This is the only
file that should ever need that fix.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

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


class PlaywrightFetcher:
    """Implements ``course_meta`` and ``captions`` over an authenticated context."""

    def __init__(self, context):
        self._page = context.new_page()
        self._base = settings.base_url.rstrip("/")

    def _json(self, path: str) -> Dict[str, Any]:
        response = self._page.request.get(f"{self._base}{path}")
        if response.status in (401, 403):
            raise SessionExpired(
                "Udemy rejected the saved session. Run `udemy-toolkit login` again."
            )
        if not response.ok:
            raise RuntimeError(f"Udemy returned HTTP {response.status} for {path}")
        return response.json()

    def course_meta(self, course_url: str) -> Dict[str, Any]:
        slug = course_slug(course_url)
        found = self._json(
            f"/api-2.0/courses/?search={slug}&fields[course]=id,title,url,visible_instructors"
        )
        results = found.get("results") or []
        if not results:
            raise RuntimeError(f"Could not resolve course from URL: {course_url}")
        match = next(
            (r for r in results if r.get("url", "").strip("/").rsplit("/", 1)[-1] == slug),
            None,
        )
        if match is None:
            titles = ", ".join(repr(r.get("title", "")) for r in results)
            raise RuntimeError(
                f"Could not find a search result matching course slug {slug!r} "
                f"(requested via {course_url!r}). Refusing to guess -- found: {titles}."
            )
        course_id = str(match["id"])
        instructors = match.get("visible_instructors") or []
        curriculum = self._json(
            f"/api-2.0/courses/{course_id}/subscriber-curriculum-items/{_CURRICULUM_FIELDS}"
        )
        return {
            "id": course_id,
            "title": match.get("title") or slug,
            "instructor": ", ".join(i.get("title", "") for i in instructors),
            "curriculum": curriculum,
        }

    def captions(self, course_id: str, lecture_id: str) -> Optional[str]:
        payload = self._json(
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
        response = self._page.request.get(url)
        return response.text() if response.ok else None
