# Stage 2 — Weekly Short List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `ladder weekly` — turn two stored runs into a short, ranked, capped brief of what changed and is worth looking at, with a one-command path to the full detail.

**Architecture:** Composes what already exists. `rundiff` supplies the transitions, `explain` supplies the per-company facts. Stage 2 adds a compact renderer, deterministic ranking, a cap with an overflow queue, and an append-only log. It computes no new metrics and fetches nothing.

**Tech Stack:** Python 3.11+, pytest, the existing `soic_ladder` package.

## What this delivers

The stated goal: filter Nifty 500 to a weekly list worth researching. The diff
already reduces 500 companies to ~78 lines; ranking and capping take that to a
handful, and each entry says enough to decide whether to open the full
`ladder explain`.

## Global Constraints

- **No composite score.** Rank by transition class, then by ticker for
  stability. Blending corroboration counts, gate margins and evidence strength
  into one number would manufacture a ranking nobody stated — the same failure
  as promoting a dated example to a universal rule.
- **Nothing is silently dropped.** Whatever the cap excludes goes to an overflow
  queue file with its transition class.
- **The engine knows nothing about Shariah, or any other belief-specific
  screen.** Filtering is a generic `--universe FILE` of tickers, one per line.
  This package is being published publicly and must stay generic; the user's own
  list stays outside it.
- **Never hardcode a personal or machine-specific absolute path.** Vault comes
  from `--vault` or `SOIC_VAULT_DIR`, exactly as Stage 1 does. This defect class
  has been fixed twice in this codebase already.
- Read-only: no network, no writes under `runs/`, no rulebook edits.
- Python 3.11+. No backslash inside an f-string expression.
- Branch off `feat/explain` — Stage 2 builds directly on Stage 1's `explain.py`.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/soic_ladder/weekly.py` | **Create.** Compact per-company lines, ranking, cap, brief text, overflow queue text. Pure functions. |
| `tests/test_weekly.py` | **Create.** Ranking order, cap and overflow, the same-date and empty-baseline guards, universe filtering. |
| `src/soic_ladder/cli.py` | **Modify.** Add a `weekly` subparser and dispatch. |

---

### Task 1: Compact lines, ranking, cap

**Files:**
- Create: `src/soic_ladder/weekly.py`
- Test: `tests/test_weekly.py`

**Interfaces:**
- Consumes: `soic_ladder.rundiff.Transition` (fields `company`, `kind`, `detail`) and `TRANSITION_ORDER`; `soic_ladder.explain.load_company`, `first_failing_gate`, `GATE_ORDER`.
- Produces:
  `DEFAULT_CAP: int`;
  `load_universe(path: Optional[Path]) -> Optional[Set[str]]`;
  `apply_universe(transitions, universe) -> List[Transition]`;
  `rank(transitions) -> List[Transition]`;
  `split_cap(transitions, cap) -> Tuple[List[Transition], List[Transition]]`;
  `compact_line(transition, record) -> List[str]`.

