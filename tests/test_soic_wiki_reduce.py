import json

from soic_wiki.pipeline import Beat
from soic_wiki.reduce import build_reduce_prompt, reduce_beats


def _beat(i, lesson="L1"):
    return Beat(lesson_id=lesson, gist="gist %d" % i, kind="heuristic",
                char_start=i * 10, char_end=i * 10 + 9,
                ts_start="00:00:0%d" % (i % 10), ts_end="00:00:0%d" % (i % 10))


CONCEPTS = {"practical-valuation-approach": "how he values",
            "tvgp-framework": "the four-pillar lens"}


def test_prompt_lists_every_pinned_concept_and_indexed_beats():
    p = build_reduce_prompt(CONCEPTS, [_beat(0), _beat(1)], {"L1": "TURN"})
    assert "practical-valuation-approach" in p and "tvgp-framework" in p
    assert "0. [TURN" in p and "1. [TURN" in p


def test_reduce_parses_assignments_and_clamps_indices():
    llm = lambda p: json.dumps({"assignments": {
        "practical-valuation-approach": [0, 99, -3],
        "tvgp-framework": [],
    }, "unassigned": [1]})
    r = reduce_beats(CONCEPTS, [_beat(0), _beat(1)], {}, llm)
    assert r.assignments["practical-valuation-approach"] == [0]   # 99, -3 dropped
    assert r.assignments["tvgp-framework"] == []
    assert r.unassigned == [1]


def test_reduce_fills_missing_slugs_with_empty_lists():
    llm = lambda p: json.dumps({"assignments": {"tvgp-framework": [0]}})
    r = reduce_beats(CONCEPTS, [_beat(0)], {}, llm)
    assert r.assignments["practical-valuation-approach"] == []
    assert r.assignments["tvgp-framework"] == [0]


def test_reduce_tolerates_garbage():
    r = reduce_beats(CONCEPTS, [_beat(0)], {}, lambda p: "not json")
    assert r.assignments == {} and r.unassigned == []


from soic_wiki.reduce import build_propose_prompt, propose_concepts


def test_propose_prompt_includes_sector_title_and_all_beats():
    p = build_propose_prompt("Lab Grown Diamonds", [_beat(0), _beat(1)], {"L1": "LGD"})
    assert "Lab Grown Diamonds" in p
    assert "0. [LGD" in p and "1. [LGD" in p


def test_propose_parses_concepts_and_computes_unassigned():
    llm = lambda p: json.dumps({"concepts": [
        {"slug": "value-chain-and-key-players", "scope": "who does what",
         "beat_indices": [0]},
    ], "unassigned": [1]})
    r = propose_concepts("Lab Grown Diamonds", [_beat(0), _beat(1)], {}, llm)
    assert len(r.concepts) == 1
    assert r.concepts[0].slug == "value-chain-and-key-players"
    assert r.concepts[0].beat_indices == [0]
    assert r.unassigned == [1]


def test_propose_drops_malformed_slugs():
    llm = lambda p: json.dumps({"concepts": [
        {"slug": "Not Kebab Case!", "scope": "x", "beat_indices": [0]},
        {"slug": "valid-slug", "scope": "y", "beat_indices": [1]},
    ]})
    r = propose_concepts("S", [_beat(0), _beat(1)], {}, llm)
    slugs = [c.slug for c in r.concepts]
    assert "valid-slug" in slugs
    assert not any(" " in s or "!" in s for s in slugs)


def test_propose_drops_a_concept_with_no_real_evidence():
    llm = lambda p: json.dumps({"concepts": [
        {"slug": "empty-concept", "scope": "x", "beat_indices": []},
        {"slug": "empty-concept-2", "scope": "x", "beat_indices": [99]},  # OOB
    ]})
    r = propose_concepts("S", [_beat(0)], {}, llm)
    assert r.concepts == []


def test_propose_never_silently_drops_a_beat_missing_from_both_lists():
    # LLM forgets to list beat 1 anywhere -- it must still surface somewhere.
    llm = lambda p: json.dumps({"concepts": [
        {"slug": "a", "scope": "x", "beat_indices": [0]},
    ], "unassigned": []})
    r = propose_concepts("S", [_beat(0), _beat(1)], {}, llm)
    assert 1 in r.unassigned


def test_propose_deduplicates_repeated_slugs():
    llm = lambda p: json.dumps({"concepts": [
        {"slug": "dup", "scope": "first", "beat_indices": [0]},
        {"slug": "dup", "scope": "second", "beat_indices": [1]},
    ]})
    r = propose_concepts("S", [_beat(0), _beat(1)], {}, llm)
    assert len([c for c in r.concepts if c.slug == "dup"]) == 1


def test_propose_tolerates_garbage():
    r = propose_concepts("S", [_beat(0)], {}, lambda p: "not json")
    assert r.concepts == [] and r.unassigned == []
