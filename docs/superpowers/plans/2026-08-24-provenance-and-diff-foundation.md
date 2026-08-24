# Provenance & Diff Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic foundation the claims graph and the weekly loop both need — a REF→lesson crosswalk, a rulebook citation validator (D13), and a run-diff (D14 step 4) — with zero LLM calls and zero network.

**Architecture:** Three independent modules in the `soic_wiki` package plus one `soic-ladder` CLI subcommand. Everything is pure functions over files already on disk: the 221-entry REF crosswalk in `Learning Vault Invest`, `data/content.json`, the ladder rulebook, and the two stored ladder runs. No claim extraction, no graph, no subagents — those are Plan B, and they depend on this.

**Tech Stack:** Python 3.9, pytest, PyYAML, existing `soic_method.corpus` loader.

## Why this plan is scoped this way

The spec (`docs/superpowers/specs/2026-08-24-d14-weekly-loop-design.md`) and the
decision set (D1-D14) cover two subsystems: a claims knowledge graph and a weekly
operational loop. They are being split into separate plans. This is **Plan A**,
the shared foundation, and it is the part that:

- needs no LLM, so it cannot hallucinate;
- is testable today against data already on disk;
- **would have caught, mechanically, the citation errors that three separate
  careful passes got wrong by hand** — see Global Constraints.

Plan B (claim extraction with Sonnet subagents, graph assembly, the `scopes`
detector) is written only after Task 2 has told us how many rulebook citations
actually resolve. Building extraction before knowing that would be guessing.

## Global Constraints

- Python 3.9 — no `match`, no `X | Y` unions, **no backslash inside an f-string
  expression** (already bit this repo once).
- Never resolve a REF code by guessing what its letters abbreviate. `TVGPF` looks
  like "TVGP Framework" and actually resolves to `18.01.26 Part 1 Valuations`.
  **Always** resolve through the crosswalk. This mistake was made independently
  by two agents in one session and produced a false "broken citation" finding.
- **A REF code alone is NOT a unique key. 25 of 221 codes map to more than one
  lesson** (`MODULB` maps to eight). Resolve by the pair `(REF, timestamp)`:
  among the candidates for that code, the correct lesson is the one containing
  that timestamp. A last-wins loader over the crosswalk produced two false
  "broken citation" findings before this was noticed.
- Never resolve a lesson by title or slug. Four courses share a lesson titled
  "What you will Learn in this Course? Intro". Resolve by `lesson_id`.
- Read-only against `soic-ladder`. This plan adds one subcommand; it never edits
  the rulebook (D9).
