from vps_extraction.multi_index import (Chunk, chunk_call, chunk_deck_layout, chunk_announcements,
                                        build, search)


def test_call_split_on_form_feed_one_chunk_per_page_and_empty_dropped():
    cs = chunk_call("page one text\fpage two text\f \f", "2024-02-09")
    assert [(c.source, c.label) for c in cs] == [("call", "2024-02-09 p1"), ("call", "2024-02-09 p2")]


def test_deck_layout_split_on_page_headers():
    t = "=== deck-2024-02-09-q3fy24 page 1 ===\nfront\n=== deck-2024-02-09-q3fy24 page 2 ===\nrevenue 5,000\n"
    cs = chunk_deck_layout(t)
    assert [(c.label, c.text.strip()) for c in cs] == [("deck-2024-02-09-q3fy24 p1", "front"),
                                                       ("deck-2024-02-09-q3fy24 p2", "revenue 5,000")]


def test_announcement_row_is_one_chunk_labelled_with_date_type_url():
    csv_text = 'sort_date,desc,text,url\n2026-09-08 08:31:17,Press Release,"Pertuzumab deal, Brazil",http://x/y.pdf\n'
    (c,) = chunk_announcements(csv_text)
    assert c.source == "announcement" and c.label == "2026-09-08 Press Release http://x/y.pdf"
    assert "Pertuzumab deal, Brazil" in c.text


def test_search_returns_source_and_label_across_sources():
    conn = build([Chunk("call", "2024-02-09 p2", "biosimilars guidance margin"),
                  Chunk("deck", "d p1", "revenue only")])
    hits = search(conn, "biosimilars margin", k=3)
    assert hits[0][:2] == ("call", "2024-02-09 p2")


def test_search_can_be_limited_to_one_source():
    conn = build([Chunk("call", "a", "alpha beta"), Chunk("deck", "b", "alpha beta alpha")])
    assert {h[0] for h in search(conn, "alpha", k=5, source="call")} == {"call"}
