from vps_extraction.verify_golden import verify_row


def test_page_grep_pass_and_fail(tmp_path):
    (tmp_path / "p006.md").write_text("Total 172,695")
    ok = {"id": "x", "kind": "page_grep", "pages": [6], "tokens": ["172,695"]}
    assert verify_row(ok, tmp_path, None)["ok"] is True
    bad = {**ok, "tokens": ["999"]}
    assert verify_row(bad, tmp_path, None)["ok"] is False


def test_derived_calc():
    r = {"id": "d", "kind": "derived", "calc": "5375+1870", "value": 7245}
    assert verify_row(r, None, None)["ok"] is True
    assert verify_row({**r, "value": 7000}, None, None)["ok"] is False


def test_calc_rejects_non_arithmetic():
    import pytest
    with pytest.raises(ValueError):
        verify_row({"id": "e", "kind": "derived", "calc": "__import__('os')", "value": 1}, None, None)


def test_refuse_kinds_are_not_machine_checked():
    r = verify_row({"id": "n", "kind": "not_in_corpus"}, None, None)
    assert r["ok"] is None  # needs a human / the retrieval test
