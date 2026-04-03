#!/bin/bash
set -euo pipefail

echo "== Gateway status =="
openclaw gateway status || true

echo
echo "== OpenClaw status =="
openclaw status || true

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
