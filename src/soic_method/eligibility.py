"""Course- and module-level rules eligibility.

Course granularity alone is insufficient: Level 6 is eligible but contains
guest-taught modules, and one of those guests also appears in the excluded
Super Investors course.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from .models import LessonRecord


class Eligibility:
    def __init__(self, courses: Dict[str, dict], excluded_modules: List[str]):
        self._courses = courses
        self._excluded = [m.casefold() for m in excluded_modules]

    def is_eligible(self, course_title: str, module_title: str) -> bool:
        entry = self._courses.get(course_title)
        if entry is None or not entry.get("eligible", False):
            return False           # unlisted defaults to ineligible
        mod = (module_title or "").casefold()
        return not any(x in mod for x in self._excluded)

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
