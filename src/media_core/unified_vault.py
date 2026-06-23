"""Materialize the captured media catalog as a unified Obsidian vault.

Layout:
    Home.md
    youtube/<channel-slug>/<video-slug>.md   # one note per video (transcript)
    web/<domain-slug>/<article-slug>.md       # one note per article
    sources/<kind>-<source-slug>.md           # one MOC per channel / site
    topics/<topic-slug>.md                    # shared topic notes

Topic notes are the cross-source linkage: a YouTube video and a web article that
match the same canonical topic appear together in one topic note (grouped by
source), so the graph view connects video and article knowledge by subject.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from rich.console import Console

from .config import CONTENT_PATH, VAULT_DIR
from .models import KIND_ARTICLE, KIND_YOUTUBE, MediaCatalog, MediaItem
from youtube_toolkit.capture import video_id_of

console = Console()

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_KIND_LABEL = {KIND_YOUTUBE: "YouTube", KIND_ARTICLE: "Web"}
_KIND_FOLDER = {KIND_YOUTUBE: "youtube", KIND_ARTICLE: "web"}


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "untitled"


def _yaml_list(items: Iterable[str]) -> str:
    items = list(items)
    return "[]" if not items else "[" + ", ".join(items) + "]"


def _yaml_quote(value: str) -> str:
    escaped = (value or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _short(url: str) -> str:
    return hashlib.sha1((url or "").encode("utf-8")).hexdigest()[:6]


def _source_slug(item: MediaItem) -> str:
    return slugify(item.source or item.source_id or "unknown")


def _item_basename(item: MediaItem) -> str:
    base = slugify(item.title)[:60] or "untitled"
    if item.kind == KIND_YOUTUBE:
        return f"{base}-{video_id_of(item.url) or _short(item.url)}"
    return f"{base}-{_short(item.url)}"


def _item_link(item: MediaItem) -> str:
    return f"{_KIND_FOLDER[item.kind]}/{_source_slug(item)}/{_item_basename(item)}"


def _source_moc_name(item: MediaItem) -> str:
    return f"{item.kind}-{_source_slug(item)}"


def _source_label(item: MediaItem) -> str:
    return f"{_KIND_LABEL.get(item.kind, item.kind)} · {item.source or item.source_id or 'unknown'}"


def _fmt_duration(seconds: int | None) -> str:
    if not seconds:
        return ""
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _render_item(item: MediaItem, source_moc: str) -> str:
    fm = ["---", f"title: {_yaml_quote(item.title)}", f"kind: {item.kind}"]
    if item.source:
        fm.append(f"source: {_yaml_quote(item.source)}")
    if item.author:
        fm.append(f"author: {_yaml_quote(item.author)}")
    if item.published_at:
        fm.append(f"published: {item.published_at.date().isoformat()}")
    fm.append(f"url: {item.url}")
    if item.duration_seconds:
        fm.append(f"duration: {_fmt_duration(item.duration_seconds)}")
    fm.append(f"topics: {_yaml_list(_yaml_quote(t) for t in item.topics)}")
    fm.append(f"tags: {_yaml_list(item.keywords)}")
    fm.append("---")

    body = ["", f"# {item.title}", ""]
    meta = []
    if item.source:
        meta.append(f"[[{source_moc}|{item.source}]]")
    if item.author and item.author != item.source:
        meta.append(item.author)
    if item.published_at:
        meta.append(item.published_at.date().isoformat())
    if item.duration_seconds:
        meta.append(_fmt_duration(item.duration_seconds))
    if meta:
        body.append("*" + " · ".join(meta) + "*")
    link_label = "Watch on YouTube" if item.kind == KIND_YOUTUBE else "Open article"
    body.append(f"\n> Source: [{link_label}]({item.url})")
    if not item.body_accessible:
        warn = ("No transcript available for this video."
                if item.kind == KIND_YOUTUBE else
                "Article body could not be extracted.")
        body += ["", f"> [!warning] {warn}"]
    if item.description:
        body += ["", "## Description" if item.kind == KIND_YOUTUBE else "## Summary",
                 "", item.description]
    if item.topics:
        body += ["", "## Topics", "",
                 " · ".join(f"[[{slugify(t)}|{t}]]" for t in item.topics)]
    if item.body_markdown:
        heading = "## Transcript" if item.kind == KIND_YOUTUBE else "## Article"
        body += ["", "---", "", heading, "", item.body_markdown]
    return "\n".join(fm + body).rstrip() + "\n"


def _render_topic(topic: str, items_by_source: dict[str, list[MediaItem]]) -> str:
    lines = ["---", f"title: {_yaml_quote(topic)}", "tags: [topic]", "---",
             "", f"# {topic}", ""]
    for label in sorted(items_by_source):
        lines.append(f"## {label}")
        for item in items_by_source[label]:
            lines.append(f"- [[{_item_link(item)}|{item.title}]]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_source_moc(label: str, kind: str, url_hint: str,
                       items: list[MediaItem]) -> str:
    items = sorted(items, key=lambda i: i.published_at or _EPOCH, reverse=True)
    lines = ["---", f"title: {_yaml_quote(label)}", "tags: [source, moc]",
             f"kind: {kind}", "---", "", f"# {label}", ""]
    if url_hint:
        lines += [f"> {url_hint}", ""]
    lines.append(f"## Items ({len(items)})")
    for item in items:
        date = f" — {item.published_at.date().isoformat()}" if item.published_at else ""
        lines.append(f"- [[{_item_link(item)}|{item.title}]]{date}")
    return "\n".join(lines).rstrip() + "\n"


def _render_home(catalog: MediaCatalog,
                 topic_index: dict[str, dict[str, list[MediaItem]]],
                 source_items: dict[str, list[MediaItem]]) -> str:
    yt = len(catalog.by_kind(KIND_YOUTUBE))
    web = len(catalog.by_kind(KIND_ARTICLE))
    lines = ["---", 'title: "Learning from YouTube & Websites"',
             "tags: [home, moc]", "---", "",
             "# Learning from YouTube & Websites", "",
             f"{yt} YouTube videos · {web} web articles. Open the **graph view** "
             "to see how topics connect videos and articles.", "", "## Sources"]
    for moc in sorted(source_items):
        items = source_items[moc]
        lines.append(f"- [[{moc}|{_source_label(items[0])}]] ({len(items)})")
    lines += ["", "## Topics"]

    def total(topic: str) -> int:
        return sum(len(v) for v in topic_index[topic].values())

    for topic in sorted(topic_index, key=lambda t: (-total(t), t)):
        lines.append(f"- [[{slugify(topic)}|{topic}]] ({total(topic)})")
    return "\n".join(lines).rstrip() + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_vault(catalog: MediaCatalog,
                vault_dir: Path | str | None = None) -> Path:
    """Write the unified YouTube + web Obsidian vault and return its path."""
    target = Path(vault_dir).expanduser() if vault_dir else VAULT_DIR
    target.mkdir(parents=True, exist_ok=True)

    topic_index: dict[str, dict[str, list[MediaItem]]] = defaultdict(
        lambda: defaultdict(list))
    source_items: dict[str, list[MediaItem]] = defaultdict(list)
    source_url: dict[str, str] = {}

    for item in catalog.items:
        moc = _source_moc_name(item)
        source_items[moc].append(item)
        source_url.setdefault(moc, "")
        _write(target / _KIND_FOLDER[item.kind] / _source_slug(item)
               / f"{_item_basename(item)}.md",
               _render_item(item, moc))
        for topic in item.topics:
            topic_index[topic][_source_label(item)].append(item)

    for moc, items in source_items.items():
        _write(target / "sources" / f"{moc}.md",
               _render_source_moc(_source_label(items[0]), items[0].kind,
                                  source_url.get(moc, ""), items))

    for topic, by_source in topic_index.items():
        _write(target / "topics" / f"{slugify(topic)}.md",
               _render_topic(topic, by_source))

    _write(target / "Home.md", _render_home(catalog, topic_index, source_items))

    console.print(f"[green]Media vault written:[/green] {target} "
                  f"({len(catalog.items)} items, {len(source_items)} sources, "
                  f"{len(topic_index)} topics)")
    return target


def build_vault_from_disk(vault_dir: Path | str | None = None) -> Path:
    if not CONTENT_PATH.exists():
        raise RuntimeError(
            f"No captured content at {CONTENT_PATH}. "
            "Capture something first (media-toolkit youtube/web ...)."
        )
    catalog = MediaCatalog.model_validate_json(CONTENT_PATH.read_text(encoding="utf-8"))
    return build_vault(catalog, vault_dir=vault_dir)
