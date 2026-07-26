from soic_method.models import LessonRecord
from soic_wiki.oracle import (
    OracleSpan,
    check_denials,
    extract_denials,
    parse_legend,
    parse_oracle_spans,
    resolve_line_range,
    span_recall,
)

LEGEND = """
- HMVC1 = `highly-moated-value-chains/part-1-highly-moated-value-chains-transcript.md`
- TURN = `spotting-turnarounds/spotting-turnarounds-ias-2024-transcript.md`
- P1 = part-1-value-chain-transcript.md
"""


def test_legend_maps_refs_to_lesson_slugs():
    leg = parse_legend(LEGEND)
    assert leg["TURN"] == "spotting-turnarounds-ias-2024"
    assert leg["HMVC1"] == "part-1-highly-moated-value-chains"
    assert leg["P1"] == "part-1-value-chain"


def _lesson(body):
    return LessonRecord(lesson_id="1", course_title="c", module_title="m",
                        title="Spotting Turnarounds IAS 2024", url="u",
                        body_text=body, eligible=True)


def test_line_range_accounts_for_the_vault_header_offset():
    # A vault transcript file is header + body; enrichment cites VAULT lines.
    # Verified empirically against the real corpus: (TURN L165-183) lands on
    # the [00:17:21] worked valuation.
    body = "\n".join("[00:%02d:00] line %d" % (i, i) for i in range(40))
    span = resolve_line_range(_lesson(body), 20, 24)
    assert span is not None
    # vault line 20 -> body line index 20-14-1 = 5
    assert "line 5" in body[span.start:span.end]
    assert "line 8" in body[span.start:span.end]
    assert span.ts_start == "00:05:00"


def test_line_range_out_of_bounds_returns_none():
    assert resolve_line_range(_lesson("[00:00:01] only one line"), 900, 950) is None


def test_extract_denials_pulls_the_quoted_phrase():
    text = ('He never uses the literal phrase "diamond of profit pools" '
            "(that's Mauboussin terminology).")
    dn = extract_denials(text, "enrichment_valuechain.md")
    assert len(dn) == 1
    assert dn[0].phrases == ["diamond of profit pools"]


def test_denial_check_flags_a_note_asserting_a_denied_phrase():
    dn = extract_denials(
        'He never uses the literal phrase "diamond of profit pools" here.', "f.md")
    notes = {
        "profit-pool-margin-analysis":
            "described via the metaphor of a 'diamond of profit pools'",
        "innocent-note": "discusses margins by node",
    }
    v = check_denials(notes, dn)
    assert len(v) == 1
    assert v[0].note_slug == "profit-pool-margin-analysis"


def test_denial_check_is_case_insensitive():
    dn = extract_denials('He never uses the phrase "Right To Win" ever.', "f.md")
    v = check_denials({"n": "the right to win idea"}, dn)
    assert len(v) == 1


def _span(lid, a, b):
    return OracleSpan(ref="X", lesson_id=lid, lesson_title="t", start=a, end=b,
                      ts_start="00:00:00", ts_end="00:00:01", kind="line_range")


def test_span_recall_counts_overlap_not_exact_match():
    oracle = [_span("1", 100, 200)]
    assert span_recall(oracle, [_span("1", 150, 300)]) == 1.0   # overlaps
    assert span_recall(oracle, [_span("1", 300, 400)]) == 0.0   # disjoint
    assert span_recall(oracle, [_span("2", 100, 200)]) == 0.0   # wrong lesson


def test_span_recall_of_a_wiki_that_cites_no_spans_is_zero():
    # The current wiki's notes carry only file-level `sources:` -- no spans at
    # all. Its oracle recall is therefore 0 by construction, which is the
    # baseline the rebuild has to beat.
    assert span_recall([_span("1", 0, 10), _span("1", 20, 30)], []) == 0.0


def test_parse_oracle_spans_skips_refs_with_no_matching_lesson():
    leg = {"ZZZ": "no-such-lesson"}
    assert parse_oracle_spans("(ZZZ L10-20)", leg, {}) == []
