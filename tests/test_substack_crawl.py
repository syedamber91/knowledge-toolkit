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


def test_crawl_free_only_skips_paid_posts(tmp_path, monkeypatch):
    monkeypatch.setattr(crawler, "CONTENT_PATH", tmp_path / "substack.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    archive = [
        {"slug": "free1", "audience": "everyone"},
        {"slug": "paid1", "audience": "only_paid"},
        {"slug": "free2", "audience": "only_free"},
    ]
    details = {
        "free1": {"title": "Free 1", "slug": "free1", "audience": "everyone",
                  "canonical_url": "https://x.substack.com/p/free1",
                  "body_html": "<p>free body</p>"},
        "free2": {"title": "Free 2", "slug": "free2", "audience": "only_free",
                  "canonical_url": "https://x.substack.com/p/free2",
                  "body_html": "<p>free body</p>"},
    }

    fetched_slugs = []

    def fetch(url: str):
        if "/api/v1/archive" in url:
            return archive if "offset=0" in url else []
        slug = url.rsplit("/", 1)[-1]
        fetched_slugs.append(slug)
        return details[slug]  # KeyError if a paid slug is ever fetched

    catalog = crawler.crawl("x", fetch=fetch, free_only=True)

    channel = catalog.get_channel("x")
    assert {p.slug for p in channel.posts} == {"free1", "free2"}
    assert "paid1" not in fetched_slugs  # paid post never even fetched


def test_crawl_continues_when_one_post_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(crawler, "CONTENT_PATH", tmp_path / "substack.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    def flaky_fetch(url: str):
        if "/api/v1/archive" in url:
            return ARCHIVE if "offset=0" in url else []
        if url.endswith("/p1"):
            raise RuntimeError("boom")
        slug = url.rsplit("/", 1)[-1]
        return DETAILS[slug]

    catalog = crawler.crawl("vutr", fetch=flaky_fetch)

    channel = catalog.get_channel("vutr")
    # p1 failed and was skipped; p2 still captured.
    assert {p.slug for p in channel.posts} == {"p2"}
