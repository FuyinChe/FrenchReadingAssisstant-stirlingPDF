#!/bin/bash
# French Reading Assistant — macOS portable launcher
cd "$(dirname "$0")" || exit 1
ROOT="$PWD"

export PATH="${ROOT}/tesseract/bin:${PATH}"
export TESSDATA_PREFIX="${ROOT}/tesseract/share/tessdata"
export FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_ENABLED=true
export VITE_FRENCH_READER_API_URL="${VITE_FRENCH_READER_API_URL:-http://127.0.0.1:5002/french-reader}"

if [[ -f "${ROOT}/VERSION.txt" ]]; then
  cat "${ROOT}/VERSION.txt"
  echo
fi

echo "Starting French Reading Assistant..."

ENGINE="${ROOT}/engine/french-reader-engine"
if [[ ! -x "${ENGINE}" ]]; then
  echo "[ERROR] Missing engine/french-reader-engine"
  read -r -p "Press Enter to close..."
  exit 1
fi

"${ENGINE}" &
ENGINE_PID=$!
cleanup() {
  kill "${ENGINE_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

READY=0
for _ in $(seq 1 45); do
  if curl -fsS "http://127.0.0.1:5002/health" >/dev/null 2>&1; then
    READY=1
    break
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

# Portable .app is unsigned; clear quarantine on the bundle (not only the .command file).
chmod -R u+w "${APP}" 2>/dev/null || true
xattr -dr com.apple.quarantine "${APP}" 2>/dev/null || true

MACOS_BIN="${APP}/Contents/MacOS/stirling-pdf"
if [[ ! -x "${MACOS_BIN}" ]]; then
  MACOS_BIN="$(find "${APP}/Contents/MacOS" -maxdepth 1 -type f -perm +111 2>/dev/null | head -1)"
fi

echo "Launching: $(basename "${APP}")"
echo "  (If the window disappears, see troubleshooting below.)"
open "${APP}"

sleep 3
if pgrep -f "${APP}/Contents/MacOS" >/dev/null 2>&1 || pgrep -x stirling-pdf >/dev/null 2>&1; then
  echo
  echo "Stirling PDF is running."
  echo "  • Check the Dock (PDF icon) or press Cmd+Tab to switch to Stirling PDF"
  echo "  • The window may be behind other apps"
else
  echo
  echo "[WARN] Stirling PDF may have quit immediately (window flash)."
  echo "Try in Terminal (keep this engine window open in another tab):"
  echo "  cd \"${ROOT}\""
  echo "  xattr -dr com.apple.quarantine \"${APP}\""
  echo "  \"${MACOS_BIN}\""
  echo "Or: Finder → right-click app/$(basename "${APP}") → Open → Open"
  echo "Then check Console.app for crash logs if it still closes."
fi

echo
echo "French Reader engine is running (PID ${ENGINE_PID})."
echo "Leave this terminal open while using Stirling. Close it to stop the engine."
wait "${ENGINE_PID}" 2>/dev/null || true
