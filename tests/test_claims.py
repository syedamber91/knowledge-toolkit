import json
from pathlib import Path

import pytest

from soic_wiki.claims import (
    CLAIM_TYPES, Claim, load_claims, save_claims, verify_all, verify_claim)


def _claim(**kw):
    base = dict(claim_id="FESTF-00:09:35-sales_growth", kind="threshold",
                ref="FESTF", ts="00:09:35", quote="more than 15% sales growth",
                statement="quarterly sales growth of at least 15%",
                metric="sales_growth_yoy_pct", bound=">= 15",
                scopes=[], source_brief="crash/FESTF.md")
    base.update(kw)
    return Claim(**base)


class FakeResolver:
    """Stands in for the real (REF, timestamp) resolver."""
    def __init__(self, text="he said more than 15% sales growth here"):
        self._text = text
    def resolve(self, ref, ts):
        return object() if ref == "FESTF" else None
    def window(self, ref, start, end=None):
        return self._text if ref == "FESTF" else ""


def test_the_six_claim_types_are_fixed():
    assert CLAIM_TYPES == ("threshold", "scope", "mechanism",
                           "disqualifier", "procedure", "worked_example")


def test_an_unknown_kind_is_rejected():
    with pytest.raises(ValueError):
        _claim(kind="vibes")


def test_a_worked_example_may_not_carry_a_bound():
    """A one-off illustration must never be usable as a rule. Making it a
    validation error means it cannot be promoted by accident."""
    with pytest.raises(ValueError):
        _claim(kind="worked_example", bound=">= 15")


def test_a_threshold_needs_a_metric_and_a_bound():
    with pytest.raises(ValueError):
        _claim(kind="threshold", metric=None)


def test_a_scope_claim_needs_no_bound():
    assert _claim(kind="scope", metric=None, bound=None).kind == "scope"


def test_verify_claim_passes_when_the_quote_is_in_the_cited_window():
    assert verify_claim(_claim(), FakeResolver()) is True


def test_verify_claim_fails_when_the_quote_is_absent():
    assert verify_claim(_claim(), FakeResolver("something else entirely")) is False


def test_verify_claim_fails_when_the_ref_does_not_resolve():
    assert verify_claim(_claim(ref="NOPE"), FakeResolver()) is False


def test_verify_claim_ignores_whitespace_and_case():
    c = _claim(quote="MORE   THAN 15%\nSALES GROWTH")
    assert verify_claim(c, FakeResolver()) is True


def test_verify_all_reports_per_claim():
    good, bad = _claim(), _claim(claim_id="x", quote="never said this")
    out = verify_all([good, bad], FakeResolver())
    assert out[good.claim_id] is True
    assert out["x"] is False


def test_round_trip_through_json(tmp_path: Path):
    path = tmp_path / "claims.json"
    save_claims(path, [_claim()])
    back = load_claims(path)
    assert len(back) == 1
    assert back[0].claim_id == _claim().claim_id
    assert json.loads(path.read_text())[0]["kind"] == "threshold"
