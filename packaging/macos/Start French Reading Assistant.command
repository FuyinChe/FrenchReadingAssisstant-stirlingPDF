#!/bin/bash
# French Reading Assistant — macOS portable launcher
cd "$(dirname "$0")" || exit 1
ROOT="$PWD"

export PATH="${ROOT}/tesseract/bin:${PATH}"
export TESSDATA_PREFIX="${ROOT}/tesseract/share/tessdata"
export FRENCH_READER_ENABLED=true
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

APP="$(find "${ROOT}/app" -maxdepth 1 -name '*.app' | head -1)"
if [[ -z "${APP}" ]]; then
  echo "[ERROR] No .app in app/ folder."
  read -r -p "Press Enter to close..."
  exit 1
fi

echo "Launching: $(basename "${APP}")"
open "${APP}"

echo
echo "French Reader engine is running (PID ${ENGINE_PID})."
echo "Close this window to stop the engine, or press Ctrl+C."
wait "${ENGINE_PID}" 2>/dev/null || true