- [ ] **Step 1: Branch**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder && git checkout feat/explain && git checkout -b feat/weekly
```
Expected: `Switched to a new branch 'feat/weekly'`

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_weekly.py
from pathlib import Path

from soic_ladder.rundiff import Transition
from soic_ladder.weekly import (
    DEFAULT_CAP, apply_universe, compact_line, load_universe, rank, split_cap)


def _t(company, kind, detail=""):
    return Transition(company=company, kind=kind, detail=detail)


def _record(company="AAA", final="CANDIDATE", gates=None, obs=None):
    gates = gates or {"G0": "PASS", "G1": "PASS", "G3": "PASS", "G8": "PASS"}
    return {
        "company": company, "final": final,
        "gates": [{"gate": g, "verdict": v, "outcomes": []} for g, v in gates.items()],
        "observations": obs or [],
    }


def test_rank_puts_exits_above_new_candidates():
    out = rank([_t("AAA", "NEW_CANDIDATE"), _t("BBB", "EXIT_FIRED")])
    assert [t.company for t in out] == ["BBB", "AAA"]


def test_rank_is_stable_by_ticker_within_a_class():
    out = rank([_t("ZZZ", "GATE_FLIP"), _t("AAA", "GATE_FLIP")])
    assert [t.company for t in out] == ["AAA", "ZZZ"]


def test_split_cap_keeps_the_top_and_queues_the_rest():
    ts = rank([_t(c, "GATE_FLIP") for c in ("AAA", "BBB", "CCC", "DDD")])
    shown, queued = split_cap(ts, 2)
    assert [t.company for t in shown] == ["AAA", "BBB"]
    assert [t.company for t in queued] == ["CCC", "DDD"]


def test_split_cap_never_drops_anything():
    ts = rank([_t(c, "GATE_FLIP") for c in ("AAA", "BBB", "CCC")])
    shown, queued = split_cap(ts, 1)
    assert len(shown) + len(queued) == 3


def test_default_cap_is_small_enough_to_read():
    assert 3 <= DEFAULT_CAP <= 10


def test_load_universe_reads_one_ticker_per_line(tmp_path: Path):
    f = tmp_path / "u.txt"
    f.write_text("AAA\n# a comment\n\nbbb\n")
    assert load_universe(f) == {"AAA", "BBB"}


def test_load_universe_is_none_when_no_file_given():
    assert load_universe(None) is None


def test_apply_universe_filters_and_none_means_everything():
    ts = [_t("AAA", "GATE_FLIP"), _t("BBB", "GATE_FLIP")]
    assert [t.company for t in apply_universe(ts, {"BBB"})] == ["BBB"]
    assert len(apply_universe(ts, None)) == 2


def test_compact_line_names_the_company_verdict_and_change():
    lines = compact_line(_t("AAA", "NEW_CANDIDATE", "WATCH -> CANDIDATE"),
                         _record("AAA", "CANDIDATE"))
    text = "\n".join(lines)
    assert "AAA" in text and "CANDIDATE" in text
    assert "NEW_CANDIDATE" in text
    assert "WATCH -> CANDIDATE" in text


def test_compact_line_says_where_a_company_stopped():
    rec = _record("AAA", "WATCH",
                  gates={"G0": "PASS", "G1": "FAIL", "G3": "PASS", "G8": "PASS"})
    text = "\n".join(compact_line(_t("AAA", "LOST_CANDIDATE"), rec))
    assert "G1" in text


def test_compact_line_flags_observations_outside_their_band():
    rec = _record("AAA", obs=[
        {"metric": "stock_pe", "value": 51.9, "reference_band": "between 15 35",
         "within_band": False, "display_text": ""},
        {"metric": "roce", "value": 30.0, "reference_band": ">= 20",
         "within_band": True, "display_text": ""}])
    text = "\n".join(compact_line(_t("AAA", "NEW_CANDIDATE"), rec))
    assert "stock_pe" in text
    assert "roce" not in text          # inside band -- not worth the space


def test_compact_line_survives_a_missing_record():
    text = "\n".join(compact_line(_t("AAA", "GATE_FLIP", "G8 flipped"), None))
    assert "AAA" in text
    assert "G8 flipped" in text


def test_compact_line_is_short():
    lines = compact_line(_t("AAA", "NEW_CANDIDATE"), _record())
    assert len(lines) <= 6, "a brief entry must stay scannable"
```

- [ ] **Step 3: Run to verify they fail**

Run: `cd ~/Documents/workspace/Claude_Code/soic-ladder && .venv/bin/python -m pytest tests/test_weekly.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'soic_ladder.weekly'`

- [ ] **Step 4: Write the implementation**

