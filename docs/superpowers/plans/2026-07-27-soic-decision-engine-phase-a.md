# SOIC Decision Engine — Phase A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** turn the machine-actionable decision-engine DESIGN (already written and
committed to `main`) into real, tested code: a `decision_rules.py` rule loader
and evaluator, a `Decision`/`SignalOutcome`-emitting `evaluate()` function added
to `decision_engine.py`, and — once that code is proven against small
self-contained fixtures — the real F21-F24 framework entries landed in
`decision-frameworks-v1.md` plus the real `decision-rules-v2.yaml` /
`metric-registry.yaml` pilot files in the vault.

**Architecture:** a new, single-responsibility module (`decision_rules.py`)
parses the machine-readable rule layer and evaluates individual rule
expressions — mirroring the existing split between `framework_router.py`
(parse frameworks) and `decision_engine.py` (assemble). `decision_engine.py`
gains `evaluate()` alongside the untouched `build_briefing()`, using
`decision_rules.py` to score each of a `Briefing`'s already-matched frameworks
against live data, applying safety-gate vetoes before a weighted combination,
and never scoring past missing data (abstain, not guess).

**Tech Stack:** Python 3.9, PyYAML (already a project dependency), pytest,
dataclasses, `unittest.mock.patch` for the existing screener-fetch mocking
pattern.

## Global Constraints

- `build_briefing(symbol, keywords, frameworks_path, sector_registry_path=None)`
  in `src/soic_senses/decision_engine.py` keeps its exact current signature
  and behavior — additive only, never modified.
- Every new function is TDD'd: write the failing test, run it, watch it fail
  for the right reason, then write minimal code to pass — this project's
  established convention (visible in its own git history: the Gate 1/Gate 2
  verifiers, `framework_router.py`, `sector_router.py` were all built this
  way).
- No fabricated numeric thresholds. Where a `Grounding:` source states a
  direction but no number (F22), the rule ships with zero signals rather than
  an invented ceiling — this is stated explicitly in the design doc (§1) and
  must not be violated for expediency.
- A signal whose metric is missing from `briefing.live_ratios`, or whose
  registry entry is `not_yet_fetchable`, always resolves to `outcome ==
  "abstain"` — never raises, never counts as bearish.
- Scope is Phase A only (per the design doc §7): schema + pilot rules
  (F10, F21, F22, F23, F24) + `evaluate()`. Sector overlays (§3),
  `framework_evolution.py` validation/regression gates (§4), and panel
  expansion (§7 Phase C) are explicitly OUT of scope for this plan.
- Design doc for full context (read once, referenced throughout):
  `docs/superpowers/plans/2026-07-27-soic-decision-engine-machine-actionable-plan.md`.
  F21-F24 source text (pre-approved, ready-to-paste): `docs/superpowers/plans/2026-07-27-soic-framework-f21-f24-draft.md`.

---

## File Structure

- **Create** `src/soic_senses/decision_rules.py` — parses
  `decision-rules-v2.yaml` into `RuleEntry`/`Signal` objects and
  `metric-registry.yaml` into `MetricInfo` objects; evaluates a rule
  expression string (`"<= 90"`, `">= 20"`, `"between 15 35"`) against a live
  float. Zero knowledge of `Briefing`/`Decision` — pure parse + evaluate,
  same responsibility split as `framework_router.py`.
- **Modify** `src/soic_senses/decision_engine.py` — add `SignalOutcome`,
  `Decision` dataclasses and `evaluate()`, importing from the new
  `decision_rules.py`. `Briefing`/`build_briefing()` untouched.
- **Create** `tests/test_soic_senses_decision_rules.py` — TDD coverage for
  the new module.
- **Modify** `tests/test_soic_senses_decision_engine.py` — add `evaluate()`
  test coverage; existing 10 tests untouched.
- **Create** `tests/fixtures/decision_rules_sample.yaml` and
  `tests/fixtures/metric_registry_sample.yaml` — small, self-contained rule
  fixtures (using framework ids `F1`/`F2`/`F3`/`F10`, matching the ids
  already used in `tests/fixtures/frameworks_sample.md`) so `evaluate()`
  tests never depend on the real, much larger production frameworks file.
- **Modify** (vault repo, content only, no test)
  `wiki/personas/soic/frameworks/decision-frameworks-v1.md` — append the
  pre-approved F21-F24 sections.
- **Create** (vault repo, content only)
  `wiki/personas/soic/frameworks/decision-rules-v2.yaml` and
  `wiki/personas/soic/frameworks/metric-registry.yaml` — the real Phase A
  pilot rule set, verified against the now-tested loader.

---

### Task 1: `decision_rules.py` — dataclasses + `check_rule()`

**Files:**
- Create: `src/soic_senses/decision_rules.py`
- Test: `tests/test_soic_senses_decision_rules.py`

**Interfaces:**
- Produces: `Signal(name: str, metric: str, rule: str, weight: float)`,
  `RuleEntry(id: str, status: str, cls: str, signals: List[Signal])`,
  `MetricInfo(label: str, status: str)`, `check_rule(value: float, rule: str) -> bool`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_soic_senses_decision_rules.py
import pytest


def test_check_rule_supports_less_or_equal():
    from soic_senses.decision_rules import check_rule

    assert check_rule(90.0, "<= 90") is True
    assert check_rule(90.1, "<= 90") is False


def test_check_rule_supports_greater_or_equal():
    from soic_senses.decision_rules import check_rule

    assert check_rule(20.0, ">= 20") is True
    assert check_rule(19.9, ">= 20") is False


def test_check_rule_supports_between_inclusive():
    from soic_senses.decision_rules import check_rule

    assert check_rule(15.0, "between 15 35") is True
    assert check_rule(35.0, "between 15 35") is True
    assert check_rule(14.9, "between 15 35") is False


