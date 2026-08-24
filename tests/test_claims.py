import json
from pathlib import Path

import pytest

from soic_wiki.claims import (
    CLAIM_TYPES, Claim, load_claims, save_claims, verify_all, verify_claim)
from soic_wiki.ref_crosswalk import Resolver


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


# The FakeResolver above only supplies resolve()/window() -- exactly the
# interface Claim's verifier is documented to need. But Resolver.window() was
# deleted once as a "zero-caller" method and this module became its first
# real caller, so every test above would still pass green against a Resolver
# that has no window() at all. Only a genuine Resolver instance would catch
# that drift, so this test builds one against the real corpus instead of a
# fake.
REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"

needs_real = pytest.mark.skipif(
    not (REFS.exists() and CONTENT.exists()),
    reason="needs the local vault + corpus")


@needs_real
def test_verify_claim_against_the_real_resolver():
    """MASTEC 00:09:35 is a known-good, unambiguously-resolving (REF,
    timestamp) pair (see test_ref_crosswalk.py) whose real transcript window
    genuinely contains "more than 15% sales growth". An invented phrase over
    the same pair must fail -- that is the whole point of verification."""
    resolver = Resolver(REFS, CONTENT)
    genuine = _claim(
        claim_id="MASTEC-00:09:35-sales_growth", ref="MASTEC", ts="00:09:35",
        quote="more than 15% sales growth",
        statement="quarterly sales growth of at least 15%")
    assert verify_claim(genuine, resolver) is True

    invented = _claim(
        claim_id="MASTEC-00:09:35-invented", ref="MASTEC", ts="00:09:35",
        quote="the company will triple its revenue every single quarter",
        statement="a fabricated claim never made in this lecture")
    assert verify_claim(invented, resolver) is False
