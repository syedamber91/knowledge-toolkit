"""ask: one question -> cited hits from the annual report + calls + decks + announcements. No model.

usage: ask.py "question" --data BIOCON/data --ar BIOCON/annual-report/FY26 [--number "7,245"] [-k 5] [--note VAULT/BIOCON.md]

Every hit names its source and page/date. With --number, the answer is "ok" only if those exact
digits are on a retrieved hit; otherwise it REFUSES (never falls back to memory or a guess). "ok"
proves the digits are on that page, not that they belong to the line item asked about.
"""
import argparse
from datetime import datetime
import re
import sys
from pathlib import Path

from vps_extraction.multi_index import chunk_text, search as multi_search
from vps_extraction.page_index import _has_number, build_index, query_terms, search as ar_search


def _snippet(text: str, terms, number=None, width=110) -> str:
    flat = " ".join(text.split())
    at = flat.find(number) if number and number in flat else -1
    if at < 0:
        m = next(filter(None, (re.search(re.escape(t), flat, re.I) for t in terms)), None)
        at = m.start() if m else 0
    return flat[max(0, at - width): at + width]


def ask(question: str, ar_conn, multi_conn, k: int = 5, number: str = None, width: int = 110, text_cap: int = 6000) -> dict:
    terms = query_terms(question)
    hits = []
    for page, score in ar_search(ar_conn, question, k):
        text = ar_conn.execute("select text from pages where page=?", (page,)).fetchone()[0]
        hits.append({"source": "annual-report", "label": f"AR p{page}", "score": score, "text": text})
    for source, label, score in multi_search(multi_conn, question, k):
        hits.append({"source": source, "label": label, "score": score, "text": chunk_text(multi_conn, source, label)})
    hits.sort(key=lambda h: h["score"])  # bm25: lower is better; scores are per-index, so this is a rough merge
    out = {"hits": [], "status": "ok" if hits else "refuse"}
    for h in hits:
        out["hits"].append({"source": h["source"], "label": h["label"],
                            "snippet": _snippet(h["text"], terms, number if number and _has_number(h["text"], number) else None, width),
                            "text": _snippet(h["text"], terms, number if number and _has_number(h["text"], number) else None, text_cap // 2)})
        if number and "found_in" not in out and _has_number(h["text"], number):
            out["found_in"] = (h["source"], h["label"])
    if number and "found_in" not in out:
        out["status"] = "refuse"
    return out


def write_note(path, question: str, result: dict, number, when: str) -> None:
    """Append one dated section to an Obsidian note (created with frontmatter if missing). Never overwrites."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("---\ntags:\n  - ask-note\n  - biocon\n---\n\n# BIOCON - ask log\n\n"
                        "Append-only. Each section is one `ask.py` run: cited hits from the annual report, calls, "
                        "decks and announcements. A number marked OK is on that page; that does not prove it is "
                        "the line item asked about.\n")
    lines = [f"\n## {when} - {question}\n"]
    if number:
        lines.append(f"**{result['status'].upper()}** - {number}" + (
            f" is on {result['found_in'][0]} {result['found_in'][1]}\n" if result["status"] == "ok"
            else " is not on any retrieved page; no answer given\n"))
    elif result["status"] == "refuse":
        lines.append("**REFUSE** - nothing matched\n")
    lines += [f"- `{h['source']} {h['label']}` - {h['snippet']}" for h in result["hits"]]
    with path.open("a") as f:
        f.write("\n".join(lines) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("question")
    ap.add_argument("--data", required=True, type=Path, help="BIOCON/data (calls, decks-layout, announcements)")
    ap.add_argument("--ar", required=True, type=Path, help="annual-report/FYxx dir of pNNN.md pages")
    ap.add_argument("--number")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--note", type=Path, help="append the result to this Obsidian note (created if missing)")
    a = ap.parse_args(argv)
    from vps_extraction.eval_multi_index import load_chunks
    from vps_extraction.multi_index import build
    r = ask(a.question, build_index(a.ar), build(load_chunks(a.data)), a.k, a.number)
    for h in r["hits"]:
        print(f"[{h['source']}] {h['label']}\n    ...{h['snippet']}...")
    if a.number:
        print(f"\n{r['status'].upper()}" + (f": {a.number} is on {r['found_in'][0]} {r['found_in'][1]}" if r["status"] == "ok"
                                           else f": {a.number} is not on any retrieved page - no answer given"))
    elif r["status"] == "refuse":
        print("\nREFUSE: nothing matched")
    if a.note:
        write_note(a.note, a.question, r, a.number, datetime.now().strftime("%Y-%m-%d %H:%M"))
        print(f"note: {a.note}")
    return 0 if r["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
