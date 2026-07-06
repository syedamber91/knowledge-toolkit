from __future__ import annotations

from html import escape

from storm_core.models import StormReport

_STYLE = (
    "body{font:16px/1.5 -apple-system,system-ui,sans-serif;max-width:760px;"
    "margin:2rem auto;padding:0 1rem;color:#1a1a1a}"
    ".badge{display:inline-block;padding:.2rem .6rem;border-radius:.4rem;"
    "background:#e8f0e8;font-weight:600}"
    ".finding{border-left:3px solid #ccc;padding:.2rem 0 .2rem 1rem;margin:1rem 0}"
    ".rel{color:#666;font-size:.85rem}"
)


def render_html(report: StormReport) -> str:
    ranked = sorted(report.findings, key=lambda f: f.reliability, reverse=True)
    rows = []
    for f in ranked:
        rows.append(
            f'<div class="finding"><strong>{escape(f.title)}</strong> '
            f'<span class="rel">(reliability {f.reliability}/10)</span>'
            f"<p>{escape(f.detail)}</p></div>"
        )
    contra = ""
    if report.contradictions:
        items = "".join(
            f"<li><strong>{escape(c.topic)}</strong>: "
            + escape("; ".join(f"{k}={v}" for k, v in c.positions.items()))
            + f" → {escape(c.resolution)}</li>"
            for c in report.contradictions
        )
        contra = f"<h2>Contradiction Map</h2><ul>{items}</ul>"
    return (
        "<!doctype html>\n<html><head><meta charset='utf-8'>"
        f"<title>{escape(report.topic)}</title><style>{_STYLE}</style></head><body>"
        f"<h1>{escape(report.topic)}</h1>"
        f'<p><span class="badge">{escape(report.verdict.value)}</span></p>'
        f"<h2>Summary</h2><p>{escape(report.summary)}</p>"
        f"<h2>Findings</h2>{''.join(rows)}"
        f"{contra}"
        "</body></html>"
    )
