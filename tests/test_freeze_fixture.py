import json
from vps_extraction.freeze_fixture import freeze, verify


def test_freeze_writes_file_and_sidecar(tmp_path):
    p = freeze(b"<html>343</html>", "https://example.test/x", tmp_path, "screener.html", now="2026-11-04T10:00:00Z")
    assert p.read_bytes() == b"<html>343</html>"
    meta = json.loads((tmp_path / "screener.html.meta.json").read_text())
    assert meta["source_url"] == "https://example.test/x"
    assert meta["fetched_at"] == "2026-11-04T10:00:00Z"
    assert len(meta["sha256"]) == 64


def test_verify_ok_then_detects_change(tmp_path):
    p = freeze(b"abc", "u", tmp_path, "a.txt", now="t")
    assert verify(p) is True
    p.write_bytes(b"abd")
    assert verify(p) is False


def test_empty_body_refused(tmp_path):
    # a 200 shell page / empty read must fail loudly, not be saved
    import pytest
    with pytest.raises(ValueError):
        freeze(b"", "u", tmp_path, "a.txt", now="t")
