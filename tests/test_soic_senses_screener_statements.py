"""Statement-table parsing (profit-loss / balance-sheet / cash-flow / ranges).

Closes the gap the POLYCAB dry run exposed: F21's cash-conversion safety gate,
F27's D/E gate, and F10/F18/F25's growth signals were all abstaining because
screener_client only parsed the '#top-ratios' grid. Every metric here is read
from a row screener already publishes -- nothing is derived from an invented
convention.
"""

from pathlib import Path
from unittest.mock import Mock, patch

FIXTURE = Path(__file__).parent / "fixtures" / "screener_tcs.html"


def _html():
    return FIXTURE.read_text(encoding="utf-8")


def test_parse_statement_section_keys_rows_by_label_then_period():
    from soic_senses.screener_client import parse_statement_section

    cf = parse_statement_section(_html(), "cash-flow")

    # screener renders labels with a trailing '+' expander and nbsp padding --
    # the parser must normalise both away.
    assert "CFO/OP" in cf
    assert cf["CFO/OP"]["Mar 2026"] == 92.0
    assert cf["CFO/OP"]["Mar 2025"] == 96.0


def test_parse_statement_section_reads_balance_sheet_rows():
    from soic_senses.screener_client import parse_statement_section

    bs = parse_statement_section(_html(), "balance-sheet")

    assert bs["Borrowings"]["Mar 2026"] == 11283.0
    assert bs["Equity Capital"]["Mar 2026"] == 362.0
    assert bs["Reserves"]["Mar 2026"] == 106878.0


def test_parse_statement_section_returns_empty_for_absent_section():
    from soic_senses.screener_client import parse_statement_section

    assert parse_statement_section("<html><body></body></html>", "cash-flow") == {}


def test_parse_growth_tables_extracts_compounded_growth_by_window():
    from soic_senses.screener_client import parse_growth_tables

    g = parse_growth_tables(_html())

    assert g["Compounded Sales Growth"]["3 Years"] == 6.0
    assert g["Compounded Profit Growth"]["3 Years"] == 8.0
    # negative values must survive the '%' strip
    assert g["Stock Price CAGR"]["5 Years"] == -7.0


def test_derive_registry_metrics_averages_cfo_over_three_years():
    from soic_senses.screener_client import derive_registry_metrics, fetch_screener_statements

    with patch(
        "soic_senses.screener_client.requests.get",
        return_value=Mock(status_code=200, text=_html()),
    ):
        st = fetch_screener_statements("TCS")
    m = derive_registry_metrics(st)

    # (92 + 96 + 88) / 3 -- the three most recent fiscal columns
    assert round(m["CFO/EBITDA (3yr avg)"], 1) == 92.0


def test_derive_registry_metrics_computes_debt_to_equity():
    from soic_senses.screener_client import derive_registry_metrics, fetch_screener_statements

    with patch(
        "soic_senses.screener_client.requests.get",
        return_value=Mock(status_code=200, text=_html()),
    ):
        st = fetch_screener_statements("TCS")
    m = derive_registry_metrics(st)

    # 11283 / (362 + 106878) = 0.1052...
    assert round(m["Debt to Equity"], 3) == 0.105


def test_derive_registry_metrics_maps_growth_windows_to_registry_labels():
    from soic_senses.screener_client import derive_registry_metrics, fetch_screener_statements

    with patch(
        "soic_senses.screener_client.requests.get",
        return_value=Mock(status_code=200, text=_html()),
    ):
        st = fetch_screener_statements("TCS")
    m = derive_registry_metrics(st)

    assert m["Profit growth 3Yr %"] == 8.0
    assert m["Compounded Sales Growth 3Yr %"] == 6.0


def test_derive_registry_metrics_omits_what_it_cannot_derive():
    """No fabrication: a metric whose source rows are missing must be absent
    from the dict entirely, so evaluate() abstains rather than scoring a zero."""
    from soic_senses.screener_client import ScreenerStatements, derive_registry_metrics

    empty = ScreenerStatements(
        profit_loss={}, balance_sheet={}, cash_flow={}, ratios={}, quarters={}, growth={}
    )
    assert derive_registry_metrics(empty) == {}


