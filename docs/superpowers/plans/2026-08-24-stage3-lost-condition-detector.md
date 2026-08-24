# Stage 3 — Lost-Condition Detector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Find rules whose source attached a condition that the rule does not encode — mechanically, instead of by luck.

**Architecture:** Claims are extracted from the already-gated lecture briefs, each carrying a quote that is verified against the raw transcript (never against the brief it came from). A `scopes` edge links a condition-claim to the threshold-claim it governs. The detector reports any rulebook rule that encodes a threshold whose scope the rule does not carry. Pure Python over JSON — no graph database.

**Tech Stack:** Python 3.9 (this repo, not the ladder's 3.11), pytest, PyYAML, the existing `soic_wiki.ref_crosswalk` and `soic_method.corpus`.

## Why this is narrower than the original design

The decisions D1–D12 argued for a full claims graph partly to audit the
rulebook's citations. Plan A did that already: `scripts/audit_rulebook.py`
reports **15 of 16 citations sound**, the single defect being
`pe_context-001`, which has no `ref` at all. And `judge.py` turned out to
already compute the exit layer we believed was missing.

So the one thing nothing else does is catch a **rule that dropped its
condition**. That is what this stage builds. The wider graph — mechanism,
disqualifier and procedure claims, the company edges, the adjudication overlay —
is deferred until this proves out.

## The acceptance criterion

The detector must **independently rediscover two conditions already found by
hand**, without being told about them:

1. `capital_efficiency_gate-001` encodes a returns bar as a point-in-time
   number, while the source attaches a carve-out for companies inflecting out of
   a turnaround (present in the `FESTF` and `TFELT` briefs).
2. `pe_context-001` encodes a flat band, while the source ties the acceptable
   multiple to the growth rate and states a much lower band for a weaker
   business (present in the `VALU2` and `BVB` briefs).

If it cannot find those two, the schema is wrong, and finding that out on four
briefs is far cheaper than on fifty-eight.

## Global Constraints

- **Verify every claim's quote against the raw transcript, never against the
  brief it was extracted from.** Minting and validating against the same
  artifact verifies a copy against itself and makes drift invisible.
- **Resolve a lecture by the pair `(REF, timestamp)`, never by REF alone** — 25
  of 221 REF codes map to more than one lesson. Use
  `soic_wiki.ref_crosswalk.Resolver`; never hand-roll resolution.
- **A `worked_example` can never become a threshold.** One-off illustrations
  being promoted to universal rules is the failure this corpus is full of.
- **The detector proposes; it never writes to the rulebook.**
- **Never hardcode a personal or machine-specific absolute path.** Vault and
  rulebook locations come from arguments or environment variables.
- Python **3.9** in this repo: no `match`, no `X | Y` unions, and **no backslash
  inside an f-string expression** (this has broken this repo before).
- Read-only with respect to `soic-ladder` and the briefs.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/soic_wiki/claims.py` | **Create.** The claim model, load/save of `claims.json`, and quote verification against raw transcripts. |
| `tests/test_claims.py` | **Create.** Model validation, the verifier's both-directions behaviour, worked_example protection. |
| `src/soic_wiki/lost_conditions.py` | **Create.** Map rules to threshold claims, follow `scopes` edges, report rules missing their scope. |
| `tests/test_lost_conditions.py` | **Create.** Detector logic against synthetic claims, including the two shapes it must catch. |
| `scripts/detect_lost_conditions.py` | **Create.** CLI: load claims + rulebook, print the report, exit non-zero if any rule is missing a scope. |

Claim extraction itself is **not** a task in this plan. It is an orchestrated
step run between Task 1 and Task 3, dispatching one reader per brief, because
its quality is a judgement matter rather than something TDD can assert.

---

### Task 1: The claim model and its verifier

**Files:**
- Create: `src/soic_wiki/claims.py`
- Test: `tests/test_claims.py`

**Interfaces:**
- Consumes: `soic_wiki.ref_crosswalk.Resolver`, `soic_method.corpus.normalize_slice`.
- Produces:
  `CLAIM_TYPES: Tuple[str, ...]`;
  `Claim` (pydantic: `claim_id`, `kind`, `ref`, `ts`, `quote`, `statement`, `metric`, `bound`, `scopes`, `source_brief`);
  `load_claims(path) -> List[Claim]`; `save_claims(path, claims) -> None`;
  `verify_claim(claim, resolver) -> bool`;
  `verify_all(claims, resolver) -> Dict[str, bool]`.

- [ ] **Step 1: Branch**

```bash
cd /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/heuristic-mclaren-37718f
git checkout -b feat/lost-conditions
```
Expected: `Switched to a new branch 'feat/lost-conditions'`

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_claims.py
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
```

- [ ] **Step 3: Run to verify they fail**

Run: `PYTHONPATH="$(pwd)/src" /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest tests/test_claims.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_wiki.claims'`

- [ ] **Step 4: Write the implementation**

```python
# src/soic_wiki/claims.py
"""Claims: one assertion from one lecture, with the quote that proves it.

A claim is minted from a lecture brief but VERIFIED against the raw
transcript. Minting and verifying against the same artifact would check a copy
against itself, which is how drift between transcript and brief stays
invisible.

`worked_example` cannot carry a bound. Treating a dated one-company
illustration as a universal rule is the single most common defect in this
corpus, so the schema refuses it rather than relying on anyone remembering.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, model_validator

CLAIM_TYPES = ("threshold", "scope", "mechanism",
               "disqualifier", "procedure", "worked_example")

_WS = re.compile(r"\s+")


def _norm(text: str) -> str:
    return _WS.sub(" ", text or "").strip().casefold()


class Claim(BaseModel):
    claim_id: str
    kind: str
    ref: str                      # lecture REF code
    ts: str                       # HH:MM:SS -- with ref, identifies the lesson
    quote: str                    # verbatim, checked against the transcript
    statement: str                # the claim in our own words
    source_brief: str
    metric: Optional[str] = None  # thresholds only
    bound: Optional[str] = None   # thresholds only, e.g. ">= 15"
    scopes: List[str] = []        # claim_ids of thresholds this scope governs

    @model_validator(mode="after")
    def _check(self):
        if self.kind not in CLAIM_TYPES:
            raise ValueError(f"unknown claim kind {self.kind!r}")
        if self.kind == "worked_example" and self.bound:
            raise ValueError(
                "a worked_example may not carry a bound -- a dated "
                "illustration must never be usable as a rule")
        if self.kind == "threshold" and not (self.metric and self.bound):
            raise ValueError("a threshold needs both a metric and a bound")
        if self.scopes and self.kind != "scope":
            raise ValueError("only a scope claim may govern thresholds")
        return self


def load_claims(path: Path) -> List[Claim]:
    return [Claim(**row) for row in json.loads(Path(path).read_text("utf-8"))]


def save_claims(path: Path, claims: List[Claim]) -> None:
    Path(path).write_text(
        json.dumps([c.model_dump() for c in claims], indent=2) + "\n",
        encoding="utf-8")


def verify_claim(claim: Claim, resolver) -> bool:
    """Is this claim's quote actually in the lecture window it cites?"""
    if resolver.resolve(claim.ref, claim.ts) is None:
        return False
    window = resolver.window(claim.ref, claim.ts)
    return _norm(claim.quote) in _norm(window)


def verify_all(claims: List[Claim], resolver) -> Dict[str, bool]:
    return {c.claim_id: verify_claim(c, resolver) for c in claims}
```

- [ ] **Step 5: Run to verify they pass**

Run: `PYTHONPATH="$(pwd)/src" /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest tests/test_claims.py -v`
Expected: PASS, 11 passed

- [ ] **Step 6: Commit**

```bash
git add src/soic_wiki/claims.py tests/test_claims.py
git commit -m "feat: claim model verified against raw transcripts

A claim is minted from a brief but verified against the transcript, never
against the brief it came from -- checking a copy against itself is how
transcript-to-brief drift stays invisible. The schema refuses a
worked_example that carries a bound, so a dated illustration cannot be
promoted to a rule by accident."
```

---

### Task 2: The detector

**Files:**
- Create: `src/soic_wiki/lost_conditions.py`
- Create: `scripts/detect_lost_conditions.py`
- Test: `tests/test_lost_conditions.py`

**Interfaces:**
- Consumes: `soic_wiki.claims.Claim`, `load_claims`.
- Produces:
  `RuleBinding` (pydantic: `rule_id`, `metric`, `bound`, `claim_id`);
  `bind_rules(rulebook_path, claims) -> List[RuleBinding]`;
  `Finding` (pydantic: `rule_id`, `threshold_claim_id`, `scope_claim_id`, `scope_statement`, `ref`, `ts`);
  `find_lost_conditions(rulebook_path, claims) -> List[Finding]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_lost_conditions.py
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
```

- [ ] **Step 2: Run to verify they fail**

Run: `PYTHONPATH="$(pwd)/src" /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest tests/test_lost_conditions.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_wiki.lost_conditions'`

- [ ] **Step 3: Write the implementation**

```python
# src/soic_wiki/lost_conditions.py
"""Which rules dropped the condition their source attached to them?

The whole point of this stage. A rule binds to the threshold claim whose
metric and bound it encodes. If that threshold has a `scopes` edge from a
condition the rule does not carry, the rule is applying a number outside the
range its source gave it.

This reports; it never edits a rulebook. Every finding carries the citation so
a human can read the source and decide.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel

from .claims import Claim


class RuleBinding(BaseModel):
    rule_id: str
    metric: str
    bound: str
    claim_id: str


class Finding(BaseModel):
    rule_id: str
    threshold_claim_id: str
    scope_claim_id: str
    scope_statement: str
    ref: str
    ts: str


def _norm_bound(bound: str) -> str:
    return "".join((bound or "").split())


def _rule_entries(rulebook_path: Path) -> List[Dict]:
    doc = yaml.safe_load(Path(rulebook_path).read_text("utf-8")) or {}
    out: List[Dict] = []
    for section in ("rules", "observations"):
        for entry in doc.get(section) or []:
            out.append(entry)
    return out


def bind_rules(rulebook_path: Path, claims: List[Claim]) -> List[RuleBinding]:
    """A rule binds to the threshold claim carrying the same metric and bound."""
    thresholds = [c for c in claims if c.kind == "threshold"]
    bindings: List[RuleBinding] = []
    for entry in _rule_entries(rulebook_path):
        metric = entry.get("metric")
        bound = entry.get("check_rule") or entry.get("reference_band")
        if not metric or not bound:
            continue
        for claim in thresholds:
            if (claim.metric == metric
                    and _norm_bound(claim.bound) == _norm_bound(bound)):
                bindings.append(RuleBinding(
                    rule_id=entry["id"], metric=metric, bound=bound,
                    claim_id=claim.claim_id))
                break
    return bindings


def find_lost_conditions(rulebook_path: Path,
                         claims: List[Claim]) -> List[Finding]:
    by_id = {c.claim_id: c for c in claims}
    scopes_for: Dict[str, List[Claim]] = {}
    for claim in claims:
        if claim.kind == "scope":
            for governed in claim.scopes:
                scopes_for.setdefault(governed, []).append(claim)

    entries = {e["id"]: e for e in _rule_entries(rulebook_path)}
    findings: List[Finding] = []
    for binding in bind_rules(rulebook_path, claims):
        entry = entries.get(binding.rule_id, {})
        # requires_attribute is how this rulebook already narrows a rule; a
        # rule that carries one is treated as having encoded its scope.
        if entry.get("requires_attribute"):
            continue
        for scope in scopes_for.get(binding.claim_id, []):
            findings.append(Finding(
                rule_id=binding.rule_id,
                threshold_claim_id=binding.claim_id,
                scope_claim_id=scope.claim_id,
                scope_statement=scope.statement,
                ref=scope.ref, ts=scope.ts))
    return findings
```

- [ ] **Step 4: Run to verify they pass**

Run: `PYTHONPATH="$(pwd)/src" /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest tests/test_lost_conditions.py -v`
Expected: PASS, 7 passed

- [ ] **Step 5: Write the CLI**

```python
#!/usr/bin/env python3
# scripts/detect_lost_conditions.py
"""Report rules applying a number outside the range their source gave it.

Reports only. Applying a fix is a human decision -- every finding names the
lecture and timestamp so the source can be read directly.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.claims import load_claims                    # noqa: E402
from soic_wiki.lost_conditions import find_lost_conditions   # noqa: E402

DEFAULT_RULEBOOK = Path.home() / (
    "Documents/workspace/Claude_Code/soic-ladder/rulebook/"
    "soic-ladder-rules-v1.yaml")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", required=True, help="path to claims.json")
    parser.add_argument("--rulebook", default=str(DEFAULT_RULEBOOK))
    args = parser.parse_args()

    claims = load_claims(Path(args.claims))
    findings = find_lost_conditions(Path(args.rulebook), claims)

    print(f"{len(claims)} claims; {len(findings)} rule(s) missing a scope\n")
    for f in findings:
        print(f"{f.rule_id}")
        print(f"    source attached: {f.scope_statement}")
        print(f"    cited at:        {f.ref} {f.ts}")
        print(f"    threshold claim: {f.threshold_claim_id}\n")
    if not findings:
        print("No rule is applying a number outside its source's stated range.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Confirm the CLI runs on an empty claim set**

```bash
cd /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/heuristic-mclaren-37718f
echo '[]' > /tmp/empty-claims.json
/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python \
  scripts/detect_lost_conditions.py --claims /tmp/empty-claims.json; echo "exit=$?"
```
Expected: `0 claims; 0 rule(s) missing a scope`, the no-findings line, `exit=0`.

- [ ] **Step 7: Run the repo's full suite**

Run: `PYTHONPATH="$(pwd)/src" /Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python -m pytest -q 2>&1 | tail -2`
Expected: the new tests pass. Six pre-existing failures in `tests/test_storm_cli.py`
and `tests/test_soic_wiki_sector_gate.py` are unrelated to this work — they come
from a stale hardcoded worktree path and predate this branch. Report the totals.

- [ ] **Step 8: Commit**

```bash
git add src/soic_wiki/lost_conditions.py scripts/detect_lost_conditions.py tests/test_lost_conditions.py
git commit -m "feat: detect rules that dropped their source's condition

A rule binds to the threshold claim whose metric and bound it encodes. If that
threshold is governed by a scope the rule does not carry, the rule is applying
a number outside the range its source gave it. Reports only -- every finding
names the lecture and timestamp so a human can read the source and decide."
```

---

## After Task 2: the orchestrated extraction

Not a TDD task — extraction quality is a judgement matter. The controller runs
this between Task 2 and the acceptance check:

1. Dispatch one reader per brief over the pilot set: `crash/FESTF`, `l5/TFELT`,
   `crash/VALU2`, `crash/BVB`. Each emits `threshold` and `scope` claims only,
   with a verbatim quote and a `(REF, timestamp)` citation for each.
2. Run `verify_all` against the raw transcripts. Any claim whose quote is not
   present is dropped, not fixed — a claim that cannot be verified is not
   evidence.
3. Run `scripts/detect_lost_conditions.py` over the surviving claims.

**The acceptance check:** it must report `capital_efficiency_gate-001` and
`pe_context-001` as missing a scope, having been told nothing about either.
If it does not, the schema or the extraction prompt is wrong — and that is the
finding, not a reason to hand-edit the claims until it passes.

Only after that passes does extraction extend to all 58 briefs.

---

## Self-Review

**Spec coverage.** Stage 3 of `docs/reassessment/ROADMAP.md` asks for the
lost-condition detector. Task 1 builds the verified claim; Task 2 builds the
detector and its CLI; the orchestrated step supplies real claims and tests the
whole thing against two conditions already known by hand.

**Deliberately not here.** `mechanism`, `disqualifier` and `procedure` claims are
allowed by the schema but nothing consumes them yet — they arrive when D14 step
7 needs the procedure checklist. The adjudication overlay (D6), the confidence
score (D12) and the contested-value machinery (D10) are all deferred until the
detector proves it finds something real.

**Placeholders.** None: every code step carries complete code, every run step an
exact command and expected output.

**Type consistency.** `Claim`, `load_claims -> List[Claim]`,
`verify_claim(claim, resolver) -> bool`, `bind_rules(path, claims) ->
List[RuleBinding]`, `find_lost_conditions(path, claims) -> List[Finding]` are
used with those exact signatures in the tests, the modules and the CLI.
