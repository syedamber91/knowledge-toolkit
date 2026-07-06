"""Materialize the captured catalog as an Obsidian vault.

Each lesson becomes one Markdown note with YAML frontmatter, organised under
``vault/<Course>/<Module>/``. Notes are interconnected with ``[[wikilinks]]`` so
Obsidian's graph view surfaces the correlations between topics:

* **Structural** — every lesson links to its Module/Course Map-of-Content (MOC)
  note, and MOCs link back down to their lessons.
* **Sequential** — prev/next links along the lesson order.
* **Content-based** — a "Related" section linking the lessons that share the
  most salient keywords, plus derived ``#tags`` that cluster topics in the graph.

The vault is the human-facing knowledge store; ``data/content.json`` remains the
internal, resumable crawl cache that this module reads from.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from rich.console import Console

from .config import CONTENT_PATH, VAULT_DIR, ensure_dirs
from .models import Catalog, Lesson

console = Console()

# Minimal stopword list for keyword extraction / tagging.
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "you", "are",
    "was", "but", "not", "all", "can", "has", "have", "will", "what", "how",
    "why", "when", "which", "into", "out", "about", "their", "them", "its",
    "our", "more", "less", "than", "then", "also", "such", "may", "one", "two",
    "use", "using", "used", "based", "part", "lesson", "module", "video",
    "soic", "course", "introduction", "overview",
}
_WORD_RE = re.compile(r"[a-z][a-z0-9]{3,}")

MAX_TAGS = 6
MAX_RELATED = 5


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "untitled"


def _keywords(text: str) -> list[str]:
    return [w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS]


@dataclass
class Note:
    """A planned lesson note: its file path and computed link targets."""

    lesson: Lesson
    course_title: str
    module_title: str
    basename: str  # unique note name used for wikilinks
    rel_path: Path
    keywords: Counter = field(default_factory=Counter)
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)  # basenames
    prev: str | None = None
    next: str | None = None
    module_moc: str = ""
    course_moc: str = ""


def _unique(basename: str, taken: set[str]) -> str:
    candidate = basename
    i = 2
    while candidate in taken:
        candidate = f"{basename}-{i}"
        i += 1
    taken.add(candidate)
    return candidate


def _plan_notes(catalog: Catalog) -> list[Note]:
    """Decide file paths, unique basenames, keywords, tags and links."""
    notes: list[Note] = []
    taken: set[str] = set()

    for course in catalog.courses:
        course_slug = slugify(course.title)
        course_moc = _unique(f"{course_slug}-moc", taken)
        for module in course.modules:
            module_slug = slugify(module.title)
            module_moc = _unique(f"{module_slug}-moc", taken)
            module_notes: list[Note] = []
            for lesson in module.lessons:
                base = _unique(slugify(lesson.title), taken)
                rel = Path(course_slug) / module_slug / f"{base}.md"
                text = f"{lesson.title}\n{lesson.body_text}\n" + "\n".join(lesson.key_points)
                kw = Counter(_keywords(text))
                note = Note(
                    lesson=lesson,
                    course_title=course.title,
                    module_title=module.title,
                    basename=base,
                    rel_path=rel,
                    keywords=kw,
                    tags=[w for w, _ in kw.most_common(MAX_TAGS)],
                    module_moc=module_moc,
                    course_moc=course_moc,
                )
                module_notes.append(note)
                notes.append(note)
            # Sequential prev/next within the module.
            for i, note in enumerate(module_notes):
                if i > 0:
                    note.prev = module_notes[i - 1].basename
                if i < len(module_notes) - 1:
                    note.next = module_notes[i + 1].basename

    _compute_related(notes)
    return notes


def _compute_related(notes: list[Note]) -> None:
    """Link each note to the few others with the highest shared-keyword score."""
    for i, note in enumerate(notes):
        scores: list[tuple[int, str]] = []
        for j, other in enumerate(notes):
            if i == j:
                continue
            shared = note.keywords & other.keywords  # Counter intersection
            score = sum(shared.values())
            if score:
                scores.append((score, other.basename))
        scores.sort(key=lambda s: (-s[0], s[1]))
        note.related = [name for _, name in scores[:MAX_RELATED]]


def _yaml_list(items: Iterable[str]) -> str:
    items = list(items)
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


def _transcript_basename(note: Note) -> str:
    return f"{note.basename}-transcript"


def _render_note(note: Note) -> str:
    lesson = note.lesson
    fm = [
        "---",
        f'title: "{lesson.title}"',
        f"course: \"{note.course_title}\"",
        f"module: \"{note.module_title}\"",
        f"source_url: {lesson.url}",
    ]
    if lesson.lesson_type:
        fm.append(f"type: {lesson.lesson_type}")
    if lesson.duration:
        fm.append(f'duration: "{lesson.duration}"')
    if lesson.has_attachment:
        fm.append("has_attachment: true")
    if lesson.captions_url:
        fm.append(f"captions_url: {lesson.captions_url}")
    if lesson.crawled_at:
        fm.append(f"crawled_at: {lesson.crawled_at.isoformat()}")
    fm.append(f"tags: {_yaml_list(note.tags)}")
    fm.append("---")

    body = ["", f"# {lesson.title}", ""]
    body.append(f"*Part of [[{note.module_moc}|{note.module_title}]] · "
                f"[[{note.course_moc}|{note.course_title}]]*")
    if lesson.url:
        body.append(f"\n> Source: [Open lesson]({lesson.url})")
    if lesson.ai_summary:
        body += ["", "## AI summary", "", "> _AI-generated summary the portal "
                 "displays; not the original lesson body._", "", lesson.ai_summary]
    if lesson.body_text:
        tname = _transcript_basename(note)
        body += ["", "## Transcript", "", f"[[{tname}|📄 Full transcript →]]"]
    if lesson.key_points:
        body += ["", "## Key points"] + [f"- {p}" for p in lesson.key_points]
    if lesson.resource_links:
        body += ["", "## Resources"] + [f"- {l}" for l in lesson.resource_links]
    if note.related:
        body += ["", "## Related"] + [f"- [[{r}]]" for r in note.related]

    nav = []
    if note.prev:
        nav.append(f"[[{note.prev}|← Previous]]")
    if note.next:
        nav.append(f"[[{note.next}|Next →]]")
    if nav:
        body += ["", "---", " · ".join(nav)]

    return "\n".join(fm + body).rstrip() + "\n"


def _render_transcript(note: Note) -> str:
    lesson = note.lesson
    lines = [
        "---",
        f'title: "{lesson.title} — Transcript"',
        f"course: \"{note.course_title}\"",
        f"source_url: {lesson.url}",
        f"lesson: \"[[{note.basename}|{lesson.title}]]\"",
        "tags: [transcript]",
        "---",
        "",
        f"# {lesson.title} — Transcript",
        "",
        f"*← [[{note.basename}|Back to lesson note]] · "
        f"[Open lesson]({lesson.url})*",
        "",
        "---",
        "",
        lesson.body_text,
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_module_moc(module_title: str, course_moc: str, lessons: list[Note]) -> str:
    lines = [
        "---",
        f'title: "{module_title} (MOC)"',
        "tags: [moc]",
        "---",
        "",
        f"# {module_title}",
        "",
        f"*Part of [[{course_moc}]]*",
        "",
        "## Lessons",
    ]
    lines += [f"- [[{n.basename}|{n.lesson.title}]]" for n in lessons]
    return "\n".join(lines).rstrip() + "\n"


def _render_course_moc(course_title: str, modules: list[tuple[str, str]]) -> str:
    # modules: list of (module_moc_basename, module_title)
    lines = [
        "---",
        f'title: "{course_title} (MOC)"',
        "tags: [moc]",
        "---",
        "",
        f"# {course_title}",
        "",
        "## Modules",
    ]
    lines += [f"- [[{moc}|{title}]]" for moc, title in modules]
    return "\n".join(lines).rstrip() + "\n"


def _render_home(courses: list[tuple[str, str]]) -> str:
    lines = [
        "---",
        'title: "SOIC Knowledge Vault"',
        "tags: [moc, home]",
        "---",
        "",
        "# SOIC Knowledge Vault",
        "",
        "Open the **graph view** to explore how topics connect.",
        "See [[Log|Ingestion Log]] for a running history of what's been added.",
        "",
        "## Courses",
    ]
    lines += [f"- [[{moc}|{title}]]" for moc, title in courses]
    return "\n".join(lines).rstrip() + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- ingestion log (append-only; distinct from Home's current-state view) ----

_LOG_TOTAL_RE = re.compile(r"\((\d+) total")


def _last_logged_total(log_path: Path) -> int:
    """Total item count recorded in the log's last entry, or 0 with no log yet."""
    if not log_path.exists():
        return 0
    for line in reversed(log_path.read_text(encoding="utf-8").splitlines()):
        m = _LOG_TOTAL_RE.search(line)
        if m:
            return int(m.group(1))
    return 0


