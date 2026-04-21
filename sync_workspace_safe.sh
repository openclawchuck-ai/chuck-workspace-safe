#!/bin/bash
set -euo pipefail

SRC_MAIN="$HOME/.openclaw/workspace"
SRC_DEV="$HOME/.openclaw/workspace-dev"
SRC_RESEARCH="$HOME/.openclaw/workspace-research"
SRC_OPS="$HOME/.openclaw/workspace-ops"
SRC_DOC="$HOME/.openclaw/workspace-doc"
DST="$HOME/repos/chuck-workspace-safe"
TOOLING_DST="$DST/tooling"

mkdir -p "$DST/subagents/dev" "$DST/subagents/research" "$DST/subagents/ops" "$DST/subagents/doc" "$TOOLING_DST"

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
sync_subagent_md "$SRC_DOC" "$DST/subagents/doc"

mkdir -p "$DST/subagents/doc/handoffs" "$DST/subagents/doc/staging"
if [[ -d "$SRC_DOC/handoffs" ]]; then
  rsync -av --include='*/' --include='*.md' --exclude='*' "$SRC_DOC/handoffs/" "$DST/subagents/doc/handoffs/"
fi
if [[ -d "$SRC_DOC/staging" ]]; then
  rsync -av --include='*/' --include='*.md' --include='*.json' --exclude='*' "$SRC_DOC/staging/" "$DST/subagents/doc/staging/"
fi

snapshot_venv() {
  local name="$1"
  local venv_dir="$HOME/.venvs/$name"
  local out_dir="$TOOLING_DST/$name"

  if [[ ! -d "$venv_dir" ]]; then
    return
  fi

  mkdir -p "$out_dir"

  if [[ -f "$venv_dir/pyvenv.cfg" ]]; then
    rsync -av "$venv_dir/pyvenv.cfg" "$out_dir/"
  fi

  if [[ -x "$venv_dir/bin/python3" ]]; then
    "$venv_dir/bin/python3" -m pip freeze > "$out_dir/requirements.txt" || true
  fi
}

snapshot_venv "browser-tool"
snapshot_venv "chuck-doc"
snapshot_venv "gdrive"

cd "$DST"
git add .
if ! git diff --cached --quiet; then
  git commit -m "Nightly workspace sync $(date +%F)"
  git push origin main
else
  echo "No safe workspace changes to commit."
fi
