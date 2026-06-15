#!/usr/bin/env bash
# Build macOS portable ZIP: Stirling desktop + French Reader engine + Tesseract.
#
# Usage:
#   ./scripts/build-portable-macos.sh --arch arm64
#   ./scripts/build-portable-macos.sh --arch x64
#   ./scripts/build-portable-macos.sh --arch arm64 --skip-desktop
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCH="arm64"
SKIP_DESKTOP=false
SKIP_ZIP=false
OUTPUT_ROOT="${ROOT}/dist/portable-macos"

log() { printf '[build-portable-macos] %s\n' "$*"; }
die() { log "ERROR: $*"; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arch) ARCH="${2:?}"; shift 2 ;;
    --skip-desktop) SKIP_DESKTOP=true; shift ;;
    --skip-zip) SKIP_ZIP=true; shift ;;
    -h|--help)
      echo "Usage: $0 [--arch arm64|x64] [--skip-desktop] [--skip-zip]"
      exit 0
      ;;
    *) die "Unknown option: $1" ;;
  esac
done

case "${ARCH}" in
  arm64|aarch64) PLATFORM="macos-arm64"; ARCH_LABEL="arm64" ;;
  x64|x86_64|intel) PLATFORM="macos-x64"; ARCH_LABEL="x64" ;;
  *) die "Unsupported --arch ${ARCH} (use arm64 or x64)" ;;
esac

for cmd in git python3 node java cargo task; do
  command -v "${cmd}" >/dev/null 2>&1 || die "Missing command: ${cmd}"
done

PYTHON="$(command -v python3)"
VERSION="$("$PYTHON" -c "import json; print(json.load(open('${ROOT}/extensions/french-reader-version.json'))['version'])")"
BUILD_ID="${VERSION}-$(date -u +%Y%m%d-%H%M%S)"
STAGING_NAME="French-Reading-Assistant-${VERSION}-${PLATFORM}"
STAGING_DIR="${OUTPUT_ROOT}/${STAGING_NAME}"

log "Plugin ${VERSION} (${PLATFORM}, build ${BUILD_ID})"
"$PYTHON" "${ROOT}/scripts/sync-plugin-version.py" --platform "${PLATFORM}" --build-id "${BUILD_ID}"

git -C "${ROOT}" submodule update --init --recursive

export FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_API_URL="${VITE_FRENCH_READER_API_URL:-http://127.0.0.1:5002/french-reader}"
export FRENCH_READER_SKIP_ENGINE_INSTALL="${FRENCH_READER_SKIP_ENGINE_INSTALL:-true}"

chmod +x "${ROOT}"/scripts/*.sh
"${ROOT}/scripts/install-extensions.sh"

log "Bundling French Reader engine..."
"${ROOT}/scripts/bundle-sidecar-macos.sh" "${PLATFORM}" "${STAGING_DIR}/engine"

log "Staging Tesseract..."
"${ROOT}/scripts/fetch-tesseract-macos.sh" "${STAGING_DIR}/tesseract"

mkdir -p "${STAGING_DIR}/app"

if [[ "${SKIP_DESKTOP}" != "true" ]]; then
  if [[ "${ARCH_LABEL}" == "x64" ]]; then
    RUST_TARGET="x86_64-apple-darwin"
  else
    RUST_TARGET="aarch64-apple-darwin"
  fi

  "${ROOT}/scripts/build-stirling-desktop-portable.sh" "${RUST_TARGET}"

  TAURI_TARGET_ROOT="${ROOT}/stirling-upstream/frontend/editor/src-tauri/target"
  BUNDLE_MACOS="${TAURI_TARGET_ROOT}/${RUST_TARGET}/release/bundle/macos"
  APP_SRC="$(find "${BUNDLE_MACOS}" -maxdepth 1 -name '*.app' 2>/dev/null | head -1)"
  if [[ -z "${APP_SRC}" ]]; then
    APP_SRC="$(find "${TAURI_TARGET_ROOT}" -path '*/bundle/macos/*.app' 2>/dev/null | head -1)"
  fi
  if [[ -n "${APP_SRC}" ]]; then
    cp -R "${APP_SRC}" "${STAGING_DIR}/app/"
    log "Copied desktop app: $(basename "${APP_SRC}")"
  else
    log "WARN: No .app found — copy manually into ${STAGING_DIR}/app/"
  fi
else
  log "Skip desktop — place Stirling .app in ${STAGING_DIR}/app/"
fi

cp -f "${ROOT}/packaging/macos/Start French Reading Assistant.command" "${STAGING_DIR}/"
cp -f "${ROOT}/packaging/macos/README.txt" "${STAGING_DIR}/"
chmod +x "${STAGING_DIR}/Start French Reading Assistant.command"

"$PYTHON" -c "
import json
from pathlib import Path
info = json.loads(Path('${ROOT}/extensions/french-reader-engine/src/french_reader/_plugin_version.json').read_text())
Path('${STAGING_DIR}/VERSION.txt').write_text(
    'French Reading Assistant (plugin)\n'
    f\"Version: {info['version']}\n\"
    f\"Build ID: {info['build']['id']}\n\"
    f\"Platform: {info['build']['platform']}\n\"
    f\"Built at: {info['build']['builtAt']}\n\"
    'Stirling PDF: https://github.com/Stirling-Tools/Stirling-PDF\n',
    encoding='utf-8',
)
"

if [[ "${SKIP_ZIP}" != "true" ]]; then
  ZIP_PATH="${OUTPUT_ROOT}/${STAGING_NAME}.zip"
  rm -f "${ZIP_PATH}"
  log "Creating zip: ${ZIP_PATH}"
  (cd "${OUTPUT_ROOT}" && ditto -c -k --sequesterRsrc --keepParent "${STAGING_NAME}" "${STAGING_NAME}.zip")
  log "Done: ${ZIP_PATH}"
else
  log "Skip zip — staged: ${STAGING_DIR}"
fi

log "Test: unzip and double-click 'Start French Reading Assistant.command'"
