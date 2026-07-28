"""Tests for the NotebookLM auth preflight.

The seam mocked here is `_load_tokens`, mirroring how
test_soic_senses_notebook_client.py mocks the notebooklm_mcp import -- these
tests must pass with no NotebookLM session and no network.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import pytest

from soic_senses import notebook_preflight as pf


@dataclass
class _Tok:
    extracted_at: float


def _at_age(monkeypatch, hours, probe_error=None):
    monkeypatch.setattr(pf, "_load_tokens", lambda: _Tok(time.time() - hours * 3600))
    monkeypatch.setattr(pf, "_probe_live", lambda: probe_error)


def test_fresh_token_passes_and_reports_headroom(monkeypatch):
    _at_age(monkeypatch, 12)
    status = pf.check_auth(job_hours=0.5)
    assert status.ok
    assert 11 < status.age_hours < 13
    assert 154 < status.headroom_hours < 158


def test_token_with_less_life_than_the_job_fails(monkeypatch):
    # 167.8h old: still "valid" this second, but only ~0.2h of life left --
    # useless for a 0.5h job. This is the case a plain is_expired() check misses.
    _at_age(monkeypatch, 167.8)
    status = pf.check_auth(job_hours=0.5)
    assert not status.ok
    assert "does not cover" in status.detail


def test_absent_token_fails_rather_than_assuming_ok(monkeypatch):
    monkeypatch.setattr(pf, "_load_tokens", lambda: None)
    monkeypatch.setattr(pf, "_probe_live", lambda: None)
    assert not pf.check_auth().ok


def test_fresh_by_age_but_dead_session_is_caught_by_the_live_probe(monkeypatch):
    # Observed for real 2026-07-29: 12h old, ~156h nominal headroom, yet the
    # session was already invalid server-side. Age alone said GREEN.
    _at_age(monkeypatch, 12, probe_error="NotebookQueryError: Authentication expired.")
    status = pf.check_auth(job_hours=0.5)
    assert not status.ok
    assert "already invalid server-side" in status.detail


def test_probe_can_be_skipped_when_caller_opts_out(monkeypatch):
    _at_age(monkeypatch, 12, probe_error="NotebookQueryError: Authentication expired.")
    assert pf.check_auth(job_hours=0.5, functional=False).ok


def test_unknown_timestamp_proceeds_without_inventing_an_age(monkeypatch):
    monkeypatch.setattr(pf, "_load_tokens", lambda: object())
    monkeypatch.setattr(pf, "_probe_live", lambda: None)
    status = pf.check_auth()
    assert status.ok
    assert "age unknown" in status.detail


def test_require_auth_raises_with_the_refresh_command_in_the_message(monkeypatch):
    monkeypatch.setattr(pf, "_load_tokens", lambda: None)
    monkeypatch.setattr(pf, "_probe_live", lambda: None)
    with pytest.raises(pf.NotebookPreflightError) as excinfo:
        pf.require_auth()
    assert pf.REFRESH_COMMAND in str(excinfo.value)


def test_require_auth_returns_status_when_healthy(monkeypatch):
    _at_age(monkeypatch, 1)
    assert pf.require_auth(job_hours=0.25).ok
