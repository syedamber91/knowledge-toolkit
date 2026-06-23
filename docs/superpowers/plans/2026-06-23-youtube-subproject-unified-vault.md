# YouTube sub-project + unified knowledge vault — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split media capture into `media_core` + `youtube_toolkit` + `web_toolkit`, build one unified Obsidian "Obsidian Vault" where Substack + YouTube + web share root topic notes, move SOIC into a standalone "Stock Market Vault", and capture `@JustinSung/shorts`.

**Architecture:** Approach A — a shared `media_core` (config/models/store/topics + `unified_vault.py`) with two peer source packages (`youtube_toolkit`, `web_toolkit`) that only depend on `media_core`. The unified builder reads both the Substack and media catalogs and emits one root `topics/` directory whose notes group entries by source.

**Tech Stack:** Python 3.9, pydantic v2, typer, rich, yt-dlp, youtube-transcript-api, trafilatura, pytest. Run Python as `.venv/bin/python`; tests as `.venv/bin/python -m pytest`. Spec: `docs/superpowers/specs/2026-06-23-youtube-subproject-unified-vault-design.md`.

**Conventions:** the repo uses a `src/` layout; run pytest with `PYTHONPATH=src` (or after `pip install -e .`). The iCloud container root is `~/Library/Mobile Documents/iCloud~md~obsidian/Documents`. Vault paths contain spaces and the literal `iCloud~md~obsidian` (mid-string `~` must NOT be expanded — use absolute paths in `.env`, only a leading `~` expands).

---

## Task 1: Move SOIC into a new "Stock Market Vault"

**Files:**
- Modify: `.env` (the `SOIC_VAULT_DIR` line)

- [ ] **Step 1: Snapshot current SOIC counts (for verification)**

Run:
```bash
SOIC="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/SOIC"
find "$SOIC" -type f | wc -l
```
Record the number.

- [ ] **Step 2: Move SOIC content to the new vault root (atomic, same volume)**

Run:
```bash
SRC="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/SOIC"
DEST="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Stock Market Vault"
mkdir -p "$DEST"
# move CONTENTS of SOIC/ to the new vault root, then drop the empty SOIC dir
( shopt -s dotglob; mv "$SRC"/* "$DEST"/ ) && rmdir "$SRC"
```

- [ ] **Step 3: Verify counts match and source is gone**

Run:
```bash
DEST="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Stock Market Vault"
find "$DEST" -type f | wc -l
ls -d "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/SOIC" 2>&1 || echo "SOIC removed from Obsidian Vault ✓"
```
Expected: file count equals Step 1; SOIC no longer under Obsidian Vault.

- [ ] **Step 4: Point the SOIC toolkit at the new vault**

In `.env`, change the `SOIC_VAULT_DIR=` line to the absolute path (no `~`):
```
SOIC_VAULT_DIR=/Users/syedamberiqbal/Library/Mobile Documents/iCloud~md~obsidian/Documents/Stock Market Vault
```

- [ ] **Step 5: Verify the toolkit resolves the new path**

Run:
```bash
PYTHONPATH=src .venv/bin/python -c "from soic_toolkit.config import VAULT_DIR; print(VAULT_DIR, VAULT_DIR.exists())"
```
Expected: prints the Stock Market Vault path and `True`.
(Note: if `soic_toolkit.config` reads a differently-named var, grep `src/soic_toolkit/config.py` for the env var it uses and set that one.)

- [ ] **Step 6: Commit (.env is usually gitignored; commit only if tracked)**

```bash
git add -u .env 2>/dev/null; git commit -q -m "chore(soic): point vault at new Stock Market Vault" 2>/dev/null || echo "(.env gitignored — nothing to commit)"
```

---

## Task 2: Create `media_core` package (move shared modules)

**Files:**
- Create: `src/media_core/__init__.py`
- Move: `src/media_toolkit/{config,models,store,topics}.py` → `src/media_core/`

