"""Catalog -> Obsidian notes for the standalone Udemy Vault.

Implements the repo's standing three-part routing pattern:
  1. Index      — Home.md plus per-course and per-section MOC notes.
  2. Log        — append-only Log.md recording when items arrived or left.
  3. Cross-links— shared topics/<topic>.md notes plus inline [[wikilinks]].
"""

from __future__ import annotations

import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from media_core.topics import match_topics

from .config import resolve_vault_dir
from .extract import format_seconds
from .models import UdemyCatalog

_LOG_TOTAL_RE = re.compile(r"\((\d+) total")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug or "untitled"


def _yaml_quote(value: str) -> str:
    """Render a string as a safely quoted YAML double-quoted scalar."""
    text = (value or "").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def note_filename(section_order: int, lecture_id: str, lecture_title: str) -> str:
    # The lecture id is appended (not just the title slug) so two lectures
    # with identical titles in the same section never collide and silently
    # overwrite each other's notes.
    return f"{section_order}-{slugify(lecture_title)}-{lecture_id}.md"


# A CLOSED vocabulary. Never invent a tag outside this tuple — a fixed list is
# what makes tags a reliable routing index rather than free-text noise.
TAG_VOCABULARY = (
    "fundamentals",
    "setup-install",
    "hands-on-demo",
    "architecture",
    "data",
    "testing",
    "debugging",
    "deployment-ops",
    "security",
    "performance",
    "tooling",
    "career-meta",
    # Not a real content category -- the fallback classify_tags() returns
    # when no cue matches. Included here (rather than special-cased in
    # verify_vault) so it's part of the one closed vocabulary that both the
    # classifier and the verifier -- and the manifest's declared
    # tag_vocabulary -- agree on.
    "uncategorized",
)

_TAG_CUES = {
    "fundamentals": ("introduction", "overview", "basics", "what is", "fundamental", "concept"),
    "setup-install": ("install", "setup", "set up", "environment", "prerequisite", "configure"),
    "hands-on-demo": ("demo", "walkthrough", "let's build", "hands on", "hands-on", "exercise", "project"),
    "architecture": ("architecture", "design pattern", "system design", "component", "structure"),
    "data": ("database", "sql", "schema", "dataset", "query", "storage", "pipeline"),
    "testing": ("test", "unit test", "assertion", "coverage", "pytest", "mock"),
    "debugging": ("debug", "error", "exception", "troubleshoot", "stack trace", "bug"),
    "deployment-ops": ("deploy", "docker", "ci/cd", "pipeline", "production", "kubernetes", "monitor"),
    "security": ("security", "auth", "token", "encryption", "vulnerab", "permission"),
    "performance": ("performance", "optimiz", "latency", "throughput", "cache", "benchmark"),
    "tooling": ("ide", "cli", "editor", "extension", "plugin", "git", "terminal"),
    "career-meta": ("career", "interview", "resume", "course wrap", "next steps", "congratulations"),
}


def classify_tags(text: str) -> List[str]:
    """1-3 tags drawn ONLY from ``TAG_VOCABULARY``, scored by cue frequency."""
    lowered = (text or "").lower()
    scored = []
    for tag in TAG_VOCABULARY:
        if tag not in _TAG_CUES:
            continue  # "uncategorized" -- the no-cue-matched fallback, not a cue itself
        score = sum(lowered.count(cue) for cue in _TAG_CUES[tag])
        if score:
            scored.append((score, tag))
    if not scored:
        return ["uncategorized"]
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [tag for _score, tag in scored[:3]]


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


def _ensure_log_exists(target: Path) -> None:
    """Guarantee Log.md exists, header-only if nothing has been logged yet.

    Home.md unconditionally links [[Log|Ingestion Log]]. ``_log_ingest``
    intentionally writes nothing when the delta is zero (e.g. total==0 on a
    brand-new, lecture-less vault) -- that no-zero-delta-entry rule is a
    pinned contract and is NOT touched here. This just backstops the file's
    existence so a zero-lecture build never leaves that link dangling.
    """
    log_path = target / "Log.md"
    if log_path.exists():
        return
    header = (
        "---\ntitle: \"Ingestion Log\"\ntags: [log]\n---\n\n"
        "# Ingestion Log\n\n"
        "A running history of what was added to (or removed from) this "
        "vault and when — append-only, never rewritten.\n\n"
    )
    _write(log_path, header)


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


