"""Score a Laya checkpoint (HF id or local dir) on the held-out SOIC test notes, same metrics as MiniLM.
  eval_laya.py [--model convaiinnovations/laya | ./laya_finetuned...] [--name zero-shot]
Laya's noul probabilities are over-confident zero-shot (all near 0.6-0.9), so AUC/top-1 matter more than F1@0.5."""
import argparse, json, sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import OUT, TAGS
from train_minilm import metrics

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="convaiinnovations/laya"); ap.add_argument("--name", default="Laya zero-shot")
ap.add_argument("--data", default=str(OUT / "laya"), help="dir holding test.jsonl (works on Kaggle: no vault needed)")
ap.add_argument("--out", default=str(OUT))
a = ap.parse_args()
from laya import Agent
agent = Agent(a.model)
rows = [json.loads(l) for l in open(Path(a.data) / "test.jsonl")]
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
P = np.array([[agent.predict(json.loads(r["state"]), json.loads(r["questions"]))["answers"][t]["noul"] for t in TAGS] for r in rows])
Y = np.array([[1 if json.loads(r["gold"])[t]["label"] == "true" else 0 for t in TAGS] for r in rows])
np.save(OUT / f"laya_probs_{a.name.replace(' ', '_')}.npy", P)
res = metrics(P, Y, np.full(len(TAGS), 0.5), a.name)
# also report with per-tag threshold = median predicted prob (rank-based, no labels used)
res_med = metrics(P, Y, np.median(P, axis=0), a.name + " (thr=per-tag median)")
(OUT / f"laya_results_{a.name.replace(' ', '_')}.json").write_text(json.dumps([res, res_med], indent=1))
for r in (res, res_med): print(f"{r['model']:44s} microF1 {r['micro_f1']:.3f} macroF1 {r['macro_f1']:.3f} AUC {r['mean_auc']:.3f} top1 {r['top1_hit']:.3f}")
