"""Analyze Jev run #2 (Fable's ideas 2, 5, 6 + 7-as-measurement) on all spoken TEST passages. Run on the VPS (CPU, niced).
  jev_analysis.py JEV2.jsonl NOTES.jsonl TRAIN_PASSAGES.jsonl MINILM_DIR
Paired bootstrap resamples NOTES (passages of one note are not independent), B=1000. Differences whose 95% CI spans 0 are noise."""
import json, sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS
from minilm_core import embed_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score
from scipy.stats import rankdata

jev_p, notes_p, trp_p, mdir = sys.argv[1:5]
rd = lambda p: [json.loads(l) for l in open(p)]
R, N, TRP = rd(jev_p), rd(notes_p), rd(trp_p)
test_passages = {json.loads(l)["id"]: json.loads(l) for l in open("/root/system-one-train/data/test_passages.jsonl")}
R = [r for r in R if r["id"] in test_passages]
nid = {n["slug"]: n for n in N}; tr = [n for n in N if n["split"] == "train"]
Y = np.array([[int(t in r["tags"]) for t in TAGS] for r in R]); notes = np.array([r["note"] for r in R])
Pn = np.array([[r["jev"][t] for t in TAGS] for r in R]); Pc = np.array([[r["choice"][t] for t in TAGS] for r in R]); none = np.array([r["choice"]["none"] for r in R])
rng = np.random.default_rng(0); un = np.unique(notes); idx_by = {n: np.where(notes == n)[0] for n in un}

def top1(P, Yt): return float(np.mean([Yt[i, int(np.argmax(P[i]))] == 1 for i in range(len(Yt))]))
def auc(P, Yt):
    a = [roc_auc_score(Yt[:, j], P[:, j]) for j in range(Yt.shape[1]) if 0 < Yt[:, j].sum() < len(Yt)]
    return float(np.mean(a))
def rk(P): return np.column_stack([rankdata(P[:, j]) / len(P) for j in range(P.shape[1])])
def boot(fn, B=1000):
    """paired bootstrap over notes: fn(sample_idx)->float ; returns (mean, lo, hi)"""
    v = []
    for _ in range(B):
        s = np.concatenate([idx_by[n] for n in rng.choice(un, len(un))]); 
        try: v.append(fn(s))
        except ValueError: pass
    return float(np.mean(v)), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
fmt = lambda t: f"{t[0]:+.3f} [{t[1]:+.3f},{t[2]:+.3f}]"
print(f"passages={len(R)} notes={len(un)} model={R[0]['model']}  none-prob mean {none.mean():.3f}  choice picks 'none' as argmax: {float(np.mean([max(r['choice'], key=r['choice'].get) == 'none' for r in R])):.3f}")

# ---- baseline + idea 5 (choice vs noul), passage level
print("\n[passage level vs inherited labels]")
print(f"Jev 12 noul     top1 {top1(Pn, Y):.3f}  AUC {auc(Pn, Y):.3f}")
print(f"Jev choice(12)  top1 {top1(Pc, Y):.3f}  AUC {auc(Pc, Y):.3f}")
d = boot(lambda s: top1(Pc[s], Y[s]) - top1(Pn[s], Y[s])); print("idea5 choice - noul top1 diff", fmt(d))
d = boot(lambda s: auc(Pc[s], Y[s]) - auc(Pn[s], Y[s])); print("idea5 choice - noul AUC  diff", fmt(d))

# ---- reference + ensemble models trained on TRAIN data only (idea 6)
txt = lambda rows: [(r.get("title", "") + " " + r["text"]) for r in rows]
Ytr_p = np.array([[int(t in r["tags"]) for t in TAGS] for r in TRP]); Ytr_n = np.array([[int(t in n["tags"]) for t in TAGS] for n in tr])
Tp = [test_passages[r["id"]]["text"] for r in R]
def tfidf_fit(T, Yt):
    v = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=40000); M = v.fit_transform(T)
    ms = [LogisticRegression(C=10.0, class_weight="balanced", max_iter=2000).fit(M, Yt[:, j]) for j in range(len(TAGS))]
    return lambda X: np.column_stack([m.predict_proba(v.transform(X))[:, 1] for m in ms])
