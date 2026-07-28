#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp>=1.0",
#     "tradingview-ta>=3.3",
# ]
# ///
"""TradingView technicals MCP server -- a background (stdio) MCP connection,
not a browser session. Exposes one tool, get_technicals, wrapping
soic_senses.tradingview_client.fetch_technicals().

Answers the price-series dependency gap F23 (Weinstein stage-analysis), F31
(market-breadth deployment-timing), F32 (sector-rotation confirmation), and
F37 (small-cap liquidity/reflexivity) each flag in decision-frameworks-v1.md's
own Live-data sections -- RSI/ADX/EMA/recommendation via TradingView's public
scanner endpoint, no login required, no browser tab.

Run standalone: uv run mcp_servers/tradingview_mcp_server.py
Registered via .mcp.json at the repo root so Claude Code launches it
automatically as a background stdio server.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from soic_senses.tradingview_client import (  # noqa: E402
    TechnicalsUnavailableError,
    fetch_technicals,
)

mcp = FastMCP("tradingview")


@mcp.tool()
def get_technicals(
    symbol: str,
    exchange: str = "NSE",
    screener: str = "india",
    interval: str = "1W",
) -> dict:
    """Fetch a live technical-analysis snapshot for one symbol from TradingView.

    Args:
        symbol: Ticker as TradingView lists it, e.g. "RELIANCE", "TCS".
        exchange: Exchange code, default "NSE" (this project's usual universe).
        screener: TradingView screener region, default "india".
        interval: One of 1m/5m/15m/30m/1h/2h/4h/1d/1W/1M. Default "1W" to
            match F23's 30-weekly-EMA convention.

    Returns a dict with: recommendation, oscillators_recommendation,
    moving_averages_recommendation (each STRONG_BUY/BUY/NEUTRAL/SELL/
    STRONG_SELL), rsi, adx, ema10 through ema200, and close. Any indicator
    TradingView hasn't computed yet comes back null, never a fabricated
    number.

    Raises a tool error (surfaced to the caller, not swallowed) if the
    symbol/exchange/screener combination has no TradingView analysis --
    e.g. a wrong ticker or an unsupported exchange code.
    """
    try:
        snapshot = fetch_technicals(symbol, exchange=exchange, screener=screener, interval=interval)
    except TechnicalsUnavailableError as exc:
        raise ValueError(str(exc)) from exc

    return {
        "symbol": snapshot.symbol,
        "interval": snapshot.interval,
        "recommendation": snapshot.recommendation,
        "oscillators_recommendation": snapshot.oscillators_recommendation,
        "moving_averages_recommendation": snapshot.moving_averages_recommendation,
        "rsi": snapshot.rsi,
        "adx": snapshot.adx,
        "ema10": snapshot.ema10,
        "ema20": snapshot.ema20,
        "ema30": snapshot.ema30,
        "ema50": snapshot.ema50,
        "ema100": snapshot.ema100,
        "ema200": snapshot.ema200,
        "close": snapshot.close,
    }


if __name__ == "__main__":
    mcp.run()
