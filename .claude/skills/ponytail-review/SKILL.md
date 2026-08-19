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
