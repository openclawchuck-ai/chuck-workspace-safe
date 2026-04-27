#!/bin/bash
set -euo pipefail

OPENCLAW_BIN="/home/chuck/.nvm/versions/node/v22.22.2/bin/openclaw"
export OPENCLAW_NO_RESPAWN=1
export CI=1

TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_OUT"' EXIT

"$OPENCLAW_BIN" doctor >"$TMP_OUT" 2>&1 || {
  echo "OpenClaw doctor failed."
  tail -n 80 "$TMP_OUT"
  exit 1
}

python3 - "$TMP_OUT" <<'PY2'
import re, sys
text=open(sys.argv[1], 'r', errors='ignore').read()
text=re.sub(r'\[[0-9;]*[A-Za-z]', '', text)
lines=[ln.rstrip() for ln in text.splitlines()]
out=[]
for ln in lines:
    s=ln.strip()
    if not s:
        if out and out[-1] != '':
            out.append('')
        continue
    if 'OPENCLAW' in s and ('▄▄' in s or '██' in s):
        continue
    if s.startswith('FAQ:') or s.startswith('Troubleshooting:') or s.startswith('Next steps:'):
        continue
    if s.startswith('Need to share?') or s.startswith('Need to debug live?') or s.startswith('Need to test channels?'):
        continue
    out.append(s)
print('
'.join(out).strip())
PY2
