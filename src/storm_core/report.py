from __future__ import annotations

from storm_core.models import StormReport


def _finding_block(f) -> str:
    lines = [f"### {f.title} (reliability {f.reliability}/10)", "", f.detail, ""]
    if f.supported_by:
        lines.append(f"- supported by: {', '.join(f.supported_by)}")
    if f.challenged_by:
        lines.append(f"- challenged by: {', '.join(f.challenged_by)}")
    for e in f.evidence:
        date = f" ({e.date})" if e.date else ""
        lines.append(
            f"- evidence: {e.claim} — {e.source}{date} · grade {e.grade.value} · {e.status}"
        )
    lines.append("")
    return "\n".join(lines)


def build_note_markdown(report: StormReport) -> str:
    fm = [
        "---",
        f'title: "{report.topic}"',
        f"tags: [storm, {report.mode}]",
        f"verdict: {report.verdict.value}",
        f"generated: {report.generated}",
        f"lenses: [{', '.join(report.lenses)}]",
        "---",
        "",
        f"# {report.topic}",
        "",
        "## Summary",
        "",
        report.summary,
        "",
        f"## Verdict: {report.verdict.value}",
        "",
        "## Findings",
        "",
    ]
    parts = ["\n".join(fm)]
    for f in report.findings:
        parts.append(_finding_block(f))

    if report.contradictions:
        parts.append("## Contradiction Map\n")
        for c in report.contradictions:
            stances = "; ".join(f"{k}: {v}" for k, v in c.positions.items())
            parts.append(f"- **{c.topic}** — {stances}. → {c.resolution}")
        parts.append("")

    if report.halal_note.strip():
        parts.append("## Halal Note\n")
        parts.append(report.halal_note)
        parts.append("")

    return "\n".join(parts)
