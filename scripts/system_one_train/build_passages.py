"""Option A: weak-labelled transcript passages from the concept notes' own citations.
Each concept note cites (REF HH:MM:SS[-HH:MM:SS]) spans of lecture transcripts; the cited passage inherits the note's tags.
Weak labels: the note's tags describe the whole note, not necessarily that passage; speech-to-text is noisy.
TRAIN-split modules only go into train_passages.jsonl (test modules are never used for training - same topic split as common.py).
Private: transcripts are paid-course content. Output stays in output/ (gitignored) and on the owner's VPS."""
import bisect, json, random, re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import CONCEPTS, HUB, OUT, load_notes, split

CONTENT = Path(__file__).resolve().parents[3].parent.parent.parent / "data" / "content.json"  # fallback below
for cand in (Path.home() / "Documents/workspace/Claude_Code/SOIC_Scraper/data/content.json",):
    if cand.exists(): CONTENT = cand
REFS = HUB / "wiki/personas/soic/refs"
CITE = re.compile(r"\(([A-Z0-9]{2,8}) (\d\d:\d\d:\d\d)(?:-(\d\d:\d\d:\d\d))?\)")
MARK = re.compile(r"\[(\d\d):(\d\d):(\d\d)\]")
MAX_PER_NOTE, MIN_WORDS, MAX_WORDS, SEED = 12, 40, 200, 7


def sec(t): h, m, s = map(int, t.split(":")); return h * 3600 + m * 60 + s


def lessons():
    d = json.load(open(CONTENT)); out = {}
    for c in d["courses"]:
        for m in c.get("modules") or []:
            for l in m.get("lessons") or []:
                if l.get("body_text"): out[l["url"].rstrip("/").rsplit("/", 1)[-1]] = l["body_text"]
    return out


def passage(body, markers, t1, t2):
    secs = [s for s, _ in markers]
    i = max(bisect.bisect_right(secs, sec(t1)) - 1, 0)
    start = markers[i][1]
    end = len(body)
    if t2:
        j = bisect.bisect_right(secs, sec(t2)); end = markers[j][1] if j < len(markers) else len(body)
    else:
        end = markers[i + 4][1] if i + 4 < len(markers) else len(body)
    txt = MARK.sub(" ", body[start:end]); w = txt.split()
    return " ".join(w[:MAX_WORDS])


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "train"   # "test" = diagnostics only, NEVER for training
    L = lessons(); train, test = split(load_notes()); keep = {n["slug"]: n for n in (test if which == "test" else train)}
    rng = random.Random(SEED); rows, miss = [], Counter()
    idx = {}
    for lid, body in L.items():
        ms = [(sec(f"{a}:{b}:{c}"), m.start()) for m in MARK.finditer(body) for a, b, c in [m.groups()]]
        idx[lid] = (body, ms)
    for slug, n in keep.items():
        refmap = {v: k for k, v in json.load(open(REFS / f"{n['topic']}.json")).items()}
        text = (CONCEPTS / f"{slug}.md").read_text(); seen, cands = set(), []
        for ref, t1, t2 in CITE.findall(text):
            lid = refmap.get(ref)
            if lid is None or lid not in idx: miss["unresolved_ref"] += 1; continue
            key = (lid, sec(t1) // 60)
            if key in seen: continue
            seen.add(key)
            body, ms = idx[lid]
            if not ms: miss["no_markers"] += 1; continue
            p = passage(body, ms, t1, t2 or None)
            if len(p.split()) < MIN_WORDS: miss["too_short"] += 1; continue
            cands.append(p)
        rng.shuffle(cands)
        for k, p in enumerate(cands[:MAX_PER_NOTE]):
            rows.append({"id": f"{slug}#{k}", "note": slug, "topic": n["topic"], "tags": n["tags"], "text": p})
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{which}_passages.jsonl", "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    tc = Counter(t for r in rows for t in r["tags"])
    print(f"{which} notes={len(keep)} passages={len(rows)} notes_with_passages={len({r['note'] for r in rows})} skipped={dict(miss)}")
    print("avg words", round(sum(len(r['text'].split()) for r in rows) / max(len(rows), 1)), "tag counts", dict(tc))


if __name__ == "__main__":
    main()
