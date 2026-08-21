"""Catalog -> Obsidian notes for the standalone Udemy Vault.

Implements the repo's standing three-part routing pattern:
  1. Index      — Home.md plus per-course and per-section MOC notes.
  2. Log        — append-only Log.md recording when items arrived or left.
  3. Cross-links— shared topics/<topic>.md notes plus inline [[wikilinks]].
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from media_core.topics import match_topics

from .config import resolve_vault_dir
from .extract import format_seconds
from .models import UdemyCatalog

_LOG_TOTAL_RE = re.compile(r"\((\d+) total")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug or "untitled"


def note_filename(section_order: int, lecture_title: str) -> str:
    return f"{section_order}-{slugify(lecture_title)}.md"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    """Append one line to Log.md recording the delta since the last build."""
    log_path = target / "Log.md"
    is_first_entry = not log_path.exists()
    delta = total - _last_logged_total(log_path)
    if delta == 0:
        return
    if is_first_entry:
        action = f"{total} item(s) already in vault (log started here)"
    else:
        action = f"{delta} new item(s) captured" if delta > 0 else f"{-delta} item(s) removed"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if is_first_entry:
        header = (
            "---\ntitle: \"Ingestion Log\"\ntags: [log]\n---\n\n"
            "# Ingestion Log\n\n"
            "A running history of what was added to (or removed from) this "
            "vault and when — append-only, never rewritten.\n\n"
        )
        _write(log_path, header)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"- **{stamp}** — {action} ({total} total: {breakdown})\n")


def _lecture_note(course, section, lecture, topics) -> str:
    duration = format_seconds(lecture.duration_seconds) if lecture.duration_seconds else ""
    topic_links = ", ".join(f'"[[topics/{t}|{t}]]"' for t in topics)
    frontmatter = [
        "---",
        f'title: "{lecture.title}"',
        f'course: "{course.title}"',
        f'section: "{section.title}"',
        f'url: "{lecture.url}"',
        f'duration: "{duration}"',
        f"captured_at: {lecture.captured_at.isoformat() if lecture.captured_at else ''}",
        f"topics: [{', '.join(topics)}]",
        f"topic_links: [{topic_links}]",
        "---",
        "",
    ]
    body = [
        f"# {lecture.title}",
        "",
        f"Part of [[courses/{slugify(course.title)}|{course.title}]] → "
        f"[[courses/{slugify(course.title)}/{section.order}-{slugify(section.title)}|{section.title}]]",
        "",
        f"[Open on Udemy]({lecture.url})",
        "",
        "## Transcript",
        "",
        lecture.transcript or "_No transcript available for this lecture._",
        "",
    ]
    return "\n".join(frontmatter + body)


def build_vault(catalog: UdemyCatalog, vault_dir: Optional[Path] = None) -> Path:
    """Write the whole Udemy Vault; returns the target directory."""
    target = Path(vault_dir).expanduser() if vault_dir else resolve_vault_dir()
    target.mkdir(parents=True, exist_ok=True)

    topic_index = defaultdict(list)  # topic -> [(note_link, title)]
    total = 0

    for course in catalog.courses:
        course_slug = slugify(course.title)
        section_links = []

        for section in course.sections:
            lecture_links = []
            for lecture in section.lectures:
                topics = match_topics(f"{lecture.title}\n{lecture.transcript}")
                filename = note_filename(section.order, lecture.title)
                note_link = f"lectures/{course_slug}/{filename[:-3]}"
                _write(
                    target / "lectures" / course_slug / filename,
                    _lecture_note(course, section, lecture, topics),
                )
                lecture_links.append(f"- [[{note_link}|{lecture.title}]]")
                for topic in topics:
                    topic_index[topic].append((note_link, lecture.title))
                total += 1

            section_file = f"{section.order}-{slugify(section.title)}.md"
            _write(
                target / "courses" / course_slug / section_file,
                "\n".join(
                    [
                        "---",
                        f'title: "{section.title}"',
                        "---",
                        "",
                        f"# {section.title}",
                        "",
                        f"Section of [[courses/{course_slug}|{course.title}]]",
                        "",
                        *lecture_links,
                        "",
                    ]
                ),
            )
            section_links.append(
                f"- [[courses/{course_slug}/{section_file[:-3]}|{section.title}]]"
            )

        _write(
            target / "courses" / f"{course_slug}.md",
            "\n".join(
                [
                    "---",
                    f'title: "{course.title}"',
                    f'instructor: "{course.instructor}"',
                    f'url: "{course.url}"',
                    "---",
                    "",
                    f"# {course.title}",
                    "",
                    f"[Open on Udemy]({course.url})",
                    "",
                    "## Sections",
                    "",
                    *section_links,
                    "",
                ]
            ),
        )

    for topic, entries in topic_index.items():
        lines = sorted({f"- [[{link}|{title}]]" for link, title in entries})
        _write(
            target / "topics" / f"{topic}.md",
            "\n".join(
                ["---", f'title: "{topic}"', "tags: [topic]", "---", "", f"# {topic}", "", *lines, ""]
            ),
        )

    course_lines = [
        f"- [[courses/{slugify(c.title)}|{c.title}]] — {len(c.lectures())} lecture(s)"
        for c in catalog.courses
    ]
    _write(
        target / "Home.md",
        "\n".join(
            [
                "---",
                'title: "Udemy Vault"',
                "---",
                "",
                "# Udemy Vault",
                "",
                "Lecture transcripts captured from courses on Udemy. Transcript text only "
                "— no video or audio is stored here.",
                "",
                "## Courses",
                "",
                *course_lines,
                "",
                "## Meta",
                "",
                "- [[Log|Ingestion Log]]",
                "",
            ]
        ),
    )

    _log_ingest(
        target,
        total,
        f"{len(catalog.courses)} course(s), {len(topic_index)} topic(s)",
    )
    return target
