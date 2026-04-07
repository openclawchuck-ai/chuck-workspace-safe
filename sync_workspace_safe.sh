#!/bin/bash
set -euo pipefail

SRC_MAIN="$HOME/.openclaw/workspace"
SRC_DEV="$HOME/.openclaw/workspace-dev"
SRC_RESEARCH="$HOME/.openclaw/workspace-research"
SRC_OPS="$HOME/.openclaw/workspace-ops"
DST="$HOME/repos/chuck-workspace-safe"

mkdir -p "$DST/subagents/dev" "$DST/subagents/research" "$DST/subagents/ops"

rsync -av \
  "$SRC_MAIN/AGENTS.md" \
  "$SRC_MAIN/TOOLS.md" \
  "$SRC_MAIN/TELEGRAM_MAP.md" \
  "$SRC_MAIN/scripts/" \
  "$DST/"

sync_subagent_md() {
  local src_dir="$1"
  local dst_dir="$2"

  mkdir -p "$dst_dir"

  local files=(
    "AGENTS.md"
    "BOOTSTRAP.md"
    "HEARTBEAT.md"
    "IDENTITY.md"
    "SOUL.md"
    "TOOLS.md"
    "USER.md"
  )

  for file in "${files[@]}"; do
    if [[ -f "$src_dir/$file" ]]; then
      rsync -av "$src_dir/$file" "$dst_dir/"
    fi
  done
}

sync_subagent_md "$SRC_DEV" "$DST/subagents/dev"
sync_subagent_md "$SRC_RESEARCH" "$DST/subagents/research"
sync_subagent_md "$SRC_OPS" "$DST/subagents/ops"

cd "$DST"
git add .
if ! git diff --cached --quiet; then
  git commit -m "Nightly workspace sync $(date +%F)"
  git push origin main
else
  echo "No safe workspace changes to commit."
fi
