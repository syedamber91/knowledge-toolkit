from typer.testing import CliRunner

from udemy_toolkit.cli import app

runner = CliRunner()


def test_help_lists_every_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("login", "status", "crawl", "build-vault"):
        assert command in result.stdout


def test_build_vault_exits_nonzero_with_an_empty_catalog(tmp_path, monkeypatch):
    monkeypatch.setattr("udemy_toolkit.cli.CATALOG_PATH", tmp_path / "empty.json")
    result = runner.invoke(app, ["build-vault"])
    assert result.exit_code == 1
    assert "Nothing captured yet" in result.stdout
