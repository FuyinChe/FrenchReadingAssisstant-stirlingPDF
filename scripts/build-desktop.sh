#!/usr/bin/env bash
# Build Stirling Tauri desktop app with French Reader extensions (M602).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"

export FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_API_URL="${VITE_FRENCH_READER_API_URL:-http://127.0.0.1:5002/french-reader}"

log() { printf '[build-desktop] %s\n' "$*"; }
die() { log "ERROR: $*"; exit 1; }

[[ -d "${STIRLING}/frontend" ]] || die "stirling-upstream missing — run: git submodule update --init --recursive"
command -v task >/dev/null 2>&1 || die "Task not found — brew install go-task"

log "Installing French Reader extensions into Stirling frontend..."
"${ROOT}/scripts/install-extensions.sh"

log "Building Tauri desktop bundle (Stirling task desktop:build)..."
cd "${STIRLING}"
task desktop:build

log "Done. Bundles are under stirling-upstream/frontend/editor/src-tauri/target/release/bundle/"
log "Run ./scripts/desktop-dev.sh for dev (starts sidecar + tauri dev)."
