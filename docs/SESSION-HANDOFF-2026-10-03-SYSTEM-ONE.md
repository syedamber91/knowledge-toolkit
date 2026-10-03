# Handoff: System One (Jev / Laya / MiniLM) vault, skill, agent and experiments (2026-10-03)

**Read this first if you touch `knowledge/system-one/`, `plugins/system-one/`, `scripts/system_one_train/`, anything Laya, or are asked
"which model should decide this: code, MiniLM, Jev, Laya, Sonnet or Opus?".** Status: done and merged (PRs
[#27](https://github.com/syedamber91/knowledge-toolkit/pull/27), [#28](https://github.com/syedamber91/knowledge-toolkit/pull/28),
[#30](https://github.com/syedamber91/knowledge-toolkit/pull/30), [#34](https://github.com/syedamber91/knowledge-toolkit/pull/34),
[#35](https://github.com/syedamber91/knowledge-toolkit/pull/35), [#36](https://github.com/syedamber91/knowledge-toolkit/pull/36),
[#37](https://github.com/syedamber91/knowledge-toolkit/pull/37)). Nothing is in flight. The only thing running on the VPS is the local
`system-one` service. This file is public: host names, user names, IPs and keys are deliberately absent. The private companions are
named at the bottom.

## TL;DR
- Built a 72-note **System One vault** from TypeSafe's Jev docs plus Laya/Kev/MiniLM sources, a **`system-one` skill** (which tier decides) and an
  **Opus `system-one-advisor` agent**, shipped as a plugin and as `.claude/` copies.
- Tested which model best tags SOIC lecture material against the **owner's own hand-checked labels** (80 spoken passages + 20 notes, blind).
  Jev's 13-way "which topic" question won clearly (top-1 0.64); every local model (MiniLM, trained/untrained Laya, BGE reranker) sat at
  0.34-0.41; keywords (TF-IDF) at 0.16-0.18. Whole-note tagging is a tie at n=20, so the free local tagger stays for existing notes.
- Fine-tuned Laya on the VPS CPU and deployed it with a local tagger + vault-finder service. Laya exists in ONE installed place.

## Where everything is (do not re-paste: read the file)
| Need | Read |
|---|---|
| Layout of every artifact, what is private, how a job picks up the trained model | [`docs/SYSTEM-ONE-ARTIFACTS.md`](SYSTEM-ONE-ARTIFACTS.md) |
| All measured results, tables, bootstrap CIs, Fable's reviews, the hand-check study, rerankers | [`docs/SYSTEM-ONE-TRAINING.md`](SYSTEM-ONE-TRAINING.md) |
| Setup of the skill/agent/plugin, cloud vs local, Jev MCP | [`docs/SYSTEM-ONE-SETUP.md`](SYSTEM-ONE-SETUP.md), [`docs/JEV-MCP-SETUP.md`](JEV-MCP-SETUP.md) |
| Decision rules for agents (ladder, tiering, anti-patterns, privacy) | `knowledge/system-one/08-playbook/`, `plugins/system-one/skills/system-one/` |
| Code: training, scoring, hand-check sheet, Jev labelling, service, bundle, fetch | `scripts/system_one_train/` (each script's docstring says how to run it) |
| Resync copies after editing the plugin or vault | `scripts/sync_system_one.sh` |
| Fetch the trained Laya from its private backup | `scripts/system_one_train/fetch_laya_model.sh` |

## Decisions and rules the owner set (keep following them)
1. **ONE installed copy of Laya.** It lives next to the other Laya checkpoints in the soic-ladder checkout's `runs/valuation/`; the service loads it via `LAYA_DIR`.
   Backups are private GitHub releases in the private `soic-ladder` repo (tags `laya-soic-tags-2026-10-03`, `laya-checkpoints-2026-08-30`); a backup is not a second install.
2. **Nothing derived from the paid course content goes in this public repo**: no transcript/note text, no model weights, no answer key, no embeddings.
   (The hand-check sheet and its key are git-ignored under `output/`.)
3. **Jev is advisory.** It never replaces the G2 cited-quote gate or `verify_briefs.py` (see `CLAUDE.md`). Hosted calls send text to a third party: ask first for anything
   from the paid course; the owner approved spoken test passages only, not written notes.
4. **The 100 hand labels are for JUDGING, never for tuning.** Pre-register one variant per idea; report paired bootstrap CIs resampling NOTES (passages of one note are not independent).
5. Style: the owner wants short, plain answers; say plainly when a claim was too strong (several were, and were corrected in the docs after Fable's review).

## Gotchas that cost time (reusable)
- A GitHub secret cannot be read back. To use one on the VPS: a throwaway-branch workflow in a PRIVATE repo that has VPS runners, data staged in a shared folder (the runner's OS user cannot read root's home),
  nothing from the data printed. Never register VPS runners on a public repo.
- `gh release create "$TAG" ...` with an unset `$TAG` silently shifts arguments (made a wrongly named release without the big file). Use `set -u`, then verify assets and digests.
- The Kaggle runner scripts in soic-ladder `shutil.rmtree` an existing output dir: never re-run a job into an existing checkpoint name; never restore a backup over a live dir.
- `pgrep -f NAME` inside a `bash -c` that contains NAME matches itself ("alive" false positive). macOS `sed -i` needs `''`; use Python for edits.
- Background jobs over ssh: `setsid nohup ... < /dev/null &`, then poll marker files; a plain `&` holds the channel open and the tool call times out.
- This Mac has 8 GB RAM: no Laya training here. VPS CPU training took about 6 s per item and about 4.6 h for 2,979 items; Kaggle T4 took 2.2 h for a different set-up.
- Qwen3-Reranker on CPU: pass `logits_to_keep=1` or full-vocabulary logits at every position OOM-kill the run.
- The soic-ladder user's `rerank-venv` is in use by two jobs (RAG open items, MiniLM sentence eval) and self-rebuilds; it was deliberately kept. Check references before deleting anything in that user's tree.

## Open items (all optional)
1. Untested Jev ideas from Fable's plan, one pre-registered variant each: neighbouring-passage context; use the original tagging subagents' definitions; skip ASR cleanup; Jev on written note text needs new owner approval.
2. If a Jev-based tagger for NEW lectures is wanted: raw transcript windows, choice + 12 yes/no, mean per lecture, a global cutoff or top-2 (never 0.5), review windows with choice confidence under 0.6; re-approve privacy for full transcripts.
3. Anomalies in the older soic-ladder Laya fine-tunes (debt-ceiling never given an AUC eval; overlap report/config temperature mismatch) are listed in the VPS-side `LAYA-INDEX.md`.
4. A bigger hand-labelled set would tighten the +-0.15 error bars.
5. `/graphify .` (the graph is flagged stale after these commits).

## Not verified
- Installing the `system-one` plugin from this repo into a DIFFERENT repo in a cloud session (marketplace file exists; never tested there).
- Fable could not recompute the TF-IDF-dependent comparisons (no sklearn on that machine); Jev vs written-notes TF-IDF at note level is inside noise (n=109, +-0.08).
- Absolute accuracies from the hand-check sample: it was built from Jev disagreements, so use it to RANK models, not to read accuracy.

## Suggested skills for the next session
`system-one` (tier ladder, question design), `jev-checkpoint` (when to call which `jev_*` tool), `verification-before-completion`, `claude-handoff`,
`karpathy-guidelines` / `ponytail` (keep it small), `vault-ask` (query the vault). For anything about private data: re-read `CLAUDE.md` guardrails first.

## Private companions (not in this repo)
The owner's private memory notes (index entry "System One vault/skill/agent") and the VPS-side `LAYA-INDEX.md` / `LAYA-MOVES-2026-10-03.txt` next to the Laya checkpoints hold the
host-level details (access, paths, users, the soic-ladder workflow route for using the Jev key).
