"""Test my guess for why transcript passages did not help: (1) domain shift spoken vs written, (2) noisy inherited labels.
Training sets (all from TRAIN modules only):  A written notes (full) | D written notes cut into ~150-word chunks, same inherited
labels | B spoken passages | F spoken passages kept only if a notes-trained model agrees with the inherited label.
Eval sets (TEST modules): full test notes | test notes as chunks, averaged | test spoken passages (diagnostics only).
Fixed hyper-parameters, no tuning, so arms are comparable.  Metrics: top-1 hit and mean AUC.
  diagnose.py NOTES TRAIN_PASSAGES TEST_PASSAGES MINILM_DIR OUT_DIR"""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS
from minilm_core import embed_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sentence_transformers import SentenceTransformer

notes_p, trp_p, tep_p, mdir, out = sys.argv[1:6]
rd = lambda p: [json.loads(l) for l in open(p)]
N, TRP, TEP = rd(notes_p), rd(trp_p), rd(tep_p)
tr, te = [n for n in N if n["split"] == "train"], [n for n in N if n["split"] == "test"]
assert not ({p["topic"] for p in TRP} & {n["topic"] for n in te}), "LEAK"
Y = lambda rows: np.array([[int(t in r["tags"]) for t in TAGS] for r in rows])
chunk = lambda text, n=150: [" ".join(text.split()[i:i + n]) for i in range(0, len(text.split()), n)][:6] or ["empty"]
st = SentenceTransformer(mdir, device="cpu"); t0 = time.time()
enc = lambda texts: st.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
# training sets
D = [{"tags": n["tags"], "text": c, "note": n["slug"]} for n in tr for c in chunk(n["text"])]
ctexts = lambda rows: [r["text"] for r in rows]
feat = {"A": (tr, [embed_text(st, n["title"], n["text"]) for n in tr]), "D": (D, enc(ctexts(D))), "B": (TRP, enc(ctexts(TRP)))}
print(f"embedded train sets {time.time()-t0:.0f}s", flush=True)
# eval sets
te_full_txt = [n["title"] + " " + n["text"] for n in te]; te_full_emb = np.array([embed_text(st, n["title"], n["text"]) for n in te])
TC = [(i, c) for i, n in enumerate(te) for c in chunk(n["text"])]; tc_emb = enc([c for _, c in TC])
tp_emb = enc(ctexts(TEP)); print(f"embedded all {time.time()-t0:.0f}s", flush=True)
Yte, Ytp = Y(te), Y(TEP)

def fit(kind, rows, X):
    Ya = Y(rows)
    if kind == "tfidf":
        v = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=40000); M = v.fit_transform(ctexts(rows))
        ms = [LogisticRegression(C=10.0, class_weight="balanced", max_iter=2000).fit(M, Ya[:, j]) for j in range(len(TAGS))]
        return lambda texts, emb: np.column_stack([m.predict_proba(v.transform(texts))[:, 1] for m in ms])
    ms = [LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(np.asarray(X), Ya[:, j]) for j in range(len(TAGS))]
    return lambda texts, emb: np.column_stack([m.predict_proba(np.asarray(emb))[:, 1] for m in ms])

def top1(P, Yt): return float(np.mean([Yt[i, int(np.argmax(P[i]))] == 1 for i in range(len(Yt))]))
def auc(P, Yt): return float(np.mean([roc_auc_score(Yt[:, j], P[:, j]) for j in range(Yt.shape[1]) if 0 < Yt[:, j].sum() < len(Yt)]))
def note_rows(model):  # full-note path, and chunk-average path
    full = model([n["title"] + " " + n["text"] for n in te], te_full_emb)
    pc = model([c for _, c in TC], tc_emb); idx = np.array([i for i, _ in TC])
    avg = np.vstack([pc[idx == i].mean(0) for i in range(len(te))])
    return full, avg

rows_out = []
for kind in ("tfidf", "minilm"):
    models = {k: fit(kind, *feat[k]) for k in ("A", "D", "B")}
    # F: keep passages whose inherited tags include the notes-trained model's top-1 guess
    pa = models["A"]([r["text"] for r in TRP], feat["B"][1]); keep = [i for i in range(len(TRP)) if TRP[i]["tags"] and TRP[i]["tags"][0] is not None and Y(TRP)[i, int(np.argmax(pa[i]))] == 1]
    Fr = [TRP[i] for i in keep]; models["F"] = fit(kind, Fr, feat["B"][1][keep]); print(f"[{kind}] F keeps {len(keep)}/{len(TRP)} passages", flush=True)
    for k in ("A", "D", "B", "F"):
        full, avg = note_rows(models[k]); pp = models[k]([r["text"] for r in TEP], tp_emb)
        r = dict(family=kind, train=k, n_train=len(Fr) if k == "F" else len(feat[k][0]),
                 notes_full=(top1(full, Yte), auc(full, Yte)), notes_chunks=(top1(avg, Yte), auc(avg, Yte)), test_passages=(top1(pp, Ytp), auc(pp, Ytp)))
        rows_out.append(r)
        print(f"{kind:7s} train={k} n={r['n_train']:5d} | notes(full) top1 {r['notes_full'][0]:.3f} auc {r['notes_full'][1]:.3f} | notes(chunks) top1 {r['notes_chunks'][0]:.3f} auc {r['notes_chunks'][1]:.3f} | spoken test passages top1 {r['test_passages'][0]:.3f} auc {r['test_passages'][1]:.3f}", flush=True)
Path(out).mkdir(parents=True, exist_ok=True); (Path(out) / "diagnose_results.json").write_text(json.dumps(rows_out, indent=1))
