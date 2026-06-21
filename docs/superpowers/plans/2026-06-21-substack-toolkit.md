# Substack Toolkit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `substack_toolkit` package that captures free + paywalled posts from a subscribed Substack publication (starting with vutr) into a dedicated Obsidian vault, with cross-channel topic linking via a shared canonical topic vocabulary.

**Architecture:** A sibling package to `soic_toolkit` in the same repo, mirroring its `config → models → topics → extract → auth/crawler → vault → cli` pipeline. The crawler uses the user's saved session cookie against Substack's JSON API (stdlib `urllib`). Topic detection is purely lexical (vocabulary matching + keyword frequency) — no AI. The same canonical topic vocabulary is matched by every channel so identical topics resolve to one shared Obsidian note.

**Tech Stack:** Python 3.9, Pydantic v2, Typer, Rich, Playwright (login only), `markdownify` (HTML→Markdown), stdlib `urllib` (HTTP API), pytest.

**Spec:** `docs/superpowers/specs/2026-06-21-substack-toolkit-design.md`

---

## File Structure

```
src/substack_toolkit/
  __init__.py    # empty package marker
  config.py      # SUBSTACK_* env + paths + ensure_dirs + channel_url
  models.py      # Post, Channel, SubstackCatalog (Pydantic)
  topics.py      # TOPIC_VOCABULARY, match_topics(), keywords()  [cross-channel seam]
  extract.py     # post_from_api(), enrich()  (API JSON -> Post, HTML -> Markdown)
  auth.py        # has_saved_session(), login()  (Playwright interactive)
  crawler.py     # crawl()  (HTTP API, resumable, polite); injectable fetcher
  vault.py       # build_vault(), build_vault_from_disk()  (Obsidian output)
  cli.py         # typer app: login | crawl | build-vault | list-topics

tests/
  test_substack_topics.py
  test_substack_extract.py
  test_substack_vault.py
  test_substack_crawl.py

pyproject.toml   # add markdownify dep + substack-toolkit script
```

Each test imports from the installed `substack_toolkit` package (the repo is installed editable; `tool.setuptools.packages.find where=["src"]` auto-discovers the new package).

---

## Task 1: Scaffold package, config, and packaging

**Files:**
- Create: `src/substack_toolkit/__init__.py`
- Create: `src/substack_toolkit/config.py`
- Modify: `pyproject.toml` (add `markdownify` dependency + `substack-toolkit` script)

- [ ] **Step 1: Create the empty package marker**

Create `src/substack_toolkit/__init__.py`:

```python
"""Personal Substack archiver: capture subscribed posts into an Obsidian vault."""
```

- [ ] **Step 2: Create `config.py`**

Create `src/substack_toolkit/config.py`:

```python
"""Configuration and filesystem paths for the Substack toolkit.

Values come from the local ``.env`` (shared with the rest of the repo) with
sensible defaults. Nothing here contains secrets: login is interactive and the
resulting session cookie is stored separately under ``.auth/``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root is two levels up: src/substack_toolkit/config.py -> repo root
ROOT_DIR = Path(__file__).resolve().parents[2]

AUTH_DIR = ROOT_DIR / ".auth"
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

# Dedicated Substack-only Obsidian vault. Point SUBSTACK_VAULT_DIR at a folder
# inside your real Obsidian vault to have notes show up directly in Obsidian.
VAULT_DIR = Path(
    os.environ.get("SUBSTACK_VAULT_DIR", "~/Documents/Obsidian Vault/Substack")
).expanduser()

STATE_PATH = AUTH_DIR / "substack_state.json"
CONTENT_PATH = DATA_DIR / "substack.json"


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _get_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    crawl_min_delay: float = _get_float("SUBSTACK_CRAWL_MIN_DELAY", 1.5)
    crawl_max_delay: float = _get_float("SUBSTACK_CRAWL_MAX_DELAY", 3.5)
    crawl_headed: bool = _get_bool("SUBSTACK_CRAWL_HEADED", True)


settings = Settings()


def channel_url(handle: str) -> str:
    """Base URL for a publication handle, e.g. 'vutr' -> https://vutr.substack.com."""
    return f"https://{handle}.substack.com"


def ensure_dirs() -> None:
    """Create the local working directories if they don't already exist."""
    for d in (AUTH_DIR, DATA_DIR, OUTPUT_DIR, VAULT_DIR):
        d.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 3: Add the `markdownify` dependency and console script to `pyproject.toml`**

In `pyproject.toml`, add `"markdownify>=0.11"` to the `dependencies` list (after `"lxml>=4.9",`):

```toml
dependencies = [
    "playwright>=1.40",
    "pydantic>=2.5",
    "python-dotenv>=1.0",
    "beautifulsoup4>=4.12",
    "lxml>=4.9",
    "markdownify>=0.11",
    "typer>=0.9",
    "rich>=13.0",
]
```

And add a second console script under `[project.scripts]`:

```toml
[project.scripts]
soic-toolkit = "soic_toolkit.cli:app"
substack-toolkit = "substack_toolkit.cli:app"
```

- [ ] **Step 4: Install the new dependency and re-install the package editable**

Run: `.venv/bin/pip install markdownify && .venv/bin/pip install -e .`
Expected: installs `markdownify` and re-registers the package so `substack_toolkit` imports and the `substack-toolkit` script resolve.

- [ ] **Step 5: Verify the package imports**

Run: `.venv/bin/python -c "import substack_toolkit.config as c; print(c.channel_url('vutr')); print(c.CONTENT_PATH.name)"`
Expected output:
```
https://vutr.substack.com
substack.json
```

- [ ] **Step 6: Commit**

```bash
git add src/substack_toolkit/__init__.py src/substack_toolkit/config.py pyproject.toml
git commit -m "feat(substack): scaffold package, config, and packaging"
```

---

## Task 2: Data models

**Files:**
- Create: `src/substack_toolkit/models.py`
- Test: `tests/test_substack_extract.py` (model construction is exercised via extract tests in Task 4; this task adds a tiny direct model test)

- [ ] **Step 1: Write the failing test**

Create `tests/test_substack_models.py`:

```python
from datetime import datetime, timezone