def test_check_rule_raises_on_unrecognized_expression():
    from soic_senses.decision_rules import check_rule

    with pytest.raises(ValueError):
        check_rule(1.0, "n/a")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_rules.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'soic_senses.decision_rules'` (or `ImportError`) for all four tests.

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_senses/decision_rules.py
"""Loads the machine-readable rule layer (decision-rules-v2.yaml +
metric-registry.yaml) that decision_engine.evaluate() scores against.

Deliberately separate from decision_engine.py: this module only parses
rule DATA and evaluates rule EXPRESSIONS (value in, bool out), with zero
knowledge of Briefing/Decision assembly -- the same single-responsibility
split as framework_router.py (parse frameworks) vs decision_engine.py
(assemble). See docs/superpowers/plans/2026-07-27-soic-decision-engine-
machine-actionable-plan.md section 1/2.1 for the full design.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union

import yaml


@dataclass
class Signal:
    name: str
    metric: str
    rule: str
    weight: float


@dataclass
class RuleEntry:
    id: str
    status: str  # machine | advisory-only | advisory-numeric | deprecated
    cls: str  # safety_gate | valuation | quality | timing | routing
    signals: List[Signal] = field(default_factory=list)


@dataclass
class MetricInfo:
    label: str
    status: str  # fetchable | not_yet_fetchable


_RULE_RE = re.compile(r"^(<=|>=|<|>)\s*(-?\d+(?:\.\d+)?)$")
_BETWEEN_RE = re.compile(r"^between\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)$")


def check_rule(value: float, rule: str) -> bool:
    """Evaluate a threshold/band rule string against a live value.

    Supports the two shapes decision-rules-v2.yaml uses: "<= 90" / ">= 20"
    / "< 5" / "> 5", and "between A B" (inclusive both ends). Raises
    ValueError on any other shape -- an unparseable rule must fail loudly,
    never silently pass or fail.
    """
    stripped = rule.strip()

    m = _BETWEEN_RE.match(stripped)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        return lo <= value <= hi

    m = _RULE_RE.match(stripped)
    if m:
        op, num = m.group(1), float(m.group(2))
        if op == "<=":
            return value <= num
        if op == ">=":
            return value >= num
        if op == "<":
            return value < num
        return value > num

    raise ValueError(f"Unrecognized rule expression: {rule!r}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_rules.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/soic_senses/decision_rules.py tests/test_soic_senses_decision_rules.py
git commit -m "feat: check_rule() threshold/band evaluator for decision rules"
```

---

### Task 2: `decision_rules.py` — `load_decision_rules()` + `load_metric_registry()`

**Files:**
- Modify: `src/soic_senses/decision_rules.py` (append to end of file)
- Create: `tests/fixtures/decision_rules_sample.yaml`
- Create: `tests/fixtures/metric_registry_sample.yaml`
- Modify: `tests/test_soic_senses_decision_rules.py` (append)

**Interfaces:**
- Consumes: `Signal`, `RuleEntry`, `MetricInfo` from Task 1.
- Produces: `load_decision_rules(path) -> List[RuleEntry]`,
  `load_metric_registry(path) -> Dict[str, MetricInfo]`.

- [ ] **Step 1: Write the fixture files**

```yaml
# tests/fixtures/decision_rules_sample.yaml
- id: F1
  status: machine
  class: safety_gate
  signals:
    - name: wc_days_gate
      metric: wc_days
      rule: "<= 90"
      weight: 1.0
- id: F2
  status: machine
  class: valuation
  signals:
    - name: moat_pe_band
      metric: stock_pe
      rule: "between 10 40"
      weight: 1.0
- id: F3
  status: machine
  class: quality
  signals:
    - name: leverage_check
      metric: debt_to_equity
      rule: "<= 1.0"
      weight: 1.0
- id: F10
  status: machine
  class: valuation
  signals:
    - name: growth_above_embedded
      metric: profit_growth_3y_pct
      rule: ">= 20"
      weight: 1.0
```

```yaml
# tests/fixtures/metric_registry_sample.yaml
metrics:
  wc_days:
    label: "WC Days"
    status: fetchable
  stock_pe:
    label: "Stock P/E"
    status: fetchable
  debt_to_equity:
    label: "Debt to Equity"
    status: fetchable
  profit_growth_3y_pct:
    label: "Profit growth 3Yr %"
    status: fetchable
```

- [ ] **Step 2: Write the failing tests**

```python
# append to tests/test_soic_senses_decision_rules.py
from pathlib import Path

RULES_FIXTURE = Path(__file__).parent / "fixtures" / "decision_rules_sample.yaml"
REGISTRY_FIXTURE = Path(__file__).parent / "fixtures" / "metric_registry_sample.yaml"


def test_load_decision_rules_parses_every_entry():
    from soic_senses.decision_rules import load_decision_rules

    rules = load_decision_rules(RULES_FIXTURE)

    assert [r.id for r in rules] == ["F1", "F2", "F3", "F10"]
    f1 = rules[0]
    assert f1.cls == "safety_gate"
    assert f1.signals[0].metric == "wc_days"
    assert f1.signals[0].rule == "<= 90"
    assert f1.signals[0].weight == 1.0


def test_load_metric_registry_parses_every_entry():
    from soic_senses.decision_rules import load_metric_registry

    registry = load_metric_registry(REGISTRY_FIXTURE)

    assert registry["stock_pe"].label == "Stock P/E"
    assert registry["stock_pe"].status == "fetchable"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_rules.py -v`
Expected: the 2 new tests FAIL with `ImportError: cannot import name 'load_decision_rules'`; the 4 existing tests still PASS.

- [ ] **Step 4: Write minimal implementation**

