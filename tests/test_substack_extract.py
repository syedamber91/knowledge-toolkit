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


def test_paid_preview_with_nonempty_body_is_not_accessible():
    # Regression: a paywalled PREVIEW has a non-empty body but is gated with
    # hidden=True. bool(body_md) alone would wrongly mark it accessible.
    data = dict(
        API_POST,
        audience="only_paid",
        hidden=True,  # Substack's gated-response marker
        body_html="<p>Intro paragraph then a subscribe call-to-action…</p>",
        truncated_body_text="Join my paid membership…",  # present even when full
    )
    post = post_from_api(data, "vutr")
    assert post.is_paid is True
    assert post.body_accessible is False  # the fix
    assert post.body_markdown  # preview text is still captured


def test_paid_full_body_when_authenticated_is_accessible():
    # Authenticated + entitled: full body, no `hidden` flag.
    data = dict(
        API_POST,
        audience="only_paid",
        body_html="<h2>Full</h2><p>" + ("content " * 200) + "</p>",
    )
    post = post_from_api(data, "vutr")
    assert post.is_paid is True
    assert post.body_accessible is True


def test_free_post_with_truncated_body_text_stays_accessible():
    # truncated_body_text on a FREE post must not be mistaken for a paywall.
    data = dict(API_POST, audience="everyone", truncated_body_text="snippet")
    post = post_from_api(data, "vutr")
    assert post.is_paid is False
    assert post.body_accessible is True


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


def test_post_from_api_handles_missing_and_malformed_bylines():
    no_bylines = {k: v for k, v in API_POST.items() if k != "publishedBylines"}
    assert post_from_api(no_bylines, "vutr").author == ""
    empty_bylines = dict(API_POST, publishedBylines=[])
    assert post_from_api(empty_bylines, "vutr").author == ""
    malformed = dict(API_POST, publishedBylines=["not-a-dict"])
    assert post_from_api(malformed, "vutr").author == ""


def test_parse_date_handles_varied_and_bad_formats():
    # One fractional digit (not 3 or 6) should still parse on Python 3.9.
    one_digit = dict(API_POST, post_date="2025-03-01T08:00:00.5Z")
    assert post_from_api(one_digit, "vutr").published_at.year == 2025
    # No fractional seconds at all.
    no_frac = dict(API_POST, post_date="2025-03-01T08:00:00Z")
    assert post_from_api(no_frac, "vutr").published_at.year == 2025
    # Garbage date -> None (not an exception).
    bad = dict(API_POST, post_date="not-a-date")
    assert post_from_api(bad, "vutr").published_at is None
    # Missing date -> None.
    missing = {k: v for k, v in API_POST.items() if k != "post_date"}
    assert post_from_api(missing, "vutr").published_at is None
