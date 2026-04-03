#!/bin/bash
set -euo pipefail

echo "Cleaning old logs..."
find /tmp/openclaw -type f -mtime +7 -delete || true

echo "Cleaning old backups..."
find $HOME/Backups/openclaw -type f -mtime +14 -delete || true

echo "Cleanup complete"
