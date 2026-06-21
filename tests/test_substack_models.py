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
