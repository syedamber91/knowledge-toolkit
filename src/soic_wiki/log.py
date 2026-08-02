"""Append-only ingestion log for the SOIC persona wiki (index + log +
cross-links pattern -- see root CLAUDE.md, "standing requirement, not
optional").

Same contract as every other vault builder in this repo (`soic_toolkit/vault.py`,
`substack_toolkit/vault.py`, `media_core/unified_vault.py`) and as the
`persona_wiki` package the A1/A2 pilot topic was originally built with (whose
one existing entry in this vault's log.md already uses this exact wording --
implemented fresh here rather than imported cross-repo, since `soic_wiki` has
no dependency on the sibling `learning-vault` repo):

- parse the prior total from the last entry's ``(N total)`` -- no separate
  state file
- word the very first-ever entry as a backfill ("N item(s) already in vault
  (log started here)") -- never claim pre-existing content was "just
  captured"
- append "N new item(s) captured" or "N item(s) removed" only when the total
  actually changed -- never spam a duplicate entry on an unchanged rebuild
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Union

_TOTAL_RE = re.compile(r"\((\d+) total\)")
_HEADER = "# Persona Wiki Log\n\nAppend-only change history.\n"


def _last_logged_total(log_path: Path) -> Optional[int]:
    """Prior total parsed from the last logged entry, or None if the log
    has no entries yet (a brand-new or still-empty file)."""
    if not log_path.exists():
        return None
    matches = _TOTAL_RE.findall(log_path.read_text(encoding="utf-8"))
    return int(matches[-1]) if matches else None


def log_ingest(
    log_path: Union[str, Path], total: int, summary: str, stamp: str
) -> bool:
    """Append one log line if the total changed since the last entry.

    Returns True when a line was written, False when the total is unchanged
    (a no-op rebuild) and nothing was appended.
    """
    log_path = Path(log_path)
    prior = _last_logged_total(log_path)
    if prior is None:
        line = f"- {stamp} — backfill: {summary} (log started here) ({total} total)\n"
        header = _HEADER + "\n" if not log_path.exists() else ""
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(header + line)
        return True
    if total == prior:
        return False
    line = f"- {stamp} — {summary} ({total} total)\n"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return True
