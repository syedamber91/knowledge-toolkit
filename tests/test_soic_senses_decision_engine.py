from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

FRAMEWORKS_FIXTURE = Path(__file__).parent / "fixtures" / "frameworks_sample.md"
SECTOR_REGISTRY_FIXTURE = Path(__file__).parent / "fixtures" / "sector_notebooks_sample.yaml"

# A technicals fetch that contributes nothing to live_ratios (every field
# None) -- used by tests that only care about screener behavior, so the
# now-unconditional fetch_technicals() call doesn't perturb their asserts.
_EMPTY_SNAPSHOT = SimpleNamespace(
    recommendation=None,
    oscillators_recommendation=None,
    moving_averages_recommendation=None,
    rsi=None,
    adx=None,
    ema10=None,
    ema20=None,
    ema30=None,
    ema50=None,
    ema100=None,
    ema200=None,
    close=None,
)


def test_build_briefing_includes_live_ratios_when_fetch_succeeds():
    from soic_senses.decision_engine import build_briefing

    fake_ratios = {"Stock P/E": 15.0, "ROCE": 63.0}
    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value=fake_ratios
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(
            symbol="TCS",
            keywords=["DCF", "intrinsic value"],
            frameworks_path=FRAMEWORKS_FIXTURE,
        )

    assert briefing.symbol == "TCS"
    assert briefing.live_ratios == fake_ratios
    assert briefing.data_error is None


def test_build_briefing_selects_matching_frameworks():
    from soic_senses.decision_engine import build_briefing

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value={}
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(
            symbol="TCS",
            keywords=["DCF", "intrinsic value", "growth"],
            frameworks_path=FRAMEWORKS_FIXTURE,
        )

    assert [f.id for f in briefing.frameworks] == ["F10"]


def test_build_briefing_records_data_error_instead_of_crashing_when_fetch_fails():
    from soic_senses.decision_engine import build_briefing
    from soic_senses.screener_client import CompanyNotFoundError

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios",
        side_effect=CompanyNotFoundError("no page for XYZ"),
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(symbol="XYZ", keywords=["DCF"], frameworks_path=FRAMEWORKS_FIXTURE)

    # Screener failed, but the (empty) technicals merge still initializes
    # live_ratios to a dict rather than leaving it None -- an empty dict is
    # still falsy, so to_markdown()'s "(no ratios returned)" branch and the
    # data_error surfacing are unaffected; see the next two tests for the
    # cross-source independence this enables.
    assert briefing.live_ratios == {}
    assert "no page for XYZ" in briefing.data_error


def test_briefing_to_markdown_never_hides_a_data_fetch_failure():
    from soic_senses.decision_engine import build_briefing
    from soic_senses.screener_client import IncompleteRatiosError

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios",
        side_effect=IncompleteRatiosError("blank ratios"),
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(symbol="VENUSPIPES", keywords=["BHEL"], frameworks_path=FRAMEWORKS_FIXTURE)

    md = briefing.to_markdown()
    assert "blank ratios" in md
    assert "VENUSPIPES" in md


def test_build_briefing_without_sector_registry_path_has_no_sectors():
    from soic_senses.decision_engine import build_briefing

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value={}
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(symbol="TCS", keywords=["DCF"], frameworks_path=FRAMEWORKS_FIXTURE)

    assert briefing.sectors == []


