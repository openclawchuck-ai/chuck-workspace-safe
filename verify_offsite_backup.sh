#!/bin/bash
set -euo pipefail
umask 077

OFFSITE_DIR="${OFFSITE_DIR:-$HOME/Backups/openclaw/offsite}"
KEY_PATH="${OPENCLAW_BACKUP_KEY_PATH:-$HOME/.secrets/openclaw-backup-offsite.key}"

if [[ ! -f "$KEY_PATH" ]]; then
  echo "status=failed"
  echo "reason=missing_key"
  exit 1
fi

bundle="${1:-}"
if [[ -z "$bundle" ]]; then
  bundle="$(
    find "$OFFSITE_DIR" -maxdepth 1 -name '*-openclaw-offsite-bundle.tar.gpg' -type f -printf '%T@ %p\n' |
      sort -nr |
      head -1 |
      cut -d' ' -f2-
  )"
fi

if [[ -z "$bundle" || ! -f "$bundle" ]]; then
  echo "status=failed"
  echo "reason=no_offsite_bundle_found"
  exit 1
fi

checksum="$bundle.sha256"
if [[ ! -f "$checksum" ]]; then
  echo "status=failed"
  echo "reason=missing_checksum"
  echo "bundle=$bundle"
  exit 1
fi

echo "==> Checking checksum"
cd /
sha256sum -c "$checksum" >/dev/null

echo "==> Checking decrypt and payload structure"
payload_list="$(
  gpg --batch --quiet --decrypt \
    --pinentry-mode loopback \
    --passphrase-file "$KEY_PATH" \
    "$bundle" |
    tar -tf -
)"

printf '%s\n' "$payload_list" | grep -q 'openclaw-backup.tar.gz'
printf '%s\n' "$payload_list" | grep -q 'offsite-manifest.txt'

echo "status=ok"
echo "bundle=$bundle"
echo "payload_entries=$(printf '%s\n' "$payload_list" | wc -l)"
