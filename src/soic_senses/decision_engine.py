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
from soic_senses.screener_client import (
    derive_registry_metrics,
    fetch_screener_ratios,
    fetch_screener_statements,
)
from soic_senses.sector_router import Sector, load_sectors, match_sectors
from soic_senses.tradingview_client import fetch_technicals

# Unified label scheme a merged Briefing.live_ratios uses for TradingView
# fields -- screener.in's own labels ("Stock P/E", "ROCE", ...) are used
# verbatim, so these are named to never collide with anything screener
# returns. metric-registry.yaml's `label:` values must match these exactly
# for evaluate() to ever see a technicals signal as fetchable.
_TECHNICALS_LABELS = {
    "rsi": "RSI (Weekly)",
    "adx": "ADX (Weekly)",
    "ema10": "EMA10 (Weekly)",
    "ema20": "EMA20 (Weekly)",
    "ema30": "EMA30 (Weekly)",
    "ema50": "EMA50 (Weekly)",
    "ema100": "EMA100 (Weekly)",
    "ema200": "EMA200 (Weekly)",
    "close": "TradingView Close (Weekly)",
    "recommendation": "TradingView Recommendation",
    "oscillators_recommendation": "TradingView Oscillators Recommendation",
    "moving_averages_recommendation": "TradingView Moving Averages Recommendation",
}


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
    errors: List[str] = []

    try:
        briefing.live_ratios = fetch_screener_ratios(symbol)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: record, never crash the briefing
        errors.append(str(exc))

    try:
        statements = derive_registry_metrics(fetch_screener_statements(symbol))
    except Exception as exc:  # noqa: BLE001 - independent of the other two sources
        errors.append(str(exc))
    else:
        if briefing.live_ratios is None:
            briefing.live_ratios = dict(statements)
        else:
            # Statement rows never overwrite a top-ratios value: where both
            # publish the same fact, the top-ratios grid is screener's own
            # headline figure and stays authoritative.
            for label, value in statements.items():
                briefing.live_ratios.setdefault(label, value)

    try:
        snapshot = fetch_technicals(symbol)
    except Exception as exc:  # noqa: BLE001 - independent of screener: one source failing must not hide the other's data
        errors.append(str(exc))
    else:
        technicals = {
            label: getattr(snapshot, field)
            for field, label in _TECHNICALS_LABELS.items()
            if getattr(snapshot, field) is not None
        }
        if briefing.live_ratios is None:
            briefing.live_ratios = technicals
        else:
            briefing.live_ratios.update(technicals)

    if errors:
        briefing.data_error = "; ".join(errors)

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


# Classes deliberately excluded from the weighted combination:
#   safety_gate -- vetoes before weighting ever runs (handled above).
#   routing     -- selects WHICH metric a valuation framework should use
#                  (F24); it has no bullish/bearish opinion to weight.
# Any other class is an authoring error and must not be silently zeroed.
_NON_SCORING_CLASSES = {"safety_gate", "routing"}

# GATE-ONLY classes participate in class gating (a weak one caps the verdict)
# but contribute NO additive weight toward a BUY. This is F23's own stated
# scope: it "never originates a thesis; it sequences it." A well-timed chart
# must not add buy-pressure to a thesis the fundamentals have not earned --
# it may only block a badly-timed entry.
_GATE_ONLY_CLASSES = {"timing"}
_CLASS_WEIGHTS = {"valuation": 0.5, "quality": 0.3}