Pb = tfidf_fit(txt(TRP), Ytr_p)(Tp)                       # TF-IDF trained on spoken train passages
from sentence_transformers import SentenceTransformer
st = SentenceTransformer(mdir, device="cpu")
Etr = np.array([embed_text(st, n["title"], n["text"]) for n in tr]); Ete = st.encode(Tp, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
ms = [LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(Etr, Ytr_n[:, j]) for j in range(len(TAGS))]
Pm = np.column_stack([m.predict_proba(Ete)[:, 1] for m in ms])   # MiniLM trained on written train notes
for name, P in (("TF-IDF (spoken-trained)", Pb), ("MiniLM (note-trained)", Pm)): print(f"{name:26s} top1 {top1(P, Y):.3f}  AUC {auc(P, Y):.3f}")
E1, E2 = (rk(Pn) + rk(Pb)) / 2, (rk(Pn) + rk(Pb) + rk(Pm)) / 3
for name, P in (("rank-avg Jev+TF-IDF", E1), ("rank-avg Jev+TF-IDF+MiniLM", E2)):
    best = max((Pn, Pb, Pm), key=lambda Q: auc(Q, Y))
    dA = boot(lambda s: auc(P[s], Y[s]) - max(auc(Pn[s], Y[s]), auc(Pb[s], Y[s]), auc(Pm[s], Y[s])))
    print(f"idea6 {name:28s} top1 {top1(P, Y):.3f} AUC {auc(P, Y):.3f} | AUC minus best single: {fmt(dA)}")

# ---- idea 2: note level (the only clean target)
def agg(P, how):
    out = []
    for n in un:
        Q = P[idx_by[n]]
        out.append(Q.mean(0) if how == "mean" else Q.max(0) if how == "max" else 1 - np.prod(1 - np.clip(Q, 0, 1), axis=0))
    return np.array(out)
Yn = np.array([[int(t in nid[n]["tags"]) for t in TAGS] for n in un])
tn = tfidf_fit([n["title"] + " " + n["text"] for n in tr], Ytr_n)([nid[n]["title"] + " " + nid[n]["text"] for n in un])
print(f"\n[note level vs the NOTE's own tags, {len(un)} notes with passages]")
print(f"reference: TF-IDF trained on written notes, applied to the note text: top1 {top1(tn, Yn):.3f} AUC {auc(tn, Yn):.3f}")
for src, P in (("Jev noul", Pn), ("Jev choice", Pc), ("rank-avg Jev+TF-IDF", E1)):
    for how in ("mean", "max", "noisyOR"):
        A = agg(P, how); print(f"{src:20s} {how:8s} top1 {top1(A, Yn):.3f}  AUC {auc(A, Yn):.3f}")
# ---- idea 7 as MEASUREMENT only: per-tag thresholds tuned on half the notes, scored on the other half
def f1s(P, Yt, thr): return f1_score(Yt, P >= thr, average="micro", zero_division=0)
An = agg(Pn, "mean"); base, tuned = [], []
for _ in range(30):
    perm = rng.permutation(len(un)); a, b = perm[: len(un) // 2], perm[len(un) // 2:]
    grid = np.arange(0.05, 0.95, 0.05)
    thr = np.array([grid[int(np.argmax([f1_score(Yn[a, j], An[a, j] >= g, zero_division=0) for g in grid]))] for j in range(len(TAGS))])
    base.append(f1s(An[b], Yn[b], 0.5)); tuned.append(f1s(An[b], Yn[b], thr))
print(f"\nidea7 (measurement only, AUC unchanged by definition) note-level micro-F1: @0.5 {np.mean(base):.3f}  vs per-tag tuned on other half {np.mean(tuned):.3f}")
