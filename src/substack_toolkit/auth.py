"""Capture the user's Substack session for the crawler.

Two ways to obtain a session, both storing only the resulting cookies under
``.auth/substack_state.json`` (Playwright storage_state format) — never a
password:

* :func:`login` — open a real browser, log in manually, save the cookies.
* :func:`import_from_chrome` — reuse the session from your everyday Google
  Chrome, where you are already logged in. This decrypts only the Substack
  cookies from Chrome's local store (macOS Keychain approval required) and is the
  reliable path when launching an automation browser is not possible.

Both produce the same on-disk shape, so the crawler does not care which was used.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.console import Console

from .config import AUTH_DIR, STATE_PATH, channel_url

console = Console()

# The cookie that proves an authenticated session. httpOnly; both Playwright and
# Chrome's store expose it. substack.lli is only a client-side hint and is NOT
# sufficient — see the login flow notes in the README.
SESSION_COOKIE = "substack.sid"


def has_saved_session() -> bool:
    return STATE_PATH.exists()


def session_has_auth() -> bool:
    """True when the saved session actually contains the real auth cookie."""
    if not STATE_PATH.exists():
        return False
    state = json.loads(STATE_PATH.read_text())
    return any(
        c.get("name") == SESSION_COOKIE and c.get("value")
        for c in state.get("cookies", [])
    )


def login(handle: str) -> None:
    """Open a browser to the publication, wait for manual login, save cookies."""
    from playwright.sync_api import sync_playwright

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    url = channel_url(handle)
    console.print(f"Opening [bold]{url}[/bold] — log in, then return here.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        input("Press Enter once you are logged in… ")
        context.storage_state(path=str(STATE_PATH))
        browser.close()
    if not session_has_auth():
        console.print(
            f"[yellow]Warning:[/yellow] no {SESSION_COOKIE} cookie was captured — "
            "the session may not be authenticated. Try `--from-chrome` instead."
        )
    console.print(f"[green]Session saved:[/green] {STATE_PATH}")


# --- Reuse the session from the user's everyday Chrome -----------------------

_CHROME_COOKIES = (
    Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
)
_KEYCHAIN_SERVICE = "Chrome Safe Storage"


def _chrome_key() -> bytes:
    """Derive Chrome's AES key from the password stored in the login Keychain.

    Reading the Keychain entry triggers a one-time approval dialog on macOS.
    """
    out = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", _KEYCHAIN_SERVICE],
        capture_output=True, text=True, check=True,
    )
    password = out.stdout.strip().encode()
    return hashlib.pbkdf2_hmac("sha1", password, b"saltysalt", 1003, 16)


def _decrypt_cookie(enc: bytes, key: bytes) -> str:
    """Decrypt one Chrome cookie value (AES-128-CBC, fixed space IV)."""
    if enc[:3] not in (b"v10", b"v11"):
        return ""  # unencrypted / unknown scheme — skip
    proc = subprocess.run(
        ["openssl", "enc", "-aes-128-cbc", "-d", "-nopad",
         "-K", key.hex(), "-iv", (b" " * 16).hex()],
        input=enc[3:], capture_output=True,
    )
    pt = proc.stdout
    if not pt:
        return ""
    pad = pt[-1]  # strip PKCS7 padding
    if 1 <= pad <= 16:
        pt = pt[:-pad]

    def _printable(b: bytes) -> bool:
        try:
            b.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    # Chrome >= 130 prepends a 32-byte SHA256(domain) to the plaintext.
    if not _printable(pt) and _printable(pt[32:]):
        pt = pt[32:]
    return pt.decode("utf-8", "replace")


def import_from_chrome() -> int:
    """Import Substack cookies from the local Chrome profile into STATE_PATH.

    Returns the number of cookies written. Raises RuntimeError if Chrome's cookie
    store is missing or no authenticated session cookie is found.
    """
    if not _CHROME_COOKIES.exists():
        raise RuntimeError(f"Chrome cookie store not found at {_CHROME_COOKIES}")

    key = _chrome_key()
    tmp = Path(tempfile.gettempdir()) / "_substack_chrome_cookies.sqlite"
    shutil.copy2(_CHROME_COOKIES, tmp)  # copy: Chrome keeps the live DB locked
    try:
        db = sqlite3.connect(str(tmp))
        rows = db.execute(
            "select host_key, name, encrypted_value, path, expires_utc, "
            "is_secure, is_httponly from cookies where host_key like '%substack%'"
        ).fetchall()
        db.close()
    finally:
        tmp.unlink(missing_ok=True)

    cookies = []
    got_session = False
    for host, name, enc, path, expires, secure, httponly in rows:
        value = _decrypt_cookie(enc, key)
        if not value:
            continue
        if name == SESSION_COOKIE:
            got_session = True
        cookies.append({
            "name": name,
            "value": value,
            "domain": host,
            "path": path or "/",
            # Chrome stores expiry as microseconds since 1601-01-01.
            "expires": (expires / 1_000_000 - 11644473600) if expires else -1,
            "httpOnly": bool(httponly),
            "secure": bool(secure),
            "sameSite": "Lax",
        })

    if not got_session:
        raise RuntimeError(
            f"No {SESSION_COOKIE} cookie in Chrome — log into Substack in Chrome "
            "first, then re-run."
        )

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"cookies": cookies, "origins": []}, indent=2))
    console.print(
        f"[green]Imported {len(cookies)} Substack cookies from Chrome[/green] "
        f"({SESSION_COOKIE} present) -> {STATE_PATH}"
    )
    return len(cookies)


if __name__ == "__main__":  # convenience: `python -m substack_toolkit.auth`
    raise SystemExit(0 if import_from_chrome() else 1)
