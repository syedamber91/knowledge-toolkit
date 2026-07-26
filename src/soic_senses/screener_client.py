"""Live financial data sense: fetch and parse screener.in's top-ratios grid.

This is the "senses" layer both the Venus Pipes and KEI Industries experiments
proved was missing: the persona wiki's frameworks tell you WHAT to check
(F10's growth-threshold rule, F13's P/E-vs-P/B gap), this fetches the CURRENT
numbers to check them against. Every number here is live, never a wiki value.
"""

from __future__ import annotations

from typing import Dict, Tuple, Union

import requests
from bs4 import BeautifulSoup

RatioValue = Union[float, Tuple[float, float]]

_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
_BASE_URL = "https://www.screener.in/company/{symbol}/{suffix}"


class CompanyNotFoundError(Exception):
    """Raised when neither the consolidated nor standalone screener.in page exists."""


class IncompleteRatiosError(Exception):
    """Raised when screener.in returns the right page shape but every ratio
    value is blank -- a data gap on screener's side for that company at
    this moment (confirmed live for Venus Pipes & Tubes: HTTP 200, correct
    company title, correct <li> rows, every <span class="number"> empty,
    reproduced on 3 separate fetches). This is "ran but produced nothing
    useful" and must raise, not return a dict that looks like a legitimate
    empty result -- the same discipline this project applies to every other
    wrapped data source (see CLAUDE.md's nse_none_streak convention).
    """


def _to_float(text: str) -> Union[float, None]:
    cleaned = text.replace(",", "").strip()
    if not cleaned:
        return None
    return float(cleaned)


def parse_top_ratios(html: str) -> Dict[str, RatioValue]:
    """Parse screener.in's `#top-ratios` list into {label: value}.

    Single-number ratios (Market Cap, Stock P/E, ROCE, ...) come back as a
    float. "High / Low" comes back as a (high, low) tuple since screener
    renders two numbers in one row. Raises IncompleteRatiosError if the
    container exists with number slots but every single one is blank.
    """
    soup = BeautifulSoup(html, "lxml")
    container = soup.find(id="top-ratios")
    if container is None:
        return {}

    ratios: Dict[str, RatioValue] = {}
    total_number_spans = 0
    parsed_count = 0
    for li in container.find_all("li"):
        name_el = li.find("span", class_="name")
        value_el = li.find("span", class_="value")
        if name_el is None or value_el is None:
            continue
        label = name_el.get_text(strip=True)
        number_spans = value_el.find_all("span", class_="number")
        total_number_spans += len(number_spans)
        numbers = [n for n in (_to_float(sp.get_text()) for sp in number_spans) if n is not None]
        parsed_count += len(numbers)
        if not numbers:
            continue
        ratios[label] = tuple(numbers) if len(numbers) > 1 else numbers[0]

    if total_number_spans > 0 and parsed_count == 0:
        raise IncompleteRatiosError(
            "screener.in page has the top-ratios structure but every value is blank"
        )
    return ratios


def fetch_screener_ratios(symbol: str) -> Dict[str, RatioValue]:
    """Fetch live top-ratios for an NSE symbol from screener.in.

    Tries the consolidated page first (matches how this session's other
    scrapers in the sibling project prefer consolidated financials), falling
    back to the standalone page. Raises CompanyNotFoundError if neither
    exists, rather than silently returning an empty dict (an empty result
    that looks structurally valid would be a "ran but produced nothing
    useful" failure mode).
    """
    consolidated_url = _BASE_URL.format(symbol=symbol, suffix="consolidated/")
    response = requests.get(consolidated_url, headers=_HEADERS, timeout=15)
    if response.status_code != 200:
        standalone_url = _BASE_URL.format(symbol=symbol, suffix="")
        response = requests.get(standalone_url, headers=_HEADERS, timeout=15)
        if response.status_code != 200:
            raise CompanyNotFoundError(
                f"No screener.in page found for {symbol!r} (tried consolidated and standalone)"
            )
    return parse_top_ratios(response.text)
