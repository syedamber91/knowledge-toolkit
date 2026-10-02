"""Build a self-contained Kaggle script-kernel (same pattern as the VPS's kaggle-real-kernel-v5):
code + data embedded as base64 xz tar, internet on, GPU on. PRIVATE kernel, private data.
  build_kernel.py smoke|full  -> output/system_one_train/kaggle_<mode>/{run_soic_tags.py,kernel-metadata.json}"""
import base64, io, lzma, sys, tarfile, json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
S, O = R / "scripts/system_one_train", R / "output/system_one_train"
mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
assert mode in ("smoke", "full")
FILES = {"scripts/" + n: S / n for n in ("common.py", "train_minilm.py", "minilm_core.py", "eval_laya.py", "finetune_laya_soic.py")}
FILES |= {"data/train.jsonl": O / "laya/train.jsonl", "data/test.jsonl": O / "laya/test.jsonl"}
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode="w") as tf:
    for arc, p in FILES.items(): tf.add(p, arcname=arc)
payload = base64.b64encode(lzma.compress(buf.getvalue(), preset=9)).decode()
EPOCHS = 1 if mode == "smoke" else 3
RUN = f'''"""SOIC tag fine-tune of Laya on a Kaggle GPU ({mode}). Code + data embedded below (base64 xz tar)."""
import base64, io, json, lzma, os, subprocess, sys, tarfile, time
MODE, EPOCHS = "{mode}", {EPOCHS}
W = "/kaggle/working"
PAYLOAD_B64 = """
{payload}
"""
t0 = time.time()
tarfile.open(fileobj=io.BytesIO(lzma.decompress(base64.b64decode(PAYLOAD_B64)))).extractall(W + "/work")
os.chdir(W + "/work/scripts")
def sh(cmd):
    print(">>", " ".join(cmd), flush=True); r = subprocess.run(cmd); print("exit", r.returncode, f"t={{time.time()-t0:.0f}}s", flush=True); return r.returncode
if MODE == "smoke":   # tiny slice: proves the whole path in minutes
    for n, k in (("train", 12), ("test", 6)):
        p = f"../data/{{n}}.jsonl"; rows = open(p).readlines()[:k]; open(p, "w").writelines(rows)
sh([sys.executable, "-m", "pip", "install", "-q", "laya==0.3.23", "datasets"])
import torch; print("cuda:", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
rc = sh([sys.executable, "finetune_laya_soic.py", "--train-jsonl", "../data/train.jsonl", "--model-dir", W + "/laya_base",
         "--output-dir", W + "/laya_soic", "--epochs", str(EPOCHS), "--micro-batch", "1", "--grad-accum", "32"])
status = {{"mode": MODE, "finetune_rc": rc}}
if rc == 0:
    status["eval_rc"] = sh([sys.executable, "eval_laya.py", "--model", W + "/laya_soic", "--name", "Laya fine-tuned " + MODE,
                            "--data", "../data", "--out", W + "/results"])
    subprocess.run(["rm", "-rf", W + "/laya_soic/checkpoint_latest", W + "/laya_base", W + "/work"])  # keep output small
status["seconds"] = round(time.time() - t0); json.dump(status, open(W + "/status.json", "w")); print(status)
sys.exit(0 if rc == 0 and status.get("eval_rc") == 0 else 1)
'''
d = O / f"kaggle_{mode}"; d.mkdir(parents=True, exist_ok=True)
(d / "run_soic_tags.py").write_text(RUN)
(d / "kernel-metadata.json").write_text(json.dumps({"id": f"syedamberiqbal/soic-tags-laya-{mode}", "title": f"soic-tags-laya-{mode}",
    "code_file": "run_soic_tags.py", "language": "python", "kernel_type": "script", "is_private": True, "enable_gpu": True,
    "enable_internet": True, "dataset_sources": [], "competition_sources": [], "kernel_sources": []}, indent=2))
print(f"{mode}: payload {len(payload)//1024} KB, script {(d/'run_soic_tags.py').stat().st_size//1024} KB -> {d}")
