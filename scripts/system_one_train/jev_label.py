"""Option B via Jev: ask Jev (hosted, TypeSafe) to tag spoken TEST passages independently, then compare with the inherited labels.
12 noul questions per passage in ONE call. Sends ~150 short transcript passages (paid-course text, owner-approved 2026-10-03).
Never prints passage text or the key. Needs env TYPESAFE_API_KEY. stdlib only.
  jev_label.py run  PASSAGES OUT.jsonl [N=150]     |   jev_label.py dry PASSAGES [N]   |   jev_label.py analyze OUT.jsonl"""
import json, os, random, sys, time, urllib.request, urllib.error
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS
from laya_data import DEFS

URL = "https://api.typesafe.ai/v1/systemone"
QUESTIONS = {t: {"type": "noul", "instructions": f"This lecture passage is substantially about {DEFS[t]}.",
                 "criteria": {"true": "The passage substantially covers this.", "false": "The passage does not substantially cover this."}} for t in TAGS}


def sample(rows, n, seed=7):
    """round-robin over tags so rare tags are represented; deterministic."""
    rng = random.Random(seed); rows = rows[:]; rng.shuffle(rows); by = {t: [r for r in rows if t in r["tags"]] for t in TAGS}
    out, seen = [], set()
    while len(out) < n and any(by.values()):
        for t in sorted(TAGS, key=lambda t: len(by[t])):
            while by[t] and by[t][-1]["id"] in seen: by[t].pop()
            if by[t] and len(out) < n: r = by[t].pop(); seen.add(r["id"]); out.append(r)
    return out


def call(key, text, tries=4):
    body = json.dumps({"state": text, "model": "jev-latest", "questions": QUESTIONS}).encode()
    for k in range(tries):
        req = urllib.request.Request(URL, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in (429, 529) and k < tries - 1: time.sleep(2 ** (k + 1)); continue
            raise SystemExit(f"HTTP {e.code} from Jev (stopping; body not printed)")
        except urllib.error.URLError:
            if k < tries - 1: time.sleep(2 ** (k + 1)); continue
            raise SystemExit("network error talking to Jev")


def analyze(path):
    import numpy as np
    from sklearn.metrics import roc_auc_score, f1_score
    R = [json.loads(l) for l in open(path)]
    P = np.array([[r["jev"][t] for t in TAGS] for r in R]); Y = np.array([[int(t in r["tags"]) for t in TAGS] for r in R])
    top1 = float(np.mean([Y[i, int(np.argmax(P[i]))] == 1 for i in range(len(R))]))
    aucs = {t: roc_auc_score(Y[:, j], P[:, j]) for j, t in enumerate(TAGS) if 0 < Y[:, j].sum() < len(Y)}
    print(f"passages={len(R)}  model={R[0].get('model')}  Jev vs inherited labels: top1 {top1:.3f}  meanAUC {np.mean(list(aucs.values())):.3f}  "
          f"microF1@0.5 {f1_score(Y, P >= 0.5, average='micro', zero_division=0):.3f}")
    print("per-tag AUC:", {t: round(a, 2) for t, a in aucs.items()})
    print("mean Jev prob on inherited-true vs inherited-false tags:", round(float(P[Y == 1].mean()), 3), round(float(P[Y == 0].mean()), 3))


def main():
    cmd = sys.argv[1]
    if cmd == "analyze": return analyze(sys.argv[2])
    rows = [json.loads(l) for l in open(sys.argv[2])]
    n = (int(sys.argv[4]) if len(sys.argv) > 4 else 150) if cmd == "run" else (int(sys.argv[3]) if len(sys.argv) > 3 else 150)
    S = sample(rows, n)
    if cmd == "dry":
        print(f"would send {len(S)} passages; avg words {sum(len(r['text'].split()) for r in S)//len(S)}; tag coverage {dict(Counter(t for r in S for t in r['tags']))}")
        return
    key = os.environ.get("TYPESAFE_API_KEY") or sys.exit("TYPESAFE_API_KEY not set")
    done = {json.loads(l)["id"] for l in open(sys.argv[3])} if os.path.exists(sys.argv[3]) else set()
    with open(sys.argv[3], "a") as f:
        for i, r in enumerate(S):
            if r["id"] in done: continue
            res = call(key, r["text"])
            f.write(json.dumps({"id": r["id"], "note": r["note"], "tags": r["tags"], "model": res.get("model"),
                                "jev": {t: res["answers"][t]["noul"] for t in TAGS}}) + "\n"); f.flush()
            if i % 25 == 0: print(f"{i}/{len(S)}", flush=True)
    print("done", len(S))


if __name__ == "__main__":
    main()
