from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from storm_core import config
from storm_core.html_render import render_html
from storm_core.models import StormReport
from storm_core.report import build_note_markdown
from storm_core.roster import discover_roster


def _slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "untitled"


def _cmd_roster(_args) -> int:
    data = [p.model_dump() for p in discover_roster()]
    print(json.dumps(data))
    return 0


def _cmd_build(args) -> int:
    report = StormReport.model_validate_json(Path(args.report).read_text(encoding="utf-8"))
    reports_dir = Path(args.reports_dir) if args.reports_dir else config.REPORTS_DIR
    html_dir = Path(args.html_dir) if args.html_dir else config.HTML_OUT_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(report.topic)
    note_path = reports_dir / f"{slug}.md"
    html_path = html_dir / f"{slug}.html"
    note_path.write_text(build_note_markdown(report), encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    print(note_path)
    print(html_path)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="storm_core")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("roster")
    b = sub.add_parser("build")
    b.add_argument("--report", required=True)
    b.add_argument("--reports-dir")
    b.add_argument("--html-dir")
    args = parser.parse_args(argv)
    if args.cmd == "roster":
        return _cmd_roster(args)
    return _cmd_build(args)


if __name__ == "__main__":
    sys.exit(main())
