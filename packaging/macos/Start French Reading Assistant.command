#!/bin/bash
# French Reading Assistant — macOS portable launcher
set +m
cd "$(dirname "$0")" || exit 1
ROOT="$PWD"

chmod -R u+w "${ROOT}" 2>/dev/null || true
xattr -cr "${ROOT}" 2>/dev/null || true

resolve_engine() {
  local onedir="${ROOT}/engine/french-reader-engine/french-reader-engine"
  local onefile="${ROOT}/engine/french-reader-engine"
  if [[ -x "${onedir}" ]]; then
    printf '%s\n' "${onedir}"
  elif [[ -f "${onefile}" && -x "${onefile}" ]]; then
    printf '%s\n' "${onefile}"
  else
    return 1
  fi
}

sign_engine() {
  local script="${ROOT}/sign-engine-bundle.sh"
  if [[ -x "${script}" ]]; then
    "${script}" "${ROOT}/engine/french-reader-engine" || {
      echo "[WARN] Engine codesign failed — OCR engine may be killed by macOS."
      echo "  Run: \"${script}\" \"${ROOT}/engine/french-reader-engine\""
    }
    return
  fi
  if command -v codesign >/dev/null 2>&1; then
    chmod -R u+w "${ROOT}/engine/french-reader-engine" 2>/dev/null || true
    codesign -s - --force --deep "${1}" || echo "[WARN] codesign failed for ${1}"
  fi
}

if xattr -l "${ROOT}/engine/french-reader-engine" 2>/dev/null | grep -q 'com.apple.quarantine'; then
  echo "[ERROR] Folder is still quarantined (common for Downloads)."
  echo "Do NOT double-click this file. Run once in Terminal:"
  echo
  echo "  cd \"${ROOT}\""
  echo "  chmod -R u+w ."
  echo "  xattr -cr ."
  echo "  chmod +x \"Start French Reading Assistant.command\""
  echo "  ./Start\\ French\\ Reading\\ Assistant.command"
  echo
  read -r -p "Press Enter to close..."
  exit 1
fi

export PATH="${ROOT}/tesseract/bin:${PATH}"
export TESSDATA_PREFIX="${ROOT}/tesseract/share/tessdata"
# Do not set DYLD_LIBRARY_PATH before the PyInstaller engine — macOS may SIGKILL it
# when it loads bundled Python/OpenCV. Bundled tesseract uses @rpath to ../lib.
export FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_API_URL="${VITE_FRENCH_READER_API_URL:-http://127.0.0.1:5002/french-reader}"
export FRENCH_READER_CORS_ORIGINS="${FRENCH_READER_CORS_ORIGINS:-http://localhost:5173,http://localhost:8080,http://127.0.0.1:8080,http://127.0.0.1:5173,https://tauri.localhost,http://tauri.localhost,https://asset.localhost,http://asset.localhost,https://ipc.localhost,http://ipc.localhost}"

export STIRLING_PDF_TEST_FORCE_AUTH_KEYRING_FAIL=1
export STIRLING_PDF_TEST_FORCE_REFRESH_KEYRING_FAIL=1

if [[ -f "${ROOT}/VERSION.txt" ]]; then
  cat "${ROOT}/VERSION.txt"
  echo
fi

ENGINE="$(resolve_engine)" || {
  echo "[ERROR] Missing engine/french-reader-engine"
  read -r -p "Press Enter to close..."
  exit 1
}

sign_engine "${ENGINE}"

LOG_DIR="${ROOT}/logs"
mkdir -p "${LOG_DIR}"
ENGINE_LOG="${LOG_DIR}/engine.log"

echo "Starting French Reading Assistant..."
echo "(Engine startup can take 20–60s on first launch — please wait.)"

