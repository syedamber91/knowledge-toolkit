import json
from pathlib import Path

import yaml


def test_normalize_body_converts_leading_h1_to_h2():
    from soic_wiki.vault_sync import normalize_body

    text = "# Company Case Studies\n\n## The mechanism\n\nSome text."
    result = normalize_body(text, fallback_title="company case studies")

    assert result.startswith("## Company Case Studies\n")
    assert "# Company Case Studies\n\n##" not in result


def test_normalize_body_prepends_derived_title_when_no_h1():
    from soic_wiki.vault_sync import normalize_body

    text = "## The mechanism\n\nSome text about De Beers."
    result = normalize_body(text, fallback_title="de-beers-history-and-natural-diamond-cartel")

    assert result.startswith("## De Beers History And Natural Diamond Cartel\n")
    assert "## The mechanism" in result


def test_build_concept_frontmatter_contains_required_fields():
    from soic_wiki.vault_sync import build_concept_frontmatter

    fm = build_concept_frontmatter(
        slug="lgd-value-chain-and-industry-structure",
        module_title="Lab Grown Diamonds Sector Analysis",
        ref_code="LGD",
        sector_slug="lgd-sector-analysis",
        last_updated="2026-07-26",
    )
    parsed = yaml.safe_load(fm.strip("-\n").split("---")[0] if fm.startswith("---") else fm)

    assert parsed["persona"] == "soic"
    assert parsed["kind"] == "concept"
    assert parsed["slug"] == "lgd-value-chain-and-industry-structure"
    assert parsed["topics"] == ["lgd-sector-analysis"]
    assert parsed["qc"] == "passed"
    assert parsed["last_updated"] == "2026-07-26"
    assert "Lab Grown Diamonds Sector Analysis" in parsed["sources"][0]
    assert "LGD" in parsed["sources"][0]


def test_sync_sector_to_vault_writes_one_concept_file_per_note(tmp_path):
    from soic_wiki.vault_sync import sync_sector_to_vault

    notes_dir = tmp_path / "out" / "notes"
    notes_dir.mkdir(parents=True)
    (notes_dir / "concept-one.md").write_text("# Concept One\n\n## The mechanism\n\nBody one.")
    (notes_dir / "concept-two.md").write_text("## The mechanism\n\nBody two, no H1.")

    refs_path = tmp_path / "refs.json"
    refs_path.write_text(json.dumps({"1234567": "TST"}))

    vault_concepts_dir = tmp_path / "vault" / "concepts"
    vault_concepts_dir.mkdir(parents=True)

    written = sync_sector_to_vault(
        notes_dir=notes_dir,
        refs_json_path=refs_path,
        module_title="Test Sector Module",
        sector_slug="test-sector-module",
        vault_concepts_dir=vault_concepts_dir,
        last_updated="2026-07-26",
    )

    assert len(written) == 2
    concept_one = (vault_concepts_dir / "concept-one.md").read_text()
    assert concept_one.startswith("---\n")
    assert "## Concept One" in concept_one
    assert "Body one." in concept_one

    concept_two = (vault_concepts_dir / "concept-two.md").read_text()
    assert "## Concept Two" in concept_two
    assert "Body two, no H1." in concept_two


def test_sync_sector_to_vault_raises_on_slug_collision_unless_overwrite(tmp_path):
    from soic_wiki.vault_sync import sync_sector_to_vault, ConceptSlugCollisionError

    notes_dir = tmp_path / "out" / "notes"
    notes_dir.mkdir(parents=True)
    (notes_dir / "dupe.md").write_text("## The mechanism\n\nNew body.")

    refs_path = tmp_path / "refs.json"
    refs_path.write_text(json.dumps({"1234567": "TST"}))

    vault_concepts_dir = tmp_path / "vault" / "concepts"
    vault_concepts_dir.mkdir(parents=True)
    (vault_concepts_dir / "dupe.md").write_text("---\nslug: dupe\n---\n\nExisting body.")

    try:
        sync_sector_to_vault(
            notes_dir=notes_dir,
            refs_json_path=refs_path,
            module_title="Test Sector Module",
            sector_slug="test-sector-module",
            vault_concepts_dir=vault_concepts_dir,
            last_updated="2026-07-26",
        )
        assert False, "expected ConceptSlugCollisionError"
    except ConceptSlugCollisionError as exc:
        assert "dupe" in str(exc)

    # Existing file must be untouched
    assert "Existing body." in (vault_concepts_dir / "dupe.md").read_text()


def test_update_index_yaml_adds_topic_and_concepts(tmp_path):
    from soic_wiki.vault_sync import update_index_yaml

    index_path = tmp_path / "index.yaml"
    index_path.write_text(yaml.safe_dump({"topics": {}, "entities": {}, "concepts": {}}))

    update_index_yaml(
        index_path=index_path,
        sector_slug="test-sector-module",
        topic_file="topics/test-sector-module.md",
        concept_slugs=["concept-one", "concept-two"],
        last_updated="2026-07-26",
    )

    data = yaml.safe_load(index_path.read_text())
    assert data["topics"]["test-sector-module"]["file"] == "topics/test-sector-module.md"
    assert data["topics"]["test-sector-module"]["sources"] == 2
    assert data["concepts"]["concept-one"]["topics"] == ["test-sector-module"]
    assert data["concepts"]["concept-two"]["last_updated"] == "2026-07-26"


def test_build_topic_file_contains_related_links_and_frontmatter():
    from soic_wiki.vault_sync import build_topic_file

    content = build_topic_file(
        sector_slug="test-sector-module",
        module_title="Test Sector Module",
        concept_slugs=["concept-one", "concept-two"],
        last_updated="2026-07-26",
    )

    assert content.startswith("---\n")
    assert "topic: test-sector-module" in content
    assert "[[concept-one]]" in content
    assert "[[concept-two]]" in content
    assert "## Synthesis" in content
