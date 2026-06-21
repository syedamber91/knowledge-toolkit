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


def test_post_frontmatter_is_valid_yaml_with_special_chars(tmp_path):
    from datetime import datetime, timezone

    tricky = SubstackCatalog(
        channels=[
            Channel(handle="vutr", url="https://vutr.substack.com", posts=[
                Post(
                    title=r'Paths like C:\Users and a "quote"',
                    slug="tricky-post",
                    url="https://vutr.substack.com/p/tricky-post",
                    published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                    body_markdown="body",
                    topics=["dbt"],
                ),
            ]),
        ]
    )
    vault.build_vault(tricky, vault_dir=tmp_path)
    note = (tmp_path / "posts" / "vutr" / "tricky-post.md").read_text()

    # Extract the frontmatter block and confirm it parses as valid YAML.
    assert note.startswith("---\n")
    fm_block = note.split("---\n", 2)[1]

    import importlib.util
    if importlib.util.find_spec("yaml") is not None:
        import yaml
        meta = yaml.safe_load(fm_block)
        assert meta["title"] == r'Paths like C:\Users and a "quote"'
    else:
        # No PyYAML available: at least assert the title line is present and the
        # backslash/quote were escaped (not left raw to break parsing).
        assert r'title: "Paths like C:\\Users and a \"quote\""' in note
