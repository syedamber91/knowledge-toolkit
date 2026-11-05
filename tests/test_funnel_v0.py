import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "funnel_v0", pathlib.Path(__file__).parents[1] / "scripts" / "funnel_v0.py"
)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def test_shortlist_needs_candidate_and_concall_and_annual_report():
    verdicts = {"A": "CANDIDATE", "B": "CANDIDATE", "C": "WATCH", "D": "CANDIDATE"}
    docs = {"A": (4, 1), "B": (4, 0), "C": (4, 1), "D": (0, 1)}
    assert f.shortlist(verdicts, docs) == ["A"]


def test_first_failed_gate_picks_earliest_gate_not_pass():
    rows = [
        ("G3", "capital_efficiency_gate-001", "FAIL", 3.6, ">= 15"),
        ("G0", "canslim_sales-001", "FAIL", 9.9, ">= 15"),
        ("G1", "leverage-001", "PASS", 0.1, "<= 0.7"),
    ]
    assert f.first_not_pass(rows) == ("G0", "canslim_sales-001", "FAIL", 9.9, ">= 15")


def test_first_not_pass_none_when_all_pass():
    assert f.first_not_pass([("G0", "x", "PASS", 1, ">= 0")]) is None


def test_random_control_is_seeded_and_size_3():
    pool = [f"C{i}" for i in range(13)]
    a, b = f.random_control(pool, 3, seed=7), f.random_control(pool, 3, seed=7)
    assert a == b and len(a) == 3 and set(a) <= set(pool)


def test_no_advice_words():
    assert f.has_advice_words("we say Buy this") is True
    assert f.has_advice_words("shortlist to read") is False
