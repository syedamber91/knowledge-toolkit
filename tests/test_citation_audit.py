from pathlib import Path

import pytest

from soic_wiki.citation_audit import audit, parse_ref


def test_parse_ref_single_and_range():
    assert parse_ref("MASTEC 00:09:35") == ("MASTEC", "00:09:35", None)
    assert parse_ref("HOWB 00:01:55-00:02:23") == ("HOWB", "00:01:55", "00:02:23")
    assert parse_ref(None) == (None, None, None)
    assert parse_ref("") == (None, None, None)


class FakeResolver:
    """Mirrors the real soic_wiki.ref_crosswalk.Resolver interface, which
    resolves by the (ref, timestamp) PAIR, not by ref alone -- 25/221 real
    REF codes are ambiguous (map to >1 lesson), so there is no `lesson(ref)`
    method. `resolve()` returns None both when a code has zero candidates
    AND when it has candidates but none contain the timestamp; `audit()`
    must tell those two cases apart via `candidates()`/`ambiguity()`, not
    via `resolve()` alone.
    """

    def candidates(self, ref):
        # GOOD: one real candidate. NOTS: one candidate that exists, but
        # doesn't contain the cited timestamp (a BAD_TIMESTAMP case).
        # MISSING: no candidates at all (a genuine UNRESOLVED_REF case).
        if ref == "GOOD":
            return [object()]
        if ref == "NOTS":
            return [object()]
        return []

    def ambiguity(self, ref):
        return len(self.candidates(ref))

    def resolve(self, ref, ts):
        return object() if ref == "GOOD" else None

    def title(self, ref, ts):
        return "A Real Lecture" if ref == "GOOD" else None

    def has_timestamp(self, ref, ts):
        return ref == "GOOD"

    def nearby_timestamps(self, ref, ts):
        return ["00:09:21", "00:09:39"] if ref == "NOTS" else []

    def window(self, ref, s, e=None):
        return "some transcript text" if ref == "GOOD" else ""


def test_audit_classifies_each_failure_mode(tmp_path: Path):
    rb = tmp_path / "rules.yaml"
    rb.write_text(
        "rules:\n"
        "  - id: good-001\n"
        "    provenance: {ref: 'GOOD 00:01:00', quote: q}\n"
        "  - id: badts-001\n"
        "    provenance: {ref: 'NOTS 00:09:35', quote: q}\n"
        "  - id: unres-001\n"
        "    provenance: {ref: 'MISSING 00:01:00', quote: q}\n"
        "observations:\n"
        "  - id: noref-001\n"
        "    provenance: {ref: null, quote: q}\n")
    checks = audit(rb, FakeResolver())
    got = {c.rule_id: c.status for c in checks}
    assert got == {"good-001": "OK", "badts-001": "BAD_TIMESTAMP",
                   "unres-001": "UNRESOLVED_REF", "noref-001": "NO_REF"}


def test_bad_timestamp_has_candidates_but_no_resolve(tmp_path: Path):
    """A code with >=1 candidate(s), none of which contain the cited
    timestamp, is BAD_TIMESTAMP -- distinct from UNRESOLVED_REF, which is
    reserved for a code with zero candidates at all."""
    rb = tmp_path / "rules.yaml"
    rb.write_text(
        "rules:\n"
        "  - id: badts-001\n"
        "    provenance: {ref: 'NOTS 00:09:35', quote: q}\n")
    c = audit(rb, FakeResolver())[0]
    assert c.status == "BAD_TIMESTAMP"
    assert c.nearby == ["00:09:21", "00:09:39"]


def test_unresolved_ref_has_zero_candidates(tmp_path: Path):
    rb = tmp_path / "rules.yaml"
    rb.write_text(
        "rules:\n"
        "  - id: unres-001\n"
        "    provenance: {ref: 'MISSING 00:01:00', quote: q}\n")
    c = audit(rb, FakeResolver())[0]
    assert c.status == "UNRESOLVED_REF"
    assert c.resolved is False


REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
RULEBOOK = Path.home() / (
    "Documents/workspace/Claude_Code/soic-ladder/rulebook/soic-ladder-rules-v1.yaml")

needs_real = pytest.mark.skipif(
    not (REFS.exists() and CONTENT.exists() and RULEBOOK.exists()),
    reason="needs the local vault, corpus and ladder checkout")


@needs_real
def test_known_citation_defects_are_still_reported():
    from soic_wiki.ref_crosswalk import Resolver
    by_id = {c.rule_id: c for c in audit(RULEBOOK, Resolver(REFS, CONTENT))}
    assert by_id["pe_context-001"].status == "NO_REF"
    # G0's MASTEC 00:09:35 IS sound: MASTEC is one of 25 ambiguous REF codes,
    # and the candidate containing 00:09:35 is "15.12.24 Class 4 How to Filter
    # Epic Stocks", where that timestamp carries the 15%/20% sentence verbatim.
    # An earlier last-wins loader picked the other candidate and reported a
    # false defect. Ambiguity must be resolved by (REF, timestamp), never by
    # REF alone.
    assert by_id["canslim_sales-001"].status == "OK"
    assert by_id["canslim_pat-001"].status == "OK"


@needs_real
def test_growth_trap_citation_is_sound():
    """Regression on OUR error, not the rulebook's: this citation was reported
    broken twice because TVGPF was resolved by guessing at its name."""
    from soic_wiki.ref_crosswalk import Resolver
    by_id = {c.rule_id: c for c in audit(RULEBOOK, Resolver(REFS, CONTENT))}
    c = by_id["growth_trap_flag-001"]
    assert c.status == "OK"
    assert c.lesson_title and "Valuation" in c.lesson_title


@needs_real
def test_full_rulebook_audit_has_exactly_one_defect():
    """The acceptance criterion for D13: exactly one non-OK row across the
    whole rulebook, and it's the known NO_REF defect."""
    from soic_wiki.ref_crosswalk import Resolver
    checks = audit(RULEBOOK, Resolver(REFS, CONTENT))
    bad = {c.rule_id: c.status for c in checks if c.status != "OK"}
    assert bad == {"pe_context-001": "NO_REF"}
