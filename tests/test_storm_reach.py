"""Offline tests for the STORM Agent Reach layer.

Every test injects the `run` / `which` seams, so the suite needs no Agent Reach
install, no credentials and no network -- the same discipline instagram_toolkit
uses for its `post_fetch` seam.
"""

import json
from pathlib import Path

from storm_core import config, reach

REGISTRY = """
version: 1
pinned_ref: "abc1234"
channels:
  - name: exa
    label: Exa search
    requires_auth: false
    argv: ["reach_exa", "{query}", "--limit", "{limit}"]
  - name: x
    label: X search
    requires_auth: true
    argv: ["reach_twitter", "search", "{query}"]
  - name: legacy
    label: disabled channel
    enabled: false
    argv: ["reach_legacy"]
"""


def _registry(tmp_path: Path) -> Path:
    p = tmp_path / "reach_channels.yaml"
    p.write_text(REGISTRY, encoding="utf-8")
    return p


def _which_all(_name):
    return "/usr/local/bin/" + _name


def _which_none(_name):
    return None


# --- registry --------------------------------------------------------------

def test_load_channels_parses_registry(tmp_path):
    chans = reach.load_channels(_registry(tmp_path))
    assert [c.name for c in chans] == ["exa", "x", "legacy"]
    assert chans[1].requires_auth is True
    assert chans[2].enabled is False


def test_missing_registry_is_absent_safe(tmp_path):
    assert reach.load_channels(tmp_path / "nope.yaml") == []
    assert reach.pinned_ref(tmp_path / "nope.yaml") == ""


