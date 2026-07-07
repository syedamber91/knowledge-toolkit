import importlib


def test_reports_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("STORM_REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setenv("STORM_HTML_DIR", str(tmp_path / "html"))
    import storm_core.config as cfg
    importlib.reload(cfg)
    assert cfg.REPORTS_DIR == (tmp_path / "reports")
    assert cfg.HTML_OUT_DIR == (tmp_path / "html")
