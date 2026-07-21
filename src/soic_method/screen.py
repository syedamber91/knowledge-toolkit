"""Bind extracted rules to real platform columns and screen companies.

This is the layer the spec calls `binding`: a rule is only executable if it
resolves to a field that actually exists in `stock_analyzer`'s Postgres.

Verified against `database/migrations/` on 2026-07-21:

    screen.sales_growth.floor -> quarterly_financials.revenue     (YoY)   DERIVED
    screen.pat_growth.floor   -> quarterly_financials.net_profit  (YoY)   DERIVED
    screen.market_cap.floor   -> company_registry.market_cap_cr           BOUND
    screen.roc.floor          -> (no column exists)                       UNBOUND

**A company is never excluded for a metric we cannot measure.** An unbound rule
evaluates to UNKNOWN, not FAIL. Silently dropping companies for missing ROC data
would look like a screen result and actually be a data outage — the same class of
error the extraction gates exist to prevent, one layer down.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .models import Rule

PASS = "pass"
FAIL = "fail"
UNKNOWN = "unknown"

# rule_key -> the metric field on CompanyMetrics that satisfies it.
# A key absent here is UNBOUND: no platform column can answer it.
BINDINGS: Dict[str, str] = {
    "screen.sales_growth.floor": "sales_growth_pct",
    "screen.pat_growth.floor": "pat_growth_pct",
    "screen.market_cap.floor": "market_cap_cr",
    # "screen.roc.floor" deliberately absent — no ROC/ROCE column exists in
    # any migration. Recorded in gaps.md rather than silently approximated.
}


class CompanyMetrics(BaseModel):
    company_code: str
    sales_growth_pct: Optional[float] = None
    pat_growth_pct: Optional[float] = None
    market_cap_cr: Optional[float] = None
    roc_pct: Optional[float] = None      # always None until a column exists


class RuleOutcome(BaseModel):
    rule_key: Optional[str]
    verdict: str                          # pass | fail | unknown
    reason: str = ""


class CompanyResult(BaseModel):
    company_code: str
    outcomes: List[RuleOutcome] = Field(default_factory=list)

    @property
    def passes(self) -> bool:
        """Passes only if every evaluable rule passed AND none were unknown.

        Deliberately strict: a company we could not fully evaluate is not a
        company that passed. `partial` distinguishes the two.
        """
        return bool(self.outcomes) and all(o.verdict == PASS for o in self.outcomes)

    @property
    def partial(self) -> bool:
        return any(o.verdict == UNKNOWN for o in self.outcomes)


def _compare(value: float, operator: Optional[str], target: float) -> bool:
    if operator == "gte":
        return value >= target
    if operator == "gt":
        return value > target
    if operator == "lte":
        return value <= target
    if operator == "lt":
        return value < target
    if operator == "eq":
        return value == target
    raise ValueError("unsupported operator %r" % operator)


def evaluate_rule(rule: Rule, metrics: CompanyMetrics) -> RuleOutcome:
    field = BINDINGS.get(rule.rule_key or "")
    if field is None:
        return RuleOutcome(rule_key=rule.rule_key, verdict=UNKNOWN,
                           reason="unbound: no platform column for this rule")

    value = getattr(metrics, field, None)
    if value is None:
        return RuleOutcome(rule_key=rule.rule_key, verdict=UNKNOWN,
                           reason="no data for %s" % field)

    if rule.value_range is not None:
        ok = rule.value_range.min <= value <= rule.value_range.max
        return RuleOutcome(rule_key=rule.rule_key, verdict=PASS if ok else FAIL,
                           reason="%s=%s vs [%s, %s]" % (field, value,
                                                         rule.value_range.min,
                                                         rule.value_range.max))
    if rule.value is None:
        return RuleOutcome(rule_key=rule.rule_key, verdict=UNKNOWN,
                           reason="rule carries no comparable value")

    ok = _compare(value, rule.operator, rule.value)
    return RuleOutcome(rule_key=rule.rule_key, verdict=PASS if ok else FAIL,
                       reason="%s=%s %s %s" % (field, value, rule.operator, rule.value))


def screen(rules: List[Rule], universe: List[CompanyMetrics]) -> List[CompanyResult]:
    out: List[CompanyResult] = []
    for m in universe:
        out.append(CompanyResult(
            company_code=m.company_code,
            outcomes=[evaluate_rule(r, m) for r in rules],
        ))
    return out


def unbound_rules(rules: List[Rule]) -> List[str]:
    """Rule keys the platform cannot currently answer. Feeds gaps.md."""
    return [r.rule_key for r in rules
            if (r.rule_key or "") not in BINDINGS and r.rule_key]


# --- SQL --------------------------------------------------------------------
# Produces the CompanyMetrics universe from the real schema. YoY windows mirror
# `_fetch_financials_screener`'s existing 330-400 day convention so this screen
# and the quarterly board agree on what "a year ago" means.

UNIVERSE_SQL = """
WITH latest AS (
    SELECT DISTINCT ON (company_code)
           company_code, period_end, revenue, net_profit
      FROM quarterly_financials
     ORDER BY company_code, period_end DESC
),
prior AS (
    SELECT DISTINCT ON (l.company_code)
           l.company_code, q.revenue AS prev_revenue, q.net_profit AS prev_net_profit
      FROM latest l
      JOIN quarterly_financials q
        ON q.company_code = l.company_code
       AND q.period_end BETWEEN l.period_end - INTERVAL '400 days'
                            AND l.period_end - INTERVAL '330 days'
     ORDER BY l.company_code, q.period_end DESC
)
SELECT r.company_code,
       CASE WHEN p.prev_revenue > 0
            THEN (l.revenue - p.prev_revenue) / p.prev_revenue * 100 END
           AS sales_growth_pct,
       CASE WHEN p.prev_net_profit > 0
            THEN (l.net_profit - p.prev_net_profit) / p.prev_net_profit * 100 END
           AS pat_growth_pct,
       r.market_cap_cr,
       NULL::numeric AS roc_pct   -- no ROC/ROCE column exists; see gaps.md
  FROM company_registry r
  JOIN latest l ON l.company_code = r.company_code
  LEFT JOIN prior p ON p.company_code = r.company_code
 WHERE r.active IS TRUE
"""


def fetch_universe(conn) -> List[CompanyMetrics]:
    """Run UNIVERSE_SQL against a live psycopg connection.

    Untested against production — the VPS was unreachable when this landed.
    The pure-Python screening logic above is fully tested; this function is the
    only part that needs a live database to validate.
    """
    with conn.cursor() as cur:
        cur.execute(UNIVERSE_SQL)
        cols = [d[0] for d in cur.description]
        return [CompanyMetrics(**dict(zip(cols, row))) for row in cur.fetchall()]