```python
# append to src/soic_senses/decision_rules.py

def load_decision_rules(path: Union[str, Path]) -> List[RuleEntry]:
    """Parse decision-rules-v2.yaml (a YAML list, one entry per framework)
    into RuleEntry objects."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    rules = []
    for entry in data:
        signals = [
            Signal(
                name=s["name"],
                metric=s["metric"],
                rule=s["rule"],
                weight=float(s.get("weight", 1.0)),
            )
            for s in entry.get("signals", [])
        ]
        rules.append(
            RuleEntry(
                id=entry["id"],
                status=entry.get("status", "machine"),
                cls=entry.get("class", "valuation"),
                signals=signals,
            )
        )
    return rules


def load_metric_registry(path: Union[str, Path]) -> Dict[str, MetricInfo]:
    """Parse metric-registry.yaml's `metrics:` mapping into MetricInfo,
    keyed by metric key."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    registry = {}
    for key, entry in data.get("metrics", {}).items():
        registry[key] = MetricInfo(
            label=entry["label"], status=entry.get("status", "fetchable")
        )
    return registry
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_rules.py -v`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add src/soic_senses/decision_rules.py tests/test_soic_senses_decision_rules.py tests/fixtures/decision_rules_sample.yaml tests/fixtures/metric_registry_sample.yaml
git commit -m "feat: load_decision_rules() + load_metric_registry() YAML loaders"
```

---

### Task 3: `decision_engine.py` — `Decision`/`SignalOutcome` + `evaluate()` veto behavior

**Files:**
- Modify: `src/soic_senses/decision_engine.py:14-21` (imports) and append
  new dataclasses + function at end of file (currently ends line 106)
- Modify: `tests/test_soic_senses_decision_engine.py` (append)

**Interfaces:**
- Consumes: `RuleEntry`, `Signal`, `MetricInfo`, `check_rule`,
  `load_decision_rules`, `load_metric_registry` from `decision_rules.py`
  (Tasks 1-2); `Briefing`, `Framework` already in `decision_engine.py`.
- Produces: `SignalOutcome(framework_id, signal, metric, value, source,
  rule, outcome)`, `Decision(symbol, verdict, conviction,
  per_framework_votes, rule_trail, contradictions,
  unresolved_human_questions, data_coverage)`,
  `evaluate(briefing, rules_path, registry_path) -> Decision`. Later tasks
  (4, 5, 6) extend `evaluate()`'s body in place — its signature does not
  change again after this task.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_soic_senses_decision_engine.py
DECISION_RULES_FIXTURE = Path(__file__).parent / "fixtures" / "decision_rules_sample.yaml"
METRIC_REGISTRY_FIXTURE = Path(__file__).parent / "fixtures" / "metric_registry_sample.yaml"


def test_evaluate_veto_caps_verdict_at_avoid_even_when_other_signals_are_bullish():
    from soic_senses.decision_engine import Briefing, evaluate
    from soic_senses.framework_router import Framework

    briefing = Briefing(
        symbol="TESTCO",
        keywords=[],
        live_ratios={
            "WC Days": 200.0,  # F1 safety gate fails: 200 > 90
            "Stock P/E": 20.0,  # F2 valuation passes: within 10..40
            "Profit growth 3Yr %": 25.0,  # F10 valuation passes: >= 20
        },
        frameworks=[
            Framework(id="F1", title="WC gate", body=""),
            Framework(id="F2", title="Moat PE band", body=""),
            Framework(id="F10", title="Growth threshold", body=""),
        ],
    )

    decision = evaluate(briefing, DECISION_RULES_FIXTURE, METRIC_REGISTRY_FIXTURE)

    assert decision.verdict == "AVOID"
    assert decision.per_framework_votes["F1"] == "veto"
    veto_signal = next(s for s in decision.rule_trail if s.framework_id == "F1")
    assert veto_signal.outcome == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py::test_evaluate_veto_caps_verdict_at_avoid_even_when_other_signals_are_bullish -v`
Expected: FAIL with `ImportError: cannot import name 'evaluate'`.

- [ ] **Step 3: Write minimal implementation**

Modify the imports at the top of `src/soic_senses/decision_engine.py` (currently lines 14-21):

```python
from soic_senses.decision_rules import (
    MetricInfo,
    RuleEntry,
    check_rule,
    load_decision_rules,
    load_metric_registry,
)
from soic_senses.framework_router import Framework, load_frameworks, match_frameworks
from soic_senses.screener_client import fetch_screener_ratios
from soic_senses.sector_router import Sector, load_sectors, match_sectors
```

Append to the end of `src/soic_senses/decision_engine.py`:

```python
@dataclass
class SignalOutcome:
    framework_id: str
    signal: str
    metric: str
    value: Optional[float]
    source: str
    rule: str
    outcome: str  # pass | fail | abstain


@dataclass
class Decision:
    symbol: str
    verdict: str  # BUY | HOLD | SELL | AVOID | INSUFFICIENT_DATA
    conviction: str  # HIGH | MEDIUM | LOW
    per_framework_votes: Dict[str, str] = field(default_factory=dict)
    rule_trail: List[SignalOutcome] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    unresolved_human_questions: List[str] = field(default_factory=list)
    data_coverage: float = 0.0


_CLASS_WEIGHTS = {"valuation": 0.5, "quality": 0.3, "timing": 0.2}


def evaluate(
    briefing: Briefing,
    rules_path: Union[str, Path],
    registry_path: Union[str, Path],
) -> Decision:
    """Score briefing.frameworks' machine rules against briefing.live_ratios.

    Deterministic and LLM-free (the counterpart to build_briefing() that
    DOES emit a verdict, once a matched framework carries a machine
    rule). A signal whose metric is missing from live_ratios, or whose
    registry entry is not_yet_fetchable, abstains -- never crashes, never
    counts as bearish. A failed safety_gate signal vetoes the whole
    verdict to AVOID before any weighted combination runs.
    """
    symbol = briefing.symbol

    if briefing.data_error is not None:
        return Decision(
            symbol=symbol,
            verdict="INSUFFICIENT_DATA",
            conviction="LOW",
            unresolved_human_questions=[
                f"Live data fetch failed: {briefing.data_error}"
            ],
        )

    rules = {r.id: r for r in load_decision_rules(rules_path)}
    registry = load_metric_registry(registry_path)

    matched_ids = [fw.id for fw in briefing.frameworks if fw.id in rules]

    rule_trail: List[SignalOutcome] = []
    framework_scores: Dict[str, float] = {}
    per_framework_votes: Dict[str, str] = {}

    for fid in matched_ids:
        rule_entry = rules[fid]
        evaluable_weight = 0.0
        passed_weight = 0.0
        any_evaluable = False

        for signal in rule_entry.signals:
            metric_info = registry.get(signal.metric)
            source = metric_info.label if metric_info else signal.metric
            value: Optional[float] = None
            outcome = "abstain"

            if metric_info is not None and metric_info.status == "fetchable":
                raw = (
                    briefing.live_ratios.get(metric_info.label)
                    if briefing.live_ratios
                    else None
                )
                if isinstance(raw, (int, float)):
                    value = float(raw)
                    outcome = "pass" if check_rule(value, signal.rule) else "fail"
                    any_evaluable = True
                    evaluable_weight += signal.weight
                    if outcome == "pass":
                        passed_weight += signal.weight

            rule_trail.append(
                SignalOutcome(
                    framework_id=fid,
                    signal=signal.name,
                    metric=signal.metric,
                    value=value,
                    source=source,
                    rule=signal.rule,
                    outcome=outcome,
                )
            )

        if not any_evaluable:
            per_framework_votes[fid] = "abstain"
            continue

        score = passed_weight / evaluable_weight if evaluable_weight else 0.0
        framework_scores[fid] = score

        if rule_entry.cls == "safety_gate":
            per_framework_votes[fid] = "veto" if score < 1.0 else "pass"
        elif score >= 0.7:
            per_framework_votes[fid] = "bullish"
        elif score < 0.3:
            per_framework_votes[fid] = "bearish"
        else:
            per_framework_votes[fid] = "neutral"

    vetoed = [fid for fid, vote in per_framework_votes.items() if vote == "veto"]
    if vetoed:
        return Decision(
            symbol=symbol,
            verdict="AVOID",
            conviction="MEDIUM",
            per_framework_votes=per_framework_votes,
            rule_trail=rule_trail,
        )

    return Decision(
        symbol=symbol,
        verdict="HOLD",
        conviction="MEDIUM",
        per_framework_votes=per_framework_votes,
        rule_trail=rule_trail,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py::test_evaluate_veto_caps_verdict_at_avoid_even_when_other_signals_are_bullish -v`
