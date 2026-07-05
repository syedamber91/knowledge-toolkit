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
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from rich.console import Console

from .config import CONTENT_PATH, VAULT_DIR
from .models import KIND_ARTICLE, KIND_INSTAGRAM, KIND_YOUTUBE, MediaCatalog, MediaItem
from youtube_toolkit.capture import video_id_of

console = Console()

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_KIND_LABEL = {KIND_YOUTUBE: "YouTube", KIND_ARTICLE: "Web", KIND_INSTAGRAM: "Instagram"}
_KIND_FOLDER = {KIND_YOUTUBE: "youtube", KIND_ARTICLE: "web", KIND_INSTAGRAM: "instagram"}

# Per-kind labels for the single "open the original" link and the body heading.
_LINK_LABEL = {KIND_YOUTUBE: "Watch on YouTube", KIND_ARTICLE: "Open article",
               KIND_INSTAGRAM: "Open on Instagram"}
_BODY_HEADING = {KIND_YOUTUBE: "## Transcript", KIND_ARTICLE: "## Article",
                 KIND_INSTAGRAM: "## Caption"}
_DESC_HEADING = {KIND_YOUTUBE: "## Description", KIND_ARTICLE: "## Summary"}
_BODY_WARNING = {KIND_YOUTUBE: "No transcript available for this video.",
                 KIND_ARTICLE: "Article body could not be extracted.",
                 KIND_INSTAGRAM: "Caption could not be captured for this post."}

_IG_SHORTCODE_RE = re.compile(r"/(?:p|reel|tv)/([^/?#]+)")


def shortcode_of(url: str) -> str:
    """Extract the Instagram shortcode from a /p/<code>/, /reel/<code>/ or /tv/ URL."""
    m = _IG_SHORTCODE_RE.search(url or "")
    return m.group(1) if m else ""


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
    if item.kind == KIND_INSTAGRAM:
        return f"{base}-{shortcode_of(item.url) or _short(item.url)}"
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
    if item.like_count is not None:
        fm.append(f"like_count: {item.like_count}")
    if item.comment_count is not None:
        fm.append(f"comment_count: {item.comment_count}")
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
    if item.like_count is not None or item.comment_count is not None:
        meta.append(f"{item.like_count or 0} likes · {item.comment_count or 0} comments")
    if meta:
        body.append("*" + " · ".join(meta) + "*")
    link_label = _LINK_LABEL.get(item.kind, "Open link")
    body.append(f"\n> Source: [{link_label}]({item.url})")
    if not item.body_accessible:
        warn = _BODY_WARNING.get(item.kind, "Body could not be captured.")
        body += ["", f"> [!warning] {warn}"]
    if item.description and item.kind in _DESC_HEADING:
        body += ["", _DESC_HEADING[item.kind], "", item.description]
    if item.topics:
        body += ["", "## Topics", "",
                 " · ".join(f"[[{slugify(t)}|{t}]]" for t in item.topics)]
    if item.body_markdown:
        heading = _BODY_HEADING.get(item.kind, "## Content")
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
    ig = len(catalog.by_kind(KIND_INSTAGRAM))
    counts = f"{yt} YouTube videos · {web} web articles"
    if ig:
        counts += f" · {ig} Instagram posts"
    lines = ["---", 'title: "Learning from YouTube & Websites"',
             "tags: [home, moc]", "---", "",
             "# Learning from YouTube & Websites", "",
             f"{counts}. Open the **graph view** "
             "to see how topics connect them.", "", "## Sources"]
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


# --- Substack adaptation -----------------------------------------------------

def _sub_post_basename(post) -> str:
    return slugify(post.slug or post.title)

def _sub_note_path(handle: str, post) -> str:
    return f"Substack/posts/{slugify(handle)}/{_sub_post_basename(post)}"

def _sub_channel_moc(handle: str) -> str:
    return f"{slugify(handle)}-channel"

def _render_sub_post(post, handle: str) -> str:
    """Substack post note with topic links that resolve to the ROOT topics/."""
    fm = ["---", f"title: {_yaml_quote(post.title)}", f"channel: {handle}"]
    if post.author:
        fm.append(f"author: {_yaml_quote(post.author)}")
    if post.published_at:
        fm.append(f"published: {post.published_at.date().isoformat()}")
    fm += [f"url: {post.url}", f"paid: {str(post.is_paid).lower()}",
           f"topics: {_yaml_list(_yaml_quote(t) for t in post.topics)}",
           f"tags: {_yaml_list(post.keywords)}", "---"]
    body = ["", f"# {post.title}", ""]
    if post.subtitle:
        body += [f"*{post.subtitle}*", ""]
    body.append(f"> Source: [Open post]({post.url})")
    if post.is_paid and not post.body_accessible:
        body += ["", "> [!warning] Paid post — body not accessible with the current session."]
    if post.topics:
        body += ["", "## Topics", "",
                 " · ".join(f"[[{slugify(t)}|{t}]]" for t in post.topics)]
    if post.body_markdown:
        body += ["", "---", "", post.body_markdown]
    return "\n".join(fm + body).rstrip() + "\n"

