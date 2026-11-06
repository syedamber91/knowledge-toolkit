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


def test_note_is_created_with_frontmatter_then_appended_never_overwritten(tmp_path):
    from vps_extraction.ask import write_note
    ar, multi = _indexes(tmp_path)
    note = tmp_path / "vault" / "BIOCON.md"
    r1 = ask("total income", ar, multi, number="172,695")
    write_note(note, "total income", r1, "172,695", "2026-11-05 10:00")
    r2 = ask("Syngene revenue Q3FY24", ar, multi)
    write_note(note, "Syngene revenue Q3FY24", r2, None, "2026-11-05 10:05")
    t = note.read_text()
    assert t.startswith("---\n") and t.count("tags:") == 1
    assert t.index("total income") < t.index("Syngene revenue Q3FY24")  # append order
    assert "OK" in t and "annual-report AR p1" in t and "call 2024-02-09 p7" in t


def test_note_records_a_refusal_plainly(tmp_path):
    from vps_extraction.ask import write_note
    ar, multi = _indexes(tmp_path)
    note = tmp_path / "BIOCON.md"
    write_note(note, "total income", ask("total income", ar, multi, number="999,999"), "999,999", "t")
    assert "REFUSE" in note.read_text()


def test_hits_carry_the_page_text_capped_and_centred_when_it_is_long(tmp_path):
    ar, multi = _indexes(tmp_path)
    h = ask("total income", ar, multi)["hits"][0]
    assert "172,695" in h["text"]
    (tmp_path / "p003.md").write_text("total income " + "filler " * 3000 + " 999,111 at the end")
    from vps_extraction.page_index import build_index
    long_hit = [x for x in ask("total income", build_index(tmp_path), multi, text_cap=500)["hits"] if x["label"] == "AR p3"][0]
    assert len(long_hit["text"]) <= 500
