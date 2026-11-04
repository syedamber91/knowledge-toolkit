"""Case-book line '(AR pN)' -> do its numbers really appear on file pNNN.md? (mechanical, no model)"""
import re
from pathlib import Path

CITE = re.compile(r"\(AR p([\d, p–-]+)\)")
NUM = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+%?|\d+%")


def parse_line(line):
    m = CITE.search(line)
    if not m:
        return None
    pages = [int(x) for x in re.findall(r"\d+", m.group(1))]
    nums = NUM.findall(line[: m.start()])
    return {"text": line.strip(), "pages": pages, "numbers": nums}


def check_row(row, pages_dir):
    text = ""
    for p in row["pages"]:
        f = Path(pages_dir) / f"p{p:03d}.md"
        if f.exists():
            text += f.read_text(encoding="utf8", errors="replace")
    return {**row, "missing": [n for n in row["numbers"] if n not in text]}
