"""Command-line interface for the SOIC study toolkit.

Subcommands:
    login      Open a browser and save your authenticated session.
    status     Report whether a saved session exists and is still valid.
    crawl      Walk your membership content and capture accessible lesson text.
    build-map  Build the interactive mind map from captured content.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from . import auth as auth_mod
from . import mindmap as mindmap_mod
from . import vault as vault_mod
from .config import STATE_PATH, settings

app = typer.Typer(
    help="Personal study toolkit for your own SOIC/Learnyst membership.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def login() -> None:
    """Open a browser, log in manually, and save the session."""
    auth_mod.login()


@app.command()
def status() -> None:
    """Show whether a saved session exists and appears valid."""
    if not auth_mod.has_saved_session():
        console.print("[yellow]No saved session.[/yellow] Run `soic-toolkit login`.")
        raise typer.Exit(code=1)
    console.print(f"Saved session: {STATE_PATH}")
    console.print("Checking validity (opening portal)…")
    if auth_mod.session_is_valid():
        console.print("[green]Session looks valid.[/green]")
    else:
        console.print(
            "[yellow]Session appears expired.[/yellow] Run `soic-toolkit login` again."
        )
        raise typer.Exit(code=1)


@app.command()
def crawl(
    limit: Optional[int] = typer.Option(
        None, help="Stop after capturing this many new lessons (useful for a first test)."
    )
) -> None:
    """Capture accessible lesson text into data/content.json (resumable)."""
    # Local import keeps Playwright off the import path for `build-map`/`status` help.
    from . import crawler as crawler_mod

    console.print(
        f"[bold]Crawling[/bold] {settings.base_url} "
        "(accessible text only — no media downloaded)."
    )
    try:
        crawler_mod.crawl(limit=limit)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("build-vault")
def build_vault() -> None:
    """Build an Obsidian vault (one linked note per lesson) under vault/."""
    try:
        vault_mod.build_vault_from_disk()
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("build-map")
def build_map() -> None:
    """Build output/mindmap.md (+ mindmap.html if Node is available)."""
    try:
        mindmap_mod.build_map()
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
