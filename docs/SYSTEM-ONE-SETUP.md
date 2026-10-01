# System One vault + skill + agent — where it lives and how to use it

Built 2026-10-02 from https://docs.typesafe.ai (full `llms-full.txt`, 111 pages) plus
third-party Laya / alternatives / community sources (labelled third-party in the notes).

| Piece | Source of truth | Copies |
|---|---|---|
| Vault (72 notes + Home, Log, 10 topic hubs) | `knowledge/system-one/` | iCloud Obsidian `System One/` |
| Skill `system-one` (self-contained `references/`) | `plugins/system-one/skills/system-one/` | `.claude/skills/`, `~/.claude/skills/` |
| Agent `system-one-advisor` (Opus) | `plugins/system-one/agents/` | `.claude/agents/`, `~/.claude/agents/` |
| Plugin + marketplace | `plugins/system-one/`, `.claude-plugin/marketplace.json` | — |

After editing anything above, run `scripts/sync_system_one.sh` (rebuilds Home/Log/topics,
runs `scripts/check_system_one_vault.py`, fans out the copies).

## Where it works
- **Local, any directory:** `~/.claude/skills/system-one` + `~/.claude/agents/system-one-advisor.md`.
- **Cloud, this repo:** committed `.claude/skills` + `.claude/agents` + `knowledge/system-one/`.
- **Cloud or local, ANY other repo:** add to that repo's `.claude/settings.json`
  (the repo must be reachable from the cloud environment; NOT yet tested in a cloud session):
  ```json
  {"extraKnownMarketplaces":{"knowledge-toolkit":{"source":{"source":"github","repo":"syedamber91/knowledge-toolkit"}}},
   "enabledPlugins":{"system-one@knowledge-toolkit":true}}
  ```
  or run `/plugin marketplace add syedamber91/knowledge-toolkit` then `/plugin install system-one@knowledge-toolkit`.
  The skill's `references/` carry the condensed playbook, so it works without the vault.
- The Jev tools themselves (`mcp__jev__*`) still need the setup in `docs/JEV-MCP-SETUP.md`.

## Tiering (owner's rule)
Sonnet reads and condenses; Opus synthesizes and does retrieval/routing; System One models
make cheap typed judgments; code does anything exact. A subagent cannot spawn subagents, so the
main session dispatches Sonnet readers and calls `system-one-advisor` (Opus).
