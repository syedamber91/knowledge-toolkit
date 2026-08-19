#!/usr/bin/env bash
#
# Build upload-ready .zip files for claude.ai chat (Settings -> Capabilities ->
# Skills -> Upload skill). Chat skills CANNOT be installed from a shell — there
# is no API for it — so this produces the artifacts and you upload them once by
# hand. Claude Code is handled separately by scripts/install-global-skills.sh.
#
#   ./scripts/build-chat-skill-bundle.sh     # -> output/chat-skills/*.zip
#
# Only the ponytail skills are built. last30days is deliberately excluded: it
# needs your API keys, node/python3, and your browser cookie store, none of
# which exist in the chat sandbox. See CLAUDE.md "Skill precedence".

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/.claude/skills"
OUT="$REPO_ROOT/output/chat-skills"

SKILLS=(ponytail ponytail-review ponytail-audit ponytail-debt ponytail-gain ponytail-help)

command -v zip >/dev/null 2>&1 || { echo "!! 'zip' not installed" >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT"

for s in "${SKILLS[@]}"; do
    [ -f "$SRC/$s/SKILL.md" ] || { echo "!! missing $SRC/$s/SKILL.md" >&2; continue; }
    staging="$(mktemp -d)"
    mkdir -p "$staging/$s"
    cp "$SRC/$s/SKILL.md" "$staging/$s/SKILL.md"
    ( cd "$staging" && zip -qr "$OUT/$s.zip" "$s" )
    rm -rf "$staging"
    echo "    $s.zip"
done

echo
echo "Built in $OUT"
echo "Upload each at claude.ai -> Settings -> Capabilities -> Skills -> Upload skill."
