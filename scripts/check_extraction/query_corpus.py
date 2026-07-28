"""Query the corpus notebooks for checkable claims across the 11 non-forensic tags.

Same prompt contract as the forensic pilot (query_themes.py) -- abstention is
explicitly correct, thresholds must be copied character-for-character, and each
claim names the source note so `verify_claims.py` can check it deterministically.

Every theme is asked of EVERY corpus notebook, because notes were chunked by
seeding order, not by tag: a valuation note can sit in any of the five. Asking
each notebook independently is what keeps the chunking from silently costing
recall -- the alternative (guessing which notebook holds a theme) would
reintroduce exactly the blind spot the residual pass just proved is expensive.
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/soic-method/src")

from soic_senses.notebook_client import ask_notebook
from soic_senses.notebook_preflight import require_auth

STATE = json.load(open("/tmp/corpus_nb_state.json"))
NOTEBOOKS = list(STATE["notebooks"].values())
OUT = "/tmp/corpus_answers.json"

THEMES = [
    ("valuation", "valuation: P/E, P/B, EV/EBITDA, DCF, reverse DCF, fair value and margin of safety"),
    ("quality_moat", "moats and business quality: pricing power, switching costs, scale, brand, entry barriers"),
    ("growth", "growth drivers: revenue and earnings growth, capacity expansion, market-share gain"),
    ("cyclicality", "cyclicality: commodity cycles, replacement cycles, upcycle and downcycle positioning"),
    ("leverage_risk", "leverage and balance-sheet risk: debt levels, interest cover, liquidity, solvency"),
    ("capital_allocation", "capital allocation: capex, acquisitions, buybacks, dividends, ROCE and ROIC discipline"),
    ("sector_macro", "industry structure and macro: demand-supply balance, regulation, competitive intensity"),
    ("technicals_timing", "technical timing: moving averages, relative strength, stage analysis, entry and exit rules"),
    ("position_sizing", "position sizing and portfolio construction: allocation limits, diversification, risk control"),
    ("behavioral", "investor psychology and decision discipline: biases, conviction, selling discipline"),
    ("operating_leverage", "operating leverage and margin mechanics: fixed-cost absorption, margin expansion triggers"),
]

TEMPLATE = """From the sources, list the checkable tests an analyst can run about {desc}.

For each test give exactly these four lines:
TEST: <one sentence, what is measured>
THRESHOLD: <copy the number or comparison EXACTLY as the source words it, character for character>
SOURCE: <the source title it came from>
QUOTE: <the sentence containing that number, copied exactly>

If the sources describe the test but state no number for it, write THRESHOLD: NONE STATED and leave QUOTE as the sentence describing the test. Answering NONE STATED is correct and expected whenever the sources are qualitative. Only give a number that you can see written in a source."""


def main() -> None:
    print(f"preflight: {require_auth(job_hours=1.5).detail}\n", flush=True)
    try:
        out = json.load(open(OUT))
    except FileNotFoundError:
        out = {}

    for key, desc in THEMES:
        for ni, nbid in enumerate(NOTEBOOKS):
            slot = f"{key}__nb{ni}"
            if slot in out and not out[slot].startswith("__ERROR__"):
                continue
            prompt = TEMPLATE.format(desc=desc)
            ok = False
            for attempt in (1, 2):
                try:
                    res = ask_notebook(nbid, prompt, timeout=420.0)
                    ans = res.get("answer", "") if isinstance(res, dict) else str(res)
                    out[slot] = ans
                    print(f"[{slot}] {len(ans)} chars", flush=True)
                    ok = True
                    break
                except Exception as exc:  # noqa: BLE001
                    msg = f"{type(exc).__name__}: {exc}"
                    if "Authentication expired" in msg:
                        out[slot] = f"__ERROR__ {msg}"
                        json.dump(out, open(OUT, "w"), indent=1)
                        print(f"[{slot}] AUTH EXPIRED -- stopping so it can be refreshed once", flush=True)
                        return
                    print(f"[{slot}] attempt {attempt} {msg}", flush=True)
                    time.sleep(8 * attempt)
            if not ok:
                out[slot] = "__ERROR__ retries exhausted"
                print(f"[{slot}] gave up", flush=True)
            json.dump(out, open(OUT, "w"), indent=1)
            time.sleep(1)

    errs = sum(1 for v in out.values() if v.startswith("__ERROR__"))
    print(f"\nCORPUS_QUERY_DONE slots={len(out)} errors={errs}", flush=True)


if __name__ == "__main__":
    main()