Expected: PASS. Also re-run the full file to confirm the 10 existing `build_briefing` tests are unaffected:
Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py -v`
Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add src/soic_senses/decision_engine.py tests/test_soic_senses_decision_engine.py
git commit -m "feat: evaluate() with safety_gate veto -> AVOID"
```

---

### Task 4: `evaluate()` — abstain on missing metric, never crash

**Files:**
- Modify: `src/soic_senses/decision_engine.py` (`evaluate()` body — no
  structural change needed, this task is proof + a guard against
  regressing it)
- Modify: `tests/test_soic_senses_decision_engine.py` (append)

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_soic_senses_decision_engine.py
def test_evaluate_missing_metric_abstains_instead_of_crashing():
    from soic_senses.decision_engine import Briefing, evaluate
    from soic_senses.framework_router import Framework

    briefing = Briefing(
        symbol="TESTCO",
        keywords=[],
        live_ratios={"Stock P/E": 20.0},  # wc_days is absent entirely
        frameworks=[Framework(id="F1", title="WC gate", body="")],
    )

    decision = evaluate(briefing, DECISION_RULES_FIXTURE, METRIC_REGISTRY_FIXTURE)

    assert decision.per_framework_votes["F1"] == "abstain"
    signal_outcome = next(s for s in decision.rule_trail if s.framework_id == "F1")
    assert signal_outcome.outcome == "abstain"
    assert signal_outcome.value is None
```

- [ ] **Step 2: Run test to verify it fails or passes**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py::test_evaluate_missing_metric_abstains_instead_of_crashing -v`
Expected: this should already PASS given Task 3's implementation (the
`briefing.live_ratios.get(metric_info.label)` lookup returns `None` when
`"WC Days"` is absent, `isinstance(None, (int, float))` is `False`, so the
signal stays `outcome = "abstain"` from its initialization). If it fails,
the bug is that `evaluate()` is treating a missing key as `0.0` somewhere
instead of `None` — fix the lookup to use `.get(...)` (not `[...]`) as
shown in Task 3's Step 3, and re-run.

- [ ] **Step 3: No new implementation needed if Step 2 passed.** This task
  exists to lock the abstain-on-missing behavior in with an explicit
  regression test, not to add new code.

- [ ] **Step 4: Commit**

```bash
git add tests/test_soic_senses_decision_engine.py
git commit -m "test: lock in abstain-not-crash behavior for missing metrics"
```

---

### Task 5: `evaluate()` — `INSUFFICIENT_DATA` refusal on low coverage

**Files:**
- Modify: `src/soic_senses/decision_engine.py` (`evaluate()` body — add
  coverage computation and the refusal branch)
- Modify: `tests/test_soic_senses_decision_engine.py` (append)

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_soic_senses_decision_engine.py
def test_evaluate_refuses_with_insufficient_data_when_coverage_is_too_low():
    from soic_senses.decision_engine import Briefing, evaluate
    from soic_senses.framework_router import Framework

    briefing = Briefing(
        symbol="TESTCO",
        keywords=[],
        live_ratios={"WC Days": 50.0},  # only 1 of 4 rule signals is evaluable
        frameworks=[
            Framework(id="F1", title="WC gate", body=""),
            Framework(id="F2", title="Moat PE band", body=""),
            Framework(id="F3", title="Leverage check", body=""),
            Framework(id="F10", title="Growth threshold", body=""),
        ],
    )

    decision = evaluate(briefing, DECISION_RULES_FIXTURE, METRIC_REGISTRY_FIXTURE)

    assert decision.verdict == "INSUFFICIENT_DATA"
    assert decision.conviction != "HIGH"
    assert decision.data_coverage < 0.5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py::test_evaluate_refuses_with_insufficient_data_when_coverage_is_too_low -v`
Expected: FAIL — `decision.verdict == "HOLD"` (Task 3's fallback branch),
not `"INSUFFICIENT_DATA"`, and `decision.data_coverage == 0.0` (never
computed).

- [ ] **Step 3: Write minimal implementation**

Replace the final `if vetoed: ... return Decision(...)` block and the
trailing `return Decision(..., verdict="HOLD", ...)` in `evaluate()`
(from Task 3's Step 3) with:

```python
    total_signals = len(rule_trail)
    evaluated_signals = sum(1 for s in rule_trail if s.outcome != "abstain")
    data_coverage = evaluated_signals / total_signals if total_signals else 0.0

    if vetoed:
        conviction = (
            "HIGH" if data_coverage >= 0.8 else "MEDIUM" if data_coverage >= 0.5 else "LOW"
        )
        return Decision(
            symbol=symbol,
            verdict="AVOID",
            conviction=conviction,
            per_framework_votes=per_framework_votes,
            rule_trail=rule_trail,
            data_coverage=data_coverage,
        )

    if data_coverage < 0.5:
        return Decision(
            symbol=symbol,
            verdict="INSUFFICIENT_DATA",
            conviction="LOW",
            per_framework_votes=per_framework_votes,
            rule_trail=rule_trail,
            data_coverage=data_coverage,
        )

    return Decision(
        symbol=symbol,
        verdict="HOLD",
        conviction="MEDIUM",
        per_framework_votes=per_framework_votes,
        rule_trail=rule_trail,
        data_coverage=data_coverage,
    )
```

(This replaces both the `if vetoed:` block and the final fallback
`return Decision(...)` that Task 3 wrote — the veto branch now also
reports `data_coverage`, and a new coverage-floor branch sits between it
and the final fallback.)

- [ ] **Step 4: Run test to verify it passes**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py -v`
Expected: all tests pass, including the new one and Task 3's veto test
(re-check: the veto fixture in Task 3 has 3 of 4 signals evaluable =
coverage 0.75 ≥ 0.5, so it still hits the veto branch before the coverage
floor — confirm this explicitly in the run output).

- [ ] **Step 5: Commit**

```bash
git add src/soic_senses/decision_engine.py tests/test_soic_senses_decision_engine.py
git commit -m "feat: evaluate() refuses with INSUFFICIENT_DATA below 0.5 coverage"
```

---

### Task 6: `evaluate()` — contradictions reported, conviction capped at LOW

**Files:**
- Modify: `src/soic_senses/decision_engine.py` (`evaluate()` body — add
  contradiction detection and the weighted-combination verdict)
