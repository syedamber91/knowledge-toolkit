import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from learning_pack_wiki import (build_planner_prompt, load_topic, parse_json,
                                validate_plan)


def seed_wiki(tmp_path: Path) -> Path:
    root = tmp_path / "vutr"
    (root / "raw" / "kafka").mkdir(parents=True)
    (root / "raw" / "kafka" / "post-a.md").write_text("acks=all waits for ISR.", encoding="utf-8")
    (root / "concepts").mkdir()
    (root / "concepts" / "producer-batching.md").write_text(
        "---\npersona: vutr\nkind: concept\nslug: producer-batching\nsources:\n"
        "- raw/kafka/post-a.md\nlast_updated: '2026-07-10'\ntopics:\n- kafka\n---\n\n"
        "Producers batch per partition.", encoding="utf-8")
    (root / "topics").mkdir()
    (root / "topics" / "kafka.md").write_text(
        "---\npersona: vutr\nkind: topic\ntopic: kafka\nlast_updated: '2026-07-10'\n---\n\n"
        "Related: [[producer-batching]]\n\n## Synthesis\nKafka.", encoding="utf-8")
    return root


def test_load_topic(tmp_path):
    td = load_topic(seed_wiki(tmp_path), "kafka")
    assert td.topic == "kafka"
    assert list(td.concepts) == ["producer-batching"]
    assert td.sources["producer-batching"] == ["raw/kafka/post-a.md"]
    assert "acks=all" in td.raw_texts["raw/kafka/post-a.md"]
    assert "Synthesis" in td.topic_body


def test_validate_plan_flags_unmapped():
    plan = {"chapters": [{"title": "Ch1", "concepts": ["producer-batching"]}]}
    assert validate_plan(plan, ["producer-batching", "consumer-pull"]) == ["consumer-pull"]
    assert validate_plan(plan, ["producer-batching"]) == []


def test_planner_prompt_and_fence_parse():
    p = build_planner_prompt("kafka", {"producer-batching": "body"})
    assert "PLAN-CHAPTERS" in p and "producer-batching" in p
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


from learning_pack_wiki import build_writer_prompt, grounding_check, render_pack_html


def test_writer_prompt_closed_book():
    ch = {"title": "Producers", "concepts": ["producer-batching"]}
    p = build_writer_prompt(ch, {"producer-batching": "batch per partition"}, "acks=all")
    assert "WRITE-CHAPTER" in p and "closed-book" in p.lower() and "acks=all" in p


def test_grounding_check_flags_unsourced_numbers():
    sources = "The threshold is 10MB and the default is 200 partitions."
    ok_chapter = "<p>Default is 200 partitions; broadcast under 10MB.</p>"
    assert grounding_check(ok_chapter, sources) == []
    bad = "<p>A 2.6GB file inflates 1.42x in memory.</p>"
    flagged = grounding_check(bad, sources)
    assert "1.42" in "".join(flagged) and "2.6" in "".join(flagged)


def test_grounding_check_allows_beyond_box():
    sources = "nothing numeric"
    ch = '<div class="beyond">industry rule of thumb: 1.5x</div><p>plain text</p>'
    assert grounding_check(ch, sources) == []


def test_render_pack_html_structure():
    html = render_pack_html("Kafka Pack", [
        {"title": "Producers", "concepts": ["producer-batching"], "html": "<p>ch1</p>"}])
    assert "Kafka Pack" in html and "<p>ch1</p>" in html and "Producers" in html
