"""Parse a lesson page's HTML into structured, legitimately-displayed text.

This module is deliberately framework-agnostic: it takes an HTML string and
returns plain data so it can be unit-tested against saved fixtures without a
live login. It extracts only text the page renders — it never fetches or
decodes media.
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

# Centralized hints for where lesson content tends to live. Learnyst's real DOM
# should be confirmed live and these tuned accordingly; we fall back gracefully.
_TITLE_SELECTORS = ["h1", "h2.lesson-title", ".lesson-title", "[class*='title']"]
_BODY_SELECTORS = [
    ".lesson-content",
    ".lesson-description",
    "[class*='description']",
    "article",
    "main",
]
_NOISE_TAGS = ["script", "style", "noscript", "nav", "header", "footer"]


def _clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def _first_match_text(soup: BeautifulSoup, selectors: list[str]) -> str:
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            txt = _clean_text(el.get_text("\n"))
            if txt:
                return txt
    return ""


def extract_title(soup: BeautifulSoup) -> str:
    title = _first_match_text(soup, _TITLE_SELECTORS)
    if title:
        # Titles are single-line; collapse any stray newlines.
        return _clean_text(title.split("\n")[0])
    if soup.title and soup.title.string:
        return _clean_text(soup.title.string)
    return "Untitled lesson"


def extract_body(soup: BeautifulSoup) -> str:
    for tag in soup(_NOISE_TAGS):
        tag.decompose()
    body = _first_match_text(soup, _BODY_SELECTORS)
    if body:
        return body
    # Fall back to the whole document text if no content container matched.
    return _clean_text(soup.get_text("\n"))


def extract_captions_url(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    track = soup.select_one("track[kind='captions'], track[kind='subtitles']")
    if track and track.get("src"):
        return urljoin(base_url, track["src"])
    return None


def extract_resource_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    links: list[str] = []
    for a in soup.select("a[href]"):
        href = a["href"]
        if re.search(r"\.(pdf|docx?|pptx?|xlsx?|csv)(\?|$)", href, re.IGNORECASE):
            links.append(urljoin(base_url, href))
    # De-duplicate while preserving order.
    seen: set[str] = set()
    return [x for x in links if not (x in seen or seen.add(x))]


def derive_key_points(body_text: str, max_points: int = 6) -> list[str]:
    """Simple extractive key points: the most substantial early sentences/lines.

    A lightweight heuristic so the mind map stays readable. Can be swapped for
    LLM summarization later.
    """
    candidates: list[str] = []
    for line in body_text.split("\n"):
        line = line.strip(" \t-•*")
        if 25 <= len(line) <= 220:
            candidates.append(line)
        if len(candidates) >= max_points:
            break
    return candidates


def extract_lesson(html: str, url: str) -> dict:
    """Return a dict of legitimately-displayed lesson fields parsed from ``html``."""
    soup = BeautifulSoup(html, "lxml")
    body = extract_body(soup)
    return {
        "title": extract_title(soup),
        "url": url,
        "body_text": body,
        "captions_url": extract_captions_url(soup, url),
        "resource_links": extract_resource_links(soup, url),
        "key_points": derive_key_points(body),
    }