def _lecture_note(course, section, lecture, topics, tags) -> str:
    duration = format_seconds(lecture.duration_seconds) if lecture.duration_seconds else ""
    topic_links = ", ".join(f'"[[topics/{t}|{t}]]"' for t in topics)
    frontmatter = [
        "---",
        f"title: {_yaml_quote(lecture.title)}",
        f"course: {_yaml_quote(course.title)}",
        f"section: {_yaml_quote(section.title)}",
        f"url: {_yaml_quote(lecture.url)}",
        f"duration: {_yaml_quote(duration)}",
        f"captured_at: {lecture.captured_at.isoformat() if lecture.captured_at else ''}",
        f"topics: [{', '.join(topics)}]",
        f"topic_links: [{topic_links}]",
        f"tags: [{', '.join(tags)}]",
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


def write_manifest(target: Path, manifest: dict) -> Path:
    """Write index.yaml — the cheap routing layer an agent reads first."""
    import yaml

    path = target / "index.yaml"
    path.write_text(
        "# Machine-readable index of this vault. Read this BEFORE grepping notes:\n"
        "# it maps every lecture to its note path, tags, and topics.\n"
        + yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def verify_vault(target: Path) -> dict:
    """Read the WHOLE built vault and report link/tag defects.

    Deliberately a single pass over every file — never trust per-note
    self-reports that each piece was written correctly.
    """
    target = Path(target)
    notes = sorted(p for p in target.rglob("*.md"))
    stems = {str(p.relative_to(target)).removesuffix(".md") for p in notes}

    dangling, linked_to, untagged, unknown_tags = [], set(), [], []
    for note in notes:
        text = note.read_text(encoding="utf-8")
        for raw in _WIKILINK_RE.findall(text):
            link = raw.strip()
            linked_to.add(link)
            if link not in stems and not link.endswith(".yaml"):
                dangling.append(link)
        if note.parent.name and note.parent.parent.name == "lectures":
            match = re.search(r"^tags: \[(.*)\]$", text, re.MULTILINE)
            found = [t.strip() for t in match.group(1).split(",") if t.strip()] if match else []
            if not found:
                untagged.append(str(note.relative_to(target)))
            unknown_tags.extend(t for t in found if t not in TAG_VOCABULARY)

    orphans = [
        str(p.relative_to(target))
        for p in notes
        if str(p.relative_to(target)).removesuffix(".md") not in linked_to
        and p.name not in {"Home.md", "Log.md"}
    ]

    # Cross-check the notes actually on disk against what the manifest
    # claims was written -- verify_vault only ever inspected files that
    # exist, so a silent filename collision (two notes overwriting one
    # another) previously went unreported even though the manifest still
    # listed both lectures.
    lecture_note_count = sum(
        1 for p in notes if p.parent.name and p.parent.parent.name == "lectures"
    )
    manifest_mismatch: List[str] = []
    manifest_path = target / "index.yaml"
    if manifest_path.exists():
        import yaml

        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        manifest_lecture_count = (manifest.get("counts") or {}).get("lectures")
        if manifest_lecture_count is not None and manifest_lecture_count != lecture_note_count:
            manifest_mismatch.append(
                f"manifest reports {manifest_lecture_count} lecture(s) but "
                f"{lecture_note_count} lecture note file(s) exist on disk"
            )

    return {
        "notes": len(notes),
        "dangling_links": sorted(set(dangling)),
        "orphan_notes": sorted(orphans),
        "untagged": sorted(untagged),
        "unknown_tags": sorted(set(unknown_tags)),
        "manifest_mismatch": manifest_mismatch,
    }


_VAULT_MARKER = ".udemy-vault"


def _looks_like_our_own_vault(target: Path) -> bool:
    """True if ``target`` is empty, unmistakably ours, or safe to treat as ours."""
    if not target.exists():
        return True
    if not any(target.iterdir()):
        return True
    if (target / _VAULT_MARKER).exists():
        return True
    # A prior (marker-less) Udemy build still leaves its own courses/ or
    # lectures/ directory behind -- treat that as proof of prior ownership
    # too, so rebuilding an already-built vault keeps working.
    return (target / "courses").is_dir() or (target / "lectures").is_dir()


def build_vault(catalog: UdemyCatalog, vault_dir: Optional[Path] = None) -> Path:
    """Write the whole Udemy Vault; returns the target directory."""
    target = Path(vault_dir).expanduser() if vault_dir else resolve_vault_dir()

    # Guard against pruning someone else's directory. build_vault deletes
    # topics/courses/lectures/tags below on every run -- if UDEMY_VAULT_DIR
    # is misconfigured to point at, say, the SHARED cross-source Obsidian
    # vault, that rmtree would destroy content other toolkits own. Refuse
    # unless the target is empty/new, already marked as ours, or already
    # has our own prior build structure.
    if not _looks_like_our_own_vault(target):
        raise RuntimeError(
            f"Refusing to build into {target} -- it already contains content "
            "(no .udemy-vault marker and no prior courses/lectures directory "
            "from a previous Udemy build), so it looks like someone else's "
            "vault. If this directory really is meant for the Udemy Vault, "
            "delete it (or create an empty .udemy-vault marker file in it) "
            "and re-run."
        )

    target.mkdir(parents=True, exist_ok=True)
    (target / _VAULT_MARKER).touch(exist_ok=True)

    # Prune generated content directories so a rebuild reflects exactly the
    # current catalog (stale/renamed/removed notes don't linger). Log.md is
    # append-only and lives directly under `target`, never inside these
    # subdirectories, so it is untouched.
    shutil.rmtree(target / "lectures", ignore_errors=True)
    shutil.rmtree(target / "courses", ignore_errors=True)
    shutil.rmtree(target / "topics", ignore_errors=True)
    shutil.rmtree(target / "tags", ignore_errors=True)

    topic_index = defaultdict(list)  # topic -> [(note_link, title)]
    tag_index = defaultdict(list)  # tag -> [(note_link, title)]
    manifest_courses = []
    total = 0

    for course in catalog.courses:
        course_slug = slugify(course.title)
        section_links = []
        manifest_sections = []

        for section in course.sections:
            lecture_links = []
            manifest_lectures = []
            for lecture in section.lectures:
                topics = match_topics(f"{lecture.title}\n{lecture.transcript}")
                tags = classify_tags(f"{lecture.title}\n{lecture.transcript}")
                filename = note_filename(section.order, lecture.id, lecture.title)
                note_link = f"lectures/{course_slug}/{filename[:-3]}"
                _write(
                    target / "lectures" / course_slug / filename,
                    _lecture_note(course, section, lecture, topics, tags),
                )
                lecture_links.append(f"- [[{note_link}|{lecture.title}]]")
                for topic in topics:
                    topic_index[topic].append((note_link, lecture.title))
                for tag in tags:
                    tag_index[tag].append((note_link, lecture.title))
                manifest_lectures.append(
                    {
                        "title": lecture.title,
                        "note": note_link,
                        "url": lecture.url,
                        "section": section.title,
                        "tags": tags,
                        "topics": topics,
                        "has_transcript": lecture.has_transcript,
                        "words": len(lecture.transcript.split()),
                    }
                )
                total += 1

            manifest_sections.append(
                {"title": section.title, "order": section.order, "lectures": manifest_lectures}
            )

            section_file = f"{section.order}-{slugify(section.title)}.md"
            _write(
                target / "courses" / course_slug / section_file,
                "\n".join(
                    [
                        "---",
                        f"title: {_yaml_quote(section.title)}",
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
                    f"title: {_yaml_quote(course.title)}",
                    f"instructor: {_yaml_quote(course.instructor)}",
                    f"url: {_yaml_quote(course.url)}",
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

        manifest_courses.append(
            {
                "title": course.title,
                "note": f"courses/{course_slug}",
                "url": course.url,
                "instructor": course.instructor,
                "sections": manifest_sections,
            }
        )

    for topic, entries in topic_index.items():
        lines = sorted({f"- [[{link}|{title}]]" for link, title in entries})
        _write(
            target / "topics" / f"{topic}.md",
            "\n".join(
                ["---", f'title: "{topic}"', "tags: [topic]", "---", "", f"# {topic}", "", *lines, ""]
            ),
        )

    for tag, entries in tag_index.items():
        lines = sorted({f"- [[{link}|{title}]]" for link, title in entries})
        _write(
            target / "tags" / f"{tag}.md",
            "\n".join(
                ["---", f'title: "{tag}"', "tags: [tag]", "---", "", f"# {tag}", "", *lines, ""]
            ),
        )

    course_lines = [
        f"- [[courses/{slugify(c.title)}|{c.title}]] — {len(c.lectures())} lecture(s)"
        for c in catalog.courses
    ]
    tag_lines = [
        f"- [[tags/{tag}|{tag}]] — {len({link for link, _ in entries})} lecture(s)"
        for tag, entries in sorted(tag_index.items())
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
                "## Tags",
                "",
                *tag_lines,
                "",
                "## Meta",
                "",
                "- [[Log|Ingestion Log]]",
                "- [[index.yaml|Machine-readable index]]",
                "",
            ]
        ),
    )

    _log_ingest(
        target,
        total,
        f"{len(catalog.courses)} course(s), {len(topic_index)} topic(s)",
    )
    _ensure_log_exists(target)

    manifest = {
        "vault": "Udemy Vault",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": (
            "Lecture transcripts captured from purchased Udemy courses. "
            "Transcript text only — no video or audio. Route via tags/ and topics/, "
            "then read the named lecture notes."
        ),
        "tag_vocabulary": list(TAG_VOCABULARY),
        "counts": {
            "courses": len(catalog.courses),
            "lectures": total,
            "topics": len(topic_index),
            "tags": len(tag_index),
        },
        "courses": manifest_courses,
    }
    write_manifest(target, manifest)

    return target
