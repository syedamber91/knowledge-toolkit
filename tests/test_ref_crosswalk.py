import json
from pathlib import Path
from typing import List, Tuple

import pytest

from soic_wiki.ref_crosswalk import (
    load_crosswalk,
    load_reassessment_crosswalk,
    Resolver,
)


def _write_content(path: Path, lessons: List[Tuple[str, str, str]]) -> None:
    """lessons: list of (lesson_id, title, body_text)."""
    data = {
        "courses": [{
            "title": "T",
            "modules": [{
                "title": "M",
                "lessons": [
                    {"url": f"https://x/{lid}", "title": title, "body_text": body}
                    for lid, title, body in lessons
                ],
            }],
        }],
    }
    path.write_text(json.dumps(data))


def test_load_crosswalk_inverts_lessonid_to_ref(tmp_path: Path):
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"3058584": "ADDITA"}))
    (d / "b.json").write_text(json.dumps({"4207666": "PALLOC", "999": "ZZZ"}))
    xw = load_crosswalk(d)
    assert xw["ADDITA"] == {"3058584"}
    assert xw["PALLOC"] == {"4207666"}
    assert len(xw) == 3


def test_duplicate_ref_returns_both_candidates(tmp_path: Path):
    """A REF code is NOT a unique key — 25 of 221 real codes are ambiguous.
    load_crosswalk must not raise; it must surface every candidate lesson_id
    so Resolver.resolve() can disambiguate by timestamp instead."""
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"111": "DUPE"}))
    (d / "b.json").write_text(json.dumps({"222": "DUPE"}))
    xw = load_crosswalk(d)
    assert xw["DUPE"] == {"111", "222"}


def test_load_reassessment_crosswalk_reads_nested_shape(tmp_path: Path):
    """The reassessment refs.json shape is REF -> {"lesson_id": ..., ...},
    the inverse of the sector crosswalk's lesson_id -> REF."""
    f1 = tmp_path / "level-3-refs.json"
    f1.write_text(json.dumps({
        "FESTF": {"lesson_id": "3543153", "slug": "s", "title": "T"},
    }))
    f2 = tmp_path / "crash-refs.json"
    f2.write_text(json.dumps({
        "VALU2": {"lesson_id": "999", "slug": "s2", "title": "T2"},
    }))
    xw = load_reassessment_crosswalk([f1, f2])
    assert xw["FESTF"] == {"3543153"}
    assert xw["VALU2"] == {"999"}


def test_resolve_disambiguates_by_timestamp(tmp_path: Path):
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"L1": "AMBIG"}))
    (d / "b.json").write_text(json.dumps({"L2": "AMBIG"}))
    content = tmp_path / "content.json"
    _write_content(content, [
        ("L1", "Lesson One", "intro [00:01:00] talk about x"),
        ("L2", "Lesson Two", "intro [00:09:35] the real quote here"),
    ])
    r = Resolver(d, content)
    assert r.ambiguity("AMBIG") == 2
    le = r.resolve("AMBIG", "00:09:35")
    assert le is not None
    assert le.lesson_id == "L2"
    assert le.title == "Lesson Two"


def test_resolve_returns_none_when_timestamp_in_multiple_candidates(tmp_path: Path):
    """Genuinely unresolvable — never pick arbitrarily."""
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"L1": "DUPTS"}))
    (d / "b.json").write_text(json.dumps({"L2": "DUPTS"}))
    content = tmp_path / "content.json"
    _write_content(content, [
        ("L1", "Lesson One", "intro [00:09:35] talk about x"),
        ("L2", "Lesson Two", "intro [00:09:35] the real quote here"),
    ])
    r = Resolver(d, content)
    assert r.resolve("DUPTS", "00:09:35") is None


def test_window_returns_text_containing_the_cited_timestamp(tmp_path: Path):
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"L1": "WNDWA"}))
    content = tmp_path / "content.json"
    _write_content(content, [
        ("L1", "Lesson One",
         "[00:01:00] intro line\n"
         "[00:09:35] more than 15% sales growth here\n"
         "[00:09:40] next line entirely\n"),
    ])
    r = Resolver(d, content)
    win = r.window("WNDWA", "00:09:35")
    assert "[00:09:35]" in win
    assert "more than 15% sales growth" in win


def test_window_returns_empty_string_when_the_pair_does_not_resolve(tmp_path: Path):
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"L1": "WNDWB"}))
    content = tmp_path / "content.json"
    _write_content(content, [
        ("L1", "Lesson One", "[00:01:00] intro line\n"),
    ])
    r = Resolver(d, content)
    assert r.window("WNDWB", "00:09:35") == ""
    assert r.window("NOPE", "00:01:00") == ""


