"""Tiny HTTP service for the VPS (stdlib server, CPU only). Loads models once.
  GET  /health
  POST /tag   {"title": "...", "text": "...", "laya": false}  -> SOIC concept-tag probabilities
  POST /find  {"query": "...", "k": 5}                         -> top System One vault notes
Binds 127.0.0.1 by default. To expose, set SYSTEM_ONE_HOST and SYSTEM_ONE_TOKEN (Bearer auth required).
Layout (relative to this file's dir): models/minilm (sentence-transformers dir), models/tagger_final.joblib,
models/vault_index.npz + vault_index.json, optional Laya checkpoint: $LAYA_DIR, else models/laya/."""
import json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import joblib
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from minilm_core import embed_text  # noqa: E402

M = HERE / "models"
HOST, PORT = os.environ.get("SYSTEM_ONE_HOST", "127.0.0.1"), int(os.environ.get("SYSTEM_ONE_PORT", "8765"))
TOKEN = os.environ.get("SYSTEM_ONE_TOKEN")
if HOST not in ("127.0.0.1", "localhost") and not TOKEN:
    sys.exit("refusing to bind a non-local address without SYSTEM_ONE_TOKEN")

from sentence_transformers import SentenceTransformer  # noqa: E402
ST = SentenceTransformer(str(M / "minilm"), device="cpu")
TAG = joblib.load(M / "tagger_final.joblib")
VEC = np.load(M / "vault_index.npz")["vecs"]
SLUGS = json.loads((M / "vault_index.json").read_text())
LAYA = None
LAYA_PATH = Path(os.environ.get("LAYA_DIR", M / "laya"))   # set LAYA_DIR to load the checkpoint from anywhere (one copy only)
if LAYA_PATH.exists():
    from laya import Agent  # noqa: E402
    from laya_choice_data import QID, QUESTION  # noqa: E402
    LAYA = Agent(str(LAYA_PATH), device="cpu")


def tag(title, text, use_laya):
    e = embed_text(ST, title, text)[None, :]
    pe = np.array([m.predict_proba(e)[0, 1] for m in TAG["minilm_models"]])
    pt = np.array([m.predict_proba(TAG["tfidf"].transform([title + " " + text]))[0, 1] for m in TAG["tfidf_models"]])
    p = (pe + pt) / 2
    thr = (np.array(TAG["thr_minilm"]) + np.array(TAG["thr_tfidf"])) / 2
    out = {"model": "avg(TF-IDF+LR, MiniLM-L6+LR)", "trained_on_notes": TAG["trained_on"],
           "tags": sorted(({"tag": t, "p": round(float(p[i]), 3), "pass": bool(p[i] >= thr[i])} for i, t in enumerate(TAG["tags"])),
                          key=lambda r: -r["p"])}
    if use_laya and LAYA:   # the VPS-trained Laya was fine-tuned on the 12-way "which topic" choice question (150-word chunks, mean per tag)
        ws = text.split(); chunks = [" ".join(ws[k:k + 150]) for k in range(0, len(ws), 150)][:6] or ["empty"]
        ps = [LAYA.predict({"passage": c}, {QID: QUESTION})["answers"][QID]["probabilities"] for c in chunks]
        out["laya_topic"] = {t: round(float(np.mean([p[t] for p in ps])), 4) for t in TAG["tags"]}
    elif use_laya:
        out["laya_topic"] = None  # no models/laya checkpoint installed
    return out


def find(q, k):
    s = VEC @ ST.encode([q], normalize_embeddings=True)[0]
    best = {}
    for sl, x in zip(SLUGS, s):
        best[sl] = max(best.get(sl, -1.0), float(x))
    return [{"slug": a, "score": round(b, 3)} for a, b in sorted(best.items(), key=lambda kv: -kv[1])[:k]]


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _authed(self):
        return not TOKEN or self.headers.get("Authorization") == f"Bearer {TOKEN}"

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "laya": LAYA is not None, "notes_indexed": len(set(SLUGS))})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        n = int(self.headers.get("Content-Length", 0))
        if n > 200_000:
            return self._send(413, {"error": "body too large"})
        try:
            d = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/tag":
                return self._send(200, tag(d.get("title", ""), d["text"], bool(d.get("laya"))))
            if self.path == "/find":
                return self._send(200, {"results": find(d["query"], int(d.get("k", 5)))})
        except (KeyError, ValueError) as e:
            return self._send(400, {"error": f"bad request: {e}"})
        self._send(404, {"error": "not found"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"system-one service on {HOST}:{PORT} (laya={'on' if LAYA else 'off'})", flush=True)
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