- Crosswalk source of truth: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Learning Vault Invest/wiki/personas/soic/refs/*.json`, each file mapping `lesson_id -> REF`.
- Corpus: `~/Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json` via `soic_method.corpus.load_corpus`.
- Commit after every task.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/soic_wiki/ref_crosswalk.py` | **Create.** Invert `refs/*.json` into `REF -> lesson_id`; resolve a REF to a `LessonRecord`. The single place any code turns a REF code into a lecture. |
| `tests/test_ref_crosswalk.py` | **Create.** Covers the two known traps (guessing a code's meaning, duplicate titles). |
| `src/soic_wiki/citation_audit.py` | **Create.** D13: for each rulebook entry, does its REF resolve, does its timestamp exist in that lesson, and does the cited window support the rule? |
| `tests/test_citation_audit.py` | **Create.** Pinned expectations for the known-good and known-bad rules. |
| `scripts/audit_rulebook.py` | **Create.** CLI wrapper printing a per-rule table; exits non-zero on an unresolvable citation. |
| `src/soic_ladder/rundiff.py` | **Create** (in the soic-ladder repo). Verdict/gate transitions between two `ladder-<as-of>.json` files. |
| `tests/test_rundiff.py` | **Create** (soic-ladder). Transition classification, including the empty-baseline backfill case. |
| `src/soic_ladder/cli.py` | **Modify.** Add a `diff` subparser. |

---

### Task 1: REF crosswalk

**Files:**
- Create: `src/soic_wiki/ref_crosswalk.py`
- Test: `tests/test_ref_crosswalk.py`

**Interfaces:**
- Consumes: `soic_method.corpus.load_corpus`, `soic_method.models.LessonRecord`.
- Produces: `load_crosswalk(refs_dir: Path) -> Dict[str, str]` (REF -> lesson_id);
  `Resolver(refs_dir: Path, content_json: Path)` with
  `.lesson(ref: str) -> Optional[LessonRecord]`,
  `.title(ref: str) -> Optional[str]`,
  `.has_timestamp(ref: str, ts: str) -> bool`,
  `.window(ref: str, start: str, end: Optional[str]) -> str`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ref_crosswalk.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_ref_crosswalk.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_wiki.ref_crosswalk'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_wiki/ref_crosswalk.py
"""Turn a REF code into the lecture it names.

NEVER infer a lecture from a REF code's letters. `TVGPF` reads like "TVGP
Framework" and actually resolves to "18.01.26 Part 1 Valuations"; two agents
independently guessed wrong in one session and reported a citation as broken
when it was sound. This module is the only sanctioned resolution path.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional

from soic_method.corpus import load_corpus
from soic_method.models import LessonRecord

_TS = r"\[(\d{2}:\d{2}:\d{2})\]"


def load_crosswalk(refs_dir: Path) -> Dict[str, str]:
    """REF code -> lesson_id, inverted from the per-module refs/*.json files."""
    out: Dict[str, str] = {}
    for f in sorted(Path(refs_dir).glob("*.json")):
        for lesson_id, ref in json.loads(f.read_text()).items():
            if ref in out and out[ref] != lesson_id:
                raise ValueError(
                    f"REF {ref} maps to two lessons: {out[ref]} and {lesson_id} "
                    f"({f.name}). A REF must identify exactly one lesson."
                )
            out[ref] = lesson_id
    return out


class Resolver:
    def __init__(self, refs_dir: Path, content_json: Path) -> None:
        self._xw = load_crosswalk(refs_dir)
        self._by_id = {le.lesson_id: le for le in load_corpus(content_json)}

    def lesson(self, ref: str) -> Optional[LessonRecord]:
        lid = self._xw.get(ref)
        return self._by_id.get(lid) if lid else None

    def title(self, ref: str) -> Optional[str]:
        le = self.lesson(ref)
        return le.title if le else None

    def has_timestamp(self, ref: str, ts: str) -> bool:
        le = self.lesson(ref)
        return bool(le) and f"[{ts}]" in le.body_text

    def window(self, ref: str, start: str, end: Optional[str] = None) -> str:
        """Raw text from `start` to `end` inclusive; empty string if absent."""
        le = self.lesson(ref)
        if le is None:
            return ""
        m = re.search(re.escape(f"[{start}]"), le.body_text)
        if not m:
            return ""
        if end:
            e = re.search(re.escape(f"[{end}]"), le.body_text[m.start():])
            if e:
                return le.body_text[m.start(): m.start() + e.end() + 200]
        return le.body_text[m.start(): m.start() + 800]

    def nearby_timestamps(self, ref: str, ts: str) -> list:
        """Markers sharing the same MM: prefix — for reporting a near-miss."""
        le = self.lesson(ref)
        if le is None:
            return []
        return [t for t in re.findall(_TS, le.body_text) if t[:5] == ts[:5]]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_ref_crosswalk.py -v`
Expected: PASS, 2 passed

- [ ] **Step 5: Add the real-data regression test**

```python
# append to tests/test_ref_crosswalk.py
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
```

- [ ] **Step 6: Run the full file**

Run: `.venv/bin/python -m pytest tests/test_ref_crosswalk.py -v`
Expected: PASS, 4 passed

- [ ] **Step 7: Commit**

```bash
git add src/soic_wiki/ref_crosswalk.py tests/test_ref_crosswalk.py
git commit -m "feat: REF crosswalk — the only sanctioned way to resolve a REF code

Pins the regression that produced a false finding: TVGPF reads like 'TVGP
Framework' and actually resolves to '18.01.26 Part 1 Valuations'. Two agents
guessed independently and both reported a sound citation as broken."
```

---

### Task 2: Rulebook citation audit (D13)

**Files:**
- Create: `src/soic_wiki/citation_audit.py`
- Create: `scripts/audit_rulebook.py`
- Test: `tests/test_citation_audit.py`

**Interfaces:**
- Consumes: `soic_wiki.ref_crosswalk.Resolver`.
- Produces: `CitationCheck` (dataclass-like: `rule_id`, `ref`, `ts_start`,
  `ts_end`, `resolved`, `lesson_title`, `timestamp_present`, `nearby`,
  `status`); `audit(rulebook_path, resolver) -> List[CitationCheck]`.
  `status` is one of `"OK"`, `"NO_REF"`, `"UNRESOLVED_REF"`, `"BAD_TIMESTAMP"`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_citation_audit.py
from pathlib import Path
import pytest
from soic_wiki.citation_audit import audit, parse_ref


def test_parse_ref_single_and_range():
    assert parse_ref("MASTEC 00:09:35") == ("MASTEC", "00:09:35", None)
    assert parse_ref("HOWB 00:01:55-00:02:23") == ("HOWB", "00:01:55", "00:02:23")
    assert parse_ref(None) == (None, None, None)
    assert parse_ref("") == (None, None, None)


class FakeResolver:
    def lesson(self, ref):
        return object() if ref in ("GOOD", "NOTS") else None
    def title(self, ref):
        return {"GOOD": "A Real Lecture", "NOTS": "Another Lecture"}.get(ref)
    def has_timestamp(self, ref, ts):
        return ref == "GOOD"
    def nearby_timestamps(self, ref, ts):
        return ["00:09:21", "00:09:39"] if ref == "NOTS" else []
    def window(self, ref, s, e=None):
        return "some transcript text" if ref == "GOOD" else ""


def test_audit_classifies_each_failure_mode(tmp_path: Path):
    rb = tmp_path / "rules.yaml"
    rb.write_text(
        "rules:\n"
        "  - id: good-001\n"
        "    provenance: {ref: 'GOOD 00:01:00', quote: q}\n"
        "  - id: badts-001\n"
        "    provenance: {ref: 'NOTS 00:09:35', quote: q}\n"
        "  - id: unres-001\n"
        "    provenance: {ref: 'MISSING 00:01:00', quote: q}\n"
        "observations:\n"
        "  - id: noref-001\n"
        "    provenance: {ref: null, quote: q}\n")
    got = {c.rule_id: c.status for c in audit(rb, FakeResolver())}
    assert got == {"good-001": "OK", "badts-001": "BAD_TIMESTAMP",
                   "unres-001": "UNRESOLVED_REF", "noref-001": "NO_REF"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_citation_audit.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_wiki.citation_audit'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/soic_wiki/citation_audit.py
"""D13 — is each rulebook citation real?

The rulebook's `provenance.quote` fields are the author's PARAPHRASE, not
transcript text, so a verbatim presence check cannot work on them. The check
that does work is structural: does the REF resolve, and does the cited
timestamp exist in that lesson? Nothing here judges whether the rule is a good
rule; it only reports whether the citation points at something real.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from pydantic import BaseModel

_REF = re.compile(
    r"^([A-Z][A-Z0-9]*)\s+(\d{2}:\d{2}:\d{2})(?:-(\d{2}:\d{2}:\d{2}))?$")


def parse_ref(ref: Optional[str]) -> Tuple[Optional[str], Optional[str],
                                           Optional[str]]:
    if not ref:
        return (None, None, None)
    m = _REF.match(ref.strip())
    if not m:
        return (None, None, None)
    return (m.group(1), m.group(2), m.group(3))


class CitationCheck(BaseModel):
    rule_id: str
    kind: str
    ref: Optional[str] = None
    ts_start: Optional[str] = None
    ts_end: Optional[str] = None
    resolved: bool = False
    lesson_title: Optional[str] = None
    timestamp_present: bool = False
    nearby: List[str] = []
    status: str = "NO_REF"


def audit(rulebook_path: Path, resolver) -> List[CitationCheck]:
    doc = yaml.safe_load(Path(rulebook_path).read_text())
    out: List[CitationCheck] = []
    for kind in ("rules", "observations"):
        for e in doc.get(kind) or []:
            raw = (e.get("provenance") or {}).get("ref")
            code, start, end = parse_ref(raw)
            c = CitationCheck(rule_id=e["id"], kind=kind[:-1], ref=raw,
                              ts_start=start, ts_end=end)
            if code is None:
                c.status = "NO_REF"
            elif resolver.lesson(code) is None:
                c.status = "UNRESOLVED_REF"
            else:
                c.resolved = True
                c.lesson_title = resolver.title(code)
                c.timestamp_present = resolver.has_timestamp(code, start)
                if c.timestamp_present:
                    c.status = "OK"
                else:
                    c.status = "BAD_TIMESTAMP"
                    c.nearby = resolver.nearby_timestamps(code, start)
            out.append(c)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_citation_audit.py -v`
Expected: PASS, 2 passed

- [ ] **Step 5: Write the CLI wrapper**

```python
#!/usr/bin/env python3
# scripts/audit_rulebook.py
"""Print a per-rule citation audit. Exit 1 if any citation does not resolve."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soic_wiki.citation_audit import audit          # noqa: E402
from soic_wiki.ref_crosswalk import Resolver        # noqa: E402

REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
RULEBOOK = Path.home() / (
    "Documents/workspace/Claude_Code/soic-ladder/rulebook/soic-ladder-rules-v1.yaml")


def main() -> int:
    checks = audit(RULEBOOK, Resolver(REFS, CONTENT))
    width = max(len(c.rule_id) for c in checks)
    print(f"{'RULE':{width}}  {'STATUS':14}  REF -> LESSON")
    print("-" * (width + 60))
    for c in checks:
        tail = f"{c.ref or '(none)'}"
        if c.lesson_title:
            tail += f"  ->  {c.lesson_title[:44]}"
        if c.status == "BAD_TIMESTAMP" and c.nearby:
            tail += f"   nearby: {', '.join(c.nearby[:4])}"
        print(f"{c.rule_id:{width}}  {c.status:14}  {tail}")
    bad = [c for c in checks if c.status != "OK"]
    print(f"\n{len(checks) - len(bad)}/{len(checks)} citations resolve to a real "
          f"timestamp in a real lesson.")
    for c in bad:
        print(f"  {c.status:14} {c.rule_id}")
    return 1 if any(c.status in ("UNRESOLVED_REF", "BAD_TIMESTAMP") for c in bad) else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Run it against the real rulebook**

Run: `.venv/bin/python scripts/audit_rulebook.py`
Expected: a 16-row table. One row is a known real defect and must appear:
`pe_context-001  NO_REF`. All other citations should resolve, including
`canslim_sales-001`/`canslim_pat-001` (MASTEC) and `growth_trap_flag-001`
(TVGPF) — both were earlier reported as broken by faulty resolution, and both
are sound. Exit code 1 (the `NO_REF` row alone does not set it; only
UNRESOLVED_REF/BAD_TIMESTAMP do — so expect exit 0 unless a real defect
appears).

- [ ] **Step 7: Pin the real-data findings as a regression test**

```python
# append to tests/test_citation_audit.py
from soic_wiki.ref_crosswalk import Resolver

REFS = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/"
    "Learning Vault Invest/wiki/personas/soic/refs")
CONTENT = Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json"
RULEBOOK = Path.home() / (
    "Documents/workspace/Claude_Code/soic-ladder/rulebook/soic-ladder-rules-v1.yaml")

needs_real = pytest.mark.skipif(
    not (REFS.exists() and CONTENT.exists() and RULEBOOK.exists()),
    reason="needs the local vault, corpus and ladder checkout")


@needs_real
def test_known_citation_defects_are_still_reported():
    by_id = {c.rule_id: c for c in audit(RULEBOOK, Resolver(REFS, CONTENT))}
    assert by_id["pe_context-001"].status == "NO_REF"
    # G0's MASTEC 00:09:35 IS sound: MASTEC is one of 25 ambiguous REF codes,
    # and the candidate containing 00:09:35 is "15.12.24 Class 4 How to Filter
    # Epic Stocks", where that timestamp carries the 15%/20% sentence verbatim.
    # An earlier last-wins loader picked the other candidate and reported a
    # false defect. Ambiguity must be resolved by (REF, timestamp), never by
    # REF alone.
    assert by_id["canslim_sales-001"].status == "OK"


@needs_real
def test_growth_trap_citation_is_sound():
    """Regression on OUR error, not the rulebook's: this citation was reported
    broken twice because TVGPF was resolved by guessing at its name."""
    by_id = {c.rule_id: c for c in audit(RULEBOOK, Resolver(REFS, CONTENT))}
    c = by_id["growth_trap_flag-001"]
    assert c.status == "OK"
    assert c.lesson_title and "Valuation" in c.lesson_title
```

- [ ] **Step 8: Run the full file**

Run: `.venv/bin/python -m pytest tests/test_citation_audit.py -v`
Expected: PASS, 4 passed

- [ ] **Step 9: Commit**

```bash
git add src/soic_wiki/citation_audit.py scripts/audit_rulebook.py tests/test_citation_audit.py
git commit -m "feat: D13 rulebook citation audit

Checks structurally, not by quote presence: the rulebook's provenance.quote
fields are the author's paraphrase, so a verbatim check cannot work on them.
Asks instead whether the REF resolves and the cited timestamp exists.

Pins three real findings: pe_context-001 has no ref; G0's MASTEC 00:09:35
does not exist in the lesson MASTEC names (the sentence is real elsewhere, so
this is mis-attribution, not fabrication); and growth_trap_flag-001 is SOUND,
regressing our own false finding from guessing TVGPF's meaning."
```

---

### Task 3: Ladder run diff (D14 step 4) — RE-PLANNED

> **This task was re-planned on 2026-08-24.** The original version filtered
> observations by `rule_id` containing `"exit"`. Ladder observations carry **no
> `rule_id` at all** — they are keyed by `metric` — so that filter always
> returned 0 and `EXIT_FIRED` was dead code that its own test could not catch.
> The original also justified `EXIT_FIRED` with "NATIONALUM is a CANDIDATE with
> 2 fired exit triggers, a contradiction", which was a misreading of the column.
> See `docs/reassessment/ERRATA.md` E2/E3.

**Files (in the `soic-ladder` repo at `~/Documents/workspace/Claude_Code/soic-ladder`):**
- Create: `src/soic_ladder/rundiff.py`
- Test: `tests/test_rundiff.py`
- Modify: `src/soic_ladder/cli.py` (add a `diff` subparser)

**Branch first.** That repo is on `main` with an untracked spec file. Before any
edit: `git checkout -b feat/run-diff`.

**Ground truth, verified in both stored runs** (`runs/out/ladder-2026-08-20.json`
and `runs/out/ladder-2026-08-22.json`, 500 companies each, same rulebook):

- A record is `{"company", "final", "gates", "observations"}`.
- `final` is one of `CANDIDATE` / `WATCH` / `REJECTED` / `INSUFFICIENT`.
- `gates` is a list of `{"gate": "G0"|"G1"|"G3"|"G8", "verdict": "PASS"|"FAIL"|"ABSTAIN", ...}`.
- `observations` is a list of `{"metric", "value", "reference_band", "within_band", "display_text"}` — **no `rule_id`**. Ten metrics, one entry each per company: `cfo_to_ebitda_pct_3y`, `debt_to_equity_delta_3y`, `ema30_break_pct`, `ema_period_used`, `exit_triggers_fired_count`, `nifty500_relative_strength`, `roce`, `sales_growth_3y_pct`, `stock_pe`, `weekly_volatility_stop`.
- `exit_triggers_fired_count` carries `reference_band: "< 3"`. **F23 fires only when the value reaches 3.**
- `within_band` may be `None` (unmeasurable — 30 companies on the 2026-08-22 run). `None` -> a value is data becoming available, **not** a signal change, and must never be reported as a flip.

**Interfaces:**
- Produces: `load_run(path) -> Dict[str, RunRow]` where `RunRow` has
  `final: str`, `gates: Dict[str, str]`, `obs: Dict[str, ObsCell]`;
  `ObsCell` has `value: Optional[float]` and `within_band: Optional[bool]`;
  `diff_runs(prev, curr) -> List[Transition]` with `Transition(company, kind, detail)`;
  `TRANSITION_ORDER: List[str]`; `EXIT_METRIC: str`; `EXIT_FIRES_AT: int`.

- [ ] **Step 1: Branch the ladder repo**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder && git checkout -b feat/run-diff
```
Expected: `Switched to a new branch 'feat/run-diff'`

- [ ] **Step 2: Write the failing test**

```python
# tests/test_rundiff.py
import json
from pathlib import Path
from soic_ladder.rundiff import (
    load_run, diff_runs, TRANSITION_ORDER, EXIT_METRIC, EXIT_FIRES_AT)


def _write(p: Path, rows):
    """rows: (company, final, {gate: verdict}, {metric: (value, within_band)})"""
    p.write_text(json.dumps([
        {"company": c, "final": f,
         "gates": [{"gate": g, "verdict": v} for g, v in gates.items()],
         "observations": [{"metric": m, "value": val, "within_band": wb,
                           "reference_band": "< 3", "display_text": ""}
                          for m, (val, wb) in obs.items()]}
        for c, f, gates, obs in rows]))


def test_exit_fires_only_at_the_threshold(tmp_path: Path):
    """2 of 3 is inside the band. Only reaching 3 is an exit."""
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _write(a, [("AAA", "CANDIDATE", {"G0": "PASS"}, {EXIT_METRIC: (1.0, True)}),
               ("BBB", "CANDIDATE", {"G0": "PASS"}, {EXIT_METRIC: (2.0, True)})])
    _write(b, [("AAA", "CANDIDATE", {"G0": "PASS"}, {EXIT_METRIC: (2.0, True)}),
               ("BBB", "CANDIDATE", {"G0": "PASS"}, {EXIT_METRIC: (3.0, False)})])
    kinds = {t.company: t.kind for t in diff_runs(load_run(a), load_run(b))}
    assert kinds["AAA"] == "EXIT_ARMING"     # 1 -> 2, still inside the band
    assert kinds["BBB"] == "EXIT_FIRED"      # 2 -> 3, all three firing
    assert EXIT_FIRES_AT == 3


def test_unmeasurable_becoming_measured_is_not_a_flip(tmp_path: Path):
    """within_band None -> a value is data arriving, not a signal change."""
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _write(a, [("AAA", "WATCH", {"G0": "PASS"}, {"roce": (None, None)})])
    _write(b, [("AAA", "WATCH", {"G0": "PASS"}, {"roce": (18.0, False)})])
    kinds = [t.kind for t in diff_runs(load_run(a), load_run(b))]
    assert kinds == ["DATA_APPEARED"]


def test_observation_flip_is_reported(tmp_path: Path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _write(a, [("AAA", "WATCH", {"G0": "PASS"}, {"stock_pe": (20.0, True)})])
    _write(b, [("AAA", "WATCH", {"G0": "PASS"}, {"stock_pe": (40.0, False)})])
    ts = diff_runs(load_run(a), load_run(b))
    assert [t.kind for t in ts] == ["OBSERVATION_FLIP"]
    assert "stock_pe" in ts[0].detail


def test_new_and_lost_candidates(tmp_path: Path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _write(a, [("AAA", "WATCH", {"G0": "PASS"}, {}),
               ("BBB", "CANDIDATE", {"G0": "PASS"}, {})])
    _write(b, [("AAA", "CANDIDATE", {"G0": "PASS"}, {}),
               ("BBB", "WATCH", {"G0": "FAIL"}, {})])
    kinds = {t.company: t.kind for t in diff_runs(load_run(a), load_run(b))}
    assert kinds["AAA"] == "NEW_CANDIDATE"
    assert kinds["BBB"] == "LOST_CANDIDATE"


def test_unchanged_is_not_emitted(tmp_path: Path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _write(a, [("AAA", "CANDIDATE", {"G0": "PASS"}, {"roce": (30.0, True)})])
    _write(b, [("AAA", "CANDIDATE", {"G0": "PASS"}, {"roce": (30.0, True)})])
    assert diff_runs(load_run(a), load_run(b)) == []


def test_gate_flip_reported_when_verdict_unchanged(tmp_path: Path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _write(a, [("AAA", "WATCH", {"G8": "PASS"}, {})])
    _write(b, [("AAA", "WATCH", {"G8": "FAIL"}, {})])
    ts = diff_runs(load_run(a), load_run(b))
    assert [t.kind for t in ts] == ["GATE_FLIP"]
    assert "G8" in ts[0].detail


def test_empty_baseline_is_backfill_not_news(tmp_path: Path):
    b = tmp_path / "b.json"
    _write(b, [("AAA", "CANDIDATE", {"G0": "PASS"}, {})])
    assert [t.kind for t in diff_runs({}, load_run(b))] == ["BACKFILL"]


def test_exit_fired_outranks_new_candidate():
    assert TRANSITION_ORDER.index("EXIT_FIRED") < \
           TRANSITION_ORDER.index("NEW_CANDIDATE")


def test_one_transition_per_company(tmp_path: Path):
    """A company that flips a gate AND an observation is reported once, at its
    most important class -- the brief must not list a name twice."""
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _write(a, [("AAA", "WATCH", {"G8": "PASS"}, {"stock_pe": (20.0, True)})])
    _write(b, [("AAA", "CANDIDATE", {"G8": "FAIL"}, {"stock_pe": (40.0, False)})])
    ts = diff_runs(load_run(a), load_run(b))
    assert len(ts) == 1
    assert ts[0].kind == "NEW_CANDIDATE"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_rundiff.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_ladder.rundiff'`

- [ ] **Step 4: Write the implementation**

```python
# src/soic_ladder/rundiff.py
"""What changed between two ladder runs.

A weekly list should answer "what changed", not "what passes". The passing set
barely moves: across 2026-08-20 -> 2026-08-22, 497 of 500 companies were
identical. Suppressing UNCHANGED is what turns a 49-name wall into a readable
brief.

Observations here are keyed by `metric` -- they carry no rule_id. An earlier
draft of this module filtered them by rule_id and silently matched nothing.

EXIT_FIRED means `exit_triggers_fired_count` reached EXIT_FIRES_AT. F23's exit
is systematic and fires only when all three triggers fire together, so 1 or 2 is
EXIT_ARMING, not an exit. Reporting a sub-threshold count as a fired exit was a
real misreading before this module existed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

EXIT_METRIC = "exit_triggers_fired_count"
EXIT_FIRES_AT = 3

TRANSITION_ORDER: List[str] = [
    "BACKFILL",
    "EXIT_FIRED",
    "LOST_CANDIDATE",
    "NEW_CANDIDATE",
    "GATE_FLIP",
    "EXIT_ARMING",
    "OBSERVATION_FLIP",
    "DATA_APPEARED",
    "DATA_LOST",
]


class ObsCell(BaseModel):
    value: Optional[float] = None
    within_band: Optional[bool] = None


class RunRow(BaseModel):
    final: str
    gates: Dict[str, str] = {}
    obs: Dict[str, ObsCell] = {}


class Transition(BaseModel):
    company: str
    kind: str
    detail: str = ""


def load_run(path: Path) -> Dict[str, RunRow]:
    out: Dict[str, RunRow] = {}
    for r in json.loads(Path(path).read_text()):
        out[r["company"]] = RunRow(
            final=r["final"],
            gates={g["gate"]: g["verdict"] for g in (r.get("gates") or [])},
            obs={o["metric"]: ObsCell(value=o.get("value"),
                                      within_band=o.get("within_band"))
                 for o in (r.get("observations") or []) if o.get("metric")})
    return out


def _exit_value(row: RunRow) -> Optional[float]:
    cell = row.obs.get(EXIT_METRIC)
    return cell.value if cell else None


def _classify(company: str, was: RunRow, now: RunRow) -> Optional[Transition]:
    """At most ONE transition per company, at its most important class."""
    prev_exit, curr_exit = _exit_value(was), _exit_value(now)
    if (curr_exit is not None and prev_exit is not None
            and curr_exit >= EXIT_FIRES_AT > prev_exit):
        return Transition(
            company=company, kind="EXIT_FIRED",
            detail=f"{EXIT_METRIC} {prev_exit:.0f} -> {curr_exit:.0f} "
                   f"(F23 fires at {EXIT_FIRES_AT}); verdict {now.final}")

    if was.final == "CANDIDATE" and now.final != "CANDIDATE":
        return Transition(company=company, kind="LOST_CANDIDATE",
                          detail=f"CANDIDATE -> {now.final}")
    if was.final != "CANDIDATE" and now.final == "CANDIDATE":
        return Transition(company=company, kind="NEW_CANDIDATE",
                          detail=f"{was.final} -> CANDIDATE")

    flips = [f"{g}: {was.gates[g]} -> {v}" for g, v in sorted(now.gates.items())
             if g in was.gates and was.gates[g] != v]
    if flips:
        return Transition(company=company, kind="GATE_FLIP",
                          detail="; ".join(flips))

    if (curr_exit is not None and prev_exit is not None
            and curr_exit > prev_exit):
        return Transition(
            company=company, kind="EXIT_ARMING",
            detail=f"{EXIT_METRIC} {prev_exit:.0f} -> {curr_exit:.0f}, "
                   f"still below {EXIT_FIRES_AT}")

    # within_band changes, ignoring None transitions (data arriving/leaving is
    # not a signal change and must never be reported as a flip)
    obs_flips, appeared, lost = [], [], []
    for metric, cell in sorted(now.obs.items()):
        old = was.obs.get(metric)
        if old is None:
            continue
        if old.within_band is None and cell.within_band is not None:
            appeared.append(metric)
        elif old.within_band is not None and cell.within_band is None:
            lost.append(metric)
        elif old.within_band != cell.within_band:
            obs_flips.append(
                f"{metric}: {'in' if old.within_band else 'out'} -> "
                f"{'in' if cell.within_band else 'out'} of band")
    if obs_flips:
        return Transition(company=company, kind="OBSERVATION_FLIP",
                          detail="; ".join(obs_flips))
    if appeared:
        return Transition(company=company, kind="DATA_APPEARED",
                          detail="now measurable: " + ", ".join(appeared))
    if lost:
        return Transition(company=company, kind="DATA_LOST",
                          detail="no longer measurable: " + ", ".join(lost))
    return None


def diff_runs(prev: Dict[str, RunRow],
              curr: Dict[str, RunRow]) -> List[Transition]:
    if not prev:
        return [Transition(company=c, kind="BACKFILL",
                           detail=f"verdict {r.final} (no baseline)")
                for c, r in sorted(curr.items())]
    out: List[Transition] = []
    for company in sorted(curr):
        was = prev.get(company)
        if was is None:
            if curr[company].final == "CANDIDATE":
                out.append(Transition(company=company, kind="NEW_CANDIDATE",
                                      detail="not in previous universe"))
            continue
        t = _classify(company, was, curr[company])
        if t is not None:
            out.append(t)
    out.sort(key=lambda t: (TRANSITION_ORDER.index(t.kind), t.company))
    return out
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_rundiff.py -v`
Expected: PASS, 9 passed

- [ ] **Step 6: Add the `diff` subcommand**

In `src/soic_ladder/cli.py`, after the `judge` subparser block (which ends at
`judge.add_argument("--out", default="out")`), add:

```python
    dif = sub.add_parser("diff", help="what changed between two stored runs")
    dif.add_argument("--prev", required=True, help="earlier ladder-<as-of>.json")
    dif.add_argument("--curr", required=True, help="later ladder-<as-of>.json")
```

and in the command dispatch add:

```python
    if args.command == "diff":
        from .rundiff import load_run, diff_runs
        prev, curr = load_run(Path(args.prev)), load_run(Path(args.curr))
        transitions = diff_runs(prev, curr)
        print(f"{len(prev)} -> {len(curr)} companies; "
              f"{len(curr) - len(transitions)} unchanged (suppressed)\n")
        for t in transitions:
            print(f"{t.kind:18} {t.company:14} {t.detail}")
        return 0
```

- [ ] **Step 7: Run against the two stored runs**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m soic_ladder.cli diff \
  --prev runs/out/ladder-2026-08-20.json \
  --curr runs/out/ladder-2026-08-22.json
```
Expected: `500 -> 500 companies` with the large majority suppressed; one
`NEW_CANDIDATE COFORGE`; roughly 20 `GATE_FLIP` lines, all on `G8`. Record the
exact counts in your report — they are the baseline for the weekly loop, and any
`EXIT_FIRED` rows are a genuine finding worth reporting.

- [ ] **Step 8: Run the ladder's own suite to confirm nothing regressed**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest -q`
Expected: the pre-existing suite still passes; report the totals.

- [ ] **Step 9: Commit**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder
git add src/soic_ladder/rundiff.py tests/test_rundiff.py src/soic_ladder/cli.py
git commit -m "feat: ladder run diff — what changed, not what passes

Observations are keyed by metric and carry no rule_id; an earlier draft
filtered them by rule_id and matched nothing. EXIT_FIRED requires
exit_triggers_fired_count to reach 3, because F23 fires only when all three
triggers fire together — 1 or 2 is EXIT_ARMING. within_band None transitions
are data arriving or leaving, never reported as a flip."
```

---

## Self-Review

**Spec coverage.** This plan implements D13 (Task 2) and D14 step 4 (Task 3), plus
the crosswalk that D8' depends on (Task 1). It deliberately does **not** cover
D14 steps 5-8 (rank, cap, procedure attachment, brief) or any of the claim-graph
decisions (D2-D8', D10-D12) — those are Plan B, gated on Task 2's output telling
us how many citations actually resolve.

**Placeholders.** None: every code step carries complete code, every run step
carries an exact command and its expected output, including the two real-data
expectations (`pe_context-001 NO_REF`, `canslim_sales-001 BAD_TIMESTAMP`) and the
497/500 diff result.

**Type consistency.** `Resolver` exposes `lesson`/`title`/`has_timestamp`/
`window`/`nearby_timestamps`; `citation_audit.audit` calls exactly those five and
the test's `FakeResolver` implements exactly those five. `load_run` returns
`Dict[str, RunRow]`, which is what `diff_runs` accepts in both the tests and the
CLI branch. `TRANSITION_ORDER` is referenced by name in the test and defined in
the module.

**Known gap, recorded not hidden.** One framework REF code (`SOICE6`) is absent
from the crosswalk, so 49/50 framework refs resolve. It affects no rulebook
entry, so it does not block Task 2; Plan B must handle it rather than assume
100% coverage.
