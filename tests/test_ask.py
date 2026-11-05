from vps_extraction.ask import ask
from vps_extraction.multi_index import Chunk, build
from vps_extraction.page_index import build_index


def _indexes(tmp_path):
    (tmp_path / "p001.md").write_text("Total income was Rs 172,695 million in the year.")
    (tmp_path / "p002.md").write_text("Nothing about money here.")
    multi = build([Chunk("call", "2024-02-09 p7", "Syngene revenue from operations INR 854 crores", "q3fy24"),
                   Chunk("announcement", "2024-03-01 Press Release http://x", "Dividend declared")])
    return build_index(tmp_path), multi


def test_every_hit_carries_source_label_and_a_snippet(tmp_path):
    ar, multi = _indexes(tmp_path)
    hits = ask("Syngene revenue Q3FY24", ar, multi)["hits"]
    top = hits[0]
    assert (top["source"], top["label"]) == ("call", "2024-02-09 p7")
    assert "854" in top["snippet"]


def test_annual_report_hits_are_cited_by_page(tmp_path):
    ar, multi = _indexes(tmp_path)
    hits = ask("total income", ar, multi)["hits"]
    assert ("annual-report", "AR p1") in [(h["source"], h["label"]) for h in hits]


def test_a_number_is_answered_only_if_its_digits_are_on_a_hit(tmp_path):
    ar, multi = _indexes(tmp_path)
    ok = ask("total income", ar, multi, number="172,695")
    assert ok["status"] == "ok" and ok["found_in"] == ("annual-report", "AR p1")
    no = ask("total income", ar, multi, number="999,999")
    assert no["status"] == "refuse" and "found_in" not in no


def test_no_match_at_all_is_a_refusal_not_a_guess(tmp_path):
    ar, multi = _indexes(tmp_path)
    r = ask("zzzzqq", ar, multi, number="1")
    assert r["hits"] == [] and r["status"] == "refuse"
