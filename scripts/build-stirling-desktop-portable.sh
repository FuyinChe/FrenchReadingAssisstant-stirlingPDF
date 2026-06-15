#!/usr/bin/env bash
# Build Stirling Tauri .app for portable zip (no dmg/msi/deb, no updater signing).
#
# Usage:
#   ./scripts/build-stirling-desktop-portable.sh aarch64-apple-darwin
#   ./scripts/build-stirling-desktop-portable.sh x86_64-apple-darwin
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
TAURI_DIR="${STIRLING}/frontend/editor"
TAURI_CONF="${TAURI_DIR}/src-tauri/tauri.conf.json"
RUST_TARGET="${1:?Usage: $0 <aarch64-apple-darwin|x86_64-apple-darwin>}"

log() { printf '[build-stirling-desktop-portable] %s\n' "$*"; }

for cmd in task npx python3; do
  command -v "${cmd}" >/dev/null 2>&1 || {
    echo "Missing command: ${cmd}" >&2
    exit 1
  }
done

log "Preparing Stirling desktop dependencies (task desktop:prepare)..."
(cd "${STIRLING}" && task desktop:prepare)

log "Patching tauri.conf.json for portable build (app-only, no updater pubkey)..."
python3 "${ROOT}/scripts/patch-tauri-portable.py" "${TAURI_CONF}"

log "Building for ${RUST_TARGET}"
rustup target add "${RUST_TARGET}" >/dev/null 2>&1 || true

# Workflow sets CARGO_BUILD_TARGET per matrix row; without matching `tauri --target`
# native arm64 builds can compile to target/release/ while the bundler expects elsewhere.
unset CARGO_BUILD_TARGET

TAURI_ARGS=(
  build
  --target "${RUST_TARGET}"
  --bundles app
  --verbose
  --config '{"bundle":{"targets":["app"],"createUpdaterArtifacts":false}}'
)

log "Running: npx tauri ${TAURI_ARGS[*]}"
log "(NOT task desktop:build — portable zip only needs .app)"
(cd "${TAURI_DIR}" && npx tauri "${TAURI_ARGS[@]}")

log "Done. Look for .app under ${TAURI_DIR}/src-tauri/target/${RUST_TARGET}/release/bundle/macos/"