def _log_ingest(target: Path, total: int, breakdown: str) -> None:
    """Append one line to Log.md recording the delta since the last build.

    Log.md is append-only — a running ingestion history, never overwritten,
    distinct from Home.md (current state). Skips writing an entry when nothing
    changed, so repeated no-op rebuilds don't spam the log.
    """
    log_path = target / "Log.md"
    is_first_entry = not log_path.exists()
    delta = total - _last_logged_total(log_path)
    if delta == 0:
        return
    if is_first_entry:
        # Backfill entry for pre-existing content — these items weren't just
        # captured in this one build, so don't claim they were.
        action = f"{total} item(s) already in vault (log started here)"
    else:
        action = f"{delta} new item(s) captured" if delta > 0 else f"{-delta} item(s) removed"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if is_first_entry:
        header = ("---\ntitle: \"Ingestion Log\"\ntags: [log]\n---\n\n"
                   "# Ingestion Log\n\n"
                   "A running history of what was added to (or removed from) this "
                   "vault and when — append-only, never rewritten.\n\n")
        _write(log_path, header)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"- **{stamp}** — {action} ({total} total: {breakdown})\n")


def build_vault(catalog: Catalog, vault_dir: Path | str | None = None) -> Path:
    """Write the full Obsidian vault and return its path.

    ``vault_dir`` overrides the destination (e.g. a folder inside your real
    Obsidian vault); when omitted it falls back to the configured ``VAULT_DIR``.
    """
    ensure_dirs()
    target_dir = Path(vault_dir).expanduser() if vault_dir else VAULT_DIR
    notes = _plan_notes(catalog)
    by_url = {n.lesson.url: n for n in notes}
    written = 0

    # Lesson notes (and separate transcript files where available).
    for note in notes:
        _write(target_dir / note.rel_path, _render_note(note))
        written += 1
        if note.lesson.body_text:
            transcript_path = (
                target_dir / note.rel_path.parent / f"{_transcript_basename(note)}.md"
            )
            _write(transcript_path, _render_transcript(note))

    # MOCs, rebuilt from the catalog structure (reusing planned basenames).
    home_courses: list[tuple[str, str]] = []
    for course in catalog.courses:
        course_modules: list[tuple[str, str]] = []
        course_moc = ""
        course_slug = slugify(course.title)
        for module in course.modules:
            mod_notes = [by_url[l.url] for l in module.lessons if l.url in by_url]
            if not mod_notes:
                continue
            module_moc = mod_notes[0].module_moc
            course_moc = mod_notes[0].course_moc
            _write(
                target_dir / course_slug / f"{module_moc}.md",
                _render_module_moc(module.title, course_moc, mod_notes),
            )
            course_modules.append((module_moc, module.title))
        if course_moc:
            _write(target_dir / course_slug / f"{course_moc}.md",
                   _render_course_moc(course.title, course_modules))
            home_courses.append((course_moc, course.title))

    _log_ingest(target_dir, written, f"{written} lesson notes")

    _write(target_dir / "Home.md", _render_home(home_courses))

    console.print(f"[green]Obsidian vault written:[/green] {target_dir} "
                  f"({written} lesson notes)")
    console.print("Open that folder in Obsidian (or it's already inside your vault) "
                  "and use the graph view.")
    return target_dir


def build_vault_from_disk(vault_dir: Path | str | None = None) -> Path:
    if not CONTENT_PATH.exists():
        raise RuntimeError(
            f"No crawled content at {CONTENT_PATH}. Run `soic-toolkit crawl` first."
        )
    catalog = Catalog.model_validate_json(CONTENT_PATH.read_text(encoding="utf-8"))
    return build_vault(catalog, vault_dir=vault_dir)
