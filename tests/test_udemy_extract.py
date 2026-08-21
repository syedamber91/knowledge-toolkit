from pathlib import Path

from udemy_toolkit.extract import (
    captions_to_transcript,
    format_seconds,
    parse_cues,
)

FIXTURE = Path(__file__).parent / "fixtures" / "udemy" / "sample_captions.vtt"


def test_format_seconds():
    assert format_seconds(0) == "00:00:00"
    assert format_seconds(3723) == "01:02:03"


def test_parse_cues_reads_starts_strips_markup_and_drops_blanks():
    cues = parse_cues(FIXTURE.read_text(encoding="utf-8"))
    assert cues == [
        (1, "first line here"),
        (4, "second line here"),
        (3723, "much later line"),
    ]


def test_parse_cues_on_empty_input():
    assert parse_cues("") == []
    assert parse_cues("WEBVTT\n\n") == []


def test_transcript_groups_cues_into_timestamped_paragraphs():
    text = captions_to_transcript(FIXTURE.read_text(encoding="utf-8"))
    paragraphs = text.split("\n\n")
    assert paragraphs[0] == "[00:00:00] first line here second line here"
    assert paragraphs[1] == "[01:02:00] much later line"


def test_transcript_of_captionless_input_is_empty_string():
    assert captions_to_transcript("") == ""
