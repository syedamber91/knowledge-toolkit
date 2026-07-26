from pathlib import Path

FRAMEWORKS_FIXTURE = Path(__file__).parent / "fixtures" / "frameworks_sample.md"


def test_build_framework_evolution_prompt_lists_existing_framework_ids_and_titles():
    from soic_senses.framework_router import load_frameworks
    from soic_wiki.framework_evolution import build_framework_evolution_prompt

    frameworks = load_frameworks(FRAMEWORKS_FIXTURE)
    prompt = build_framework_evolution_prompt("Fluorine Industry", frameworks)

    assert "F1" in prompt
    assert "Working-capital re-rating" in prompt
    assert "F10" in prompt
    assert "DCF sanity" in prompt
    assert "Fluorine Industry" in prompt


def test_parse_framework_response_extracts_a_new_framework_block():
    from soic_wiki.framework_evolution import parse_framework_response

    response = """### NEW FRAMEWORK
## FNEW. Vendor-approval moat (specialty chemistry) model

**Model.** Long customer-audit cycles create a tiny approved-vendor pool.

**Applies when.** Specialty/fine chemicals with regulated end customers.

**Ask.** How many approved competitors exist per customer?

**Live data.** Customer concentration (annual report).

**Grounding.** Fluorine Industry sector notes.
"""
    proposal = parse_framework_response(response)

    assert len(proposal.new_frameworks) == 1
    assert proposal.new_frameworks[0].title == "Vendor-approval moat (specialty chemistry) model"
    assert "tiny approved-vendor pool" in proposal.new_frameworks[0].body
    assert proposal.reinforcements == []


def test_parse_framework_response_extracts_a_reinforcement():
    from soic_wiki.framework_evolution import parse_framework_response

    response = """### REINFORCES F2
Navin Fluorine's Manchester Organics acquisition is another example of the
vendor-approval moat: customer audit cycles of 2-4 years limit the approved
pool to 3-5 players (FLUORB 00:14:22-00:19:47).
"""
    proposal = parse_framework_response(response)

    assert proposal.new_frameworks == []
    assert len(proposal.reinforcements) == 1
    fid, addition = proposal.reinforcements[0]
    assert fid == "F2"
    assert "Manchester Organics" in addition


def test_parse_framework_response_handles_multiple_blocks():
    from soic_wiki.framework_evolution import parse_framework_response

    response = """### REINFORCES F1
Some grounding addition for F1.

### NEW FRAMEWORK
## FNEW. Some New Mechanism

**Model.** Body text here.

**Grounding.** Some sector.
"""
    proposal = parse_framework_response(response)

    assert len(proposal.reinforcements) == 1
    assert len(proposal.new_frameworks) == 1


def test_assign_next_framework_numbers_uses_max_existing_plus_one():
    from soic_senses.framework_router import load_frameworks
    from soic_wiki.framework_evolution import assign_next_framework_numbers, parse_framework_response

    existing = load_frameworks(FRAMEWORKS_FIXTURE)  # F1, F2, F10 -> max is 10
    response = """### NEW FRAMEWORK
## FNEW. First New One

**Model.** Body A.

### NEW FRAMEWORK
## FNEW. Second New One

**Model.** Body B.
"""
    proposal = parse_framework_response(response)
    numbered = assign_next_framework_numbers(proposal, existing)

    assert [fw.id for fw in numbered.new_frameworks] == ["F11", "F12"]


def test_render_proposed_diff_never_writes_to_the_frameworks_file(tmp_path):
    from soic_senses.framework_router import load_frameworks
    from soic_wiki.framework_evolution import (
        assign_next_framework_numbers,
        parse_framework_response,
        render_proposed_diff,
    )

    fixture_copy = tmp_path / "frameworks.md"
    fixture_copy.write_text(FRAMEWORKS_FIXTURE.read_text())
    original_content = fixture_copy.read_text()

    existing = load_frameworks(fixture_copy)
    response = """### NEW FRAMEWORK
## FNEW. Some New Mechanism

**Model.** Body text.
"""
    proposal = parse_framework_response(response)
    numbered = assign_next_framework_numbers(proposal, existing)

    diff = render_proposed_diff(existing, numbered)

    assert "F11" in diff
    assert "Some New Mechanism" in diff
    # The function must be read-only -- no write ever happens without an
    # explicit, separate human-approved step.
    assert fixture_copy.read_text() == original_content
