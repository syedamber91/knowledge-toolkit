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
