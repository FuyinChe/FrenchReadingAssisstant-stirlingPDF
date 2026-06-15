#!/usr/bin/env bash
# Build Stirling Tauri .app for portable zip (no dmg/msi/deb, no updater signing).
#
# Usage:
#   ./scripts/build-stirling-desktop-portable.sh              # native (arm64 on Apple Silicon)
#   ./scripts/build-stirling-desktop-portable.sh x86_64-apple-darwin
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
TAURI_DIR="${STIRLING}/frontend/editor"
RUST_TARGET="${1:-}"

log() { printf '[build-stirling-desktop-portable] %s\n' "$*"; }

for cmd in task npx; do
  command -v "${cmd}" >/dev/null 2>&1 || {
    echo "Missing command: ${cmd}" >&2
    exit 1
  }
done

log "Preparing Stirling desktop dependencies (task desktop:prepare)..."
(cd "${STIRLING}" && task desktop:prepare)

TAURI_ARGS=(
  build
  --bundles app
  --verbose
  --config '{"bundle":{"targets":["app"],"createUpdaterArtifacts":false}}'
)

if [[ -n "${RUST_TARGET}" ]]; then
  log "Cross-compiling for ${RUST_TARGET}"
  rustup target add "${RUST_TARGET}" >/dev/null 2>&1 || true
  TAURI_ARGS+=(--target "${RUST_TARGET}")
fi

log "Running: npx tauri ${TAURI_ARGS[*]}"
log "(NOT task desktop:build — portable zip only needs .app)"
(cd "${TAURI_DIR}" && npx tauri "${TAURI_ARGS[@]}")

log "Done. Look for .app under ${TAURI_DIR}/src-tauri/target/*/release/bundle/macos/"
