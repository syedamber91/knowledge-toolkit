"""Orchestrates the senses (screener) + the framework layer into one briefing.

Deliberately does NOT write the verdict. Both the Venus Pipes and KEI
Industries experiments showed the reasoning -- picking the right framework,
connecting it to the specific numbers, weighing the risk -- is where the
actual value is, and that's a judgment step for a human or an LLM call, not
something to freeze into a template. This module automates only the
mechanical part: fetch what's live, surface which frameworks apply, and
assemble both into one document that reasoning step can start from instead
of a blank page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

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


@dataclass
class Briefing:
    symbol: str
    keywords: List[str]
    live_ratios: Optional[Dict[str, object]] = None
    data_error: Optional[str] = None
    frameworks: List[Framework] = field(default_factory=list)
    sectors: List[Sector] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# Decision Briefing — {self.symbol}", ""]

        lines.append("## Live Data (screener.in)")
        if self.data_error is not None:
            lines.append(f"**FETCH FAILED:** {self.data_error}")
            lines.append(
                "No live numbers are available below -- do not substitute a "
                "wiki value or an estimate; re-fetch or source manually before "
                "using any framework that needs a number."
            )
        elif self.live_ratios:
            for label, value in self.live_ratios.items():
                lines.append(f"- **{label}:** {value}")
        else:
            lines.append("(no ratios returned)")
        lines.append("")

        lines.append("## Applicable Frameworks")
        if self.frameworks:
            for fw in self.frameworks:
                lines.append(f"### {fw.id}. {fw.title}")
                lines.append(fw.body)
                lines.append("")
        else:
            lines.append("(no framework matched the given keywords)")

        lines.append("## Applicable Sector Context")
        if self.sectors:
            for sector in self.sectors:
                lines.append(f"### {sector.title}")
                lines.append(f"NotebookLM notebook: `{sector.notebook_id}`")
                lines.append("")
        else:
            lines.append("(no sector notebook matched the given keywords)")

        return "\n".join(lines)


def build_briefing(
    symbol: str,
    keywords: List[str],
    frameworks_path: Union[str, Path],
    sector_registry_path: Optional[Union[str, Path]] = None,
) -> Briefing:
    """Fetch live ratios + match frameworks + match sector notebooks for one
    company.

    A screener fetch failure is recorded on the briefing (data_error), never
    raised past this point -- the caller still gets the framework matches
    even when the data layer is down, and to_markdown() surfaces the failure
    loudly rather than silently proceeding with no numbers.

    sector_registry_path is optional (default None -> skip sector matching
    entirely, so existing callers that don't pass it are unaffected). When
    given, sectors are matched the same way frameworks are: growing
    configs/sector_notebooks.yaml is the only wiring a new sector needs --
    this function never changes again as more sectors are registered.
    """
    briefing = Briefing(symbol=symbol, keywords=keywords)

    try:
        briefing.live_ratios = fetch_screener_ratios(symbol)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: record, never crash the briefing
        briefing.data_error = str(exc)

    frameworks = load_frameworks(frameworks_path)
    briefing.frameworks = match_frameworks(frameworks, keywords)

    if sector_registry_path is not None:
        sectors = load_sectors(sector_registry_path)
        briefing.sectors = match_sectors(sectors, keywords)

    return briefing


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
