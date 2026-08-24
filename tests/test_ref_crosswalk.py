import json
from pathlib import Path
import pytest
from soic_wiki.ref_crosswalk import load_crosswalk


def test_load_crosswalk_inverts_lessonid_to_ref(tmp_path: Path):
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"3058584": "ADDITA"}))
    (d / "b.json").write_text(json.dumps({"4207666": "PALLOC", "999": "ZZZ"}))
    xw = load_crosswalk(d)
    assert xw["ADDITA"] == "3058584"
    assert xw["PALLOC"] == "4207666"
    assert len(xw) == 3


def test_duplicate_ref_across_files_raises(tmp_path: Path):
    """A REF code must identify exactly one lesson. Silent last-wins is how a
    title-keyed lookup once verified an L3 brief against the L4 course."""
    d = tmp_path / "refs"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"111": "DUPE"}))
    (d / "b.json").write_text(json.dumps({"222": "DUPE"}))
    with pytest.raises(ValueError, match="DUPE"):
        load_crosswalk(d)


from soic_wiki.ref_crosswalk import Resolver

REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"

needs_real = pytest.mark.skipif(
    not (REFS.exists() and CONTENT.exists()),
    reason="needs the local vault + corpus")


@needs_real
def test_tvgpf_is_not_the_tvgp_lecture():
    """The regression that matters: TVGPF reads like 'TVGP Framework' but is
    the 18.01.26 Valuations lecture. Guessing produced a false finding."""
    r = Resolver(REFS, CONTENT)
    title = r.title("TVGPF")
    assert title is not None
    assert "Valuation" in title
    assert "TVGP" not in title


@needs_real
def test_every_rulebook_ref_resolves():
    import yaml
    rb = yaml.safe_load((Path.home() / (
        "Documents/workspace/Claude_Code/soic-ladder/rulebook/"
        "soic-ladder-rules-v1.yaml")).read_text())
    r = Resolver(REFS, CONTENT)
    refs = {(e.get("provenance") or {}).get("ref", "").split()[0]
            for k in ("rules", "observations") for e in (rb.get(k) or [])
            if (e.get("provenance") or {}).get("ref")}
    unresolved = sorted(x for x in refs if r.lesson(x) is None)
    assert unresolved == [], f"unresolved REF codes: {unresolved}"
