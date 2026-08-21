"""Command-line interface for the Udemy transcript toolkit.

Subcommands:
    login        Open a browser and save your authenticated session.
    status       Report whether a saved session exists and is still valid.
    crawl        Capture transcripts for one course, by URL.
    build-vault  Build the Obsidian Udemy Vault from the catalog.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from . import auth as auth_mod
from . import crawler as crawler_mod
from . import vault as vault_mod
from .config import CATALOG_PATH, STATE_PATH, resolve_vault_dir, settings
from .models import UdemyCatalog

app = typer.Typer(
    help="Capture transcripts from courses you have purchased on Udemy.",
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
        console.print("[yellow]No saved session.[/yellow] Run `udemy-toolkit login`.")
        raise typer.Exit(code=1)
    console.print(f"Saved session: {STATE_PATH}")
    if auth_mod.session_is_valid():
        console.print("[green]Session looks valid.[/green]")
    else:
        console.print("[yellow]Session appears expired.[/yellow] Run `udemy-toolkit login` again.")
        raise typer.Exit(code=1)


@app.command()
def crawl(
    course_url: str = typer.Argument(..., help="Full URL of a course you own."),
    limit: Optional[int] = typer.Option(None, help="Stop after N lectures. Use a small value first."),
) -> None:
    """Capture lecture transcripts for one course."""
    from .fetcher import PlaywrightFetcher

    def _announce(title: str) -> None:
        console.print(f"Resolved course: [bold]{title}[/bold]")

    try:
        with auth_mod.authenticated_context(headed=settings.crawl_headed) as context:
            summary = crawler_mod.crawl_course(
                course_url,
                PlaywrightFetcher(context),
                limit=limit,
                on_resolved=_announce,
            )
    except crawler_mod.SessionExpired as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    console.print(
        f"[green]{summary.course_title}[/green]: {summary.captured} captured, "
        f"{summary.skipped_no_captions} without captions, {summary.already_seen} already known."
    )
    console.print(f"Catalog: {CATALOG_PATH}")


@app.command("build-vault")
def build_vault() -> None:
    """Build the Obsidian Udemy Vault from the captured catalog."""
    catalog = UdemyCatalog.load(CATALOG_PATH)
    if not catalog.courses:
        console.print("[yellow]Nothing captured yet.[/yellow] Run `udemy-toolkit crawl <url>` first.")
        raise typer.Exit(code=1)
    target = vault_mod.build_vault(catalog, vault_dir=resolve_vault_dir())
    console.print(f"[green]Vault built:[/green] {target} ({catalog.total_lectures()} lecture note(s))")

    report = vault_mod.verify_vault(target)
    problems = {k: v for k, v in report.items() if k != "notes" and v}
    if problems:
        console.print(f"[yellow]Vault verification found issues:[/yellow] {problems}")
        raise typer.Exit(code=1)
    console.print(f"[green]Verified:[/green] {report['notes']} note(s), no dangling links, all tagged.")
    console.print(f"Routing index: {target / 'index.yaml'}")
