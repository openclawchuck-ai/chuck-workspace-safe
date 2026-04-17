#!/bin/bash
set -euo pipefail

OPENCLAW_BIN="/home/chuck/.nvm/versions/node/v22.22.2/bin/openclaw"

echo "== Gateway status =="
"$OPENCLAW_BIN" gateway status || true

echo
echo "== OpenClaw status =="
"$OPENCLAW_BIN" status || true

echo
echo "== Recent backup files =="
ls -lt "$HOME/Backups/openclaw" 2>/dev/null | head -n 5 || echo "No backup directory found"

echo
echo "== Git backup repo status =="
cd "$HOME/repos/chuck-workspace-safe" 2>/dev/null || {
  echo "Safe workspace repo not found"
  exit 0
}
git status --short || true
git log --oneline -n 3 || true
