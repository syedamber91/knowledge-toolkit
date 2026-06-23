import re

from media_toolkit import vault
from media_toolkit.models import KIND_ARTICLE, KIND_YOUTUBE, MediaCatalog, MediaItem


def _catalog():
    return MediaCatalog(items=[
        MediaItem(kind=KIND_YOUTUBE, title="Kafka deep dive",
                  url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                  source="DataChan", source_id="UC1",
                  duration_seconds=3725,
                  body_markdown="kafka transcript text",
                  topics=["Apache Kafka", "Streaming"], keywords=["kafka"]),
        MediaItem(kind=KIND_ARTICLE, title="Kafka in production",
                  url="https://blog.example.com/kafka",
                  source="example.com", source_id="example.com",
                  body_markdown="kafka article body",
                  topics=["Apache Kafka"], keywords=["kafka"]),
        MediaItem(kind=KIND_YOUTUBE, title="No transcript video",
                  url="https://www.youtube.com/watch?v=zzzzzzzzzzz",
                  source="DataChan", source_id="UC1",
                  body_markdown="", body_accessible=False, topics=[]),
    ])


def test_build_vault_cross_source_topic_and_layout(tmp_path):
    out = tmp_path / "vault"
    vault.build_vault(_catalog(), vault_dir=out)

    written = {p.relative_to(out).as_posix() for p in out.rglob("*.md")}
    assert "Home.md" in written
    assert "youtube/datachan/kafka-deep-dive-dQw4w9WgXcQ.md" in written
    assert "web/examplecom/kafka-in-production-" + _hash("https://blog.example.com/kafka") + ".md" in written
    assert "sources/youtube-datachan.md" in written
    assert "sources/article-examplecom.md" in written
    assert "topics/apache-kafka.md" in written

    # The shared topic note lists BOTH a YouTube and a Web source section.
    kafka = (out / "topics" / "apache-kafka.md").read_text()
    assert "## YouTube · DataChan" in kafka
    assert "## Web · example.com" in kafka

    # The no-transcript video shows a warning callout.
    note = (out / "youtube" / "datachan" / "no-transcript-video-zzzzzzzzzzz.md").read_text()
    assert "[!warning]" in note


def test_build_vault_has_no_broken_wikilinks(tmp_path):
    out = tmp_path / "vault"
    vault.build_vault(_catalog(), vault_dir=out)
    resolvable = set()
    for md in out.rglob("*.md"):
        resolvable.add(md.relative_to(out).as_posix()[:-3])
        resolvable.add(md.stem)
    broken = []
    for md in out.rglob("*.md"):
        text = re.sub(r"```.*?```", "", md.read_text(), flags=re.S)  # ignore code
        for target in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text):
            if target not in resolvable:
                broken.append((md.relative_to(out).as_posix(), target))
    assert broken == [], f"broken wikilinks: {broken}"


def _hash(url: str) -> str:
    import hashlib
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:6]
