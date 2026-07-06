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
    assert "[[Substack/posts/vutr/why-kafka|Why Kafka]]" in kafka

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


# --- ingestion log (index + log + cross-links routing pattern) ---------------

def test_log_created_on_first_build_backfills_without_claiming_new(tmp_path):
    out = tmp_path / "Obsidian Vault"
    uv.build_unified(_media(), _substack(), vault_dir=out)

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 1        # exactly one entry
    # First-ever entry backfills pre-existing content — must not claim it was
    # "just captured" when it wasn't.
    assert "3 item(s) already in vault (log started here) (3 total: 1 YouTube, 1 web, 0 Instagram, 1 Substack)" in log
    assert "[[Log|Ingestion Log]]" in (out / "Home.md").read_text()


def test_log_appends_new_entry_when_items_added(tmp_path):
    out = tmp_path / "Obsidian Vault"
    uv.build_unified(_media(), _substack(), vault_dir=out)

    grown = _media()
    grown.items.append(MediaItem(
        kind=KIND_YOUTUBE, title="Kafka part 2",
        url="https://www.youtube.com/watch?v=aaaaaaaaaaa",
        source="JustinSung", source_id="UCx",
        body_markdown="kafka 2", topics=["Apache Kafka"], keywords=["kafka"]))
    uv.build_unified(grown, _substack(), vault_dir=out)

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 2        # first entry preserved, second appended
    assert "1 new item(s) captured (4 total: 2 YouTube, 1 web, 0 Instagram, 1 Substack)" in log


def test_log_skips_entry_when_no_new_items(tmp_path):
    out = tmp_path / "Obsidian Vault"
    uv.build_unified(_media(), _substack(), vault_dir=out)
    uv.build_unified(_media(), _substack(), vault_dir=out)  # identical rebuild

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 1        # no duplicate entry for an unchanged rebuild


def test_log_records_removed_items(tmp_path):
    out = tmp_path / "Obsidian Vault"
    uv.build_unified(_media(), _substack(), vault_dir=out)

    shrunk = MediaCatalog(items=_media().items[:1])  # drop the web article
    uv.build_unified(shrunk, _substack(), vault_dir=out)

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 2
    assert "1 item(s) removed (2 total: 1 YouTube, 0 web, 0 Instagram, 1 Substack)" in log
