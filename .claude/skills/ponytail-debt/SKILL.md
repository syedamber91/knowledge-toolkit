---
name: ponytail-debt
description: >
  Harvest every `ponytail:` comment in the codebase into a debt ledger, so the
  deliberate shortcuts and deferrals ponytail leaves behind get tracked instead
  of rotting into "later means never". Use when the user says "ponytail debt",
  "/ponytail-debt", "what did ponytail defer", "list the shortcuts", "ponytail
  ledger", or "what did we mark to do later". One-shot report, changes nothing.
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
