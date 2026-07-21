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
