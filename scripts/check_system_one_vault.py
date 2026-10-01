"""Check the System One vault: every expected slug exists, frontmatter has the
required keys, tags/topics come from the fixed vocab, no dangling [[links]]."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "knowledge" / "system-one"
TAGS = set("system-one primitives confidence patterns cookbook routing classification extraction retrieval-rerank guardrails evaluation api-sdk agent-tooling alternatives cost-latency state-design use-case model-limits".split())
TOPICS = set("topic-calibration topic-routing topic-classification topic-extraction topic-guardrails topic-retrieval-rerank topic-cost-latency topic-state-design topic-agent-integration topic-model-selection".split())
KEYS = ("title", "kind", "source", "tags", "topics")


def fm(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def lst(v):
    return [x.strip() for x in v.strip("[]").split(",") if x.strip()]


notes = {p.stem: p for p in ROOT.rglob("*.md") if p.stem not in ("Home", "Log")}
errs = []
for slug, p in sorted(notes.items()):
    t = p.read_text()
    f = fm(t)
    if f is None:
        errs.append(f"{slug}: no frontmatter"); continue
    for k in KEYS:
        if k not in f:
            errs.append(f"{slug}: missing {k}")
    if p.parent.name != "topics":
        for x in lst(f.get("tags", "")):
            if x not in TAGS: errs.append(f"{slug}: bad tag {x}")
        for x in lst(f.get("topics", "")):
            if x not in TOPICS: errs.append(f"{slug}: bad topic {x}")
    for l in re.findall(r"\[\[([^\]|#]+)", t):
        if l.strip() not in notes and l.strip() not in ("Home", "Log"):
            errs.append(f"{slug}: dangling [[{l.strip()}]]")
print(f"{len(notes)} notes, {len(errs)} problems")
for e in errs: print(" ", e)
sys.exit(1 if errs else 0)