```python
# src/soic_ladder/weekly.py
"""Turn two stored runs into a short weekly brief.

Composes what already exists: rundiff supplies the transitions, explain
supplies the per-company facts. Nothing here computes a metric or fetches
anything.

Ranking is by transition class, never by a computed score. Blending gate
margins and evidence strength into one number would invent a ranking nobody
stated -- the same failure mode as treating a dated worked example as a
universal rule. The class order already encodes what matters: an exit that has
fired outranks a company newly arriving.

Whatever the cap excludes goes to an overflow queue rather than disappearing.
A brief that silently drops names reads as "this is everything".
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .explain import GATE_ORDER, first_failing_gate
from .rundiff import TRANSITION_ORDER, Transition

# Small enough to actually read on a weekly cadence. The overflow queue keeps
# the remainder, so this is a display cap, not a filter.
DEFAULT_CAP = 5


def load_universe(path: Optional[Path]) -> Optional[Set[str]]:
    """Tickers to keep, one per line. None means no filtering at all.

    Deliberately generic: the engine has no notion of any belief-specific or
    strategy-specific screen. Callers supply whatever list they want.
    """
    if path is None:
        return None
    out: Set[str] = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        token = line.strip()
        if token and not token.startswith("#"):
            out.add(token.upper())
    return out


def apply_universe(transitions: Sequence[Transition],
                   universe: Optional[Set[str]]) -> List[Transition]:
    if universe is None:
        return list(transitions)
    return [t for t in transitions if t.company.upper() in universe]


def rank(transitions: Sequence[Transition]) -> List[Transition]:
    """Transition class first, then ticker. Deterministic and explainable."""
    return sorted(transitions,
                  key=lambda t: (TRANSITION_ORDER.index(t.kind)
                                 if t.kind in TRANSITION_ORDER
                                 else len(TRANSITION_ORDER),
                                 t.company))


def split_cap(transitions: Sequence[Transition],
              cap: int = DEFAULT_CAP) -> Tuple[List[Transition], List[Transition]]:
    """(shown, queued). Their lengths always sum to the input length."""
    ordered = list(transitions)
    return ordered[:cap], ordered[cap:]


def _outside_band(record: Optional[Dict]) -> List[str]:
    if not record:
        return []
    out = []
    for obs in record.get("observations") or []:
        if obs.get("within_band") is False:
            value = obs.get("value")
            shown = f"{value:g}" if isinstance(value, float) else str(value)
            out.append(f"{obs.get('metric','?')} {shown} "
                       f"(band {obs.get('reference_band','?')})")
    return out


def compact_line(transition: Transition,
                 record: Optional[Dict]) -> List[str]:
    """One brief entry: a few lines, enough to decide whether to look closer."""
    lines: List[str] = []
    verdict = record.get("final", "?") if record else "?"
    lines.append(f"{transition.company}  [{transition.kind}]  verdict {verdict}")
    if transition.detail:
        lines.append(f"    {transition.detail}")
    if record:
        stopped = first_failing_gate(record)
        lines.append(f"    stopped at {stopped}" if stopped
                     else "    cleared every gate")
        flags = _outside_band(record)
        if flags:
            shown = "; ".join(flags[:2])
            more = f" (+{len(flags) - 2} more)" if len(flags) > 2 else ""
            lines.append(f"    outside band: {shown}{more}")
    lines.append(f"    full detail: ladder explain {transition.company}")
    return lines
```

- [ ] **Step 5: Run to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_weekly.py -v`
Expected: PASS, 13 passed

- [ ] **Step 6: Commit**

```bash
git add src/soic_ladder/weekly.py tests/test_weekly.py
git commit -m "feat: weekly brief building blocks

