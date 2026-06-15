#!/usr/bin/env bash
# Build all Docker images for FrenchPdfReader (M601).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAG="${FRENCH_READER_IMAGE_TAG:-french-pdf-reader}"

log() { printf '[docker-build] %s\n' "$*"; }

[[ -d "${ROOT}/stirling-upstream/.git" ]] || {
  log "Initializing stirling-upstream submodule..."
  git -C "${ROOT}" submodule update --init --recursive
}

log "Building French Reader engine image..."
docker build \
  -f "${ROOT}/docker/french-reader-engine/Dockerfile" \
  -t "${TAG}-engine" \
  "${ROOT}"

log "Building Stirling extended image (this may take a long time)..."
docker build \
  -f "${ROOT}/docker/stirling-extended/Dockerfile" \
  -t "${TAG}-stirling" \
  "${ROOT}"

log "Building gateway image..."
docker build \
  -f "${ROOT}/docker/gateway/Dockerfile" \
  -t "${TAG}-gateway" \
  "${ROOT}"

log "Done."
log "Start with: ./scripts/docker-up.sh"
