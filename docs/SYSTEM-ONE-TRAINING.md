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
Adding the fine-tuned Laya later (no Mac needed): copy the folder next to the other Laya checkpoints (see SYSTEM-ONE-ARTIFACTS.md), point `LAYA_DIR` in the service unit at it, then
`./venv/bin/pip install laya && sudo systemctl restart system-one`; `/tag` with `"laya": true` then returns per-tag probabilities.
- Local-only by default (127.0.0.1). To expose it: `SYSTEM_ONE_HOST=0.0.0.0` + `SYSTEM_ONE_TOKEN` (the server refuses without a token).
- Verified here: bundle unpacks, checksums match, installer + smoke test pass on Python 3.14/arm64, `/health`, `/find`, `/tag` answer.
- NOT verified: an actual VPS. The pinned deps (numpy 2.5, scikit-learn 1.9, transformers 5.18) were built on Python 3.14;
  an older VPS Python may refuse them. The installer demands Python >= 3.10 and pip will say so if the pins need newer.
  A scikit-learn mismatch would break the `.joblib`; if so, rerun `train_minilm.py` on the VPS with the same pins.
- Nothing is sent anywhere by me; I have no VPS access.

## Done on 2026-10-02 (what is actually running)
- VPS (root account): `/root/system-one-vps`, systemd service `system-one`, 127.0.0.1:8765, `laya: true`.
- Laya lives in exactly one place (consolidated 2026-10-03): the weights are in the soic-ladder checkout's `runs/valuation/laya-finetune-soic-tags-vps-2026-10-03`, next to the other Laya checkpoints; the `laya` package is in the service venv only (no HF cache copy). The service reads the weights via `LAYA_DIR`. All Laya artifacts are indexed in that folder's `LAYA-INDEX.md`; see `docs/SYSTEM-ONE-ARTIFACTS.md`.
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
  on its VPS runner (the runner's own OS user), reading data staged in /var/tmp/jev-label (deleted after). The log shows the key masked and counts only.
  Per the owner the branch is kept. Raw Jev outputs (ids, tags, probabilities; no passage text): VPS `/root/system-one-train/results/jev_labels.jsonl`.

## Making Jev score better on spoken passages: Fable's ideas 2, 5, 6, 7 (2026-10-03, owner chose option A)
Fable (independent review, files read only) said the target itself is noisy: "better" = agrees more with note-level tags copied onto fragments, and a perfect
reader can't reach AUC 1.0. Run #2 sent ALL 905 spoken test passages (109 notes) to Jev, same 12 noul questions + one 13-way choice question (12 tags + "none") in
the same call (`jev_label2.py`, `jev_analysis.py`; via the soic-ladder VPS-runner workflow, data staged then deleted; raw numbers in VPS `results/jev_labels2.jsonl`).
Error bars: paired bootstrap over NOTES (1,000 resamples). Still agreement with inherited labels, not truth.
| Idea | Result | Verdict |
|---|---|---|
| baseline, passage level | 12 noul: top-1 0.598, AUC 0.733 (150-sample run said 0.627 / 0.723) | consistent |
| 5: add choice+"none" | top-1 0.650 (+0.052, CI +0.022..+0.085) but AUC 0.710 (-0.024, CI -0.044..-0.003) | **corrected after Fable's review:** the top-1 ignores "none"; counting a "none" pick (11.7% of passages) as a miss gives 0.593, NOT above noul 0.598. Among non-none passages choice still wins (0.672 vs 0.618), so it helps as a forced pick, not as a labeller. AUC drop falls on secondary tags (choice squeezes a 2nd tag). Constant "sector-macro" scores top-1 0.459, so 0.60-0.65 is +0.14-0.19 over a constant |
| 6: rank-average with TF-IDF(+MiniLM) | AUC 0.765 / 0.776 (+0.025 / +0.036 over best single, both CIs exclude 0) | method fine (best single re-chosen inside each resample = conservative) but unverified by Fable here (sklearn missing); rank-normalising uses the 905 test ranks, so it is NOT deployable per passage without stored reference quantiles; TF-IDF spoken-trained partly learns the labeller |
| 2: aggregate to note level (mean) | Jev noul mean: top-1 0.706, AUC 0.860. Jev choice mean: top-1 0.798, AUC 0.883. Reference TF-IDF trained on written notes, same 109 notes: 0.789 / 0.875 | **overclaimed, corrected:** Jev choice-mean top-1 CI [0.716, 0.872] (+-0.08, not +-0.04), AUC CI [0.855, 0.906]. Difference to the written-notes TF-IDF reference (~+0.01) is inside noise. Not apples-to-apples: TF-IDF reads the tagged note, Jev reads passages the note writer CHOSE as on-topic. Score rises with passage count (1-3: 0.667, 4-8: 0.750, 9-12: 0.860 top-1; one random passage per note 0.651). `mean` beat `max` and noisy-OR. The right comparison (spoken-trained TF-IDF aggregated per note) was never computed |
| 7 (measurement only) | note-level micro-F1 @0.5 = 0.164 vs per-tag thresholds tuned on the other half = 0.545 | never use 0.5 with Jev; AUC unchanged by definition. Fable: ONE global threshold (0.562) or plain top-2 (0.562) matches the per-tag tuned 0.549, so per-tag tuning is unsupported; choice-mean does better (tuned 0.641, top-2 0.616) |
Not run: 1 (Jev on written chunks, needs sending note text: not approved), 3 (question rewrites), 4 (neighbour context), 8 (ASR cleanup).
Hand-checked labels remain the only way to separate "noisy labels" from "hard fragments".

### Fable's final review (2026-10-03, recomputed from the raw Jev file; TF-IDF-dependent numbers unverified there)
- All doc numbers reproduce. Wording to soften: "real", "on par", "+-0.04" (now fixed above).
- Code issues in `jev_analysis.py`: hard-coded `/root/...` path; unused `best`; bare `except ValueError`; per-resample tag filtering changes the AUC tag set (forensic has ~5 positive notes);
  argmax ties go to the first tag (3% of passages); choice top-1/AUC silently drop "none"; idea 7 only on noul, no global-threshold/top-k control; shared `rng`.
  Data: 22 duplicate test passage texts, 2 test passages identical to train passages (tiny leak for the spoken-trained model).
- Jev's choice confidence is informative and unused: max >= 0.8 covers 49% of passages at 0.753 hit, below 0.4 it hits 0.482. Speech-garble proxy shows no relation to hit rate.
- Ideas not run, bar = top-1 >= +0.04 or AUC >= +0.03 with CI excluding 0 (paired bootstrap over notes), ONE pre-registered variant each, no tuning wording against these labels:
  first idea 4 (neighbour passages, +-1 window, all 905), then idea 3 (use the definitions the original tagging subagents saw instead of my DEFS), idea 8 skip, idea 1 skip (not approved; local TF-IDF on written notes is already 0.80/0.87 and free).
- Recommendation: do NOT build a Jev note tagger to replace MiniLM+TF-IDF (0.83/0.87, free, private) for existing notes; stop Laya for this task. Jev only earns a place for NEW
  lectures with no note: raw transcript windows -> choice + 12 nouls -> mean per lecture -> top-2 or one global threshold -> review windows with choice max < 0.6.
  Transcripts leave the VPS for TypeSafe: re-approve for full transcripts. Expect < 0.80 on un-curated windows [inference].
- Human-labelling plan (<= 2 h): 80 spoken passages (<=2 per note: 30 where Jev agrees with inherited, 30 confident disagreements, 20 none/low), read BLIND (no inherited tags, no Jev),
  primary tag + optional second + "can't tell"; plus 20 test notes confirmed. Score: inherited-vs-human = label noise, Jev-vs-human, "can't tell" rate = hard-fragment rate. n=80 gives +-0.11.

## Final scoreboard vs the owner's hand-checked labels (2026-10-03; 66 tellable passages, population-weighted, 95% bootstrap CI)
Top-1 equals the owner's primary topic. Sample was built from Jev disagreements/uncertainty, so use it to RANK models, not to read accuracy; CIs are about +-0.13.
| Model | top-1 |
|---|---|
| Jev, 13-way topic question | **0.64** [0.53-0.76] |
| Jev, 12 yes/no | 0.52 [0.39-0.64] |
| MiniLM (written notes / spoken) | 0.41 / 0.37 |
| Laya VPS-trained yes/no; Laya untrained yes/no; Laya Kaggle-trained yes/no | 0.39; 0.39; 0.37 |
| BGE-reranker-v2-m3 zero-shot (best local on "either of the owner's two topics": 0.60) | 0.39 [0.26-0.52] |
| Laya trained, topic question (both trained Layas) / untrained | 0.34 / 0.23 |
| mxbai-rerank-base-v2 / ms-marco MiniLM reranker | 0.28 / 0.21 |
| TF-IDF (spoken / written) | 0.18 / 0.16 |
Chance references: random 12 tags 0.08; always "sector-macro" 0.14; random tag from the AI tags 0.30; the AI tag SET contains the owner's primary 0.78.
Whole notes (20): top-1 in the owner's tags: Jev topic 17/20, TF-IDF 15-17, MiniLM 12-16, BGE reranker 13, Laya 7-13: not separable at n=20.
Laya on 114 held-out notes vs AI tags (choice protocol, chunk-mean): VPS-trained AUC 0.860 / top-1 0.702; Kaggle-trained 0.783 / 0.667; untrained 0.756 / 0.412.
Qwen3-Reranker-0.6B: first run was OOM-killed at a 5 GB cap (full-vocabulary logits at every position); fixed with `logits_to_keep=1` and rerun; its result is in the private results pack once finished.
The VPS-trained Laya replaced the Kaggle-trained one on the notes test (both top-1 and AUC); against the owner's labels the two tie, so that swap is not evidence of a better model.
Artifacts and how to pick them up: `docs/SYSTEM-ONE-ARTIFACTS.md`.