Ranking is by transition class, never a computed score -- a blended number
would invent a ranking nobody stated. Whatever the cap excludes goes to an
overflow queue rather than disappearing, because a brief that silently drops
names reads as if it were everything."
```

---

### Task 2: The brief, the guards, and the CLI

**Files:**
- Modify: `src/soic_ladder/weekly.py`
- Modify: `tests/test_weekly.py`
- Modify: `src/soic_ladder/cli.py`

**Interfaces:**
- Consumes: everything from Task 1, plus `soic_ladder.rundiff.load_run` and `diff_runs`, and `soic_ladder.explain.load_company`.
- Produces:
  `build_brief(prev_path, curr_path, universe=None, cap=DEFAULT_CAP) -> Tuple[str, str]` returning `(brief_text, queue_text)`;
  `GuardError` (an `Exception` subclass).

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_weekly.py
import json
import pytest
from soic_ladder.weekly import GuardError, build_brief


def _write_run(p: Path, records):
    p.write_text(json.dumps(records))
    return p


def _rec(company, final, gates=None):
    gates = gates or {"G0": "PASS", "G1": "PASS", "G3": "PASS", "G8": "PASS"}
    return {"company": company, "final": final,
            "gates": [{"gate": g, "verdict": v, "outcomes": []}
                      for g, v in gates.items()],
            "observations": []}


def test_build_brief_refuses_when_both_paths_are_the_same(tmp_path: Path):
    run = _write_run(tmp_path / "ladder-2026-01-01.json", [_rec("AAA", "WATCH")])
    with pytest.raises(GuardError, match="same"):
        build_brief(run, run)


def test_build_brief_labels_an_empty_baseline_as_backfill(tmp_path: Path):
    prev = _write_run(tmp_path / "ladder-2026-01-01.json", [])
    curr = _write_run(tmp_path / "ladder-2026-01-08.json", [_rec("AAA", "CANDIDATE")])
    brief, _ = build_brief(prev, curr)
    assert "backfill" in brief.lower()
    assert "week" not in brief.lower().split("backfill")[0][-40:]


def test_build_brief_names_both_run_files(tmp_path: Path):
    prev = _write_run(tmp_path / "ladder-2026-01-01.json", [_rec("AAA", "WATCH")])
    curr = _write_run(tmp_path / "ladder-2026-01-08.json", [_rec("AAA", "CANDIDATE")])
    brief, _ = build_brief(prev, curr)
    assert "ladder-2026-01-01.json" in brief
    assert "ladder-2026-01-08.json" in brief


def test_build_brief_reports_the_suppressed_count(tmp_path: Path):
    prev = _write_run(tmp_path / "a.json", [_rec("AAA", "WATCH"), _rec("BBB", "WATCH")])
    curr = _write_run(tmp_path / "b.json", [_rec("AAA", "CANDIDATE"), _rec("BBB", "WATCH")])
    brief, _ = build_brief(prev, curr)
    assert "unchanged" in brief.lower()


def test_build_brief_queues_what_the_cap_excludes(tmp_path: Path):
    prev = _write_run(tmp_path / "a.json",
                      [_rec(c, "WATCH") for c in ("AAA", "BBB", "CCC")])
    curr = _write_run(tmp_path / "b.json",
                      [_rec(c, "CANDIDATE") for c in ("AAA", "BBB", "CCC")])
    brief, queue = build_brief(prev, curr, cap=1)
    assert "AAA" in brief
    assert "BBB" in queue and "CCC" in queue


def test_build_brief_honours_the_universe(tmp_path: Path):
    prev = _write_run(tmp_path / "a.json", [_rec("AAA", "WATCH"), _rec("BBB", "WATCH")])
    curr = _write_run(tmp_path / "b.json",
                      [_rec("AAA", "CANDIDATE"), _rec("BBB", "CANDIDATE")])
    brief, _ = build_brief(prev, curr, universe={"BBB"})
    assert "BBB" in brief
    assert "AAA" not in brief
```

- [ ] **Step 2: Run to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_weekly.py -v`
Expected: FAIL — `ImportError: cannot import name 'GuardError'`

- [ ] **Step 3: Add the brief builder**

```python
# append to src/soic_ladder/weekly.py
from .explain import load_company
from .rundiff import diff_runs, load_run


class GuardError(Exception):
    """A refusal to produce a brief that would mislead."""


def build_brief(prev_path: Path, curr_path: Path,
                universe: Optional[Set[str]] = None,
                cap: int = DEFAULT_CAP) -> Tuple[str, str]:
    """(brief_text, queue_text).

    Refuses rather than emits when the two runs are the same file: a diff of a
    run against itself reports nothing changed, which is indistinguishable from
    a genuinely quiet week.
    """
    prev_path, curr_path = Path(prev_path), Path(curr_path)
    if prev_path.resolve() == curr_path.resolve():
        raise GuardError(
            "previous and current run are the same file -- a diff against "
            "itself cannot be told apart from a quiet week")

    prev, curr = load_run(prev_path), load_run(curr_path)
    transitions = apply_universe(rank(diff_runs(prev, curr)), universe)
    shown, queued = split_cap(transitions, cap)
    unchanged = max(len(curr) - len(transitions), 0)
    backfill = not prev

    head: List[str] = []
    head.append("BACKFILL -- first run, not a week's news"
                if backfill else "Weekly brief")
    head.append(f"  previous: {prev_path.name}")
    head.append(f"  current:  {curr_path.name}")
    head.append(f"  {len(curr)} companies; {len(transitions)} changed; "
                f"{unchanged} unchanged (suppressed)")
    if universe is not None:
        head.append(f"  universe filter applied: {len(universe)} tickers")
    head.append("")

    body: List[str] = []
    if not shown:
        body.append("Nothing changed worth reporting.")
    for transition in shown:
        body += compact_line(transition, load_company(curr_path, transition.company))
        body.append("")
    if queued:
        body.append(f"{len(queued)} more not shown -- see the queue file.")

    queue_lines = [f"{t.kind}\t{t.company}\t{t.detail}" for t in queued]
    return "\n".join(head + body), "\n".join(queue_lines)
