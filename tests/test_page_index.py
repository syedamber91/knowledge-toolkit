from vps_extraction.page_index import build_index, search, answer_or_refuse


def _pages(tmp_path):
    (tmp_path / "p001.md").write_text("Cover page. Biocon annual report.")
    (tmp_path / "p002.md").write_text("Total income 172,695 Rs million for the year.")
    (tmp_path / "p003.md").write_text("Median employee remuneration rose. Ratio 71.78 times.")
    (tmp_path / "manifest.json").write_text("{}")  # must be ignored: not a page
    return build_index(tmp_path)


def test_one_chunk_per_page_page_number_from_file_name(tmp_path):
    conn = _pages(tmp_path)
    assert conn.execute("select count(*) from pages").fetchone()[0] == 3
    assert [p for p, _ in search(conn, "total income", k=3)][0] == 2


def test_search_never_crashes_on_punctuation(tmp_path):
    conn = _pages(tmp_path)
    assert search(conn, 'FY26 "total income"? (Rs. million)', k=3)[0][0] == 2


def test_empty_query_returns_nothing(tmp_path):
    assert search(_pages(tmp_path), "?!", k=3) == []


def test_answer_cites_page_when_number_is_on_a_retrieved_page(tmp_path):
    r = answer_or_refuse(_pages(tmp_path), "total income", "172,695", k=3)
    assert r == {"status": "ok", "page": 2}


def test_refuses_when_number_is_not_on_any_retrieved_page(tmp_path):
    r = answer_or_refuse(_pages(tmp_path), "total income", "999,999", k=3)
    assert r["status"] == "refuse"


def test_number_must_match_whole_not_inside_a_longer_number(tmp_path):
    (tmp_path / "p001.md").write_text("Capex was 11,999 and 9990 units. Total income grew.")
    conn = build_index(tmp_path)
    assert answer_or_refuse(conn, "total income", "999", k=3)["status"] == "refuse"
    assert answer_or_refuse(conn, "total income", "11,999", k=3)["status"] == "ok"
    assert answer_or_refuse(conn, "total income", "9990", k=3)["status"] == "ok"


def test_year_spellings_all_become_fy26():
    from vps_extraction.page_index import normalize_years
    for s in ["26FY", "FY 2026", "FY2026", "FY2025-26", "FY 2025-26", "FY26"]:
        assert normalize_years(s) == "FY26", s
    assert normalize_years("FY25 and 24FY") == "FY25 and FY24"


def test_page_that_prints_26FY_is_found_by_a_FY26_question(tmp_path):
    (tmp_path / "p001.md").write_text("Highlights 26FY total income 172,695")
    (tmp_path / "p002.md").write_text("Total income total income total income notes and more text here")
    conn = build_index(tmp_path)
    assert search(conn, "FY26 total income", k=1)[0][0] == 1


def test_query_terms_drop_filler_words():
    from vps_extraction.page_index import query_terms
    assert query_terms("What was the total income for FY26?") == ["total", "income", "FY26"]
    assert query_terms("what was the") == []


def test_word_endings_do_not_hide_a_page(tmp_path):
    (tmp_path / "p001.md").write_text("interest net of borrowing cost capitalisation 1,597")
    (tmp_path / "p002.md").write_text("unrelated words only")
    assert [pg for pg, _ in search(build_index(tmp_path), "capitalised", k=2)] == [1]
