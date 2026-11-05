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
