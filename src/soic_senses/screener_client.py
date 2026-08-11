"""Live financial data sense: fetch and parse screener.in's top-ratios grid.

This is the "senses" layer both the Venus Pipes and KEI Industries experiments
proved was missing: the persona wiki's frameworks tell you WHAT to check
(F10's growth-threshold rule, F13's P/E-vs-P/B gap), this fetches the CURRENT
numbers to check them against. Every number here is live, never a wiki value.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Union

import requests
from bs4 import BeautifulSoup

RatioValue = Union[float, Tuple[float, float]]

# One statement row -> {period label: value}. e.g. {"CFO/OP": {"Mar 2026": 92.0}}
StatementRows = Dict[str, Dict[str, float]]

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
    return parse_top_ratios(_fetch_company_html(symbol))


def _fetch_company_html(symbol: str) -> str:
    """Fetch a screener.in company page, consolidated first then standalone."""
    consolidated_url = _BASE_URL.format(symbol=symbol, suffix="consolidated/")
    response = requests.get(consolidated_url, headers=_HEADERS, timeout=15)
    if response.status_code != 200:
        standalone_url = _BASE_URL.format(symbol=symbol, suffix="")
        response = requests.get(standalone_url, headers=_HEADERS, timeout=15)
        if response.status_code != 200:
            raise CompanyNotFoundError(
                f"No screener.in page found for {symbol!r} (tried consolidated and standalone)"
            )
    return response.text


# --------------------------------------------------------------------------
# Statement tables (profit-loss / balance-sheet / cash-flow / ratios / quarters)
#
# The top-ratios grid parsed above carries only price-level facts. The gating
# metrics F21 (cash conversion), F22 (DuPont), F27 (leverage) and F10/F18/F25
# (growth) actually need are in screener's statement sections -- which it
# already renders as plain server-side HTML on the same page. Every value below
# is READ from a row screener publishes; none is derived from a convention this
# project invented. Notably screener computes `CFO/OP` itself, so F21's
# cash-conversion metric needs no numerator/denominator choice of our own.
# --------------------------------------------------------------------------


@dataclass
class ScreenerStatements:
    profit_loss: StatementRows
    balance_sheet: StatementRows
    cash_flow: StatementRows
    ratios: StatementRows
    quarters: StatementRows
    growth: StatementRows  # {"Compounded Sales Growth": {"3 Years": 6.0}}
    top_ratios: Dict[str, RatioValue] = field(default_factory=dict)


def _norm_label(text: str) -> str:
    """Screener labels carry nbsp padding and a trailing '+' expander glyph."""
    return text.replace("\xa0", " ").strip().rstrip("+").strip()


def _to_number(text: str) -> Optional[float]:
    cleaned = text.replace(",", "").replace("%", "").replace("\xa0", "").strip()
    if not cleaned or cleaned in {"-", "—"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_statement_section(html: str, section_id: str) -> StatementRows:
    """Parse one screener statement section into {row label: {period: value}}.

    Returns {} when the section is absent, rather than raising -- an absent
    section is a normal shape for some companies (e.g. a bank has no
    'Operating Profit' row), and the caller decides whether that matters.
    """
    soup = BeautifulSoup(html, "lxml")
    section = soup.find(id=section_id)
    if section is None:
        return {}
    table = section.find("table")
    if table is None or table.find("thead") is None:
        return {}

    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    periods = headers[1:]  # first header cell is the row-label column

    rows: StatementRows = {}
    body = table.find("tbody")
    if body is None:
        return {}
    for tr in body.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 2:
            continue
        label = _norm_label(cells[0].get_text())
        if not label:
            continue
        values: Dict[str, float] = {}
        for period, cell in zip(periods, cells[1:]):
            number = _to_number(cell.get_text())
            if number is not None:
                values[period] = number
        if values:
            rows[label] = values
    return rows


def parse_growth_tables(html: str) -> StatementRows:
    """Parse screener's `table.ranges-table` blocks (Compounded Sales Growth,
    Compounded Profit Growth, Stock Price CAGR, Return on Equity) into
    {table title: {window: value}} -- e.g. {"Compounded Sales Growth": {"3 Years": 27.0}}.
    """
    soup = BeautifulSoup(html, "lxml")
    out: StatementRows = {}
    for table in soup.find_all("table", class_="ranges-table"):
        header = table.find("th")
        if header is None:
            continue
        title = _norm_label(header.get_text())
        windows: Dict[str, float] = {}
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) != 2:
                continue
            window = cells[0].get_text(strip=True).rstrip(":").strip()
            number = _to_number(cells[1].get_text())
            if number is not None:
                windows[window] = number
        if windows:
            out[title] = windows
    return out


def fetch_screener_statements(symbol: str) -> ScreenerStatements:
    """Fetch and parse every statement section for one symbol in a single GET."""
    html = _fetch_company_html(symbol)
    try:
        top_ratios = parse_top_ratios(html)
    except IncompleteRatiosError:
        # screener sometimes serves the #top-ratios panel with every value
        # blank (a data gap on their side, confirmed live for Venus Pipes &
        # Tubes). Degrade to the statement-table metrics rather than losing
        # the whole company -- callers that need top-ratios specifically
        # (fetch_screener_ratios) still raise.
        top_ratios = {}
    return ScreenerStatements(
        profit_loss=parse_statement_section(html, "profit-loss"),
        balance_sheet=parse_statement_section(html, "balance-sheet"),
        cash_flow=parse_statement_section(html, "cash-flow"),
        ratios=parse_statement_section(html, "ratios"),
        quarters=parse_statement_section(html, "quarters"),
        growth=parse_growth_tables(html),
        top_ratios=top_ratios,
    )


def _latest(values: Dict[str, float], back: int = 0) -> Optional[float]:
    """Nth-most-recent value. Screener renders periods oldest-first, and a
    trailing 'TTM' column when present -- which we skip, because the fiscal
    columns are what the annual metrics below are defined against."""
    periods = [p for p in values if p.upper() != "TTM"]
    if len(periods) <= back:
        return None
    return values[periods[-1 - back]]


def derive_registry_metrics(st: ScreenerStatements) -> Dict[str, float]:
    """Map parsed statements onto the exact labels metric-registry.yaml uses.

    Only emits a key when its source rows are actually present -- a missing
    metric must stay missing so evaluate() abstains, rather than being
    defaulted to a number nobody measured.
    """
    out: Dict[str, float] = {}

    # F21 -- screener publishes CFO/OP directly; average the last 3 fiscal years.
    cfo_op = st.cash_flow.get("CFO/OP")
    if cfo_op:
        recent = [v for v in (_latest(cfo_op, i) for i in range(3)) if v is not None]
        if recent:
            out["CFO/EBITDA (3yr avg)"] = sum(recent) / len(recent)

    # F27 -- Borrowings / (Equity Capital + Reserves)
    borrowings = st.balance_sheet.get("Borrowings")
    equity = st.balance_sheet.get("Equity Capital")
    reserves = st.balance_sheet.get("Reserves")
    if borrowings and equity and reserves:
        b, e, r = _latest(borrowings), _latest(equity), _latest(reserves)
        if b is not None and e is not None and r is not None and (e + r) > 0:
            out["Debt to Equity"] = b / (e + r)

    # F10 / F18 -- compounded 3-year growth, read from the ranges tables.
    profit_growth = st.growth.get("Compounded Profit Growth", {}).get("3 Years")
    if profit_growth is not None:
        out["Profit growth 3Yr %"] = profit_growth
    sales_growth_3y = st.growth.get("Compounded Sales Growth", {}).get("3 Years")
    if sales_growth_3y is not None:
        out["Compounded Sales Growth 3Yr %"] = sales_growth_3y

    # F7 / F25 -- QUARTERLY YoY: latest quarter vs the same quarter a year
    # earlier (4 columns back in the #quarters table). F25 (CANSLIM) asks for
    # quarterly *acceleration* specifically, so an annual FY-over-FY figure is
    # the wrong periodicity even though it is directionally similar -- taking
    # it from the annual P&L was a real defect, caught 2026-07-28.
    for row_name, label in (
        ("Sales", "Quarterly Sales Growth YoY %"),
        ("Net Profit", "Quarterly PAT Growth YoY %"),
    ):
        quarters = st.quarters.get(row_name)
        if not quarters:
            continue
        periods = list(quarters)
        if len(periods) < 5:
            continue  # need the year-ago quarter to compute YoY at all
        cur, year_ago = quarters[periods[-1]], quarters[periods[-5]]
        if year_ago:
            out[label] = (cur / year_ago - 1) * 100

    # F22 -- DuPont components, surfaced for the human even though F22 itself
    # stays advisory-numeric (SOIC states no leverage-share ceiling to gate on).
    # These stay ANNUAL: DuPont decomposes a full-year return, not a quarter.
    sales = st.profit_loss.get("Sales")
    net_profit = st.profit_loss.get("Net Profit")
    total_assets = st.balance_sheet.get("Total Assets")
    if net_profit and sales:
        np_v, s_v = _latest(net_profit), _latest(sales)
        if np_v is not None and s_v not in (None, 0):
            out["Net Profit Margin"] = np_v / s_v * 100
    if sales and total_assets:
        s_v, ta_v = _latest(sales), _latest(total_assets)
        if s_v is not None and ta_v not in (None, 0):
            out["Asset Turnover"] = s_v / ta_v

    # metric-registry.yaml declares these 5 as "fetchable" via
    # parse_top_ratios() -- read straight off screener's #top-ratios panel,
    # already present in the same HTML fetch. Only scalar values are taken;
    # "High / Low" (a tuple) is deliberately never read here.
    for label in ("Stock P/E", "ROCE", "ROE", "Market Cap", "Book Value"):
        value = st.top_ratios.get(label)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            out[label] = float(value)

    return out