- [ ] **Step 1: Create the package and move shared modules with git**

```bash
mkdir -p src/media_core
git mv src/media_toolkit/config.py src/media_core/config.py
git mv src/media_toolkit/models.py src/media_core/models.py
git mv src/media_toolkit/store.py  src/media_core/store.py
git mv src/media_toolkit/topics.py src/media_core/topics.py
printf '"""Shared core for media capture: config, models, catalog store, topic\nvocabulary, and the unified Obsidian vault builder."""\n' > src/media_core/__init__.py
```

- [ ] **Step 2: Fix internal imports inside moved modules**

`store.py` imports `from .config import CONTENT_PATH` and `from .models import MediaCatalog` — these stay valid (same package). No change needed. Verify:
```bash
grep -n "from \.\|import \." src/media_core/*.py
```
Expected: only intra-package relative imports (`.config`, `.models`), which are still correct.

- [ ] **Step 3: Verify media_core imports cleanly**

Run:
```bash
PYTHONPATH=src .venv/bin/python -c "import media_core.config, media_core.models, media_core.store, media_core.topics; print('media_core ok')"
```
Expected: `media_core ok`.

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -q -m "refactor(media): extract shared modules into media_core"
```

---

## Task 3: Create `youtube_toolkit` (capture + CLI)

**Files:**
- Create: `src/youtube_toolkit/__init__.py`, `src/youtube_toolkit/cli.py`
- Move: `src/media_toolkit/youtube.py` → `src/youtube_toolkit/capture.py`
- Modify: `tests/test_media_youtube.py` (repoint imports)

- [ ] **Step 1: Move the module**

```bash
mkdir -p src/youtube_toolkit
git mv src/media_toolkit/youtube.py src/youtube_toolkit/capture.py
printf '"""Capture YouTube videos/shorts (transcript + metadata) into the shared media catalog."""\n' > src/youtube_toolkit/__init__.py
```

- [ ] **Step 2: Repoint its imports to media_core**

In `src/youtube_toolkit/capture.py`, change the source imports:
```bash
sed -i '' \
  -e 's/^from \.config import/from media_core.config import/' \
  -e 's/^from \.models import/from media_core.models import/' \
  -e 's/^from \.store import/from media_core.store import/' \
  -e 's/^from \.topics import/from media_core.topics import/' \
  src/youtube_toolkit/capture.py
