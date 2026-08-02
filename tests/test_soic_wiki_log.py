def test_log_ingest_backfills_first_entry_when_log_absent(tmp_path):
    from soic_wiki.log import log_ingest

    log_path = tmp_path / "log.md"
    wrote = log_ingest(log_path, total=23, summary="22 concept(s) synthesized", stamp="2026-07-14")

    assert wrote is True
    text = log_path.read_text(encoding="utf-8")
    assert text.startswith("# Persona Wiki Log\n")
    assert "backfill: 22 concept(s) synthesized (log started here) (23 total)" in text
    assert "2026-07-14" in text


def test_log_ingest_appends_delta_entry_when_total_changes(tmp_path):
    from soic_wiki.log import log_ingest

    log_path = tmp_path / "log.md"
    log_ingest(log_path, total=23, summary="backfill", stamp="2026-07-14")

    wrote = log_ingest(log_path, total=459, summary="436 new concept(s) synced", stamp="2026-08-02")

    assert wrote is True
    text = log_path.read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if l.startswith("- ")]
    assert len(lines) == 2
    assert "436 new concept(s) synced (459 total)" in lines[1]
    assert "backfill:" not in lines[1]


def test_log_ingest_is_noop_when_total_unchanged(tmp_path):
    from soic_wiki.log import log_ingest

    log_path = tmp_path / "log.md"
    log_ingest(log_path, total=23, summary="backfill", stamp="2026-07-14")
    before = log_path.read_text(encoding="utf-8")

    wrote = log_ingest(log_path, total=23, summary="no-op rebuild", stamp="2026-07-15")

    assert wrote is False
    assert log_path.read_text(encoding="utf-8") == before


def test_log_ingest_reports_removed_items_on_negative_delta(tmp_path):
    from soic_wiki.log import log_ingest

    log_path = tmp_path / "log.md"
    log_ingest(log_path, total=100, summary="backfill", stamp="2026-07-14")

    log_ingest(log_path, total=90, summary="10 item(s) removed", stamp="2026-08-02")

    text = log_path.read_text(encoding="utf-8")
    assert "10 item(s) removed (90 total)" in text
