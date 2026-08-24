from pathlib import Path

from soic_wiki.claims import Claim
from soic_wiki.lost_conditions import bind_rules, find_lost_conditions


def _threshold(cid, metric, bound, ref="FESTF", ts="00:09:35"):
    return Claim(claim_id=cid, kind="threshold", ref=ref, ts=ts,
                 quote="q", statement="s", metric=metric, bound=bound,
                 source_brief="b.md")


def _scope(cid, governs, statement, ref="FESTF", ts="00:42:15"):
    return Claim(claim_id=cid, kind="scope", ref=ref, ts=ts, quote="q",
                 statement=statement, scopes=governs, source_brief="b.md")


def _rulebook(tmp_path: Path, entries) -> Path:
    lines = ["rules:"]
    for rid, metric, check in entries:
        lines += [f"  - id: {rid}", f"    metric: {metric}",
                  f"    check_rule: \"{check}\"", "    requires_attribute: {}"]
    path = tmp_path / "rules.yaml"
    path.write_text("\n".join(lines) + "\n")
    return path


def test_bind_rules_matches_a_rule_to_its_threshold_claim(tmp_path: Path):
    rb = _rulebook(tmp_path, [("roce_gate-001", "roce", ">= 15")])
    claims = [_threshold("c1", "roce", ">= 15")]
    bound = bind_rules(rb, claims)
    assert len(bound) == 1
    assert bound[0].rule_id == "roce_gate-001"
    assert bound[0].claim_id == "c1"


def test_a_rule_with_no_matching_claim_binds_to_nothing(tmp_path: Path):
    rb = _rulebook(tmp_path, [("mystery-001", "unknown_metric", ">= 1")])
    assert bind_rules(rb, [_threshold("c1", "roce", ">= 15")]) == []


def test_the_detector_reports_a_rule_missing_its_scope(tmp_path: Path):
    """The shape this stage exists to catch: the source attached a carve-out,
    the rule encodes the bare number."""
    rb = _rulebook(tmp_path, [("roce_gate-001", "roce", ">= 15")])
    claims = [_threshold("c1", "roce", ">= 15"),
              _scope("s1", ["c1"], "does not apply to a turnaround")]
    found = find_lost_conditions(rb, claims)
    assert len(found) == 1
    assert found[0].rule_id == "roce_gate-001"
    assert found[0].scope_claim_id == "s1"
    assert "turnaround" in found[0].scope_statement


def test_no_finding_when_the_threshold_has_no_scope(tmp_path: Path):
    rb = _rulebook(tmp_path, [("roce_gate-001", "roce", ">= 15")])
    assert find_lost_conditions(rb, [_threshold("c1", "roce", ">= 15")]) == []


def test_a_rule_that_encodes_its_scope_is_not_reported(tmp_path: Path):
    """requires_attribute is how this rulebook already scopes a rule."""
    path = tmp_path / "rules.yaml"
    path.write_text(
        "rules:\n"
        "  - id: roce_gate-001\n    metric: roce\n"
        "    check_rule: \">= 15\"\n"
        "    requires_attribute: {is_lender: \"false\"}\n")
    claims = [_threshold("c1", "roce", ">= 15"),
              _scope("s1", ["c1"], "is_lender must be false")]
    assert find_lost_conditions(path, claims) == []


def test_one_finding_per_rule_scope_pair(tmp_path: Path):
    rb = _rulebook(tmp_path, [("roce_gate-001", "roce", ">= 15")])
    claims = [_threshold("c1", "roce", ">= 15"),
              _scope("s1", ["c1"], "not for lenders"),
              _scope("s2", ["c1"], "not during a turnaround")]
    assert len(find_lost_conditions(rb, claims)) == 2


def test_a_finding_carries_its_citation(tmp_path: Path):
    rb = _rulebook(tmp_path, [("roce_gate-001", "roce", ">= 15")])
    claims = [_threshold("c1", "roce", ">= 15"),
              _scope("s1", ["c1"], "not for lenders", ref="TFELT", ts="00:42:09")]
    f = find_lost_conditions(rb, claims)[0]
    assert f.ref == "TFELT" and f.ts == "00:42:09"