# The score at or above which a framework -- and, under class gating, a whole
# class -- counts as bullish.
_BULLISH_AT = 0.7


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

    # Conditional pattern-warnings a framework's prose authorises without
    # authorising an unconditional gate (F29's growth-trap band). Surfaced to
    # the human, never scored -- see decision_rules.AdvisoryFlag.
    advisory_hits: List[str] = []
    for fid in matched_ids:
        flag = rules[fid].advisory_flag
        if flag is None:
            continue
        metric_info = registry.get(flag.metric)
        if metric_info is None or metric_info.status != "fetchable":
            continue
        raw = briefing.live_ratios.get(metric_info.label) if briefing.live_ratios else None
        if isinstance(raw, (int, float)) and check_rule(float(raw), flag.rule):
            advisory_hits.append(
                f"{fid} advisory flag: {metric_info.label} is {raw} "
                f"({flag.rule}) -- {flag.message}"
            )

    # A safety gate that could not be evaluated must never vanish silently --
    # otherwise a veto-class framework whose metric isn't fetchable lets a
    # confident BUY through with nothing in the Decision saying the gate
    # never ran (the F21-on-POLYCAB hole).
    unresolved: List[str] = list(advisory_hits)
    abstained_gates = sorted(
        fid
        for fid in matched_ids
        if rules[fid].cls == "safety_gate" and per_framework_votes.get(fid) == "abstain"
    )
    if abstained_gates:
        unresolved.append(
            f"Safety gate(s) {', '.join(abstained_gates)} could not be evaluated "
            "(metric not fetchable) -- verify manually before acting."
        )

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
            unresolved_human_questions=unresolved,
            data_coverage=data_coverage,
        )

    # Contradictions are computed BEFORE the coverage floor so an
    # INSUFFICIENT_DATA verdict still reports a disagreement its own votes
    # show -- the POLYCAB v1 defect, where F10-bearish vs F23-bullish never
    # reached the field built to surface it.
    bullish_ids = [fid for fid, v in per_framework_votes.items() if v == "bullish"]
    bearish_ids = [fid for fid, v in per_framework_votes.items() if v == "bearish"]
    contradictions: List[str] = []
    if bullish_ids and bearish_ids:
        contradictions.append(
            f"{', '.join(bullish_ids)} (bullish) vs {', '.join(bearish_ids)} (bearish)"
        )

    if data_coverage < 0.5:
        return Decision(
            symbol=symbol,
            verdict="INSUFFICIENT_DATA",
            conviction="LOW",
            per_framework_votes=per_framework_votes,
            rule_trail=rule_trail,
            contradictions=contradictions,
            unresolved_human_questions=unresolved,
            data_coverage=data_coverage,
        )

    weighted_sum = 0.0
    weight_total = 0.0
    class_scores: Dict[str, List[float]] = {}
    for fid, score in framework_scores.items():
        cls = rules[fid].cls
        if cls in _NON_SCORING_CLASSES:
            continue
        # Gate-only classes enter class_scores (so they can cap) but never
        # weighted_sum (so they cannot push toward BUY).
        class_scores.setdefault(cls, []).append(score)
        if cls in _GATE_ONLY_CLASSES:
            continue
        w = _CLASS_WEIGHTS[cls]  # KeyError, not a silent 0.0 -- see above
        weighted_sum += w * score
        weight_total += w

    combined_score = weighted_sum / weight_total if weight_total else 0.0

    if combined_score >= 0.7:
        verdict = "BUY"
    elif combined_score < 0.3:
        verdict = "SELL"
    else:
        verdict = "HOLD"

    # Conjunctive class gating. Additive weighted averaging is the wrong
    # algebra for a method whose essence is "wonderful business AND fair
    # price": quality frameworks structurally outnumber valuation ones
    # (prose rarely states a valuation number), so any additive scheme lets
    # quality outvote price forever -- the POLYCAB defect, where nine
    # passing quality/growth signals produced BUY/HIGH at a P/E of 47.
    # So a BUY additionally requires EVERY evaluated class to clear the same
    # bar on its own; a class below it caps the verdict at HOLD and is named.
    # This invents no threshold: it reuses the existing 0.7 constant, and the
    # no-invented-thresholds rule governs financial signals sourced from the
    # framework prose, not the engine's aggregation design.
    failing_classes = sorted(
        cls
        for cls, scores in class_scores.items()
        if sum(scores) / len(scores) < _BULLISH_AT
    )
    if failing_classes:
        detail = ", ".join(
            f"{cls} class scored "
            f"{sum(class_scores[cls]) / len(class_scores[cls]):.2f}"
            for cls in failing_classes
        )
        if verdict == "BUY":
            verdict = "HOLD"
            unresolved.append(
                f"Capped at HOLD: {detail} (below the {_BULLISH_AT:.1f} bar) while "
                "other classes were strong. A BUY requires every evaluated class to "
                "clear it independently."
            )
        else:
            # Not verdict-changing here, but still the reason a BUY is out of
            # reach -- report it rather than leaving the caller to infer it.
            unresolved.append(
                f"{detail} (below the {_BULLISH_AT:.1f} bar) -- a BUY would require "
                "every evaluated class to clear it independently."
            )

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
        unresolved_human_questions=unresolved,
        data_coverage=data_coverage,
    )
