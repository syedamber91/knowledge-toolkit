from soic_senses.sector_router import Sector


def test_build_keyword_index_note_lists_keywords_with_topic_links():
    from soic_wiki.keyword_index import build_keyword_index_note

    sectors = [
        Sector(slug="fluorine-industry-megatrend-or-fad", notebook_id="n1", title="t",
               keywords=["fluorine", "backward integration"]),
    ]
    body = build_keyword_index_note(sectors, vault_topics={"fluorine-industry-megatrend-or-fad"}, stamp="2026-08-02")

    assert body.startswith("---\npersona: soic\n")
    assert "**fluorine** — [[fluorine-industry-megatrend-or-fad]]" in body
    assert "**backward integration** — [[fluorine-industry-megatrend-or-fad]]" in body


def test_build_keyword_index_note_merges_shared_keywords_across_sectors():
    from soic_wiki.keyword_index import build_keyword_index_note

    sectors = [
        Sector(slug="sector-a", notebook_id="n1", title="t", keywords=["nbfc"]),
        Sector(slug="sector-b", notebook_id="n2", title="t", keywords=["nbfc"]),
    ]
    body = build_keyword_index_note(sectors, vault_topics={"sector-a", "sector-b"}, stamp="2026-08-02")

    assert "**nbfc** — [[sector-a]] · [[sector-b]]" in body


def test_build_keyword_index_note_skips_sectors_not_in_vault():
    from soic_wiki.keyword_index import build_keyword_index_note

    sectors = [Sector(slug="not-synced-yet", notebook_id="n1", title="t", keywords=["something"])]
    body = build_keyword_index_note(sectors, vault_topics=set(), stamp="2026-08-02")

    assert "something" not in body.split("## Gaps")[0]  # not rendered in the browse table


def test_build_keyword_index_note_reports_vault_topics_missing_from_registry():
    from soic_wiki.keyword_index import build_keyword_index_note

    sectors = [Sector(slug="sector-a", notebook_id="n1", title="t", keywords=["kw"])]
    body = build_keyword_index_note(sectors, vault_topics={"sector-a", "orphan-topic"}, stamp="2026-08-02")

    assert "1 vault topic(s) have no registry entry at all" in body
    assert "`orphan-topic`" in body


def test_build_keyword_index_note_reports_zero_keyword_entries():
    from soic_wiki.keyword_index import build_keyword_index_note

    sectors = [Sector(slug="sector-a", notebook_id="n1", title="t", keywords=[])]
    body = build_keyword_index_note(sectors, vault_topics={"sector-a"}, stamp="2026-08-02")

    assert "1 registry entries map to a real vault topic but have an empty" in body
    assert "`sector-a`" in body


def test_build_keyword_index_note_reports_stale_registry_entries():
    from soic_wiki.keyword_index import build_keyword_index_note

    sectors = [Sector(slug="superseded-batch", notebook_id="n1", title="t", keywords=["kw"])]
    body = build_keyword_index_note(sectors, vault_topics=set(), stamp="2026-08-02")

    assert "1 registry entries have no matching vault topic" in body
    assert "`superseded-batch`" in body
