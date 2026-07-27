"""Live technicals sense: fetch RSI/ADX/EMA/recommendation snapshots from
TradingView via the unofficial `tradingview-ta` package (public
scanner/technical-analysis endpoint, no login required).

This is the answer to the price-series dependency gap F23 (Weinstein
stage-analysis), F31 (market-breadth deployment-timing), F32
(sector-rotation confirmation), and F37 (small-cap liquidity/reflexivity)
each flag in decision-frameworks-v1.md's own Live-data sections --
screener_client.py has no weekly/daily OHLCV, EMA, RSI, ADX, or relative-
strength fetch. This module does NOT return raw OHLCV bars (tradingview-ta
only exposes TradingView's own computed indicator snapshot, not historical
candles), so relative-strength-vs-Nifty and custom-index construction
still need a richer source -- see decision-frameworks-v1.md's Data-source
routing table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tradingview_ta import TA_Handler


class TechnicalsUnavailableError(Exception):
    """Raised when TradingView has no analysis for the given symbol/exchange
    (wrong symbol, wrong exchange, or the endpoint itself failed) -- never
    silently returns a snapshot of Nones that looks like real data."""


@dataclass
class TechnicalSnapshot:
    symbol: str
    interval: str
    recommendation: str  # STRONG_BUY | BUY | NEUTRAL | SELL | STRONG_SELL
    oscillators_recommendation: str
    moving_averages_recommendation: str
    rsi: Optional[float]
    adx: Optional[float]
    ema10: Optional[float]
    ema20: Optional[float]
    ema30: Optional[float]
    ema50: Optional[float]
    ema100: Optional[float]
    ema200: Optional[float]
    close: Optional[float]


def fetch_technicals(
    symbol: str,
    exchange: str = "NSE",
    screener: str = "india",
    interval: str = "1W",
) -> TechnicalSnapshot:
    """Fetch a live technical-analysis snapshot for one symbol.

    Defaults match this project's usual universe: NSE-listed Indian
    equities, weekly interval (matches F23's 30-weekly-EMA convention).
    Raises TechnicalsUnavailableError (naming the symbol) on any failure
    from the underlying handler -- a wrong symbol/exchange must fail
    loudly, not return a snapshot of Nones indistinguishable from a
    genuine "indicator not computed yet" gap.
    """
    handler = TA_Handler(symbol=symbol, exchange=exchange, screener=screener, interval=interval)
    try:
        analysis = handler.get_analysis()
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any handler failure becomes one clear error
        raise TechnicalsUnavailableError(
            f"TradingView has no analysis for {symbol!r} on {exchange!r}/{screener!r}: {exc}"
        ) from exc

    indicators = analysis.indicators
    return TechnicalSnapshot(
        symbol=symbol,
        interval=interval,
        recommendation=analysis.summary["RECOMMENDATION"],
        oscillators_recommendation=analysis.oscillators["RECOMMENDATION"],
        moving_averages_recommendation=analysis.moving_averages["RECOMMENDATION"],
        rsi=indicators.get("RSI"),
        adx=indicators.get("ADX"),
        ema10=indicators.get("EMA10"),
        ema20=indicators.get("EMA20"),
        ema30=indicators.get("EMA30"),
        ema50=indicators.get("EMA50"),
        ema100=indicators.get("EMA100"),
        ema200=indicators.get("EMA200"),
        close=indicators.get("close"),
    )
