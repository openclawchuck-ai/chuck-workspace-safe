#!/bin/bash
set -euo pipefail
umask 077

export PATH="/home/chuck/.nvm/versions/node/v22.22.2/bin:/home/chuck/bin:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:/usr/local/bin:/usr/bin:/bin:/snap/bin:${PATH:-}"

BACKUP_DIR="${BACKUP_DIR:-$HOME/Backups/openclaw}"
OFFSITE_DIR="${OFFSITE_DIR:-$BACKUP_DIR/offsite}"
KEY_PATH="${OPENCLAW_BACKUP_KEY_PATH:-$HOME/.secrets/openclaw-backup-offsite.key}"
GOG_ACCOUNT="${GOG_ACCOUNT:-openclawchuck@gmail.com}"
DRIVE_FOLDER_NAME="${OPENCLAW_BACKUP_DRIVE_FOLDER:-OpenClaw Encrypted Backups}"
TIMESTAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
STAGING_DIR="$OFFSITE_DIR/staging-$TIMESTAMP"
STAGING_TAR="$OFFSITE_DIR/${TIMESTAMP}-openclaw-offsite-bundle.tar"
ENCRYPTED_BUNDLE="$STAGING_TAR.gpg"
CHECKSUM_FILE="$ENCRYPTED_BUNDLE.sha256"
STATUS_FILE="$OFFSITE_DIR/${TIMESTAMP}-offsite-status.txt"

mkdir -p "$OFFSITE_DIR" "$(dirname "$KEY_PATH")"
chmod 700 "$(dirname "$KEY_PATH")" 2>/dev/null || true

if [[ ! -f "$KEY_PATH" ]]; then
  openssl rand -base64 48 > "$KEY_PATH"
  chmod 600 "$KEY_PATH"
  echo "created_key=$KEY_PATH" > "$STATUS_FILE"
fi

latest_openclaw="$(
  find "$BACKUP_DIR" -maxdepth 1 -name '*-openclaw-backup.tar.gz' -type f -printf '%T@ %p\n' |
    sort -nr |
    head -1 |
    cut -d' ' -f2-
)"

latest_supplemental="$(
  find "$BACKUP_DIR" -maxdepth 1 -name '*-supplemental-system-backup.tar.gz' -type f -printf '%T@ %p\n' |
    sort -nr |
    head -1 |
    cut -d' ' -f2-
)"

latest_manifest="$(
  find "$BACKUP_DIR" -maxdepth 1 -name '*-manifest.txt' -type f -printf '%T@ %p\n' |
    sort -nr |
    head -1 |
    cut -d' ' -f2-
)"

if [[ -z "$latest_openclaw" || ! -f "$latest_openclaw" ]]; then
  echo "status=failed" >> "$STATUS_FILE"
  echo "reason=no_openclaw_backup_found" >> "$STATUS_FILE"
  exit 1
fi

echo "==> Verifying latest OpenClaw backup"
openclaw backup verify "$latest_openclaw" >/dev/null

if [[ -n "$latest_supplemental" && -f "$latest_supplemental" ]]; then
  gzip -t "$latest_supplemental"
fi

mkdir -p "$STAGING_DIR"
cp "$latest_openclaw" "$STAGING_DIR/"
if [[ -n "$latest_supplemental" && -f "$latest_supplemental" ]]; then
  cp "$latest_supplemental" "$STAGING_DIR/"
fi
if [[ -n "$latest_manifest" && -f "$latest_manifest" ]]; then
  cp "$latest_manifest" "$STAGING_DIR/"
fi

{
  echo "timestamp_utc=$TIMESTAMP"
  echo "source_openclaw_backup=$(basename "$latest_openclaw")"
  if [[ -n "$latest_supplemental" && -f "$latest_supplemental" ]]; then
    echo "source_supplemental_backup=$(basename "$latest_supplemental")"
  fi
  if [[ -n "$latest_manifest" && -f "$latest_manifest" ]]; then
    echo "source_manifest=$(basename "$latest_manifest")"
  fi
  echo "hostname=$(hostname)"
  echo "openclaw_version=$(openclaw --version 2>/dev/null || true)"
} > "$STAGING_DIR/offsite-manifest.txt"

