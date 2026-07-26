"""End-to-end composition of every stage over a synthetic corpus.

Each module was individually well tested and individually sound; the defects
the final branch review found were all in the CONTRACTS BETWEEN modules --
`extract_rules`, `refute` and `reconcile` had zero production callers and were
never placed in the same call stack by any test. This file is the regression
net for that class: route -> extract -> verify -> corroborate -> refute ->
reconcile -> write_bundle, asserting on the published bundle rather than on
any single stage's return value.

Both LLM stages take an injected fake. No network, no model.
"""

from __future__ import annotations

import json

import yaml

from soic_method.corpus import hash_text
from soic_method.corroborate import corroborate
from soic_method.eligibility import Eligibility, apply_eligibility
from soic_method.extract import extract_rules
from soic_method.models import LessonRecord
from soic_method.publish import write_bundle
from soic_method.reconcile import reconcile
from soic_method.refute import refute
from soic_method.router import route
from soic_method.verify import verify_rule

COURSE = "Level 5- How to Screen & Filter Epic Stocks"
RULE_KEYS = ["screen.sales_growth.floor", "screen.roc.floor",
             "screen.pe.ceiling", "screen.margin.floor"]

SALES_A = "we want sales growth of at least 15 percent over the last five years"
ROC_A = "and on top of that the roc has to be more than 20 percent to qualify"
PE_A = "on valuation we are comfortable at a pe ratio of 15 to 30 times earnings"
BODY_A = ("[00:00:00] welcome back everyone lets get into the screening filters.\n"
          "[00:12:30] " + SALES_A + " without exception.\n"
          "[00:31:00] " + ROC_A + " at all.\n"
          "[00:47:10] " + PE_A + " and no higher.\n")

SALES_B = "sales growth of at least 15 percent is the first filter we apply here"
ROC_B = "the roc must be more than 20 percent across a full cycle no exceptions"
PE_B = "but the pe ratio should be less than 50 times, i stretch to 40 at most"
BODY_B = ("[00:00:00] a quick recap of the same screen before the case study.\n"
          "[00:09:45] " + SALES_B + " always.\n"
          "[00:22:00] " + ROC_B + " ever.\n"
          "[00:38:20] " + PE_B + " frankly.\n")

MARGIN_C = "management told us they will keep operating margin above 25 percent"
BODY_C = ("[00:00:00] one more thing before we wrap up the session today.\n"
          "[00:05:00] " + MARGIN_C + " going forward.\n")

BODIES = {"1": BODY_A, "2": BODY_B, "3": BODY_C}


def _corpus():
    lessons = [
        LessonRecord(lesson_id=lid, course_title=COURSE, module_title="m",
                     title="t", url="https://x/lesson/" + lid, body_text=body,
                     text_hash=hash_text(body))
        for lid, body in sorted(BODIES.items())
    ]
    elig = Eligibility({COURSE: {"eligible": True}}, excluded_modules=[])
    return apply_eligibility(lessons, elig)


def _at(lid, quote, **fields):
    """A canned extraction pinned to a REAL offset range in the corpus."""
    start = BODIES[lid].index(quote)
    fields.update({"start": start, "end": start + len(quote)})
    return fields


EXTRACTIONS = {
    "1": [
        _at("1", SALES_A, kind="threshold", operator="gte", value=15,
            unit="percent", rule_key="screen.sales_growth.floor"),
        _at("1", ROC_A, kind="threshold", operator="gte", value=20,
            unit="percent", rule_key="screen.roc.floor"),
        _at("1", PE_A, kind="range", value_min=15, value_max=30,
            unit="multiple", rule_key="screen.pe.ceiling"),
        # Citation does NOT support this: the span says 15, the rule claims
        # 99. Gate 1 must reject it before it can be corroborated.
        _at("1", SALES_A, kind="threshold", operator="gte", value=99,
            unit="percent", rule_key="screen.sales_growth.floor"),
    ],
    "2": [
        _at("2", SALES_B, kind="threshold", operator="gte", value=15,
            unit="percent", rule_key="screen.sales_growth.floor"),
        _at("2", ROC_B, kind="threshold", operator="gte", value=20,
            unit="percent", rule_key="screen.roc.floor"),
        # Directly contradicts lesson 1's P/E band, with no scope claimed.
        _at("2", PE_B, kind="range", value_min=40, value_max=50,
            unit="multiple", rule_key="screen.pe.ceiling"),
    ],
    # Reported speech: a company's own guidance, not a SOIC rule.
    "3": [_at("3", MARGIN_C, kind="threshold", operator="gte", value=25,
              unit="percent", rule_key="screen.margin.floor")],
}


