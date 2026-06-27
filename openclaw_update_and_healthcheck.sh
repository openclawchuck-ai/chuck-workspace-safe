#!/usr/bin/env bash
set -u

export PATH="/home/chuck/.nvm/versions/node/v22.22.2/bin:/home/chuck/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
OPENCLAW="/home/chuck/.nvm/versions/node/v22.22.2/bin/openclaw"
TG_POST="/home/chuck/bin/tg_post"
CHAT_ID="-1003843810073"
THREAD_ID="2"
STAMP="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="/home/chuck/.openclaw/workspace/healthchecks/openclaw-update-${STAMP}"
mkdir -p "$RUN_DIR"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$RUN_DIR/run.log"
}

run_cmd() {
  local name="$1"
  shift
  log "START ${name}: $*"
  {
    printf '$'
    for arg in "$@"; do printf ' %q' "$arg"; done
    printf '\n\n'
    "$@"
  } >"$RUN_DIR/${name}.out" 2>"$RUN_DIR/${name}.err"
  local rc=$?
  log "END ${name}: rc=${rc}"
  return "$rc"
}

run_shell() {
  local name="$1"
  local cmd="$2"
  log "START ${name}: ${cmd}"
  bash -lc "$cmd" >"$RUN_DIR/${name}.out" 2>"$RUN_DIR/${name}.err"
  local rc=$?
  log "END ${name}: rc=${rc}"
  return "$rc"
}

post() {
  local msg="$1"
  if command -v egress_scan >/dev/null 2>&1; then
    local scan
    scan="$(egress_scan "$msg" 2>/dev/null || true)"
    if printf '%s' "$scan" | grep -Eq 'BLOCK|REDACT'; then
      msg="OpenClaw update/healthcheck finished, but I held back the detailed Telegram summary because the local egress scanner flagged it. Log path: ${RUN_DIR}"
    fi
  fi
  "$TG_POST" "$CHAT_ID" "$THREAD_ID" "$msg" >/dev/null 2>&1 || true
}

log "OpenClaw update + healthcheck started"
run_cmd "pre_update_version" "$OPENCLAW" --version
run_cmd "pre_update_status" "$OPENCLAW" update status --json

UPDATE_RC=0
run_cmd "update" "$OPENCLAW" update --yes --json || UPDATE_RC=$?

if [ "$UPDATE_RC" -ne 0 ]; then
  log "Update returned rc=${UPDATE_RC}; attempting post-update repair diagnostics only"
  run_cmd "update_repair" "$OPENCLAW" update repair || true
fi

sleep 8

run_cmd "post_update_version" "$OPENCLAW" --version
run_cmd "update_status" "$OPENCLAW" update status --json
run_cmd "status" "$OPENCLAW" status --json
run_cmd "gateway_status_deep" "$OPENCLAW" gateway status --deep
run_cmd "health" "$OPENCLAW" health
run_cmd "doctor_lint" "$OPENCLAW" doctor --lint --deep --json
run_cmd "security_audit_deep" "$OPENCLAW" security audit --deep --json
run_cmd "channels_status_probe" "$OPENCLAW" channels status --json --probe --timeout 15000
run_cmd "models_status" "$OPENCLAW" models status --json
run_cmd "agents_list" "$OPENCLAW" agents list --json --bindings
run_cmd "plugins_list" "$OPENCLAW" plugins list --json
run_cmd "skills_list" "$OPENCLAW" skills list --json
run_cmd "cron_list" "$OPENCLAW" cron list --json
run_cmd "tasks_list" "$OPENCLAW" tasks list --json
run_cmd "mcp_list" "$OPENCLAW" mcp list --json
run_cmd "backup_list" "$OPENCLAW" backup list --json

run_shell "systemd_gateway" "systemctl --user status openclaw-gateway.service --no-pager"
run_shell "systemd_failed" "systemctl --user --failed --no-pager"
run_shell "listening_ports" "ss -ltnup"
run_shell "disk_space" "df -h / /home /tmp 2>/dev/null || df -h"
run_shell "memory" "free -h"
run_shell "wsl_os" "uname -a && cat /etc/os-release"
run_shell "tailscale_status" "tailscale status --json"
run_shell "gdrive_smoke" "/home/chuck/bin/gdrive_tool.py list"
run_shell "gog_version" "gog --version"
run_shell "ollama_health" "curl -fsS http://127.0.0.1:11434/api/tags"

