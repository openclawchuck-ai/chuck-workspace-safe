#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 5 ]; then
  echo "usage: $0 <name> <chat_id> <thread_id> <log_dir> <command> [args...]" >&2
  exit 64
fi

name="$1"
chat_id="$2"
thread_id="$3"
log_dir="$4"
shift 4

mkdir -p "$log_dir"

safe_name="$(printf '%s' "$name" | tr -cs 'A-Za-z0-9_.-' '_' | sed 's/^_//; s/_$//')"
stamp="$(date +%Y%m%d-%H%M%S)"
log_file="$log_dir/${safe_name:-cron-report}-$stamp.log"
tmp_out="$(mktemp)"
trap 'rm -f "$tmp_out"' EXIT

set +e
"$@" >"$tmp_out" 2>&1
status=$?
set -e

cp "$tmp_out" "$log_file"

if [ "$status" -eq 0 ]; then
  prefix="$name complete"
else
  prefix="$name FAILED with exit $status"
fi

body="$(cat "$tmp_out")"
if [ -z "$body" ]; then
  body="No output."
fi

max_body_chars=3200
if [ "${#body}" -gt "$max_body_chars" ]; then
  body="$(tail -c "$max_body_chars" "$tmp_out")"
  body="[output trimmed to last $max_body_chars chars]\n$body"
fi

message="$prefix
Log: $log_file

$body"

timeout 120 /home/chuck/bin/tg_post "$chat_id" "$thread_id" "$message"
exit "$status"
