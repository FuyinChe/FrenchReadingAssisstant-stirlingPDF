#!/usr/bin/env bash
# Tauri desktop dev with French Reader sidecar (M602).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
ENGINE="${ROOT}/extensions/french-reader-engine"

export FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_API_URL="${VITE_FRENCH_READER_API_URL:-http://127.0.0.1:5002/french-reader}"

log() { printf '[desktop-dev] %s\n' "$*"; }
die() { log "ERROR: $*"; exit 1; }

[[ -d "${STIRLING}/frontend" ]] || die "stirling-upstream missing"
command -v task >/dev/null 2>&1 || die "Task not found"

if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT}/.env"
  set +a
fi

"${ROOT}/scripts/install-extensions.sh"

cleanup() {
  log "Stopping French Reader sidecar..."
  for pid in $(jobs -p); do
    kill "${pid}" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

log "Starting French Reader engine on :5002 ..."
(
  cd "${ENGINE}"
  if command -v uv >/dev/null 2>&1; then
    uv run uvicorn french_reader.main:app --host 127.0.0.1 --port 5002 --reload
  else
    python3 -m uvicorn french_reader.main:app --host 127.0.0.1 --port 5002 --reload
  fi
) &

sleep 2
log "Starting Tauri dev (task desktop:dev)..."
cd "${STIRLING}"
task desktop:dev
