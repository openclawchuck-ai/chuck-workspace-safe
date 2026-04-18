#!/bin/bash
set -euo pipefail

BASE_DIR="$HOME/repos/chuck-observability"
LOG_DIR="$BASE_DIR/logs"
SCRIPT_DIR="$BASE_DIR/scripts"
CRON_RUNS_DIR="$HOME/.openclaw/cron/runs"
OUT_JSON="$LOG_DIR/cron_runs_latest.json"

mkdir -p "$LOG_DIR"

python3 - <<'PY'
import json
from pathlib import Path

runs_dir = Path.home() / ".openclaw" / "cron" / "runs"
out_path = Path.home() / "repos" / "chuck-observability" / "logs" / "cron_runs_latest.json"
entries = []

for path in sorted(runs_dir.glob("*.jsonl")):
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

entries.sort(key=lambda e: e.get("ts", 0))
out_path.write_text(json.dumps({"entries": entries}, indent=2))
print(f"Wrote {out_path}")
PY

python3 "$SCRIPT_DIR/collect_usage.py"
python3 "$SCRIPT_DIR/summarize_usage.py"
