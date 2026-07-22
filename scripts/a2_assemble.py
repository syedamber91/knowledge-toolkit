"""A2 assembly: load beats -> validate -> build the reduce prompt.

Run after all 9 map agents have written their beats files. Validates every
beat through the real parser (range/kind checks + timestamp resolution),
merges with the T1 lesson's already-validated beats, and emits the reduce
prompt for the clustering call.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, "/Users/syedamberiqbal/Library/Mobile Documents/"
                   "iCloud~md~obsidian/Documents/learning-vault/src")

from de_toolkit.vault import slugify  # noqa: E402

from soic_method.corpus import load_corpus  # noqa: E402
from soic_method.eligibility import apply_eligibility, load_eligibility  # noqa: E402
from soic_wiki.pipeline import map_lesson  # noqa: E402
from soic_wiki.reduce import build_reduce_prompt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "out" / "a2"


def main() -> int:
    elig = load_eligibility(ROOT / "configs" / "course_eligibility.yaml")
    lessons = [l for l in apply_eligibility(load_corpus(ROOT / "data" / "content.json"), elig)
               if l.eligible]
    by_slug = {slugify(l.title): l for l in lessons}
    by_id = {l.lesson_id: l for l in lessons}

    meta = json.loads((A2 / "lessons.json").read_text())
    refs = json.loads((A2 / "refs.json").read_text())
    concepts = json.loads((A2 / "concepts.json").read_text())

    all_beats = []
    report = []
    for slug, m in sorted(meta.items()):
        f = A2 / ("beats_%s.json" % slug)
        if not f.exists():
            report.append("MISSING beats for %s" % slug)
            continue
        lesson = by_id[m["lesson_id"]]
        raw = f.read_text(encoding="utf-8")
        n_raw = len(json.loads(raw).get("beats", []))
        beats = map_lesson(lesson, lambda p, r=raw: r)
        all_beats.extend(beats)
        report.append("%-44s raw=%-3d accepted=%-3d" % (slug, n_raw, len(beats)))

    # T1's lesson (already validated during A1)
    t1_raw = (ROOT / "out" / "t1" / "beats.json").read_text(encoding="utf-8")
    turn = by_slug["spotting-turnarounds-ias-2024"]
    t1_beats = map_lesson(turn, lambda p: t1_raw)
    all_beats.extend(t1_beats)
    report.append("%-44s raw=%-3d accepted=%-3d (from A1)"
                  % ("spotting-turnarounds-ias-2024", len(t1_beats), len(t1_beats)))

    print("\n".join(report))
    print("TOTAL beats: %d across %d lessons"
          % (len(all_beats), len({b.lesson_id for b in all_beats})))

    (A2 / "all_beats.json").write_text(
        json.dumps([b.model_dump() for b in all_beats], indent=1), encoding="utf-8")
    prompt = build_reduce_prompt(concepts, all_beats, refs)
    (A2 / "reduce_prompt.txt").write_text(prompt, encoding="utf-8")
    print("reduce prompt: %d chars -> out/a2/reduce_prompt.txt" % len(prompt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
