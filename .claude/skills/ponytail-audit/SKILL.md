---
name: ponytail-audit
description: >
  Whole-repo audit for over-engineering. Like ponytail-review, but scans the
  entire codebase instead of a diff: a ranked list of what to delete, simplify,
  or replace with stdlib/native equivalents. Use when the user says "audit this
  codebase", "audit for over-engineering", "what can I delete from this repo",
  "find bloat", "ponytail-audit", or "/ponytail-audit". One-shot report, does
  not apply fixes.
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
ponytail-review, repo-wide. Scan the whole tree instead of a diff. Rank
findings biggest cut first.

## Tags

Same as ponytail-review:

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

## Hunt

Deps the stdlib or platform already ships, single-implementation interfaces,
factories with one product, wrappers that only delegate, files exporting one
thing, dead flags and config, hand-rolled stdlib.

## Output

One line per finding, ranked: `<tag> <what to cut>. <replacement>. [path]`.
End with `net: -<N> lines, -<M> deps possible.` Nothing to cut: `Lean already. Ship.`

## Boundaries

Scope: over-engineering and complexity only. Correctness bugs, security holes,
and performance are explicitly out of scope. Route them to a normal review
pass. Lists findings, applies nothing. One-shot.
"stop ponytail-audit" or "normal mode" to revert.