from substack_toolkit.models import Channel, Post, SubstackCatalog


def _post(slug: str) -> Post:
    return Post(
        title=f"Post {slug}",
        slug=slug,
        url=f"https://vutr.substack.com/p/{slug}",
        published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )


def test_catalog_post_urls_and_get_channel():
    catalog = SubstackCatalog(
        channels=[
            Channel(handle="vutr", url="https://vutr.substack.com",
                    posts=[_post("a"), _post("b")]),
        ]
    )
    assert catalog.post_urls() == {
        "https://vutr.substack.com/p/a",
        "https://vutr.substack.com/p/b",
    }
    assert catalog.get_channel("vutr").handle == "vutr"
    assert catalog.get_channel("missing") is None


def test_post_defaults():
    post = _post("x")
    assert post.is_paid is False
    assert post.body_accessible is True
    assert post.topics == []
    assert post.keywords == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_substack_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'substack_toolkit.models'`

- [ ] **Step 3: Write `models.py`**

Create `src/substack_toolkit/models.py`:

```python
"""Pydantic models describing captured Substack content.

A Channel (one publication) contains Posts. Only legitimately rendered text is
stored — never media files. The shape is intentionally flat (Channel -> Post)
because Substack publications are flat lists of posts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class Post(BaseModel):
    title: str
    subtitle: str = ""
    slug: str
    url: str
    author: str = ""
    published_at: Optional[datetime] = None
    # True when the post is marked subscriber-only / paid.
    is_paid: bool = False
    # True when the body text was actually captured (False = paywalled, no access).
    body_accessible: bool = True
    # Post body rendered to Markdown.
    body_markdown: str = ""
    # Canonical topics matched from the shared vocabulary (cross-channel links).
    topics: List[str] = Field(default_factory=list)
    # Secondary auto-extracted keyword tags.
    keywords: List[str] = Field(default_factory=list)
    captured_at: Optional[datetime] = None


class Channel(BaseModel):
    handle: str            # e.g. "vutr"
    name: str = ""         # display name, if known
    url: str               # e.g. https://vutr.substack.com
    posts: List[Post] = Field(default_factory=list)


class SubstackCatalog(BaseModel):
    """Top-level container persisted to data/substack.json."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    channels: List[Channel] = Field(default_factory=list)

    def post_urls(self) -> set[str]:
        """All captured post URLs — used to make crawls resumable."""
        urls: set[str] = set()
        for channel in self.channels:
            for post in channel.posts:
                urls.add(post.url)
        return urls

    def get_channel(self, handle: str) -> Optional[Channel]:
        for channel in self.channels:
            if channel.handle == handle:
                return channel
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_substack_models.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/substack_toolkit/models.py tests/test_substack_models.py
git commit -m "feat(substack): add Post/Channel/SubstackCatalog models"
```

---

## Task 3: Topic vocabulary and matcher (cross-channel seam)

**Files:**
- Create: `src/substack_toolkit/topics.py`
- Test: `tests/test_substack_topics.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_substack_topics.py`:

```python
from substack_toolkit.topics import keywords, match_topics


