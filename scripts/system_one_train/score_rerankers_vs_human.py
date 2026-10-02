"""Zero-shot RERANKER pilot vs the owner's hand-check labels. Run on the VPS, one model per call (a failure must not kill the others).
  score_rerankers_vs_human.py MODEL_KEY HUMAN_MAP TEST_PASSAGES NOTES OUT_DIR     MODEL_KEY in: msmarco | bge | mxbai | qwen3
ONE pre-registered variant per model, NO tuning on the 100 human labels: query = the topic description (laya_data.DEFS), document = the passage
(or a <=150-word chunk of a note, <=6 chunks, scores averaged per tag); the passage's predicted topic = argmax over the 12 topic queries.
Writes OUT_DIR/preds_rerank_<key>.json in the same format score_models_vs_human.py reports on."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import TAGS
from laya_data import DEFS

key, hm_p, tp_p, notes_p, out = sys.argv[1:6]
HM = json.load(open(hm_p)); P, Nn = HM["passages"], HM["notes"]
TEP = {r["id"]: r for r in map(json.loads, open(tp_p))}; N = {n["slug"]: n for n in map(json.loads, open(notes_p))}
tell = [pid for pid, v in P.items() if v["primary"] != "cant_tell"]
ptxt = {pid: TEP[P[pid]["real_id"]]["text"] for pid in tell}
ntxt = {nid: N[v["slug"]]["title"] + " " + N[v["slug"]]["text"] for nid, v in Nn.items()}
chunk = lambda s, n=150: [" ".join(s.split()[k:k + n]) for k in range(0, len(s.split()), n)][:6] or ["empty"]
NAMES = {"msmarco": "Reranker ms-marco-MiniLM-L6 (zero-shot)", "bge": "Reranker BGE-v2-m3 (zero-shot)", "mxbai": "Reranker mxbai-base-v2 (zero-shot)", "qwen3": "Reranker Qwen3-0.6B (zero-shot)"}
INSTR = "Given a description of an investing topic, judge whether the lecture passage is substantially about that topic"

if key == "qwen3":
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-Reranker-0.6B", padding_side="left")
    lm = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-Reranker-0.6B", torch_dtype=torch.float32).eval()
    yes, no = tok.convert_tokens_to_ids("yes"), tok.convert_tokens_to_ids("no")
    pre = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
    suf = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
    def score(pairs):                       # pairs: [(query, doc)] -> P(yes)
        out = []
        for i in range(0, len(pairs), 6):
            txt = [f"{pre}<Instruct>: {INSTR}\n<Query>: {q}\n<Document>: {d}{suf}" for q, d in pairs[i:i + 6]]
            enc = tok(txt, return_tensors="pt", padding=True, truncation=True, max_length=1024)
            with torch.no_grad(): lg = lm(**enc).logits[:, -1, :]
            out += torch.log_softmax(torch.stack([lg[:, no], lg[:, yes]], 1), 1)[:, 1].exp().tolist()
        return np.array(out)
else:
    from sentence_transformers import CrossEncoder
    repo = {"msmarco": "cross-encoder/ms-marco-MiniLM-L6-v2", "bge": "BAAI/bge-reranker-v2-m3", "mxbai": "mixedbread-ai/mxbai-rerank-base-v2"}[key]
    ce = CrossEncoder(repo, device="cpu", max_length=512)
    score = lambda pairs: np.array(ce.predict(pairs, batch_size=8, show_progress_bar=False)).reshape(-1)

def tag_scores(docs):                         # -> (len(docs), 12)
    pairs = [(DEFS[t], d) for d in docs for t in TAGS]
    return score(pairs).reshape(len(docs), len(TAGS))

t0 = time.time(); pids = list(ptxt)
S = tag_scores([ptxt[p] for p in pids]); pp = {p: TAGS[int(np.argmax(S[k]))] for k, p in enumerate(pids)}
print(key, "passages done", f"{time.time()-t0:.0f}s", flush=True)
nn = {}
for nid in Nn:
    cs = chunk(ntxt[nid]); nn[nid] = TAGS[int(np.argmax(tag_scores(cs).mean(0)))]
print(key, "notes done", f"{time.time()-t0:.0f}s", flush=True)
Path(out).mkdir(parents=True, exist_ok=True)
(Path(out) / f"preds_rerank_{key}.json").write_text(json.dumps({NAMES[key]: {"passages": pp, "notes": nn}}))
print("saved", NAMES[key])
