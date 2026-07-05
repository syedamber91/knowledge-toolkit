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


# --- ingestion log (index + log + cross-links routing pattern) ---------------

def test_log_created_on_first_build_backfills_without_claiming_new(tmp_path):
    out = tmp_path / "Obsidian Vault"
    vault.build_vault(_catalog(), vault_dir=out)

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 1        # exactly one entry
    # First-ever entry backfills pre-existing content — must not claim it was
    # "just captured" when it wasn't.
    assert "2 item(s) already in vault (log started here) (2 total: 2 lesson notes)" in log
    assert "[[Log|Ingestion Log]]" in (out / "Home.md").read_text()


def test_log_appends_new_entry_when_items_added(tmp_path):
    out = tmp_path / "Obsidian Vault"
    vault.build_vault(_catalog(), vault_dir=out)

    grown = _catalog()
    grown.courses[0].modules[0].lessons.append(
        Lesson(
            title="Margin of Safety",
            url="https://learn.soic.in/l3",
            body_text="Margin of safety protects against valuation error.",
            key_points=["Buy below intrinsic value"],
        )
    )
    vault.build_vault(grown, vault_dir=out)

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 2        # first entry preserved, second appended
    assert "1 new item(s) captured (3 total: 3 lesson notes)" in log


def test_log_skips_entry_when_no_new_items(tmp_path):
    out = tmp_path / "Obsidian Vault"
    vault.build_vault(_catalog(), vault_dir=out)
    vault.build_vault(_catalog(), vault_dir=out)  # identical rebuild

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 1        # no duplicate entry for an unchanged rebuild


def test_log_records_removed_items(tmp_path):
    out = tmp_path / "Obsidian Vault"
    vault.build_vault(_catalog(), vault_dir=out)

    shrunk = _catalog()
    shrunk.courses[0].modules[0].lessons.pop()  # drop one lesson

    vault.build_vault(shrunk, vault_dir=out)

    log = (out / "Log.md").read_text()
    assert log.count("\n- **") == 2
    assert "1 item(s) removed (1 total: 1 lesson notes)" in log
