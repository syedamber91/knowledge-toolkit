from vps_extraction.t6_combo import (ARMS, gate, jev_verifier, laya_verifier, run_arms)

HITS = [{"source": "call", "label": "c p7", "snippet": "revenue was INR 854 crores"},
        {"source": "annual-report", "label": "AR p1", "snippet": "income Rs 172,695 million"}]
ROW = {"id": "C05", "kind": "call_grep", "question": "q", "tokens": ["INR 854"]}
NOT = {"id": "N01", "kind": "not_in_corpus", "question": "q", "tokens": []}
GOOD = {"answer": "INR 854 crores", "cite": "c p7"}


def yes(q, a, e):
    return 0.9


def no(q, a, e):
    return 0.1


def test_gate_keeps_an_answer_every_verifier_accepts():
    assert gate(GOOD, HITS, "q", [yes, yes]) == GOOD


def test_gate_turns_an_answer_into_a_refusal_if_any_verifier_rejects():
    out = gate(GOOD, HITS, "q", [yes, no])
    assert out["refuse"] is True and out["gated_by"] == 1


def test_gate_refuses_a_cite_that_was_never_shown_and_never_calls_a_verifier():
    def boom(q, a, e):
        raise AssertionError("must not be called")
    assert gate({"answer": "1", "cite": "zzz"}, HITS, "q", [boom])["refuse"] is True


def test_gate_passes_refusals_and_empty_replies_through_untouched():
    assert gate({"refuse": True}, HITS, "q", [no]) == {"refuse": True}
    assert gate(None, HITS, "q", [no]) is None


def test_a_verifier_that_errors_fails_closed_and_is_counted():
    def broken(q, a, e):
        raise RuntimeError("down")
    errs = []
    out = gate(GOOD, HITS, "q", [broken], errors=errs)
    assert out["refuse"] is True and len(errs) == 1


def test_jev_verifier_asks_one_noul_question_and_returns_its_probability():
    seen = {}

    class R:
        nouls = {"ok": type("N", (), {"noul": 0.93})()}

    class FakeClient:
        def system_one(self, state, questions):
            seen.update(state=state, questions=questions)
            return R()
    assert jev_verifier(FakeClient(), lambda instructions: ("NOUL", instructions))("the q", "INR 854", "revenue INR 854") == 0.93
    assert "INR 854" in seen["state"] and "the q" in seen["state"]
    assert list(seen["questions"]) == ["ok"] and seen["questions"]["ok"][0] == "NOUL"


def test_laya_verifier_asks_one_noul_question_and_returns_its_probability():
    class FakeAgent:
        def system_one(self, text, questions):
            assert "the question" in text and "the answer" in text and "the excerpt" in text
            assert list(questions) == ["ok"] and questions["ok"]["type"] == "noul"
            return {"answers": {"ok": {"noul": 0.77}}}
    assert laya_verifier(FakeAgent())("the question", "the answer", "the excerpt") == 0.77


def test_arms_share_one_set_of_model_replies_and_differ_only_by_the_gate():
    rows = [ROW, NOT]
    hits = {"C05": HITS, "N01": HITS}
    replies = {"C05": [GOOD, GOOD], "N01": [{"answer": "9", "cite": "AR p1"}, {"refuse": True}]}  # 2 reps
    out = run_arms(rows, hits, replies, {"plain": [], "gated": [no]})
    assert out["plain"]["reps"] == [[True, False], [True, True]]   # N01 rep1 invented an answer
    assert out["gated"]["reps"] == [[False, True], [False, True]]  # gate blocks the good C05 answer, catches the invention
    assert out["gated"]["blocked_right"] == 2 and out["gated"]["caught_wrong"] == 1


def test_four_arms_are_defined():
    assert list(ARMS) == ["nemotron", "nemotron+jev", "nemotron+laya", "nemotron+jev+laya"]


def test_collect_replies_keeps_errors_with_their_reason_and_never_swallows_them():
    from vps_extraction.t6_combo import collect_replies
    calls = iter([('{"refuse": true}', None), (None, "status=404 attempts=1: model not found")])
    rows = [ROW, NOT]
    replies, errors = collect_replies(rows, {"C05": HITS, "N01": HITS}, 1, lambda prompt: next(calls))
    assert replies["C05"] == [{"refuse": True}] and replies["N01"] == [None]
    assert errors == [("N01", "status=404 attempts=1: model not found")]


def test_a_run_where_most_model_calls_failed_is_stopped_not_tabled():
    import pytest
    from vps_extraction.t6_combo import check_error_rate
    check_error_rate([("a", "x")], 10)  # 10% failing: fine
    with pytest.raises(SystemExit) as e:
        check_error_rate([("a", "status=404")] * 6, 10)
    assert "status=404" in str(e.value) and "6 of 10" in str(e.value)


def test_a_404_stop_message_lists_the_nemotron_ids_the_account_can_use():
    import pytest
    from vps_extraction.t6_combo import check_error_rate
    with pytest.raises(SystemExit) as e:
        check_error_rate([("a", "status=404 attempts=1: HTTP 404: Not Found")] * 4, 4,
                         list_models=lambda: ["nvidia/nemotron-x-1", "nvidia/nemotron-y-2"])
    assert "nvidia/nemotron-x-1" in str(e.value) and "--model" in str(e.value)


def test_the_model_list_is_only_asked_for_on_a_404():
    import pytest
    from vps_extraction.t6_combo import check_error_rate

    def boom():
        raise AssertionError("must not be called")
    with pytest.raises(SystemExit) as e:
        check_error_rate([("a", "status=503")] * 4, 4, list_models=boom)
    assert "status=503" in str(e.value)


