# Training MiniLM + Laya on the SOIC tags, and moving it to the VPS

Written 2026-10-02. Code: `scripts/system_one_train/`. Everything trained or derived from your notes lives in
`output/system_one_train/` (gitignored, PRIVATE). Never commit it.

## Task
Tag each of the 459 SOIC concept notes with 1-3 of 12 fixed tags (`wiki/personas/soic/concepts/`, Learning Vault Invest).
Labels come from the LLM tagging pass in CLAUDE.md, so every score below is **agreement with that tagger, not truth**.
Split by module (`topics`), 345 train / 114 test, so near-duplicate notes never straddle the split.

## Measured results (114 held-out notes)
| Model | micro-F1 | macro-F1 | mean AUC | top-1 hit |
|---|---|---|---|---|
| predict tag frequency | 0.00 | 0.00 | 0.50 | 0.44 |
| TF-IDF + LR | 0.64 | 0.58 | 0.87 | 0.80 |
| MiniLM-L6 + LR | 0.58 | 0.52 | 0.86 | 0.78 |
| **avg(TF-IDF, MiniLM)** (deployed) | 0.62 | 0.56 | 0.87 | **0.83** |
| Laya zero-shot | 0.32 | 0.30 | 0.69 | 0.47 |
| Laya fine-tuned (3 epochs, Kaggle T4, 2 h 13 min) | 0.60 | 0.42 | 0.80 | 0.67 |

Reading it: MiniLM alone did not beat plain keywords; the average is best but the test set is small. Laya zero-shot is
weak, as its own docs say. Fine-tuning lifted it a lot (top-1 0.47 -> 0.67, AUC 0.69 -> 0.80) but it still trails the
MiniLM+TF-IDF average (0.83 / 0.87) on this task. Its noul probabilities are compressed by the fitted temperature (8.5), so use
its ranking or a tuned threshold, never 0.5. Weakest tags: leverage-risk F1 0.00, capital-allocation 0.22, forensic 0.33. It was
installed anyway on the owner's instruction; the tagger endpoint still returns the MiniLM+TF-IDF answer first and Laya's as `laya_noul`.
Vault finder (`vault_finder.py eval`, 18 probes I wrote myself, so optimistic): MiniLM hit@3 1.00 / MRR 0.92 vs TF-IDF 0.94 / 0.78.

## Pipeline
```bash
V=output/system_one_train/.venv/bin/python
$V scripts/system_one_train/train_minilm.py        # CV + holdout eval, saves tagger_final.joblib (refit on all 459)
$V scripts/system_one_train/vault_finder.py eval   # embeds knowledge/system-one, probes vs TF-IDF
$V scripts/system_one_train/export_laya_dataset.py # train.jsonl / test.jsonl (12 yes/no questions per note)
$V scripts/system_one_train/eval_laya.py           # Laya zero-shot on the test split (~4 s/note on MPS)
```
The deployed tagger is refit on ALL notes, so it has no held-out score of its own; the table above is its honest estimate.

## Fine-tuning Laya (needs a GPU: this Mac has 8 GB RAM, upstream wants 16 GB for the Apple path)
`finetune_laya_soic.py` wraps Laya's own training script, pinned at upstream commit `e38c5bfa`, swapping its HF dataset
for our `train.jsonl` and selecting CUDA when present. **Only the preprocessing is verified** (4,140 items, 0 skipped).
Training itself is untested. Upstream reports ~4-5 h for 4 epochs over ~30k questions on 2xT4; ours is ~4k questions.
1. Kaggle: new notebook, GPU on, upload `output/system_one_train/laya/{train,test}.jsonl` as a PRIVATE dataset.
2. `pip install laya datasets` and copy `finetune_laya_soic.py`, `eval_laya.py`, `common.py`, `laya_data.py`, `train_minilm.py`, `minilm_core.py`.
3. `python finetune_laya_soic.py --train-jsonl /kaggle/input/<ds>/train.jsonl --model-dir ./laya_base --output-dir ./laya_soic --epochs 3 --micro-batch 1 --grad-accum 32`
4. `python eval_laya.py --model ./laya_soic --name "Laya fine-tuned" --data /kaggle/input/<ds> --out ./res` and compare with the table.
5. Download `laya_soic/` (model.safetensors, encoder/, tokenizer/, rl_agent_config.json). Keep it only if it beats the MiniLM average.

