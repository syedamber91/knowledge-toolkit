"""Resumable Substack crawler over the publication JSON API.

The user's saved session cookie (from ``auth.login``) is sent with each request
so paid posts return their body. The HTTP fetcher is injectable so the crawl
logic is unit-testable without network access. The cache is written incrementally
so an interrupted crawl never loses captured posts.
"""

from __future__ import annotations

import json
import random
import time
import urllib.request
from typing import Callable, Optional

from rich.console import Console

from .config import CONTENT_PATH, STATE_PATH, channel_url, settings
from .extract import enrich, is_free_audience, post_from_api
from .models import Channel, SubstackCatalog

console = Console()

# A fetcher takes a URL and returns parsed JSON (a list or dict).
Fetcher = Callable[[str], object]

_ARCHIVE_PAGE = 12


def _load_cookie_header() -> str:
    if not STATE_PATH.exists():
        raise RuntimeError(
            "No saved session. Run `substack-toolkit login --handle <handle>` first."
        )
    state = json.loads(STATE_PATH.read_text())
    pairs = [
        f"{c['name']}={c['value']}"
        for c in state.get("cookies", [])
        if c.get("name") and c.get("value") is not None
    ]
    return "; ".join(pairs)


def _default_fetcher(cookie_header: str) -> Fetcher:
    def fetch(url: str):
        req = urllib.request.Request(
            url,
            headers={
                "Cookie": cookie_header,
                "User-Agent": "Mozilla/5.0 (personal-knowledge-archive)",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    return fetch


def _load_catalog() -> SubstackCatalog:
    if CONTENT_PATH.exists():
        return SubstackCatalog.model_validate_json(CONTENT_PATH.read_text())
    return SubstackCatalog()


def _save_catalog(catalog: SubstackCatalog) -> None:
    CONTENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTENT_PATH.write_text(catalog.model_dump_json(indent=2))


def list_post_slugs(
    fetch: Fetcher,
    handle: str,
    limit: Optional[int],
    free_only: bool = False,
) -> list[str]:
    """Enumerate post slugs newest-first by paging the archive endpoint.

    When ``free_only`` is set, paid posts are filtered out using the ``audience``
    the archive already reports — so we never even fetch their (preview-only)
    bodies. Useful for publications you follow but do not pay for.
    """
    base = channel_url(handle)
    slugs: list[str] = []
    offset = 0
    while True:
        items = fetch(f"{base}/api/v1/archive?sort=new&limit={_ARCHIVE_PAGE}&offset={offset}")
        if not items:
            break
        for item in items:
            slug = item.get("slug")
            if not slug:
                continue
            if free_only and not is_free_audience(item.get("audience")):
                continue
            slugs.append(slug)
        if limit and len(slugs) >= limit:
            return slugs[:limit]
        offset += _ARCHIVE_PAGE
    return slugs


def crawl(
    handle: str,
    limit: Optional[int] = None,
    fetch: Optional[Fetcher] = None,
    free_only: bool = False,
) -> SubstackCatalog:
    """Capture new posts for ``handle`` into the cache (resumable).

    Set ``free_only`` to skip paid posts entirely (handy for publications you
    follow but are not a paying subscriber of, where paid posts would only yield
    truncated previews).
    """
    if fetch is None:
        fetch = _default_fetcher(_load_cookie_header())

    catalog = _load_catalog()
    channel = catalog.get_channel(handle)
    if channel is None:
        channel = Channel(handle=handle, url=channel_url(handle))
        catalog.channels.append(channel)
    existing = {p.url for p in channel.posts}

    slugs = list_post_slugs(fetch, handle, limit, free_only=free_only)
    new_count = 0
    for slug in slugs:
        url_guess = f"{channel_url(handle)}/p/{slug}"
        if url_guess in existing:
            continue
        try:
            detail = fetch(f"{channel_url(handle)}/api/v1/posts/{slug}")
            post = enrich(post_from_api(detail, handle))
        except Exception as exc:  # noqa: BLE001 - one bad post must not abort the crawl
            console.print(f"  [yellow]skipped {slug}: {exc}[/yellow]")
            continue
        if post.url in existing:
            continue
        channel.posts.append(post)
        existing.add(post.url)
        new_count += 1
        _save_catalog(catalog)  # incremental — survive interruption
        flag = " [paid]" if post.is_paid and not post.body_accessible else ""
        console.print(f"  captured: {post.title}{flag}")
        time.sleep(random.uniform(settings.crawl_min_delay, settings.crawl_max_delay))

    _save_catalog(catalog)
    console.print(f"[green]Done.[/green] {new_count} new post(s) for {handle}.")
    return catalog