def test_build_briefing_matches_sectors_when_registry_path_given():
    from soic_senses.decision_engine import build_briefing

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value={}
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(
            symbol="NAVINFLUOR",
            keywords=["fluorine", "srf"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    assert [s.slug for s in briefing.sectors] == ["fluorine-industry-megatrend-or-fad"]


def test_build_briefing_sector_matching_does_not_disturb_framework_matching():
    from soic_senses.decision_engine import build_briefing

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value={}
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(
            symbol="TCS",
            keywords=["DCF", "intrinsic value", "growth"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    assert [f.id for f in briefing.frameworks] == ["F10"]
    assert briefing.sectors == []


def test_briefing_to_markdown_includes_sector_context_section():
    from soic_senses.decision_engine import build_briefing

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value={}
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        briefing = build_briefing(
            symbol="NAVINFLUOR",
            keywords=["fluorine"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    md = briefing.to_markdown()
    assert "## Applicable Sector Context" in md
    assert "Fluorine Industry" in md


def test_adding_a_second_unrelated_sector_does_not_crowd_out_the_first():
    """Evolutionary-behavior test: as configs/sector_notebooks.yaml grows,
    decision_engine needs no further code change -- each sector is still
    independently discoverable by its own keywords."""
    from soic_senses.decision_engine import build_briefing

    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value={}
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=_EMPTY_SNAPSHOT):
        real_estate_briefing = build_briefing(
            symbol="DLF",
            keywords=["real estate", "joint development"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )
        fluorine_briefing = build_briefing(
            symbol="NAVINFLUOR",
            keywords=["fluorine", "navin fluorine"],
            frameworks_path=FRAMEWORKS_FIXTURE,
            sector_registry_path=SECTOR_REGISTRY_FIXTURE,
        )

    assert [s.slug for s in real_estate_briefing.sectors] == ["detailed-analysis-of-real-estate-sector"]
    assert [s.slug for s in fluorine_briefing.sectors] == ["fluorine-industry-megatrend-or-fad"]


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


def test_build_briefing_merges_tradingview_technicals_into_live_ratios_under_unified_labels():
    from soic_senses.decision_engine import build_briefing

    fake_ratios = {"Stock P/E": 15.0, "ROCE": 63.0}
    fake_snapshot = SimpleNamespace(
        recommendation="BUY",
        oscillators_recommendation="NEUTRAL",
        moving_averages_recommendation="BUY",
        rsi=55.3,
        adx=27.1,
        ema10=1310.0,
        ema20=1300.0,
        ema30=1290.0,
        ema50=1270.0,
        ema100=1200.0,
        ema200=1100.0,
        close=1320.0,
    )
    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value=fake_ratios
    ), patch(
        "soic_senses.decision_engine.fetch_technicals", return_value=fake_snapshot
    ) as mock_fetch_technicals:
        briefing = build_briefing(symbol="TCS", keywords=["DCF"], frameworks_path=FRAMEWORKS_FIXTURE)

    mock_fetch_technicals.assert_called_once_with("TCS")
    assert briefing.live_ratios["Stock P/E"] == 15.0
    assert briefing.live_ratios["ROCE"] == 63.0
    assert briefing.live_ratios["RSI (Weekly)"] == 55.3
    assert briefing.live_ratios["ADX (Weekly)"] == 27.1
    assert briefing.live_ratios["EMA10 (Weekly)"] == 1310.0
    assert briefing.live_ratios["EMA30 (Weekly)"] == 1290.0
    assert briefing.live_ratios["EMA200 (Weekly)"] == 1100.0
    assert briefing.live_ratios["TradingView Recommendation"] == "BUY"
    assert briefing.data_error is None


def test_build_briefing_records_technicals_error_without_losing_screener_data():
    from soic_senses.decision_engine import build_briefing
    from soic_senses.tradingview_client import TechnicalsUnavailableError

    fake_ratios = {"Stock P/E": 15.0}
    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios", return_value=fake_ratios
    ), patch(
        "soic_senses.decision_engine.fetch_technicals",
        side_effect=TechnicalsUnavailableError("no analysis for XYZ"),
    ):
        briefing = build_briefing(symbol="XYZ", keywords=["DCF"], frameworks_path=FRAMEWORKS_FIXTURE)

    assert briefing.live_ratios["Stock P/E"] == 15.0
    assert "RSI (Weekly)" not in briefing.live_ratios
    assert "no analysis for XYZ" in briefing.data_error


def test_build_briefing_records_screener_error_without_losing_technicals_data():
    from soic_senses.decision_engine import build_briefing
    from soic_senses.screener_client import CompanyNotFoundError

    fake_snapshot = SimpleNamespace(
        recommendation="SELL",
        oscillators_recommendation="SELL",
        moving_averages_recommendation="SELL",
        rsi=40.0,
        adx=None,
        ema10=None,
        ema20=None,
        ema30=None,
        ema50=None,
        ema100=None,
        ema200=None,
        close=None,
    )
    with patch(
        "soic_senses.decision_engine.fetch_screener_ratios",
        side_effect=CompanyNotFoundError("no page for XYZ"),
    ), patch("soic_senses.decision_engine.fetch_technicals", return_value=fake_snapshot):
        briefing = build_briefing(symbol="XYZ", keywords=["DCF"], frameworks_path=FRAMEWORKS_FIXTURE)

    assert briefing.live_ratios["RSI (Weekly)"] == 40.0
    assert "no page for XYZ" in briefing.data_error


def test_evaluate_caps_at_hold_when_one_class_fails_even_if_others_are_strong():
    """Conjunctive class gating (the POLYCAB BUY/HIGH defect, 2026-07-28).

    Additive weighted averaging is the wrong algebra for a method whose
    essence is "wonderful business AND fair price": quality frameworks
    structurally outnumber valuation ones, so any additive scheme lets
    quality outvote price forever. Every evaluated class must clear the
    same 0.7 bar for a BUY -- a class below it caps the verdict at HOLD
    and is named in the decision.
    """
    from soic_senses.decision_engine import Briefing, evaluate
    from soic_senses.framework_router import Framework

    briefing = Briefing(
        symbol="TESTCO",
        keywords=[],
        live_ratios={
            "Stock P/E": 90.0,        # F2 valuation FAILS its 10..40 band
            "Debt to Equity": 0.1,    # F3 quality passes <= 1.0
            "WC Days": 50.0,          # F1 safety gate passes <= 90
        },
        frameworks=[
            Framework(id="F1", title="WC gate", body=""),
            Framework(id="F2", title="Moat PE band", body=""),
            Framework(id="F3", title="Leverage check", body=""),
        ],
    )

    decision = evaluate(briefing, DECISION_RULES_FIXTURE, METRIC_REGISTRY_FIXTURE)

    # Quality is perfect and the safety gate passes, but valuation is 0.0 --
    # the verdict must not reach BUY on the strength of the other classes.
    assert decision.verdict == "HOLD"
    assert any("valuation" in q for q in decision.unresolved_human_questions)


def test_evaluate_still_reaches_buy_when_every_class_clears_the_bar():
    from soic_senses.decision_engine import Briefing, evaluate
    from soic_senses.framework_router import Framework

    briefing = Briefing(
        symbol="TESTCO",
        keywords=[],
        live_ratios={
            "Stock P/E": 20.0,        # F2 valuation passes 10..40
            "Debt to Equity": 0.1,    # F3 quality passes
            "WC Days": 50.0,          # F1 safety gate passes
        },
        frameworks=[
            Framework(id="F1", title="WC gate", body=""),
            Framework(id="F2", title="Moat PE band", body=""),
            Framework(id="F3", title="Leverage check", body=""),
        ],
    )

    decision = evaluate(briefing, DECISION_RULES_FIXTURE, METRIC_REGISTRY_FIXTURE)

    assert decision.verdict == "BUY"
    assert decision.unresolved_human_questions == []
