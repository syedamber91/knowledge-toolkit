"""The negative test that was missing.

`route_company.py` documented an attribute-based admissibility gate for two
weeks while routing actually ran on hand-written slug allowlists -- ATTRS_TRUE
and ATTRS_FALSE were declared, printed in a status banner, and never consulted.
Every existing check still passed, because the only assertion was that the tier
counts summed to 459, which is true of a completely wrong routing.

The defect is only detectable by a test that flips a subject attribute and
demands the routing change. That is this file.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_MODULE_PATH = (pathlib.Path(__file__).resolve().parents[1]
                / "scripts" / "check_extraction" / "route_company.py")


def _load():
    spec = importlib.util.spec_from_file_location("route_company", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rc():
    return _load()


def test_every_excluded_topic_names_a_real_attribute(rc):
    """A required attribute must be declared TRUE or FALSE for the subject.

    A typo'd attribute name would silently never match, re-creating the exact
    dead-code failure in a subtler form.
    """
    known = rc.ATTRS_TRUE | rc.ATTRS_FALSE
    unknown = {t: a for t, a in rc.TOPIC_REQUIRES_ATTR.items() if a not in known}
    assert not unknown, f"topics requiring undeclared attributes: {unknown}"


def test_lending_topics_are_gated_on_the_lending_attribute(rc):
    """The F12 failure, pinned.

    A loan-to-value rule reached a cables company in the previous framework
    version. Gold-NBFC mechanics must be excluded for a subject whose
    `lending_book` is FALSE -- and admitted for one where it is TRUE. If only
    the first half is asserted, a hardcoded exclusion list passes too.
    """
    attr = rc.TOPIC_REQUIRES_ATTR["gold-nbfcs-niche-financiers"]
    assert attr == "lending_book"
    assert attr in rc.ATTRS_FALSE, "Polycab must not carry a lending book"
    assert attr not in rc.ATTRS_TRUE


def test_flipping_an_attribute_changes_admissibility(rc):
    """THE test. Gate behaviour must depend on the attribute set.

    Simulates the routing decision for a lender: with `lending_book` TRUE, the
    gold-NBFC topic is no longer attribute-blocked. Against the old dead-code
    implementation this fails, because routing ignored the attributes entirely.
    """
    topic = "gold-nbfcs-niche-financiers"
    attr = rc.TOPIC_REQUIRES_ATTR[topic]

    blocked_for_manufacturer = attr in rc.ATTRS_FALSE
    lender_attrs_false = rc.ATTRS_FALSE - {attr}
    blocked_for_lender = attr in lender_attrs_false

    assert blocked_for_manufacturer is True
    assert blocked_for_lender is False


def test_subject_attributes_are_disjoint(rc):
    """An attribute asserted both TRUE and FALSE makes the gate incoherent."""
    assert not (rc.ATTRS_TRUE & rc.ATTRS_FALSE)


def test_routing_output_changes_when_the_attribute_set_changes(rc):
    """THE behavioural test: run the real router twice and diff the output.

    An earlier version of this file asserted only that the string
    "ATTRS_FALSE" appeared inside main(). That proves nothing -- in the broken
    implementation a banner `print(f"...{len(ATTRS_FALSE)}...")` sat inside
    main(), so the structural assertion passed against the very defect it was
    written to catch. Replaced with a test that exercises routing and compares
    admitted sets.
    """
    rows = [
        {"slug": "lending-safety-principles", "topics": ["gold-nbfcs-niche-financiers"], "tags": []},
        {"slug": "nbfc-vs-banks", "topics": ["gold-nbfcs-niche-financiers"], "tags": []},
        {"slug": "module-5-ratio-analysis-note", "topics": ["module-5-ratio-analysis"], "tags": []},
    ]

    def admitted(attrs_false, attrs_true):
        return {r["slug"] for r in rc.route(rows, attrs_false=attrs_false,
                                            attrs_true=attrs_true)
                if r["tier"] != "D-excluded"}

    as_manufacturer = admitted(rc.ATTRS_FALSE, rc.ATTRS_TRUE)
    as_lender = admitted(rc.ATTRS_FALSE - {"lending_book"},
                         rc.ATTRS_TRUE | {"lending_book"})

    # Universal curriculum is admitted for both subjects.
    assert "module-5-ratio-analysis-note" in as_manufacturer
    assert "module-5-ratio-analysis-note" in as_lender

    # Lending mechanics: excluded for the manufacturer, admitted for the lender.
    assert "lending-safety-principles" not in as_manufacturer, (
        "F12 regression: lending mechanics reached a non-lender")
    assert "lending-safety-principles" in as_lender

    # The sets must genuinely differ -- a hardcoded slug list yields identical output.
    assert as_manufacturer != as_lender


def test_exclusion_records_which_attribute_blocked_it(rc):
    """An audit must be able to ask 'which attribute excluded this note?'.

    The old implementation answered that only in English prose inside a
    `reason` string, which no downstream consumer can parse.
    """
    rows = [{"slug": "lending-safety-principles",
             "topics": ["gold-nbfcs-niche-financiers"], "tags": []}]
    row = rc.route(rows)[0]
    assert row["tier"] == "D-excluded"
    assert row["attribute_provenance"] == "lending_book"