echo "==> Creating offsite staging tar"
tar -C "$STAGING_DIR" -cf "$STAGING_TAR" .

echo "==> Encrypting offsite bundle"
gpg --batch --yes \
  --symmetric \
  --cipher-algo AES256 \
  --pinentry-mode loopback \
  --passphrase-file "$KEY_PATH" \
  --output "$ENCRYPTED_BUNDLE" \
  "$STAGING_TAR"

sha256sum "$ENCRYPTED_BUNDLE" > "$CHECKSUM_FILE"
rm -rf "$STAGING_DIR" "$STAGING_TAR"

upload_status="skipped"
upload_detail="gog_not_available"

if command -v gog >/dev/null 2>&1; then
  set +e
  folder_json="$(gog drive search "name = '$DRIVE_FOLDER_NAME' and mimeType = 'application/vnd.google-apps.folder'" --account "$GOG_ACCOUNT" --json --no-input 2>&1)"
  folder_rc=$?
  set -e

  if [[ $folder_rc -eq 0 ]]; then
    folder_id="$(printf '%s\n' "$folder_json" | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{try{const j=JSON.parse(d); const files=j.files || j.results || j; const f=Array.isArray(files) ? files[0] : null; console.log(f && f.id ? f.id : '')}catch(e){}})")"

    if [[ -z "$folder_id" ]]; then
      set +e
      mkdir_json="$(gog drive mkdir "$DRIVE_FOLDER_NAME" --account "$GOG_ACCOUNT" --json --no-input 2>&1)"
      mkdir_rc=$?
      set -e
      if [[ $mkdir_rc -eq 0 ]]; then
        folder_id="$(printf '%s\n' "$mkdir_json" | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{try{const j=JSON.parse(d); console.log(j.id || (j.file && j.file.id) || '')}catch(e){}})")"
      else
        upload_detail="mkdir_failed"
      fi
    fi

    if [[ -n "$folder_id" ]]; then
      set +e
      gog drive upload "$ENCRYPTED_BUNDLE" --parent "$folder_id" --account "$GOG_ACCOUNT" --json --no-input >/tmp/openclaw-backup-upload.json 2>/tmp/openclaw-backup-upload.err
      upload_rc=$?
      gog drive upload "$CHECKSUM_FILE" --parent "$folder_id" --account "$GOG_ACCOUNT" --json --no-input >/tmp/openclaw-backup-upload-sha.json 2>/tmp/openclaw-backup-upload-sha.err
      checksum_upload_rc=$?
      set -e

      if [[ $upload_rc -eq 0 && $checksum_upload_rc -eq 0 ]]; then
        upload_status="uploaded"
        upload_detail="$DRIVE_FOLDER_NAME"
      else
        upload_status="pending"
        upload_detail="upload_failed_or_auth_stale"
      fi
    else
      upload_status="pending"
      upload_detail="${upload_detail:-folder_unavailable}"
    fi
  else
    upload_status="pending"
    upload_detail="drive_auth_or_search_failed"
  fi
fi

{
  echo "status=ok"
  echo "encrypted_bundle=$ENCRYPTED_BUNDLE"
  echo "checksum_file=$CHECKSUM_FILE"
  echo "upload_status=$upload_status"
  echo "upload_detail=$upload_detail"
} >> "$STATUS_FILE"

echo "==> Offsite hardening complete"
echo "Encrypted bundle: $ENCRYPTED_BUNDLE"
echo "Checksum: $CHECKSUM_FILE"
echo "Upload status: $upload_status ($upload_detail)"
echo "Status file: $STATUS_FILE"
