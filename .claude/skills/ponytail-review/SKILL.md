---
name: ponytail-review
description: >
  Code review focused exclusively on over-engineering. Finds what to delete:
  reinvented standard library, unneeded dependencies, speculative abstractions,
  dead flexibility. One line per finding: location, what to cut, what replaces
  it. Use when the user says "review for over-engineering", "what can we
  delete", "is this over-engineered", "simplify review", or invokes
  /ponytail-review. Complements correctness-focused review, this one only
  hunts complexity.
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
Review diffs for unnecessary complexity. One line per finding: location, what
to cut, what replaces it. The diff's best outcome is getting shorter.

## Format

`L<line>: <tag> <what>. <replacement>.`, or `<file>:L<line>: ...` for
multi-file diffs.

Tags:

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

## Examples

❌ "This EmailValidator class might be more complex than necessary, have you
considered whether all these validation rules are needed at this stage?"

✅ `L12-38: stdlib: 27-line validator class. "@" in email, 1 line, real validation is the confirmation mail.`

✅ `L4: native: moment.js imported for one format call. Intl.DateTimeFormat, 0 deps.`

✅ `repo.py:L88: yagni: AbstractRepository with one implementation. Inline it until a second one exists.`

✅ `L52-71: delete: retry wrapper around an idempotent local call. Nothing replaces it.`

✅ `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`

## Scoring

End with the only metric that matters: `net: -<N> lines possible.`

If there is nothing to cut, say `Lean already. Ship.` and stop.

## Boundaries

Scope: over-engineering and complexity only. Correctness bugs, security holes,
and performance are explicitly out of scope. Route them to a normal review
pass, not this one. A single smoke test or `assert`-based
self-check is the ponytail minimum, not bloat, never flag it for deletion.
Does not apply the fixes, only lists them.
"stop ponytail-review" or "normal mode": revert to verbose review style.
