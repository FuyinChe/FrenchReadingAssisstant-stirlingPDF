#!/usr/bin/env bash
# Sync stirling-upstream submodule with upstream main and reinstall extensions.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
BRANCH="${STIRLING_UPSTREAM_BRANCH:-main}"

log() { printf '[sync-upstream] %s\n' "$*"; }
die() { printf '[sync-upstream] ERROR: %s\n' "$*" >&2; exit 1; }

[[ -d "${STIRLING}/.git" ]] || die "stirling-upstream submodule missing"

log "Fetching Stirling-PDF origin/${BRANCH}..."
git -C "${STIRLING}" fetch origin "${BRANCH}"

log "Merging origin/${BRANCH} into submodule..."
git -C "${STIRLING}" merge "origin/${BRANCH}" || {
  die "Merge conflicts — resolve in stirling-upstream/, then re-run ./scripts/install-extensions.sh"
}

log "Reinstalling extensions..."
"${ROOT}/scripts/install-extensions.sh"

log "Sync complete. Run ./scripts/dev.sh to verify."
