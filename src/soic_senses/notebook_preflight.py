"""Fail-fast NotebookLM auth preflight.

Every long NotebookLM job in this project (seeding N sources, running a batch
of thematic queries) has the same failure mode: the cached Google session
expires PART WAY THROUGH, so the job dies after doing -- and paying for --
most of its work, with an opaque RPC error. The seeding run this module was
written for uploads 38 sources one at a time; losing it at source 30 wastes
every prior upload.

The fix is not a retry loop (a retry cannot mint a session). It is to refuse
to START unless the cached token has enough remaining life to plausibly
outlast the job, and to say exactly how to refresh when it doesn't.

Deliberately NOT an auto-refresher: minting a NotebookLM session requires a
fresh browser cookie that only a human can supply (`notebooklm-mcp-auth
--file`). Pretending otherwise would just relocate the same mid-run failure
into a background thread. This module's whole job is to convert a late,
expensive, cryptic failure into an early, cheap, actionable one.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

# notebooklm_mcp lives only in the tool venv, so keep the import behind a seam
# for the same reason notebook_client does -- callers that never touch
# NotebookLM must not fail to import.
_CACHE_MAX_AGE_HOURS = 168.0  # notebooklm_mcp.auth.AuthTokens.is_expired default

REFRESH_COMMAND = "notebooklm-mcp-auth --file <path-to-fresh-cookie-file>"


class NotebookPreflightError(Exception):
    """Raised when NotebookLM auth cannot support the job about to run.

    Carries the remediation in the message: a caller that prints only the
    exception still tells the operator what to do next.
    """


@dataclass
class AuthStatus:
    ok: bool
    age_hours: float
    headroom_hours: float
    detail: str


def _load_tokens():
    from notebooklm_mcp.auth import load_cached_tokens  # noqa: PLC0415

    return load_cached_tokens()


def _extracted_at(tokens) -> Optional[float]:
    for attr in ("extracted_at", "timestamp", "created_at"):
        value = getattr(tokens, attr, None)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _probe_live() -> Optional[str]:
    """Cheap functional probe. Returns None if the session works, else the error.

    THIS IS THE CHECK THAT MATTERS. Age is a necessary but NOT sufficient
    signal: measured 2026-07-29, a token 12h old with a nominal 156h of
    remaining life returned "Authentication expired" on a live query -- Google
    had invalidated the session server-side long before the local 7-day cache
    cap. An age-only preflight reports a comfortable green and the job still
    dies mid-run, which is the exact failure this module exists to prevent.
    """
    try:
        from soic_senses.notebook_client import list_notebooks  # noqa: PLC0415

        list_notebooks()
        return None
    except Exception as exc:  # noqa: BLE001
        return f"{type(exc).__name__}: {exc}"


def check_auth(
    job_hours: float = 0.5,
    max_age_hours: float = _CACHE_MAX_AGE_HOURS,
    functional: bool = True,
) -> AuthStatus:
    """Report whether cached auth can plausibly outlast a `job_hours` job.

    `job_hours` is the caller's own estimate of how long the work will take;
    headroom is measured against it rather than against zero, because a token
    with 10 minutes left is useless to a 40-minute seeding run even though it
    is technically still valid right now.

    `functional=True` (the default) additionally makes one live call, because
    age alone has been observed to pass while the session is already dead.
    Pass functional=False only when a live call is itself too expensive.
    """
    tokens = _load_tokens()
    if tokens is None:
        return AuthStatus(False, float("nan"), float("nan"),
                          "no cached NotebookLM token (absent, or already past the 7-day cache cap)")

    extracted = _extracted_at(tokens)
    if extracted is None:
        # Unknown age is not the same as expired -- report it, don't guess an age.
        return AuthStatus(True, float("nan"), float("nan"),
                          "token present but carries no readable timestamp; age unknown, proceeding")

    age = (time.time() - extracted) / 3600.0
    headroom = max_age_hours - age
    if headroom <= job_hours:
        return AuthStatus(False, age, headroom,
                          f"token is {age:.1f}h old; only {headroom:.1f}h of its {max_age_hours:.0f}h "
                          f"life remain, which does not cover the ~{job_hours:.1f}h job")

    if functional:
        err = _probe_live()
        if err is not None:
            return AuthStatus(False, age, headroom,
                              f"token looks fresh by age ({age:.1f}h old, {headroom:.1f}h nominal "
                              f"headroom) but a live call FAILED -- the Google session is already "
                              f"invalid server-side: {err}")

    return AuthStatus(True, age, headroom,
                      f"token {age:.1f}h old, {headroom:.1f}h headroom (~{headroom / 24:.1f} days)"
                      + (", live probe OK" if functional else ", age-only (probe skipped)"))


def require_auth(job_hours: float = 0.5) -> AuthStatus:
    """check_auth, but raise NotebookPreflightError when it is not usable."""
    status = check_auth(job_hours=job_hours)
    if not status.ok:
        raise NotebookPreflightError(
            f"NotebookLM auth preflight FAILED: {status.detail}. "
            f"Refresh with:  {REFRESH_COMMAND}   "
            "(get a fresh cookie from a logged-in notebooklm.google.com tab: DevTools -> Network "
            "-> any batchexecute request -> copy the full `cookie:` header)."
        )
    return status