def _render_sub_channel_moc(channel) -> str:
    posts = sorted(channel.posts, key=lambda p: p.published_at or _EPOCH, reverse=True)
    name = channel.name or channel.handle
    lines = ["---", f"title: {_yaml_quote(name + ' (Channel)')}",
             "tags: [channel, moc]", "---", "", f"# {name}", "",
             f"> {channel.url}", "", "## Posts"]
    for post in posts:
        date = f" — {post.published_at.date().isoformat()}" if post.published_at else ""
        lines.append(f"- [[{_sub_note_path(channel.handle, post)}|{post.title}]]{date}")
    return "\n".join(lines).rstrip() + "\n"


# --- unified build -----------------------------------------------------------

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
    distinct from Home.md (current state) and topics/*.md (cross-links).
    Skips writing an entry when nothing changed, so repeated no-op rebuilds
    don't spam the log.
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


def build_unified(media, substack, vault_dir=None):
    """Write the unified vault: media + Substack content notes sharing one topics/."""
    target = Path(vault_dir).expanduser() if vault_dir else VAULT_DIR
    target.mkdir(parents=True, exist_ok=True)

    # Migration: drop stale per-source Substack topic notes / Home.
    shutil.rmtree(target / "Substack" / "topics", ignore_errors=True)
    (target / "Substack" / "Home.md").unlink(missing_ok=True)

    # topic -> source_label -> [(note_path, title)]
    topic_index = defaultdict(lambda: defaultdict(list))
    source_items = defaultdict(list)

    # --- media content notes ---
    for item in media.items:
        moc = _source_moc_name(item)
        source_items[moc].append(item)
        _write(target / _KIND_FOLDER[item.kind] / _source_slug(item)
               / f"{_item_basename(item)}.md", _render_item(item, moc))
        for topic in item.topics:
            topic_index[topic][_source_label(item)].append((_item_link(item), item.title))

    for moc, items in source_items.items():
        _write(target / "sources" / f"{moc}.md",
               _render_source_moc(_source_label(items[0]), items[0].kind, "", items))

    # --- substack content notes ---
    if substack is not None:
        for channel in substack.channels:
            for post in channel.posts:
                _write(target / "Substack" / "posts" / slugify(channel.handle)
                       / f"{_sub_post_basename(post)}.md",
                       _render_sub_post(post, channel.handle))
                label = f"Substack · {channel.handle}"
                for topic in post.topics:
                    topic_index[topic][label].append(
                        (_sub_note_path(channel.handle, post), post.title))
            _write(target / "Substack" / "channels" / f"{_sub_channel_moc(channel.handle)}.md",
                   _render_sub_channel_moc(channel))

    # --- shared root topic notes ---
    for topic, by_source in topic_index.items():
        lines = ["---", f"title: {_yaml_quote(topic)}", "tags: [topic]", "---",
                 "", f"# {topic}", ""]
        for label in sorted(by_source):
            lines.append(f"## {label}")
            for note_path, title in by_source[label]:
                lines.append(f"- [[{note_path}|{title}]]")
            lines.append("")
        _write(target / "topics" / f"{slugify(topic)}.md",
               "\n".join(lines).rstrip() + "\n")

    # --- ingestion log (append-only; distinct from Home's current-state view) ---
    yt_count = len([i for i in media.items if i.kind == KIND_YOUTUBE])
    web_count = len([i for i in media.items if i.kind == KIND_ARTICLE])
    ig_count = len([i for i in media.items if i.kind == KIND_INSTAGRAM])
    sub_count = sum(len(c.posts) for c in substack.channels) if substack is not None else 0
    breakdown = f"{yt_count} YouTube, {web_count} web, {ig_count} Instagram, {sub_count} Substack"
    _log_ingest(target, len(media.items) + sub_count, breakdown)

    # --- root Home ---
    home = ["---", 'title: "Knowledge Vault"', "tags: [home, moc]", "---", "",
            "# Knowledge Vault", "",
            "Unified topics across Substack, YouTube and web. Open the graph view.",
            "See [[Log|Ingestion Log]] for a running history of what's been added.",
            "", "## Sources"]
    for moc, items in source_items.items():
        home.append(f"- [[sources/{moc}|{_source_label(items[0])}]] ({len(items)})")
    if substack is not None:
        for channel in substack.channels:
            label = channel.name or channel.handle
            home.append(f"- [[Substack/channels/{_sub_channel_moc(channel.handle)}"
                        f"|Substack · {label}]] ({len(channel.posts)})")
    home += ["", "## Topics"]
    for topic in sorted(topic_index, key=lambda t: (-sum(len(v) for v in topic_index[t].values()), t)):
        total = sum(len(v) for v in topic_index[topic].values())
        home.append(f"- [[{slugify(topic)}|{topic}]] ({total})")
    _write(target / "Home.md", "\n".join(home).rstrip() + "\n")

    console.print(f"[green]Unified vault written:[/green] {target} "
                  f"({len(media.items)} media items, {len(topic_index)} topics)")
    return target


def build_from_disk(vault_dir=None):
    """Build the unified vault from data/media.json (+ data/substack.json if present)."""
    from substack_toolkit.config import CONTENT_PATH as SUB_PATH
    from substack_toolkit.models import SubstackCatalog
    if not CONTENT_PATH.exists():
        raise RuntimeError(f"No media at {CONTENT_PATH}. Capture something first.")
    media = MediaCatalog.model_validate_json(CONTENT_PATH.read_text(encoding="utf-8"))
    substack = None
    if SUB_PATH.exists():
        substack = SubstackCatalog.model_validate_json(SUB_PATH.read_text(encoding="utf-8"))
    return build_unified(media, substack, vault_dir=vault_dir)
