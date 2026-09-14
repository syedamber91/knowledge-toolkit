from pathlib import Path

from udemy_toolkit import config


def test_paths_are_under_repo_root():
    assert config.STATE_PATH == config.AUTH_DIR / "udemy_state.json"
    assert config.CATALOG_PATH == config.DATA_DIR / "udemy.json"
    assert config.AUTH_DIR.name == ".auth"


def test_default_vault_is_the_icloud_udemy_vault(monkeypatch):
    monkeypatch.delenv("UDEMY_VAULT_DIR", raising=False)
    resolved = config.resolve_vault_dir()
    assert resolved.name == "Udemy Vault"
    assert "iCloud~md~obsidian" in str(resolved)


def test_vault_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("UDEMY_VAULT_DIR", str(tmp_path / "elsewhere"))
    assert config.resolve_vault_dir() == Path(tmp_path / "elsewhere")


def test_settings_defaults():
    assert config.settings.base_url == "https://www.udemy.com"
    assert config.settings.crawl_min_delay == 1.5
    assert config.settings.crawl_max_delay == 3.5
    assert config.settings.crawl_headed is True
