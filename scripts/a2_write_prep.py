"""Build the 22 write prompts from the reduce result, with an evidence budget.

Concepts drew 1-149 beats. A write prompt cannot carry 149 raw slices, so
evidence is RANKED and BUDGETED per note:

  rank: worked_example+numbers > framework > heuristic > caveat > sector_fact,
        then by span length (longer teaching passages first)
  dedupe: a beat whose span overlaps an already-selected span >60% is skipped
  budget: ~45K chars of excerpt text per prompt

Dropped beats are RECORDED per concept (never silently discarded) — they are
future enrichment material and an honesty ledger for what the note omits.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soic_method.corpus import load_corpus  # noqa: E402
from soic_method.eligibility import apply_eligibility, load_eligibility  # noqa: E402
from soic_wiki.pipeline import Beat, WriteJob, build_write_prompt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "out" / "a2"

BUDGET_CHARS = 45_000
KIND_RANK = {"worked_example": 0, "framework": 1, "heuristic": 2,
             "caveat": 3, "sector_fact": 4}


def overlap_frac(a: Beat, b: Beat) -> float:
    if a.lesson_id != b.lesson_id:
        return 0.0
    inter = min(a.char_end, b.char_end) - max(a.char_start, b.char_start)
    if inter <= 0:
        return 0.0
    shorter = min(a.char_end - a.char_start, b.char_end - b.char_start)
    return inter / max(shorter, 1)


def select(beats, budget=BUDGET_CHARS):
    """Budgeted, LESSON-DIVERSE selection.

    Plain rank-by-length let one lesson's long beats monopolize the budget:
    the A2 practical-valuation prompt ended up with ZERO excerpts from the
    Spotting Turnarounds lesson even though reduce had assigned its worked
    valuation (idx 547) — regressing exactly what T1 proved. Within each
    (kind, has_numbers) tier, beats are now taken round-robin across lessons,
    so every assigned lesson's best evidence is represented before any lesson
    gets its second pick.
    """
    tiers = {}
    for b in beats:
        tiers.setdefault((KIND_RANK.get(b.kind, 9), 0 if b.has_numbers else 1),
                         {}).setdefault(b.lesson_id, []).append(b)
    ordered = []
    for tier_key in sorted(tiers):
        by_lesson = tiers[tier_key]
        for lst in by_lesson.values():
            lst.sort(key=lambda b: -(b.char_end - b.char_start))
        queues = sorted(by_lesson.items())          # deterministic lesson order
        while any(lst for _, lst in queues):
            for _, lst in queues:                   # one per lesson per round
                if lst:
                    ordered.append(lst.pop(0))

    picked, dropped, used = [], [], 0
    for b in ordered:
        size = b.char_end - b.char_start
        if used + size > budget or any(overlap_frac(b, p) > 0.6 for p in picked):
            dropped.append(b)
            continue
        picked.append(b)
        used += size
    picked.sort(key=lambda b: (b.lesson_id, b.char_start))
    return picked, dropped, used


def main() -> int:
    elig = load_eligibility(ROOT / "configs" / "course_eligibility.yaml")
    lessons = {l.lesson_id: l for l in
               apply_eligibility(load_corpus(ROOT / "data" / "content.json"), elig)
               if l.eligible}
    beats = [Beat(**b) for b in json.loads((A2 / "all_beats.json").read_text())]
    reduce_res = json.loads((A2 / "reduce_result.json").read_text())
    concepts = json.loads((A2 / "concepts.json").read_text())
    refs = json.loads((A2 / "refs.json").read_text())

    (A2 / "write_prompts").mkdir(exist_ok=True)

    # Pass 1: per-concept budgeted selection.
    selections = {}
    for slug, idxs in sorted(reduce_res["assignments"].items()):
        cbeats = [beats[i] for i in idxs]
        picked, dropped, used = select(cbeats)
        selections[slug] = {"idxs": idxs, "picked": picked, "used": used}

    # Pass 2: GLOBAL coverage top-up. A beat assigned to two concepts can be
    # budget-dropped by both, so its teaching lands in NO prompt at all —
    # measured on the pilot: 16 enrichment-cited spans fell through exactly
    # this crack. Every assigned beat now surfaces in at least one note: each
    # globally-unused beat goes to its owning concept with the most headroom,
    # inside a raised top-up budget. Deliberately oracle-independent (it
    # maximizes BEAT coverage, not oracle-span coverage) so the pilot's
    # oracle-recall metric stays a real test rather than a training target.
    TOPUP_BUDGET = 58_000
    picked_keys = {(b.lesson_id, b.char_start, b.char_end)
                   for s in selections.values() for b in s["picked"]}
    for i, b in enumerate(beats):
        key = (b.lesson_id, b.char_start, b.char_end)
        if key in picked_keys:
            continue
        owners = [slug for slug, s in selections.items() if i in s["idxs"]]
        if not owners:
            continue                      # reducer left it unassigned
        owners.sort(key=lambda s: selections[s]["used"])
        for slug in owners:
            s = selections[slug]
            size = b.char_end - b.char_start
            if s["used"] + size <= TOPUP_BUDGET and \
                    not any(overlap_frac(b, p) > 0.6 for p in s["picked"]):
                s["picked"].append(b)
                s["used"] += size
                picked_keys.add(key)
                break

    ledger = {}
    for slug, s in sorted(selections.items()):
        picked = sorted(s["picked"], key=lambda b: (b.lesson_id, b.char_start))
        job = WriteJob(concept_title=slug.replace("-", " ").title(),
                       concept_scope=concepts[slug], slug=slug,
                       beats=picked, refs=refs)
        prompt = build_write_prompt(job, lessons)
        (A2 / "write_prompts" / ("%s.txt" % slug)).write_text(prompt, encoding="utf-8")
        ledger[slug] = {"assigned": len(s["idxs"]), "used": len(picked),
                        "excerpt_chars": s["used"], "prompt_chars": len(prompt)}
        print("%-46s beats=%3d used=%3d prompt=%6d chars"
              % (slug, len(s["idxs"]), len(picked), len(prompt)))
    uncovered = [i for i, b in enumerate(beats)
                 if (b.lesson_id, b.char_start, b.char_end) not in picked_keys
                 and any(i in s["idxs"] for s in selections.values())]
    print("assigned beats still in no prompt: %d" % len(uncovered))

    (A2 / "write_ledger.json").write_text(json.dumps(ledger, indent=1),
                                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
