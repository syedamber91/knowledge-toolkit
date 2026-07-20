from soic_method.models import Candidate, LessonRecord, Span
from soic_method.router import _merge_overlaps, find_candidates, route


def _lesson(body, eligible=True):
    return LessonRecord(
        lesson_id="1", course_title="c", module_title="m", title="t",
        url="u", body_text=body, eligible=eligible,
    )


def test_matches_asr_variant_roc_not_just_roce():
    # ROCE appears 54x in the corpus; ROC 961x. Missing ROC misses ~95%.
    cands = find_candidates(_lesson("[00:01:00] we want ROC above 18% consistently"))
    assert len(cands) == 1
    assert "roc" in cands[0].signals


def test_matches_asr_variant_pad_growth():
    cands = find_candidates(_lesson("[00:01:00] look for more than 15% pad growth here"))
    assert len(cands) == 1
    assert "pat" in cands[0].signals


def test_requires_both_a_metric_and_a_comparative_number():
    assert find_candidates(_lesson("[00:01:00] ROC is a useful concept")) == []
    assert find_candidates(_lesson("[00:01:00] more than 15% of people agree")) == []


def test_span_covers_a_context_window_around_the_hit():
    body = "x" * 500 + "[00:01:00] ROC above 18% " + "y" * 500
    cand = find_candidates(_lesson(body))[0]
    assert cand.span.start < 500
    assert cand.span.end > 520


def test_route_skips_ineligible_lessons():
    good = _lesson("[00:01:00] ROC above 18%", eligible=True)
    bad = _lesson("[00:01:00] ROC above 18%", eligible=False)
    assert len(route([good, bad])) == 1


def test_roc_word_boundary_rejects_substring_in_ferocious_and_rochit():
    # "ferocious" and "Rochit" both contain the raw substring "roc" but neither
    # is a genuine ROC/ROCE mention. Plain substring containment used to
    # false-positive on these (measured ~19% of real-corpus "roc" hits).
    # This body still satisfies the comparative+number gate ("above" + "18"),
    # so the only thing standing between it and a false candidate is
    # word-boundary matching on the metric term itself.
    body = ("[00:01:00] Rochit said the rally felt ferocious, "
            "prices moved above 18% today")
    assert find_candidates(_lesson(body)) == []


def test_roc_word_boundary_still_matches_genuine_usage_next_to_trap_words():
    # Same trap words present ("Rochit", "ferocious"), but a genuine standalone
    # "ROC" mention is also in range — it must still be caught.
    body = ("[00:01:00] Rochit noted it was a ferocious quarter, but ROC came in "
            "above 18% which is what matters")
    cands = find_candidates(_lesson(body))
    assert len(cands) == 1
    assert "roc" in cands[0].signals


def test_merge_overlaps_unions_signals_when_spans_overlap():
    a = Candidate(lesson_id="1", span=Span(start=0, end=100), signals=["roc"])
    b = Candidate(lesson_id="1", span=Span(start=50, end=150), signals=["pat"])
    merged = _merge_overlaps([a, b])
    assert len(merged) == 1
    assert merged[0].span.start == 0
    assert merged[0].span.end == 150
    assert set(merged[0].signals) == {"roc", "pat"}


def test_merge_overlaps_keeps_non_overlapping_candidates_separate():
    a = Candidate(lesson_id="1", span=Span(start=0, end=100), signals=["roc"])
    b = Candidate(lesson_id="1", span=Span(start=500, end=600), signals=["pat"])
    merged = _merge_overlaps([a, b])
    assert len(merged) == 2
    assert merged[0].signals == ["roc"]
    assert merged[1].signals == ["pat"]
