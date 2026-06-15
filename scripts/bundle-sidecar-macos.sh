#!/usr/bin/env bash
# Bundle french-reader-engine for macOS (PyInstaller one-file binary).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM="${1:-macos-arm64}"
OUTPUT_DIR="${2:-${ROOT}/dist/sidecar-macos}"

log() { printf '[bundle-sidecar-macos] %s\n' "$*"; }

command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || {
  echo "python not found" >&2
  exit 1
}
PYTHON="$(command -v python3 2>/dev/null || command -v python)"

log "Syncing plugin version (${PLATFORM})..."
"$PYTHON" "${ROOT}/scripts/sync-plugin-version.py" --platform "${PLATFORM}"

ENGINE_DIR="${ROOT}/extensions/french-reader-engine"
VENV_DIR="${ROOT}/dist/build-venv-macos-${PLATFORM}"
SPEC="${ROOT}/packaging/macos/pyinstaller-engine.spec"
BUILD_WORK="${ROOT}/dist/pyinstaller-work-macos-${PLATFORM}"
BUILD_DIST="${ROOT}/dist/pyinstaller-dist-macos-${PLATFORM}"

if [[ ! -d "${VENV_DIR}" ]]; then
  log "Creating build venv: ${VENV_DIR}"
  "$PYTHON" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip wheel >/dev/null
pip install pyinstaller >/dev/null
pip install -e "${ENGINE_DIR}[bubble]" >/dev/null

log "Running PyInstaller..."
pyinstaller "${SPEC}" --noconfirm --clean --workpath "${BUILD_WORK}" --distpath "${BUILD_DIST}"

BUILT="${BUILD_DIST}/french-reader-engine"
[[ -f "${BUILT}" ]] || { echo "PyInstaller output missing: ${BUILT}" >&2; exit 1; }

mkdir -p "${OUTPUT_DIR}"
cp -f "${BUILT}" "${OUTPUT_DIR}/french-reader-engine"
chmod +x "${OUTPUT_DIR}/french-reader-engine"
log "Engine binary: ${OUTPUT_DIR}/french-reader-engine"
