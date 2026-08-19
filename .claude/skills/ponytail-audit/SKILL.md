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
