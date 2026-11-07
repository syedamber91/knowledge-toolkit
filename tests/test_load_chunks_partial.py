from vps_extraction.eval_multi_index import load_chunks


def test_a_company_with_only_an_annual_report_loads_zero_chunks_instead_of_crashing(tmp_path):
    assert load_chunks(tmp_path) == []


def test_a_company_with_only_an_announcements_file_loads_just_those(tmp_path):
    (tmp_path / "announcements-latest.csv").write_text("")
    assert load_chunks(tmp_path) == []
