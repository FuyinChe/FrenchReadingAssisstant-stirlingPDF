#!/usr/bin/env bash
# Install French Reader extensions into stirling-upstream (sidecar engine + frontend tool).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
EXT_ENGINE="${ROOT}/extensions/french-reader-engine"
EXT_FRONTEND="${ROOT}/extensions/french-reader-frontend"
MARKER="${ROOT}/.extensions-installed"
ENABLED="${FRENCH_READER_ENABLED:-true}"

log() { printf '[install-extensions] %s\n' "$*"; }
die() { printf '[install-extensions] ERROR: %s\n' "$*" >&2; exit 1; }

PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  die "python not found (install Python 3.11+)"
fi

if ! "$PYTHON" "${ROOT}/scripts/sync-plugin-version.py"; then
  die "sync-plugin-version failed"
fi

[[ -d "${STIRLING}/frontend" ]] || die "stirling-upstream not found. Run: git submodule update --init --recursive"

log "Installing French Reader extensions (enabled=${ENABLED})"

# --- Frontend: copy extension sources (under core/ so @app/* resolves) ---
FE_CORE="${STIRLING}/frontend/editor/src/core"
mkdir -p "${FE_CORE}/tools/frenchReader"
mkdir -p "${FE_CORE}/hooks/tools/frenchReader"
mkdir -p "${FE_CORE}/components/frenchReader"
mkdir -p "${FE_CORE}/contexts"
mkdir -p "${FE_CORE}/services"
mkdir -p "${FE_CORE}/utils"
mkdir -p "${FE_CORE}/extensions/french-reader"

cp "${EXT_FRONTEND}/src/tools/FrenchReader.tsx" "${FE_CORE}/tools/frenchReader/FrenchReader.tsx"
cp "${EXT_FRONTEND}/src/hooks/tools/frenchReader/"*.ts "${FE_CORE}/hooks/tools/frenchReader/"
cp "${EXT_FRONTEND}/src/components/frenchReader/"*.tsx "${FE_CORE}/components/frenchReader/"
cp "${EXT_FRONTEND}/src/contexts/FrenchReaderContext.tsx" "${FE_CORE}/contexts/FrenchReaderContext.tsx"
cp "${EXT_FRONTEND}/src/services/"*.ts "${FE_CORE}/services/"
cp "${EXT_FRONTEND}/src/utils/"*.ts "${FE_CORE}/utils/"
cp "${EXT_FRONTEND}/src/extensions/french-reader/useFrenchReaderToolRegistry.tsx" \
  "${FE_CORE}/extensions/french-reader/useFrenchReaderToolRegistry.tsx"

# Remove legacy install paths (pre-core layout)
rm -rf "${STIRLING}/frontend/editor/src/tools/frenchReader" \
  "${STIRLING}/frontend/editor/src/hooks/tools/frenchReader" \
  "${STIRLING}/frontend/editor/src/components/frenchReader" \
  "${STIRLING}/frontend/editor/src/extensions/french-reader"

# --- Frontend: apply minimal patches (reversible via git checkout in submodule) ---
if [[ "${ENABLED}" == "true" ]]; then
  cp "${EXT_FRONTEND}/patches/prototypeToolId.ts" \
    "${FE_CORE}/types/prototypeToolId.ts"
  cp "${EXT_FRONTEND}/patches/usePrototypeToolRegistry.tsx" \
    "${FE_CORE}/data/usePrototypeToolRegistry.tsx"
  log "Applied frontend registry patches (prototype tool + frenchReader id)"
  "$PYTHON" "${ROOT}/scripts/patch-vite-proxy.py" \
    "${STIRLING}/frontend/editor/vite.config.ts" || die "vite proxy patch failed"
else
  log "FRENCH_READER_ENABLED=false — skipped frontend patches"
fi

# --- Engine: sidecar service (no Stirling engine core changes) ---
if [[ "${FRENCH_READER_SKIP_ENGINE_INSTALL:-}" == "true" ]]; then
  log "FRENCH_READER_SKIP_ENGINE_INSTALL=true — skipped engine Python deps (Docker Stirling build)"
elif [[ "${ENABLED}" == "true" ]]; then
  if ! command -v tesseract >/dev/null 2>&1; then
    log "Tesseract not found — run: ./scripts/setup-ocr.sh"
  fi
  log "Installing French Reader engine Python deps..."
  (
    cd "${EXT_ENGINE}"
    if command -v uv >/dev/null 2>&1; then
      uv sync --dev --extra bubble
    else
      "$PYTHON" -m pip install -e ".[bubble]" 2>/dev/null || "$PYTHON" -m pip install -e .
    fi
  )
  log "French Reader engine runs as sidecar on port 5002 (see scripts/dev.sh)"
else
  log "FRENCH_READER_ENABLED=false — skipped engine install"
fi

if date -u +"%Y-%m-%dT%H:%M:%SZ" > "${MARKER}" 2>/dev/null; then
  :
else
  "$PYTHON" -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))" > "${MARKER}"
fi
log "Done. Marker written to ${MARKER}"