: > "${ENGINE_LOG}"
env -u DYLD_LIBRARY_PATH \
  PATH="${ROOT}/tesseract/bin:${PATH}" \
  TESSDATA_PREFIX="${ROOT}/tesseract/share/tessdata" \
  FRENCH_READER_ENABLED="${FRENCH_READER_ENABLED}" \
  VITE_FRENCH_READER_ENABLED="${VITE_FRENCH_READER_ENABLED}" \
  VITE_FRENCH_READER_API_URL="${VITE_FRENCH_READER_API_URL}" \
  FRENCH_READER_CORS_ORIGINS="${FRENCH_READER_CORS_ORIGINS}" \
  "${ENGINE}" >>"${ENGINE_LOG}" 2>&1 &
ENGINE_PID=$!
STIRLING_PID=""
cleanup() {
  kill "${ENGINE_PID}" 2>/dev/null || true
  if [[ -n "${STIRLING_PID}" ]]; then
    kill "${STIRLING_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

READY=0
for i in $(seq 1 90); do
  if ! kill -0 "${ENGINE_PID}" 2>/dev/null; then
    wait "${ENGINE_PID}" 2>/dev/null || true
    echo "[ERROR] French Reader engine exited while starting."
    if [[ -s "${ENGINE_LOG}" ]]; then
      echo
      echo "--- engine log (last 40 lines) ---"
      tail -40 "${ENGINE_LOG}"
      echo "--- end ---"
    else
      echo "No engine log output (process may have been killed by macOS before startup)."
      echo "Try signing the engine bundle:"
      echo "  \"${ROOT}/sign-engine-bundle.sh\" \"${ROOT}/engine/french-reader-engine\""
      echo "Or: codesign -s - --force --deep \"${ENGINE}\""
    fi
    echo
    echo "Full log: ${ENGINE_LOG}"
    read -r -p "Press Enter to close..."
    exit 1
  fi
  if /usr/sbin/lsof -nP -iTCP:5002 -sTCP:LISTEN -t >/dev/null 2>&1; then
    READY=1
    break
  fi
  if (( i % 5 == 0 )); then
    echo "  … waiting for engine (${i}s)"
  fi
  sleep 1
done

if [[ "${READY}" -eq 0 ]]; then
  echo "[WARN] Engine still starting; OCR may take a moment."
else
  echo "French Reader engine is ready."
fi

APP="$(find "${ROOT}/app" -maxdepth 2 -name '*.app' | head -1)"
if [[ -z "${APP}" ]]; then
  echo "[ERROR] No .app in app/ folder."
  read -r -p "Press Enter to close..."
  exit 1
fi

chmod -R u+w "${APP}" 2>/dev/null || true
xattr -cr "${APP}" 2>/dev/null || true

MACOS_BIN="${APP}/Contents/MacOS/stirling-pdf"
if [[ ! -x "${MACOS_BIN}" ]]; then
  MACOS_BIN="$(find "${APP}/Contents/MacOS" -maxdepth 1 -type f -perm +111 2>/dev/null | head -1)"
fi

echo "Launching: $(basename "${APP}")"
if [[ ! -x "${MACOS_BIN}" ]]; then
  echo "[ERROR] Missing ${MACOS_BIN}"
  read -r -p "Press Enter to close..."
  exit 1
fi
"${MACOS_BIN}" &
STIRLING_PID=$!

sleep 3
if kill -0 "${STIRLING_PID}" 2>/dev/null || pgrep -x stirling-pdf >/dev/null 2>&1; then
  echo
  echo "Stirling PDF is running."
  echo "  • Check the Dock (PDF icon) or press Cmd+Tab to switch to Stirling PDF"
else
  echo
  echo "[WARN] Stirling PDF may have quit immediately."
  echo "Try: right-click app/$(basename "${APP}") → Open → Open"
fi

echo
echo "French Reader engine is running (PID ${ENGINE_PID})."
echo "Engine log: ${ENGINE_LOG}"
echo "Leave this terminal open while using Stirling. Close it to stop the engine."
wait "${ENGINE_PID}" 2>/dev/null || true
