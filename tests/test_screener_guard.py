from pathlib import Path

import pytest

from vps_extraction.screener_guard import require_ratios

FIX = Path("data/fixtures/2026-11-04/screener-BIOCON-consolidated.html")


def test_shell_page_raises_not_blank():
    with pytest.raises(ValueError):
        require_ratios("<html><body>Please wait</body></html>")


@pytest.mark.skipif(not FIX.exists(), reason="local fixture not present")
def test_fixture_values_pinned():
    r = require_ratios(FIX.read_text(encoding="utf8"))
    assert (r["Current Price"], r["Stock P/E"], r["ROE"], r["ROCE"]) == (344.0, 82.3, 1.4, 3.61)
