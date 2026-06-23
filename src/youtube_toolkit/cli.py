"""CLI for YouTube capture: `youtube-toolkit`."""
from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(help="Capture YouTube transcripts into the unified Obsidian vault.",
                  no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def capture(
    url: str = typer.Argument(..., help="Video, channel (@handle or /shorts), or playlist URL."),
    limit: Optional[int] = typer.Option(None, help="For channels/playlists/shorts: cap new items."),
) -> None:
    """Capture a video, or every video/short of a channel/playlist (resumable)."""
    from . import capture as cap
    console.print(f"[bold]Capturing YouTube[/bold] {url}")
    cap.capture(url, limit=limit)


@app.command("build")
def build(
    vault_path: Optional[str] = typer.Option(None, "--vault-path",
        help="Vault root. Overrides MEDIA_VAULT_DIR."),
) -> None:
    """Build the unified Obsidian vault (Substack + YouTube + web)."""
    from media_core import unified_vault
    try:
        unified_vault.build_from_disk(vault_dir=vault_path)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
