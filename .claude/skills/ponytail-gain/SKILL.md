---
name: ponytail-gain
description: >
  Show ponytail's measured impact as a compact scoreboard: less code, less
  cost, more speed, from the benchmark medians. One-shot display, not a
  persistent mode, and not a per-repo number. Trigger: /ponytail-gain,
  "ponytail gain", "what does ponytail save", "show ponytail impact",
  "ponytail scoreboard".
---

> **Provenance (vendored 2026-08-19).** Copied verbatim from
> `github.com/DietrichGebert/ponytail` @ `2ed6c52` (2026-08-08), MIT, author
> `DietrichGebert`, upstream plugin version 4.9.0. Vendored rather than
> installed from the marketplace so the text is pinned and reviewable in-repo —
> a skill is an instruction file that steers future sessions, so it should not
> silently change under us. To update, re-clone upstream and diff against this
> file deliberately.
>
> **Reviewed before install.** The six `ponytail*` SKILL.md files are pure
> prose — no scripts, network calls, or postinstall steps. Upstream also ships
> session hooks (`hooks/*.js`), vendored separately at
> `.claude/hooks/ponytail/` and wired only by `scripts/install-global-skills.sh`;
> those were read line-by-line and touch only the local filesystem and env vars
> (`fs`, `path`, `os`, `process.env`) — no network, no `exec`/`spawn`.
>
> **Precedence in this repo.** ponytail is the *primary* general prior at
> intensity `full`, ranking above `karpathy-guidelines`. It is still outranked
> by this repo's non-negotiable invariants and by the repo-specific skills
> (`test-driven-development`, `verification-before-completion`, `writing-plans`,
> `systematic-debugging`). See "Skill precedence" in `CLAUDE.md` for the full
> ladder and the explicit do-not-cut list.

# Ponytail Gain

Display this scoreboard when invoked. One-shot: do NOT change mode, write flag
files, or persist anything.

The figures are the published benchmark medians (5 everyday tasks: email
validator, debounce, CSV sum, countdown timer, rate limiter; three models:
Haiku, Sonnet, Opus). They are measured, not computed from the current repo.
Source: `benchmarks/` and the README.

## Scoreboard

Render plain ASCII bars. The bar length shows the measured range; the label
carries the exact figure:

```
  ponytail gain                     benchmark median · 5 tasks · 3 models

  Lines of code   no-skill  ████████████████████  100%
                  ponytail  ██▌·················    6–20%   ▼ 80–94%
  Cost            no-skill  ████████████████████  100%
                  ponytail  █████▌··············   23–53%  ▼ 47–77%
  Speed           ponytail  ▸ 3–6× faster

  This repo:  /ponytail-debt  (shortcuts you deferred)
              /ponytail-audit (what's still cuttable)
```

## Honesty boundary

These are benchmark medians, not this repo. NEVER print a per-repo savings
number ("you saved X lines/tokens here"): the unbuilt version was never
written, so there is no real baseline to subtract from in a live repo. The
only real per-repo figures come from `/ponytail-debt` (a counted ledger), and
this card points there instead of inventing one.

## Boundaries

One-shot display. Edits nothing, changes no mode.
"stop ponytail" or "normal mode": revert.
