---
name: ponytail-help
description: >
  Quick-reference card for all ponytail modes, skills, and commands.
  One-shot display, not a persistent mode. Trigger: /ponytail-help,
  "ponytail help", "what ponytail commands", "how do I use ponytail".
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

# Ponytail Help

Display this reference card when invoked. One-shot, do NOT change mode,
write flag files, or persist anything.

## Levels

| Level | Trigger | What change |
|-------|---------|-------------|
| **Lite** | `/ponytail lite` | Build what's asked, name the lazier alternative in one line. |
| **Full** | `/ponytail` | The ladder enforced: YAGNI → stdlib → native → one line → minimum. Default. |
| **Ultra** | `/ponytail ultra` | YAGNI extremist. Deletion before addition. Challenges requirements before building. |

Level sticks until changed or session end.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| **ponytail** | `/ponytail` | Lazy mode itself. Simplest solution that works. |
| **ponytail-review** | `/ponytail-review` | Over-engineering review: `L42: yagni: factory, one product. Inline.` |
| **ponytail-audit** | `/ponytail-audit` | Whole-repo over-engineering audit: ranked list of what to delete. |
| **ponytail-debt** | `/ponytail-debt` | Harvest `ponytail:` shortcut comments into a tracked ledger. |
| **ponytail-gain** | `/ponytail-gain` | Measured-impact scoreboard: less code, less cost, more speed. |
| **ponytail-help** | `/ponytail-help` | This card. |

Codex uses `@ponytail`, `@ponytail-review`, and `@ponytail-help`; Claude Code
and OpenCode use the slash-command forms above (OpenCode ships all six as
slash commands).

## Deactivate

Say "stop ponytail" or "normal mode". Resume anytime with `/ponytail`.
`/ponytail off` also works.

## Configure Default Mode

Default mode = `full`, auto-active every session. Change it:

**Environment variable** (highest priority):
```bash
export PONYTAIL_DEFAULT_MODE=ultra
```

**Config file** (`~/.config/ponytail/config.json`, Windows: `%APPDATA%\ponytail\config.json`):
```json
{ "defaultMode": "lite" }
```

Set `"off"` to disable auto-activation on session start, activate manually
with `/ponytail` when wanted.

Resolution: env var > config file > `full`.

## Update

Enable auto-update once: open `/plugin`, go to Marketplaces, pick ponytail, Enable auto-update. Claude Code then pulls new versions at startup (run `/reload-plugins` when it prompts). Manual refresh: `/plugin marketplace update ponytail` then `/reload-plugins`.

If `/plugin` is not recognized, your Claude Code is out of date. Update it (`npm install -g @anthropic-ai/claude-code@latest`, or `brew upgrade claude-code`) and restart. Other hosts use their own update flow.

## More

Full docs + examples: https://github.com/DietrichGebert/ponytail
