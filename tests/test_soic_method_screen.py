from soic_method.models import Rule
from soic_method.screen import (
    BINDINGS,
    CompanyMetrics,
    evaluate_rule,
    screen,
    unbound_rules,
)


def _rule(key, value, op="gte"):
    return Rule(tier="graded", kind="threshold", stage="screen",
                rule_key=key, operator=op, value=value, status="active")


SALES = _rule("screen.sales_growth.floor", 15)
PAT = _rule("screen.pat_growth.floor", 20)
ROC = _rule("screen.roc.floor", 15)
MCAP = _rule("screen.market_cap.floor", 1000)


def test_bound_rule_passes_when_metric_clears_threshold():
    m = CompanyMetrics(company_code="X", sales_growth_pct=22.0)
    assert evaluate_rule(SALES, m).verdict == "pass"


def test_bound_rule_fails_when_metric_misses_threshold():
    m = CompanyMetrics(company_code="X", sales_growth_pct=9.0)
    assert evaluate_rule(SALES, m).verdict == "fail"


def test_unbound_rule_is_unknown_never_fail():
    # ROC has no platform column. A company must NOT be excluded for it --
    # that would be a data outage masquerading as a screen result.
    m = CompanyMetrics(company_code="X", sales_growth_pct=50.0)
    out = evaluate_rule(ROC, m)
    assert out.verdict == "unknown"
    assert "unbound" in out.reason


def test_missing_data_on_a_bound_rule_is_unknown_not_fail():
    m = CompanyMetrics(company_code="X", market_cap_cr=None)
    assert evaluate_rule(MCAP, m).verdict == "unknown"


def test_roc_is_deliberately_absent_from_bindings():
    assert "screen.roc.floor" not in BINDINGS
    assert unbound_rules([SALES, PAT, ROC, MCAP]) == ["screen.roc.floor"]


def test_company_with_an_unknown_does_not_count_as_passing():
    m = CompanyMetrics(company_code="X", sales_growth_pct=50.0,
                       pat_growth_pct=50.0, market_cap_cr=5000.0)
    res = screen([SALES, PAT, ROC, MCAP], [m])[0]
    assert res.passes is False      # ROC unknown -> not a pass
    assert res.partial is True


def test_fully_evaluable_company_passes():
    m = CompanyMetrics(company_code="X", sales_growth_pct=50.0,
                       pat_growth_pct=50.0, market_cap_cr=5000.0)
    res = screen([SALES, PAT, MCAP], [m])[0]
    assert res.passes is True
    assert res.partial is False


def _pe_ceiling():
    """The human-resolved P/E rule: a <=40 CEILING.

    Resolved 2026-07-21 (configs/resolutions.yaml), keeping "i can do less
    than 40" over "pe ratio is between 15 to 30". Effectively a 0-40 band,
    since UNIVERSE_SQL never emits a non-positive P/E.
    """
    return Rule(tier="graded", kind="threshold", stage="screen",
                rule_key="screen.pe.ceiling", operator="lte", value=40,
                status="active")


def test_pe_under_the_ceiling_passes():
    m = CompanyMetrics(company_code="X", pe_ratio=22.0)
    assert evaluate_rule(_pe_ceiling(), m).verdict == "pass"


def test_pe_above_the_ceiling_fails():
    m = CompanyMetrics(company_code="X", pe_ratio=41.0)
    assert evaluate_rule(_pe_ceiling(), m).verdict == "fail"


def test_low_pe_passes_because_a_ceiling_does_not_exclude_cheapness():
    # This is the behaviour change from the superseded 15-30 band, which
    # rejected a P/E of 9 as "too cheap". A ceiling cuts only the expensive
    # end -- the correct reading of "less than 40".
    m = CompanyMetrics(company_code="X", pe_ratio=9.0)
    assert evaluate_rule(_pe_ceiling(), m).verdict == "pass"


def test_pe_exactly_at_the_ceiling_passes():
    # "less than 40" is implemented as <= 40. Pinned so the boundary is a
    # decision on the record rather than an accident of the operator choice.
    m = CompanyMetrics(company_code="X", pe_ratio=40.0)
    assert evaluate_rule(_pe_ceiling(), m).verdict == "pass"


def test_pe_is_unknown_when_earnings_are_negative():
    # UNIVERSE_SQL emits NULL P/E for loss-makers (TTM EPS <= 0). A loss-maker
    # must not screen as "cheap" -- it has no meaningful P/E at all. This is
    # also what makes the <=40 ceiling equivalent to the requested 0-40 band.
    m = CompanyMetrics(company_code="X", pe_ratio=None)
    assert evaluate_rule(_pe_ceiling(), m).verdict == "unknown"


def test_pe_is_now_bound_but_roc_still_is_not():
    assert "screen.pe.ceiling" in BINDINGS
    assert "screen.roc.floor" not in BINDINGS


def test_abb_reported_pat_growth_passes_while_normalised_reality_fails():
    """The documented ABB Q1-CY26 case, from stock_analyzer's CLAUDE.md.

    Reported PAT YoY was +275.6%, driven by a ~Rs 1,350cr EXCEPTIONAL gain.
    The normalised figure was about -18%. Both are 'real' numbers; screening
    on the reported one admits a company whose underlying business shrank.

    The screen cannot tell these apart -- quarterly_financials stores
    as-reported figures by an explicit product decision ("screener wins,
    reported as-is"). This test pins that limitation so it is visible rather
    than discovered later against real money.
    """
    reported = CompanyMetrics(company_code="ABB", pat_growth_pct=275.6)
    normalised = CompanyMetrics(company_code="ABB", pat_growth_pct=-18.0)
    assert evaluate_rule(PAT, reported).verdict == "pass"
    assert evaluate_rule(PAT, normalised).verdict == "fail"
