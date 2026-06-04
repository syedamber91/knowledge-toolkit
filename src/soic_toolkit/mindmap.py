"""Turn the captured catalog into a Markmap mind map.

The Markdown produced here is the portable source of truth (works in any Markmap
viewer / VS Code extension / markmap.js.org). If Node is available, it can be
rendered to a standalone interactive ``mindmap.html`` via ``markmap-cli``.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rich.console import Console

from .config import CONTENT_PATH, MINDMAP_HTML_PATH, MINDMAP_MD_PATH, ensure_dirs
from .models import Catalog

console = Console()


def _escape(text: str) -> str:
    return text.replace("\n", " ").strip()


def build_markdown(catalog: Catalog, title: str = "SOIC Knowledge Map") -> str:
    """Render the catalog as nested Markmap Markdown.

    Heading levels: course (#) → module (##) → lesson (###) → key points (bullets).
    """
    lines: list[str] = [
        "---",
        "markmap:",
        "  colorFreezeLevel: 2",
        "---",
        "",
        f"# {title}",
        "",
    ]
    for course in catalog.courses:
        lines.append(f"## {_escape(course.title)}")
        for module in course.modules:
            lines.append(f"### {_escape(module.title)}")
            for lesson in module.lessons:
                label = _escape(lesson.title)
                if lesson.url:
                    lines.append(f"- [{label}]({lesson.url})")
                else:
                    lines.append(f"- {label}")
                for point in lesson.key_points:
                    lines.append(f"  - {_escape(point)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_markdown(catalog: Catalog) -> Path:
    ensure_dirs()
    md = build_markdown(catalog)
    MINDMAP_MD_PATH.write_text(md, encoding="utf-8")
    return MINDMAP_MD_PATH


def render_html() -> bool:
    """Render the Markdown to interactive HTML using markmap-cli via npx.

    Returns True on success. If Node/npx isn't available, prints guidance and
    returns False — the Markdown is still usable on its own.
    """
    npx = shutil.which("npx")
    if not npx:
        console.print(
            "[yellow]Node/npx not found.[/yellow] Markdown written; to render HTML install "
            "Node and run:\n"
            f"  npx markmap-cli {MINDMAP_MD_PATH} -o {MINDMAP_HTML_PATH}"
        )
        return False
    try:
        subprocess.run(
            [npx, "-y", "markmap-cli", str(MINDMAP_MD_PATH), "-o",
             str(MINDMAP_HTML_PATH), "--no-open"],
            check=True,
        )
        console.print(f"[green]Interactive mind map:[/green] {MINDMAP_HTML_PATH}")
        return True
    except subprocess.CalledProcessError as exc:
        console.print(f"[red]markmap-cli failed:[/red] {exc}")
        return False


def build_map() -> Path:
    """Load the catalog, write Markdown, and attempt an HTML render."""
    if not CONTENT_PATH.exists():
        raise RuntimeError(
            f"No crawled content at {CONTENT_PATH}. Run `soic-toolkit crawl` first."
        )
    catalog = Catalog.model_validate_json(CONTENT_PATH.read_text(encoding="utf-8"))
    md_path = write_markdown(catalog)
    console.print(f"[green]Mind map Markdown:[/green] {md_path}")
    render_html()
    return md_path
