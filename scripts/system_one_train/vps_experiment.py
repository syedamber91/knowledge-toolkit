"""Run ON THE VPS (CPU). Does transcript-passage training help MiniLM/TF-IDF? Same 114 held-out test notes as before.
  python vps_experiment.py NOTES.jsonl PASSAGES.jsonl MINILM_DIR OUT_DIR
Arms: A notes only (repro) | B passages only | C notes + passages.  Passages come from train-split modules only."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS
from minilm_core import embed_text
from train_minilm import metrics, ovr_fit, ovr_proba, oof, tune_thr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score
from sentence_transformers import SentenceTransformer

notes_p, pass_p, minilm_dir, out_dir = sys.argv[1:5]
out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
rd = lambda p: [json.loads(l) for l in open(p)]
N, P = rd(notes_p), rd(pass_p)
tr, te = [n for n in N if n["split"] == "train"], [n for n in N if n["split"] == "test"]
assert not ({p["topic"] for p in P} & {n["topic"] for n in te}), "LEAK: passages from a test module"
Y = lambda rows: np.array([[int(t in r["tags"]) for t in TAGS] for r in rows])
st = SentenceTransformer(minilm_dir, device="cpu"); t0 = time.time()
Etr = np.array([embed_text(st, n["title"], n["text"]) for n in tr]); Ete = np.array([embed_text(st, n["title"], n["text"]) for n in te])
Ep = st.encode([p["text"] for p in P], normalize_embeddings=True, batch_size=32, show_progress_bar=False)
print(f"embedded in {time.time()-t0:.0f}s", flush=True)
txt = lambda rows: [(r.get("title", "") + " " + r["text"]) for r in rows]
arms = {"A notes only": (Etr, txt(tr), Y(tr), [n["topic"] for n in tr]),
        "B passages only": (Ep, txt(P), Y(P), [p["topic"] for p in P]),
        "C notes + passages": (np.vstack([Etr, Ep]), txt(tr) + txt(P), np.vstack([Y(tr), Y(P)]), [n["topic"] for n in tr] + [p["topic"] for p in P])}
Yte, Tte = Y(te), txt(te); res = []
for name, (E, T, Ya, G) in arms.items():
    best = {}
    for C in (1.0, 10.0):
        Pe = oof(lambda a, b: (E[a], E[b]), G, Ya, C, G); thr = tune_thr(Pe, Ya)
        f = f1_score(Ya, Pe >= thr, average="macro", zero_division=0)
        if f > best.get("m", (0,))[0]: best["m"] = (f, C, thr)
        def mk(a, b):
            v = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=40000)
            return v.fit_transform([T[i] for i in a]), v.transform([T[i] for i in b])
        Pt = oof(mk, G, Ya, C, G); thr = tune_thr(Pt, Ya)
        f = f1_score(Ya, Pt >= thr, average="macro", zero_division=0)
        if f > best.get("t", (0,))[0]: best["t"] = (f, C, thr)
    me = ovr_fit(E, Ya, best["m"][1]); pe = ovr_proba(me, Ete)
    v = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=40000)
    mt = ovr_fit(v.fit_transform(T), Ya, best["t"][1]); pt = ovr_proba(mt, v.transform(Tte))
    for lab, p, th in (("MiniLM+LR", pe, best["m"][2]), ("TF-IDF+LR", pt, best["t"][2]), ("avg", (pe + pt) / 2, (best["m"][2] + best["t"][2]) / 2)):
        r = metrics(p, Yte, th, f"{name} | {lab}"); res.append(r)
        print(f"{r['model']:34s} microF1 {r['micro_f1']:.3f} macroF1 {r['macro_f1']:.3f} AUC {r['mean_auc']:.3f} top1 {r['top1_hit']:.3f}", flush=True)
(out / "vps_experiment_results.json").write_text(json.dumps({"train_notes": len(tr), "passages": len(P), "test_notes": len(te), "results": res}, indent=1))
