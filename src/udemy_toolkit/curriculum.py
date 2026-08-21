"""Course URL and curriculum-payload parsing.

Pure functions: given the JSON a curriculum request returned, build the
section/lecture tree. No network access lives here, which is what lets the
crawler be tested entirely offline.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .models import UdemyCourse, UdemyLecture, UdemySection

_SLUG_RE = re.compile(r"/course/(?P<slug>[^/?#]+)")


def course_slug(url: str) -> str:
    """Extract the course slug from any Udemy course URL."""
    match = _SLUG_RE.search(url or "")
    if not match:
        raise ValueError(
            f"Not a Udemy course URL: {url!r}. "
            "Expected something like https://www.udemy.com/course/<slug>/"
        )
    return match.group("slug")


def _lecture_url(course_url: str, lecture_id: str) -> str:
    return f"{course_url.rstrip('/')}/learn/lecture/{lecture_id}"


def parse_curriculum(
    payload: Dict[str, Any],
    course_id: str,
    course_title: str,
    course_url: str,
    instructor: str = "",
) -> UdemyCourse:
    """Curriculum response -> ``UdemyCourse``; non-lecture items are dropped."""
    sections: List[UdemySection] = []
    current: Optional[UdemySection] = None

    for item in (payload or {}).get("results", []) or []:
        kind = item.get("_class")
        if kind == "chapter":
            current = UdemySection(
                title=item.get("title") or "Untitled section",
                order=int(item.get("object_index") or len(sections) + 1),
            )
            sections.append(current)
            continue
        if kind != "lecture":
            # Quizzes, practice tests, and coding exercises are out of scope.
            continue
        if current is None:
            current = UdemySection(title="Introduction", order=1)
            sections.append(current)
        asset = item.get("asset") or {}
        duration = asset.get("time_estimation")
        lecture_id = str(item.get("id"))
        current.lectures.append(
            UdemyLecture(
                id=lecture_id,
                title=item.get("title") or f"Lecture {lecture_id}",
                url=_lecture_url(course_url, lecture_id),
                duration_seconds=int(duration) if duration is not None else None,
                section_title=current.title,
            )
        )

    return UdemyCourse(
        id=str(course_id),
        title=course_title,
        url=course_url,
        instructor=instructor,
        sections=sections,
    )
