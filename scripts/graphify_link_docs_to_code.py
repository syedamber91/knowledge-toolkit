"""Stitch graphify's doc layer to its code layer (run after every /graphify refresh).

graphify extracts code by AST and docs by an LLM pass, in separate id spaces, so a doc node about `sector_gate.py` never
connects to the code node `sector_gate.py` (2 of 9,611 edges crossed in the 2026-10-03 graph) and "how does this note relate
to that code" comes back empty. This adds `doc -> code` edges where a doc/rationale node's label literally names a code file
or function. Deterministic, no LLM, and it never guesses: a name that matches two code nodes is skipped.

    EXTRACTED  the label names the file by path with a directory ("soic_wiki/sector_gate.py")
    INFERRED   the label names a bare file, a `name()` call, or a snake_case identifier that is unique in the code

Communities are NOT recomputed (that would invalidate the hand-written community labels in GRAPH_REPORT.md); the edges are
for query/path/explain. Usage: python scripts/graphify_link_docs_to_code.py [graphify-out/graph.json]
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CODE_EXTS = ("py", "js", "ts", "tsx", "sh")
PATH_RE = re.compile(r"[\w./-]+\.(?:%s)\b" % "|".join(CODE_EXTS))
CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\(\)")
SNAKE_RE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
DOC_TYPES = ("document", "rationale")


def link_docs_to_code(data: dict) -> list:
    """New doc->code links for a graph.json dict. Does not modify ``data``."""
    nodes = data["nodes"]
    code = [n for n in nodes if n.get("file_type") == "code"]
    files_by_label = defaultdict(list)  # "sector_gate.py" -> [code file nodes]
    names = defaultdict(list)           # "verify_rule" -> [code function nodes] (label "verify_rule()" or "verify_rule")
    for n in code:
        label = n.get("label", "")
        if PATH_RE.fullmatch(label):
            files_by_label[label].append(n)
        elif re.fullmatch(r"\w+(\(\))?", label):
            names[label[:-2] if label.endswith("()") else label].append(n)
    linked = {frozenset((l["source"], l["target"])) for l in data["links"]}

    out, seen = [], set()

    def add(doc, target, confidence):
        pair = frozenset((doc["id"], target["id"]))
        if pair in linked or pair in seen or doc.get("source_file") == target.get("source_file"):
            return
        seen.add(pair)
        out.append({"source": doc["id"], "target": target["id"], "relation": "references", "confidence": confidence,
                    "confidence_score": 1.0 if confidence == "EXTRACTED" else 0.8,
                    "source_file": doc.get("source_file"), "source_location": None, "weight": 1.0})

    for doc in (n for n in nodes if n.get("file_type") in DOC_TYPES):
        label = doc.get("label", "")
        for tok in PATH_RE.findall(label):
            tok = tok.lstrip("./")
            base = tok.rsplit("/", 1)[-1]
            hits = [f for f in files_by_label.get(base, []) if f.get("source_file", "").endswith(tok)]
            if len(hits) == 1:
                add(doc, hits[0], "EXTRACTED" if "/" in tok else "INFERRED")
        for name in CALL_RE.findall(label):
            if "_" in name and len(names.get(name, [])) == 1:  # one-word names (normalize, main, load) collide across repos
                add(doc, names[name][0], "INFERRED")
        for name in SNAKE_RE.findall(label):
            if len(name) >= 8 and len(names.get(name, [])) == 1:
                add(doc, names[name][0], "INFERRED")
    return out


def apply_links(data: dict) -> int:
    new = link_docs_to_code(data)
    data["links"].extend(new)
    return len(new)


def main(argv=None) -> int:
    path = Path((argv or sys.argv[1:] or ["graphify-out/graph.json"])[0])
    data = json.loads(path.read_text())
    added = apply_links(data)
    path.write_text(json.dumps(data, indent=2))
    print(f"{path}: added {added} doc->code links ({len(data['links'])} total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
