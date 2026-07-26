import yaml
from unittest.mock import patch


def test_assign_ref_codes_derives_mnemonic_from_module_title():
    from soic_wiki.notebooklm_sector_pipeline import assign_ref_codes

    lessons = [{"lesson_id": "111", "title": "Fluorine chemistry overview"}]
    codes = assign_ref_codes(lessons, module_title="Fluorine Industry", existing_codes=set())

    assert codes == {"111": "FLUOR"}


def test_assign_ref_codes_suffixes_multi_lesson_modules_a_b_c():
    from soic_wiki.notebooklm_sector_pipeline import assign_ref_codes

    lessons = [
        {"lesson_id": "111", "title": "Part 1"},
        {"lesson_id": "222", "title": "Part 2"},
        {"lesson_id": "333", "title": "Part 3"},
    ]
    codes = assign_ref_codes(lessons, module_title="Fluorine Industry", existing_codes=set())

    assert codes == {"111": "FLUORA", "222": "FLUORB", "333": "FLUORC"}


def test_assign_ref_codes_avoids_collision_with_existing_codes():
    from soic_wiki.notebooklm_sector_pipeline import assign_ref_codes

    lessons = [{"lesson_id": "111", "title": "Real estate part 2"}]
    codes = assign_ref_codes(lessons, module_title="Real Estate", existing_codes={"REAL"})

    assert codes == {"111": "REAL2"}


def test_ensure_sector_notebook_reuses_existing_entry_without_creating(tmp_path):
    from soic_wiki.notebooklm_sector_pipeline import ensure_sector_notebook

    registry_path = tmp_path / "sector_notebooks.yaml"
    registry_path.write_text(
        yaml.safe_dump(
            {"notebooks": {"fluorine-industry": {"notebook_id": "existing-id", "title": "Fluorine Industry"}}}
        )
    )

    with patch("soic_wiki.notebooklm_sector_pipeline.create_notebook") as mock_create:
        notebook_id = ensure_sector_notebook(
            slug="fluorine-industry", title="Fluorine Industry", registry_path=registry_path
        )

    mock_create.assert_not_called()
    assert notebook_id == "existing-id"


def test_ensure_sector_notebook_creates_and_persists_new_entry(tmp_path):
    from soic_wiki.notebooklm_sector_pipeline import ensure_sector_notebook

    registry_path = tmp_path / "sector_notebooks.yaml"
    registry_path.write_text(yaml.safe_dump({"notebooks": {}}))

    with patch("soic_wiki.notebooklm_sector_pipeline.create_notebook", return_value="new-id") as mock_create:
        notebook_id = ensure_sector_notebook(
            slug="fluorine-industry", title="SOIC L6 -- Fluorine Industry", registry_path=registry_path
        )

    mock_create.assert_called_once_with(title="SOIC L6 -- Fluorine Industry")
    assert notebook_id == "new-id"

    data = yaml.safe_load(registry_path.read_text())
    assert data["notebooks"]["fluorine-industry"]["notebook_id"] == "new-id"
    assert data["notebooks"]["fluorine-industry"]["title"] == "SOIC L6 -- Fluorine Industry"


def test_seed_sector_sources_calls_add_text_source_per_lesson():
    from soic_wiki.notebooklm_sector_pipeline import seed_sector_sources

    lessons_with_codes = [
        {"lesson_id": "111", "ref_code": "FLUORA", "title": "Part 1", "body_text": "text one"},
        {"lesson_id": "222", "ref_code": "FLUORB", "title": "Part 2", "body_text": "text two"},
    ]

    with patch("soic_wiki.notebooklm_sector_pipeline.add_text_source") as mock_add:
        seed_sector_sources("nb-1", lessons_with_codes)

    assert mock_add.call_count == 2
    mock_add.assert_any_call("nb-1", "text one", title="FLUORA Part 1")
    mock_add.assert_any_call("nb-1", "text two", title="FLUORB Part 2")
