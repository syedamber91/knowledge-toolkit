"""Typer CLI for the SOIC method extraction pipeline."""

from __future__ import annotations

from pathlib import Path

import typer

from .corpus import load_corpus
from .eligibility import apply_eligibility, load_eligibility
from .publish import write_bundle
from .reconcile import ReconcileOutput
from .router import route

app = typer.Typer(help="Extract SOIC's investing method into an executable spec.")

DEFAULT_CORPUS = Path("data/content.json")
DEFAULT_CONFIG = Path("configs/course_eligibility.yaml")


@app.command("route")
def route_cmd(
    corpus: Path = typer.Option(DEFAULT_CORPUS, help="content.json path"),
    config: Path = typer.Option(DEFAULT_CONFIG, help="eligibility config"),
) -> None:
    """Report candidate spans per eligible lesson."""
    lessons = apply_eligibility(load_corpus(corpus), load_eligibility(config))
    eligible = [l for l in lessons if l.eligible]
    cands = route(lessons)
    typer.echo("lessons=%d eligible=%d candidates=%d"
               % (len(lessons), len(eligible), len(cands)))


@app.command("publish")
def publish_cmd(
    dest: Path = typer.Option(..., help="bundle output directory"),
    corpus: Path = typer.Option(DEFAULT_CORPUS),
    config: Path = typer.Option(DEFAULT_CONFIG),
) -> None:
    """Write an (empty-until-extracted) bundle skeleton plus the SNAPSHOT."""
    lessons = apply_eligibility(load_corpus(corpus), load_eligibility(config))
    write_bundle(ReconcileOutput(), {l.lesson_id: l for l in lessons}, dest)
    typer.echo("wrote bundle to %s" % dest)


if __name__ == "__main__":
    app()
