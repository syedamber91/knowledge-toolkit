"""Pydantic models describing a captured Udemy course.

Only transcript text and openly-rendered metadata are stored — never media.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class UdemyLecture(BaseModel):
    id: str
    title: str
    url: str
    duration_seconds: Optional[int] = None
    section_title: str = ""
    # Cleaned, timestamped transcript text. Empty when no captions exist.
    transcript: str = ""
    # False means "we looked and there were no captions" — never "not checked".
    has_transcript: bool = False
    captured_at: Optional[datetime] = None


class UdemySection(BaseModel):
    title: str
    order: int = 0
    lectures: List[UdemyLecture] = Field(default_factory=list)


class UdemyCourse(BaseModel):
    id: str
    title: str
    url: str
    instructor: str = ""
    sections: List[UdemySection] = Field(default_factory=list)

    def lectures(self) -> List[UdemyLecture]:
        return [lec for section in self.sections for lec in section.lectures]


class UdemyCatalog(BaseModel):
    """Top-level container persisted to data/udemy.json."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    courses: List[UdemyCourse] = Field(default_factory=list)
    # Lectures we've already dealt with, including ones that had no captions,
    # so a resumed crawl doesn't retry them forever.
    seen_lecture_ids: List[str] = Field(default_factory=list)

    def known_ids(self) -> set:
        ids = set(self.seen_lecture_ids)
        for course in self.courses:
            for lecture in course.lectures():
                ids.add(lecture.id)
        return ids

    def total_lectures(self) -> int:
        return sum(len(course.lectures()) for course in self.courses)

    def upsert_course(self, course: UdemyCourse) -> None:
        for index, existing in enumerate(self.courses):
            if existing.id == course.id:
                self.courses[index] = course
                return
        self.courses.append(course)

    @classmethod
    def load(cls, path: Path) -> "UdemyCatalog":
        if not Path(path).exists():
            return cls()
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def save(self, path: Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(
            json.dumps(json.loads(self.model_dump_json()), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
