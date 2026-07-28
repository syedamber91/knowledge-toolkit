"""Forensic pilot, query stage: ask NotebookLM for checkable forensic claims
across the 38 seeded notes, THEME BY THEME rather than note by note.

Prompt design notes (each earned the hard way earlier in this project):
  * Chat-turn input is empirically capped around 5KB, so every prompt here is
    short and the corpus does the heavy lifting as sources.
  * State only what a GOOD answer looks like. Showing a "don't do this"
    example primes the model to emit exactly that pattern (the documented
    `[N-M]` range-syntax failure).
  * Abstention must be the cheap path. The whole point of the deterministic
    verifier downstream is to catch invented thresholds; the prompt should
    minimise how often it has to fire, by making "the notes do not state a
    number" an explicitly correct and expected answer.
"""

from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/soic-method/src")

from soic_senses.notebook_client import ask_notebook
from soic_senses.notebook_preflight import require_auth

NOTEBOOK_ID = json.load(open("/tmp/forensic_nb_state.json"))["notebook_id"]

THEMES = [
    ("cash_conversion", "cash conversion: operating cash flow versus reported profit or EBITDA"),
    ("working_capital", "working capital: receivables, inventory, payables, and cash conversion cycle days"),
    ("revenue_quality", "revenue recognition quality and possible revenue inflation"),
    ("capitalisation", "expense capitalisation, depreciation policy, and intangibles"),
    ("promoter_conduct", "promoter pledging, promoter holding changes, and management incentives"),
    ("related_party", "related-party transactions and corporate structure complexity"),
    ("auditor_governance", "auditor opinions, auditor or KMP resignations, and governance red flags"),
    ("balance_sheet_health", "balance-sheet health: debt, contingent liabilities, off-balance-sheet items"),
    ("margin_profitability", "margin and profitability ratio analysis"),
    ("checklist_aggregate", "overall forensic or investing checklists that combine several red flags"),
]

TEMPLATE = """From the sources, list the checkable tests an analyst can run about {desc}.

For each test give exactly these four lines:
TEST: <one sentence, what is measured>
THRESHOLD: <copy the number or comparison EXACTLY as the source words it, character for character>
SOURCE: <the source title it came from>
QUOTE: <the sentence containing that number, copied exactly>

If the sources describe the test but state no number for it, write THRESHOLD: NONE STATED and leave QUOTE as the sentence describing the test. Answering NONE STATED is correct and expected whenever the sources are qualitative. Only give a number that you can see written in a source."""


def main() -> None:
    status = require_auth(job_hours=0.5)
    print(f"preflight: {status.detail}\n", flush=True)

    out = {}
    for key, desc in THEMES:
        prompt = TEMPLATE.format(desc=desc)
        assert len(prompt) < 5000, len(prompt)
        try:
            res = ask_notebook(NOTEBOOK_ID, prompt, timeout=300.0)
            ans = res.get("answer", "") if isinstance(res, dict) else str(res)
            out[key] = ans
            print(f"[{key}] {len(ans)} chars", flush=True)
        except Exception as exc:  # noqa: BLE001
            out[key] = f"__ERROR__ {type(exc).__name__}: {exc}"
            print(f"[{key}] ERROR {type(exc).__name__}: {exc}", flush=True)
        json.dump(out, open("/tmp/forensic_answers.json", "w"), indent=1)
        time.sleep(2)

    ok = sum(1 for v in out.values() if not v.startswith("__ERROR__"))
    print(f"\nthemes answered: {ok}/{len(THEMES)}", flush=True)


if __name__ == "__main__":
    main()