def test_match_topics_aliases_and_canonical():
    text = "We used dbt and Airflow to populate the data warehouse."
    topics = match_topics(text)
    assert "dbt" in topics
    assert "Apache Airflow" in topics
    assert "Data Warehouse" in topics


def test_match_topics_is_case_insensitive():
    assert "dbt" in match_topics("DBT is great")


def test_match_topics_whole_word_only():
    # "dbt" embedded inside another token must not match.
    assert "dbt" not in match_topics("the adbtx library")


def test_match_topics_dedupes_repeated_aliases():
    topics = match_topics("Spark spark PySpark everywhere")
    assert topics.count("Apache Spark") == 1


def test_match_topics_empty():
    assert match_topics("") == []


def test_keywords_returns_most_frequent_terms():
    text = "pipeline pipeline pipeline ingestion ingestion lineage"
    kw = keywords(text, limit=2)
    assert kw[0] == "pipeline"
    assert "ingestion" in kw
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_substack_topics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'substack_toolkit.topics'`

- [ ] **Step 3: Write `topics.py`**

Create `src/substack_toolkit/topics.py`:

```python
"""Canonical topic vocabulary and lexical matchers.

This module is the cross-channel linking seam: every channel matches its posts
against the SAME canonical vocabulary, so identical topics (e.g. "dbt") collapse
to one shared Obsidian topic note regardless of which publication they came from.

Extend ``TOPIC_VOCABULARY`` to recognise more topics; re-running the vault build
re-links every post against the updated vocabulary.
"""

from __future__ import annotations

import re
from collections import Counter

# Canonical topic name -> alias phrases (matched case-insensitively, whole-word).
TOPIC_VOCABULARY: dict[str, list[str]] = {
    "Data Engineering": ["data engineering"],
    "dbt": ["dbt", "data build tool"],
    "Apache Airflow": ["airflow"],
    "Apache Kafka": ["kafka"],
    "Apache Spark": ["spark", "pyspark"],
    "Apache Iceberg": ["iceberg"],
    "Apache Flink": ["flink"],
    "Snowflake": ["snowflake"],
    "Databricks": ["databricks"],
    "Delta Lake": ["delta lake"],
    "BigQuery": ["bigquery"],
    "Data Modeling": ["data modeling", "data modelling", "dimensional model"],
    "Data Warehouse": ["data warehouse"],
    "Data Lake": ["data lake"],
    "Lakehouse": ["lakehouse"],
    "Orchestration": ["orchestration"],
    "Streaming": ["streaming", "stream processing"],
    "Batch Processing": ["batch processing"],
    "Change Data Capture": ["change data capture", "cdc"],
    "Data Quality": ["data quality"],
    "Data Governance": ["data governance"],
    "ETL": ["etl", "elt"],
}

# Precompiled whole-word, case-insensitive patterns per alias.
_COMPILED: dict[str, list[re.Pattern]] = {
    canon: [re.compile(r"\b" + re.escape(alias) + r"\b", re.IGNORECASE)
            for alias in aliases]
    for canon, aliases in TOPIC_VOCABULARY.items()
}

_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "you", "are",
    "was", "but", "not", "all", "can", "has", "have", "will", "what", "how",
    "why", "when", "which", "into", "out", "about", "their", "them", "its",
    "our", "more", "less", "than", "then", "also", "such", "may", "one", "two",
    "use", "using", "used", "based", "part", "post", "article", "data",
}
_WORD_RE = re.compile(r"[a-z][a-z0-9]{3,}")


def match_topics(text: str) -> list[str]:
    """Return canonical topics found in ``text`` (deduped, vocabulary order)."""
    if not text:
        return []
    found: list[str] = []
    for canon, patterns in _COMPILED.items():
        if any(p.search(text) for p in patterns):
            found.append(canon)
    return found


