"""Score a Laya checkpoint on the held-out test NOTES via the 12-way choice question (CPU ok).
A note is cut into <=6 chunks of ~150 words; per-tag probabilities are averaged over chunks.
  eval_laya_choice.py NOTES.jsonl MODEL_DIR_OR_ID NAME OUT_DIR"""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS
from laya_choice_data import QID, QUESTION
from train_minilm import metrics
notes_p, model, name, out = sys.argv[1:5]
te = [json.loads(l) for l in open(notes_p)]; te = [n for n in te if n["split"] == "test"]
from laya import Agent
agent = Agent(model, device="cpu"); t0 = time.time(); P = []
for i, n in enumerate(te):
    w = n["text"].split(); ch = [" ".join(w[k:k + 150]) for k in range(0, len(w), 150)][:6] or ["empty"]
    ps = [agent.predict({"passage": c}, {QID: QUESTION})["answers"][QID]["probabilities"] for c in ch]
    P.append([np.mean([p[t] for p in ps]) for t in TAGS])
    if i % 20 == 0: print(i, f"{time.time()-t0:.0f}s", flush=True)
P = np.array(P); Y = np.array([[int(t in n["tags"]) for t in TAGS] for n in te])
Path(out).mkdir(parents=True, exist_ok=True); np.save(Path(out) / f"probs_{name.replace(' ', '_')}.npy", P)
rs = [metrics(P, Y, np.median(P, axis=0), name + " (choice; thr=per-tag median)")]
rs[0]["top1_hit"] = round(float(np.mean([Y[i, int(np.argmax(P[i]))] == 1 for i in range(len(Y))])), 3)
(Path(out) / f"choice_results_{name.replace(' ', '_')}.json").write_text(json.dumps(rs, indent=1))
r = rs[0]; print(f"{r['model']:56s} microF1 {r['micro_f1']:.3f} macroF1 {r['macro_f1']:.3f} AUC {r['mean_auc']:.3f} top1 {r['top1_hit']:.3f}")
