"""Build Home.md, Log.md and topics/*.md for knowledge/system-one from note frontmatter.
Log is append-only: backfill wording first time, growth/removal only when the total changes."""
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "knowledge" / "system-one"
FOLDERS = [
    ("00-orientation", "Orientation"), ("01-concepts", "Concepts & primitives"),
    ("02-patterns", "Patterns"), ("03-cookbooks", "Cookbooks"),
    ("04-use-cases", "Use cases & demos"), ("05-api-sdk", "API & SDKs"),
    ("06-agent-tooling", "Agent tooling & community"),
    ("07-alternatives", "Alternatives (Laya, Kev, MiniLM...)"),
    ("08-playbook", "Playbook (agent decision rules)"),
]
TOPICS = {
    "topic-calibration": ("Calibration & confidence", "Probabilities that mean something; confidence vs probability; thresholds."),
    "topic-routing": ("Routing", "Send each input to code, a small model, an LLM or a human based on answer + confidence."),
    "topic-classification": ("Classification", "Choice-based labelling, hierarchies, 'unsure' outcomes."),
    "topic-extraction": ("Extraction", "Pulling dates, values, structure and fields out of text, verified in code."),
    "topic-guardrails": ("Guardrails & verification", "Screening, citation checks, hazard scoring, pass/review/block."),
    "topic-retrieval-rerank": ("Retrieval & rerank", "Shortlist cheaply, then score candidates with typed questions."),
    "topic-cost-latency": ("Cost & latency", "Batching, fan-out, cascades; the measured numbers."),
    "topic-state-design": ("State design", "What to put in state; how to word questions, options, levels."),
    "topic-agent-integration": ("Agent integration", "MCP server, agent skill, SDKs, OpenRouter, cloud/local setup."),
    "topic-model-selection": ("Model selection", "Jev vs Laya vs Kev vs MiniLM vs LLMs: when each wins."),
}


def fm(t):
    m = re.match(r"---\n(.*?)\n---\n", t, re.S)
    d = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" in line:
            k, v = line.split(":", 1); d[k.strip()] = v.strip()
    return d


def gist(t):
    m = re.search(r"^> (.+)$", t, re.M)
    return m.group(1).strip() if m else ""


notes = {}
for folder, _ in FOLDERS:
    for p in sorted((ROOT / folder).glob("*.md")):
        t = p.read_text()
        d = fm(t)
        notes[p.stem] = dict(folder=folder, title=d.get("title", p.stem),
                             topics=[x.strip() for x in d.get("topics", "").strip("[]").split(",") if x.strip()],
                             gist=gist(t))

(ROOT / "topics").mkdir(exist_ok=True)
for slug, (title, blurb) in TOPICS.items():
    rows = [f"- [[{s}]] — {n['gist']}" for s, n in notes.items() if slug in n["topics"]]
    body = (f"---\ntitle: {title}\nkind: topic\nsource: generated from note frontmatter\ntags: [system-one]\ntopics: []\n---\n"
            f"# {title}\n> {blurb}\n\n## Notes on this topic ({len(rows)})\n" + "\n".join(rows) + "\n\n"
            "Back to [[Home]].\n")
    (ROOT / "topics" / f"{slug}.md").write_text(body)

home = ["---\ntitle: System One Home\nkind: index\nsource: generated\ntags: [system-one]\ntopics: []\n---\n",
        "# System One — Home\n> Everything from TypeSafe's Jev / System One docs plus the open alternatives (Laya, Kev, MiniLM), "
        "condensed for autonomous agents. Start at [[when-to-use-which-model]] or [[agent-operating-protocol]]. "
        "History: [[Log|Ingestion Log]].\n"]
home.append("## Topic hubs\n" + "\n".join(f"- [[{s}]] — {b}" for s, (_, b) in TOPICS.items()) + "\n")
for folder, label in FOLDERS:
    rows = [f"- [[{s}]] — {n['gist']}" for s, n in notes.items() if n["folder"] == folder]
    home.append(f"## {label}\n" + "\n".join(rows) + "\n")
(ROOT / "Home.md").write_text("\n".join(home))

logp = ROOT / "Log.md"
total = len(notes)
prev = None
if logp.exists():
    m = re.findall(r"\((\d+) total", logp.read_text())
    prev = int(m[-1]) if m else None
today = date.today().isoformat()
if prev is None:
    entry = f"- {today}: {total} item(s) already in vault (log started here) ({total} total)\n"
elif total > prev:
    entry = f"- {today}: {total - prev} new item(s) captured ({total} total)\n"
elif total < prev:
    entry = f"- {today}: {prev - total} item(s) removed ({total} total)\n"
else:
    entry = None
if entry:
    head = "" if logp.exists() else "# Ingestion Log\n> Append-only. Index is [[Home]].\n\n"
    with logp.open("a") as f:
        f.write(head + entry)
print(f"built: {total} notes, log entry: {'yes' if entry else 'no change'}")