def test_cached_verifier_calls_the_model_once_per_input():
    from vps_extraction.t6_combo import cached
    n = []

    def v(q, a, e):
        n.append(1)
        return 0.7
    c = cached(v)
    assert c("q", "a", "e") == c("q", "a", "e") == 0.7 and len(n) == 1


def test_tune_picks_the_threshold_on_train_rows_and_scores_it_on_unseen_test_rows():
    from vps_extraction.t6_combo import tune
    # unanswerable rows: a wrong answer scores 0, a refusal scores 1. Verifier gives wrong answers 0.2.
    rows = [{"id": f"N{i}", "kind": "not_in_corpus", "question": "q", "tokens": []} for i in range(4)]
    hits = {r["id"]: HITS for r in rows}
    replies = {r["id"]: [GOOD] for r in rows}
    out = tune(rows, hits, replies, lambda q, a, e: 0.2, grid=[0.0, 0.1, 0.3, 0.5])
    assert out["best"] == 0.3            # lowest threshold that blocks them all
    assert out["train"][0.3] == 4 and out["test"][0.3] == 4 and out["test"][0.0] == 0  # utility: wrong(-1) -> right(+1) = +2 per row


def test_nim_generate_retries_a_timeout_then_returns_the_reply():
    from types import SimpleNamespace as NS
    from vps_extraction.t6_combo import nim_generate
    calls = []

    def fake(prompt, model, **kw):
        calls.append(kw.get("timeout_seconds"))
        if len(calls) < 3:
            return None, NS(summary="status=transport_error attempts=1: ReadTimeout")
        return NS(content='{"refuse": true}', finish_reason="stop"), NS(summary="ok")
    text, err = nim_generate("m", call=fake, sleep=lambda s: None)("p")
    assert text == '{"refuse": true}' and err is None and len(calls) == 3 and calls[0] >= 300


def test_nim_generate_gives_up_after_three_timeouts_and_reports_it():
    from types import SimpleNamespace as NS
    from vps_extraction.t6_combo import nim_generate
    fake = lambda p, m, **kw: (None, NS(summary="status=transport_error attempts=1: ReadTimeout"))
    text, err = nim_generate("m", call=fake, sleep=lambda s: None)("p")
    assert text is None and "transport_error" in err


def test_a_gate_that_turns_a_wrong_answer_on_an_answerable_row_into_a_refusal_now_earns_a_point():
    from vps_extraction.t6_combo import tune
    rows = [dict(ROW, id=f"C{i}") for i in range(4)]
    hits = {r["id"]: HITS for r in rows}
    bad = {"answer": "INR 999", "cite": "c p7"}      # confident wrong number
    replies = {r["id"]: [bad] for r in rows}
    out = run_arms(rows, hits, replies, {"plain": [], "gated": [no]})
    assert out["plain"]["util"] == -4 and out["gated"]["util"] == 0 and out["gated"]["verdicts"]["refused"] == 4  # +1 each
    assert tune(rows, hits, replies, lambda q, a, e: 0.2, grid=[0.0, 0.5])["best"] == 0.5


def test_a_gate_that_blocks_a_right_answer_loses_a_point():
    rows = [ROW]
    out = run_arms(rows, {"C05": HITS}, {"C05": [GOOD]}, {"plain": [], "gated": [no]})
    assert out["plain"]["util"] == 1 and out["gated"]["util"] == 0


def test_grep_answer_picks_the_line_that_shares_the_most_question_words_and_refuses_when_too_few():
    from vps_extraction.t6_combo import grep_answer
    hits = [{"source": "call", "label": "c p7", "snippet": "x",
             "text": "Intro words only. Syngene revenue from operations was INR 854 crores in the quarter. Other 12 things."}]
    got = grep_answer("What was Syngene revenue from operations?", hits)
    assert got["cite"] == "c p7" and "854" in got["answer"] and "12" not in got["answer"]
    assert grep_answer("Totally unrelated zebra question", hits) == {"refuse": True}


def test_grep_first_uses_grep_for_prose_sources_and_the_model_for_tables():
    from vps_extraction.t6_combo import grep_first
    prose = {"source": "call", "label": "c p7", "snippet": "s", "text": "Syngene revenue from operations INR 854 crores"}
    table = {"source": "annual-report", "label": "AR p1", "snippet": "s", "text": "Total income 172,695"}
    rows = [{"id": "A", "kind": "call_grep", "question": "Syngene revenue from operations?", "tokens": ["854"]},
            {"id": "B", "kind": "page_grep", "question": "Total income?", "tokens": ["172,695"]}]
    hits = {"A": [prose], "B": [table]}
    model = {"A": [{"answer": "MODEL"}], "B": [{"answer": "MODEL"}]}
    out = grep_first(rows, hits, model)
    assert "854" in out["A"][0]["answer"] and out["B"] == [{"answer": "MODEL"}]


def test_the_gate_finds_a_cite_the_same_loose_way_the_scorer_does():
    # a right answer whose cite carries brackets/trailing words must not be blocked by the gate itself
    reply = {"answer": "INR 854 crores", "cite": "[c p7] (call)"}
    assert gate(reply, HITS, "q", []) == reply
    assert run_arms([ROW], {"C05": HITS}, {"C05": [reply]}, {"plain": []})["plain"]["blocked_right"] == 0


def test_replies_can_be_saved_and_reloaded_for_offline_rescoring(tmp_path):
    from vps_extraction.t6_combo import load_replies, save_replies
    p = tmp_path / "r.json"
    save_replies(p, {"C05": [GOOD, None]})
    assert load_replies(p) == {"C05": [GOOD, None]}
