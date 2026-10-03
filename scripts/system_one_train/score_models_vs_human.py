"""Score every model against the OWNER'S hand-check labels (80 passages, 20 notes). Run on the VPS.
  stage 1:  score_models_vs_human.py predict-light  HUMAN_MAP JEV2 NOTES TRAIN_PASSAGES TEST_PASSAGES MINILM_DIR OUT_DIR
  stage 2:  score_models_vs_human.py predict-laya   HUMAN_MAP JEV2 NOTES TRAIN_PASSAGES TEST_PASSAGES MINILM_DIR OUT_DIR  name=path [name=path ...]
  report:   score_models_vs_human.py report         HUMAN_MAP OUT_DIR
Metric: model top-1 tag == human primary, and top-1 in human {primary, second}; "can't tell" passages excluded. Passage strata were sampled on purpose,
so the overall figure is population-weighted by stratum size (agree/disagree/nonelow among the 836 classified passages) with a stratified bootstrap CI.
These 100 labels are for JUDGING only: nothing is tuned on them."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS

cmd = sys.argv[1]
rd = lambda p: [json.loads(l) for l in open(p)]
HM = json.load(open(sys.argv[2])); OUT = Path(sys.argv[-1] if cmd == "report" else sys.argv[8]); OUT.mkdir(parents=True, exist_ok=True)
P, Nn = HM["passages"], HM["notes"]
tell = [pid for pid, v in P.items() if v["primary"] != "cant_tell"]

if cmd.startswith("predict"):
    jev = {r["id"]: r for r in rd(sys.argv[3])}; N = {n["slug"]: n for n in rd(sys.argv[4])}
    TRP = rd(sys.argv[5]); TEP = {r["id"]: r for r in rd(sys.argv[6])}; mdir = sys.argv[7]
    ptxt = {pid: TEP[P[pid]["real_id"]]["text"] for pid in tell}
    ntxt = {nid: N[v["slug"]]["title"] + " " + N[v["slug"]]["text"] for nid, v in Nn.items()}
    top = lambda M, ids: {i: TAGS[int(np.argmax(M[k]))] for k, i in enumerate(ids)}
    preds = {}
    if cmd == "predict-light":
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sentence_transformers import SentenceTransformer
        from minilm_core import embed_text
        tr = [n for n in N.values() if n["split"] == "train"]
        Y = lambda rows: np.array([[int(t in r["tags"]) for t in TAGS] for r in rows])
        # Jev (no model fitting): noul, choice(12 tags), choice with "none" counted as a miss
        pj = {"Jev noul(12)": {}, "Jev choice": {}, "Jev choice (none=miss)": {}}
        for pid in tell:
            r = jev[P[pid]["real_id"]]
            pj["Jev noul(12)"][pid] = max(TAGS, key=lambda t: r["jev"][t])
            pj["Jev choice"][pid] = max(TAGS, key=lambda t: r["choice"][t])
            pj["Jev choice (none=miss)"][pid] = "none" if max(r["choice"], key=r["choice"].get) == "none" else pj["Jev choice"][pid]
        npj = {"Jev noul(12)": {}, "Jev choice": {}}
        for nid, v in Nn.items():
            rs = [r for r in jev.values() if r["note"] == v["slug"]]
            npj["Jev noul(12)"][nid] = max(TAGS, key=lambda t: np.mean([r["jev"][t] for r in rs]))
            npj["Jev choice"][nid] = max(TAGS, key=lambda t: np.mean([r["choice"][t] for r in rs]))
        for k in pj: preds[k] = {"passages": pj[k], "notes": npj.get(k, {})}
        def fit_tfidf(rows):
            v = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=40000); M = v.fit_transform([r.get("title", "") + " " + r["text"] for r in rows]); Ya = Y(rows)
            ms = [LogisticRegression(C=10.0, class_weight="balanced", max_iter=2000).fit(M, Ya[:, j]) for j in range(len(TAGS))]
            return lambda T: np.column_stack([m.predict_proba(v.transform(T))[:, 1] for m in ms])
        pids, nids = list(ptxt), list(ntxt)
        for name, rows in (("TF-IDF (trained on spoken)", TRP), ("TF-IDF (trained on written notes)", tr)):
            f = fit_tfidf(rows); preds[name] = {"passages": top(f([ptxt[i] for i in pids]), pids), "notes": top(f([ntxt[i] for i in nids]), nids)}
        st = SentenceTransformer(mdir, device="cpu"); enc = lambda T: st.encode(T, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
        def fit_lr(E, rows):
            Ya = Y(rows); ms = [LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(E, Ya[:, j]) for j in range(len(TAGS))]
            return lambda X: np.column_stack([m.predict_proba(X)[:, 1] for m in ms])
        Epass = enc([ptxt[i] for i in pids]); Enote = np.array([embed_text(st, N[Nn[i]["slug"]]["title"], N[Nn[i]["slug"]]["text"]) for i in nids])
        f = fit_lr(np.array([embed_text(st, n["title"], n["text"]) for n in tr]), tr); preds["MiniLM (trained on written notes)"] = {"passages": top(f(Epass), pids), "notes": top(f(Enote), nids)}
        f = fit_lr(enc([r["text"] for r in TRP]), TRP); preds["MiniLM (trained on spoken)"] = {"passages": top(f(Epass), pids), "notes": top(f(Enote), nids)}
    else:
        from laya import Agent
        from laya_data import question as nq
        from laya_choice_data import QID, QUESTION
        noul = {t: nq(t) for t in TAGS}; chunk = lambda s, n=150: [" ".join(s.split()[k:k + n]) for k in range(0, len(s.split()), n)][:6] or ["empty"]
        for spec in sys.argv[9:-0 or None]:
            if "=" not in spec: continue
            name, path = spec.split("=", 1); ag = Agent(path, device="cpu"); t0 = time.time()
            pn, pc, nn, nc = {}, {}, {}, {}
            for pid in tell:
                a = ag.predict({"passage": ptxt[pid]}, noul)["answers"]; pn[pid] = max(TAGS, key=lambda t: a[t]["noul"])
                c = ag.predict({"passage": ptxt[pid]}, {QID: QUESTION})["answers"][QID]["probabilities"]; pc[pid] = max(TAGS, key=lambda t: c[t])
            for nid in Nn:
                cs = chunk(ntxt[nid]); sums = {t: 0.0 for t in TAGS}; sn = {t: 0.0 for t in TAGS}
                for ch in cs:
                    c = ag.predict({"passage": ch}, {QID: QUESTION})["answers"][QID]["probabilities"]
                    for t in TAGS: sums[t] += c[t]
                    a = ag.predict({"passage": ch}, noul)["answers"]
                    for t in TAGS: sn[t] += a[t]["noul"]
                nc[nid] = max(TAGS, key=sums.get); nn[nid] = max(TAGS, key=sn.get)
            preds[f"{name} noul(12)"] = {"passages": pn, "notes": nn}; preds[f"{name} choice"] = {"passages": pc, "notes": nc}
            print(name, f"{time.time()-t0:.0f}s", flush=True); del ag
    (OUT / f"preds_{cmd.split('-')[1]}.json").write_text(json.dumps(preds)); print("saved", list(preds)); sys.exit()

# ---------------- report
preds = {}
for f in sorted(OUT.glob("preds_*.json")): preds.update(json.load(open(f)))
W = HM["strata_sizes"]; S = ("agree", "disagree", "nonelow"); rng = np.random.default_rng(0)
by = {s: [pid for pid in tell if P[pid]["stratum"] == s] for s in S}
def rate(hits, which):
    ps = [np.mean([hits(pid) for pid in by[s]]) if by[s] else 0 for s in S]
    return sum(W[s] * p for s, p in zip(S, ps)) / sum(W[s] for s in S), ps
def ci(hits):
    v = []
    for _ in range(2000):
        ps = [np.mean([hits(pid) for pid in rng.choice(by[s], len(by[s]))]) for s in S]; v.append(sum(W[s] * p for s, p in zip(S, ps)) / sum(W[s] for s in S))
    return np.percentile(v, 2.5), np.percentile(v, 97.5)
rows = []
for name, pr in preds.items():
    h1 = lambda pid, pr=pr: float(pr["passages"].get(pid) == P[pid]["primary"]); h2 = lambda pid, pr=pr: float(pr["passages"].get(pid) in (P[pid]["primary"], P[pid]["second"]))
    w1, ps = rate(h1, 1); w2, _ = rate(h2, 2); lo, hi = ci(h1)
    nh = [pr["notes"][n] in Nn[n]["human"] for n in Nn if n in pr["notes"]]
    rows.append((name, w1, lo, hi, w2, ps, (sum(nh), len(nh))))
rows.sort(key=lambda r: -r[1])
print(f"tellable passages scored: {len(tell)}/80 (can't-tell excluded)\n")
print(f"{'model':36s} {'top1==human primary (weighted, 95% CI)':40s} {'in human {1st,2nd}':>18s}  per-stratum agree/disagree/nonelow   notes: top1 in human tags")
for n, w1, lo, hi, w2, ps, (k, m) in rows:
    print(f"{n:36s} {w1:5.2f} [{lo:4.2f}-{hi:4.2f}]{'':22s} {w2:12.2f}      {ps[0]:.2f} / {ps[1]:.2f} / {ps[2]:.2f}        {k}/{m}" if m else f"{n:36s} {w1:5.2f} [{lo:4.2f}-{hi:4.2f}]{'':22s} {w2:12.2f}      {ps[0]:.2f} / {ps[1]:.2f} / {ps[2]:.2f}        n/a")
inh = lambda pid: float(P[pid]["primary"] in P[pid]["inherited"]); w, ps = rate(inh, 0); lo, hi = ci(inh)
print(f"\nreference: inherited tag SET contains the human primary (lenient: 1-3 tags): {w:.2f} [{lo:.2f}-{hi:.2f}]  per-stratum {ps[0]:.2f}/{ps[1]:.2f}/{ps[2]:.2f}")
from collections import Counter
mc = Counter(P[p]["primary"] for p in tell).most_common(1)[0]; c1 = lambda pid: float(P[pid]["primary"] == mc[0]); print(f"reference: always guess '{mc[0]}' (the commonest human primary): {rate(c1, 0)[0]:.2f}; uniform random 12 tags: {1/12:.2f}")
print("notes reference (20 notes): inherited tags that overlap the human's: " + f"{sum(len(set(v['human']) & set(v['inherited'])) for v in Nn.values())/sum(len(v['inherited']) for v in Nn.values()):.2f}")
