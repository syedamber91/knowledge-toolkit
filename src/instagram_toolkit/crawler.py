"""Instaloader-backed Instagram capture into the shared media catalog.

Captures CAPTION + METADATA ONLY — no images/videos are ever downloaded, and no
comment text is fetched (repo guardrail). Resumable via the shared catalog's URL
set; polite random delays. The network seam ``post_fetch`` is injectable, so the
crawl logic is unit-testable without Instaloader or a login.
"""

from __future__ import annotations

import random
import time
from typing import Callable, Iterable, Optional

from rich.console import Console

from media_core.models import MediaCatalog
from media_core.store import load_catalog as _load_catalog
from media_core.store import save_catalog as _save_catalog

from . import extract
from .config import settings

console = Console()

# A post_fetch takes a target (handle or hashtag) and yields normalized post dicts.
PostFetch = Callable[[str], Iterable[dict]]

# Instaloader exception names that mean "stop politely and resume later".
_BLOCK_NAMES = {
    "LoginRequiredException", "ConnectionException", "TooManyRequestsException",
    "QueryReturnedBadRequestException", "QueryReturnedForbiddenException",
    "ProfileNotExistsException",
}


def _make_loader():
    """An Instaloader configured to fetch NO media and NO comments."""
    import instaloader

    return instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        post_metadata_txt_pattern="",
        quiet=True,
    )


def _safe_field(post, name):
    """getattr that also tolerates a lazily-fetched Instaloader property
    raising mid-access (e.g. BadResponseException), not just a missing
    attribute. `comments` and `video_duration` fall back to a per-post
    single-shortcode GraphQL fetch when the initial timeline payload didn't
    include them, and that secondary fetch can be blocked/403'd independently
    of the rest of the post — which must not crash the whole crawl."""
    try:
        return getattr(post, name, None)
    except Exception:  # noqa: BLE001 - any failure in the lazy fetch, not just KeyError
        return None


def _normalize(post) -> dict:
    """Instaloader Post -> normalized dict (no *required* extra network requests)."""
    is_video = bool(getattr(post, "is_video", False))
    kind = "reel" if is_video else "p"
    return {
        "shortcode": post.shortcode,
        "url": f"https://www.instagram.com/{kind}/{post.shortcode}/",
        "caption": post.caption or "",
        "owner_username": post.owner_username,
        # Deliberately do NOT touch post.owner_profile — that triggers an extra
        # network fetch per post. Author falls back to the username downstream.
        "owner_fullname": "",
        "taken_at": post.date_utc,
        "is_video": is_video,
        "video_duration": _safe_field(post, "video_duration"),
        "likes": getattr(post, "likes", None),
        "comments": _safe_field(post, "comments"),
        "hashtags": list(getattr(post, "caption_hashtags", []) or []),
        "mentions": list(getattr(post, "caption_mentions", []) or []),
    }


def _profile_posts(handle: str):
    import instaloader

    from . import auth
    loader = _make_loader()
    auth.load_session_into(loader)
    profile = instaloader.Profile.from_username(loader.context, handle)
    for post in profile.get_posts():
        yield _normalize(post)


def _hashtag_posts(tag: str):
    import instaloader

    from . import auth
    loader = _make_loader()
    auth.load_session_into(loader)
    hashtag = instaloader.Hashtag.from_name(loader.context, tag.lstrip("#"))
    for post in hashtag.get_posts():
        yield _normalize(post)


def _reraise_as_block(exc: Exception) -> None:
    """Convert a genuine Instagram rate-limit/block error into a friendly message.

    Matches on Instaloader exception *types* (not loose substrings), so our own
    guidance errors — e.g. "run `instagram-toolkit login` first", which contains
    the word 'login' — propagate unchanged instead of being mislabelled a block.
    """
    name = type(exc).__name__
    text = str(exc).lower()
    is_block = (
        name in _BLOCK_NAMES
        or "429" in str(exc)
        or "too many requests" in text
        or "please wait" in text
        or "checkpoint_required" in text
    )
    if is_block:
        raise RuntimeError(
            f"Instagram rate-limited or blocked the request ({name}: {exc}). "
            "Progress is saved — wait a while, then re-run the same command to resume."
        ) from exc
    raise exc


def _run(posts: Iterable[dict], limit: Optional[int], label: str) -> MediaCatalog:
    catalog = _load_catalog()
    existing = catalog.item_urls()
    new_count = 0
    iterator = iter(posts)
    while True:
        try:
            data = next(iterator)
        except StopIteration:
            break
        except Exception as exc:  # noqa: BLE001 - block/login while iterating
            _save_catalog(catalog)
            _reraise_as_block(exc)
            break
        url = data.get("url")
        if not url or url in existing:
            continue
        item = extract.item_from_post(data)
        catalog.items.append(item)
        existing.add(item.url)
        new_count += 1
        _save_catalog(catalog)  # incremental — survive interruption
        console.print(f"  captured: {item.title}")
        if limit and new_count >= limit:
            break
        time.sleep(random.uniform(settings.crawl_min_delay, settings.crawl_max_delay))

    _save_catalog(catalog)
    console.print(f"[green]Done.[/green] {new_count} new Instagram item(s) from {label}.")
    return catalog


def crawl(handle: str, limit: Optional[int] = None,
          *, post_fetch: Optional[PostFetch] = None) -> MediaCatalog:
    """Capture a public profile's posts + reels (captions + metadata). Resumable."""
    handle = handle.lstrip("@")
    post_fetch = post_fetch or _profile_posts
    return _run(post_fetch(handle), limit, label=f"@{handle}")


def crawl_hashtag(tag: str, limit: Optional[int] = None,
                  *, post_fetch: Optional[PostFetch] = None) -> MediaCatalog:
    """Discover posts by hashtag (captions + metadata). Resumable."""
    tag = tag.lstrip("#")
    post_fetch = post_fetch or _hashtag_posts
    return _run(post_fetch(tag), limit, label=f"#{tag}")
