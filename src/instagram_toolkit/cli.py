"""Command-line interface for the Instagram toolkit: `instagram-toolkit`.

Subcommands:
    login          Save an Instagram session cookie (use a BURNER account).
    crawl          Capture a public profile's posts + reels into data/media.json.
    crawl-hashtag  Discover posts by hashtag into data/media.json.
    build          Build the unified Obsidian vault (Substack + YouTube + web + IG).
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from . import auth as auth_mod

app = typer.Typer(
    help="Capture public Instagram captions + metadata into the unified Obsidian vault.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

_BURNER_WARNING = (
    "[yellow]⚠ Use a DEDICATED / BURNER Instagram account, never your primary — "
    "scraping can get an account restricted or locked.[/yellow]"
)


@app.command()
def login(
    from_chrome: bool = typer.Option(
        False, "--from-chrome",
        help="Reuse your existing Chrome session (log into Instagram in Chrome first).",
    ),
) -> None:
    """Save an Instagram session cookie — via browser login or by importing Chrome's."""
    console.print(_BURNER_WARNING)
    if from_chrome:
        try:
            auth_mod.import_from_chrome()
        except RuntimeError as exc:
            console.print(f"[yellow]{exc}[/yellow]")
            raise typer.Exit(code=1)
        return
    auth_mod.login()


@app.command()
def crawl(
    handle: str = typer.Argument(..., help="Public profile username, e.g. bateel."),
    limit: Optional[int] = typer.Option(
        30, help="Cap new posts captured this run (keep small — IG rate-limits)."
    ),
) -> None:
    """Capture a public profile's posts + reels (captions + metadata) — resumable."""
    from . import crawler

    console.print(
        f"[bold]Capturing Instagram[/bold] @{handle.lstrip('@')} "
        "(captions + metadata only — no media downloaded)."
    )
    try:
        crawler.crawl(handle, limit=limit)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("crawl-hashtag")
def crawl_hashtag(
    tag: str = typer.Argument(..., help="Hashtag without '#', e.g. bhopaldates."),
    limit: Optional[int] = typer.Option(
        30, help="Cap new posts captured this run (keep small — IG rate-limits)."
    ),
) -> None:
    """Discover posts by hashtag (captions + metadata) — resumable."""
    from . import crawler

    console.print(
        f"[bold]Capturing Instagram[/bold] #{tag.lstrip('#')} "
        "(captions + metadata only — no media downloaded)."
    )
    try:
        crawler.crawl_hashtag(tag, limit=limit)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("build")
def build(
    vault_path: Optional[str] = typer.Option(
        None, "--vault-path", help="Vault root. Overrides MEDIA_VAULT_DIR."
    ),
) -> None:
    """Build the unified Obsidian vault (Substack + YouTube + web + Instagram)."""
    from media_core import unified_vault

    try:
        unified_vault.build_from_disk(vault_dir=vault_path)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
