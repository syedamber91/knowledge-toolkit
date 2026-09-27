from pathlib import Path
from unittest.mock import Mock, patch

FIXTURE = Path(__file__).parent / "fixtures" / "screener_tcs.html"


def test_parse_top_ratios_extracts_single_value_ratios():
    from soic_senses.screener_client import parse_top_ratios

    html = FIXTURE.read_text(encoding="utf-8")
    ratios = parse_top_ratios(html)

    assert ratios["Market Cap"] == 802492.0
    assert ratios["Current Price"] == 2218.0
    assert ratios["Stock P/E"] == 15.0
    assert ratios["Book Value"] == 296.0
    assert ratios["Dividend Yield"] == 2.89
    assert ratios["ROCE"] == 63.0
    assert ratios["ROE"] == 51.8
    assert ratios["Face Value"] == 1.00


def test_parse_top_ratios_extracts_high_low_as_a_pair():
    from soic_senses.screener_client import parse_top_ratios

    html = FIXTURE.read_text(encoding="utf-8")
    ratios = parse_top_ratios(html)

    assert ratios["High / Low"] == (3350.0, 1976.0)


def test_fetch_screener_ratios_requests_the_consolidated_url_by_default():
    from soic_senses.screener_client import fetch_screener_ratios

    fake_response = Mock(status_code=200, text=FIXTURE.read_text(encoding="utf-8"))
    with patch("soic_senses.screener_client.requests.get", return_value=fake_response) as mock_get:
        ratios = fetch_screener_ratios("TCS")

    called_url = mock_get.call_args[0][0]
    assert called_url == "https://www.screener.in/company/TCS/consolidated/"
    assert ratios["Stock P/E"] == 15.0


def test_fetch_screener_ratios_falls_back_to_standalone_url_when_no_consolidated_page():
    from soic_senses.screener_client import fetch_screener_ratios

    consolidated_404 = Mock(status_code=404, text="")
    standalone_ok = Mock(status_code=200, text=FIXTURE.read_text(encoding="utf-8"))
    with patch(
        "soic_senses.screener_client.requests.get",
        side_effect=[consolidated_404, standalone_ok],
    ) as mock_get:
        ratios = fetch_screener_ratios("SOMECO")

    urls_requested = [c[0][0] for c in mock_get.call_args_list]
    assert urls_requested == [
        "https://www.screener.in/company/SOMECO/consolidated/",
        "https://www.screener.in/company/SOMECO/",
    ]
    assert ratios["Stock P/E"] == 15.0


def test_parse_top_ratios_raises_when_the_page_has_no_populated_numbers():
    """Real failure mode hit live: screener.in can return HTTP 200 with the
    correct company page and the right <li> rows, but every <span
    class="number"> is empty (e.g. Venus Pipes & Tubes, confirmed on 3
    separate live fetches). That is structurally different from "this
    company just has no ratios" -- it's screener's own data gap for that
    company right now, and must raise loudly, not return a dict that looks
    like a legitimate (if empty) result.
    """
    from soic_senses.screener_client import IncompleteRatiosError, parse_top_ratios

    empty_ratios_html = """
    <ul id="top-ratios">
      <li class="flex flex-space-between" data-source="default">
        <span class="name">Market Cap</span>
        <span class="nowrap value">₹<span class="number"></span> Cr.</span>
      </li>
      <li class="flex flex-space-between" data-source="default">
        <span class="name">Stock P/E</span>
        <span class="nowrap value"><span class="number"></span></span>
      </li>
    </ul>
    """
    try:
        parse_top_ratios(empty_ratios_html)
        assert False, "expected IncompleteRatiosError"
    except IncompleteRatiosError:
        pass


def test_fetch_screener_ratios_raises_when_company_not_found_on_either_page():
    from soic_senses.screener_client import CompanyNotFoundError, fetch_screener_ratios

    not_found = Mock(status_code=404, text="")
    with patch("soic_senses.screener_client.requests.get", return_value=not_found):
        try:
            fetch_screener_ratios("NOSUCHCOMPANY")
            assert False, "expected CompanyNotFoundError"
        except CompanyNotFoundError:
            pass