def test_malformed_registry_does_not_raise(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("channels: [ this is not: valid: yaml", encoding="utf-8")
    assert reach.load_channels(bad) == []


def test_pinned_ref_is_read(tmp_path):
    assert reach.pinned_ref(_registry(tmp_path)) == "abc1234"


# --- probe -----------------------------------------------------------------

def test_probe_reports_available_when_executable_resolves(tmp_path):
    statuses = {s.name: s for s in reach.probe(path=_registry(tmp_path), which=_which_all)}
    assert statuses["exa"].available is True
    assert statuses["exa"].executable.endswith("reach_exa")
    assert statuses["legacy"].available is False
    assert statuses["legacy"].reason == "disabled in registry"


def test_probe_reports_reason_when_not_installed(tmp_path):
    statuses = {s.name: s for s in reach.probe(path=_registry(tmp_path), which=_which_none)}
    assert statuses["x"].available is False
    assert "not on PATH" in statuses["x"].reason


def test_probe_can_be_narrowed_to_a_subset(tmp_path):
    statuses = reach.probe(["exa"], path=_registry(tmp_path), which=_which_all)
    assert [s.name for s in statuses] == ["exa"]


# --- search: the absent-safe contract --------------------------------------

def test_search_is_off_by_default(tmp_path):
    found = reach.search("anything", path=_registry(tmp_path), enabled=False)
    assert found.enabled is False
    assert found.results == []
    assert found.channels_used == []
    assert "disabled" in " ".join(found.channels_skipped.values())


def test_search_skips_uninstalled_channels_without_raising(tmp_path):
    found = reach.search(
        "india cable demand", ["exa"], path=_registry(tmp_path),
        which=_which_none, run=lambda argv: (_ for _ in ()).throw(AssertionError("must not run")),
        enabled=True,
    )
    assert found.results == []
    assert "not on PATH" in found.channels_skipped["exa"]


def test_search_records_nonzero_exit_as_a_skip(tmp_path):
    found = reach.search(
        "q", ["exa"], path=_registry(tmp_path), which=_which_all,
        run=lambda argv: (1, "", "auth expired"), enabled=True,
    )
    assert found.results == []
    assert "auth expired" in found.channels_skipped["exa"]


def test_search_swallows_an_exploding_backend(tmp_path):
    def boom(argv):
        raise OSError("exec format error")

    found = reach.search("q", ["exa"], path=_registry(tmp_path),
                         which=_which_all, run=boom, enabled=True)
    assert found.results == []
    assert "OSError" in found.channels_skipped["exa"]


def test_empty_output_is_a_skip_not_a_result(tmp_path):
    found = reach.search("q", ["exa"], path=_registry(tmp_path), which=_which_all,
                         run=lambda argv: (0, "   ", ""), enabled=True)
    assert found.channels_skipped["exa"] == "no results"


# --- search: happy path + argv rendering -----------------------------------

def test_search_substitutes_query_and_limit_into_argv(tmp_path):
    seen = {}

    def capture(argv):
        seen["argv"] = list(argv)
        return 0, json.dumps([{"title": "t", "url": "https://e.com"}]), ""

    reach.search("copper demand", ["exa"], limit=3, path=_registry(tmp_path),
                 which=_which_all, run=capture, enabled=True)
    assert seen["argv"] == ["reach_exa", "copper demand", "--limit", "3"]


def test_search_normalizes_json_results(tmp_path):
    payload = json.dumps({"results": [
        {"title": "Cable capex cycle", "url": "https://x.com/a", "date": "2026-07-01",
         "author": "@analyst", "snippet": "capex up 30%"},
        {"title": "Second", "link": "https://x.com/b"},
    ]})
    found = reach.search("capex", ["exa"], path=_registry(tmp_path), which=_which_all,
                         run=lambda argv: (0, payload, ""), enabled=True)
    assert found.channels_used == ["exa"]
    assert [r.title for r in found.results] == ["Cable capex cycle", "Second"]
    assert found.results[0].published == "2026-07-01"
    assert found.results[0].author == "@analyst"
    assert found.results[1].url == "https://x.com/b"
    assert all(r.channel == "exa" for r in found.results)


def test_search_respects_limit_per_channel(tmp_path):
    payload = json.dumps([{"title": f"t{i}", "url": f"https://e.com/{i}"} for i in range(10)])
    found = reach.search("q", ["exa"], limit=2, path=_registry(tmp_path), which=_which_all,
                         run=lambda argv: (0, payload, ""), enabled=True)
    assert len(found.results) == 2


def test_search_merges_multiple_channels(tmp_path):
    def run(argv):
        who = argv[0]
        return 0, json.dumps([{"title": who, "url": f"https://{who}.test"}]), ""

    found = reach.search("q", ["exa", "x"], path=_registry(tmp_path),
                         which=_which_all, run=run, enabled=True)
    assert found.channels_used == ["exa", "x"]
    assert {r.channel for r in found.results} == {"exa", "x"}


# --- normalize -------------------------------------------------------------

def test_normalize_handles_a_bare_json_list():
    out = reach.normalize("x", json.dumps([{"text": "hello", "permalink": "https://x/1"}]))
    assert out[0].url == "https://x/1"
    assert out[0].snippet == "hello"


def test_normalize_falls_back_to_url_bearing_lines():
    out = reach.normalize("rss", "Post one https://a.test/1\nnoise\nPost two https://a.test/2")
    assert [r.url for r in out] == ["https://a.test/1", "https://a.test/2"]


def test_normalize_keeps_unparseable_text_as_one_result():
    out = reach.normalize("x", "just prose with no links at all")
    assert len(out) == 1
    assert out[0].snippet == "just prose with no links at all"


def test_normalize_clips_long_snippets():
    out = reach.normalize("x", json.dumps([{"title": "a" * 900}]))
    assert len(out[0].snippet) <= 500
    assert out[0].snippet.endswith("…")


def test_normalize_empty_output_is_empty_list():
    assert reach.normalize("x", "") == []


# --- the registry this repo actually ships ---------------------------------

def test_shipped_registry_declares_the_four_agreed_channels():
    chans = reach.load_channels(config.REACH_CONFIG)
    assert {c.name for c in chans} == {"exa", "x", "reddit", "rss"}
    assert all(c.argv for c in chans), "every shipped channel needs an argv"
    by_name = {c.name: c for c in chans}
    # Burner-account guardrail: these two are the credentialed ones.
    assert by_name["x"].requires_auth is True
    assert by_name["reddit"].requires_auth is True
    assert by_name["exa"].requires_auth is False


def test_reach_layer_is_disabled_unless_env_opts_in(monkeypatch):
    monkeypatch.delenv("STORM_REACH_ENABLED", raising=False)
    assert config.reach_enabled() is False
    monkeypatch.setenv("STORM_REACH_ENABLED", "1")
    assert config.reach_enabled() is True
    monkeypatch.setenv("STORM_REACH_ENABLED", "false")
    assert config.reach_enabled() is False