def test_derive_registry_metrics_uses_quarterly_periodicity_for_yoy_growth():
    """F25 (CANSLIM) asks for quarterly acceleration specifically. Taking the
    figure from the annual P&L was a real defect -- YoY must compare the
    latest quarter against the same quarter a year earlier (4 columns back)."""
    from soic_senses.screener_client import ScreenerStatements, derive_registry_metrics

    st = ScreenerStatements(
        profit_loss={"Sales": {"Mar 2025": 100.0, "Mar 2026": 400.0}},  # +300% annually
        balance_sheet={},
        cash_flow={},
        ratios={},
        quarters={
            "Sales": {
                "Jun 2025": 100.0, "Sep 2025": 105.0, "Dec 2025": 110.0,
                "Mar 2026": 115.0, "Jun 2026": 120.0,
            }
        },
        growth={},
    )
    m = derive_registry_metrics(st)

    # Jun 2026 vs Jun 2025 = +20%, NOT the +300% the annual rows would imply.
    assert round(m["Quarterly Sales Growth YoY %"], 1) == 20.0


def test_derive_registry_metrics_skips_yoy_without_a_year_ago_quarter():
    from soic_senses.screener_client import ScreenerStatements, derive_registry_metrics

    st = ScreenerStatements(
        profit_loss={}, balance_sheet={}, cash_flow={}, ratios={},
        quarters={"Sales": {"Mar 2026": 115.0, "Jun 2026": 120.0}},  # only 2 columns
        growth={},
    )
    assert "Quarterly Sales Growth YoY %" not in derive_registry_metrics(st)


def test_fetch_screener_statements_populates_top_ratios():
    from soic_senses.screener_client import fetch_screener_statements

    with patch(
        "soic_senses.screener_client.requests.get",
        return_value=Mock(status_code=200, text=_html()),
    ):
        st = fetch_screener_statements("TCS")

    assert st.top_ratios["ROCE"] == 63.0
    assert st.top_ratios["ROE"] == 51.8
    assert st.top_ratios["Stock P/E"] == 15.0
    assert st.top_ratios["Market Cap"] == 802492.0
    assert st.top_ratios["Book Value"] == 296.0


def test_derive_registry_metrics_reads_top_ratios_scalars():
    from soic_senses.screener_client import ScreenerStatements, derive_registry_metrics

    st = ScreenerStatements(
        profit_loss={}, balance_sheet={}, cash_flow={}, ratios={}, quarters={}, growth={},
        top_ratios={
            "Stock P/E": 15.0, "ROCE": 63.0, "ROE": 51.8,
            "Market Cap": (802492.0, 1.0),  # tuple shape under a GUARDED key -- must be skipped
            "Book Value": 296.0,
        },
    )
    m = derive_registry_metrics(st)

    assert m["Stock P/E"] == 15.0
    assert m["ROCE"] == 63.0
    assert m["ROE"] == 51.8
    assert m["Book Value"] == 296.0
    assert "Market Cap" not in m


def test_derive_registry_metrics_top_ratios_absent_is_still_empty():
    """Backward compat: the pre-existing 'omits what it cannot derive'
    contract must hold even though ScreenerStatements now carries a 7th
    field."""
    from soic_senses.screener_client import ScreenerStatements, derive_registry_metrics

    empty = ScreenerStatements(
        profit_loss={}, balance_sheet={}, cash_flow={}, ratios={}, quarters={}, growth={}
    )
    assert derive_registry_metrics(empty) == {}


def test_fetch_and_derive_end_to_end_top_ratios():
    from soic_senses.screener_client import derive_registry_metrics, fetch_screener_statements

    with patch(
        "soic_senses.screener_client.requests.get",
        return_value=Mock(status_code=200, text=_html()),
    ):
        st = fetch_screener_statements("TCS")
    m = derive_registry_metrics(st)

    assert m["ROCE"] == 63.0
    assert m["ROE"] == 51.8
    assert m["Stock P/E"] == 15.0
    assert m["Market Cap"] == 802492.0
    assert m["Book Value"] == 296.0


