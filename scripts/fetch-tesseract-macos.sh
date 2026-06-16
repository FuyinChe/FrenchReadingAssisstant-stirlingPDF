#!/usr/bin/env bash
# Stage Tesseract OCR binaries for macOS portable bundle.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${1:-${ROOT}/dist/portable-staging/tesseract}"

log() { printf '[fetch-tesseract-macos] %s\n' "$*"; }

copy_tess_tree() {
  local prefix="$1"
  local bin="${prefix}/bin/tesseract"
  [[ -x "${bin}" ]] || return 1
  mkdir -p "${OUTPUT_DIR}/bin" "${OUTPUT_DIR}/share"
  cp -f "${bin}" "${OUTPUT_DIR}/bin/"
  chmod u+rw "${OUTPUT_DIR}/bin/tesseract"
  chmod +x "${OUTPUT_DIR}/bin/tesseract"
  if [[ -d "${prefix}/share/tessdata" ]]; then
    rm -rf "${OUTPUT_DIR}/share/tessdata"
    cp -R "${prefix}/share/tessdata" "${OUTPUT_DIR}/share/"
  elif [[ -d "${prefix}/share/tesseract/tessdata" ]]; then
    rm -rf "${OUTPUT_DIR}/share/tessdata"
    cp -R "${prefix}/share/tesseract/tessdata" "${OUTPUT_DIR}/share/"
  fi
  # Homebrew sometimes uses /opt/homebrew/share/tessdata
  if [[ ! -d "${OUTPUT_DIR}/share/tessdata" && -d "${prefix}/../share/tessdata" ]]; then
    cp -R "${prefix}/../share/tessdata" "${OUTPUT_DIR}/share/"
  fi
  return 0
}

if command -v brew >/dev/null 2>&1; then
  PREFIX="$(brew --prefix tesseract 2>/dev/null || brew --prefix)"
  if copy_tess_tree "${PREFIX}"; then
    log "Copied Tesseract from ${PREFIX}"
    exit 0
  fi
fi

for candidate in /opt/homebrew/opt/tesseract /usr/local/opt/tesseract; do
  if copy_tess_tree "${candidate}"; then
    log "Copied Tesseract from ${candidate}"
    exit 0
  fi
done

log "Tesseract not found. Install with: brew install tesseract tesseract-lang"
exit 1
