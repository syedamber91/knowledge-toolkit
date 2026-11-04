from vps_extraction.golden_candidates import parse_line, check_row


def test_parse_line_gets_numbers_and_pages():
    r = parse_line("- Total income for FY26 was 172,695 million rupees, growth of 14%. (AR p6)")
    assert r["pages"] == [6]
    assert "172,695" in r["numbers"] and "14%" in r["numbers"]


def test_parse_line_without_cite_is_none():
    assert parse_line("- no cite here 1,234") is None


def test_check_row_found_and_missing(tmp_path):
    (tmp_path / "p006.md").write_text("Total income 172,695 and 60%")
    ok = check_row({"pages": [6], "numbers": ["172,695", "60%"]}, tmp_path)
    assert ok["missing"] == []
    bad = check_row({"pages": [6], "numbers": ["172,695", "99,999"]}, tmp_path)
    assert bad["missing"] == ["99,999"]


def test_missing_page_file_marks_all_missing(tmp_path):
    r = check_row({"pages": [7], "numbers": ["1,000"]}, tmp_path)
    assert r["missing"] == ["1,000"]
