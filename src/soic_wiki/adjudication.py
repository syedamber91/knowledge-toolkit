"""G1 term-flag adjudication registry.

`gates.py` flags a term as suspect (hapax or summary-inflated) whenever its
frequency distribution looks like a summarizer artifact; the module docstring
there is explicit that this is informational -- "GATES FLAG; THEY NEVER
DELETE" -- and the actual call ("is this real terminology or a summarizer
artifact?") is deferred to an L4 adjudicator that reads the raw window.

What was missing: nowhere was that call ever RECORDED. Every gate run
re-surfaced the same already-judged terms (e.g. a genuinely rare-but-real
term repeated across every sector that happens to use it) with no way to
distinguish "seen this, already decided it's real" from "new, needs a
look" -- so each run either re-adjudicates from scratch or the flag list
grows noisier every batch.

This module is a small persisted registry: term -> {verdict, reason, date}.
`unadjudicated()` filters a gate run's G1 flags down to terms with no
recorded verdict yet -- the actual triage queue.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

import yaml

VERDICT_REAL = "real"
VERDICT_ARTIFACT = "artifact"
_VALID_VERDICTS = (VERDICT_REAL, VERDICT_ARTIFACT)


def load_adjudications(path: Union[str, Path]) -> Dict[str, dict]:
    """Return the adjudication registry, or {} if it doesn't exist yet."""
    path = Path(path)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def record_adjudication(
    path: Union[str, Path], term: str, verdict: str, reason: str, stamp: str
) -> None:
    """Persist a verdict for one flagged term. A later call for the SAME
    term overwrites its verdict -- adjudication can be revisited (e.g. a
    term first judged an artifact turns out, on a later sector, to be real
    terminology after all), and only the current verdict is meaningful."""
    if verdict not in _VALID_VERDICTS:
        raise ValueError(f"verdict must be one of {_VALID_VERDICTS}, got {verdict!r}")
    path = Path(path)
    data = load_adjudications(path)
    data[term] = {"verdict": verdict, "reason": reason, "date": stamp}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=True, allow_unicode=True), encoding="utf-8")


def unadjudicated(
    flagged: Dict[str, List[str]], adjudications: Dict[str, dict]
) -> Dict[str, List[str]]:
    """The subset of a gate run's G1 flags with no recorded verdict yet --
    what a run actually needs a human/L4 adjudicator to look at."""
    return {term: slugs for term, slugs in flagged.items() if term not in adjudications}
