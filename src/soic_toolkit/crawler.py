"""Walk the membership content using the saved session and capture lesson text.

The crawl is polite (randomized delays, sequential) and resumable (lessons
already present in ``data/content.json`` are skipped). Because the live Learnyst
DOM is only knowable once logged in, the discovery selectors are centralized in
``SELECTORS`` below and should be tuned after inspecting a real lesson page.
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin, urlparse

from playwright.sync_api import BrowserContext, Page
from rich.console import Console

from .auth import authenticated_context
from .config import CONTENT_PATH, ensure_dirs, settings
from .extract import extract_lesson
from .models import Catalog, Course, Lesson, Module

console = Console()

# --- Discovery hints -------------------------------------------------------
# Tune these once the real portal DOM is confirmed while logged in.
SELECTORS = {
    # Anchors on the dashboard that lead to enrolled courses.
    "course_links": "a[href*='/learn/'], a[class*='course'] a[href], .course-card a[href]",
    # Within a course page: section/module headings and lesson links.
    "module_headings": "h2, h3, .section-title, [class*='section'] [class*='title']",
    "lesson_links": "a[href*='lesson'], a[href*='/learn/'][href*='content'], li a[href]",
}

# href substrings that strongly indicate an individual lesson page.
_LESSON_HINTS = ("lesson", "content", "topic", "video")


def load_catalog() -> Catalog:
    if CONTENT_PATH.exists():
        return Catalog.model_validate_json(CONTENT_PATH.read_text(encoding="utf-8"))
    return Catalog(base_url=settings.base_url)


def save_catalog(catalog: Catalog) -> None:
    ensure_dirs()
    CONTENT_PATH.write_text(
        catalog.model_dump_json(indent=2), encoding="utf-8"
    )


def _polite_sleep() -> None:
    time.sleep(random.uniform(settings.crawl_min_delay, settings.crawl_max_delay))


def _same_site(url: str, base: str) -> bool:
    return urlparse(url).netloc in ("", urlparse(base).netloc)


def _collect_links(page: Page, selector: str) -> list[tuple[str, str]]:
    """Return (text, absolute_url) pairs for anchors matching ``selector``."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for el in page.query_selector_all(selector):
        href = el.get_attribute("href")
        if not href:
            continue
        abs_url = urljoin(page.url, href)
        if not _same_site(abs_url, settings.base_url) or abs_url in seen:
            continue
        seen.add(abs_url)
        out.append(((el.inner_text() or "").strip(), abs_url))
    return out


def discover_courses(page: Page) -> list[Course]:
    page.goto(settings.base_url.rstrip("/"), wait_until="domcontentloaded")
    _polite_sleep()
    courses: list[Course] = []
    seen: set[str] = set()
    for text, url in _collect_links(page, SELECTORS["course_links"]):
        if url in seen:
            continue
        seen.add(url)
        courses.append(Course(title=text or url, url=url))
    return courses


def discover_modules_and_lessons(page: Page, course: Course) -> None:
    """Populate ``course.modules`` from its course page (best-effort grouping)."""
    if not course.url:
        return
    page.goto(course.url, wait_until="domcontentloaded")
    _polite_sleep()

    lesson_links = [
        (text, url)
        for text, url in _collect_links(page, SELECTORS["lesson_links"])
        if any(hint in url.lower() for hint in _LESSON_HINTS)
    ]
    # Without reliable section markers we group everything under one module;
    # refine here once real module headings are confirmed.
    module = Module(title=course.title, url=course.url)
    for text, url in lesson_links:
        module.lessons.append(Lesson(title=text or url, url=url))
    course.modules = [module]


def crawl(limit: Optional[int] = None) -> Catalog:
    """Discover structure and capture text for any not-yet-seen lessons."""
    catalog = load_catalog()
    already = catalog.lesson_urls()
    captured = 0

    with authenticated_context() as context:  # type: BrowserContext
        page = context.new_page()

        if not catalog.courses:
            console.print("[bold]Discovering courses…[/bold]")
            catalog.courses = discover_courses(page)
            for course in catalog.courses:
                console.print(f"  • {course.title}")
                discover_modules_and_lessons(page, course)
            save_catalog(catalog)

        for course in catalog.courses:
            for module in course.modules:
                for lesson in module.lessons:
                    if lesson.url in already and lesson.body_text:
                        continue
                    if limit is not None and captured >= limit:
                        save_catalog(catalog)
                        console.print(f"[green]Reached limit of {limit} lessons.[/green]")
                        return catalog
                    try:
                        page.goto(lesson.url, wait_until="domcontentloaded")
                        _polite_sleep()
                        data = extract_lesson(page.content(), lesson.url)
                        lesson.title = data["title"] or lesson.title
                        lesson.body_text = data["body_text"]
                        lesson.captions_url = data["captions_url"]
                        lesson.resource_links = data["resource_links"]
                        lesson.key_points = data["key_points"]
                        lesson.crawled_at = datetime.now(timezone.utc)
                        captured += 1
                        console.print(f"  [cyan]captured[/cyan] {lesson.title[:70]}")
                        save_catalog(catalog)  # incremental — resumable on crash
                    except Exception as exc:  # noqa: BLE001 — keep crawling past one bad page
                        console.print(f"  [red]skip[/red] {lesson.url}: {exc}")

    save_catalog(catalog)
    console.print(f"[green]Done. Captured {captured} new lesson(s).[/green]")
    return catalog
