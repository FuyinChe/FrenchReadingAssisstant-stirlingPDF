#!/usr/bin/env bash
# Start FrenchPdfReader Docker stack (builds images if missing).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

log() { printf '[docker-up] %s\n' "$*"; }

if [[ ! -f "${ROOT}/.env" ]] && [[ -f "${ROOT}/.env.docker.example" ]]; then
  log "No .env found — using .env.docker.example defaults via compose env_file (optional)."
fi

if ! docker compose config >/dev/null 2>&1; then
  log "ERROR: docker compose config failed"
  exit 1
fi

log "Building / starting stack (gateway :${FRENCH_READER_HTTP_PORT:-8080})..."
docker compose up -d --build

log "Waiting for gateway..."
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${FRENCH_READER_HTTP_PORT:-8080}/french-reader/ai/providers" >/dev/null 2>&1; then
    log "French Reader API ready."
    break
  fi
  sleep 3
done

log "Open http://localhost:${FRENCH_READER_HTTP_PORT:-8080}"
log "French Reader Tool: Recommended tools → French Reading Assistant"