```
Verify no stray relative imports remain:
```bash
grep -n "^from \.\|^import \." src/youtube_toolkit/capture.py || echo "no relative imports ✓"
```

- [ ] **Step 3: Create the CLI**

Create `src/youtube_toolkit/cli.py`:
```python
"""CLI for YouTube capture: `youtube-toolkit`."""
from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(help="Capture YouTube transcripts into the unified Obsidian vault.",
                  no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def capture(
    url: str = typer.Argument(..., help="Video, channel (@handle or /shorts), or playlist URL."),
    limit: Optional[int] = typer.Option(None, help="For channels/playlists/shorts: cap new items."),
) -> None:
    """Capture a video, or every video/short of a channel/playlist (resumable)."""
    from . import capture as cap
    console.print(f"[bold]Capturing YouTube[/bold] {url}")
    cap.capture(url, limit=limit)


@app.command("build")
def build(
    vault_path: Optional[str] = typer.Option(None, "--vault-path",
        help="Vault root. Overrides MEDIA_VAULT_DIR."),
) -> None:
    """Build the unified Obsidian vault (Substack + YouTube + web)."""
    from media_core import unified_vault
    try:
        unified_vault.build_from_disk(vault_dir=vault_path)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
```
(`build` is fleshed out in Task 6; importing it here is fine — it only resolves when called.)

- [ ] **Step 4: Repoint the YouTube test imports**

In `tests/test_media_youtube.py`:
```bash
sed -i '' \
  -e 's/import media_toolkit\.youtube as yt/import youtube_toolkit.capture as yt/' \
  -e 's/import media_toolkit\.store as store/import media_core.store as store/' \
  tests/test_media_youtube.py
```

- [ ] **Step 5: Run the YouTube tests**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_media_youtube.py -q`
Expected: PASS (same count as before, 4 tests).

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -q -m "refactor(media): youtube_toolkit as its own package + CLI"
```

---

## Task 4: Create `web_toolkit` (capture + CLI)

**Files:**
- Create: `src/web_toolkit/__init__.py`, `src/web_toolkit/cli.py`
- Move: `src/media_toolkit/web.py` → `src/web_toolkit/capture.py`
- Modify: `tests/test_media_web.py` (repoint imports)

- [ ] **Step 1: Move the module**

```bash
mkdir -p src/web_toolkit
git mv src/media_toolkit/web.py src/web_toolkit/capture.py
printf '"""Capture readable web articles into the shared media catalog."""\n' > src/web_toolkit/__init__.py
```

- [ ] **Step 2: Repoint imports to media_core**

```bash
sed -i '' \
  -e 's/^from \.config import/from media_core.config import/' \
  -e 's/^from \.models import/from media_core.models import/' \
  -e 's/^from \.store import/from media_core.store import/' \
  -e 's/^from \.topics import/from media_core.topics import/' \
  src/web_toolkit/capture.py
grep -n "^from \.\|^import \." src/web_toolkit/capture.py || echo "no relative imports ✓"
```

- [ ] **Step 3: Create the CLI**

Create `src/web_toolkit/cli.py`:
```python
"""CLI for web article capture: `web-toolkit`."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

app = typer.Typer(help="Capture readable web articles into the unified Obsidian vault.",
                  no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def capture(
    urls: Optional[List[str]] = typer.Argument(None, help="One or more article URLs."),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File with one URL per line."),
) -> None:
    """Capture readable article text from one or more web pages (resumable)."""
    from . import capture as cap
    collected: List[str] = list(urls or [])
    if file:
        if not file.exists():
            console.print(f"[yellow]File not found: {file}[/yellow]")
            raise typer.Exit(code=1)
        collected += [ln.strip() for ln in file.read_text().splitlines()
                      if ln.strip() and not ln.strip().startswith("#")]
    if not collected:
        console.print("[yellow]Provide at least one URL, or --file <path>.[/yellow]")
        raise typer.Exit(code=1)
    console.print(f"[bold]Capturing {len(collected)} article(s).[/bold]")
    cap.capture_urls(collected)


@app.command("build")
def build(
    vault_path: Optional[str] = typer.Option(None, "--vault-path",
        help="Vault root. Overrides MEDIA_VAULT_DIR."),
) -> None:
    """Build the unified Obsidian vault (Substack + YouTube + web)."""
    from media_core import unified_vault
    try:
        unified_vault.build_from_disk(vault_dir=vault_path)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Repoint web test imports**

```bash
sed -i '' \
  -e 's/import media_toolkit\.web as web/import web_toolkit.capture as web/' \
  -e 's/import media_toolkit\.store as store/import media_core.store as store/' \
  tests/test_media_web.py
```

- [ ] **Step 5: Run web tests**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_media_web.py -q`
Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -q -m "refactor(media): web_toolkit as its own package + CLI"
```

---

## Task 5: Move media-item rendering into `media_core/unified_vault.py`

This relocates the existing media vault renderers (currently `src/media_toolkit/vault.py`) into `media_core/unified_vault.py`, then deletes the empty `media_toolkit`. Substack aggregation is added in Task 6.

**Files:**
- Move: `src/media_toolkit/vault.py` → `src/media_core/unified_vault.py`
- Delete: `src/media_toolkit/` (cli.py, __init__.py remain — handle below)
- Modify: `tests/test_media_vault.py` (repoint imports)

- [ ] **Step 1: Move the media vault module**

```bash
git mv src/media_toolkit/vault.py src/media_core/unified_vault.py
```

- [ ] **Step 2: Repoint its imports**

In `src/media_core/unified_vault.py`, the imports `from .config`, `from .models` stay valid (now in media_core). But it imports `from .youtube import video_id_of` — repoint to youtube_toolkit:
```bash
sed -i '' -e 's/^from \.youtube import video_id_of/from youtube_toolkit.capture import video_id_of/' \
  src/media_core/unified_vault.py
grep -n "video_id_of" src/media_core/unified_vault.py
```
Expected: the import now reads `from youtube_toolkit.capture import video_id_of`.

- [ ] **Step 3: Remove the now-empty media_toolkit package**

`media_toolkit/cli.py` and `__init__.py` are the only files left; the package is superseded. Remove it and its pyproject script (script removal is in Task 8):
```bash
git rm -r src/media_toolkit
```

- [ ] **Step 4: Repoint vault test imports**

```bash
sed -i '' \
  -e 's/from media_toolkit import vault/from media_core import unified_vault as vault/' \
  -e 's/from media_toolkit\.models import/from media_core.models import/' \
  tests/test_media_vault.py
```

- [ ] **Step 5: Run vault + full media tests**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_media_vault.py tests/test_media_topics.py -q`
Expected: PASS. (`test_media_topics.py` imports `media_toolkit.topics` — fix it too:)
```bash
sed -i '' -e 's/from media_toolkit\.topics import/from media_core.topics import/' tests/test_media_topics.py
PYTHONPATH=src .venv/bin/python -m pytest tests/test_media_vault.py tests/test_media_topics.py -q
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -q -m "refactor(media): media vault renderers -> media_core.unified_vault; drop media_toolkit"
```

---

## Task 6: Unified topic notes across Substack + media

Extend `media_core/unified_vault.py` so the build aggregates BOTH the media catalog and the Substack catalog into one root `topics/`, writes Substack content notes under `Substack/`, and removes the stale `Substack/topics/` + `Substack/Home.md`.

**Files:**
- Modify: `src/media_core/unified_vault.py`
- Test: `tests/test_unified_vault.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_unified_vault.py`:
```python
import re

from media_core import unified_vault as uv
from media_core.models import KIND_ARTICLE, KIND_YOUTUBE, MediaCatalog, MediaItem
from substack_toolkit.models import Channel, Post, SubstackCatalog


def _media():
    return MediaCatalog(items=[
        MediaItem(kind=KIND_YOUTUBE, title="Kafka explained",
                  url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                  source="JustinSung", source_id="UCx",
                  body_markdown="kafka", topics=["Apache Kafka"], keywords=["kafka"]),
        MediaItem(kind=KIND_ARTICLE, title="Kafka in prod",
                  url="https://martinfowler.com/kafka",
                  source="martinfowler.com", source_id="martinfowler.com",
                  body_markdown="kafka", topics=["Apache Kafka"], keywords=["kafka"]),
    ])


def _substack():
    p = Post(title="Why Kafka", slug="why-kafka",
             url="https://vutr.substack.com/p/why-kafka",
             topics=["Apache Kafka"], keywords=["kafka"], body_markdown="kafka body")
    return SubstackCatalog(channels=[Channel(handle="vutr", url="https://vutr.substack.com", posts=[p])])


def test_unified_topic_note_groups_all_sources(tmp_path):
    out = tmp_path / "Obsidian Vault"
    uv.build_unified(_media(), _substack(), vault_dir=out)

    kafka = (out / "topics" / "apache-kafka.md").read_text()
    assert "## Substack · vutr" in kafka
    assert "## YouTube · JustinSung" in kafka
    assert "## Web · martinfowler.com" in kafka
    # links use vault-root-relative paths
    assert "[[Substack/posts/vutr/why-kafka|Why Kafka]]" in kafka

    # content notes written in their subfolders
    assert (out / "Substack" / "posts" / "vutr" / "why-kafka.md").exists()
    assert (out / "youtube" / "justinsung" / "kafka-explained-dQw4w9WgXcQ.md").exists()


def test_unified_build_removes_stale_substack_topics(tmp_path):
    out = tmp_path / "Obsidian Vault"
    stale = out / "Substack" / "topics"
    stale.mkdir(parents=True)
    (stale / "apache-kafka.md").write_text("OLD")
    (out / "Substack" / "Home.md").write_text("OLD")

    uv.build_unified(_media(), _substack(), vault_dir=out)
    assert not stale.exists()
    assert not (out / "Substack" / "Home.md").exists()


def test_unified_vault_link_integrity(tmp_path):
    out = tmp_path / "Obsidian Vault"
    uv.build_unified(_media(), _substack(), vault_dir=out)
    resolvable = set()
    for md in out.rglob("*.md"):
        resolvable.add(md.relative_to(out).as_posix()[:-3]); resolvable.add(md.stem)
    broken = []
    for md in out.rglob("*.md"):
        text = re.sub(r"```.*?```", "", md.read_text(), flags=re.S)
        for t in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text):
            if t not in resolvable:
                broken.append((md.relative_to(out).as_posix(), t))
    assert broken == [], f"broken: {broken}"
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_unified_vault.py -q`
Expected: FAIL (`build_unified` not defined).

- [ ] **Step 3: Implement `build_unified` + Substack rendering**

Append to `src/media_core/unified_vault.py` (uses existing helpers `slugify`, `_render_item`, `_item_link`, `_source_label`, `_source_moc_name`, `_source_slug`, `_item_basename`, `_render_source_moc`, `_write`, `_EPOCH`). Add at top: `import shutil` and `from typing import Optional`.

```python
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

def build_unified(media: MediaCatalog, substack, vault_dir=None):
    """Write the unified vault: media + Substack content notes sharing one topics/."""
    target = Path(vault_dir).expanduser() if vault_dir else VAULT_DIR
    target.mkdir(parents=True, exist_ok=True)

    # Migration: drop stale per-source Substack topic notes / Home.
    shutil.rmtree(target / "Substack" / "topics", ignore_errors=True)
    (target / "Substack" / "Home.md").unlink(missing_ok=True)

    # topic -> source_label -> [(note_path, title)]
    topic_index: dict = defaultdict(lambda: defaultdict(list))
    source_items: dict = defaultdict(list)

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

    # --- root Home ---
    home = ["---", 'title: "Knowledge Vault"', "tags: [home, moc]", "---", "",
            "# Knowledge Vault", "",
            "Unified topics across Substack, YouTube and web. Open the graph view.",
            "", "## Topics"]
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
```
Ensure these names are imported/defined at module top: `defaultdict` (from collections), `Path`, `CONTENT_PATH`, `VAULT_DIR` (from `.config`), `MediaCatalog` (from `.models`), `_yaml_list`, `_yaml_quote` (already present from the moved file). Add `import shutil`.

- [ ] **Step 4: Run the unified-vault tests**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_unified_vault.py -q`
Expected: PASS (3 tests).

- [ ] **Step 5: Keep the legacy media-only `build_vault`/`build_vault_from_disk`?**

`build_vault_from_disk` (media-only) is still referenced by `test_media_vault.py`. Leave it in place (it still works for media-only). No change.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -q -m "feat(media): unified topic notes across Substack + YouTube + web"
```

---

## Task 7: Update `pyproject.toml` entry points + packages

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Replace the media-toolkit script with the two new ones**

In `[project.scripts]`, remove the `media-toolkit = ...` line and add:
```
youtube-toolkit = "youtube_toolkit.cli:app"
web-toolkit = "web_toolkit.cli:app"
```
(`[tool.setuptools.packages.find] where = ["src"]` auto-discovers the new packages; no change needed there.)

- [ ] **Step 2: Reinstall editable so entry points + packages register**

Run: `.venv/bin/python -m pip install -e . --quiet && echo OK`
Expected: `OK`.

- [ ] **Step 3: Smoke the CLIs**

Run:
```bash
.venv/bin/python -m youtube_toolkit.cli --help | head -5
.venv/bin/python -m web_toolkit.cli --help | head -5
```
Expected: both print help with `capture` and `build` commands.

- [ ] **Step 4: Full suite green**

Run: `.venv/bin/python -m pytest -q`
Expected: all pass (prior media tests + new unified tests + substack/soic tests).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -q -m "build: youtube-toolkit + web-toolkit entry points"
```

---

## Task 8: Shorts enumeration test

Confirms `@handle/shorts` URLs enumerate via the nested-tab walker.

**Files:**
- Modify: `tests/test_media_youtube.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_media_youtube.py`:
```python
def test_capture_shorts_tab_enumerates(tmp_path, monkeypatch):
    import media_core.store as store
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(yt.time, "sleep", lambda *a, **k: None)

    # yt-dlp returns a channel page whose entries are a nested "Shorts" tab.
    nested = {"entries": [{"entries": [{"id": "short000001"}, {"id": "short000002"}]}]}
    monkeypatch.setattr(yt, "enumerate_entries",
                        lambda url: yt.enumerate_entries.__wrapped__(url) if False else _walk(nested))

    # Use the real enumerate_entries walker against an injected info dict instead:
    def fake_entries(url):
        out = []
        def walk(node):
            for e in node.get("entries") or []:
                if e.get("entries"): walk(e)
                elif e.get("id"): out.append(e)
        walk(nested)
        return out

    cat = yt.capture("https://www.youtube.com/@JustinSung/shorts", limit=2,
                     info_fetch=lambda u: {"id": yt.video_id_of(u), "title": "Short",
                                           "webpage_url": u, "channel": "JustinSung"},
                     transcript_fetch=lambda vid: "study tip",
                     entries_fetch=fake_entries)
    assert len(cat.items) == 2
    assert all(i.kind == "youtube" for i in cat.items)
```
Remove the unused `_walk`/`nested` monkeypatch line if your linter complains — the operative seam is `entries_fetch=fake_entries`.

- [ ] **Step 2: Run it**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_media_youtube.py::test_capture_shorts_tab_enumerates -q`
Expected: PASS (capture already supports injected `entries_fetch`; this verifies the nested walk shape).

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -q -m "test(youtube): shorts tab enumeration"
```

---

## Task 9: Capture `@JustinSung/shorts` (real run)

**Files:** none (writes `data/media.json`).

- [ ] **Step 1: Capture (start with a small limit to sanity-check)**

Run:
```bash
PYTHONPATH=src .venv/bin/python -m youtube_toolkit.cli capture "https://www.youtube.com/@JustinSung/shorts" --limit 5
```
Expected: prints `captured: …` lines; some shorts may show `[no transcript]`.

- [ ] **Step 2: Inspect what was captured**

Run:
```bash
PYTHONPATH=src .venv/bin/python -c "
from media_core.models import MediaCatalog; from media_core.config import CONTENT_PATH
c=MediaCatalog.model_validate_json(CONTENT_PATH.read_text())
yt=[i for i in c.items if i.kind=='youtube']
print('youtube items:', len(yt))
for i in yt[:5]: print('-', i.title[:50], '| transcript_chars:', len(i.body_markdown), '| topics:', i.topics)
"
```
Expected: items present; transcript_chars > 0 for most; topics populated.

- [ ] **Step 3: Capture the rest (full shorts catalogue)**

Run:
```bash
PYTHONPATH=src .venv/bin/python -m youtube_toolkit.cli capture "https://www.youtube.com/@JustinSung/shorts"
```
Expected: `Done. N new YouTube item(s).`

---

## Task 10: Unified build into "Obsidian Vault" + verify

**Files:** none (writes the live vault).

- [ ] **Step 1: Build the unified vault**

Run:
```bash
PYTHONPATH=src .venv/bin/python -m youtube_toolkit.cli build
```
Expected: `Unified vault written: …/Obsidian Vault (… media items, … topics)`.

- [ ] **Step 2: Verify migration + link integrity (code-fence aware)**

Run:
```bash
PYTHONPATH=src .venv/bin/python -c "
import re, pathlib
r=pathlib.Path.home()/'Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault'
assert not (r/'Substack'/'topics').exists(), 'stale Substack/topics still present'
m=list(r.rglob('*.md')); res={x for f in m for x in (f.relative_to(r).as_posix()[:-3], f.stem)}
broken=[t for f in m for t in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', re.sub(r'\`\`\`.*?\`\`\`','',f.read_text(),flags=re.S)) if t not in res]
print('md files:', len(m), '| broken wikilinks:', len(broken))
k=(r/'topics'/'apache-kafka.md')
if k.exists(): print('kafka sections:', [l for l in k.read_text().splitlines() if l.startswith('## ')])
"
```
Expected: `Substack/topics` gone; `broken wikilinks: 0`; kafka topic note shows Substack + YouTube (+ Web if present) sections.

- [ ] **Step 3: (No commit — vaults are outside the repo / gitignored.)**

---

## Task 11: media-capture skill + agent

**Files:**
- Create: `.claude/skills/media-capture/SKILL.md`
- Create: `.claude/agents/media-capturer.md`

- [ ] **Step 1: Write the skill**

Create `.claude/skills/media-capture/SKILL.md` with frontmatter `name: media-capture`, a description (capture YouTube transcripts + web articles into the unified Obsidian vault), and a body documenting: the `media_core` + `youtube_toolkit` + `web_toolkit` split; CLI usage (`youtube-toolkit capture <url> [--limit]`, `web-toolkit capture <urls>|--file`, `… build`); that channels/playlists/`/shorts` enumerate via yt-dlp and transcripts via youtube-transcript-api (no key); no-caption items are flagged not fabricated; trafilatura for articles; the unified root `topics/` cross-links sources; SOIC lives in the separate Stock Market Vault; dependency/disk gotchas (`uv`/`puppeteer` cache when disk is low).

- [ ] **Step 2: Write the agent**

Create `.claude/agents/media-capturer.md` with frontmatter (`name: media-capturer`, description, `tools: Bash, Read, Edit, Write, Grep, Glob`, `model: sonnet`) and a body mirroring the skill: procedure (resolve URL kind → capture → verify transcript/body sizes → build unified vault → check link integrity), and the same gotchas.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -q -m "feat: media-capture skill + agent"
```

---

## Task 12: Docs + memory + push

**Files:**
- Modify: `README.md`
- Modify: memory files under the project memory dir

- [ ] **Step 1: Update README** — replace the "YouTube & web toolkit" section to describe the new `youtube-toolkit` / `web-toolkit` commands, the unified vault in "Obsidian Vault", and SOIC now in "Stock Market Vault".

- [ ] **Step 2: Update memory** — edit `media-toolkit-youtube-web.md` to reflect the `media_core`/`youtube_toolkit`/`web_toolkit` split, unified vault, and the SOIC → Stock Market Vault move.

- [ ] **Step 3: Full suite + push**

```bash
.venv/bin/python -m pytest -q
git add -A && git commit -q -m "docs: document youtube/web sub-projects + unified vault"
git push origin claude/eager-gates-UqFZF
```
Expected: tests pass; push succeeds.

---

## Self-review notes

- Spec coverage: SOIC move (T1), media_core (T2), youtube_toolkit (T3), web_toolkit (T4), media renderers relocation (T5), unified topics + migration (T6), entry points (T7), shorts (T8), capture (T9), unified build + integrity (T10), skill+agent (T11), docs/push (T12). All spec sections mapped.
- The `build` command is exposed identically on both source CLIs (calls `unified_vault.build_from_disk`) — resolves the spec's "shared build" ambiguity.
- `sed -i ''` is the macOS/BSD form (this repo is on darwin).
