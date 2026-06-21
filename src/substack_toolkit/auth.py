"""Interactive login: capture the user's Substack session cookie.

The password is never read or stored — the user logs in manually in a real
browser and we persist only the resulting storage state (cookies) under
``.auth/substack_state.json``.
"""

from __future__ import annotations

from rich.console import Console

from .config import AUTH_DIR, STATE_PATH, channel_url

console = Console()


def has_saved_session() -> bool:
    return STATE_PATH.exists()


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
    console.print(f"[green]Session saved:[/green] {STATE_PATH}")
