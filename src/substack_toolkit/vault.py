"""Materialize the captured Substack catalog as a dedicated Obsidian vault.

Layout:
    Home.md
    channels/<handle>-channel.md      # one MOC per channel
    posts/<handle>/<slug>.md          # one note per post
    topics/<topic-slug>.md            # shared topic notes (cross-channel)

Topic notes are the cross-channel linkage: because every channel matches the same
canonical vocabulary, the same topic resolves to one note here, and that note
lists every post (from every channel) that mentions the topic, grouped by channel.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from rich.console import Console

from .config import CONTENT_PATH, VAULT_DIR
from .models import Channel, Post, SubstackCatalog

console = Console()

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "untitled"


def _yaml_list(items: Iterable[str]) -> str:
    items = list(items)
    return "[]" if not items else "[" + ", ".join(items) + "]"


def _yaml_quote(value: str) -> str:
    # Double-quoted YAML scalar: backslash is the escape char, so escape it
    # first, then escape embedded double-quotes. Keeps titles with paths,
    # regexes, or quotes from producing invalid frontmatter.
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _post_basename(post: Post) -> str:
    return slugify(post.slug or post.title)


def _channel_moc_name(channel: Channel) -> str:
    return f"{slugify(channel.handle)}-channel"


def _render_post(post: Post, handle: str, channel_moc: str) -> str:
    fm = [
        "---",
        f"title: {_yaml_quote(post.title)}",
        f"channel: {handle}",
    ]
    if post.author:
        fm.append(f"author: {_yaml_quote(post.author)}")
    if post.published_at:
        fm.append(f"published: {post.published_at.date().isoformat()}")
    fm.append(f"url: {post.url}")
    fm.append(f"paid: {str(post.is_paid).lower()}")
    fm.append(f"topics: {_yaml_list(_yaml_quote(t) for t in post.topics)}")
    fm.append(f"tags: {_yaml_list(post.keywords)}")
    fm.append("---")

    body = ["", f"# {post.title}", ""]
    if post.subtitle:
        body += [f"*{post.subtitle}*", ""]
    meta = []
    if post.author:
        meta.append(post.author)
    if post.published_at:
        meta.append(post.published_at.date().isoformat())
    meta.append(f"[[{channel_moc}|{handle}]]")
    body.append("*" + " · ".join(meta) + "*")
    body.append(f"\n> Source: [Open post]({post.url})")
    if post.is_paid and not post.body_accessible:
        body += ["", "> [!warning] Paid post — body not accessible with the "
                 "current session."]
    if post.topics:
        body += ["", "## Topics", "",
                 " · ".join(f"[[{slugify(t)}|{t}]]" for t in post.topics)]
    if post.body_markdown:
        body += ["", "---", "", post.body_markdown]
    return "\n".join(fm + body).rstrip() + "\n"


def _render_topic(topic: str, posts_by_channel: dict[str, list[Post]]) -> str:
    lines = ["---", f"title: {_yaml_quote(topic)}", "tags: [topic]", "---",
             "", f"# {topic}", ""]
    for handle in sorted(posts_by_channel):
        lines.append(f"## {handle}")
        for post in posts_by_channel[handle]:
            lines.append(f"- [[{_post_basename(post)}|{post.title}]]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_channel_moc(channel: Channel) -> str:
    posts = sorted(channel.posts, key=lambda p: p.published_at or _EPOCH, reverse=True)
    name = channel.name or channel.handle
    lines = ["---", f"title: {_yaml_quote(name + ' (Channel)')}",
             "tags: [channel, moc]", "---", "", f"# {name}", "",
             f"> {channel.url}", "", "## Posts"]
    for post in posts:
        date = f" — {post.published_at.date().isoformat()}" if post.published_at else ""
        lines.append(f"- [[{_post_basename(post)}|{post.title}]]{date}")
    return "\n".join(lines).rstrip() + "\n"


def _render_home(catalog: SubstackCatalog,
                 topic_index: dict[str, dict[str, list[Post]]]) -> str:
    lines = ["---", 'title: "Substack Knowledge Vault"', "tags: [home, moc]",
             "---", "", "# Substack Knowledge Vault", "",
             "Open the **graph view** to see how topics connect across channels.",
             "", "## Channels"]
    for channel in catalog.channels:
        moc = _channel_moc_name(channel)
        label = channel.name or channel.handle
        lines.append(f"- [[{moc}|{label}]] ({len(channel.posts)} posts)")
    lines += ["", "## Topics"]

    def total(topic: str) -> int:
        return sum(len(v) for v in topic_index[topic].values())

    for topic in sorted(topic_index, key=lambda t: (-total(t), t)):
        lines.append(f"- [[{slugify(topic)}|{topic}]] ({total(topic)})")
    return "\n".join(lines).rstrip() + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_vault(catalog: SubstackCatalog,
                vault_dir: Path | str | None = None) -> Path:
    """Write the Substack Obsidian vault and return its path."""
    target = Path(vault_dir).expanduser() if vault_dir else VAULT_DIR
    target.mkdir(parents=True, exist_ok=True)

    # topic -> channel handle -> [posts]
    topic_index: dict[str, dict[str, list[Post]]] = defaultdict(
        lambda: defaultdict(list)
    )
    written = 0
    for channel in catalog.channels:
        channel_moc = _channel_moc_name(channel)
        for post in channel.posts:
            _write(
                target / "posts" / slugify(channel.handle) / f"{_post_basename(post)}.md",
                _render_post(post, channel.handle, channel_moc),
            )
            written += 1
            for topic in post.topics:
                topic_index[topic][channel.handle].append(post)
        _write(target / "channels" / f"{channel_moc}.md", _render_channel_moc(channel))

    for topic, by_channel in topic_index.items():
        _write(target / "topics" / f"{slugify(topic)}.md",
               _render_topic(topic, by_channel))

    _write(target / "Home.md", _render_home(catalog, topic_index))

    console.print(f"[green]Substack vault written:[/green] {target} "
                  f"({written} posts, {len(topic_index)} topics)")
    return target


def build_vault_from_disk(vault_dir: Path | str | None = None) -> Path:
    if not CONTENT_PATH.exists():
        raise RuntimeError(
            f"No crawled content at {CONTENT_PATH}. "
            "Run `substack-toolkit crawl <handle>` first."
        )
    catalog = SubstackCatalog.model_validate_json(CONTENT_PATH.read_text(encoding="utf-8"))
    return build_vault(catalog, vault_dir=vault_dir)
