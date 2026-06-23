"""CLI for web article capture: `web-toolkit`."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

app = typer.Typer(help="Capture readable web articles into the unified Obsidian vault.",
                  no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def capture(
    urls: Optional[List[str]] = typer.Argument(None, help="One or more article URLs."),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File with one URL per line."),
) -> None:
    """Capture readable article text from one or more web pages (resumable)."""
    from . import capture as cap
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
    cap.capture_urls(collected)


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
