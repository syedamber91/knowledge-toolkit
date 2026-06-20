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


# ---------------------------------------------------------------------------
# Learnyst "Bodhi" portal helpers (learn.soic.in)
#
# The live portal renders everything in Shadow DOM via Bodhi web components, so
# the crawler reads already-rendered TEXT (see crawler.py / docs/PORTAL_NOTES.md)
# rather than HTML. These pure helpers normalize those rendered strings and are
# unit-tested against real captured samples. They capture only structure and the
# openly-rendered AI summary — never protected article bodies or video transcripts.
# ---------------------------------------------------------------------------

# "01 Important Membership Updates  4 lessons • 2 attachments"
# (rendered text sometimes omits spaces between the number and the title)
_SECTION_HEADER_RE = re.compile(
    r"^\s*(\d{1,3})\s*(.+?)\s*(\d+)\s*lessons?"
    r"(?:\s*[•·]\s*(\d+)\s*attachments?)?\s*$",
    re.IGNORECASE,
)

# "Video • 4m 30s" | "Article • attachment" | "Article •" | "video • 12m"
_LESSON_META_RE = re.compile(
    r"\b(video|article|quiz|pdf|live)\b\s*(?:[•·]\s*(.*))?$",
    re.IGNORECASE,
)

_DURATION_RE = re.compile(
    r"\d{1,2}:\d{2}(?::\d{2})?"                        # 4:30 or 1:04:30
    r"|(?:\d+\s*h\s*)?(?:\d+\s*m(?:in)?\s*)?\d+\s*s"   # compound ending in seconds (4m 30s)
    r"|(?:\d+\s*h\s*)?\d+\s*m(?:in)?"                  # hours/minutes (1h 5m, 5m)
    r"|\d+\s*h",                                        # hours only
    re.IGNORECASE,
)


def parse_section_header(text: str) -> Optional[dict]:
    """Parse a rendered syllabus section header into structured fields.

    Returns ``{"number", "title", "lesson_count", "attachment_count"}`` or None.
    """
    m = _SECTION_HEADER_RE.match((text or "").replace("\n", " ").strip())
    if not m:
        return None
    return {
        "number": int(m.group(1)),
        "title": m.group(2).strip(),
        "lesson_count": int(m.group(3)),
        "attachment_count": int(m.group(4)) if m.group(4) else 0,
    }


def parse_lesson_meta(text: str) -> dict:
    """Parse a lesson row's type/duration/attachment from its rendered text.

    Accepts either the full row ("Must Watch Intro Video Video • 4m 30s") or just
    the meta tail ("Video • 4m 30s"). Returns
    ``{"lesson_type", "duration", "has_attachment"}``.
    """
    raw = (text or "").replace("\n", " ").strip()
    m = _LESSON_META_RE.search(raw)
    lesson_type = (m.group(1).lower() if m else "")
    tail = (m.group(2).strip() if (m and m.group(2)) else "")
    has_attachment = "attachment" in tail.lower()
    dur = _DURATION_RE.search(tail)
    duration = dur.group(0).strip() if dur else None
    return {
        "lesson_type": lesson_type or None,
        "duration": duration,
        "has_attachment": has_attachment,
    }


def clean_summary(text: str, watermark_lines: Optional[list[str]] = None) -> str:
    """Normalize a rendered AI-summary block.

    Strips the "Lesson summary generated by AI" header and any per-user watermark
    lines (e.g. the viewer's email / phone overlaid on the content).
    """
    if not text:
        return ""
    lines = []
    wm = [w.lower() for w in (watermark_lines or [])]
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        low = s.lower()
        if "summary generated by ai" in low:
            continue
        if any(w and w in low for w in wm):
            continue
        # Generic watermark heuristics: bare email or phone-only lines.
        if re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", s):
            continue
        if re.fullmatch(r"\+?\d[\d\s-]{7,}\d", s):
            continue
        lines.append(s)
    return _clean_text("\n".join(lines))
