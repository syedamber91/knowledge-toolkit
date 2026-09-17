---
name: ponytail-debt
description: >
  Harvest every `ponytail:` comment in the codebase into a debt ledger, so the
  deliberate shortcuts and deferrals ponytail leaves behind get tracked instead
  of rotting into "later means never". Use when the user says "ponytail debt",
  "/ponytail-debt", "what did ponytail defer", "list the shortcuts", "ponytail
  ledger", or "what did we mark to do later". One-shot report, changes nothing.
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
Every deliberate ponytail shortcut is marked with a `ponytail:` comment naming
its ceiling and upgrade path. This collects them into one ledger so a deferral
can't quietly become permanent.

## Scan

Grep the repo for comment markers, skipping `node_modules`, `.git`, and build
output:

`grep -rnE '(#|//) ?ponytail:' .`  (add other comment prefixes if your stack uses them)

Each hit is one ledger row. The comment prefix keeps prose that merely mentions
the convention out of the ledger.

## Output

One row per marker, grouped by file:

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.`

The convention is `ponytail: <ceiling>, <upgrade path>`, so pull the ceiling
and the trigger straight from the comment. Want an owner per row too? add
`git blame -L<line>,<line>`.

Flag the rot risk: any `ponytail:` comment that names no upgrade path or
trigger gets a `no-trigger` tag, those are the ones that silently rot.

End with `<N> markers, <M> with no trigger.` Nothing found: `No ponytail: debt. Clean ledger.`

## Boundaries

Reads and reports only, changes nothing. To persist it, ask and it writes the
ledger to a file (e.g. `PONYTAIL-DEBT.md`). One-shot. "stop ponytail-debt" or
"normal mode" to revert.
