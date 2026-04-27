#!/bin/bash
set -euo pipefail

OPENCLAW_BIN="/home/chuck/.nvm/versions/node/v22.22.2/bin/openclaw"
export OPENCLAW_NO_RESPAWN=1
export CI=1

retry() {
  local n=0 max=2 delay=5
  until "$@"; do
    n=$((n+1))
    if [ "$n" -gt "$max" ]; then
      return 1
    fi
    sleep "$delay"
  done
}

echo "== Gateway status =="
retry "$OPENCLAW_BIN" gateway status || echo "gateway status failed after retries"

echo
echo "== OpenClaw status =="
retry "$OPENCLAW_BIN" status || echo "openclaw status failed after retries"

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
