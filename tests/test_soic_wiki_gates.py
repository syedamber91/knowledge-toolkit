from soic_method.models import LessonRecord
from soic_wiki.gates import (
    FLAG_HAPAX,
    FLAG_INFLATED,
    candidate_terms,
    measure_term,
)


def _lesson(lid, body, summary="", eligible=True):
    return LessonRecord(lesson_id=lid, course_title="c", module_title="m",
                        title="t", url="u", body_text=body,
                        ai_summary=summary, eligible=eligible)


def test_term_in_many_lessons_is_clean():
    lessons = [_lesson(str(i), "he talks about the value chain a lot here")
               for i in range(6)]
    st = measure_term("value chain", lessons)
    assert st.lesson_n == 6
    assert st.flags == []
    assert st.suspect is False


def test_single_lesson_term_is_flagged_hapax():
    # The live failure: "diamond of profit pools" occurs in exactly one lesson.
    lessons = [_lesson("1", "as we saw in the lab ground diamond of profit pools ok"),
               _lesson("2", "unrelated content about margins")]
    st = measure_term("diamond of profit pools", lessons)
    assert st.lesson_n == 1
    assert FLAG_HAPAX in st.flags


def test_summary_inflated_term_is_flagged_even_across_two_lessons():
    # L2 catches what L1 misses: said a couple of times, but amplified by the
    # summarizer. Real terms invert this ratio hard.
    lessons = [
        _lesson("1", "niche chemistry matters", "niche chemistry niche chemistry"),
        _lesson("2", "more niche chemistry", "niche chemistry niche chemistry"),
    ]
    st = measure_term("niche chemistry", lessons)
    assert st.lesson_n == 2                 # passes L1
    assert st.summary_n >= st.body_n
    assert FLAG_INFLATED in st.flags        # caught by L2


def test_real_term_with_body_dominance_is_not_flagged_inflated():
    lessons = [_lesson(str(i), "right to win " * 8, "right to win") for i in range(5)]
    st = measure_term("right to win", lessons)
    assert st.body_n > st.summary_n
    assert st.flags == []


def test_ineligible_lessons_do_not_count_toward_evidence():
    # A guest lesson must not be able to legitimise a term.
    lessons = [_lesson("1", "special guest framework here", eligible=False),
               _lesson("2", "special guest framework here", eligible=False)]
    st = measure_term("special guest framework", lessons)
    assert st.lesson_n == 0
    assert FLAG_HAPAX in st.flags


def test_asr_variants_are_counted_as_the_same_term():
    # ROC is the ASR mangling of ROCE (961 vs 54 in the real corpus). Counting
    # only the correct spelling would make a real term look like a hapax.
    lessons = [_lesson("1", "we want roc above eighteen percent"),
               _lesson("2", "roce is the metric we care about")]
    st = measure_term("roce", lessons)
    assert st.lesson_n == 2
    assert FLAG_HAPAX not in st.flags


def test_stats_capture_a_raw_window_for_adjudication():
    # The adjudicator must see the ASR as spoken -- "lab ground" is what
    # explains the artifact, and normalising would hide it.
    lessons = [_lesson("1", "x" * 50 + " as we saw in the lab ground diamond of profit pools, you can also use")]
    st = measure_term("diamond of profit pools", lessons)
    assert "lab ground" in st.example_window
    assert st.example_lesson_id == "1"


def test_candidate_terms_picks_quoted_and_named_phrases():
    note = (
        'The source describes it via the metaphor of a "diamond of profit pools".\n'
        'It also introduces the right to win framework as a lens.\n'
        'Single words like "moat" should not be picked up.\n'
    )
    terms = candidate_terms(note)
    assert "diamond of profit pools" in terms
    assert "right to win" in terms
    assert "moat" not in terms        # single word, below the 2-word floor


def test_split_cited_quotes_partitions_on_nearby_citation():
    from soic_wiki.gates import split_cited_quotes
    note = ('He says "stock market is a weighing machine" (TURN 00:06:40).\n'
            'The "diamond of profit pools" framework is central.\n')
    parts = split_cited_quotes(note)
    assert parts["cited"] == ["stock market is a weighing machine|TURN"]
    assert parts["uncited"] == ["diamond of profit pools"]


def test_verify_cited_quotes_checks_presence_in_the_cited_lesson():
    from soic_wiki.gates import verify_cited_quotes
    lesson = _lesson("1", "[00:06:40] the stock market is a weighing machine ok")
    note = 'He says "stock market is a weighing machine" (TURN 00:06:40).'
    checks = verify_cited_quotes(note, {"TURN": lesson})
    assert len(checks) == 1 and checks[0].verified is True


def test_verify_cited_quotes_fails_a_quote_absent_from_the_cited_lesson():
    from soic_wiki.gates import verify_cited_quotes
    lesson = _lesson("1", "[00:06:40] entirely different content here")
    note = 'He says "stock market is a weighing machine" (TURN 00:06:40).'
    checks = verify_cited_quotes(note, {"TURN": lesson})
    assert checks[0].verified is False


def test_verify_cited_quotes_strips_bracketed_corrections():
    from soic_wiki.gates import verify_cited_quotes
    # The ASR says "Sammy hotels"; the note writes the mandated bracket form.
    lesson = _lesson("1", "[00:17:23] business by the name of Sammy hotels ok")
    note = 'The company "Sammy hotels [Samhi Hotels]" (TURN 00:17:23) is revealed.'
    checks = verify_cited_quotes(note, {"TURN": lesson})
    assert checks[0].verified is True


def test_citation_near_matches_timestamp_ranges():
    # The real bug this pins: range citations ("(REF HH:MM:SS-HH:MM:SS)")
    # are what the write-prompt citation headers actually produce
    # (ts_start-ts_end), and a regex that only matched single timestamps
    # silently mis-flagged correctly-cited quotes as uncited.
    from soic_wiki.gates import split_cited_quotes
    note = 'He says "the market corrects fast" (LGD 00:14:24-00:14:32).'
    parts = split_cited_quotes(note)
    assert parts["cited"] == ["the market corrects fast|LGD"]
    assert parts["uncited"] == []


def test_bracketed_gloss_after_a_range_citation_is_cited_by_the_same_citation():
    # The real LGD case: an English gloss immediately follows the cited
    # non-English quote, both covered by ONE range citation at the end.
    from soic_wiki.gates import split_cited_quotes
    note = ('Store staff said "unne 10 rings rakthi mom ke saamne" '
            '["they placed 10 rings in front of mom"] (LGD 00:14:24-00:14:32).')
    parts = split_cited_quotes(note)
    cited_phrases = [c.split("|")[0] for c in parts["cited"]]
    assert "unne 10 rings rakthi mom ke saamne" in cited_phrases
    assert "they placed 10 rings in front of mom" in cited_phrases
    assert parts["uncited"] == []
