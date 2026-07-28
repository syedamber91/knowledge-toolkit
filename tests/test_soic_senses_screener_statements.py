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
