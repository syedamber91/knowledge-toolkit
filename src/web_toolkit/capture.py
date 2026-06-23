"""Capture readable web articles into the media catalog.

Uses trafilatura to strip nav/ads/boilerplate and return the main article as
Markdown plus metadata (title, author, date, site). The HTML fetch is injectable
so extraction is unit-testable from a fixed HTML string without network access.
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone
from typing import Callable, Optional
from urllib.parse import urlparse

from rich.console import Console

from media_core.config import settings
from media_core.models import KIND_ARTICLE, MediaCatalog, MediaItem
from media_core.store import load_catalog, save_catalog
from media_core.topics import keywords, match_topics

console = Console()


def fetch_html(url: str) -> str:
    """Download raw HTML for a URL (trafilatura's fetcher)."""
    import trafilatura

    return trafilatura.fetch_url(url) or ""


def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw[:len(fmt) + 2] if "T" in fmt else raw[:10],
                                     fmt).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def item_from_html(url: str, html: str) -> Optional[MediaItem]:
    """Extract a readable article MediaItem from HTML, or None if not extractable."""
    import trafilatura

    if not html:
        return None
    body = trafilatura.extract(
        html, output_format="markdown",
        include_comments=False, include_tables=True, include_links=True,
    )
    meta = trafilatura.extract_metadata(html)
    title = (getattr(meta, "title", None) if meta else None) or url
    canonical = (getattr(meta, "url", None) if meta else None) or url
    site = (getattr(meta, "sitename", None) if meta else None) or _domain(canonical)
    author = (getattr(meta, "author", None) if meta else None) or ""
    description = (getattr(meta, "description", None) if meta else None) or ""
    date = getattr(meta, "date", None) if meta else None

    item = MediaItem(
        kind=KIND_ARTICLE,
        title=title,
        url=canonical,
        source=site,
        source_id=_domain(canonical),
        author=author,
        published_at=_parse_date(date),
        description=description.strip(),
        body_markdown=(body or "").strip(),
        body_accessible=bool(body),
    )
    text = f"{item.title}\n{item.description}\n{item.body_markdown}"
    item.topics = match_topics(text)
    item.keywords = keywords(text)
    item.captured_at = datetime.now(timezone.utc)
    return item


HtmlFetch = Callable[[str], str]


def capture_urls(
    urls: list[str],
    *,
    html_fetch: Optional[HtmlFetch] = None,
) -> MediaCatalog:
    """Capture a batch of article URLs into the shared catalog (resumable)."""
    html_fetch = html_fetch or fetch_html
    catalog = load_catalog()
    existing = catalog.item_urls()

    new_count = 0
    for url in urls:
        url = url.strip()
        if not url or url in existing:
            continue
        html = html_fetch(url)
        item = item_from_html(url, html)
        if item is None:
            console.print(f"  [yellow]skipped {url}: not extractable[/yellow]")
            continue
        if item.url in existing:
            continue
        catalog.items.append(item)
        existing.add(item.url)
        new_count += 1
        save_catalog(catalog)  # incremental
        flag = "" if item.body_accessible else " [no body]"
        console.print(f"  captured: {item.title}{flag}")
        time.sleep(random.uniform(settings.capture_min_delay, settings.capture_max_delay))

    save_catalog(catalog)
    console.print(f"[green]Done.[/green] {new_count} new article(s).")
    return catalog
