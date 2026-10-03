"""Build the blind hand-check sheet (Fable's plan, 2026-10-03): 80 spoken test passages + 20 test notes.
Strata for the 80: 30 where Jev's choice top-1 is in the inherited tags, 30 confident disagreements (choice max >= 0.6, top-1 not inherited),
20 none/low (argmax "none" or max < 0.4). <= 2 passages per note. The sheet shows NO inherited tags and NO Jev output; the answer key
is a separate file. PRIVATE (paid-course text): written under output/ (gitignored), never published.
  build_handcheck.py [PASSAGES] [JEV2] [NOTES]"""
import html, json, random, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import OUT, TAGS
from laya_data import DEFS

root = Path(__file__).resolve().parents[2]
P_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / "test_passages.jsonl"
J_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/private/tmp/claude-501/fable/jev_labels2.jsonl")
N_PATH = Path(sys.argv[3]) if len(sys.argv) > 3 else OUT / "notes.jsonl"
rd = lambda p: [json.loads(l) for l in open(p)]
P = {r["id"]: r for r in rd(P_PATH)}; J = {r["id"]: r for r in rd(J_PATH)}; N = {r["slug"]: r for r in rd(N_PATH)}
rng = random.Random(11)

def info(i):
    ch = J[i]["choice"]; top = max(TAGS, key=lambda t: ch[t]); allmax = max(ch, key=ch.get)
    return top, ch[allmax], allmax, set(P[i]["tags"])
strata = {"agree": [], "disagree": [], "nonelow": []}
for i in P:
    if i not in J: continue
    top, mx, am, inh = info(i)
    if am == "none" or mx < 0.4: strata["nonelow"].append((i, inh))
    elif mx >= 0.6 and top not in inh: strata["disagree"].append((i, top))
    elif top in inh: strata["agree"].append((i, top))
want = {"agree": 30, "disagree": 30, "nonelow": 20}
used_notes = defaultdict(int); chosen = []
for s in ("nonelow", "disagree", "agree"):        # scarcest first
    by = defaultdict(list)
    items = strata[s][:]; rng.shuffle(items)
    for i, key in items:
        for t in (sorted(key) if s == "nonelow" else [key]): by[t].append(i)
    picked = []
    while len(picked) < want[s] and any(by.values()):
        for t in sorted(TAGS, key=lambda t: len(by[t])):
            while by[t] and (by[t][-1] in {c[0] for c in chosen + picked} or used_notes[P[by[t][-1]]["note"]] >= 2): by[t].pop()
            if by[t] and len(picked) < want[s]:
                i = by[t].pop(); picked.append((i, s)); used_notes[P[i]["note"]] += 1
    chosen += picked
rng.shuffle(chosen)
passages = [{"id": f"P{k+1:02d}", "text": P[i]["text"]} for k, (i, s) in enumerate(chosen)]
key = {f"P{k+1:02d}": {"real_id": i, "note": P[i]["note"], "stratum": s, "inherited": P[i]["tags"],
                       "jev_choice": J[i]["choice"], "jev_noul": J[i]["jev"]} for k, (i, s) in enumerate(chosen)}
# part 2: 20 test notes that have passages, <= 6500 chars, round-robin over inherited tags
cand = [n for n in N.values() if n["split"] == "test" and n["slug"] in {P[i]["note"] for i in P} and len(n["text"]) <= 6500]
rng.shuffle(cand); by = defaultdict(list)
for n in cand:
    for t in n["tags"]: by[t].append(n)
pn, seen = [], set()
while len(pn) < 20 and any(by.values()):
    for t in sorted(TAGS, key=lambda t: len(by[t])):
        while by[t] and by[t][-1]["slug"] in seen: by[t].pop()
        if by[t] and len(pn) < 20: n = by[t].pop(); seen.add(n["slug"]); pn.append(n)
rng.shuffle(pn)
notes = [{"id": f"N{k+1:02d}", "title": n["title"], "text": n["text"]} for k, n in enumerate(pn)]
nkey = {f"N{k+1:02d}": {"slug": n["slug"], "inherited": n["tags"]} for k, n in enumerate(pn)}

d = OUT / "handcheck"; d.mkdir(parents=True, exist_ok=True)
(d / "handcheck_key.json").write_text(json.dumps({"passages": key, "notes": nkey, "strata_sizes": {s: len(v) for s, v in strata.items()}}, indent=1))
DATA = {"tags": [{"tag": t, "desc": DEFS[t]} for t in TAGS], "passages": passages, "notes": notes}
data_js = json.dumps(DATA).replace("</", "<\\/")
PAGE = open(Path(__file__).parent / "handcheck_template.html").read().replace("__DATA__", data_js)
(d / "handcheck_sheet.html").write_text(PAGE)
from collections import Counter
print("strata available:", {s: len(v) for s, v in strata.items()}, "| picked:", dict(Counter(s for _, s in chosen)),
      "| notes in passages:", len({P[i]['note'] for i, _ in chosen}), "| part-2 notes:", len(notes))
print("sheet:", d / "handcheck_sheet.html")
