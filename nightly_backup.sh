#!/bin/bash
set -euo pipefail

OPENCLAW_BIN="/home/chuck/.nvm/versions/node/v22.22.2/bin/openclaw"
BACKUP_DIR="$HOME/Backups/openclaw"
SYNC_SCRIPT="$HOME/.openclaw/workspace/scripts/sync_workspace_safe.sh"

echo "==> Ensuring backup directory exists"
mkdir -p "$BACKUP_DIR"

echo "==> Starting OpenClaw archive backup"
"$OPENCLAW_BIN" backup create --verify --output "$BACKUP_DIR"

echo "==> Syncing safe workspace to Git"
"$SYNC_SCRIPT"

echo "==> Nightly backup complete"
