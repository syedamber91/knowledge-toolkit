"""Pydantic models describing the captured course structure.

The shape mirrors a typical LMS hierarchy: a Course contains Modules, and each
Module contains Lessons. Only legitimately displayed text is stored — never
media files.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class Lesson(BaseModel):
    title: str
    url: str
    # Free-text body the portal renders for the lesson (description/notes/transcript).
    body_text: str = ""
    # URL of a captions/subtitle track, only if the portal openly exposes one.
    captions_url: Optional[str] = None
    # Links to attached resources (PDFs etc.) the portal exposes.
    resource_links: List[str] = Field(default_factory=list)
    # Optional short bullet "key points" derived from body_text for the mind map.
    key_points: List[str] = Field(default_factory=list)
    crawled_at: Optional[datetime] = None


class Module(BaseModel):
    title: str
    url: Optional[str] = None
    lessons: List[Lesson] = Field(default_factory=list)


class Course(BaseModel):
    title: str
    url: Optional[str] = None
    modules: List[Module] = Field(default_factory=list)


class Catalog(BaseModel):
    """Top-level container persisted to data/content.json."""

    base_url: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    courses: List[Course] = Field(default_factory=list)

    def lesson_urls(self) -> set[str]:
        """All lesson URLs already captured — used to make crawls resumable."""
        urls: set[str] = set()
        for course in self.courses:
            for module in course.modules:
                for lesson in module.lessons:
                    urls.add(lesson.url)
        return urls
