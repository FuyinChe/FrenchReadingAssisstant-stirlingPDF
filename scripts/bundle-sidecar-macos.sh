#!/usr/bin/env bash
# Bundle french-reader-engine for macOS (PyInstaller onedir + ad-hoc codesign).
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

log "Verifying OpenCV (cv2) before PyInstaller..."
python -c "import cv2; print('opencv', cv2.__version__)"

log "Running PyInstaller..."
pyinstaller "${SPEC}" --noconfirm --clean --workpath "${BUILD_WORK}" --distpath "${BUILD_DIST}"

BUILT_DIR="${BUILD_DIST}/french-reader-engine"
BUILT_BIN="${BUILT_DIR}/french-reader-engine"
[[ -x "${BUILT_BIN}" ]] || { echo "PyInstaller output missing: ${BUILT_BIN}" >&2; exit 1; }

mkdir -p "${OUTPUT_DIR}"
rm -rf "${OUTPUT_DIR}/french-reader-engine"
cp -R "${BUILT_DIR}" "${OUTPUT_DIR}/french-reader-engine"
chmod +x "${OUTPUT_DIR}/french-reader-engine/french-reader-engine"

if command -v codesign >/dev/null 2>&1; then
  log "Ad-hoc codesigning engine bundle..."
  codesign -s - --force --deep "${OUTPUT_DIR}/french-reader-engine/french-reader-engine"
fi

log "Engine bundle: ${OUTPUT_DIR}/french-reader-engine/french-reader-engine"
