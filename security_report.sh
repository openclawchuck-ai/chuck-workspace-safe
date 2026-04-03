#!/bin/bash
set -euo pipefail

LOG_FILE="/tmp/openclaw/openclaw-$(date +%F).log"

echo "== Recent suspicious security signals =="

if [ -f "$LOG_FILE" ]; then
  grep -Ei 'suspicious|malicious|denied|blocked|prompt injection|redact|security alert' "$LOG_FILE" | tail -n 50 || true
else
  echo "No current log file found: $LOG_FILE"
fi
