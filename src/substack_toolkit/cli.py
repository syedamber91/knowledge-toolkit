"""Command-line interface for the Substack toolkit.

Subcommands:
    login        Open a browser and save your Substack session cookie.
    crawl        Capture posts for a publication into data/substack.json.
    build-vault  Build the Obsidian vault from captured posts.
    list-topics  Show the topic vocabulary and per-topic post counts.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from . import auth as auth_mod
from . import vault as vault_mod
from .config import CONTENT_PATH

app = typer.Typer(
    help="Personal Substack archiver for your own subscriptions -> Obsidian.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def login(
    handle: str = typer.Option(
        None, "--handle", help="Publication handle, e.g. vutr (browser login only)."
    ),
    from_chrome: bool = typer.Option(
        False, "--from-chrome",
        help="Reuse your existing Google Chrome session instead of opening a "
             "browser. Requires being logged into Substack in Chrome.",
    ),
) -> None:
    """Save a Substack session cookie — via browser login or by importing Chrome's."""
    if from_chrome:
        try:
            auth_mod.import_from_chrome()
        except RuntimeError as exc:
            console.print(f"[yellow]{exc}[/yellow]")
            raise typer.Exit(code=1)
        return
    if not handle:
        console.print("[yellow]Provide --handle for browser login, or use --from-chrome.[/yellow]")
        raise typer.Exit(code=1)
    auth_mod.login(handle)


@app.command()
def crawl(
    handle: str = typer.Argument(..., help="Publication handle, e.g. vutr."),
    limit: Optional[int] = typer.Option(
        None, help="Stop after capturing this many new posts (useful for a first test)."
    ),
    free_only: bool = typer.Option(
        False, "--free-only",
        help="Skip paid posts entirely (for publications you follow but don't pay "
             "for, where paid posts would only be truncated previews).",
    ),
) -> None:
    """Capture accessible post text into data/substack.json (resumable)."""
    from . import crawler as crawler_mod

    scope = "free posts only" if free_only else "accessible text only — no media"
    console.print(f"[bold]Crawling[/bold] {handle} ({scope}).")
    try:
        crawler_mod.crawl(handle, limit=limit, free_only=free_only)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("build-vault")
def build_vault(
    vault_path: Optional[str] = typer.Option(
        None, "--vault-path",
        help="Folder to write notes into. Overrides SUBSTACK_VAULT_DIR.",
    )
) -> None:
    """Build the Substack Obsidian vault (one linked note per post)."""
    try:
        vault_mod.build_vault_from_disk(vault_dir=vault_path)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("list-topics")
def list_topics() -> None:
    """Print the topic vocabulary and per-topic captured post counts."""
    from .models import SubstackCatalog
    from .topics import TOPIC_VOCABULARY

    counts: dict[str, int] = {}
    if CONTENT_PATH.exists():
        catalog = SubstackCatalog.model_validate_json(CONTENT_PATH.read_text())
        for channel in catalog.channels:
            for post in channel.posts:
                for topic in post.topics:
                    counts[topic] = counts.get(topic, 0) + 1
    for topic in TOPIC_VOCABULARY:
        console.print(f"{topic:24} {counts.get(topic, 0)}")


if __name__ == "__main__":
    app()
