from vps_extraction.t6_models import ANSWERABLE
from vps_extraction.truth_exam import filing_chunks, truth_rows

CSV = ("quarter_end,source,note,sale_of_products,total_income,finance_costs,profit_for_period\n"
       "2024-03-31,own filing,n,29473,39657,-2270,500\n"
       "2024-06-30,own filing,n,,45674,2360,\n")


def test_each_big_filled_cell_becomes_one_question_with_the_comma_formatted_value(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text(CSV)
    rows = truth_rows(p)
    by = {r["id"]: r for r in rows}
    r = by["T-2024-03-31-sale_of_products"]
    assert r["tokens"] == ["29,473"] and r["kind"] in ANSWERABLE
    assert "2024-03-31" in r["question"] and "sale of products" in r["question"].lower()
    assert by["T-2024-03-31-finance_costs"]["tokens"] == ["2,270"]      # sign dropped: statements print (2,270)
    assert "T-2024-06-30-sale_of_products" not in by                     # blank cell
    assert "T-2024-03-31-profit_for_period" not in by                    # below 1,000: too easy to match by luck


def test_filing_excerpts_become_one_chunk_per_quarter_with_the_quarter_searchable(tmp_path):
    (tmp_path / "consolidated-2024-03-31.txt").write_text("Sale of products 29,473")
    (tmp_path / "segment-2024-03-31.txt").write_text("ignored")
    cs = filing_chunks(tmp_path)
    assert len(cs) == 1 and cs[0].source == "filing" and cs[0].label == "Filing 2024-03-31"
    assert "2024-03-31" in cs[0].tags and "29,473" in cs[0].text