python3 - "$RUN_DIR" "$UPDATE_RC" >"$RUN_DIR/summary.txt" <<'PY'
import json, pathlib, sys, re
run_dir = pathlib.Path(sys.argv[1])
update_rc = int(sys.argv[2])

def read(name, stream="out"):
    p = run_dir / f"{name}.{stream}"
    return p.read_text(errors="replace") if p.exists() else ""

def json_after_cmd(text):
    # command files start with "$ ..." then a blank line
    payload = text.split("\n\n", 1)[1] if "\n\n" in text else text
    try:
        return json.loads(payload)
    except Exception:
        return None

pre_v = read("pre_update_version").strip().splitlines()[-1:] or ["unknown"]
post_v = read("post_update_version").strip().splitlines()[-1:] or ["unknown"]
upd_status = json_after_cmd(read("update_status")) or {}
status = json_after_cmd(read("status")) or {}
doctor = json_after_cmd(read("doctor_lint")) or {}
security = json_after_cmd(read("security_audit_deep")) or {}
channels = json_after_cmd(read("channels_status_probe")) or {}
models = json_after_cmd(read("models_status")) or {}

doctor_findings = doctor.get("findings") or doctor.get("issues") or []
sec_findings = security.get("findings") or security.get("issues") or []

gateway = status.get("gateway", {})
gw_service = status.get("gatewayService", {})
node_service = status.get("nodeService", {})
tasks = status.get("tasks", {})

channel_count = 0
channel_bad = []
if isinstance(channels, dict):
    vals = channels.get("channels") or channels.get("accounts") or channels.get("status") or []
    if isinstance(vals, dict):
        iterable = vals.items()
    elif isinstance(vals, list):
        iterable = enumerate(vals)
    else:
        iterable = []
    for k, v in iterable:
        channel_count += 1
        blob = json.dumps(v, default=str).lower()
        if any(word in blob for word in ["error", "expired", "missing", "failed", "unauthorized"]):
            channel_bad.append(str(k))

latest = (upd_status.get("update") or {}).get("registry", {}).get("latestVersion") or upd_status.get("availability", {}).get("latestVersion")
available = (upd_status.get("availability") or {}).get("available")
summary = []
summary.append("OpenClaw update + systems test complete.")
summary.append(f"Version: {pre_v[0]} → {post_v[0]}" + (f" (latest stable: {latest})" if latest else ""))
summary.append(f"Update result: {'OK' if update_rc == 0 else 'returned rc=' + str(update_rc)}")
summary.append(f"Gateway: {'reachable' if gateway.get('reachable') else 'check needed'}; service {gw_service.get('runtimeShort') or gw_service.get('runtime', {}).get('status', 'unknown')}; bind {((read('gateway_status_deep') or '').find('Loopback-only') >= 0 and 'loopback') or gateway.get('urlSource', 'unknown')}")
summary.append(f"Agents: {len((status.get('agents') or {}).get('agents') or [])}; active tasks: {(tasks or {}).get('active', 'unknown')}; task failures: {(tasks or {}).get('failures', 'unknown')}")
summary.append(f"Node service: {node_service.get('runtimeShort') or node_service.get('runtime', {}).get('status', 'unknown')}")
summary.append(f"Doctor findings: {len(doctor_findings)}; security findings: {len(sec_findings)}")
if channel_count:
    summary.append(f"Channels probed: {channel_count}" + (f"; attention: {', '.join(channel_bad[:5])}" if channel_bad else "; no obvious probe failures"))

disk = read("disk_space")
root_line = next((ln for ln in disk.splitlines() if re.search(r"\s/$", ln)), "")
if root_line:
    parts = root_line.split()
    if len(parts) >= 5:
        summary.append(f"Disk /: {parts[4]} used ({parts[3]} free)")

failed = read("systemd_failed")
if "0 loaded units listed" in failed or "No failed units" in failed:
    summary.append("Systemd user failed units: none")
elif failed.strip():
    summary.append("Systemd user failed units: check log")

gdrive_err = read("gdrive_smoke", "err").strip()
if gdrive_err:
    summary.append("Google Drive smoke: check log")
else:
    summary.append("Google Drive smoke: OK")

ollama = read("ollama_health")
summary.append("Ollama local endpoint: " + ("OK" if '"models"' in ollama else "check log"))

summary.append(f"Local report: {run_dir}")
print("\n".join(summary))
PY

SUMMARY="$(cat "$RUN_DIR/summary.txt")"
log "$SUMMARY"
post "$SUMMARY"
log "OpenClaw update + healthcheck finished"
