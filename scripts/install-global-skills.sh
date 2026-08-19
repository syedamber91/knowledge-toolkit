#!/usr/bin/env bash
#
# Install this repo's vendored third-party skills globally for Claude Code, so
# they load in EVERY project rather than only inside knowledge-toolkit.
#
#   ./scripts/install-global-skills.sh              # skills + ponytail session hooks
#   ./scripts/install-global-skills.sh --no-hooks   # skills only, leave settings.json alone
#
# Idempotent: re-run after `git pull` to refresh. Backs up settings.json before
# touching it. See "Skill precedence" in CLAUDE.md for why these are primary.
#
# NOTE: this covers Claude Code only. claude.ai chat skills cannot be installed
# from a shell — see scripts/build-chat-skill-bundle.sh.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_SRC="$REPO_ROOT/.claude/skills"
SKILLS_DEST="$CLAUDE_DIR/skills"
HOOKS_SRC="$REPO_ROOT/.claude/hooks/ponytail"
HOOKS_DEST="$CLAUDE_DIR/hooks/ponytail"
SETTINGS="$CLAUDE_DIR/settings.json"

WIRE_HOOKS=1
[ "${1:-}" = "--no-hooks" ] && WIRE_HOOKS=0

SKILLS=(ponytail ponytail-review ponytail-audit ponytail-debt ponytail-gain ponytail-help last30days)

echo "==> installing skills into $SKILLS_DEST"
mkdir -p "$SKILLS_DEST"
for s in "${SKILLS[@]}"; do
    if [ ! -d "$SKILLS_SRC/$s" ]; then
        echo "    !! missing $SKILLS_SRC/$s — skipping" >&2
        continue
    fi
    rm -rf "${SKILLS_DEST:?}/$s"
    cp -R "$SKILLS_SRC/$s" "$SKILLS_DEST/$s"
    echo "    $s"
done

if [ "$WIRE_HOOKS" -eq 0 ]; then
    echo "==> --no-hooks: leaving $SETTINGS untouched"
    echo "done."
    exit 0
fi

if ! command -v node >/dev/null 2>&1; then
    echo "==> node not found; skipping hooks (skills still work, just not always-on)" >&2
    echo "done."
    exit 0
fi

echo "==> installing ponytail session hooks into $HOOKS_DEST"
mkdir -p "$HOOKS_DEST"
cp "$HOOKS_SRC"/*.js "$HOOKS_DEST"/

echo "==> wiring hooks into $SETTINGS"
HOOKS_DEST="$HOOKS_DEST" SETTINGS="$SETTINGS" python3 - <<'PY'
import json, os, pathlib, shutil, sys

settings = pathlib.Path(os.environ["SETTINGS"])
hooks_dir = os.environ["HOOKS_DEST"]

data = {}
if settings.exists():
    shutil.copy2(settings, settings.with_suffix(".json.bak"))
    try:
        data = json.loads(settings.read_text())
    except json.JSONDecodeError:
        sys.exit(f"!! {settings} is not valid JSON; refusing to overwrite. Fix it or re-run with --no-hooks.")

wanted = {
    "SessionStart": ("startup|resume|clear|compact", "ponytail-activate.js", "Loading ponytail mode..."),
    "SubagentStart": (None, "ponytail-subagent.js", "Loading ponytail mode..."),
    "UserPromptSubmit": (None, "ponytail-mode-tracker.js", "Tracking ponytail mode..."),
}

hooks = data.setdefault("hooks", {})
for event, (matcher, script, msg) in wanted.items():
    cmd = f'node "{hooks_dir}/{script}"'
    entries = hooks.setdefault(event, [])
    # idempotent: drop any prior ponytail entry for this event before re-adding
    for entry in entries:
        entry["hooks"] = [h for h in entry.get("hooks", []) if script not in h.get("command", "")]
    entries[:] = [e for e in entries if e.get("hooks")]
    block = {"hooks": [{"type": "command", "command": cmd, "timeout": 5, "statusMessage": msg}]}
    if matcher:
        block["matcher"] = matcher
    entries.append(block)

# ponytail intensity default: full (see CLAUDE.md "Skill precedence")
data.setdefault("env", {}).setdefault("PONYTAIL_DEFAULT_MODE", "full")

settings.parent.mkdir(parents=True, exist_ok=True)
settings.write_text(json.dumps(data, indent=2) + "\n")
print(f"    wired 3 hooks; PONYTAIL_DEFAULT_MODE=full")
PY

echo "done. Restart Claude Code (or /clear) to pick up the hooks."
