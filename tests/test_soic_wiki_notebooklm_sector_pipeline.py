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


# --- propose-concepts prompt building and parsing ---


def test_build_propose_prompt_lists_ref_codes_and_min_max():
    from soic_wiki.notebooklm_sector_pipeline import build_propose_prompt

    prompt = build_propose_prompt(
        module_title="Fluorine Industry", ref_codes=["FLUORA", "FLUORB", "FLUORC"], min_concepts=4, max_concepts=8
    )

    assert "Fluorine Industry" in prompt
    assert "FLUORA" in prompt and "FLUORB" in prompt and "FLUORC" in prompt
    assert "minimum of 4" in prompt
    assert "maximum of 8" in prompt


def test_parse_propose_response_extracts_title_scope_sources_timestamps():
    from soic_wiki.notebooklm_sector_pipeline import parse_propose_response

    response = """### The Sitting Duck Mental Model
Scope: Explains the sitting duck framework and China's fluorspar supply disruptions.
Sources: FLUORA, FLUORB
Timestamps: FLUORA [00:03:47]-[00:10:51], FLUORB [00:00:00]-[00:04:19]

### Fluorine Value Chain Segments
Scope: Details the value chain segments and backward integration.
Sources: FLUORB, FLUORC
Timestamps: FLUORB [00:04:50]-[00:10:29], FLUORC [00:02:43]-[00:05:45]
"""
    concepts = parse_propose_response(response)

    assert len(concepts) == 2
    assert concepts[0].title == "The Sitting Duck Mental Model"
    assert "sitting duck" in concepts[0].scope.lower()
    assert concepts[0].sources == ["FLUORA", "FLUORB"]
    assert "00:03:47" in concepts[0].timestamps

    assert concepts[1].title == "Fluorine Value Chain Segments"
    assert concepts[1].sources == ["FLUORB", "FLUORC"]


def test_parse_propose_response_returns_empty_list_for_unparseable_text():
    from soic_wiki.notebooklm_sector_pipeline import parse_propose_response

    concepts = parse_propose_response("Sorry, I don't understand the question.")

    assert concepts == []


def test_slugify_concept_title_produces_a_filesystem_safe_slug():
    from soic_wiki.notebooklm_sector_pipeline import slugify_concept_title

    assert slugify_concept_title("The Sitting Duck Mental Model") == "the-sitting-duck-mental-model"
    assert slugify_concept_title("SOTP (Sum of the Parts)!") == "sotp-sum-of-the-parts"


# --- write-concept prompt building ---


def test_build_write_prompt_states_the_exact_citation_format_once():
    from soic_wiki.notebooklm_sector_pipeline import ConceptProposal, build_write_prompt

    concept = ConceptProposal(
        title="The Sitting Duck Mental Model",
        scope="Explains the sitting duck framework.",
        sources=["FLUORA", "FLUORB"],
        timestamps="FLUORA [00:03:47]-[00:10:51]",
    )
    prompt = build_write_prompt(concept)

    assert "The Sitting Duck Mental Model" in prompt
    assert "## The mechanism" in prompt
    assert "## Why it matters" in prompt
    assert "## Caveats and limits" in prompt
    # Positive-only framing per this project's own "no forbidden-pattern
    # examples" lesson -- must never show the malformed "(FLUORA HH:MM:SS-
    # FLUORA HH:MM:SS)" pattern as a "don't do this" example.
    assert "FLUORA 00:" not in prompt.replace("HH:MM:SS", "")


# --- the two NotebookLM-calling wrappers ---


def test_propose_concepts_via_notebook_calls_ask_notebook_and_parses():
    from soic_wiki.notebooklm_sector_pipeline import propose_concepts_via_notebook

    fake_answer = (
        "### Concept One\nScope: some scope.\nSources: FLUORA\nTimestamps: FLUORA [00:00:00]-[00:01:00]\n"
    )
    with patch(
        "soic_wiki.notebooklm_sector_pipeline.ask_notebook",
        return_value={"answer": fake_answer, "conversation_id": "conv-1", "turn_number": 1},
    ) as mock_ask:
        concepts, conversation_id = propose_concepts_via_notebook(
            "nb-1", module_title="Fluorine Industry", ref_codes=["FLUORA"]
        )

    mock_ask.assert_called_once()
    assert mock_ask.call_args.args[0] == "nb-1"
    assert len(concepts) == 1
    assert concepts[0].title == "Concept One"
    assert conversation_id == "conv-1"