def keywords(text: str, limit: int = 6) -> list[str]:
    """Return the most frequent non-stopword terms in ``text`` (secondary tags)."""
    if not text:
        return []
    words = [w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS]
    return [w for w, _ in Counter(words).most_common(limit)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_substack_topics.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add src/substack_toolkit/topics.py tests/test_substack_topics.py
git commit -m "feat(substack): add canonical topic vocabulary and matchers"
```

---

## Task 4: Extraction (API JSON -> Post, HTML -> Markdown)

**Files:**
- Create: `src/substack_toolkit/extract.py`
- Test: `tests/test_substack_extract.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_substack_extract.py`:

```python
from substack_toolkit.extract import enrich, post_from_api

API_POST = {
    "title": "A deep dive into dbt",
    "subtitle": "How dbt builds the warehouse",
    "slug": "a-deep-dive-into-dbt",
    "canonical_url": "https://vutr.substack.com/p/a-deep-dive-into-dbt",
    "post_date": "2025-03-01T08:00:00.000Z",
    "audience": "everyone",
    "publishedBylines": [{"name": "Vu Trinh"}],
    "body_html": "<h2>Intro</h2><p>dbt is a <strong>data build tool</strong> "
                 "for the data warehouse.</p>",
}


def test_post_from_api_maps_fields_and_converts_markdown():
    post = post_from_api(API_POST, "vutr")
    assert post.title == "A deep dive into dbt"
    assert post.subtitle == "How dbt builds the warehouse"
    assert post.slug == "a-deep-dive-into-dbt"
    assert post.url == "https://vutr.substack.com/p/a-deep-dive-into-dbt"
    assert post.author == "Vu Trinh"
    assert post.published_at is not None and post.published_at.year == 2025
    assert post.is_paid is False
    assert post.body_accessible is True
    assert "## Intro" in post.body_markdown
    assert "**data build tool**" in post.body_markdown


def test_post_from_api_paid_without_body():
    data = dict(API_POST, audience="only_paid", body_html="")
    post = post_from_api(data, "vutr")
    assert post.is_paid is True
    assert post.body_accessible is False
    assert post.body_markdown == ""


def test_post_from_api_builds_url_when_canonical_missing():
    data = dict(API_POST)
    del data["canonical_url"]
    post = post_from_api(data, "vutr")
    assert post.url == "https://vutr.substack.com/p/a-deep-dive-into-dbt"


def test_enrich_attaches_topics_and_keywords():
    post = enrich(post_from_api(API_POST, "vutr"))
    assert "dbt" in post.topics
    assert "Data Warehouse" in post.topics
    assert isinstance(post.keywords, list)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_substack_extract.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'substack_toolkit.extract'`

- [ ] **Step 3: Write `extract.py`**

Create `src/substack_toolkit/extract.py`:

```python
"""Convert Substack API JSON into Post models and enrich with topics.

Body HTML is converted to Markdown with ``markdownify`` so code blocks, headings,
lists and links survive. Only text the API returns is stored; media is left as
Markdown links, never downloaded.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from markdownify import markdownify as html_to_md

from .config import channel_url
from .models import Post
from .topics import keywords, match_topics

# Substack "audience" values that mean freely available to everyone.
_FREE_AUDIENCES = {"", "everyone", "only_free"}


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _author(data: dict[str, Any]) -> str:
    bylines = data.get("publishedBylines") or []
    if bylines and isinstance(bylines[0], dict):
        return bylines[0].get("name", "") or ""
    return ""


def post_from_api(data: dict[str, Any], handle: str) -> Post:
    """Build a Post from one Substack ``/api/v1/posts/<slug>`` JSON object."""
    body_html = data.get("body_html") or ""
    body_md = (
        html_to_md(body_html, heading_style="ATX", strip=["script", "style"]).strip()
        if body_html
        else ""
    )
    slug = data.get("slug", "") or ""
    url = data.get("canonical_url") or f"{channel_url(handle)}/p/{slug}"
    audience = data.get("audience", "") or ""
    is_paid = audience not in _FREE_AUDIENCES
    return Post(
        title=data.get("title") or "(untitled)",
        subtitle=data.get("subtitle") or "",
        slug=slug,
        url=url,
        author=_author(data),
        published_at=_parse_date(data.get("post_date")),
        is_paid=is_paid,
        body_accessible=bool(body_md),
        body_markdown=body_md,
        captured_at=datetime.now(timezone.utc),
    )


def enrich(post: Post) -> Post:
    """Attach canonical topics and secondary keyword tags to a Post."""
    text = f"{post.title}\n{post.subtitle}\n{post.body_markdown}"
    post.topics = match_topics(text)
    post.keywords = keywords(text)
    return post
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_substack_extract.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/substack_toolkit/extract.py tests/test_substack_extract.py
git commit -m "feat(substack): API JSON -> Post extraction with HTML->Markdown"
```

---

## Task 5: Auth + resumable crawler

**Files:**
- Create: `src/substack_toolkit/auth.py`
- Create: `src/substack_toolkit/crawler.py`
- Test: `tests/test_substack_crawl.py`

- [ ] **Step 1: Write `auth.py` (no unit test for the interactive browser flow)**

Create `src/substack_toolkit/auth.py`:

```python
"""Interactive login: capture the user's Substack session cookie.

The password is never read or stored — the user logs in manually in a real
browser and we persist only the resulting storage state (cookies) under
``.auth/substack_state.json``.
"""

from __future__ import annotations

from rich.console import Console

from .config import AUTH_DIR, STATE_PATH, channel_url

console = Console()


def has_saved_session() -> bool:
    return STATE_PATH.exists()


def login(handle: str) -> None:
    """Open a browser to the publication, wait for manual login, save cookies."""
    from playwright.sync_api import sync_playwright

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    url = channel_url(handle)
    console.print(f"Opening [bold]{url}[/bold] — log in, then return here.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        input("Press Enter once you are logged in… ")
        context.storage_state(path=str(STATE_PATH))
        browser.close()
    console.print(f"[green]Session saved:[/green] {STATE_PATH}")
```

- [ ] **Step 2: Write the failing crawler test**

Create `tests/test_substack_crawl.py`:

```python
import substack_toolkit.crawler as crawler

ARCHIVE = [{"slug": "p1"}, {"slug": "p2"}]
DETAILS = {
    "p1": {
        "title": "Post 1", "slug": "p1",
        "canonical_url": "https://vutr.substack.com/p/p1",
        "audience": "everyone", "post_date": "2025-01-01T00:00:00.000Z",
        "body_html": "<p>dbt pipeline</p>",
    },
    "p2": {
        "title": "Post 2", "slug": "p2",
        "canonical_url": "https://vutr.substack.com/p/p2",
        "audience": "everyone", "post_date": "2025-02-01T00:00:00.000Z",
        "body_html": "<p>airflow orchestration</p>",
    },
}


def _fake_fetch(url: str):
    if "/api/v1/archive" in url:
        return ARCHIVE if "offset=0" in url else []
    slug = url.rsplit("/", 1)[-1]
    return DETAILS[slug]


def test_crawl_captures_new_posts(tmp_path, monkeypatch):
    monkeypatch.setattr(crawler, "CONTENT_PATH", tmp_path / "substack.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    catalog = crawler.crawl("vutr", fetch=_fake_fetch)

    channel = catalog.get_channel("vutr")
    assert {p.slug for p in channel.posts} == {"p1", "p2"}
    assert "dbt" in channel.posts[0].topics
    assert (tmp_path / "substack.json").exists()


def test_crawl_skips_already_captured(tmp_path, monkeypatch):
    monkeypatch.setattr(crawler, "CONTENT_PATH", tmp_path / "substack.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    crawler.crawl("vutr", fetch=_fake_fetch)
    catalog = crawler.crawl("vutr", fetch=_fake_fetch)  # second run, same data

    channel = catalog.get_channel("vutr")
    assert len(channel.posts) == 2  # no duplicates


def test_crawl_respects_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(crawler, "CONTENT_PATH", tmp_path / "substack.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    catalog = crawler.crawl("vutr", limit=1, fetch=_fake_fetch)

    channel = catalog.get_channel("vutr")
    assert len(channel.posts) == 1
```

- [ ] **Step 3: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_substack_crawl.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'substack_toolkit.crawler'`

- [ ] **Step 4: Write `crawler.py`**

Create `src/substack_toolkit/crawler.py`:

```python
"""Resumable Substack crawler over the publication JSON API.

The user's saved session cookie (from ``auth.login``) is sent with each request
so paid posts return their body. The HTTP fetcher is injectable so the crawl
logic is unit-testable without network access. The cache is written incrementally
so an interrupted crawl never loses captured posts.
"""

from __future__ import annotations

import json
import random
import time
import urllib.request
from typing import Callable, Optional

from rich.console import Console

from .config import CONTENT_PATH, STATE_PATH, channel_url, settings
from .extract import enrich, post_from_api
from .models import Channel, SubstackCatalog

console = Console()

# A fetcher takes a URL and returns parsed JSON (a list or dict).
Fetcher = Callable[[str], object]

_ARCHIVE_PAGE = 12


def _load_cookie_header() -> str:
    if not STATE_PATH.exists():
        raise RuntimeError(
            "No saved session. Run `substack-toolkit login --handle <handle>` first."
        )
    state = json.loads(STATE_PATH.read_text())
    pairs = [f"{c['name']}={c['value']}" for c in state.get("cookies", [])]
    return "; ".join(pairs)


def _default_fetcher(cookie_header: str) -> Fetcher:
    def fetch(url: str):
        req = urllib.request.Request(
            url,
            headers={
                "Cookie": cookie_header,
                "User-Agent": "Mozilla/5.0 (personal-knowledge-archive)",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    return fetch


def _load_catalog() -> SubstackCatalog:
    if CONTENT_PATH.exists():
        return SubstackCatalog.model_validate_json(CONTENT_PATH.read_text())
    return SubstackCatalog()


def _save_catalog(catalog: SubstackCatalog) -> None:
    CONTENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTENT_PATH.write_text(catalog.model_dump_json(indent=2))


def list_post_slugs(fetch: Fetcher, handle: str, limit: Optional[int]) -> list[str]:
    """Enumerate post slugs newest-first by paging the archive endpoint."""
    base = channel_url(handle)
    slugs: list[str] = []
    offset = 0
    while True:
        items = fetch(f"{base}/api/v1/archive?sort=new&limit={_ARCHIVE_PAGE}&offset={offset}")
        if not items:
            break
        for item in items:
            slug = item.get("slug")
            if slug:
                slugs.append(slug)
        if limit and len(slugs) >= limit:
            return slugs[:limit]
        offset += _ARCHIVE_PAGE
    return slugs


def crawl(
    handle: str,
    limit: Optional[int] = None,
    fetch: Optional[Fetcher] = None,
) -> SubstackCatalog:
    """Capture new posts for ``handle`` into the cache (resumable)."""
    if fetch is None:
        fetch = _default_fetcher(_load_cookie_header())

    catalog = _load_catalog()
    channel = catalog.get_channel(handle)
    if channel is None:
        channel = Channel(handle=handle, url=channel_url(handle))
        catalog.channels.append(channel)
    existing = {p.url for p in channel.posts}

    slugs = list_post_slugs(fetch, handle, limit)
    new_count = 0
    for slug in slugs:
        url_guess = f"{channel_url(handle)}/p/{slug}"
        if url_guess in existing:
            continue
        detail = fetch(f"{channel_url(handle)}/api/v1/posts/{slug}")
        post = enrich(post_from_api(detail, handle))
        if post.url in existing:
            continue
        channel.posts.append(post)
        existing.add(post.url)
        new_count += 1
        _save_catalog(catalog)  # incremental — survive interruption
        flag = " [paid]" if post.is_paid and not post.body_accessible else ""
        console.print(f"  captured: {post.title}{flag}")
        time.sleep(random.uniform(settings.crawl_min_delay, settings.crawl_max_delay))

    _save_catalog(catalog)
    console.print(f"[green]Done.[/green] {new_count} new post(s) for {handle}.")
    return catalog
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_substack_crawl.py -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add src/substack_toolkit/auth.py src/substack_toolkit/crawler.py tests/test_substack_crawl.py
git commit -m "feat(substack): interactive login + resumable API crawler"
```

---

## Task 6: Vault builder (post notes, channel MOC, cross-channel topic notes, Home)

**Files:**
- Create: `src/substack_toolkit/vault.py`
- Test: `tests/test_substack_vault.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_substack_vault.py`:

```python
from datetime import datetime, timezone

from substack_toolkit import vault
from substack_toolkit.models import Channel, Post, SubstackCatalog


def _post(title, slug, topics, handle):
    return Post(
        title=title,
        slug=slug,
        url=f"https://{handle}.substack.com/p/{slug}",
        published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        body_markdown="Some body text.",
        topics=topics,
        keywords=["pipeline"],
    )


def _catalog():
    return SubstackCatalog(
        channels=[
            Channel(handle="vutr", url="https://vutr.substack.com", posts=[
                _post("dbt deep dive", "dbt-deep-dive", ["dbt", "Data Warehouse"], "vutr"),
            ]),
            Channel(handle="other", url="https://other.substack.com", posts=[
                _post("dbt at scale", "dbt-at-scale", ["dbt"], "other"),
            ]),
        ]
    )


def test_build_vault_writes_posts_channels_topics_home(tmp_path):
    vault.build_vault(_catalog(), vault_dir=tmp_path)
    files = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*.md")}
    assert "posts/vutr/dbt-deep-dive.md" in files
    assert "posts/other/dbt-at-scale.md" in files
    assert "channels/vutr-channel.md" in files
    assert "topics/dbt.md" in files
    assert "topics/data-warehouse.md" in files
    assert "Home.md" in files


def test_topic_note_aggregates_across_channels(tmp_path):
    vault.build_vault(_catalog(), vault_dir=tmp_path)
    dbt_note = (tmp_path / "topics" / "dbt.md").read_text()
    assert "## vutr" in dbt_note
    assert "## other" in dbt_note
    assert "[[dbt-deep-dive|dbt deep dive]]" in dbt_note
    assert "[[dbt-at-scale|dbt at scale]]" in dbt_note


def test_post_note_frontmatter_and_links(tmp_path):
    vault.build_vault(_catalog(), vault_dir=tmp_path)
    note = (tmp_path / "posts" / "vutr" / "dbt-deep-dive.md").read_text()
    assert note.startswith("---")
    assert 'title: "dbt deep dive"' in note
    assert "url: https://vutr.substack.com/p/dbt-deep-dive" in note
    assert "channel: vutr" in note
    # Topic wikilink in body, channel MOC backlink.
    assert "[[dbt|dbt]]" in note
    assert "[[vutr-channel|vutr]]" in note
    assert "Some body text." in note


def test_build_vault_from_disk_errors_without_cache(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(vault, "CONTENT_PATH", tmp_path / "missing.json")
    with pytest.raises(RuntimeError):
        vault.build_vault_from_disk()


def test_slugify():
    assert vault.slugify("Apache Airflow") == "apache-airflow"
    assert vault.slugify("dbt!") == "dbt"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_substack_vault.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'substack_toolkit.vault'`

- [ ] **Step 3: Write `vault.py`**

Create `src/substack_toolkit/vault.py`:

```python
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
    return '"' + value.replace('"', "'") + '"'


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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_substack_vault.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/substack_toolkit/vault.py tests/test_substack_vault.py
git commit -m "feat(substack): Obsidian vault builder with cross-channel topic notes"
```

---

## Task 7: CLI wiring

**Files:**
- Create: `src/substack_toolkit/cli.py`
- Test: manual smoke (the typer app is thin glue over already-tested modules)

- [ ] **Step 1: Write `cli.py`**

Create `src/substack_toolkit/cli.py`:

```python
"""Command-line interface for the Substack toolkit.

Subcommands:
    login        Open a browser and save your Substack session cookie.
    crawl        Capture posts for a publication into data/substack.json.
    build-vault  Build the Obsidian vault from captured posts.
    list-topics  Show the topic vocabulary and per-topic post counts.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from . import auth as auth_mod
from . import vault as vault_mod
from .config import CONTENT_PATH

app = typer.Typer(
    help="Personal Substack archiver for your own subscriptions -> Obsidian.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def login(
    handle: str = typer.Option(..., "--handle", help="Publication handle, e.g. vutr.")
) -> None:
    """Open a browser, log in manually, and save the session cookie."""
    auth_mod.login(handle)


@app.command()
def crawl(
    handle: str = typer.Argument(..., help="Publication handle, e.g. vutr."),
    limit: Optional[int] = typer.Option(
        None, help="Stop after capturing this many new posts (useful for a first test)."
    ),
) -> None:
    """Capture accessible post text into data/substack.json (resumable)."""
    from . import crawler as crawler_mod

    console.print(f"[bold]Crawling[/bold] {handle} (accessible text only — no media).")
    try:
        crawler_mod.crawl(handle, limit=limit)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("build-vault")
def build_vault(
    vault_path: Optional[str] = typer.Option(
        None, "--vault-path",
        help="Folder to write notes into. Overrides SUBSTACK_VAULT_DIR.",
    )
) -> None:
    """Build the Substack Obsidian vault (one linked note per post)."""
    try:
        vault_mod.build_vault_from_disk(vault_dir=vault_path)
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(code=1)


@app.command("list-topics")
def list_topics() -> None:
    """Print the topic vocabulary and per-topic captured post counts."""
    from .models import SubstackCatalog
    from .topics import TOPIC_VOCABULARY

    counts: dict[str, int] = {}
    if CONTENT_PATH.exists():
        catalog = SubstackCatalog.model_validate_json(CONTENT_PATH.read_text())
        for channel in catalog.channels:
            for post in channel.posts:
                for topic in post.topics:
                    counts[topic] = counts.get(topic, 0) + 1
    for topic in TOPIC_VOCABULARY:
        console.print(f"{topic:24} {counts.get(topic, 0)}")


if __name__ == "__main__":
    app()
```

- [ ] **Step 2: Verify the CLI loads and shows help**

Run: `.venv/bin/substack-toolkit --help`
Expected: help text listing `login`, `crawl`, `build-vault`, `list-topics`.

- [ ] **Step 3: Verify `list-topics` runs without a cache**

Run: `.venv/bin/substack-toolkit list-topics`
Expected: the vocabulary printed with `0` counts (no cache yet).

- [ ] **Step 4: Run the full test suite**

Run: `.venv/bin/python -m pytest tests/test_substack_models.py tests/test_substack_topics.py tests/test_substack_extract.py tests/test_substack_crawl.py tests/test_substack_vault.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/substack_toolkit/cli.py
git commit -m "feat(substack): CLI (login, crawl, build-vault, list-topics)"
```

---

## Task 8: End-to-end smoke + docs

**Files:**
- Modify: `.env.example` (document `SUBSTACK_*` variables)
- Modify: `README.md` (add a short Substack section)

- [ ] **Step 1: Document env vars in `.env.example`**

Append to `.env.example`:

```
# --- Substack toolkit ---
# Dedicated Obsidian vault for Substack channels.
SUBSTACK_VAULT_DIR="~/Documents/Obsidian Vault/Substack"
# Politeness delays between API requests (seconds).
SUBSTACK_CRAWL_MIN_DELAY=1.5
SUBSTACK_CRAWL_MAX_DELAY=3.5
# Show the browser during `substack-toolkit login`.
SUBSTACK_CRAWL_HEADED=true
```

- [ ] **Step 2: Add a Substack section to `README.md`**

Add near the existing usage section:

```markdown
## Substack toolkit

Capture posts from a Substack publication you subscribe to into a dedicated
Obsidian vault, with cross-channel topic linking.

```bash
substack-toolkit login --handle vutr     # one-time: log in, session saved
substack-toolkit crawl vutr --limit 5    # capture a few posts to start
substack-toolkit build-vault             # write the Obsidian vault
substack-toolkit list-topics             # see topic coverage
```

Personal use of your own subscription only. Only text the authenticated page
renders is captured — no media is downloaded. Your password is never stored;
only the session cookie is saved under `.auth/` (gitignored).
```

- [ ] **Step 3: Live smoke test (manual, requires the user)**

Run:
```bash
.venv/bin/substack-toolkit login --handle vutr
.venv/bin/substack-toolkit crawl vutr --limit 3
.venv/bin/substack-toolkit build-vault
```
Expected: 3 posts captured into `data/substack.json`; vault written to
`~/Documents/Obsidian Vault/Substack` with `posts/vutr/*.md`, `channels/vutr-channel.md`,
`topics/*.md`, and `Home.md`. Open in Obsidian and confirm topic notes link posts.

> NOTE: This step needs the user's logged-in session and makes live requests.
> Pause for the user to run it / confirm before relying on live data.

- [ ] **Step 4: Commit**

```bash
git add .env.example README.md
git commit -m "docs(substack): document env vars and usage"
```

---

## Self-Review Notes

- **Spec coverage:** login/auth (Task 5), API crawl + resumability (Task 5), HTML→Markdown extract + paid/free flags (Task 4), canonical topic vocabulary + matching (Task 3), shared cross-channel topic notes (Task 6, explicitly tested), channel MOC + Home (Task 6), separate vault path via `SUBSTACK_VAULT_DIR` (Task 1/6), CLI (Task 7), guardrails reflected in auth/crawler behavior + docs (Task 5/8). All spec sections map to a task.
- **Dependency decision:** Spec listed `requests` vs `urllib` as open; chose stdlib `urllib` (verified Python 3.9.6 has working `fromisoformat` for Substack dates after `Z`→offset swap), so the only new dependency is `markdownify`.
- **Type consistency:** `Post`, `Channel`, `SubstackCatalog` fields and methods (`post_urls`, `get_channel`) are used consistently across crawler/vault/cli. Topic note filenames and post wikilinks both use `slugify(...)` so links resolve. `channel_moc` name (`<handle>-channel`) is generated by the single `_channel_moc_name` helper and referenced identically in post notes, channel MOC, and Home.
- **No placeholders:** every code step contains complete, runnable code.
