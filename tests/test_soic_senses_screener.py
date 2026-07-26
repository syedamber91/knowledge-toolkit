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
