"""Interactive authentication and session persistence.

Login is deliberately *manual*: a real browser window opens, you sign in with
your own credentials (including any OTP/MFA), and only then is the session
saved to ``.auth/udemy_state.json`` for reuse. Your password is never read or
stored by this tool.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import BrowserContext, sync_playwright
from rich.console import Console

from .config import STATE_PATH, ensure_dirs, settings

console = Console()


def login() -> None:
    """Open a browser, let the user log in manually, then save the session."""
    ensure_dirs()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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


@contextmanager
def authenticated_context(headed: bool = False) -> Iterator[BrowserContext]:
    """Yield a browser context restored from the saved session."""
    if not has_saved_session():
        raise RuntimeError("No saved session. Run `udemy-toolkit login` first.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        context = browser.new_context(storage_state=str(STATE_PATH))
        try:
            yield context
        finally:
            browser.close()


def session_is_valid() -> bool:
    """Best-effort check that the saved session still resolves to a logged-in page."""
    if not has_saved_session():
        return False
    with authenticated_context(headed=False) as context:
        page = context.new_page()
        page.goto(
            f"{settings.base_url.rstrip('/')}/api-2.0/users/me/",
            wait_until="domcontentloaded",
        )
        return "anonymous" not in page.content().lower()
