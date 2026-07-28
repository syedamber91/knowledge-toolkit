from unittest.mock import MagicMock, patch


def _fake_analysis(
    recommendation="BUY",
    oscillators_recommendation="NEUTRAL",
    moving_averages_recommendation="BUY",
    indicators=None,
):
    analysis = MagicMock()
    analysis.summary = {"RECOMMENDATION": recommendation, "BUY": 10, "SELL": 5, "NEUTRAL": 3}
    analysis.oscillators = {"RECOMMENDATION": oscillators_recommendation}
    analysis.moving_averages = {"RECOMMENDATION": moving_averages_recommendation}
    analysis.indicators = indicators or {
        "RSI": 55.3,
        "ADX": 27.1,
        "EMA10": 1310.0,
        "EMA20": 1300.0,
        "EMA30": 1290.0,
        "EMA50": 1270.0,
        "EMA100": 1200.0,
        "EMA200": 1100.0,
        "close": 1320.0,
    }
    return analysis


def test_fetch_technicals_returns_a_populated_snapshot():
    from soic_senses.tradingview_client import fetch_technicals

    fake_handler = MagicMock()
    fake_handler.get_analysis.return_value = _fake_analysis()

    with patch("soic_senses.tradingview_client.TA_Handler", return_value=fake_handler) as mock_handler:
        snapshot = fetch_technicals("RELIANCE", exchange="NSE", screener="india", interval="1W")

    mock_handler.assert_called_once_with(
        symbol="RELIANCE", exchange="NSE", screener="india", interval="1W"
    )
    assert snapshot.symbol == "RELIANCE"
    assert snapshot.interval == "1W"
    assert snapshot.recommendation == "BUY"
    assert snapshot.oscillators_recommendation == "NEUTRAL"
    assert snapshot.moving_averages_recommendation == "BUY"
    assert snapshot.rsi == 55.3
    assert snapshot.adx == 27.1
    assert snapshot.ema10 == 1310.0
    assert snapshot.ema30 == 1290.0
    assert snapshot.ema200 == 1100.0
    assert snapshot.close == 1320.0


def test_fetch_technicals_defaults_to_nse_india_weekly():
    from soic_senses.tradingview_client import fetch_technicals

    fake_handler = MagicMock()
    fake_handler.get_analysis.return_value = _fake_analysis()

    with patch("soic_senses.tradingview_client.TA_Handler", return_value=fake_handler) as mock_handler:
        fetch_technicals("TCS")

    mock_handler.assert_called_once_with(symbol="TCS", exchange="NSE", screener="india", interval="1W")


def test_fetch_technicals_handles_missing_indicators_gracefully():
    from soic_senses.tradingview_client import fetch_technicals

    fake_handler = MagicMock()
    fake_handler.get_analysis.return_value = _fake_analysis(indicators={"RSI": 40.0})

    with patch("soic_senses.tradingview_client.TA_Handler", return_value=fake_handler):
        snapshot = fetch_technicals("SOMECO")

    assert snapshot.rsi == 40.0
    assert snapshot.adx is None
    assert snapshot.ema10 is None
    assert snapshot.close is None


def test_fetch_technicals_raises_technicals_unavailable_error_when_handler_fails():
    from soic_senses.tradingview_client import TechnicalsUnavailableError, fetch_technicals

    fake_handler = MagicMock()
    fake_handler.get_analysis.side_effect = Exception("Exchange or symbol not found")

    with patch("soic_senses.tradingview_client.TA_Handler", return_value=fake_handler):
        try:
            fetch_technicals("NOSUCHSYMBOL")
            assert False, "expected TechnicalsUnavailableError"
        except TechnicalsUnavailableError as exc:
            assert "NOSUCHSYMBOL" in str(exc)


def test_fetch_technicals_raises_clearly_when_the_optional_dep_is_absent():
    """tradingview-ta is optional: decision_engine imports this module, and
    decision_engine is imported by soic_wiki.cli, which runs under the
    notebooklm-mcp tool venv where the package isn't installed. A missing dep
    must surface as a normal TechnicalsUnavailableError (which build_briefing
    already records into data_error), not a ModuleNotFoundError at import."""
    from soic_senses.tradingview_client import TechnicalsUnavailableError, fetch_technicals

    with patch("soic_senses.tradingview_client.TA_Handler", None):
        try:
            fetch_technicals("TCS")
            assert False, "expected TechnicalsUnavailableError"
        except TechnicalsUnavailableError as exc:
            assert "tradingview-ta is not installed" in str(exc)
            assert "TCS" in str(exc)