def _fake_extractor(lesson_id):
    payload = {"rules": [dict(r, tier="graded", stage="screen")
                         for r in EXTRACTIONS[lesson_id]]}
    return lambda _prompt: json.dumps(payload)


def _fake_refuter(prompt):
    refuted = "management told us" in prompt
    return json.dumps({"refuted": refuted, "reason": "reported speech"})


def _run(tmp_path):
    lessons = _corpus()
    by_id = {l.lesson_id: l for l in lessons}

    raw = []
    for cand in route(lessons):
        raw.extend(extract_rules(by_id[cand.lesson_id], cand,
                                 _fake_extractor(cand.lesson_id),
                                 rule_keys=RULE_KEYS))

    verified = [r for r in raw if verify_rule(r, by_id).ok]
    rejected = [r for r in raw if not verify_rule(r, by_id).ok]
    corroborated = [corroborate(r, by_id) for r in verified]
    survived = [r for r in corroborated if refute(r, by_id, _fake_refuter)]

    out = reconcile(survived, by_id, {})
    write_bundle(out, by_id, tmp_path)
    return {
        "raw": raw, "verified": verified, "rejected": rejected,
        "survived": survived, "out": out,
        "files": {p.name: p.read_text(encoding="utf-8")
                  for p in tmp_path.iterdir()},
    }


def _load(res, name):
    return yaml.safe_load(res["files"][name]) or []


def test_router_reaches_every_lesson_and_extraction_produces_rules(tmp_path):
    res = _run(tmp_path)
    # The router must actually find all three lessons, or the rest of these
    # assertions would pass vacuously on an empty pipeline.
    assert {c.lesson_id for c in route(_corpus())} == {"1", "2", "3"}
    assert len(res["raw"]) == 8


def test_a_good_rule_reaches_graded_yaml_as_active(tmp_path):
    res = _run(tmp_path)
    graded = _load(res, "graded.yaml")
    by_key = {g["rule_key"]: g for g in graded}
    assert by_key["screen.sales_growth.floor"]["value"] == 15
    assert by_key["screen.sales_growth.floor"]["status"] == "active"
    assert by_key["screen.roc.floor"]["status"] == "active"
    # Two lessons independently state it -- that is what "active" means.
    assert by_key["screen.roc.floor"]["corroboration"] >= 2


def test_a_rule_its_citation_does_not_support_is_rejected(tmp_path):
    res = _run(tmp_path)
    assert [r.value for r in res["rejected"]] == [99]
    assert 99 not in [g["value"] for g in _load(res, "graded.yaml")]
    assert "99" not in res["files"]["knockouts.yaml"]


def test_reported_speech_is_killed_by_the_refuter(tmp_path):
    res = _run(tmp_path)
    keys = {r.rule_key for r in res["survived"]}
    assert "screen.margin.floor" not in keys
    assert "screen.margin.floor" not in res["files"]["graded.yaml"]


def test_a_genuine_contradiction_lands_in_the_conflict_queue(tmp_path):
    res = _run(tmp_path)
    conflicts = _load(res, "conflicts.open.yaml")
    assert len(conflicts) == 1
    assert {r["rule_key"] for r in conflicts[0]} == {"screen.pe.ceiling"}
    # ...and neither side was published as if it had been adjudicated.
    assert "screen.pe.ceiling" not in res["files"]["graded.yaml"]


def test_nothing_in_the_bundle_ships_a_bound_binding(tmp_path):
    res = _run(tmp_path)
    for name, text in res["files"].items():
        assert "status: bound" not in text, name
