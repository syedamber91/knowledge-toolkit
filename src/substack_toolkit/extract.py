"""Convert Substack API JSON into Post models and enrich with topics.

Body HTML is converted to Markdown with ``markdownify`` so code blocks, headings,
lists and links survive. Only text the API returns is stored; media is left as
Markdown links, never downloaded.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional

from markdownify import markdownify as html_to_md

from .config import channel_url
from .models import Post
from .topics import keywords, match_topics

# Substack "audience" values that mean freely available to everyone.
# Any value NOT in this set is treated as paid (safe default for unknown values).
_FREE_AUDIENCES = {"", "everyone", "only_free"}


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    cleaned = raw.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        pass
    # Python 3.9's fromisoformat only accepts 3- or 6-digit fractional seconds.
    # Normalise any fractional part to 6 digits and retry.
    match = re.match(r"^(.*?)\.(\d+)(.*)$", cleaned)
    if match:
        head, frac, tail = match.groups()
        normalised = f"{head}.{frac[:6].ljust(6, '0')}{tail}"
        try:
            return datetime.fromisoformat(normalised)
        except ValueError:
            return None
    return None


def _author(data: dict[str, Any]) -> str:
    bylines = data.get("publishedBylines") or []
    if bylines and isinstance(bylines[0], dict):
        return bylines[0].get("name", "") or ""
    return ""


def post_from_api(data: dict[str, Any], handle: str) -> Post:
    """Build a Post from one Substack ``/api/v1/posts/<slug>`` JSON object."""
    body_html = data.get("body_html") or ""
    body_md = (
        html_to_md(body_html, heading_style="ATX", strip=["script", "style"]).strip()
        if body_html
        else ""
    )
    slug = data.get("slug", "") or ""
    url = data.get("canonical_url") or f"{channel_url(handle)}/p/{slug}"
    audience = data.get("audience", "") or ""
    is_paid = audience not in _FREE_AUDIENCES
    return Post(
        title=data.get("title") or "(untitled)",
        subtitle=data.get("subtitle") or "",
        slug=slug,
        url=url,
        author=_author(data),
        published_at=_parse_date(data.get("post_date")),
        is_paid=is_paid,
        body_accessible=bool(body_md),
        body_markdown=body_md,
        captured_at=datetime.now(timezone.utc),
    )


def enrich(post: Post) -> Post:
    """Attach canonical topics and secondary keyword tags (mutates and returns post)."""
    text = f"{post.title}\n{post.subtitle}\n{post.body_markdown}"
    post.topics = match_topics(text)
    post.keywords = keywords(text)
    return post
