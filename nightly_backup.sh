#!/bin/bash
set -euo pipefail

OPENCLAW_BIN="/home/chuck/.nvm/versions/node/v22.22.2/bin/openclaw"
BACKUP_DIR="$HOME/Backups/openclaw"
SYNC_SCRIPT="$HOME/.openclaw/workspace/scripts/sync_workspace_safe.sh"
TIMESTAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
SUPPLEMENTAL_ARCHIVE="$BACKUP_DIR/${TIMESTAMP}-supplemental-system-backup.tar.gz"
CRONTAB_SNAPSHOT="$BACKUP_DIR/${TIMESTAMP}-crontab.txt"
MANIFEST="$BACKUP_DIR/${TIMESTAMP}-manifest.txt"

SUPPLEMENTAL_PATHS=(
  "$HOME/bin"
  "$HOME/repos"
  "$HOME/.secrets"
  "$HOME/previews"
  "/mnt/c/Users/OpenC/obsidian-vault"
)

EXISTING_PATHS=()
for path in "${SUPPLEMENTAL_PATHS[@]}"; do
  if [[ -e "$path" ]]; then
    EXISTING_PATHS+=("$path")
  fi
done

echo "==> Ensuring backup directory exists"
mkdir -p "$BACKUP_DIR"

echo "==> Starting OpenClaw archive backup"
"$OPENCLAW_BIN" backup create --verify --output "$BACKUP_DIR"

echo "==> Capturing crontab snapshot"
crontab -l > "$CRONTAB_SNAPSHOT" 2>/dev/null || true

echo "==> Creating supplemental system archive"
tar -czf "$SUPPLEMENTAL_ARCHIVE" "${EXISTING_PATHS[@]}" "$CRONTAB_SNAPSHOT"

echo "==> Writing backup manifest"
{
  echo "timestamp_utc=$TIMESTAMP"
  echo "openclaw_root=$HOME/.openclaw"
  echo "supplemental_archive=$SUPPLEMENTAL_ARCHIVE"
  echo "crontab_snapshot=$CRONTAB_SNAPSHOT"
  printf 'included_path=%s\n' "${EXISTING_PATHS[@]}"
  sha256sum "$SUPPLEMENTAL_ARCHIVE"
} > "$MANIFEST"

echo "==> Syncing safe workspace to Git"
"$SYNC_SCRIPT"

echo "==> Nightly backup complete"
echo "Supplemental archive: $SUPPLEMENTAL_ARCHIVE"
echo "Crontab snapshot: $CRONTAB_SNAPSHOT"
echo "Manifest: $MANIFEST"
