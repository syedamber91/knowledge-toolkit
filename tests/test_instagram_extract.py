"""Offline tests for instagram_toolkit — no network, no login, no Instaloader.

The crawler's network seam (post_fetch) is injected with plain dicts, and the
extractor is fed normalized post dicts from a saved fixture.
"""

import json
from pathlib import Path

import pytest

import instagram_toolkit.crawler as crawler
from instagram_toolkit.extract import item_from_post
import media_core.store as store
from media_core import unified_vault as vault
from media_core.models import MediaCatalog

FIX = Path(__file__).parent / "fixtures" / "instagram_profile_posts.json"


def _posts():
    return json.loads(FIX.read_text())


# --- extract -----------------------------------------------------------------

def test_item_from_post_maps_reel_fields():
    it = item_from_post(_posts()[0])
    assert it.kind == "instagram"
    assert it.title.startswith("Premium Ajwa dates gift box")
    assert it.url == "https://www.instagram.com/reel/CxAbc123/"
    assert it.source == "premiumdatesco"
    assert it.author == "Premium Dates Co"
    assert it.like_count == 1240 and it.comment_count == 57
    assert it.duration_seconds == 28          # 28.5 -> int
    assert it.published_at.year == 2026 and it.published_at.month == 3
    assert "#dates" in it.keywords and "#ramadan" in it.keywords
    assert "@somepartner" in it.keywords
    assert "reel" in it.keywords
    assert it.body_markdown.startswith("Premium Ajwa")
    assert it.body_accessible is True


def test_item_from_post_empty_caption_falls_back_to_handle_and_date():
    it = item_from_post(_posts()[1])
    assert it.title == "@premiumdatesco · 2026-02-15"
    assert "post" in it.keywords              # not a video
    assert it.duration_seconds is None
    assert it.body_accessible is True


def test_item_from_post_matches_topics_from_caption():
    it = item_from_post({
        "shortcode": "Zz1", "url": "https://www.instagram.com/p/Zz1/",
        "caption": "My productivity routine: time management and deep work.",
        "owner_username": "coach", "taken_at": "2026-01-01T00:00:00+00:00",
        "is_video": False, "likes": 10, "comments": 1,
        "hashtags": ["productivity"], "mentions": [],
    })
    assert "Productivity" in it.topics


# --- _normalize resilience ----------------------------------------------------

def test_normalize_tolerates_failed_lazy_metadata_fields():
    """Some Instaloader Post properties (comments count, video_duration) return
    None from the initial timeline payload and lazily fetch full single-post
    metadata on first access. If that secondary network request fails (e.g.
    Instagram 403s the endpoint for this session), _normalize must still
    return a usable item with those specific fields as None, rather than
    letting the underlying exception crash the whole crawl."""

    class _ExplodingField:
        def __get__(self, obj, objtype=None):
            raise RuntimeError("simulated Instaloader BadResponseException")

    class FakePost:
        shortcode = "ABC123"
        caption = "hello world"
        owner_username = "someone"
        date_utc = "2026-01-01T00:00:00+00:00"
        is_video = True
        caption_hashtags = []
        caption_mentions = []
        likes = 42
        video_duration = _ExplodingField()
        comments = _ExplodingField()

    item = crawler._normalize(FakePost())
    assert item["video_duration"] is None
    assert item["comments"] is None
    assert item["likes"] == 42
    assert item["caption"] == "hello world"


# --- crawler (resumable, polite, block-safe) ---------------------------------

def test_crawl_resumes_and_respects_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)
    posts = _posts()

    cat = crawler.crawl("premiumdatesco", limit=1, post_fetch=lambda h: posts)
    assert len(cat.items) == 1               # limit honored
    assert (tmp_path / "media.json").exists()

    cat2 = crawler.crawl("premiumdatesco", post_fetch=lambda h: posts)
    assert len(cat2.items) == 2              # second one added, first not duplicated
    assert len({i.url for i in cat2.items}) == 2


def test_crawl_hashtag_captures(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)
    cat = crawler.crawl_hashtag("bhopaldates", post_fetch=lambda t: _posts())
    assert len(cat.items) == 2
    assert all(i.kind == "instagram" for i in cat.items)


def test_block_is_reraised_as_friendly_runtimeerror(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    def boom(_target):
        raise RuntimeError("Please wait a few minutes before you try again.")
        yield  # makes this a generator, mirroring a real fetch that blocks mid-stream

    with pytest.raises(RuntimeError) as ei:
        crawler.crawl("someacct", post_fetch=boom)
    assert "resume" in str(ei.value).lower()


def test_non_block_error_propagates_unchanged(tmp_path, monkeypatch):
    """A 'run login first'-style error (contains the word 'login') must NOT be
    relabelled as a rate-limit/block message."""
    monkeypatch.setattr(store, "CONTENT_PATH", tmp_path / "media.json")
    monkeypatch.setattr(crawler.time, "sleep", lambda *a, **k: None)

    def no_session(_target):
        raise RuntimeError(
            "No authenticated Instagram session. Run "
            "`instagram-toolkit login --from-chrome` first (use a burner account)."
        )
        yield

    with pytest.raises(RuntimeError) as ei:
        crawler.crawl("someacct", post_fetch=no_session)
    msg = str(ei.value).lower()
    assert "login" in msg and "burner" in msg          # original guidance preserved
    assert "rate-limited" not in msg and "blocked" not in msg


# --- vault rendering ---------------------------------------------------------

def test_vault_renders_instagram_note(tmp_path):
    cat = MediaCatalog(items=[item_from_post(_posts()[0])])
    out = tmp_path / "vault"
    vault.build_vault(cat, vault_dir=out)

    written = {p.relative_to(out).as_posix() for p in out.rglob("*.md")}
    note_rel = f"instagram/premiumdatesco/{vault._item_basename(cat.items[0])}.md"
    assert note_rel in written
    assert "sources/instagram-premiumdatesco.md" in written

    text = (out / note_rel).read_text()
    assert "## Caption" in text
    assert "Open on Instagram" in text
    assert "1240 likes · 57 comments" in text
    assert "kind: instagram" in text
