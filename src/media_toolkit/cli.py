"""Command-line interface for the media (YouTube + web) toolkit.

Subcommands:
    youtube      Capture a video, channel, or playlist (transcript + metadata).
    web          Capture one or more web articles (readable text).
    build-vault  Build the unified Obsidian vault from captured items.
    list-topics  Show the topic vocabulary and per-topic captured counts.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from .config import CONTENT_PATH

app = typer.Typer(
    help="Capture YouTube transcripts and web articles into a unified Obsidian vault.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def youtube(
    url: str = typer.Argument(..., help="Video, channel (@handle/URL), or playlist URL."),
    limit: Optional[int] = typer.Option(
        None, help="For channels/playlists: stop after this many new videos."),
) -> None:
    """Capture a YouTube video, or every video of a channel/playlist (resumable)."""
    from . import youtube as yt

    console.print(f"[bold]Capturing YouTube[/bold] {url} (transcript + metadata).")
    yt.capture(url, limit=limit)


@app.command()
def web(
    urls: Optional[List[str]] = typer.Argument(
        None, help="One or more article URLs."),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Path to a file with one URL per line."),
) -> None:
    """Capture readable article text from one or more web pages (resumable)."""
    from . import web as web_mod

    collected: List[str] = list(urls or [])
    if file:
        if not file.exists():
            console.print(f"[yellow]File not found: {file}[/yellow]")
            raise typer.Exit(code=1)
        collected += [ln.strip() for ln in file.read_text().splitlines()
                      if ln.strip() and not ln.strip().startswith("#")]
    if not collected:
        console.print("[yellow]Provide at least one URL, or --file <path>.[/yellow]")
        raise typer.Exit(code=1)
    console.print(f"[bold]Capturing {len(collected)} article(s).[/bold]")
    web_mod.capture_urls(collected)


@app.command("build-vault")
def build_vault(
    vault_path: Optional[str] = typer.Option(
        None, "--vault-path", help="Folder to write notes into. Overrides MEDIA_VAULT_DIR."),
) -> None:
    """Build the unified YouTube + web Obsidian vault."""
    from . import vault as vault_mod

    try:
        vault_mod.build_vault_from_disk(vault_dir=vault_path)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("list-topics")
def list_topics() -> None:
    """Print the topic vocabulary and per-topic captured item counts."""
    from .models import MediaCatalog
    from .topics import TOPIC_VOCABULARY

    counts: dict[str, int] = {}
    if CONTENT_PATH.exists():
        catalog = MediaCatalog.model_validate_json(CONTENT_PATH.read_text())
        for item in catalog.items:
            for topic in item.topics:
                counts[topic] = counts.get(topic, 0) + 1
    for topic in TOPIC_VOCABULARY:
        console.print(f"{topic:26} {counts.get(topic, 0)}")


if __name__ == "__main__":
    app()
