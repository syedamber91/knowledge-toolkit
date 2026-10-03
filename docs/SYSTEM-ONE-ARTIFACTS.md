# System One: where everything lives (2026-10-03) and how other jobs pick it up

| Thing | Where | Private? |
|---|---|---|
| Code (training, scoring, hand-check, serve, deploy) | this repo, `scripts/system_one_train/` | public, no data |
| Docs and measured results | this repo, `docs/SYSTEM-ONE-TRAINING.md`, `docs/SYSTEM-ONE-SETUP.md` | public, numbers only |
| Playbook, skill, Opus advisor agent | this repo, `knowledge/system-one/`, `plugins/system-one/` (+ copies in `.claude/`) | public |
| **Fine-tuned Laya** (SOIC topic tags, 808 MB) | **private release** `laya-soic-tags-2026-10-03` in `syedamber91/soic-ladder` (asset `laya-soic-tags-vps-2026-10-03.tar`, sha256 `05fc68fb...42c28`) | **private**: trained on paid-course notes |
| Same model, running | VPS, in the soic-ladder checkout next to the other Laya checkpoints: `runs/valuation/laya-finetune-soic-tags-vps-2026-10-03` (the only installed copy; the service reads it via `LAYA_DIR`) | private |
| Backup of the four older Laya fine-tunes (4 x ~807 MB) | **private release** `laya-checkpoints-2026-08-30` in `syedamber91/soic-ladder` | **private** |
| Index of ALL Laya artifacts (checkpoints, kits, rules, anomalies) | VPS: `runs/valuation/LAYA-INDEX.md`; rollback log of the consolidation moves: `runs/valuation/LAYA-MOVES-2026-10-03.txt` | private |
| Results pack (ids, tags, probabilities, hand-check labels, scoreboards; no text) | same private release, asset `system-one-results-2026-10-03.tar.gz` | private |
| Tagger + vault-finder service | VPS: systemd `system-one`, 127.0.0.1:8765 (`/health`, `/tag`, `/find`) | local only |
| Notes / passages text, transcripts | VPS `/root/system-one-train/data/` and the owner's vault; never committed or released | private |

## Picking the model up from another job
- A **soic-ladder workflow** (private repo, runs on the VPS runners): `GH_TOKEN: ${{ github.token }}` then `scripts/system_one_train/fetch_laya_model.sh <dest>`
  (copy the script in, or `curl` it from this public repo). It verifies the checksum and refuses to create a second copy.
- Any other session: needs `gh` access to `soic-ladder`. This public repo's own token cannot read that private release.
- A job on the VPS that only needs answers should call the local service instead of loading the model:
  `curl -s -X POST localhost:8765/tag -d '{"title":"..","text":"..","laya":true}'` (returns the MiniLM+TF-IDF tags and `laya_topic`).
- Rules: keep ONE installed copy; the release is the backup, not a second install. Do not make `soic-ladder` or the release public.

## What is NOT checked in, on purpose
Transcript passages, note text, the answer-key file with inherited tags, the blind hand-check sheet, embeddings and the Kaggle/VPS
intermediate files: they hold or derive from paid-course content (CLAUDE.md: nothing captured is ever committed).
The 100 hand-check labels (ids and tags only) are in the private results pack.

## Consolidation on the VPS (2026-10-03)
All Laya weights now live in one place, the soic-ladder checkout's `runs/valuation/` (`$SOIC_VAL`, gitignored): the four existing fine-tunes, the new tags model, `laya-base-upstream` (the untouched upstream base) and `laya-kits/` (13 Kaggle/Modal training kits, moved in unchanged). Three Sonnet readers (provenance, kits, job path rules) fed an Opus-written index. Nothing was deleted or renamed in the four existing checkpoint dirs because workflows and committed reports print their paths; no code globs `laya-*`, so a new sibling dir is safe. One exact duplicate name (kernel-v5 output) was kept because its tokenizer config differs; it shares the weights file, so it costs no space. The four 2026-08-30 fine-tunes are backed up (checksums verified) in the private release `laya-checkpoints-2026-08-30` of `syedamber91/soic-ladder`, one tar per checkpoint, restorable with `gh release download`; they must never be restored over an existing directory (the Kaggle runner scripts `rmtree` an existing out-dir).

## Duplicates on the VPS (audit 2026-10-03, before consolidation)
Only one Laya is installed for this project (root). The soic-ladder user's own older Laya fine-tunes (4 workflow outputs under
`runs/valuation/`, a Kaggle kernel output, a Kaggle packaging base) were audited by sha256: one exact duplicate was replaced by a
hardlink (saved ~0.8 GB, no paths changed); the rest are distinct and referenced by soic-ladder workflows, so they were left alone.
