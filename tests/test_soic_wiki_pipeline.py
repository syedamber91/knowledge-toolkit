import json

from soic_method.models import LessonRecord
from soic_wiki.pipeline import (
    Beat,
    WriteJob,
    build_write_prompt,
    map_lesson,
    write_note,
)

BODY = (
    "[00:00:05] intro padding here for a while.\n"
    "[00:17:21] What is the value hidden into the business we are studying?\n"
    "[00:17:39] EBITDA run rate of 606 crores in two years.\n"
    "[00:19:07] moving on to the next section now.\n"
)


def _lesson():
    return LessonRecord(lesson_id="3638545", course_title="c", module_title="m",
                        title="Spotting Turnarounds IAS 2024", url="u",
                        body_text=BODY, eligible=True)


def _llm_beats(beats):
    return lambda p: json.dumps({"beats": beats})


def test_map_resolves_offsets_to_timestamps():
    s = BODY.index("What is the value")
    e = BODY.index("moving on")
    beats = map_lesson(_lesson(), _llm_beats([{
        "gist": "worked valuation", "kind": "worked_example",
        "char_start": s, "char_end": e, "has_numbers": True,
    }]))
    assert len(beats) == 1
    assert beats[0].ts_start == "00:17:21"
    # end-1 (179) sits past the [00:19:07] marker at 169, so the nearest
    # PRECEDING marker for the span's end is 00:19:07, not 00:17:39.
    assert beats[0].ts_end == "00:19:07"


def test_map_drops_out_of_range_and_unknown_kinds():
    beats = map_lesson(_lesson(), _llm_beats([
        {"gist": "bad", "kind": "worked_example", "char_start": 5, "char_end": 99999},
        {"gist": "bad", "kind": "not_a_kind", "char_start": 5, "char_end": 30},
        "not a dict",
    ]))
    assert beats == []


def test_map_tolerates_malformed_llm_output():
    assert map_lesson(_lesson(), lambda p: "garbage") == []
    assert map_lesson(_lesson(), lambda p: json.dumps({"beats": 3})) == []


def test_write_prompt_contains_raw_slice_and_citation_header():
    s = BODY.index("[00:17:21]")
    e = BODY.index("moving on")
    job = WriteJob(concept_title="Practical valuation", concept_scope="how he values",
                   slug="practical-valuation-approach",
                   beats=[Beat(lesson_id="3638545", gist="SELECTION-ONLY-TEXT",
                               kind="worked_example", char_start=s, char_end=e,
                               ts_start="00:17:21", ts_end="00:17:39")],
                   refs={"3638545": "TURN"})
    prompt = build_write_prompt(job, {"3638545": _lesson()})
    assert "EBITDA run rate of 606 crores" in prompt          # raw slice present
    assert "=== TURN 00:17:21-00:17:39 (Spotting Turnarounds IAS 2024) ===" in prompt


def test_write_prompt_never_contains_beat_gist():
    # THE structural rule: beat prose is selection metadata, and letting it
    # into the write prompt would recreate the summaries-feeding-synthesis
    # failure this rebuild exists to fix.
    s = BODY.index("[00:17:21]")
    job = WriteJob(concept_title="t", concept_scope="s", slug="x",
                   beats=[Beat(lesson_id="3638545", gist="UNIQUE-GIST-MARKER-XYZ",
                               kind="heuristic", char_start=s, char_end=s + 40)],
                   refs={"3638545": "TURN"})
    prompt = build_write_prompt(job, {"3638545": _lesson()})
    assert "UNIQUE-GIST-MARKER-XYZ" not in prompt


def test_write_note_returns_none_on_empty_output():
    job = WriteJob(concept_title="t", concept_scope="s", slug="x", beats=[])
    assert write_note(job, {}, lambda p: "   ") is None
    assert write_note(job, {}, lambda p: "## note body") == "## note body"