## VPS deploy (option A: private tarball, nothing leaves your machines)
```bash
scripts/system_one_train/deploy/make_bundle.sh [--laya-dir /path/to/laya_soic]   # -> output/system_one_train/system-one-vps.tar.gz (84 MB)
scp output/system_one_train/system-one-vps.tar.gz you@vps:~/
# on the VPS
tar xzf system-one-vps.tar.gz && cd system-one-vps && sha256sum -c SHA256SUMS | grep -v OK
bash install_vps.sh --service        # venv + CPU torch + pinned deps + smoke test + systemd
curl -s localhost:8765/health
curl -s -X POST localhost:8765/tag  -d '{"title":"...","text":"..."}'
curl -s -X POST localhost:8765/find -d '{"query":"which model for 77 classes","k":5}'
```
Adding the fine-tuned Laya later (no Mac needed): `scp -r laya_soic you@vps:~/system-one-vps/models/laya`, then
`./venv/bin/pip install laya && sudo systemctl restart system-one`; `/tag` with `"laya": true` then returns per-tag probabilities.
- Local-only by default (127.0.0.1). To expose it: `SYSTEM_ONE_HOST=0.0.0.0` + `SYSTEM_ONE_TOKEN` (the server refuses without a token).
- Verified here: bundle unpacks, checksums match, installer + smoke test pass on Python 3.14/arm64, `/health`, `/find`, `/tag` answer.
- NOT verified: an actual VPS. The pinned deps (numpy 2.5, scikit-learn 1.9, transformers 5.18) were built on Python 3.14;
  an older VPS Python may refuse them. The installer demands Python >= 3.10 and pip will say so if the pins need newer.
  A scikit-learn mismatch would break the `.joblib`; if so, rerun `train_minilm.py` on the VPS with the same pins.
- Nothing is sent anywhere by me; I have no VPS access.

## Done on 2026-10-02 (what is actually running)
- VPS (root account, ssh alias `hostinger_root`): `/root/system-one-vps`, systemd service `system-one`, 127.0.0.1:8765, `laya: true`.
- Laya lives in exactly one place: weights `/root/system-one-vps/models/laya`, package in `/root/system-one-vps/venv` only (no HF cache copy).
  Older Laya copies under `/home/syamiq` (soic-ladder runs, kaggle-* kits, HF cache) were left alone: other projects.
- Training ran through the VPS's existing Kaggle setup: `scripts/system_one_train/kaggle/build_kernel.py smoke|full` builds a
  self-contained private script-kernel (code + data embedded), pushed with the kaggle CLI from the VPS. A 12-note smoke run
  (4 min) proved the path before the full run. Data sits in PRIVATE Kaggle kernels `soic-tags-laya-smoke` / `-full`; delete them
  on kaggle.com if you want the notes off Kaggle. Modal was tried earlier and needs a payment method, so it was not used.

## Do transcript passages help? (2026-10-03, run on the VPS CPU)
Weak labels: each passage cited by a concept note inherits that note's tags (`build_passages.py`; 2,979 train passages, 905 test passages
from held-out modules, test passages used for diagnostics only). Same 114 test notes. Fixed hyper-parameters, one run, so gaps under ~5 points are noise.
- Training on spoken passages did NOT help (MiniLM+TF-IDF avg top-1 0.82 notes-only -> 0.69 passages-only, 0.72 notes+passages).
- Diagnostics (`diagnose.py`): written notes cut into passage-sized chunks with the same inherited labels do as well as full notes
  (AUC 0.87 both) -> inherited labels alone are not the problem. Spoken-trained models score 6-10 points lower top-1 on written notes than
  written-chunk-trained ones -> spoken-vs-written shift is real. 5x more data did not help -> label quality, not quantity, is the limit.
  Dropping "suspect" passages (agreement with a notes-trained model) gave mixed results: inconclusive.
- Independent reader check (Option B via Jev): Jev `jev-1.13.0`, 12 yes/no questions per passage, 150 stratified spoken test passages, zero-shot,
  vs the inherited labels: top-1 0.63, mean AUC 0.72 (per-tag AUC 0.61-0.92). Our models on all 905 spoken test passages: AUC 0.72-0.74, top-1 0.52-0.57.
  So an independent strong reader agrees with the inherited passage labels no better than our trained models do: the ceiling on spoken passages is low.
  That fits "loose inherited labels / hard short fragments" but cannot separate the two. Different samples (150 stratified vs 905 random), my own tag
  definitions in the questions, Jev is an AI opinion not ground truth. Hand-checked labels remain the only real answer.
- How Jev was run without the key leaving GitHub: workflow `jev-label-spoken-passages` on a throwaway branch of the private `soic-ladder` repo,
  on its VPS runner (user `syamiq`), reading data staged in /var/tmp/jev-label (deleted after). The log shows the key masked and counts only.
  Per the owner the branch is kept. Raw Jev outputs (ids, tags, probabilities; no passage text): VPS `/root/system-one-train/results/jev_labels.jsonl`.
