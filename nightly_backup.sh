#!/bin/bash
set -euo pipefail

OPENCLAW_BIN="/home/chuck/.nvm/versions/node/v22.22.2/bin/openclaw"
BACKUP_DIR="$HOME/Backups/openclaw"
SYNC_SCRIPT="$HOME/.openclaw/workspace/scripts/sync_workspace_safe.sh"
TIMESTAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
SUPPLEMENTAL_ARCHIVE="$BACKUP_DIR/${TIMESTAMP}-supplemental-system-backup.tar.gz"
CRONTAB_SNAPSHOT="$BACKUP_DIR/${TIMESTAMP}-crontab.txt"
DEPENDENCY_SNAPSHOT_DIR="$BACKUP_DIR/${TIMESTAMP}-dependency-snapshot"
MANIFEST="$BACKUP_DIR/${TIMESTAMP}-manifest.txt"

SUPPLEMENTAL_PATHS=(
  "$HOME/bin"
  "$HOME/repos"
  "$HOME/.secrets"
  "$HOME/previews"
  "$HOME/.config/systemd/user"
  "$HOME/.bashrc"
  "$HOME/.profile"
  "$HOME/.gitconfig"
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

echo "==> Capturing dependency snapshot"
mkdir -p "$DEPENDENCY_SNAPSHOT_DIR"/venvs

{
  date -u
  uname -a
} > "$DEPENDENCY_SNAPSHOT_DIR/system.txt" 2>/dev/null || true

if [[ -f /etc/os-release ]]; then
  cp /etc/os-release "$DEPENDENCY_SNAPSHOT_DIR/os-release.txt"
fi

{
  command -v openclaw || true
  "$OPENCLAW_BIN" --version || true
  command -v node || true
  node --version || true
  command -v npm || true
  npm --version || true
  command -v pnpm || true
  pnpm --version || true
  command -v python3 || true
  python3 --version || true
} > "$DEPENDENCY_SNAPSHOT_DIR/runtime-tools.txt" 2>&1 || true

npm list -g --depth=0 --json > "$DEPENDENCY_SNAPSHOT_DIR/npm-global.json" 2>/dev/null || true
python3 -m pip freeze --user > "$DEPENDENCY_SNAPSHOT_DIR/pip-user-requirements.txt" 2>/dev/null || true
apt-mark showmanual > "$DEPENDENCY_SNAPSHOT_DIR/apt-manual.txt" 2>/dev/null || true
dpkg-query -W -f='${binary:Package}\t${Version}\n' > "$DEPENDENCY_SNAPSHOT_DIR/dpkg-packages.tsv" 2>/dev/null || true

if [[ -d "$HOME/.venvs" ]]; then
  for venv_dir in "$HOME/.venvs"/*; do
    [[ -d "$venv_dir" ]] || continue
    venv_name="$(basename "$venv_dir")"
    out_dir="$DEPENDENCY_SNAPSHOT_DIR/venvs/$venv_name"
    mkdir -p "$out_dir"

    if [[ -f "$venv_dir/pyvenv.cfg" ]]; then
      cp "$venv_dir/pyvenv.cfg" "$out_dir/pyvenv.cfg"
    fi

    if [[ -x "$venv_dir/bin/python3" ]]; then
      "$venv_dir/bin/python3" -m pip freeze > "$out_dir/requirements.txt" 2>/dev/null || true
    fi
  done
fi

if [[ -d "$HOME/bin" ]]; then
  find "$HOME/bin" -maxdepth 1 -type f -printf '%f\n' | sort > "$DEPENDENCY_SNAPSHOT_DIR/home-bin-files.txt"
fi

echo "==> Creating supplemental system archive"
tar -czf "$SUPPLEMENTAL_ARCHIVE" "${EXISTING_PATHS[@]}" "$CRONTAB_SNAPSHOT" "$DEPENDENCY_SNAPSHOT_DIR"

echo "==> Writing backup manifest"
{
  echo "timestamp_utc=$TIMESTAMP"
  echo "openclaw_root=$HOME/.openclaw"
  echo "supplemental_archive=$SUPPLEMENTAL_ARCHIVE"
  echo "crontab_snapshot=$CRONTAB_SNAPSHOT"
  echo "dependency_snapshot=$DEPENDENCY_SNAPSHOT_DIR"
  printf 'included_path=%s\n' "${EXISTING_PATHS[@]}"
  sha256sum "$SUPPLEMENTAL_ARCHIVE"
} > "$MANIFEST"

echo "==> Syncing safe workspace to Git"
"$SYNC_SCRIPT"

echo "==> Creating encrypted offsite-ready backup bundle"
bash "$HOME/.openclaw/workspace/scripts/harden_backup_offsite.sh" || true

echo "==> Nightly backup complete"
echo "Supplemental archive: $SUPPLEMENTAL_ARCHIVE"
echo "Crontab snapshot: $CRONTAB_SNAPSHOT"
echo "Manifest: $MANIFEST"
