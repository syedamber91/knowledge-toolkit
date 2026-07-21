"""Course- and module-level rules eligibility.

Course granularity alone is insufficient: Level 6 is eligible but contains
guest-taught modules, and one of those guests also appears in the excluded
Super Investors course.
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

    def __init__(self, courses: Dict[str, dict], excluded_modules: List[str]):
        self._courses = courses
        self._excluded = [m.casefold() for m in excluded_modules]
        self._allowed: Dict[str, Optional[Set[str]]] = {}
        for title, entry in (courses or {}).items():
            allow = (entry or {}).get("modules_allowlist")
            self._allowed[title] = (
                None if allow is None else {m.casefold() for m in allow}
            )

    def is_eligible(self, course_title: str, module_title: str) -> bool:
        entry = self._courses.get(course_title)
        if entry is None or not entry.get("eligible", False):
            return False           # unlisted defaults to ineligible
        mod = (module_title or "").casefold()
        if any(x in mod for x in self._excluded):
            return False
        allow = self._allowed.get(course_title)
        if allow is None:
            return True            # course has not opted into module approval
        return mod in allow

    def fidelity(self, course_title: str) -> str:
        entry = self._courses.get(course_title) or {}
        return entry.get("transcript_fidelity", "verbatim")


def load_eligibility(path: Path) -> Eligibility:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Eligibility(data.get("courses") or {}, data.get("excluded_modules") or [])


def apply_eligibility(lessons: List[LessonRecord], elig: Eligibility) -> List[LessonRecord]:
    out: List[LessonRecord] = []
    for l in lessons:
        out.append(
            l.model_copy(
                update={
                    "eligible": elig.is_eligible(l.course_title, l.module_title),
                    "transcript_fidelity": elig.fidelity(l.course_title),
                }
            )
        )
    return out
