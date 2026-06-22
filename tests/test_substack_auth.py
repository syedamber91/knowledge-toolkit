"""Tests for session import from Chrome — crypto/Keychain mocked out.

The AES decryption and Keychain read are environment-specific, so we stub them
and exercise the parts we own: reading Chrome's cookie SQLite, filtering to
Substack, requiring the real session cookie, and writing storage_state JSON.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from substack_toolkit import auth


def _make_chrome_db(path, rows):
    """Build a minimal Chrome-shaped Cookies SQLite at ``path``."""
    db = sqlite3.connect(str(path))
    db.execute(
        "create table cookies (host_key text, name text, encrypted_value blob, "
        "path text, expires_utc integer, is_secure integer, is_httponly integer)"
    )
    db.executemany(
        "insert into cookies values (?,?,?,?,?,?,?)", rows
    )
    db.commit()
    db.close()


def _wire(monkeypatch, tmp_path, rows):
    chrome_db = tmp_path / "Cookies"
    _make_chrome_db(chrome_db, rows)
    state = tmp_path / "substack_state.json"
    monkeypatch.setattr(auth, "_CHROME_COOKIES", chrome_db)
    monkeypatch.setattr(auth, "STATE_PATH", state)
    monkeypatch.setattr(auth, "AUTH_DIR", tmp_path)
    monkeypatch.setattr(auth, "_chrome_key", lambda: b"0" * 16)
    # Decrypt = strip the "v10" prefix and decode (no real AES needed here).
    monkeypatch.setattr(auth, "_decrypt_cookie", lambda enc, key: enc[3:].decode())
    return state


def test_import_from_chrome_writes_session(tmp_path, monkeypatch):
    rows = [
        ("vutr.substack.com", "substack.sid", b"v10SIDVALUE", "/", 0, 1, 1),
        (".substack.com", "cf_clearance", b"v10CFVALUE", "/", 0, 1, 0),
        ("example.com", "other", b"v10NOPE", "/", 0, 0, 0),  # filtered out by query
    ]
    state = _wire(monkeypatch, tmp_path, rows)

    count = auth.import_from_chrome()
    assert count == 2  # only the two substack cookies

    saved = json.loads(state.read_text())
    names = {c["name"]: c["value"] for c in saved["cookies"]}
    assert names["substack.sid"] == "SIDVALUE"
    assert names["cf_clearance"] == "CFVALUE"
    assert "other" not in names
    # httpOnly flag round-trips from the is_httponly column.
    sid = next(c for c in saved["cookies"] if c["name"] == "substack.sid")
    assert sid["httpOnly"] is True


def test_import_from_chrome_requires_session_cookie(tmp_path, monkeypatch):
    rows = [(".substack.com", "cf_clearance", b"v10CFVALUE", "/", 0, 1, 0)]
    _wire(monkeypatch, tmp_path, rows)
    with pytest.raises(RuntimeError, match="substack.sid"):
        auth.import_from_chrome()


def test_session_has_auth(tmp_path, monkeypatch):
    state = tmp_path / "substack_state.json"
    monkeypatch.setattr(auth, "STATE_PATH", state)
    assert auth.session_has_auth() is False
    state.write_text(json.dumps({"cookies": [{"name": "substack.lli", "value": "1"}]}))
    assert auth.session_has_auth() is False  # lli is not enough
    state.write_text(json.dumps({"cookies": [{"name": "substack.sid", "value": "x"}]}))
    assert auth.session_has_auth() is True
