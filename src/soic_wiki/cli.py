"""Typer CLI wrapping the NotebookLM-brain pipeline + decision engine.

Ties together, per command, exactly the calls that were previously
hand-typed one-off Python snippets each time this session:

  briefing       -- soic_senses.decision_engine.build_briefing, printed
  run-sector     -- notebooklm_sector_pipeline.run_sector_pipeline, then
                     the same deterministic gate every prior batch used,
                     then writes notes/refs.json to disk
  evolve-frameworks -- framework_evolution's propose/parse/render chain,
                     writing a PREVIEW file -- never the real frameworks
                     file. Applying an approved diff stays a manual,
                     human-reviewed step outside this CLI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import typer

from soic_senses.decision_engine import build_briefing
from soic_senses.framework_router import load_frameworks
from soic_senses.notebook_client import ask_notebook
from soic_wiki.framework_evolution import (
    assign_next_framework_numbers,
    build_framework_evolution_prompt,
    parse_framework_response,
    render_proposed_diff,
)
from soic_wiki.notebooklm_sector_pipeline import run_sector_pipeline
from soic_wiki.sector_gate import print_report, run_sector_acceptance_report
from soic_method.corpus import load_corpus

app = typer.Typer(help="NotebookLM-brain sector pipeline + decision engine CLI.")

DEFAULT_CORPUS = Path("data/content.json")


@app.command("briefing")
def briefing_cmd(
    symbol: str = typer.Argument(..., help="Screener.in / NSE symbol, e.g. NAVINFLUOR"),
    keyword: List[str] = typer.Option(..., "--keyword", help="Repeatable; keywords describing the company/theme"),
    frameworks: Path = typer.Option(..., help="Path to decision-frameworks-v1.md"),
    sectors: Optional[Path] = typer.Option(None, help="Path to configs/sector_notebooks.yaml (optional)"),
) -> None:
    """Print a live decision briefing: screener ratios + matching
    frameworks + matching sector context, for one company."""
    result = build_briefing(
        symbol=symbol,
        keywords=list(keyword),
        frameworks_path=str(frameworks),
        sector_registry_path=str(sectors) if sectors else None,
    )
    typer.echo(result.to_markdown())


@app.command("run-sector")
def run_sector_cmd(
    module_title: str = typer.Argument(..., help="Exact module title as it appears in data/content.json"),
    slug: str = typer.Option(..., help="Sector slug, e.g. fluorine-industry-megatrend-or-fad"),
    corpus: Path = typer.Option(DEFAULT_CORPUS, help="content.json path"),
    sector_registry: Path = typer.Option(Path("configs/sector_notebooks.yaml")),
    out_dir: Path = typer.Option(..., help="Where to write notes/ and refs.json"),
    reseed: bool = typer.Option(True, help="Re-upload sources even if the notebook already exists"),
    max_lessons_per_batch: Optional[int] = typer.Option(
        None,
        help=(
            "Split the module into several smaller notebooks of at most this many lessons "
            "each, instead of one notebook holding every lesson. A ceiling, not a forced "
            "split -- a module already at or under this size is unaffected. Added after a "
            "31-lesson notebook fabricated citations that smaller notebooks didn't."
        ),
    ),
) -> None:
    """Run the NotebookLM-brain pipeline for one sector module: assign REF
    codes, ensure/seed the notebook, propose concepts, write each note,
    then run the SAME deterministic gate every prior batch used."""
    all_lessons = load_corpus(corpus)
    matching = [l for l in all_lessons if l.module_title == module_title]
    if not matching:
        typer.echo(f"ERROR: no lessons found for module title {module_title!r} in {corpus}", err=True)
        raise typer.Exit(code=1)

    lessons = [{"lesson_id": l.lesson_id, "title": l.title, "body_text": l.body_text} for l in matching]

    result = run_sector_pipeline(
        module_title=module_title,
        slug=slug,
        lessons=lessons,
        sector_registry_path=sector_registry,
        existing_codes=set(),
        reseed=reseed,
        max_lessons_per_batch=max_lessons_per_batch,
    )

    notes_dir = out_dir / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    for concept_slug, text in result.notes.items():
        (notes_dir / f"{concept_slug}.md").write_text(text, encoding="utf-8")

    (out_dir / "refs.json").write_text(json.dumps(result.ref_codes), encoding="utf-8")

    report = run_sector_acceptance_report(notes_dir, result.ref_codes, label=module_title)
    print_report(report, label=module_title)

    if not report.verdict:
        raise typer.Exit(code=1)


@app.command("evolve-frameworks")
def evolve_frameworks_cmd(
    notebook_id: str = typer.Option(..., help="The sector's NotebookLM notebook_id"),
    sector_title: str = typer.Option(..., help="Sector title, for the query prompt"),
    frameworks: Path = typer.Option(..., help="Path to the CURRENT decision-frameworks-v1.md"),
    out: Path = typer.Option(..., help="Where to write the PREVIEW diff -- never applied automatically"),
) -> None:
    """Propose a framework-file diff for one sector and write it as a
    preview -- decision-frameworks-v1.md itself is NEVER written to by
    this command. A human reviews `out` and applies an approved diff by
    hand, exactly as every framework diff this session was reviewed."""
    existing = load_frameworks(frameworks)
    prompt = build_framework_evolution_prompt(sector_title, existing)
    result = ask_notebook(notebook_id, prompt, timeout=180.0)

    proposal = parse_framework_response(result["answer"])
    numbered = assign_next_framework_numbers(proposal, existing)
    diff = render_proposed_diff(existing, numbered)

    out.write_text(diff, encoding="utf-8")
    typer.echo(f"Wrote proposed diff to {out} -- NOT applied. Review before editing {frameworks}.")


if __name__ == "__main__":
    app()
