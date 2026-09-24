# Claude Handoff Tool Documentation

> **Provenance (vendored 2026-09-24).** Copied from
> `github.com/mattpocock/skills` @ `main`,
> `skills/in-progress/claude-handoff/SKILL.md`, by Matt Pocock. Vendored
> rather than plugin-installed, for the same reason `grill-me` and
> `ponytail` are pinned in-repo elsewhere in this file's own history: a
> skill steers a future session's behavior, so its text must not drift
> under this repo without a diff. The sibling `agents/openai.yaml` is
> vendored alongside it, verbatim, for fidelity to the upstream package
> shape even though nothing in this session's runtime reads it.
>
> **THE UPSTREAM MECHANISM DOES NOT EXIST IN THIS ENVIRONMENT, AND THAT IS
> STATED HERE RATHER THAN SILENTLY REINTERPRETED.** The upstream skill's
> "Core Function" launches a new background agent via a literal shell
> command, `claude --bg --name "<name>" "<summary>"` — a CLI flag from
> Matt Pocock's own tool setup that this session's Claude Code build does
> not ship; there is no `--bg` flag here, and `claude agents` is not a
> command this environment recognises either. Treating the upstream text
> as if it described a real local command here would silently fail or,
> worse, get "fixed" into something the author never wrote. The real
> equivalents, in order of how directly each matches "spin up a fresh
> agent with this prompt and return immediately":
>
> 1. **`mcp__Claude_Code_Remote__create_session`** (when the Claude Code
>    Remote MCP server is connected) — creates a genuinely separate
>    session with a supplied initial prompt, in the current environment or
>    a named one. This is the real analogue of `claude --bg --name`.
> 2. **A committed handoff document** that a future session's own
>    `CLAUDE.md` points a reader at first. This repo already does this
>    extensively (`docs/SESSION-HANDOFF-*.md`, `docs/Q1-HANDOFF.md`,
>    `docs/Q4-COMPLETE-RECORD.md`, `docs/Q3-COMPLETE-RECORD.md`) and it is
>    the cheaper, review-friendly default: no session is spawned, no API
>    cost is spent starting one, and a human decides when — and whether —
>    to pick it up.
>
> **Default to (2) unless the person explicitly asks to spawn a running
> background session right now.** Spawning one is a consequential,
> cost-incurring action (it starts making its own tool calls immediately)
> and must never happen silently just because a handoff was written. When
> (2) is the target, write the doc following this repo's own existing
> handoff-file convention if one exists (see the pointers in `CLAUDE.md`'s
> own opening section) rather than inventing a new shape.

This tool enables conversation handoffs to fresh background agents. Here are the key points:

**Core Function:**
The handoff creates a summary of the current conversation and launches a new background agent with that summary as its prompt using `claude --bg --name "<descriptive name>" "<handoff summary>"`.

**Key Requirements:**
- Always include a descriptive name via `-n`/`--name` flag (examples: "Fix login bug")
- The new agent starts in the current working directory and returns immediately
- Users manage background agents via `claude agents` command

**Summary Content Guidelines:**
- Avoid duplicating content already in artifacts (specs, plans, ADRs, issues, commits, diffs)—reference them by path or URL instead
- Include a "suggested skills" section indicating which tools the next agent should utilize
- Redact sensitive data like API keys, passwords, and personally identifiable information
- If users provided arguments describing the next session's focus, tailor the summary accordingly

**Workflow:**
The handoff summary becomes the foundation for the background agent's prompt, allowing seamless continuation of work without manual context transfer.
