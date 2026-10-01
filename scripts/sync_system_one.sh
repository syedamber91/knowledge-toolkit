#!/usr/bin/env bash
# Single source of truth: plugins/system-one + knowledge/system-one.
# Fan out to: repo .claude/ (cloud + this repo), ~/.claude/ (local global), iCloud Obsidian vault.
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"
P="$R/plugins/system-one"
python3 "$R/scripts/build_system_one_vault.py"
python3 "$R/scripts/check_system_one_vault.py"
for base in "$R/.claude" "$HOME/.claude"; do
  mkdir -p "$base/skills" "$base/agents"
  rsync -a --delete "$P/skills/system-one/" "$base/skills/system-one/"
  cp "$P/agents/system-one-advisor.md" "$base/agents/system-one-advisor.md"
done
ICLOUD="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/System One"
if [ -d "$(dirname "$ICLOUD")" ]; then
  mkdir -p "$ICLOUD"
  rsync -a --delete "$R/knowledge/system-one/" "$ICLOUD/"
  echo "vault -> $ICLOUD"
fi
echo "synced skill+agent to $R/.claude and ~/.claude"
