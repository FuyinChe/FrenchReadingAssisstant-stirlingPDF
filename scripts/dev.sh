#!/usr/bin/env bash
# Start Stirling PDF dev stack + French Reader sidecar engine.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
ENGINE_EXT="${ROOT}/extensions/french-reader-engine"
ENABLED="${FRENCH_READER_ENABLED:-true}"

export VITE_FRENCH_READER_ENABLED="${ENABLED}"
export FRENCH_READER_ENABLED="${ENABLED}"

log() { printf '[dev] %s\n' "$*"; }
die() { log "ERROR: $*"; exit 1; }

install_engine_deps() {
  cd "${ENGINE_EXT}"
  if command -v uv >/dev/null 2>&1; then
    uv sync --dev
  else
    log "uv not found — installing engine with pip (recommended: brew install uv)"
    python3 -m pip install -e .
  fi
}

ensure_ocr_ready() {
  if [[ "${ENABLED}" != "true" ]]; then
    return 0
  fi
  if ! command -v tesseract >/dev/null 2>&1; then
    log "Tesseract not found — running setup-ocr.sh ..."
    "${ROOT}/scripts/setup-ocr.sh" || log "WARN: setup-ocr failed; OCR may not work until Tesseract is installed"
  fi
  install_engine_deps
}

[[ -d "${STIRLING}" ]] || { log "Initializing submodule..."; git -C "${ROOT}" submodule update --init --recursive; }

command -v task >/dev/null 2>&1 || die "Task not found. Install: brew install go-task (https://taskfile.dev/installation/)"

if [[ ! -f "${ROOT}/.extensions-installed" ]]; then
  log "Extensions not installed — running install-extensions.sh"
  "${ROOT}/scripts/install-extensions.sh"
fi

cleanup() {
  log "Stopping background services..."
  for pid in $(jobs -p); do
    kill "${pid}" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

if [[ "${ENABLED}" == "true" ]]; then
  log "Starting French Reader engine on :5002 ..."
  (
    ensure_ocr_ready
    if command -v uv >/dev/null 2>&1; then
      uv run uvicorn french_reader.main:app --host 0.0.0.0 --port 5002 --reload
    else
      python3 -m uvicorn french_reader.main:app --host 0.0.0.0 --port 5002 --reload
    fi
  ) &
fi

log "Starting Stirling PDF (task dev) ..."
cd "${STIRLING}"
task dev
