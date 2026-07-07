from pathlib import Path
from storm_core.roster import discover_roster, Persona


def _write_agent(d: Path, fname: str, name: str, desc: str):
    (d / fname).write_text(
        f"---\nname: {name}\ndescription: {desc}\n---\n\n# {name}\n", encoding="utf-8"
    )


def test_discovers_and_parses_agents(tmp_path):
    _write_agent(tmp_path, "buffett.md", "warren-buffett", "value investor")
    _write_agent(tmp_path, "mufti.md", "mufti-taqi-usmani", "halal compliance")
    roster = discover_roster(tmp_path)
    assert [p.name for p in roster] == ["mufti-taqi-usmani", "warren-buffett"]
    assert roster[1].description == "value investor"
    assert all(isinstance(p, Persona) for p in roster)


def test_missing_frontmatter_falls_back_to_stem(tmp_path):
    (tmp_path / "codie.md").write_text("# no frontmatter here", encoding="utf-8")
    roster = discover_roster(tmp_path)
    assert roster[0].name == "codie"
    assert roster[0].description == ""


def test_missing_dir_returns_empty(tmp_path):
    assert discover_roster(tmp_path / "does-not-exist") == []


def _write_business_persona(d, fname, title, industry, scale):
    (d / fname).write_text(
        f'---\ntitle: "{title}"\ntags: [persona]\n'
        f'industry: "{industry}"\nscale: "{scale}"\n---\n\n# X\n## Snapshot\nprose\n',
        encoding="utf-8",
    )


def test_business_persona_frontmatter_is_parsed(tmp_path):
    _write_business_persona(tmp_path, "WarrenBuffett.md",
                            "Warren Buffett (Business Persona)",
                            "value investing, insurance", "large")
    roster = discover_roster(tmp_path)
    assert roster[0].name == "Warren Buffett"          # title:, suffix stripped
    assert roster[0].slug == "WarrenBuffett"
    assert "value investing" in roster[0].description  # synthesized from industry:
    assert "large" in roster[0].description            # scale folded in


def test_name_frontmatter_still_wins_when_present(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\nname: al\ndescription: d\n---\n", encoding="utf-8")
    roster = discover_roster(tmp_path)
    assert roster[0].name == "al" and roster[0].description == "d"
