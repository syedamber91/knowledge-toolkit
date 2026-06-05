from soic_toolkit import vault
from soic_toolkit.models import Catalog, Course, Lesson, Module


def _catalog():
    return Catalog(
        base_url="https://learn.soic.in",
        courses=[
            Course(
                title="Valuation",
                url="https://learn.soic.in/learn/valuation",
                modules=[
                    Module(
                        title="Fundamentals",
                        lessons=[
                            Lesson(
                                title="Intrinsic Value",
                                url="https://learn.soic.in/l1",
                                body_text="Intrinsic value reflects discounted future cash flows.",
                                key_points=["Discounted cash flow", "Margin of safety"],
                            ),
                            Lesson(
                                title="Discounted Cash Flow",
                                url="https://learn.soic.in/l2",
                                body_text="DCF discounts future cash flows to estimate intrinsic value.",
                                key_points=["Project cash flows", "Discount rate"],
                            ),
                        ],
                    )
                ],
            )
        ],
    )


def test_build_vault_writes_notes_and_mocs(tmp_path, monkeypatch):
    monkeypatch.setattr(vault, "VAULT_DIR", tmp_path)
    vault.build_vault(_catalog())

    files = {p.name for p in tmp_path.rglob("*.md")}
    assert "intrinsic-value.md" in files
    assert "discounted-cash-flow.md" in files
    assert "Home.md" in files
    assert any(name.endswith("-moc.md") for name in files)


def test_notes_have_frontmatter_and_links(tmp_path, monkeypatch):
    monkeypatch.setattr(vault, "VAULT_DIR", tmp_path)
    vault.build_vault(_catalog())

    note = (tmp_path / "valuation" / "fundamentals" / "intrinsic-value.md").read_text()
    assert note.startswith("---")
    assert 'title: "Intrinsic Value"' in note
    assert "source_url: https://learn.soic.in/l1" in note
    # Structural link up to the module MOC.
    assert "[[fundamentals-moc|Fundamentals]]" in note
    # Sequential link to the next lesson.
    assert "[[discounted-cash-flow|Next →]]" in note
    # Content-based relation (the two lessons share cash-flow keywords).
    assert "[[discounted-cash-flow]]" in note


def test_vault_dir_override_writes_to_custom_path(tmp_path):
    # Simulates pointing at a folder inside an existing Obsidian vault.
    target = tmp_path / "MyObsidianVault" / "SOIC"
    returned = vault.build_vault(_catalog(), vault_dir=target)
    assert returned == target
    assert (target / "Home.md").exists()
    assert (target / "valuation" / "fundamentals" / "intrinsic-value.md").exists()


def test_slugify():
    assert vault.slugify("Intrinsic Value!") == "intrinsic-value"
    assert vault.slugify("  A/B  Test ") == "ab-test"
