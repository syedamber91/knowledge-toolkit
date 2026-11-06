import pytest

from vps_extraction.t6_models import (build_prompt, load_key, parse_reply, score_row, summarize)

HITS = [{"source": "call", "label": "2024-02-09 p7", "snippet": "Syngene revenue from operations INR 854 crores"},
        {"source": "annual-report", "label": "AR p1", "snippet": "Total income Rs 172,695 million"}]
ROW = {"id": "C05", "kind": "call_grep", "question": "q", "tokens": ["INR 854"]}
NOT = {"id": "N01", "kind": "not_in_corpus", "question": "q", "tokens": []}


def test_prompt_lists_every_hit_with_its_label_and_asks_for_json():
    p = build_prompt("q?", HITS)
    assert "2024-02-09 p7" in p and "AR p1" in p and "JSON" in p and "q?" in p


def test_parse_reply_finds_json_inside_chatter_and_none_when_absent():
    assert parse_reply('sure! {"answer": "854", "cite": "x"} done') == {"answer": "854", "cite": "x"}
    assert parse_reply("no json here") is None


def test_right_number_on_the_cited_hit_passes():
    assert score_row(ROW, HITS, {"answer": "INR 854 crores", "cite": "2024-02-09 p7"}) is True


def test_a_made_up_number_fails_even_with_a_real_citation():
    assert score_row(ROW, HITS, {"answer": "INR 855 crores", "cite": "2024-02-09 p7"}) is False


def test_a_real_number_cited_to_the_wrong_hit_fails():
    assert score_row(ROW, HITS, {"answer": "854", "cite": "AR p1"}) is False


def test_a_citation_that_was_never_retrieved_fails():
    assert score_row(ROW, HITS, {"answer": "854", "cite": "2020-01-01 p9"}) is False


def test_unparseable_or_empty_reply_fails_and_refusal_only_passes_unanswerable_rows():
    assert score_row(ROW, HITS, None) is False
    assert score_row(ROW, HITS, {"refuse": True}) is False
    assert score_row(NOT, HITS, {"refuse": True}) is True
    assert score_row(NOT, HITS, {"answer": "5", "cite": "AR p1"}) is False


def test_summary_gives_min_max_and_a_noise_floor_of_one_row():
    s = summarize({"m1": [[True, False], [True, True], [False, False]]})
    assert s["m1"]["min"] == 0 and s["m1"]["max"] == 100 and s["m1"]["reps"] == 3
    assert s["noise_floor"] == 50.0  # 2 rows -> one row = 50 points


def test_key_is_read_from_env_file_and_missing_key_raises_without_leaking(tmp_path):
    f = tmp_path / ".env"
    f.write_text("OTHER=1\nNVIDIA_API_KEY='abc123'\n")
    assert load_key(f) == "abc123"
    f.write_text("OTHER=1\n")
    with pytest.raises(RuntimeError) as e:
        load_key(f)
    assert "abc123" not in str(e.value)


def test_key_comes_from_the_environment_first_and_env_file_is_optional(tmp_path, monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "fromenv")
    assert load_key(None) == "fromenv"
    f = tmp_path / ".env"
    f.write_text("NVIDIA_API_KEY=fromfile\n")
    assert load_key(f) == "fromenv"  # project env var wins
    monkeypatch.delenv("NVIDIA_API_KEY")
    assert load_key(f) == "fromfile"
    with pytest.raises(RuntimeError):
        load_key(None)


def test_why_wrong_names_the_first_reason_a_reply_fails():
    from vps_extraction.t6_models import why_wrong
    hits = [{"source": "call", "label": "c p7", "snippet": "revenue INR 854 crores"}]
    row = {"id": "C05", "kind": "call_grep", "question": "q", "tokens": ["INR 854"]}
    assert why_wrong(row, hits, None) == "no JSON in reply"
    assert why_wrong(row, hits, {"refuse": True}) == "refused an answerable row"
    assert why_wrong(row, hits, {"answer": "854", "cite": "zzz"}) == "cite is not a shown label"
    assert why_wrong(row, hits, {"answer": "855", "cite": "c p7"}) == "number missing from answer"
    assert why_wrong(row, hits, {"answer": "854", "cite": "c p7"}) == "ok"
    hits2 = [{"source": "call", "label": "c p7", "snippet": "revenue nothing"}]
    assert why_wrong(row, hits2, {"answer": "854", "cite": "c p7"}) == "number not on the cited hit"
    unans = {"id": "N01", "kind": "not_in_corpus", "question": "q", "tokens": []}
    assert why_wrong(unans, hits, {"answer": "1", "cite": "c p7"}) == "answered an unanswerable row"


def test_parse_reply_strips_brackets_the_prompt_shows_around_a_cite():
    assert parse_reply('{"answer": "1", "cite": "[AR p347]"}')["cite"] == "AR p347"
    assert parse_reply('{"answer": "1", "cite": "AR p347"}')["cite"] == "AR p347"


# --- exam fixes after the Opus review (2026-11-06) ---
from vps_extraction.t6_models import UTILITY, find_hit, verdict


def test_find_hit_accepts_a_cite_with_trailing_junk_and_brackets_but_not_a_guess():
    assert find_hit(HITS, "AR p1] (annual-report)")["label"] == "AR p1"
    assert find_hit(HITS, "[2024-02-09 p7]")["label"] == "2024-02-09 p7"
    assert find_hit(HITS, "ar P1")["label"] == "AR p1"
    assert find_hit(HITS, "AR p10") is None  # p10 must not match p1
    assert find_hit(HITS, "2020-01-01 p9") is None


def test_verdict_is_right_refused_wrong_or_none_and_refused_beats_wrong():
    assert verdict(ROW, HITS, {"answer": "INR 854", "cite": "2024-02-09 p7"}) == "right"
    assert verdict(ROW, HITS, {"refuse": True}) == "refused"
    assert verdict(ROW, HITS, {"answer": "INR 999", "cite": "2024-02-09 p7"}) == "wrong"
    assert verdict(ROW, HITS, None) == "none"
    assert verdict(NOT, HITS, {"refuse": True}) == "right"
    assert verdict(NOT, HITS, {"answer": "5", "cite": "AR p1"}) == "wrong"
    assert UTILITY["right"] > UTILITY["refused"] > UTILITY["wrong"]


def test_a_row_with_no_digits_is_scored_on_its_words_not_failed_forever():
    row = {"id": "A06", "kind": "announcement_grep", "question": "q", "tokens": ["Biofusion Therapeutics"]}
    hits = [{"source": "announcement", "label": "a1", "snippet": "Biocon acquires Biofusion Therapeutics Inc."}]
    assert score_row(row, hits, {"answer": "Biofusion Therapeutics", "cite": "a1"}) is True
    assert score_row(row, hits, {"answer": "Something else", "cite": "a1"}) is False


def test_the_model_is_shown_and_scored_on_the_same_text_not_a_short_snippet():
    hit = {"source": "annual-report", "label": "AR p5", "snippet": "short", "shown": "short ... Total income 172,695"}
    row = {"id": "G", "kind": "page_grep", "question": "q", "tokens": ["172,695"]}
    assert "172,695" in build_prompt("q", [hit])
    assert score_row(row, [hit], {"answer": "172,695", "cite": "AR p5"}) is True