# --------------------------------------------------------------------------
# _fetch_company_html falling back on a 200-but-empty consolidated page
#
# Real symptom, measured live 2026-09-27: screener.in's /consolidated/ URL
# for a company with no subsidiaries to consolidate (ABBOTINDIA, GILLETTE,
# GRSE, SBILIFE all confirmed) returns HTTP 200 with the full page shape --
# every statement section present, every row label present -- but ZERO
# numeric cells in any row, on any period. /  (standalone) carries the real
# data. The prior fallback only checked the HTTP status code, so it accepted
# that empty consolidated page as final and never tried standalone.
# --------------------------------------------------------------------------

_EMPTY_QUARTERS_HTML = """
<html><body>
<section id="quarters"><table>
<thead><tr><th></th><th>Mar 2024</th><th>Jun 2024</th></tr></thead>
<tbody>
<tr><td class="text">Sales<span class="blue-icon">+</span></td></tr>
<tr><td class="text">Net Profit<span class="blue-icon">+</span></td></tr>
</tbody>
</table></section>
</body></html>
"""


def test_page_has_financial_data_is_true_for_a_real_quarters_table():
    from soic_senses.screener_client import _page_has_financial_data

    assert _page_has_financial_data(FIXTURE.read_text(encoding="utf-8")) is True


def test_page_has_financial_data_is_false_for_a_label_only_quarters_table():
    from soic_senses.screener_client import _page_has_financial_data

    assert _page_has_financial_data(_EMPTY_QUARTERS_HTML) is False


def test_page_has_financial_data_is_false_when_quarters_section_absent():
    from soic_senses.screener_client import _page_has_financial_data

    assert _page_has_financial_data("<html><body></body></html>") is False


def test_fetch_company_html_falls_back_to_standalone_on_a_200_but_empty_consolidated_page():
    from soic_senses.screener_client import fetch_screener_statements

    empty_consolidated = Mock(status_code=200, text=_EMPTY_QUARTERS_HTML)
    real_standalone = Mock(status_code=200, text=FIXTURE.read_text(encoding="utf-8"))
    with patch(
        "soic_senses.screener_client.requests.get",
        side_effect=[empty_consolidated, real_standalone],
    ) as mock_get:
        st = fetch_screener_statements("ABBOTINDIA")

    urls_requested = [c[0][0] for c in mock_get.call_args_list]
    assert urls_requested == [
        "https://www.screener.in/company/ABBOTINDIA/consolidated/",
        "https://www.screener.in/company/ABBOTINDIA/",
    ]
    # the real standalone data reached the parser, not the empty consolidated page
    assert st.quarters["Net Profit"]


def test_fetch_company_html_does_not_retry_when_consolidated_already_has_real_data():
    """The common case (ACC, AMBUJACEM, TCS, ...) must cost exactly one
    request -- a StopIteration here means the code tried a second fetch it
    had no reason to make."""
    from soic_senses.screener_client import fetch_screener_statements

    with patch(
        "soic_senses.screener_client.requests.get",
        side_effect=[Mock(status_code=200, text=FIXTURE.read_text(encoding="utf-8"))],
    ) as mock_get:
        fetch_screener_statements("TCS")

    assert mock_get.call_count == 1


def test_fetch_company_html_returns_the_empty_consolidated_page_when_standalone_also_fails():
    """Consolidated succeeded (200) even though it was empty; standalone
    failed outright (404). The empty consolidated page is still the best
    available answer -- there is nothing better to fall back to, and this
    must not raise CompanyNotFoundError for a company that DOES exist."""
    from soic_senses.screener_client import fetch_screener_statements

    empty_consolidated = Mock(status_code=200, text=_EMPTY_QUARTERS_HTML)
    standalone_404 = Mock(status_code=404, text="")
    with patch(
        "soic_senses.screener_client.requests.get",
        side_effect=[empty_consolidated, standalone_404],
    ):
        st = fetch_screener_statements("SOMECO")

    assert st.quarters == {}  # the empty page, correctly parsed as empty -- not a crash
