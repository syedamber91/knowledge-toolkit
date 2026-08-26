"""Authentication and session persistence.

Two ways to obtain a session, both storing only the resulting cookies under
``.auth/udemy_state.json`` (Playwright storage_state format) — never a password:

* :func:`login` — open a real browser, log in manually, save the cookies.
* :func:`import_from_chrome` — reuse the session from your everyday Google
  Chrome, where you are already logged in. This decrypts only the Udemy
  cookies from Chrome's local store (macOS Keychain approval required) and is
  the reliable path when Udemy's bot-detection challenge loops an automated
  browser indefinitely.

Both produce the same on-disk shape, so the crawler does not care which was used.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from playwright.sync_api import BrowserContext, sync_playwright
from rich.console import Console

from .config import AUTH_DIR, STATE_PATH, ensure_dirs, settings

console = Console()

# The cookie that proves an authenticated Udemy session; httpOnly, sent on every
# API request. Both Playwright and Chrome's cookie store expose it.
SESSION_COOKIE = "access_token"


def _launch_headed(p, headless: bool = False):
    """Prefer the user's real installed Chrome over bundled Chromium.

    Udemy's bot-detection challenge is far more likely to loop indefinitely
    against Playwright's bundled Chromium than against a real Chrome install;
    this is a normal browser-choice config, not a bot-detection bypass.
    """
    try:
        return p.chromium.launch(headless=headless, channel="chrome")
    except Exception:
        return p.chromium.launch(headless=headless)


def login() -> None:
    """Open a browser, let the user log in manually, then save the session."""
    ensure_dirs()
    with sync_playwright() as p:
        browser = _launch_headed(p, headless=False)
        context = browser.new_context()
        page = context.new_page()

        login_url = settings.base_url.rstrip("/")
        console.print(f"[bold]Opening[/bold] {login_url}")
        page.goto(login_url, wait_until="domcontentloaded")

        console.print(
            "\n[bold yellow]Log in to your Udemy account in the browser window.[/bold yellow]\n"
            "Complete any OTP/2FA step until you reach My Learning.\n"
        )
        input("Once you are fully logged in, return here and press Enter to save the session... ")

        context.storage_state(path=str(STATE_PATH))
        console.print(f"[green]Session saved to[/green] {STATE_PATH}")
        browser.close()


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


@contextmanager
def authenticated_context(headed: bool = True) -> Iterator[BrowserContext]:
    """Yield a browser context restored from the saved session.

    Defaults to headed: Udemy's Cloudflare protection returns 403 "Just a
    moment..." to headless Chrome even with a fully valid session cookie, so
    headless is not a viable default here regardless of authentication state.
    """
    if not has_saved_session():
        raise RuntimeError("No saved session. Run `udemy-toolkit login` first.")
    with sync_playwright() as p:
        browser = _launch_headed(p, headless=not headed)
        context = browser.new_context(storage_state=str(STATE_PATH))
        try:
            yield context
        finally:
            browser.close()


def session_is_valid() -> bool:
    """Best-effort check that the saved session still resolves to a logged-in page."""
    if not has_saved_session():
        return False
    with authenticated_context() as context:
        page = context.new_page()
        resp = page.goto(
            f"{settings.base_url.rstrip('/')}/api-2.0/users/me/",
            wait_until="domcontentloaded",
        )
        if resp is None or not resp.ok:
            return False
        try:
            # A logged-in response is a user object with a numeric id; an
            # anonymous/expired session gets a small {"_class":"anonymous..."}
            # payload with no id. Checking for "anonymous" as a substring is
            # wrong: a real user's own default-avatar filename contains it
            # (e.g. "anonymous_3.png"), so that check always failed.
            data = page.evaluate("() => JSON.parse(document.body.innerText)")
        except Exception:
            return False
        return isinstance(data, dict) and data.get("_class") == "user" and bool(data.get("id"))


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
    """Import Udemy cookies from the local Chrome profile into STATE_PATH.

    Returns the number of cookies written. Raises RuntimeError if Chrome's cookie
    store is missing or no authenticated session cookie is found.
    """
    if not _CHROME_COOKIES.exists():
        raise RuntimeError(f"Chrome cookie store not found at {_CHROME_COOKIES}")

    key = _chrome_key()
    tmp = Path(tempfile.gettempdir()) / "_udemy_chrome_cookies.sqlite"
    shutil.copy2(_CHROME_COOKIES, tmp)  # copy: Chrome keeps the live DB locked
    try:
        db = sqlite3.connect(str(tmp))
        rows = db.execute(
            "select host_key, name, encrypted_value, path, expires_utc, "
            "is_secure, is_httponly from cookies where host_key like '%udemy.com%'"
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
            f"No {SESSION_COOKIE} cookie in Chrome — log into Udemy in Chrome "
            "first, then re-run."
        )

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"cookies": cookies, "origins": []}, indent=2))
    console.print(
        f"[green]Imported {len(cookies)} Udemy cookies from Chrome[/green] "
        f"({SESSION_COOKIE} present) -> {STATE_PATH}"
    )
    return len(cookies)
