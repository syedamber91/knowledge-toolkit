"""Wrap the existing soic_senses parser so a 200-but-empty page fails loudly (never a blank)."""
from soic_senses.screener_client import parse_top_ratios

NEEDED = ("Current Price", "Stock P/E", "ROE", "ROCE")


def require_ratios(html: str) -> dict:
    r = parse_top_ratios(html)
    missing = [k for k in NEEDED if r.get(k) is None]
    if missing:
        raise ValueError(f"Screener page missing {missing}: shell page or layout change")
    return r
