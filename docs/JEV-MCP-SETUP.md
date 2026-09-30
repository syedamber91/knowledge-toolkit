# Jev MCP — setup for cloud and local sessions

Written 2026-09-30. Server: `@jkudish/jev-mcp`, pinned `0.11.0` in `.mcp.json`
(stdio, needs `TYPESAFE_API_KEY`). Twelve tools: `jev_verify`, `jev_audit`,
`jev_screen`, `jev_noul`, `jev_find`, `jev_rerank`, `jev_classify`,
`jev_decide`, `jev_compare`, `jev_extract`, `jev_review`, `jev_gate`.
When to call which: `.claude/skills/jev-checkpoint/SKILL.md`.

**Advisory only.** Jev gates nothing and never replaces this repo's own
checks (see CLAUDE.md).

## What was measured (cloud session, 2026-09-30)

- The server starts and answers `initialize` / `tools/list` by hand.
- A real tool call was NOT proven: the egress proxy answered 403 to
  `CONNECT api.typesafe.ai:443`. `TYPESAFE_API_KEY` validity is unchecked.
- The session's working directory was `/home/user`, not a repo, so no
  repo's `.mcp.json` was read and no `mcp__jev__*` tool loaded.

## Cloud (claude.ai/code)

1. **Network:** environment settings -> network access -> Custom, add
   `api.typesafe.ai`, keep "include default list". Without it every call
   fails even when the tools load.
2. **Key:** set `TYPESAFE_API_KEY` in the environment's own settings, never
   in chat. Anyone using the environment can read it.
3. **Start a ONE-repo session.** A multi-repo session starts above the
   clones and does not read their `.mcp.json` or hooks. Project servers
   load without an approval prompt there.
4. **Verify:** `ToolSearch "jev"` lists `mcp__jev__*`; call `jev_decide` on a
   trivial choice; `curl -sS "$HTTPS_PROXY/__agentproxy/status"` shows no new
   `api.typesafe.ai` rejection. Negative control: a multi-repo session shows
   no jev tools.

## Local CLI

1. Export `TYPESAFE_API_KEY` in the shell that launches `claude`.
2. Approve the server once: trust the workspace when prompted, or add
   `{"enabledMcpjsonServers": ["jev"]}` to `.claude/settings.local.json`
   (uncommitted) or user settings. Do NOT use `enableAllProjectMcpServers`
   where `.mcp.json` holds another server that must stay gated.
3. **Verify:** `claude mcp list` shows `jev`; `/mcp` shows it connected; make
   one real tool call. Unset the key and confirm the session still works.

## Not done, on purpose

No hooks. A `Stop`/`PreToolUse` hook would send diffs to a third party on
every turn, and an exit-2 hook would turn an advisory tool into a gate.
Revisit only after real calls are proven, and then make it async, advisory
and fail-open.
