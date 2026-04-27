#!/bin/bash
set -euo pipefail

PATTERN='suspicious|malicious|denied command|blocked|prompt injection|redact|security alert'
TMP_MATCHES="$(mktemp)"
trap 'rm -f "$TMP_MATCHES"' EXIT

printf '== Recent suspicious security signals ==
'

FILES=(
  "$HOME/.openclaw/logs/commands.log"
  "$HOME/.openclaw/logs/config-audit.jsonl"
  "$HOME/.openclaw/logs/gateway-restart.log"
)

for file in "${FILES[@]}"; do
  [ -f "$file" ] || continue
  grep -HnEi "$PATTERN" "$file" || true
done |
  python3 - <<'PY2' > "$TMP_MATCHES"
import sys
for line in sys.stdin:
    if len(line) > 600:
        continue
    if '"payloads"' in line or 'finalAssistantRawText' in line or 'finalPromptText' in line:
        continue
    print(line, end='')
PY2

if [ -s "$TMP_MATCHES" ]; then
  tail -n 80 "$TMP_MATCHES"
else
  echo 'No suspicious/malicious/denied/blocked/redacted signals found in the focused security logs.'
  echo
  echo 'Files reviewed:'
  for file in "${FILES[@]}"; do
    [ -f "$file" ] && echo "$file"
  done
fi
