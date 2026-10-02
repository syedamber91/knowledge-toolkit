"""Fine-tune Laya on the SOIC tag questions using Laya's OWN training script (not vendored).
Downloads NandhaKishorM/laya's notebooks/laya_finetune_typed_decisions_mps.py at a pinned commit,
swaps its HF dataset for our local train.jsonl, and picks CUDA when present (the upstream script
only knows mps/cpu). Intended for a free Kaggle/Colab GPU: this Mac has 8 GB RAM, too little for
421M-param AdamW training (upstream says 16 GB for the MPS path).

  python finetune_laya_soic.py --train-jsonl train.jsonl --model-dir ./laya_base --output-dir ./laya_soic \
        --epochs 3 --micro-batch 1 --grad-accum 32
UNTESTED end-to-end here: only the preprocessing step is verified locally (see docs/SYSTEM-ONE-TRAINING.md)."""
import importlib.util, json, sys, urllib.request
from pathlib import Path

PIN = "e38c5bfa2f01b7830d7bdb83d2d58432f51f0924"
URL = f"https://raw.githubusercontent.com/NandhaKishorM/laya/{PIN}/notebooks/laya_finetune_typed_decisions_mps.py"


def load_upstream():
    dst = Path("laya_finetune_upstream.py")
    if not dst.exists():
        dst.write_bytes(urllib.request.urlopen(URL, timeout=60).read())
    spec = importlib.util.spec_from_file_location("laya_ft", dst)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def main():
    args = sys.argv[1:]
    jl = Path(args[args.index("--train-jsonl") + 1]); del args[args.index("--train-jsonl"):args.index("--train-jsonl") + 2]
    mod = load_upstream()
    import torch, types
    try:
        import datasets
    except ImportError:  # CPU VPS: avoid pulling pyarrow/pandas just to be patched out
        datasets = sys.modules["datasets"] = types.ModuleType("datasets")
    datasets.load_dataset = lambda *a, **k: [json.loads(l) for l in open(jl) if l.strip()]
    mod.DATASET_ID = f"local:{jl.name}"
    orig = mod.choose_device
    mod.choose_device = lambda req: torch.device("cuda") if (req == "auto" and torch.cuda.is_available()) else orig(req)
    sys.argv = ["finetune"] + args
    mod.main()


if __name__ == "__main__":
    main()