- Modify: `tests/test_soic_senses_decision_engine.py` (append)

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_soic_senses_decision_engine.py
def test_evaluate_reports_contradictions_and_caps_conviction_at_low():
    from soic_senses.decision_engine import Briefing, evaluate
    from soic_senses.framework_router import Framework

    briefing = Briefing(
        symbol="TESTCO",
        keywords=[],
        live_ratios={
            "WC Days": 50.0,  # F1 safety gate passes: 50 <= 90, no veto
            "Stock P/E": 20.0,  # F2 valuation bullish: within 10..40
            "Debt to Equity": 3.0,  # F3 quality bearish: fails <= 1.0
            # profit_growth_3y_pct absent -> F10 abstains
        },
        frameworks=[
            Framework(id="F1", title="WC gate", body=""),
            Framework(id="F2", title="Moat PE band", body=""),
            Framework(id="F3", title="Leverage check", body=""),
            Framework(id="F10", title="Growth threshold", body=""),
        ],
    )

    decision = evaluate(briefing, DECISION_RULES_FIXTURE, METRIC_REGISTRY_FIXTURE)

    assert decision.contradictions != []
    assert "F2" in decision.contradictions[0]
    assert "F3" in decision.contradictions[0]
    assert decision.conviction == "LOW"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py::test_evaluate_reports_contradictions_and_caps_conviction_at_low -v`
Expected: FAIL — `decision.contradictions == []` (never computed) and
`decision.conviction == "MEDIUM"` (Task 5's fallback), not `"LOW"`.

- [ ] **Step 3: Write minimal implementation**

Replace the final fallback `return Decision(..., verdict="HOLD", ...)`
from Task 5's Step 3 with:

```python
    bullish_ids = [fid for fid, v in per_framework_votes.items() if v == "bullish"]
    bearish_ids = [fid for fid, v in per_framework_votes.items() if v == "bearish"]
    contradictions: List[str] = []
    if bullish_ids and bearish_ids:
        contradictions.append(
            f"{', '.join(bullish_ids)} (bullish) vs {', '.join(bearish_ids)} (bearish)"
        )

    weighted_sum = 0.0
    weight_total = 0.0
    for fid, score in framework_scores.items():
        cls = rules[fid].cls
        if cls == "safety_gate":
            continue
        w = _CLASS_WEIGHTS.get(cls, 0.0)
        weighted_sum += w * score
        weight_total += w

    combined_score = weighted_sum / weight_total if weight_total else 0.0

    if combined_score >= 0.7:
        verdict = "BUY"
    elif combined_score < 0.3:
        verdict = "SELL"
    else:
        verdict = "HOLD"

    if contradictions:
        conviction = "LOW"
    elif data_coverage >= 0.8:
        conviction = "HIGH"
    else:
        conviction = "MEDIUM"

    return Decision(
        symbol=symbol,
        verdict=verdict,
        conviction=conviction,
        per_framework_votes=per_framework_votes,
        rule_trail=rule_trail,
        contradictions=contradictions,
        data_coverage=data_coverage,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/test_soic_senses_decision_engine.py -v`
Expected: all tests pass (14 total: 10 original `build_briefing` +
`test_evaluate_veto_caps_verdict_at_avoid_even_when_other_signals_are_bullish`
+ `test_evaluate_missing_metric_abstains_instead_of_crashing` +
`test_evaluate_refuses_with_insufficient_data_when_coverage_is_too_low` +
`test_evaluate_reports_contradictions_and_caps_conviction_at_low`).

- [ ] **Step 5: Commit**

```bash
git add src/soic_senses/decision_engine.py tests/test_soic_senses_decision_engine.py
git commit -m "feat: evaluate() reports contradictions and caps conviction at LOW"
```

---

### Task 7: Full-suite regression check

**Files:** none modified — verification only.

- [ ] **Step 1: Run the entire project test suite**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/ -q`
Expected: `418 passed` (the pre-Phase-A baseline) `+ 10` new tests (4 in
`test_soic_senses_decision_rules.py`, 6 new `evaluate()`-related additions
counted above split as 4 new functions across Tasks 3-6 plus the 2
loader tests from Task 2 — reconcile the exact new count from your own
test run's summary line) `= 428 passed`, plus the same 3 pre-existing,
unrelated `test_storm_cli.py` failures (stale worktree path issue, not
introduced by this plan). If the failure count is anything other than
exactly those 3, stop and investigate before proceeding to Task 8 — do
not carry a regression into the content tasks below.

- [ ] **Step 2: No commit** — this task only verifies; nothing changed.

---

### Task 8: Apply F21-F24 to the real `decision-frameworks-v1.md`

**Files:**
- Modify (vault repo):
  `wiki/personas/soic/frameworks/decision-frameworks-v1.md` — insert after
  line 262 (F20's content, which ends right before the `---` divider at
  line 263) and before the file's final colophon line (currently the
  `*Distilled 2026-07-23 from...*` line) — i.e., insert the new section
  right after the existing `## Known pipeline lesson...` section's
  closing `---` divider, immediately before the colophon paragraph.
- Source (read-only): `docs/superpowers/plans/2026-07-27-soic-framework-f21-f24-draft.md`

- [ ] **Step 1: Copy the F21-F24 sections verbatim**

Open
`/Users/syedamberiqbal/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest/wiki/personas/soic/frameworks/decision-frameworks-v1.md`.
Insert the following, verbatim from the draft file's `## F21.` through
`## F24.` sections (do not re-derive or paraphrase — copy exactly),
preceded by a new divider heading:

```markdown
## Method-course additions (L2-L5, 2026-07-27)

## F21. Cash-conversion / forensic red-flag safety gate

**Model.** Reported profit is an accrual opinion; cash conversion is the reality check. Healthy operators convert operating profit to operating cash at a stable rate -- CFO/EBITDA "should ideally be around 70% for consumer-facing B2C businesses and 60% for B2B businesses" (MODULB 01:58:04-01:58:28). Manipulated revenue breaks this conversion through known mechanisms: channel stuffing and lenient credit trap cash in receivables -- visible as "a spike in trade receivables that are delayed by more than 180 days" (MODULA 00:15:05-00:15:47) -- so "the conversion of operating profit into operating cash flow begins to rapidly decline, which is a major red flag" (MODULB 00:18:31-00:18:48); diluting the mix with traded goods (core manufacturing at 10-15% margin vs ~1% on traded third-party goods) inflates the top line while producing "poor quality of revenues" (MODULB 00:16:40-00:17:34); and burying one-offs in core revenue manufactures fake growth -- Aarti Industries' revenue "inclusive of contract termination [likely fees] of 631 crores" made ~7% underlying PBT growth look like 50-60% (MODULG 00:16:42-00:17:19, MODULG 00:19:38-00:20:02). This is a **veto-class gate**: a failed gate caps the verdict at AVOID regardless of how attractive valuation/growth frameworks look -- it does not generate BUY signals.

**Applies when.** Any non-financial company, before any bullish framework's output is trusted. **Explicitly inapplicable to banks/NBFCs:** their operating cash flow is inherently negative, making the cash flow statement "redundant and void" for these sectors (MODULB 01:54:03-01:55:34) -- lenders are gated by F12 instead.

**Ask.** What is CFO/EBITDA over 3-5 years vs the 70% (B2C) / 60% (B2B) band -- and is the trend deteriorating? Are receivable days rising faster than peers', with any disclosure of receivables outstanding >180 days? Is the traded-goods share of revenue rising at the expense of manufactured margin? Does "revenue from operations" contain one-off items (termination fees, expected compensation booked before cash receipt -- the SpiceJet/Boeing pattern, MODULG 00:20:35-00:21:43) that should sit in exceptional items/other income?

**Live data.** CFO, EBITDA, receivable days multi-year (screener cash-flow + ratios sections -- NOTE: derived from statement tables, not the top-ratios grid `screener_client.py` currently parses; a fetch extension is required), >180-day receivables ageing and traded-vs-manufactured split (annual report/NotebookLM), one-off disclosure (results footnotes/concall).

**Grounding.** `cash-flow-reconciliation-and-working-capital-dynamics` (Module 3), `revenue-manipulation-and-recognition` (Module 4 Forensic Analysis). Legitimate exceptions the gate must respect before vetoing: B2B models holding strategic inventory (MODULA 00:21:18-00:22:08) and B2G receivables stretched by the government as a "notoriously lazy payer" (MODULA 00:22:39-00:22:56) -- high WC there is business model, not fraud; and "interpreting financial statements is an 'imperfect art'" (MODULC 00:37:00-00:37:06), so a single soft quarter is a flag to investigate, not an automatic veto.

## F22. DuPont ROE-quality decomposition gate

**Model.** ROE alone hides *how* the return is produced. DuPont decomposes it into net profit margin x asset turnover x financial leverage (MODULE 00:19:00-00:19:35, MODULH 00:16:35-00:17:39); investors should prefer "an ROE driven by strong profit margins and efficient asset turnover rather than one inflated primarily by debt" (MODULE 00:19:37-00:20:25). Because debt is excluded from the equity denominator, leverage creates an "illusion" -- a mediocre business can print a high ROE right up until "excessive debt can cause the ROE to rapidly collapse or turn negative", as Tata Motors' seemingly high ROE structurally declined while leverage expanded and margins/turns deteriorated (MODULE 00:18:16-00:23:43). The same decomposition powers peer ranking: APL Apollo's ~24.64% ROE comes from ~3x asset turnover plus better margins, while Rama Steel Tubes and Hi-Tech Pipes reach their ROEs "much more heavily [through] financial leverage" (MODULH 01:01:00-01:03:37); Vedant Fashions' 28% ROE is driven by ~31% net margins -- pricing power, not leverage (MODULH 00:46:34-00:47:30).

**Applies when.** Any quality/compounder thesis resting on a headline ROE/ROCE number, and any peer comparison within a sector.

**Ask.** Decompose: what fraction of the ROE comes from margin, turnover, and leverage respectively -- and which component is *trending*? Is the leverage component's contribution rising while margin/turnover flatten (the Tata Motors failure shape)? Versus peers, is this company's ROE the margin/turns kind or the debt kind? **Calibration caveat -- state it, don't fake it:** SOIC states the *direction* (margin/turns good, leverage-driven bad) but no numeric leverage-share ceiling; until a follow-up calibration note derives and documents one, this framework downgrades quality conviction directionally and cannot emit a hard numeric pass/fail.

**Live data.** Net margin, sales, total assets, equity, debt (screener balance-sheet/P&L tables -- beyond the current top-ratios fetch; ROE/ROCE themselves are in top-ratios), multi-year for trend.

**Grounding.** `return-on-equity-roe-and-dupont-analysis` (Module 5 Ratio Analysis). Hard limit: ROE is "highly deceptive in cyclical industries" -- CEAT's ROE collapsed from peak double digits to ~6% purely on raw-material costs (MODULH 00:50:23-01:00:24) -- so for sectors flagged cyclical in the sector overlay this gate must ABSTAIN rather than score, judging the cycle via F5 instead.

## F23. Weinstein Stage-Analysis timing gate (entry / exit / time-stop)

**Model.** Stan Weinstein's four stages tie price/volume structure to EPS momentum -- "a stock price is ultimately a 'slave to earnings growth'" (HOWC 00:31:31, HOWC 01:14:48). Stage 1: sideways base oscillating around the 30-weekly moving average (HOWD 00:22:15-00:23:22). Stage 2 (buyable): breakout above the 30-weekly MA on high volume, fundamentally triggered by a "positive surprise" starting "EPS momentum" (HOWD 00:05:51, HOWC 01:40:19-01:41:14); screen for fresh entries with ADX crossing above 20 and weekly RSI crossing 50 (HOWB 00:01:55-00:02:23). Stage 4 (must-avoid/exit): breakdown below the 30-weekly MA aligned with "loss of EPS momentum" (HOWD 00:26:07, HOWC 01:41:14-01:41:40). The exit is systematic, not discretionary -- sell when **three conditions fire together**: price breaks below the 30-weekly EMA, Relative Strength vs Nifty 50/500 (RS length 26 or 52 weeks) turns negative, and the volatility stop (ATR, length 10, multiplier 2-2.5) turns negative (FRAMEC 01:46:39-01:47:01, FRAMEC 01:52:06-01:52:35, FRAMEC 01:54:57, FRAMEC 01:55:28-01:55:30). Independently, a time stop-loss of 4-8 quarters caps how long capital waits in a fundamentally-fine-but-flat stock (FRAMEC 01:30:22-01:30:56). In a parabolic rise, when price extends more than 70% above the 30-weekly EMA, tighten to a 10-weekly (or 40-daily) MA (FRAMEC 02:01:03-02:02:51).

**Applies when.** Timing an entry into, or a systematic exit from, any stock a fundamental framework already likes -- this gate never originates a thesis; it sequences it. Per the source's own scope limit, the technical exit system is "recommended primarily for 'satellite PF stocks' rather than 'core holdings'" (FRAMEC 01:56:49-01:57:42).

**Ask.** Which stage is the stock in on the weekly chart? For entry: has a Stage-2 breakout printed on high volume with ADX>20 and weekly RSI>50 -- or is the stock still Stage 1 (dead capital risk) or Stage 3/4? For exit: how many of the three triggers (30w-EMA break, negative RS, negative V-stop) are currently firing? Has the position been flat past the chosen 4-8-quarter time stop? Is price >70% extended above the 30-weekly EMA (switch to the tighter MA)?

**Live data.** **Dependency gap -- flagged, not papered over:** this framework needs weekly OHLCV price series (for the 30w/10w EMA, 26/52w RS vs Nifty, ATR V-stop, ADX, weekly RSI, volume), which `screener_client.py` does NOT fetch -- it parses only screener.in's top-ratios grid. Until a price-series source (e.g. NSE bhavcopy/TradingView export) is wired into the senses layer, this framework is evaluable only manually against a charting tool and must ABSTAIN in any automated run.

**Grounding.** `stan-weinstein-s-stage-analysis-framework` (How to Screen & Filter Epic Stocks), `system-based-exits-and-time-stop-losses` (Framework For Buying & Selling A Stock). Known costs and limits, from the sources themselves: the triple-trigger exit surrenders "10% to 25% from the top" (FRAMEC 01:47:39-01:47:44); choppy/sideways markets generate false breakdowns (FRAMEC 01:57:25-01:57:52); Stage 3->4 transitions are often clear only "in hindsight" (HOWD 00:11:45-00:11:50); recent IPOs lack the history for a 30-weekly EMA (FRAMEC 01:58:56-01:59:12); recovering charts face "overhead supply" resistance (HOWD 00:18:01-00:18:59).

## F24. Sector-metric-selection meta-rule (which valuation lens is even valid)

**Model.** A **routing rule, not a bullish/bearish signal**: before any valuation framework (F10, F13) runs, select the metric the sector's accounting actually supports -- using one blanket P/E is like judging an aspiring engineer "by their overall report card percentage" instead of their maths marks (HOWE 00:01:25-00:02:50). The routing table: **banks/financials -> P/B**, because extreme leverage (one unit of equity funding ~ten of assets) makes P/B + ROA/ROE + NPA management the real drivers (HOWC 00:45:35, HOWC 00:48:08-00:51:53); **asset-heavy (hotels, hospitals, QSR, telecom) -> EV/EBITDA**, because 20-40-year assets make accounting depreciation overstate costs and depress P/E (HOWH 00:19:52-00:21:07); **cement -> EV/ton (or EV/EBITDA)**, proxying replacement cost of capacity in a high-debt, cash-generative sector (HOWC 00:58:12-00:58:39); **real estate -> market-cap/pre-sales or "imputed EBITDA"**, because upfront construction costs plus handover-time revenue recognition create optical losses (HOWF 00:42:42-00:44:20); **asset-light IT/FMCG -> plain P/E and cash-flow metrics remain accurate** (HOWC 00:41:22-00:43:01). Output of this framework: the metric key F10's band check should evaluate for this sector -- nothing more.

**Applies when.** Always -- as the first step of any valuation evaluation, resolving the sector overlay before a single multiple is compared to a band.

**Ask.** Which row of the routing table does this company fall in -- and if a conglomerate spans several, has a Sum-of-the-Parts split been done (complex structures carry a "conglomerate discount", HOWD 01:11:34-01:15:25; see also F19)? Is the chosen metric currently distorted by one-off earnings (bulk orders, inventory gains) that "inevitably guarantee a severe derating once the anomaly passes" (HOWH 00:32:09-00:34:12)?

**Live data.** Sector classification (sector overlay / `sector_notebooks.yaml`), then the routed metric's inputs: P/B and NPAs (screener) for financials; EV components -- market cap, debt, cash (screener top-ratios + balance sheet) -- and EBITDA for asset-heavy; capacity tonnage (AR/concall) for cement; pre-sales disclosures (investor PPT/NotebookLM) for real estate.

**Grounding.** `sector-specific-valuation-metrics` (How to Value a Company & Portfolio Creation, merged with the L2 SOIC Screener Sheet walkthrough). **Calibration (dated, and handle with care):** the note's IHCL trailing market-cap/EBITDA of 42 (UPDAT 00:23:59-00:24:53) is a point-in-time worked example, NOT a durable threshold -- per F11 it must never be reused as a band. The UPDAT source passage also carries flagged ASR garbling ("float statement" for a flawed metric, "more depression" for depreciation -- UPDAT 00:06:59, UPDAT 00:24:53-00:25:04), so no numeric threshold may be sourced from that stretch of transcript; and the sheet's own author disclaims stock-picking: "there is no recommendation here" (UPDAT 00:15:31-00:15:38). Also respect: "accounting is an imprecise language" and depreciation excluded by EV/EBITDA "remains a real and eventual expense" (HOWE 00:25:00-00:26:32).

---
```

Then add one sentence to the existing colophon paragraph (the
`*Distilled 2026-07-23 from...*` line) recording this addition, e.g.
append before its closing `*`: `` F21-F24 added 2026-07-27 from the L2-L5
method-course concept notes (Level 5 screening, L4 technicals, Level 3
valuation, Level 2 fundamentals). ``

- [ ] **Step 2: Verify the file parses correctly**

Run:
```bash
/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -c "
from soic_senses.framework_router import load_frameworks
fws = load_frameworks('/Users/syedamberiqbal/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest/wiki/personas/soic/frameworks/decision-frameworks-v1.md')
ids = [f.id for f in fws]
assert ids[-4:] == ['F21', 'F22', 'F23', 'F24'], ids[-4:]
assert fws[-4].title == 'Cash-conversion / forensic red-flag safety gate'
print('OK:', len(fws), 'frameworks, last 4:', ids[-4:])
"
```
Expected: `OK: 24 frameworks, last 4: ['F21', 'F22', 'F23', 'F24']` (no
exception — if `load_frameworks` raises or the assertion fails, the
insertion broke the `## F<n>. <title>` header pattern; re-check the
copy-paste for stray formatting).

- [ ] **Step 3: Commit (vault repo, `main` branch — no branch protection there)**

```bash
cd "/Users/syedamberiqbal/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest"
git add wiki/personas/soic/frameworks/decision-frameworks-v1.md
git commit -m "feat(soic): add F21-F24 -- cash-conversion gate, DuPont quality gate, Weinstein timing gate, sector-metric routing (L2-L5 method courses)"
```

---

### Task 9: Author the real `decision-rules-v2.yaml` + `metric-registry.yaml`

**Files:**
- Create (vault repo): `wiki/personas/soic/frameworks/decision-rules-v2.yaml`
- Create (vault repo): `wiki/personas/soic/frameworks/metric-registry.yaml`

**Interfaces:**
- Consumes: `load_decision_rules`, `load_metric_registry` (Task 2),
  `evaluate` (Tasks 3-6) — this task's verification step exercises all of
  them against real files for the first time.

- [ ] **Step 1: Write `decision-rules-v2.yaml`**

```yaml
# wiki/personas/soic/frameworks/decision-rules-v2.yaml
#
# Phase A pilot rule set for F10, F21-F24 (F12/F13 deferred -- see
# docs/superpowers/plans/2026-07-27-soic-decision-engine-machine-actionable-plan.md
# section 8.1). Never invents a threshold: F22 and F24 ship with zero
# signals below because SOIC states no calibrated number for either yet
# (direction-only for F22; a routing table, not a scored signal, for F24)
# -- see decision-frameworks-v1.md's F22/F24 entries for the full caveat.
- id: F10
  status: machine
  class: valuation
  signals:
    - name: growth_above_embedded
      metric: profit_growth_3y_pct
      rule: ">= 20"
      weight: 0.6
    - name: pe_within_band
      metric: stock_pe
      rule: "between 15 35"
      weight: 0.4
- id: F21
  status: machine
  class: safety_gate
  signals:
    - name: cfo_ebitda_conversion
      metric: cfo_to_ebitda_pct_3y
      rule: ">= 60"
      weight: 1.0
- id: F22
  status: advisory-numeric
  class: quality
  signals: []
- id: F23
  status: machine
  class: timing
  signals:
    - name: stage4_exit_trigger
      metric: weekly_price_series
      rule: "n/a"
      weight: 1.0
- id: F24
  status: machine
  class: routing
  signals: []
```

- [ ] **Step 2: Write `metric-registry.yaml`**

```yaml
# wiki/personas/soic/frameworks/metric-registry.yaml
#
# fetchable = a label screener_client.parse_top_ratios() already returns
# today. not_yet_fetchable = the metric key is defined for a Phase A
# pilot rule but no fetch exists yet -- signals referencing it always
# abstain until a fetch extension is built (Phase B/C, not this plan).
metrics:
  stock_pe:
    label: "Stock P/E"
    status: fetchable
  roce:
    label: "ROCE"
    status: fetchable
  roe:
    label: "ROE"
    status: fetchable
  market_cap:
    label: "Market Cap"
    status: fetchable
  book_value:
    label: "Book Value"
    status: fetchable
  profit_growth_3y_pct:
    label: "Profit growth 3Yr %"
    status: not_yet_fetchable
  cfo_to_ebitda_pct_3y:
    label: "CFO/EBITDA (3yr avg)"
    status: not_yet_fetchable
  receivable_days:
    label: "Receivable Days"
    status: not_yet_fetchable
  net_margin:
    label: "Net Profit Margin"
    status: not_yet_fetchable
  asset_turnover:
    label: "Asset Turnover"
    status: not_yet_fetchable
  debt_to_equity:
    label: "Debt to Equity"
    status: not_yet_fetchable
  weekly_price_series:
    label: "Weekly OHLCV"
    status: not_yet_fetchable
```

- [ ] **Step 3: Verify both files load and `evaluate()` runs against them**

Run:
```bash
/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -c "
import sys
sys.path.insert(0, '/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/soic-method/src')
from soic_senses.decision_engine import Briefing, evaluate
from soic_senses.framework_router import Framework

VAULT = '/Users/syedamberiqbal/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest/wiki/personas/soic/frameworks'

briefing = Briefing(
    symbol='SMOKETEST',
    keywords=[],
    live_ratios={'Stock P/E': 20.0},
    frameworks=[Framework(id='F10', title='DCF sanity + growth-threshold rule', body='')],
)
decision = evaluate(briefing, f'{VAULT}/decision-rules-v2.yaml', f'{VAULT}/metric-registry.yaml')
assert decision.per_framework_votes['F10'] in ('bullish', 'neutral'), decision.per_framework_votes
pe_signal = next(s for s in decision.rule_trail if s.signal == 'pe_within_band')
assert pe_signal.outcome == 'pass', pe_signal
growth_signal = next(s for s in decision.rule_trail if s.signal == 'growth_above_embedded')
assert growth_signal.outcome == 'abstain', growth_signal  # profit_growth_3y_pct is not_yet_fetchable
print('OK — F10 partially evaluable (PE band scored, growth signal abstains as expected)')
"
```
Expected: `OK — F10 partially evaluable (PE band scored, growth signal
abstains as expected)`, no exception. This confirms the loader, the
registry's `not_yet_fetchable` gating, and `evaluate()` all work together
against the real production files, not just the small test fixtures.

- [ ] **Step 4: Commit (vault repo, `main`)**

```bash
cd "/Users/syedamberiqbal/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest"
git add wiki/personas/soic/frameworks/decision-rules-v2.yaml wiki/personas/soic/frameworks/metric-registry.yaml
git commit -m "feat(soic): decision-rules-v2.yaml + metric-registry.yaml -- Phase A pilot (F10, F21-F24)"
```

- [ ] **Step 5: Final full-suite regression check**

Run: `/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.venv/bin/python3 -m pytest tests/ -q`
Expected: same pass count as Task 7 plus zero new failures (nothing in
Task 8/9 touches code, only vault content) — confirms Phase A is complete
and the existing test suite is untouched.

---

## Self-Review

**Spec coverage:** design doc §1 (schema) → Tasks 1, 2, 8, 9. §2/§2.1
(`evaluate()`, `Decision`, `SignalOutcome`) → Tasks 3-6. §6 risk 1
(no fabricated thresholds) → enforced in Task 9 Step 1's comment and F22's
empty `signals: []`. §6 risk 3 (fail loudly on incomplete data) → Task 3's
`data_error` early-return. §7 Phase A "done" gate (citations + human
agreement) → satisfied structurally since F21-F24's text is pre-approved
verbatim from the sign-off draft; the "human agrees with every cell of a
dry-run table" step is Task 9 Step 3's smoke test made concrete for F10,
and is naturally repeatable per-stock once this plan lands. §8.1's five
pilot rules (F10 + 4 new) → Task 9's `decision-rules-v2.yaml`. §9 (ongoing
evolution process) is explicitly a *process* description, not code — no
task implements it because there's nothing to implement; it governs how
Phase B+ re-triggers, out of this plan's scope.

**Placeholder scan:** no TBD/TODO, no "add error handling" without shown
code, every step shows the real diff or the real command + expected
output.

**Type consistency:** `Signal`/`RuleEntry`/`MetricInfo` (Task 1) are used
identically in `load_decision_rules`/`load_metric_registry` (Task 2) and
in `evaluate()` (Task 3+) — same field names (`cls` not `class`, since
`class` is a Python keyword; the YAML key stays `class:` but the loader
maps it to the dataclass field `cls`, consistent everywhere it's read).
`SignalOutcome`/`Decision` field names introduced in Task 3 are reused
unchanged through Tasks 4-6 and in Task 9's smoke test.

## Execution Handoff

Plan complete and saved to
`docs/superpowers/plans/2026-07-27-soic-decision-engine-phase-a.md`. Two
execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per
task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using
executing-plans, batch execution with checkpoints

**Which approach?**
