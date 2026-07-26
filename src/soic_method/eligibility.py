"""Course-, module-, and lesson-level rules eligibility.

Course granularity alone is insufficient: Level 6 is eligible but contains
guest-taught modules, and one of those guests also appears in the excluded
Super Investors course.

Module granularity alone is ALSO insufficient (found in the A3 corpus-wide
scan): "SOIC Labs: Become an AI-Powered Investor" is a legitimate,
Ishmohit-taught module whose one exception -- "Stocks Dashboard with Dr.
Shashank" -- is an SOIC community member (an anesthesiologist, not staff,
not Ishmohit) presenting a tool he personally built. Excluding the whole
module would discard four good lessons to keep out one guest lesson;
including it would repeat exactly the Sajal Kapoor failure one level down.
Hence ``excluded_lessons``, matched the same way as ``excluded_modules``
(case-insensitive substring of the lesson title).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

from .models import LessonRecord


class Eligibility:
    """Course allow-list + module deny-list, plus an OPTIONAL per-course
    module allow-list.

    A course may declare ``modules_allowlist``, which flips that course from
    "every module is eligible unless denied" to "modules must be
    individually approved" -- i.e. an unlisted module inside it is
    INELIGIBLE, matching the global constraint that unclassified eligibility
    defaults to ineligible for courses AND modules alike.

    The deny-list is not replaced by it and still wins: an allow-listed
    module that also matches an exclusion stays out, so a course can be
    module-classified without having to keep the two lists mutually
    consistent by hand.

    Courses that declare no allow-list keep the previous behaviour
    unchanged. That is deliberate rather than a compromise: 46 of the 86
    modules inside eligible courses have never had the per-module
    classification pass that Level 6 got, and silently excluding them the
    moment this shipped would misreport a corpus-coverage decision as a code
    change (final-branch-review.md I3). The mechanism now exists; opting each
    remaining course in is a human classification pass, one course at a time.
    """

    def __init__(
        self,
        courses: Dict[str, dict],
        excluded_modules: List[str],
        excluded_lessons: Optional[List[str]] = None,
    ):
        self._courses = courses
        self._excluded = [m.casefold() for m in excluded_modules]
        self._excluded_lessons = [t.casefold() for t in (excluded_lessons or [])]
        self._allowed: Dict[str, Optional[Set[str]]] = {}
        for title, entry in (courses or {}).items():
            allow = (entry or {}).get("modules_allowlist")
            self._allowed[title] = (
                None if allow is None else {m.casefold() for m in allow}
            )

    def is_eligible(
        self,
        course_title: str,
        module_title: str,
        lesson_title: Optional[str] = None,
    ) -> bool:
        entry = self._courses.get(course_title)
        if entry is None or not entry.get("eligible", False):
            return False           # unlisted defaults to ineligible
        mod = (module_title or "").casefold()
        if any(x in mod for x in self._excluded):
            return False
        allow = self._allowed.get(course_title)
        if allow is not None and mod not in allow:
            return False
        if lesson_title is not None:
            les = lesson_title.casefold()
            if any(x in les for x in self._excluded_lessons):
                return False       # a guest lesson inside an otherwise-fine module
        return True

    def fidelity(self, course_title: str) -> str:
        entry = self._courses.get(course_title) or {}
        return entry.get("transcript_fidelity", "verbatim")


def load_eligibility(path: Path) -> Eligibility:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Eligibility(
        data.get("courses") or {},
        data.get("excluded_modules") or [],
        data.get("excluded_lessons") or [],
    )


def apply_eligibility(lessons: List[LessonRecord], elig: Eligibility) -> List[LessonRecord]:
    out: List[LessonRecord] = []
    for l in lessons:
        out.append(
            l.model_copy(
                update={
                    "eligible": elig.is_eligible(
                        l.course_title, l.module_title, l.title
                    ),
                    "transcript_fidelity": elig.fidelity(l.course_title),
                }
            )
        )
    return out
