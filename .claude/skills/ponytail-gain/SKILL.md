---
name: ponytail-gain
description: >
  Show ponytail's measured impact as a compact scoreboard: less code, less
  cost, more speed, from the benchmark medians. One-shot display, not a
  persistent mode, and not a per-repo number. Trigger: /ponytail-gain,
  "ponytail gain", "what does ponytail save", "show ponytail impact",
  "ponytail scoreboard".
---

> **Provenance (vendored 2026-09-17).** Copied verbatim from
> `github.com/DietrichGebert/ponytail` @ `e3ba2aa`, plugin version **4.10.0**,
> author Dietrich Gebert. Vendored rather than plugin-installed because
> `.claude/settings.json`'s `extraKnownMarketplaces` + `enabledPlugins` do NOT
> trigger an install on their own — measured 2026-09-17 in a fresh cloud session
> on this repo's `main`: the settings file was present, `ListPlugins` returned
> `[]`, `installed_plugins.json` was empty, and no marketplace had been fetched.
> The plugin installs only when a human runs `/plugin marketplace add
> DietrichGebert/ponytail` then `/plugin install ponytail@ponytail`, which writes
> those same two keys into USER settings and clones the marketplace. Vendoring
> makes the six skills load with no network, no `node`, and no per-machine step —
> the same reason `grill-me` is pinned here.
>
> **What vendoring does NOT carry: the two lifecycle hooks.** Upstream's
> always-on activation (`hooks/ponytail-activate.js`,
> `hooks/ponytail-instructions.js`) and its statusline badge are plugin-only, so
> the mode is NOT applied automatically here — invoke `/ponytail` when you want
> it. Reviewed before vendoring: pure prose, no scripts, network calls or
> postinstall steps. To update, re-clone upstream and diff against this file
> deliberately.
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