def test_window_with_end_spans_both_timestamps(tmp_path: Path):
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"L1": "WNDWC"}))
    content = tmp_path / "content.json"
    _write_content(content, [
        ("L1", "Lesson One",
         "[00:01:00] intro line\n"
         "[00:09:35] more than 15% sales growth here\n"
         "[00:09:40] and margins expanded too\n"
         "[00:15:00] unrelated later line\n"),
    ])
    r = Resolver(d, content)
    win = r.window("WNDWC", "00:09:35", "00:09:40")
    assert "[00:09:35]" in win
    assert "[00:09:40]" in win
    assert "margins expanded too" in win
    assert "unrelated later line" not in win


REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
RULEBOOK = Path.home() / (
    "Documents/workspace/Claude_Code/soic-ladder/rulebook/"
    "soic-ladder-rules-v1.yaml")
_REPO_ROOT = Path(__file__).resolve().parent.parent
REASSESSMENT_REFS = [
    _REPO_ROOT / "docs/reassessment/level-3/refs.json",
    _REPO_ROOT / "docs/reassessment/l4/refs.json",
    _REPO_ROOT / "docs/reassessment/l5/refs.json",
    _REPO_ROOT / "docs/reassessment/crash/refs.json",
]

needs_real = pytest.mark.skipif(
    not (REFS.exists() and CONTENT.exists()),
    reason="needs the local vault + corpus")


@needs_real
def test_tvgpf_is_not_the_tvgp_lecture():
    """The regression that matters: TVGPF reads like 'TVGP Framework' but is
    the 18.01.26 Valuations lecture. Guessing produced a false finding."""
    r = Resolver(REFS, CONTENT)
    assert r.ambiguity("TVGPF") == 1
    le = r.candidates("TVGPF")[0]
    assert "Valuation" in le.title
    assert "TVGP" not in le.title


@needs_real
def test_every_rulebook_ref_resolves():
    """Every REF citation in the real rulebook must resolve via (REF,
    timestamp) — parse `provenance.ref` as `CODE HH:MM:SS[-HH:MM:SS]` and
    resolve on the first timestamp."""
    import yaml

    rb = yaml.safe_load(RULEBOOK.read_text())
    r = Resolver(REFS, CONTENT)
    unresolved = []
    for k in ("rules", "observations"):
        for e in (rb.get(k) or []):
            ref_str = (e.get("provenance") or {}).get("ref")
            if not ref_str:
                continue
            parts = ref_str.split()
            code = parts[0]
            ts = parts[1].split("-")[0] if len(parts) > 1 else None
            if ts is None or r.resolve(code, ts) is None:
                unresolved.append(ref_str)
    assert unresolved == [], f"unresolved REF citations: {unresolved}"


@needs_real
def test_mastec_resolves_by_timestamp_not_first_candidate():
    """Pins the exact regression that produced a false finding: an earlier
    last-wins loader picked the wrong MASTEC candidate and reported the
    canslim_sales-001 citation as broken. The correct lesson is the one
    whose transcript actually contains 00:09:35."""
    r = Resolver(REFS, CONTENT)
    le = r.resolve("MASTEC", "00:09:35")
    assert le is not None
    assert le.title == "15.12.24 Class 4 How to Filter Epic Stocks"


@needs_real
def test_modulb_ambiguity_is_measured_not_assumed():
    r = Resolver(REFS, CONTENT)
    assert r.ambiguity("MODULB") == 8


@needs_real
def test_resolver_with_extra_refs_resolves_reassessment_code():
    """FESTF only exists in the reassessment vocabulary (docs/reassessment/
    crash/refs.json), never in the sector refs dir. A Resolver built with
    extra_refs must actually resolve it -- this must run for real, not
    skip, since a skipped test would silently re-hide this exact bug."""
    r = Resolver(REFS, CONTENT, extra_refs=REASSESSMENT_REFS)
    le = r.resolve("FESTF", "00:09:35")
    assert le is not None
    assert le.title == "15.12.24 Class 4 How to Filter Epic Stocks"


@needs_real
def test_resolver_with_extra_refs_still_resolves_sector_code():
    """Both vocabularies must live at once: adding the reassessment refs
    must not crowd out the sector crosswalk's own codes."""
    r = Resolver(REFS, CONTENT, extra_refs=REASSESSMENT_REFS)
    le = r.resolve("MASTEC", "00:09:35")
    assert le is not None
    assert le.title == "15.12.24 Class 4 How to Filter Epic Stocks"


@needs_real
def test_two_argument_constructor_still_resolves_sector_code():
    """extra_refs is optional -- existing callers (tests, audit_rulebook.py)
    that only pass (refs_dir, content_json) must keep working unchanged."""
    r = Resolver(REFS, CONTENT)
    le = r.resolve("MASTEC", "00:09:35")
    assert le is not None
    assert le.title == "15.12.24 Class 4 How to Filter Epic Stocks"
