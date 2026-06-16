#!/usr/bin/env bash
# Verify a staged macOS portable folder before zipping.
set -euo pipefail

STAGING_DIR="${1:?Usage: $0 <staging-dir> [--skip-desktop] [--no-smoke]}"
SKIP_DESKTOP=false
SMOKE_TEST=true

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-desktop) SKIP_DESKTOP=true; shift ;;
    --no-smoke) SMOKE_TEST=false; shift ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

log() { printf '[verify-portable-staging] %s\n' "$*"; }
fail() { log "ERROR: $*"; exit 1; }

[[ -d "${STAGING_DIR}" ]] || fail "Staging directory not found: ${STAGING_DIR}"

log "Verifying ${STAGING_DIR}"

LAUNCHER="${STAGING_DIR}/Start French Reading Assistant.command"
ENGINE_DIR="${STAGING_DIR}/engine/french-reader-engine"
if [[ -x "${ENGINE_DIR}/french-reader-engine" ]]; then
  ENGINE="${ENGINE_DIR}/french-reader-engine"
elif [[ -x "${ENGINE_DIR}" ]]; then
  ENGINE="${ENGINE_DIR}"
else
  fail "Missing engine binary under engine/french-reader-engine"
fi
TESS_BIN="${STAGING_DIR}/tesseract/bin/tesseract"
TESS_LIB="${STAGING_DIR}/tesseract/lib"
FRA_DATA="${STAGING_DIR}/tesseract/share/tessdata/fra.traineddata"

[[ -f "${LAUNCHER}" ]] || fail "Missing launcher: ${LAUNCHER}"
[[ -x "${ENGINE}" ]] || fail "Missing engine binary: ${ENGINE}"
[[ -x "${TESS_BIN}" ]] || fail "Missing tesseract binary: ${TESS_BIN}"
[[ -f "${FRA_DATA}" ]] || fail "Missing French OCR data: ${FRA_DATA}"

dylib_count="$(find "${TESS_LIB}" -maxdepth 1 -name '*.dylib' 2>/dev/null | wc -l | tr -d ' ')"
[[ "${dylib_count}" -ge 10 ]] || fail "tesseract/lib has only ${dylib_count} dylib(s); expected bundled Homebrew dependencies"

for pattern in libtesseract libleptonica libtiff libjpeg libgif libopenjp2; do
  if ! ls "${TESS_LIB}/${pattern}"*.dylib >/dev/null 2>&1; then
    fail "Missing ${pattern}*.dylib in tesseract/lib"
  fi
done

export PATH="${STAGING_DIR}/tesseract/bin:${PATH}"
export DYLD_LIBRARY_PATH="${TESS_LIB}${DYLD_LIBRARY_PATH:+:${DYLD_LIBRARY_PATH}}"
export TESSDATA_PREFIX="${STAGING_DIR}/tesseract/share/tessdata"

tess_version="$("${TESS_BIN}" --version 2>&1 | head -1)"
[[ "${tess_version}" == dyld* ]] && fail "Bundled tesseract failed to load libraries: ${tess_version}"
[[ -n "${tess_version}" ]] || fail "Bundled tesseract --version failed"
"${TESS_BIN}" --list-langs 2>/dev/null | grep -qx fra || fail "Bundled tesseract missing fra language pack"
log "Tesseract OK: ${tess_version}; fra present (${dylib_count} dylibs)"

if [[ "${SKIP_DESKTOP}" != "true" ]]; then
  APP="$(find "${STAGING_DIR}/app" -maxdepth 2 -name '*.app' 2>/dev/null | head -1)"
  [[ -n "${APP}" ]] || fail "No Stirling .app under app/"
  JAVA_BIN="$(find "${APP}" -path '*/runtime/jre/bin/java' -type f 2>/dev/null | head -1)"
  JAR="$(find "${APP}" -path '*/libs/stirling-pdf-*.jar' -type f 2>/dev/null | head -1)"
  MACOS_BIN="$(find "${APP}/Contents/MacOS" -maxdepth 1 -type f -perm +111 2>/dev/null | head -1)"
  [[ -n "${JAVA_BIN}" && -x "${JAVA_BIN}" ]] || fail "Stirling .app missing bundled JRE java: ${APP}"
  [[ -n "${JAR}" ]] || fail "Stirling .app missing stirling-pdf jar under Resources/libs"
  [[ -n "${MACOS_BIN}" ]] || fail "Stirling .app missing MacOS binary"
  log "Stirling desktop OK: $(basename "${APP}"), $(basename "${JAR}")"
fi

if [[ "${SMOKE_TEST}" == "true" ]]; then
  export PATH="${STAGING_DIR}/tesseract/bin:${PATH}"
  export DYLD_LIBRARY_PATH="${TESS_LIB}${DYLD_LIBRARY_PATH:+:${DYLD_LIBRARY_PATH}}"
  export TESSDATA_PREFIX="${STAGING_DIR}/tesseract/share/tessdata"
  export FRENCH_READER_CORS_ORIGINS="${FRENCH_READER_CORS_ORIGINS:-http://localhost:5173,https://tauri.localhost}"
  ENGINE_PID=""
  cleanup() {
    if [[ -n "${ENGINE_PID}" ]]; then
      kill "${ENGINE_PID}" 2>/dev/null || true
      wait "${ENGINE_PID}" 2>/dev/null || true
    fi
  }
  trap cleanup EXIT

  "${ENGINE}" &
  ENGINE_PID=$!

  status_json=""
  for _ in $(seq 1 45); do
    if status_json="$(curl -fsS "http://127.0.0.1:5002/french-reader/status" 2>/dev/null)"; then
      break
    fi
    sleep 1
  done
  [[ -n "${status_json}" ]] || fail "Engine did not respond on :5002/french-reader/status"

  echo "${status_json}" | python3 -c "
import json, sys
s = json.load(sys.stdin)
if not s.get('ocr_ready'):
    raise SystemExit('Engine ocr_ready=false — tesseract/pytesseract not usable')
if not s.get('bubble_ready'):
    raise SystemExit('Engine bubble_ready=false — OpenCV (cv2) not bundled in PyInstaller binary')
print('ocr_ready=%s bubble_ready=%s' % (s.get('ocr_ready'), s.get('bubble_ready')))
" || fail "Engine smoke test failed"
  log "Engine smoke test OK"

  if ! curl -fsS -o /dev/null -X OPTIONS \
    -H 'Origin: https://tauri.localhost' \
    -H 'Access-Control-Request-Method: POST' \
    -H 'Access-Control-Request-Headers: content-type' \
    -w '%{http_code}' \
    "http://127.0.0.1:5002/french-reader/ocr/region" 2>/dev/null | grep -qE '^(200|204)$'; then
    fail "CORS preflight failed for Tauri origin (OPTIONS /ocr/region)"
  fi
  log "CORS preflight OK for https://tauri.localhost"
fi

log "All checks passed for ${STAGING_DIR}"
