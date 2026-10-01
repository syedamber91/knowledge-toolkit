"""Train + evaluate MiniLM-embedding classifiers for the 12 SOIC concept tags, vs baselines.
Run: output/system_one_train/.venv/bin/python scripts/system_one_train/train_minilm.py"""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import OUT, TAGS, load_notes, split, y_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import GroupKFold

MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 256-token max seq -> chunk long notes
CHUNK_WORDS, MAX_CHUNKS = 180, 10


def embed(notes, model):
    out = []
    for n in notes:
        w = (n["title"] + ". " + n["text"]).split()
        chunks = [" ".join(w[i:i + CHUNK_WORDS]) for i in range(0, len(w), CHUNK_WORDS)][:MAX_CHUNKS]
        e = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)
        v = e.mean(0)
        out.append(v / np.linalg.norm(v))
    return np.array(out)


def ovr_fit(X, Y, C):
    ms = []
    for j in range(Y.shape[1]):
        m = LogisticRegression(C=C, class_weight="balanced", max_iter=2000)
        m.fit(X, Y[:, j]); ms.append(m)
    return ms


def ovr_proba(ms, X):
    return np.column_stack([m.predict_proba(X)[:, 1] for m in ms])


def oof(make_X, notes, Y, C, groups):
    """out-of-fold probs on train, used only to tune per-tag thresholds."""
    P = np.zeros(Y.shape)
    for tr, va in GroupKFold(5).split(notes, groups=groups):
        Xtr, Xva = make_X(tr, va)
        ms = ovr_fit(Xtr, Y[tr], C)
        P[va] = ovr_proba(ms, Xva)
    return P


def tune_thr(P, Y):
    grid = np.arange(0.1, 0.91, 0.05)
    return np.array([grid[int(np.argmax([f1_score(Y[:, j], P[:, j] >= g, zero_division=0) for g in grid]))]
                     for j in range(Y.shape[1])])


def metrics(P, Y, thr, name):
    pred = P >= thr
    aucs = [roc_auc_score(Y[:, j], P[:, j]) if 0 < Y[:, j].sum() < len(Y) else float("nan") for j in range(Y.shape[1])]
    top1 = float(np.mean([Y[i, int(np.argmax(P[i]))] == 1 for i in range(len(Y))]))
    return dict(model=name, micro_f1=round(f1_score(Y, pred, average="micro", zero_division=0), 3),
                macro_f1=round(f1_score(Y, pred, average="macro", zero_division=0), 3),
                mean_auc=round(float(np.nanmean(aucs)), 3), top1_hit=round(top1, 3),
                per_tag_f1={t: round(f1_score(Y[:, j], pred[:, j], zero_division=0), 2) for j, t in enumerate(TAGS)})


def main():
    from sentence_transformers import SentenceTransformer
    t0 = time.time()
    notes = load_notes(); train, test = split(notes)
    Ytr, Yte = y_matrix(train), y_matrix(test)
    groups = [n["topic"] for n in train]
    print(f"notes={len(notes)} train={len(train)} test={len(test)} (topic-grouped split)")
    cache = OUT / "emb.npz"
    if cache.exists() and json.loads((OUT / "emb.meta.json").read_text()) == [n["slug"] for n in notes]:
        z = np.load(cache); Etr, Ete = z["tr"], z["te"]
    else:
        st = SentenceTransformer(MODEL)
        Etr, Ete = embed(train, st), embed(test, st)
        np.savez(cache, tr=Etr, te=Ete); (OUT / "emb.meta.json").write_text(json.dumps([n["slug"] for n in notes]))
    print(f"embedded in {time.time()-t0:.0f}s")

    prior = Ytr.mean(0)
    Pprior = np.tile(prior, (len(test), 1))
    res = [metrics(Pprior, Yte, np.full(len(TAGS), 0.5), "prior-only (predict tag frequency)")]
    res[0]["top1_hit"] = round(float(np.mean([Yte[i, int(np.argmax(prior))] == 1 for i in range(len(test))])), 3)

    Ttr, Tte = [n["title"] + " " + n["text"] for n in train], [n["title"] + " " + n["text"] for n in test]
    best = {}
    for C in (1.0, 10.0):
        mk_e = lambda tr, va: (Etr[tr], Etr[va])
        Pe = oof(mk_e, train, Ytr, C, groups); thr = tune_thr(Pe, Ytr)
        f = np.mean([f1_score(Ytr, Pe >= thr, average="macro", zero_division=0)])
        if f > best.get("minilm", (0,))[0]: best["minilm"] = (f, C, thr)
        def mk_t(tr, va):
            v = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=40000)
            return v.fit_transform([Ttr[i] for i in tr]), v.transform([Ttr[i] for i in va])
        Pt = oof(mk_t, train, Ytr, C, groups); thr = tune_thr(Pt, Ytr)
        f = np.mean([f1_score(Ytr, Pt >= thr, average="macro", zero_division=0)])
        if f > best.get("tfidf", (0,))[0]: best["tfidf"] = (f, C, thr)
    print({k: (round(v[0], 3), v[1]) for k, v in best.items()}, "<- train CV macro-F1 / chosen C")

    _, Ce, thr_e = best["minilm"]; _, Ct, thr_t = best["tfidf"]
    me = ovr_fit(Etr, Ytr, Ce); Pe_te = ovr_proba(me, Ete)
    v = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=40000)
    mt = ovr_fit(v.fit_transform(Ttr), Ytr, Ct); Pt_te = ovr_proba(mt, v.transform(Tte))
    res.append(metrics(Pt_te, Yte, thr_t, "TF-IDF + LR"))
    res.append(metrics(Pe_te, Yte, thr_e, "MiniLM-L6 + LR"))
    res.append(metrics((Pt_te + Pe_te) / 2, Yte, (thr_t + thr_e) / 2, "avg(TF-IDF, MiniLM)"))
    (OUT / "minilm_results.json").write_text(json.dumps(dict(test_notes=len(test), train_notes=len(train), results=res), indent=1))
    import joblib; joblib.dump(dict(models=me, C=Ce, thr=thr_e, tags=TAGS), OUT / "minilm_tagger.joblib")
    print(f"\n{'model':38s} microF1 macroF1 AUC   top1")
    for r in res: print(f"{r['model']:38s} {r['micro_f1']:.3f}   {r['macro_f1']:.3f}   {r['mean_auc']:.3f} {r['top1_hit']:.3f}")


if __name__ == "__main__":
    main()
