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

[[ -d "${STIRLING}/frontend" ]] || die "stirling-upstream not found. Run: git submodule update --init --recursive"

log "Installing French Reader extensions (enabled=${ENABLED})"

# --- Frontend: copy extension sources (under core/ so @app/* resolves) ---
FE_CORE="${STIRLING}/frontend/editor/src/core"
mkdir -p "${FE_CORE}/tools/frenchReader"
mkdir -p "${FE_CORE}/hooks/tools/frenchReader"
mkdir -p "${FE_CORE}/components/frenchReader"
mkdir -p "${FE_CORE}/extensions/french-reader"

cp "${EXT_FRONTEND}/src/tools/FrenchReader.tsx" "${FE_CORE}/tools/frenchReader/FrenchReader.tsx"
cp "${EXT_FRONTEND}/src/hooks/tools/frenchReader/"*.ts "${FE_CORE}/hooks/tools/frenchReader/"
cp "${EXT_FRONTEND}/src/components/frenchReader/"*.tsx "${FE_CORE}/components/frenchReader/"
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
else
  log "FRENCH_READER_ENABLED=false — skipped frontend patches"
fi

# --- Engine: sidecar service (no Stirling engine core changes) ---
log "French Reader engine runs as sidecar on port 5002 (see scripts/dev.sh)"
log "Install Python deps manually: cd extensions/french-reader-engine && uv sync --dev"

date -u +"%Y-%m-%dT%H:%M:%SZ" > "${MARKER}"
log "Done. Marker written to ${MARKER}"
