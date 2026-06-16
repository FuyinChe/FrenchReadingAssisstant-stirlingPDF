#!/usr/bin/env bash
# Build Stirling bootJar for portable desktop bundles.
# Skips Spotless (hits flaky build.shibboleth.net on GitHub Actions).
# Same flags as docker/stirling-extended/Dockerfile.
#
# Usage:
#   ./scripts/gradle-bootjar-portable.sh windows-x64
#   ./scripts/gradle-bootjar-portable.sh darwin-arm64
#   ./scripts/gradle-bootjar-portable.sh darwin-x64
set -euo pipefail

JPDFIUM_PLATFORMS="${1:?Usage: $0 <jpdfium-platform>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
INIT_SCRIPT="${ROOT}/scripts/portable-gradle.init.gradle"

SPOTLESS_SKIP=(
  -x spotlessApply -x spotlessCheck -x spotlessJava
  -x spotlessGradle -x spotlessGradleApply -x spotlessYaml -x spotlessYamlApply
)

cd "${STIRLING}"
export DISABLE_ADDITIONAL_FEATURES=true
[[ -f "${INIT_SCRIPT}" ]] || { echo "[gradle-bootjar-portable] missing init script: ${INIT_SCRIPT}" >&2; exit 1; }

run_gradle() {
  # Core-only JAR (:stirling-pdf). Root `bootJar` still compiles :proprietary even when
  # DISABLE_ADDITIONAL_FEATURES=true, which we do not need for portable desktop.
  local -a GRADLE_ARGS=(
    --init-script "${INIT_SCRIPT}"
    :stirling-pdf:bootJar
    --no-daemon
    -PnoSpotless=true
    -PjpdfiumPlatforms="${JPDFIUM_PLATFORMS}"
    "${SPOTLESS_SKIP[@]}"
  )
  if [[ -f "./gradlew.bat" ]] && { [[ "${OS:-}" == "Windows_NT" ]] || [[ "$(uname -s 2>/dev/null)" == MINGW* ]] || [[ "$(uname -s 2>/dev/null)" == MSYS* ]]; }; then
    cmd //c gradlew.bat "${GRADLE_ARGS[@]}"
  else
    ./gradlew "${GRADLE_ARGS[@]}"
  fi
}

printf '[gradle-bootjar-portable] :stirling-pdf:bootJar (jpdfium=%s, spotless=skipped, init=%s)\n' "${JPDFIUM_PLATFORMS}" "$(basename "${INIT_SCRIPT}")"
run_gradle
