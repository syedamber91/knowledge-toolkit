"""MiniLM semantic finder over knowledge/system-one (no training: embeddings only).
  build + self-test:  vault_finder.py eval
  query:              vault_finder.py query "which model for 77 classes" -k 5
Shortlist helper for the Opus advisor; it ranks notes, it does not answer."""
import argparse, json, sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import OUT

VAULT = Path(__file__).resolve().parents[2] / "knowledge" / "system-one"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_WORDS = 160

# Hand-written probes: (query, acceptable slugs). Hit@3 = any acceptable slug in top 3.
PROBES = [
    ("which model for 77 classes with a few thousand labelled examples", {"minilm-embeddings", "when-to-use-which-model", "benchmarks-and-comparisons"}),
    ("run Jev in a cloud session behind the egress proxy", {"jev-mcp-server", "agent-operating-protocol"}),
    ("confidence threshold that sends an item to human review", {"confidence-gated-routing", "confidence", "cb-consistency-nouls", "cb-consistency-choices"}),
    ("known weaknesses of jev 1.13", {"jev-1-13-jaggedness", "anti-patterns"}),
    ("how much cheaper is batching many questions in one call", {"cb-parallel-questions", "speculative-fan-out"}),
    ("rerank BM25 candidates with typed questions", {"cb-reranking"}),
    ("screen messages for hazard and prompt injection", {"cb-llm-guardrails"}),
    ("laya accuracy before and after fine-tuning", {"laya", "jev-vs-laya"}),
    ("extract absolute and relative dates from a document", {"cb-date-extraction"}),
    ("how to word the levels of a score question", {"score", "question-design-checklist"}),
    ("what data must never be sent to a hosted api", {"privacy-and-cost-gates"}),
    ("who reads and who synthesizes sonnet or opus", {"model-tiering-sonnet-opus", "agent-operating-protocol"}),
    ("check whether a quoted citation is supported by the source", {"cb-citation-check"}),
    ("hierarchical classification with beam search over probabilities", {"cb-hierarchical-classification"}),
    ("python sdk retry policy and exceptions", {"sdk-python-retries-and-exceptions", "sdk-python-usage"}),
    ("pick one skill for an agent turn from a large catalog", {"cb-skill-suggestion"}),
    ("yes no probability noul question", {"noul"}),
    ("route requests to deterministic code, a specialist model or a human", {"intent-routing", "confidence-gated-routing"}),
]


def docs():
    out = []
    for p in sorted(VAULT.rglob("*.md")):
        if p.stem in ("Home", "Log") or p.parent.name == "topics":
            continue
        t = p.read_text().split("\n---\n", 1)[-1]
        out.append((p.stem, t))
    return out


def chunks(slug, text):
    w = (slug.replace("-", " ") + ". " + text).split()
    return [" ".join(w[i:i + CHUNK_WORDS]) for i in range(0, len(w), CHUNK_WORDS)][:40]


def build():
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer(MODEL)
    slugs, vecs = [], []
    for slug, t in docs():
        c = chunks(slug, t)
        e = st.encode(c, normalize_embeddings=True, show_progress_bar=False)
        for v in e: slugs.append(slug); vecs.append(v)
    np.savez(OUT / "vault_index.npz", vecs=np.array(vecs)); (OUT / "vault_index.json").write_text(json.dumps(slugs))
    return st, np.array(vecs), slugs


def load():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL), np.load(OUT / "vault_index.npz")["vecs"], json.loads((OUT / "vault_index.json").read_text())


def rank(st, V, slugs, q, k=5):
    s = V @ st.encode([q], normalize_embeddings=True)[0]
    best = {}
    for sl, x in zip(slugs, s): best[sl] = max(best.get(sl, -1), float(x))
    return sorted(best.items(), key=lambda kv: -kv[1])[:k]


def tfidf_rank(q, k=5):
    from sklearn.feature_extraction.text import TfidfVectorizer
    d = docs(); v = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), stop_words="english")
    M = v.fit_transform([s.replace("-", " ") + " " + t for s, t in d]); s = (M @ v.transform([q]).T).toarray().ravel()
    return [(d[i][0], float(s[i])) for i in np.argsort(-s)[:k]]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["eval", "query", "build"]); ap.add_argument("text", nargs="?"); ap.add_argument("-k", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "build": build(); print("built"); return
    st, V, slugs = build() if a.cmd == "eval" else load()
    if a.cmd == "query":
        for sl, sc in rank(st, V, slugs, a.text, a.k): print(f"{sc:.3f}  {sl}")
        return
    def score(fn):
        h = mrr = 0
        for q, ok in PROBES:
            r = [s for s, _ in fn(q)]
            h += any(x in ok for x in r[:3]); mrr += next((1 / (i + 1) for i, x in enumerate(r) if x in ok), 0)
        return round(h / len(PROBES), 3), round(mrr / len(PROBES), 3)
    print(f"probes={len(PROBES)}  notes={len(set(slugs))}  chunks={len(slugs)}")
    print("MiniLM  hit@3, MRR:", score(lambda q: rank(st, V, slugs, q, 10)))
    print("TF-IDF  hit@3, MRR:", score(lambda q: tfidf_rank(q, 10)))
    for q, ok in PROBES:
        top = [s for s, _ in rank(st, V, slugs, q, 3)]
        if not any(x in ok for x in top): print("  MISS:", q, "->", top)


if __name__ == "__main__":
    main()
