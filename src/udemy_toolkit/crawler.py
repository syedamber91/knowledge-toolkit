"""Walk one course's lectures and capture their transcripts.

Resumable and polite by design: the catalog is saved after every single
lecture, already-handled lectures are skipped on a re-run, and a random delay
separates network calls. All network access arrives through the injected
``fetcher`` seam, so this module is fully testable offline.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from .config import CATALOG_PATH, settings
from .curriculum import parse_curriculum
from .extract import captions_to_transcript
from .models import UdemyCatalog, UdemyCourse, UdemySection


class SessionExpired(RuntimeError):
    """Raised when the saved Udemy session no longer authenticates."""


@dataclass
class CrawlSummary:
    course_title: str
    captured: int = 0
    skipped_no_captions: int = 0
    already_seen: int = 0


def crawl_course(
    course_url: str,
    fetcher,
    catalog_path: Path = CATALOG_PATH,
    limit: Optional[int] = None,
    sleep: Callable[[float], None] = time.sleep,
    on_resolved: Optional[Callable[[str], None]] = None,
) -> CrawlSummary:
    """Capture transcripts for one course, resuming from any previous run.

    ``on_resolved``, if given, is called with the resolved course title as
    soon as ``course_meta`` returns -- before any lecture is crawled -- so a
    caller can show the human what is about to be captured.
    """
    catalog = UdemyCatalog.load(catalog_path)
    known = catalog.known_ids()

    meta = fetcher.course_meta(course_url)
    if on_resolved is not None:
        on_resolved(meta["title"])
    parsed = parse_curriculum(
        meta["curriculum"],
        course_id=meta["id"],
        course_title=meta["title"],
        course_url=course_url,
        instructor=meta.get("instructor", ""),
    )

    # Start from what we already have for this course so a resumed run keeps
    # previously captured transcripts instead of blanking them.
    existing = next((c for c in catalog.courses if c.id == parsed.id), None)
    previous = {lec.id: lec for lec in existing.lectures()} if existing else {}

    # Build the course shell with the current section layout but no lectures
    # yet -- lectures are appended one at a time below so the catalog on disk
    # grows incrementally rather than jumping straight to the full course.
    course = UdemyCourse(
        id=parsed.id,
        title=parsed.title,
        url=parsed.url,
        instructor=parsed.instructor,
        sections=[UdemySection(title=s.title, order=s.order) for s in parsed.sections],
    )
    catalog.upsert_course(course)
    summary = CrawlSummary(course_title=course.title)
    processed = 0

    limit_reached = False

    for section, target_section in zip(parsed.sections, course.sections):
        for lecture in section.lectures:
            # `known` is the union of every previously-seen lecture id
            # (captured or recorded as captionless) across this catalog, so
            # any lecture that was already handled in a prior run is caught
            # here -- this is what preserves previously captured lectures
            # under a small --limit on a re-crawl: they're re-appended via
            # `previous.get(...)` before `limit` is ever consulted below,
            # since only genuinely NEW lectures reach the limit check.
            if lecture.id in known:
                summary.already_seen += 1
                target_section.lectures.append(previous.get(lecture.id, lecture))
                continue
            if limit_reached:
                # `limit` only bounds how many NEW lectures get FETCHED.
                continue
            if limit is not None and processed >= limit:
                limit_reached = True
                continue

            raw = fetcher.captions(course.id, lecture.id)
            processed += 1
            if raw:
                lecture.transcript = captions_to_transcript(raw)
                lecture.has_transcript = bool(lecture.transcript)
            if lecture.has_transcript:
                summary.captured += 1
            else:
                # Looked, found nothing. Record it so a resume never retries.
                lecture.transcript = ""
                summary.skipped_no_captions += 1
                if lecture.id not in catalog.seen_lecture_ids:
                    catalog.seen_lecture_ids.append(lecture.id)
            lecture.captured_at = datetime.now(timezone.utc)

            target_section.lectures.append(lecture)
            catalog.save(catalog_path)
            sleep(random.uniform(settings.crawl_min_delay, settings.crawl_max_delay))

    catalog.save(catalog_path)
    return summary
