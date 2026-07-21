"""Emit the spec bundle.

Two tiers land in separate files because they execute differently: knockouts
are hard exclusions, graded rules rank and flag but never exclude.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from .models import LessonRecord, Rule
from .reconcile import ReconcileOutput

GAPS_HEADER = """# Data gaps

Rules SOIC states and the verifier accepted, which cannot execute because the
platform has no field to run them against. Sourced from the method, not guessed.

"""


def _dump(rules: List[Rule]) -> str:
    return yaml.safe_dump(
        [r.model_dump(mode="json", exclude_none=True) for r in rules],
        sort_keys=False, allow_unicode=True,
    )


def write_bundle(
    out: ReconcileOutput, lessons: Dict[str, LessonRecord], dest: Path
) -> None:
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Status gates publication, not just tier. The pipeline sets `status`
    # faithfully and then used to publish regardless of it, so a
    # `needs_audio_check` knockout -- a rule the pipeline itself flagged as
    # needing human ear verification -- shipped in knockouts.yaml
    # indistinguishable from a corroborated one, and a downstream consumer
    # executing that file as hard exclusions would apply it
    # (final-branch-review.md I2). Only `active` rules reach the two
    # executable files; everything else joins drafts.yaml, which is the
    # existing not-yet-executable queue.
    active = [r for r in out.rules if r.status == "active"]
    withheld = [r for r in out.rules if r.status != "active"]

    knockouts = [r for r in active if r.tier == "knockout"]
    graded = [r for r in active if r.tier != "knockout"]

    (dest / "knockouts.yaml").write_text(_dump(knockouts), encoding="utf-8")
    (dest / "graded.yaml").write_text(_dump(graded), encoding="utf-8")
    (dest / "drafts.yaml").write_text(_dump(out.drafts + withheld), encoding="utf-8")

    (dest / "conflicts.open.yaml").write_text(
        yaml.safe_dump(
            [[r.model_dump(mode="json", exclude_none=True) for r in g]
             for g in out.conflicts],
            sort_keys=False, allow_unicode=True,
        ),
        encoding="utf-8",
    )

    # Corpus integrity: a re-capture with drifted ASR must hard-fail rather
    # than silently re-point citations at moved audio.
    (dest / "SNAPSHOT").write_text(
        yaml.safe_dump({lid: l.text_hash for lid, l in sorted(lessons.items())},
                       sort_keys=False),
        encoding="utf-8",
    )

    unbound = [r for r in out.rules if r.binding.status != "bound"]
    lines = [GAPS_HEADER]
    for r in unbound:
        lines.append("- `%s` (%s) — %s\n" % (r.rule_key, r.tier, r.binding.status))
    (dest / "gaps.md").write_text("".join(lines), encoding="utf-8")
