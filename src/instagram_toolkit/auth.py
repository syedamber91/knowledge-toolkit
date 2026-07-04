"""Capture the user's Instagram session for the crawler.

Two ways to obtain a session, both storing only cookies under
``.auth/instagram_state.json`` (never a password):

* :func:`login` — open a real browser, log in manually, save the cookies.
* :func:`import_from_chrome` — reuse the session from your everyday Google
  Chrome, decrypting only the Instagram cookies from Chrome's local store
  (macOS Keychain approval required).

:func:`load_session_into` injects the saved cookies into an Instaloader instance
and verifies the session with ``test_login()``.

SAFETY: scraping can get an Instagram account restricted or locked. Authenticate
with a DEDICATED / BURNER account, never the account you rely on.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from rich.console import Console

from .config import AUTH_DIR, SESSION_COOKIE, STATE_PATH

console = Console()

_LOGIN_URL = "https://www.instagram.com/accounts/login/"


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


def _saved_cookies() -> dict[str, str]:
    """name -> value for every saved cookie (empty if none)."""
    if not STATE_PATH.exists():
        return {}
    state = json.loads(STATE_PATH.read_text())
    return {c["name"]: c["value"] for c in state.get("cookies", []) if c.get("value")}


def login(timeout: float = 300.0, poll: float = 2.0) -> None:
    """Open a browser to Instagram and auto-save cookies once you're logged in.

    Polls for the ``sessionid`` cookie so no keypress is needed — log in at your
    own pace in the opened window and this returns as soon as the authenticated
    session appears (or raises if it does not within ``timeout`` seconds).
    """
    import time as _time

    from playwright.sync_api import sync_playwright

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    console.print(
        f"Opening [bold]{_LOGIN_URL}[/bold] — log in with your BURNER account in "
        "the window that appears. I'll detect and save the session automatically "
        f"(waiting up to {int(timeout)}s)."
    )
    deadline = _time.time() + timeout
    saved = False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(_LOGIN_URL)
        while _time.time() < deadline:
            has_session = any(
                c.get("name") == SESSION_COOKIE and c.get("value")
                and "instagram" in (c.get("domain") or "")
                for c in context.cookies()
            )
            if has_session:
                context.storage_state(path=str(STATE_PATH))
                saved = True
                break
            _time.sleep(poll)
        browser.close()
    if saved and session_has_auth():
        console.print(f"[green]Session saved:[/green] {STATE_PATH}")
    else:
        console.print(
            "[yellow]No logged-in Instagram session detected before the timeout. "
            "Re-run `instagram-toolkit login` and complete the login in the "
            "window.[/yellow]"
        )
        raise RuntimeError("Instagram login not detected before timeout.")


# --- Reuse the session from the user's everyday Chrome -----------------------

_CHROME_COOKIES = (
    Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
)
_KEYCHAIN_SERVICE = "Chrome Safe Storage"


def _chrome_key() -> bytes:
    """Derive Chrome's AES key from the password in the login Keychain.

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
    """Import Instagram cookies from the local Chrome profile into STATE_PATH.

    Returns the number of cookies written. Raises RuntimeError if Chrome's cookie
    store is missing or no authenticated session cookie is found.
    """
    if not _CHROME_COOKIES.exists():
        raise RuntimeError(f"Chrome cookie store not found at {_CHROME_COOKIES}")

    key = _chrome_key()
    tmp = Path(tempfile.gettempdir()) / "_instagram_chrome_cookies.sqlite"
    shutil.copy2(_CHROME_COOKIES, tmp)  # copy: Chrome keeps the live DB locked
    try:
        db = sqlite3.connect(str(tmp))
        rows = db.execute(
            "select host_key, name, encrypted_value, path, expires_utc, "
            "is_secure, is_httponly from cookies where host_key like '%instagram%'"
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
            f"No {SESSION_COOKIE} cookie in Chrome — log into Instagram in Chrome "
            "first (ideally with a burner account), then re-run."
        )

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"cookies": cookies, "origins": []}, indent=2))
    console.print(
        f"[green]Imported {len(cookies)} Instagram cookies from Chrome[/green] "
        f"({SESSION_COOKIE} present) -> {STATE_PATH}"
    )
    return len(cookies)


# --- Instaloader integration -------------------------------------------------

def load_session_into(loader) -> str:
    """Inject saved cookies into an Instaloader instance; return the username.

    Raises RuntimeError if there is no saved session or it is not authenticated.
    """
    if not session_has_auth():
        raise RuntimeError(
            "No authenticated Instagram session. Run "
            "`instagram-toolkit login --from-chrome` first (use a burner account)."
        )
    cookies = _saved_cookies()
    session = loader.context._session
    for name, value in cookies.items():
        session.cookies.set(name, value, domain=".instagram.com")
    try:
        username = loader.test_login()
    except Exception as exc:  # noqa: BLE001 - network/session failure
        raise RuntimeError(f"Instagram session check failed: {exc}") from exc
    if not username:
        raise RuntimeError(
            "Saved Instagram session is not valid (expired or logged out). "
            "Re-run `instagram-toolkit login --from-chrome`."
        )
    loader.context.username = username
    return username


if __name__ == "__main__":  # convenience: `python -m instagram_toolkit.auth`
    raise SystemExit(0 if import_from_chrome() else 1)