_BLANK_TOP_RATIOS_HTML = """
<html><body>
<ul id="top-ratios">
  <li class="flex flex-space-between" data-source="default">
    <span class="name">Market Cap</span>
    <span class="nowrap value">
      Rs.
      <span class="number"></span>
      Cr.
    </span>
  </li>
  <li class="flex flex-space-between" data-source="default">
    <span class="name">Stock P/E</span>
    <span class="nowrap value">
      <span class="number"></span>
    </span>
  </li>
</ul>
</body></html>
"""


def test_parse_top_ratios_raises_on_blank_panel():
    """Sanity check: this fixture must actually trigger IncompleteRatiosError,
    mirroring the confirmed-live Venus Pipes & Tubes case (right #top-ratios
    shape, every <span class="number"> blank)."""
    from soic_senses.screener_client import IncompleteRatiosError, parse_top_ratios
    import pytest

    with pytest.raises(IncompleteRatiosError):
        parse_top_ratios(_BLANK_TOP_RATIOS_HTML)


def test_fetch_screener_statements_degrades_to_empty_top_ratios_on_blank_panel():
    """A blank #top-ratios panel must not destroy the other 8 statement-table
    metrics that parsed fine -- fetch_screener_statements should degrade to
    top_ratios={} instead of letting IncompleteRatiosError propagate."""
    from soic_senses.screener_client import fetch_screener_statements

    with patch(
        "soic_senses.screener_client.requests.get",
        return_value=Mock(status_code=200, text=_BLANK_TOP_RATIOS_HTML),
    ):
        st = fetch_screener_statements("TCS")

    assert st.top_ratios == {}


_MIXED_NA_TOP_RATIOS_HTML = """
<html><body>
<ul id="top-ratios">
  <li class="flex flex-space-between" data-source="default">
    <span class="name">Market Cap</span>
    <span class="nowrap value">
      Rs.
      <span class="number">N/A</span>
      Cr.
    </span>
  </li>
  <li class="flex flex-space-between" data-source="default">
    <span class="name">Stock P/E</span>
    <span class="nowrap value">
      <span class="number">15.00</span>
    </span>
  </li>
</ul>
</body></html>
"""


def test_parse_top_ratios_skips_a_non_numeric_span_without_raising():
    """A single garbage value (e.g. 'N/A', '--') in one span must not take
    down the whole panel -- the sibling statement-table parser (_to_number)
    already tolerates this via a caught ValueError; _to_float needs the same
    treatment so one bad span doesn't cost the 8 good statement metrics that
    parsed fine in the same fetch."""
    from soic_senses.screener_client import parse_top_ratios

    ratios = parse_top_ratios(_MIXED_NA_TOP_RATIOS_HTML)

    assert ratios == {"Stock P/E": 15.0}
    assert "Market Cap" not in ratios


_ALL_GARBAGE_TOP_RATIOS_HTML = """
<html><body>
<ul id="top-ratios">
  <li class="flex flex-space-between" data-source="default">
    <span class="name">Market Cap</span>
    <span class="nowrap value">
      Rs.
      <span class="number">N/A</span>
      Cr.
    </span>
  </li>
  <li class="flex flex-space-between" data-source="default">
    <span class="name">Stock P/E</span>
    <span class="nowrap value">
      <span class="number">--</span>
    </span>
  </li>
</ul>
</body></html>
"""


def test_parse_top_ratios_still_raises_when_every_span_is_non_numeric_garbage():
    """The degrade contract must stay intact: _to_float returning None for
    unparseable text (instead of raising) must NOT quietly satisfy the
    IncompleteRatiosError check -- parse_top_ratios already filters None out
    of `numbers`, so an all-garbage panel (parsed_count == 0) still trips it,
    exactly like an all-blank panel does."""
    from soic_senses.screener_client import IncompleteRatiosError, parse_top_ratios
    import pytest

    with pytest.raises(IncompleteRatiosError):
        parse_top_ratios(_ALL_GARBAGE_TOP_RATIOS_HTML)
