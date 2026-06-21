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
