"""End-to-end integration test for the Substack pipeline.

Exercises the REAL pipeline with no network or auth: an injected fetcher returns
realistic Substack-shaped API JSON, ``crawler.crawl`` writes the cache, and
``vault.build_vault_from_disk`` renders the Obsidian vault. Verifies the headline
cross-channel topic linking, the paywalled-post path, and that every generated
``[[wikilink]]`` resolves to a real note.
"""

from __future__ import annotations

import re

import substack_toolkit.crawler as crawler
from substack_toolkit import vault
from substack_toolkit.models import SubstackCatalog

# --- Realistic fake Substack API across two publications -------------------

_ARCHIVES = {
    "vutr": [
        {"slug": "deep-dive-dbt"},
        {"slug": "airflow-orchestration"},
        {"slug": "members-only-internals"},
    ],
    "datatalks": [
        {"slug": "dbt-in-practice"},
    ],
}

_DETAILS = {
    "deep-dive-dbt": {
        "title": "A deep dive into dbt",
        "subtitle": "Models, tests, and the warehouse",
        "slug": "deep-dive-dbt",
        "canonical_url": "https://vutr.substack.com/p/deep-dive-dbt",
        "post_date": "2025-03-01T08:00:00.000Z",
        "audience": "everyone",
        "publishedBylines": [{"name": "Vu Trinh"}],
        "body_html": "<h2>Why dbt</h2><p>dbt is a <strong>data build tool</strong> "
                     "for the data warehouse.</p>",
    },
    "airflow-orchestration": {
        "title": "Airflow orchestration patterns",
        "subtitle": "DAGs that scale",
        "slug": "airflow-orchestration",
        "canonical_url": "https://vutr.substack.com/p/airflow-orchestration",
        "post_date": "2025-02-01T08:00:00.000Z",
        "audience": "everyone",
        "publishedBylines": [{"name": "Vu Trinh"}],
        "body_html": "<p>Apache Airflow handles orchestration of batch jobs.</p>",
    },
    "members-only-internals": {
        "title": "Members-only engine internals",
        "subtitle": "Subscriber edition",
        "slug": "members-only-internals",
        "canonical_url": "https://vutr.substack.com/p/members-only-internals",
        "post_date": "2025-04-01T08:00:00.000Z",
        "audience": "only_paid",
        "publishedBylines": [{"name": "Vu Trinh"}],
        "body_html": "",  # paywalled: body not accessible with this session
    },
    "dbt-in-practice": {
        "title": "dbt in practice",
        "subtitle": "Lessons from production",
        "slug": "dbt-in-practice",
        "canonical_url": "https://datatalks.substack.com/p/dbt-in-practice",
        "post_date": "2025-03-15T08:00:00.000Z",
        "audience": "everyone",
        "publishedBylines": [{"name": "Data Talks"}],
        "body_html": "<p>Running dbt with Snowflake in production.</p>",
    },
}


def _fake_fetch(url: str):
    if "/api/v1/archive" in url:
        handle = url.split("//", 1)[1].split(".", 1)[0]
        return _ARCHIVES.get(handle, []) if "offset=0" in url else []
    slug = url.rsplit("/", 1)[-1]
    return _DETAILS[slug]


def _all_wikilink_targets(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text)


def test_full_pipeline_crawl_then_build(tmp_path, monkeypatch):
    cache = tmp_path / "substack.json"
    monkeypatch.setattr(crawler, "CONTENT_PATH", cache)
    monkeypatch.setattr(vault, "CONTENT_PATH", cache)
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    # --- Crawl two channels through the REAL crawl() with an injected fetcher.
    crawler.crawl("vutr", fetch=_fake_fetch)
    crawler.crawl("datatalks", fetch=_fake_fetch)

    assert cache.exists()
    catalog = SubstackCatalog.model_validate_json(cache.read_text())
    assert {c.handle for c in catalog.channels} == {"vutr", "datatalks"}
    assert len(catalog.get_channel("vutr").posts) == 3
    assert len(catalog.get_channel("datatalks").posts) == 1

    # Paywalled post captured but marked inaccessible.
    paid = next(p for p in catalog.get_channel("vutr").posts
                if p.slug == "members-only-internals")
    assert paid.is_paid is True
    assert paid.body_accessible is False
    assert paid.body_markdown == ""

    # --- Build the vault from the on-disk cache.
    out = tmp_path / "vault"
    vault.build_vault_from_disk(vault_dir=out)

    written = {p.relative_to(out).as_posix() for p in out.rglob("*.md")}
    assert "posts/vutr/deep-dive-dbt.md" in written
    assert "posts/datatalks/dbt-in-practice.md" in written
    assert "channels/vutr-channel.md" in written
    assert "channels/datatalks-channel.md" in written
    assert "topics/dbt.md" in written
    assert "Home.md" in written

    # --- Headline feature: one shared dbt topic note spanning both channels.
    dbt_note = (out / "topics" / "dbt.md").read_text()
    assert "## vutr" in dbt_note
    assert "## datatalks" in dbt_note
    assert "[[posts/vutr/deep-dive-dbt|A deep dive into dbt]]" in dbt_note
    assert "[[posts/datatalks/dbt-in-practice|dbt in practice]]" in dbt_note

    # --- Paywalled post note shows the inaccessible warning.
    paid_note = (out / "posts" / "vutr" / "members-only-internals.md").read_text()
    assert "[!warning]" in paid_note

    # --- Link integrity: every wikilink target resolves to a generated note
    #     (by full vault-relative path or by bare basename).
    resolvable = set()
    for md in out.rglob("*.md"):
        rel = md.relative_to(out).as_posix()[:-3]
        resolvable.add(rel)
        resolvable.add(md.stem)
    broken = []
    for md in out.rglob("*.md"):
        for target in _all_wikilink_targets(md.read_text()):
            if target not in resolvable:
                broken.append((md.relative_to(out).as_posix(), target))
    assert broken == [], f"broken wikilinks: {broken}"


def test_crawl_is_resumable_across_runs(tmp_path, monkeypatch):
    cache = tmp_path / "substack.json"
    monkeypatch.setattr(crawler, "CONTENT_PATH", cache)
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    crawler.crawl("vutr", fetch=_fake_fetch)
    catalog = crawler.crawl("vutr", fetch=_fake_fetch)  # second run, same data

    # No duplicates: still exactly the three vutr posts.
    assert len(catalog.get_channel("vutr").posts) == 3
