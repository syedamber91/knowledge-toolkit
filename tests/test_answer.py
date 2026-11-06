from vps_extraction.answer import answer, check_answer, numbers_in, write_answer_note

HITS = [{"source": "call", "label": "2024-02-09 p7", "snippet": "s", "text": "Syngene revenue from operations INR 854 crores, up 12%"},
        {"source": "annual-report", "label": "AR p1", "snippet": "s", "text": "Total income Rs 172,695 million"}]


def test_numbers_in_keeps_real_figures_and_drops_small_labels_like_fy26():
    assert numbers_in("FY26: Rs 172,695 million; FY25: 1,782; 12% growth; 3 quarters; 854") == ["172,695", "1,782", "12%", "854"]


def test_an_answer_whose_numbers_are_all_on_the_cited_page_is_accepted():
    ok, hit, why = check_answer({"answer": "INR 854 crores", "cite": "[2024-02-09 p7]"}, HITS)
    assert ok and hit["label"] == "2024-02-09 p7" and why == ""


def test_a_number_that_is_not_on_the_cited_page_becomes_a_refusal_with_the_reason():
    ok, hit, why = check_answer({"answer": "INR 855 crores", "cite": "2024-02-09 p7"}, HITS)
    assert not ok and "855" in why


def test_a_cite_that_was_never_shown_a_missing_cite_and_a_numberless_answer_are_all_refused():
    assert not check_answer({"answer": "854", "cite": "nope"}, HITS)[0]
    assert not check_answer({"answer": "854"}, HITS)[0]
    assert not check_answer({"answer": "it went up a lot", "cite": "AR p1"}, HITS)[0]   # no figure to verify


def test_answer_returns_the_source_and_page_when_ok_and_refuses_when_the_model_refuses():
    good = lambda prompt: ('{"answer": "INR 854 crores", "cite": "2024-02-09 p7"}', None)
    r = answer("q", HITS, good)
    assert r["status"] == "ok" and r["source"] == "call" and r["cite"] == "2024-02-09 p7" and "854" in r["answer"]
    no = lambda prompt: ('{"refuse": true}', None)
    assert answer("q", HITS, no)["status"] == "refuse"


def test_a_failed_model_call_is_a_visible_refusal_not_a_silent_fallback():
    boom = lambda prompt: (None, "transport_error")
    r = answer("q", HITS, boom)
    assert r["status"] == "refuse" and "transport_error" in r["reason"]


def test_the_note_gets_one_dated_section_per_answer_and_never_overwrites(tmp_path):
    p = tmp_path / "BIOCON.md"
    p.write_text("# BIOCON\n")
    ok = {"status": "ok", "answer": "INR 854 crores", "cite": "2024-02-09 p7", "source": "call", "reason": ""}
    write_answer_note(p, "Syngene revenue?", ok, "2026-11-07 10:00")
    write_answer_note(p, "Total income?", {"status": "refuse", "reason": "number 855 is not on the cited page"}, "2026-11-07 10:01")
    t = p.read_text()
    assert t.startswith("# BIOCON") and "INR 854 crores" in t and "call 2024-02-09 p7" in t and "REFUSE" in t and "855" in t


def test_ask_and_answer_retrieves_asks_the_model_and_logs_to_the_note(tmp_path):
    from vps_extraction.answer import ask_and_answer
    from vps_extraction.multi_index import Chunk, build
    from vps_extraction.page_index import build_index
    (tmp_path / "p001.md").write_text("Total income was Rs 172,695 million in the year.")
    multi = build([Chunk("call", "2024-02-09 p7", "Syngene revenue from operations INR 854 crores", "q3fy24")])
    seen = {}

    def gen(prompt):
        seen["prompt"] = prompt
        return '{"answer": "Rs 172,695 million", "cite": "AR p1"}', None
    note = tmp_path / "n.md"
    r = ask_and_answer("What was total income?", build_index(tmp_path), multi, gen, note=note, when="2026-11-07 10:00")
    assert r["status"] == "ok" and r["cite"] == "AR p1" and "172,695" in seen["prompt"]
    assert "ANSWER" in note.read_text() and "annual-report AR p1" in note.read_text()


# --- batching: grep for all questions, send each page once, ask several questions per call ---
from vps_extraction.answer import answer_batch, build_batch_prompt, group_questions, parse_batch_reply

PA = {"source": "annual-report", "label": "AR p34", "snippet": "s", "text": "Revenue 67,137 EBITDA 17,053"}
PB = {"source": "annual-report", "label": "AR p19", "snippet": "s", "text": "Employees 3,842 R&D 3,556"}
PC = {"source": "annual-report", "label": "AR p81", "snippet": "s", "text": "Other 999"}
QS = [{"id": "Q1", "question": "Revenue?"}, {"id": "Q2", "question": "Employees?"}, {"id": "Q3", "question": "EBITDA?"}]
HITS_BY = {"Q1": [PA, PC], "Q2": [PB], "Q3": [PA]}


def test_questions_that_share_their_top_page_go_in_the_same_batch_and_batches_are_capped():
    groups = group_questions(QS, HITS_BY, size=2)
    assert [[q["id"] for q in g] for g in groups] == [["Q1", "Q3"], ["Q2"]]
    assert all(len(g) <= 2 for g in group_questions(QS, HITS_BY, size=2))


def test_the_batch_prompt_shows_each_page_once_and_numbers_the_questions():
    p = build_batch_prompt([QS[0], QS[2]], {"Q1": [PA, PC], "Q3": [PA]})
    assert p.count("[AR p34]") == 1 and "[AR p81]" in p
    assert "1. Revenue?" in p and "2. EBITDA?" in p and "JSON" in p


def test_parse_batch_reply_reads_the_answers_list_even_inside_chatter():
    text = 'ok {"answers": [{"q": 1, "answer": "67,137", "cite": "AR p34"}, {"q": 2, "refuse": true}]} done'
    assert parse_batch_reply(text) == {1: {"answer": "67,137", "cite": "AR p34"}, 2: {"refuse": True}}
    assert parse_batch_reply("no json") is None


def test_answer_batch_checks_each_answer_against_its_own_cited_page_and_refuses_what_is_missing():
    # grouped order is Q1, Q3 (both top page p34), Q2: so "q": 2 is Q3 and "q": 3 (never answered) is Q2
    reply = ('{"answers": [{"q": 1, "answer": "67,137", "cite": "[AR p34]"}, '
             '{"q": 2, "answer": "3,999", "cite": "AR p34"}]}')   # Q3's figure is not on p34
    out = answer_batch(QS, HITS_BY, lambda prompt: (reply, None), size=3)
    assert out["Q1"]["status"] == "ok" and out["Q1"]["cite"] == "AR p34"
    assert out["Q3"]["status"] == "refuse" and "3,999" in out["Q3"]["reason"]
    assert out["Q2"]["status"] == "refuse" and "no answer" in out["Q2"]["reason"]


def test_a_failed_batch_call_refuses_every_question_in_it_visibly():
    out = answer_batch(QS, HITS_BY, lambda prompt: (None, "transport_error"), size=3)
    assert all(v["status"] == "refuse" and "transport_error" in v["reason"] for v in out.values())
