from soic_method.models import LessonRecord
from soic_method.router import find_candidates, route


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
