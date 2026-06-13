#!/usr/bin/env bash
# Install system OCR dependencies (Tesseract + French) for French Reader.
set -euo pipefail

log() { printf '[setup-ocr] %s\n' "$*"; }

if command -v tesseract >/dev/null 2>&1; then
  if tesseract --list-langs 2>/dev/null | grep -qx "fra"; then
    log "Tesseract + French (fra) already available: $(tesseract --version 2>&1 | head -1)"
    exit 0
  fi
  log "Tesseract found but French (fra) missing — installing language pack..."
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    log "Homebrew not found. Install from https://brew.sh then run:"
    log "  brew install tesseract tesseract-lang"
    exit 1
  fi
  brew install tesseract tesseract-lang
elif command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y tesseract-ocr tesseract-ocr-fra
else
  log "Install Tesseract + French manually, then re-run dev.sh"
  log "  macOS: brew install tesseract tesseract-lang"
  log "  Debian/Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-fra"
  exit 1
fi

log "Done: $(tesseract --version 2>&1 | head -1)"
tesseract --list-langs 2>/dev/null | grep -E '^(fra|eng)$' || true