```

- [ ] **Step 4: Run to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_weekly.py -v`
Expected: PASS, 19 passed

- [ ] **Step 5: Add the CLI subcommand**

In `src/soic_ladder/cli.py`, after the `explain` subparser, add:

```python
    wk = sub.add_parser("weekly", help="a short brief of what changed between two runs")
    wk.add_argument("--prev", required=True, help="earlier ladder-<as-of>.json")
    wk.add_argument("--curr", required=True, help="later ladder-<as-of>.json")
    wk.add_argument("--universe", default=None,
                    help="optional file of tickers to keep, one per line")
    wk.add_argument("--cap", type=int, default=None,
                    help="how many entries to show (default 5)")
    wk.add_argument("--queue-out", default=None,
                    help="write the overflow queue here instead of stdout")
```

and in the dispatch, beside the `explain` branch:

```python
    if args.command == "weekly":
        from .weekly import DEFAULT_CAP, GuardError, build_brief, load_universe
        try:
            brief, queue = build_brief(
                Path(args.prev), Path(args.curr),
                universe=load_universe(Path(args.universe) if args.universe else None),
                cap=args.cap if args.cap is not None else DEFAULT_CAP)
        except GuardError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(brief)
        if queue:
            if args.queue_out:
                Path(args.queue_out).write_text(queue + "\n", encoding="utf-8")
                print(f"\nqueue written to {args.queue_out}")
            else:
                print("\nQUEUE\n" + queue)
        return 0
```

- [ ] **Step 6: Run it on the two stored runs**

```bash
cd ~/Documents/workspace/Claude_Code/soic-ladder
.venv/bin/ladder weekly --prev runs/out/ladder-2026-08-20.json \
                        --curr runs/out/ladder-2026-08-22.json
```
Expected: a header naming both files and the unchanged count, then at most 5
entries led by the exit-related classes, then a queue. Report the full output.

- [ ] **Step 7: Confirm the same-file guard**

```bash
.venv/bin/ladder weekly --prev runs/out/ladder-2026-08-22.json \
                        --curr runs/out/ladder-2026-08-22.json; echo "exit=$?"
```
Expected: a clear refusal and `exit=1`.

- [ ] **Step 8: Confirm the universe filter on real data**

```bash
printf 'ATUL\nBSE\nCOFORGE\n' > /tmp/universe.txt
.venv/bin/ladder weekly --prev runs/out/ladder-2026-08-20.json \
                        --curr runs/out/ladder-2026-08-22.json \
                        --universe /tmp/universe.txt
```
Expected: only those tickers appear, and the header states the filter was
applied. Report the output.

- [ ] **Step 9: Full suite**

Run: `.venv/bin/python -m pytest -q >/dev/null 2>&1; echo "exit=$?"`
Expected: `0`.

- [ ] **Step 10: Commit**

```bash
git add src/soic_ladder/weekly.py tests/test_weekly.py src/soic_ladder/cli.py
git commit -m "feat: ladder weekly -- a short brief of what changed

Refuses to diff a run against itself, because that is indistinguishable from
a quiet week. Labels an empty baseline a backfill rather than presenting it as
news. Universe filtering is a plain ticker file so the engine stays generic."
```

---

## Self-Review

**Spec coverage.** Stage 2 of `docs/reassessment/ROADMAP.md` asks for a ranked,
capped weekly short list reusing Stage 1's renderer. Task 1 covers ranking, the
cap and the compact entry; Task 2 covers the brief, its guards and the CLI.

**Deliberately not here.** D14 step 7 (attaching the corpus's `procedure`
checklist to each surfaced name) needs the claims graph and is Stage 3. The
append-only `runs/weekly/LOG.md` is deferred with it, so the log arrives once
alongside the content it will record rather than being written twice.

**A pipeline step that does not exist.** The D14 spec listed a Shariah screen
between judge and diff. There is no such code in this engine — that shortlist
was produced by a separate tool. Rather than invent one, filtering is the
generic `--universe` file, which serves that use and any other.

**Placeholders.** None: every code step carries complete code, every run step an
exact command and its expected output.

**Type consistency.** `load_universe -> Optional[Set[str]]`,
`apply_universe(transitions, universe) -> List[Transition]`, `rank -> List`,
`split_cap -> Tuple[List, List]`, `compact_line -> List[str]`,
`build_brief -> Tuple[str, str]` are used with those exact signatures in the
tests, the module and the CLI branch.
