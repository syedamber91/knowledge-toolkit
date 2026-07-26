"""Per-sector framework evolution: propose, never auto-commit.

Part 3 of the NotebookLM-brain plan. Fable's review of the original design
was explicit: header-parseability alone is not a content-quality check, and
a corrupted or low-quality framework poisons every downstream briefing. So
this module is deliberately read-only past parsing -- it produces a
reviewable diff string, never writes to decision-frameworks-v1.md itself.
A human approves the actual diff (per framework, per sector) before it is
committed to the vault; that write is a separate, explicit step outside
this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

from soic_senses.framework_router import Framework

_NEW_BLOCK = re.compile(
    r"###\s*NEW FRAMEWORK\s*\n##\s*FNEW\.\s*(.+?)\s*\n\n(.*?)(?=\n###|\Z)",
    re.DOTALL,
)
_REINFORCE_BLOCK = re.compile(
    r"###\s*REINFORCES\s+(F\d+)\s*\n(.*?)(?=\n###|\Z)",
    re.DOTALL,
)


@dataclass
class FrameworkProposal:
    new_frameworks: List[Framework] = field(default_factory=list)
    reinforcements: List[Tuple[str, str]] = field(default_factory=list)


def build_framework_evolution_prompt(sector_title: str, existing_frameworks: List[Framework]) -> str:
    """Build the prompt asking NotebookLM whether this sector reinforces an
    existing framework or reveals a new one.

    Lists every existing framework's id/title/Model line so NotebookLM can
    judge overlap against the CURRENT state (the caller should re-load
    existing_frameworks fresh each time, not reuse a stale snapshot from
    earlier in a run -- that's what makes the framework layer compound
    sector-over-sector, not just batch-over-batch).
    """
    lines = [
        f"You have analyzed the sector '{sector_title}'. Below are the existing "
        "SOIC decision frameworks already distilled from other sectors:",
        "",
    ]
    for fw in existing_frameworks:
        model_line = ""
        m = re.search(r"\*\*Model\.\*\*\s*(.+)", fw.body)
        if m:
            model_line = m.group(1).split("\n")[0].strip()
        lines.append(f"- {fw.id}. {fw.title} -- {model_line}")
    lines.append("")
    lines.append(
        "For each mechanism this sector's material illustrates, decide: does it "
        "REINFORCE one of the frameworks above (a new grounding example), or does "
        "it reveal a NEW mechanism not covered by any of them?"
    )
    lines.append("")
    lines.append(
        "For a reinforcement, respond with:\n"
        "### REINFORCES F<n>\n"
        "<one paragraph: the new grounding example, with citations>"
    )
    lines.append("")
    lines.append(
        "For a new mechanism, respond with:\n"
        "### NEW FRAMEWORK\n"
        "## FNEW. <title>\n\n"
        "**Model.** ...\n\n**Applies when.** ...\n\n**Ask.** ...\n\n"
        "**Live data.** ...\n\n**Grounding.** ..."
    )
    return "\n".join(lines)


def parse_framework_response(response_text: str) -> FrameworkProposal:
    """Parse NotebookLM's answer into new-framework blocks and
    reinforcement statements. Purely mechanical (regex) -- the judgment of
    whether a proposed mechanism is genuinely novel was already made by the
    NotebookLM query; this just extracts what it said.
    """
    proposal = FrameworkProposal()

    for m in _NEW_BLOCK.finditer(response_text):
        title, body = m.group(1).strip(), m.group(2).strip()
        proposal.new_frameworks.append(Framework(id="FNEW", title=title, body=body))

    for m in _REINFORCE_BLOCK.finditer(response_text):
        fid, addition = m.group(1), m.group(2).strip()
        proposal.reinforcements.append((fid, addition))

    return proposal


def assign_next_framework_numbers(
    proposal: FrameworkProposal, existing_frameworks: List[Framework]
) -> FrameworkProposal:
    """Replace each new framework's 'FNEW' placeholder id with the next
    sequential F-number after the current max, in the order proposed.
    """
    max_id = 0
    for fw in existing_frameworks:
        n = int(fw.id[1:])
        max_id = max(max_id, n)

    numbered = []
    for i, fw in enumerate(proposal.new_frameworks):
        numbered.append(Framework(id=f"F{max_id + 1 + i}", title=fw.title, body=fw.body))

    return FrameworkProposal(new_frameworks=numbered, reinforcements=proposal.reinforcements)


def render_proposed_diff(existing_frameworks: List[Framework], proposal: FrameworkProposal) -> str:
    """Render a human-readable preview of what WOULD be added to
    decision-frameworks-v1.md. Read-only: never touches the actual file --
    a human reviews this string and approves (or rejects/edits) before any
    write happens, as a separate explicit step.
    """
    lines = ["# Proposed framework-file diff (NOT YET APPLIED — needs human sign-off)", ""]

    if proposal.new_frameworks:
        lines.append("## New frameworks to append")
        lines.append("")
        for fw in proposal.new_frameworks:
            lines.append(f"## {fw.id}. {fw.title}")
            lines.append("")
            lines.append(fw.body)
            lines.append("")

    if proposal.reinforcements:
        lines.append("## Grounding additions to existing frameworks")
        lines.append("")
        by_id = {fw.id: fw for fw in existing_frameworks}
        for fid, addition in proposal.reinforcements:
            title = by_id[fid].title if fid in by_id else "(unknown framework id)"
            lines.append(f"### {fid}. {title}")
            lines.append(f"+ {addition}")
            lines.append("")

    if not proposal.new_frameworks and not proposal.reinforcements:
        lines.append("(no changes proposed)")

    return "\n".join(lines)
