#!/bin/bash
set -euo pipefail

SRC="$HOME/.openclaw/workspace"
DST="$HOME/repos/chuck-workspace-safe"

mkdir -p "$DST"

rsync -av \
  "$SRC/AGENTS.md" \
  "$SRC/TOOLS.md" \
  "$SRC/TELEGRAM_MAP.md" \
  "$SRC/scripts/" \
  "$DST/"

cd "$DST"
git add .
if ! git diff --cached --quiet; then
  git commit -m "Nightly workspace sync $(date +%F)"
  git push origin main
else
  echo "No safe workspace changes to commit."
fi
