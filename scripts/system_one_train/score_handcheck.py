"""Score the owner's blind hand-check against inherited labels and Jev (stdlib only).
  score_handcheck.py RESULTS.json [KEY.json] [JEV2.jsonl]
Passage strata were sampled on purpose (agree / disagree / none-low), so we report per stratum and a population-weighted overall
(weights = stratum sizes among the 836 classified of 905 test passages; the ~69 'middle' passages are in no stratum)."""
import json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
here = Path(__file__).resolve().parents[2] / "output/system_one_train"
res = json.load(open(sys.argv[1]))["answers"]
key = json.load(open(sys.argv[2] if len(sys.argv) > 2 else here / "handcheck/handcheck_key.json"))
jev = {r["id"]: r for r in map(json.loads, open(sys.argv[3] if len(sys.argv) > 3 else "/private/tmp/claude-501/fable/jev_labels2.jsonl"))}
TAGS = list(next(iter(jev.values()))["jev"].keys())

def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d
fmt = lambda k, n: f"{k}/{n} = {k/max(n,1):.2f} [{wilson(k, n)[0]:.2f}-{wilson(k, n)[1]:.2f}]"

rows = []
for pid, meta in key["passages"].items():
    a = res.get(pid) or {}
    if not a.get("primary"): continue
    h = a["primary"]; h2 = a.get("second") or ""
    ch = jev[meta["real_id"]]["choice"]; top = max(TAGS, key=lambda t: ch[t])
    rows.append(dict(stratum=meta["stratum"], cant=h == "cant_tell", human={h, h2} - {"", "cant_tell"}, prim=h,
                     inh=set(meta["inherited"]), jev=top))
print(f"passages answered: {len(rows)}/80")
W = key["strata_sizes"]; per = defaultdict(list)
for r in rows: per[r["stratum"]].append(r)
def stat(name, f, only_tellable=True):
    print(f"\n{name}")
    tot = wsum = 0
    for s in ("agree", "disagree", "nonelow"):
        rs = [r for r in per[s] if (not r["cant"] or not only_tellable)]
        k = sum(1 for r in rs if f(r)); print(f"  {s:9s} {fmt(k, len(rs))}")
        if rs: tot += W[s] * k / len(rs); wsum += W[s]
    print(f"  weighted overall (point estimate only): {tot / max(wsum, 1):.2f}")
allr = rows
print(f"\n'Can't tell' rate (hard-fragment rate): " + ", ".join(f"{s} {fmt(sum(r['cant'] for r in per[s]), len(per[s]))}" for s in ('agree', 'disagree', 'nonelow')))
print(f"  overall (unweighted): {fmt(sum(r['cant'] for r in allr), len(allr))}")
stat("A. Label noise: human primary topic is in the INHERITED tags (excludes can't-tell)", lambda r: r["prim"] in r["inh"])
stat("B. Jev choice top-1 equals the human primary topic", lambda r: r["jev"] == r["prim"])
stat("B2. Jev choice top-1 is in the human's topics (primary or second)", lambda r: r["jev"] in r["human"])
stat("C. For reference: Jev top-1 is in the INHERITED tags (same passages)", lambda r: r["jev"] in r["inh"])
print("\nHow to read: A low => the inherited labels are noisy for passages. B well above C => Jev is closer to the truth than the labels say.")
print("'Can't tell' high => the fragments themselves are too short/ambiguous. n per stratum is small: +-0.15-0.20; this separates 0.6 from 0.9, not finer.")

nrows = []
for nid, meta in key["notes"].items():
    a = res.get(nid) or {}
    if not a.get("tags"): continue
    H = set(a["tags"]); I = set(meta["inherited"])
    ps = [r for r in jev.values() if r["note"] == meta["slug"]]
    mean = {t: sum(r["choice"][t] for r in ps) / len(ps) for t in TAGS} if ps else {}
    nrows.append((H, I, max(mean, key=mean.get) if mean else None))
print(f"\nnotes answered: {len(nrows)}/20")
if nrows:
    exact = sum(H == I for H, I, _ in nrows); inh_in_h = sum(len(H & I) for H, I, _ in nrows) / max(sum(len(I) for _, I, _ in nrows), 1)
    h_in_i = sum(len(H & I) for H, I, _ in nrows) / max(sum(len(H) for H, _, _ in nrows), 1)
    print(f"  human tags == inherited tags exactly: {fmt(exact, len(nrows))}")
    print(f"  share of inherited tags the human also picked: {inh_in_h:.2f} | share of human tags that were inherited: {h_in_i:.2f}")
    print(f"  Jev mean-over-passages top-1 in human tags: {fmt(sum(j in H for H, _, j in nrows), len(nrows))} | in inherited tags: {fmt(sum(j in I for _, I, j in nrows), len(nrows))}")
