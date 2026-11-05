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


def test_jev_verifier_maps_verified_to_its_confidence_and_anything_else_to_zero():
    seen = {}

    def fake(tool, args):
        seen.update(tool=tool, args=args)
        return {"results": [{"verdict": "verified", "confidence": 0.93}]}, None
    assert jev_verifier(fake)("q", "INR 854", "revenue INR 854") == 0.93
    assert seen["tool"] == "jev_verify" and "INR 854" in str(seen["args"])
    assert jev_verifier(lambda t, a: ({"results": [{"verdict": "unsupported", "confidence": 0.9}]}, None))("q", "a", "e") == 0.0


def test_jev_verifier_raises_on_an_error_or_a_shape_it_does_not_know():
    import pytest
    with pytest.raises(RuntimeError):
        jev_verifier(lambda t, a: (None, "TYPESAFE_API_KEY is not set"))("q", "a", "e")
    with pytest.raises(RuntimeError):
        jev_verifier(lambda t, a: ({"weird": 1}, None))("q", "a", "e")


def test_laya_verifier_asks_one_noul_question_and_returns_its_probability():
    class FakeAgent:
        def predict(self, state, questions):
            assert state["excerpt"] == "e" and "ok" in questions and questions["ok"]["type"] == "noul"
            return {"answers": {"ok": {"noul": 0.77}}}
    assert laya_verifier(FakeAgent())("q", "a", "e") == 0.77


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