def test_write_concept_via_notebook_calls_ask_notebook_with_conversation_id():
    from soic_wiki.notebooklm_sector_pipeline import ConceptProposal, write_concept_via_notebook

    concept = ConceptProposal(
        title="Concept One", scope="scope", sources=["FLUORA"], timestamps="FLUORA [00:00:00]-[00:01:00]"
    )
    with patch(
        "soic_wiki.notebooklm_sector_pipeline.ask_notebook",
        return_value={"answer": "## The mechanism\n\nBody.", "conversation_id": "conv-1", "turn_number": 2},
    ) as mock_ask:
        note_text = write_concept_via_notebook("nb-1", concept, conversation_id="conv-1")

    mock_ask.assert_called_once_with("nb-1", mock_ask.call_args.args[1], conversation_id="conv-1", timeout=180.0)
    assert note_text == "## The mechanism\n\nBody."


# --- the master orchestrator ---


def test_run_sector_pipeline_wires_all_stages_together(tmp_path):
    from soic_wiki.notebooklm_sector_pipeline import ConceptProposal, run_sector_pipeline

    registry_path = tmp_path / "sector_notebooks.yaml"
    registry_path.write_text(yaml.safe_dump({"notebooks": {}}))

    lessons = [{"lesson_id": "111", "title": "Fluorine Part 1", "body_text": "raw transcript text"}]
    concepts = [
        ConceptProposal(title="Concept One", scope="s1", sources=["FLUOR"], timestamps="FLUOR [00:00:00]-[00:01:00]"),
        ConceptProposal(title="Concept Two", scope="s2", sources=["FLUOR"], timestamps="FLUOR [00:02:00]-[00:03:00]"),
    ]

    with patch(
        "soic_wiki.notebooklm_sector_pipeline.create_notebook", return_value="nb-1"
    ) as mock_create, patch(
        "soic_wiki.notebooklm_sector_pipeline.add_text_source"
    ) as mock_add, patch(
        "soic_wiki.notebooklm_sector_pipeline.propose_concepts_via_notebook",
        return_value=(concepts, "conv-1"),
    ) as mock_propose, patch(
        "soic_wiki.notebooklm_sector_pipeline.write_concept_via_notebook",
        side_effect=["## The mechanism\n\nNote one.", "## The mechanism\n\nNote two."],
    ) as mock_write:
        result = run_sector_pipeline(
            module_title="Fluorine Industry",
            slug="fluorine-industry",
            lessons=lessons,
            sector_registry_path=registry_path,
            existing_codes=set(),
        )

    mock_create.assert_called_once()
    assert mock_add.call_count == 1
    mock_propose.assert_called_once()
    assert mock_write.call_count == 2

    assert result.notebook_id == "nb-1"
    assert result.ref_codes == {"111": "FLUOR"}
    assert set(result.notes.keys()) == {"concept-one", "concept-two"}
    assert result.notes["concept-one"] == "## The mechanism\n\nNote one."


def test_run_sector_pipeline_reuses_existing_notebook_without_reseeding(tmp_path):
    """A re-run against an already-seeded sector must not re-create the
    notebook or re-upload sources -- only propose+write should re-fire."""
    from soic_wiki.notebooklm_sector_pipeline import run_sector_pipeline

    registry_path = tmp_path / "sector_notebooks.yaml"
    registry_path.write_text(
        yaml.safe_dump({"notebooks": {"fluorine-industry": {"notebook_id": "nb-existing", "title": "x"}}})
    )

    lessons = [{"lesson_id": "111", "title": "Fluorine Part 1", "body_text": "raw transcript text"}]

    with patch("soic_wiki.notebooklm_sector_pipeline.create_notebook") as mock_create, patch(
        "soic_wiki.notebooklm_sector_pipeline.add_text_source"
    ) as mock_add, patch(
        "soic_wiki.notebooklm_sector_pipeline.propose_concepts_via_notebook", return_value=([], "conv-1")
    ):
        result = run_sector_pipeline(
            module_title="Fluorine Industry",
            slug="fluorine-industry",
            lessons=lessons,
            sector_registry_path=registry_path,
            existing_codes=set(),
            reseed=False,
        )

    mock_create.assert_not_called()
    mock_add.assert_not_called()
    assert result.notebook_id == "nb-existing"
