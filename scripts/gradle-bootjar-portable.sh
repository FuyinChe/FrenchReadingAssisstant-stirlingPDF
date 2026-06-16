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

SPOTLESS_SKIP=(
  -x spotlessApply -x spotlessCheck -x spotlessJava
  -x spotlessGradle -x spotlessGradleApply -x spotlessYaml -x spotlessYamlApply
)

cd "${STIRLING}"
export DISABLE_ADDITIONAL_FEATURES=true

run_gradle() {
  if [[ -f "./gradlew.bat" ]] && { [[ "${OS:-}" == "Windows_NT" ]] || [[ "$(uname -s 2>/dev/null)" == MINGW* ]] || [[ "$(uname -s 2>/dev/null)" == MSYS* ]]; }; then
    cmd //c gradlew.bat bootJar --no-daemon -PjpdfiumPlatforms="${JPDFIUM_PLATFORMS}" "${SPOTLESS_SKIP[@]}"
  else
    ./gradlew bootJar --no-daemon -PjpdfiumPlatforms="${JPDFIUM_PLATFORMS}" "${SPOTLESS_SKIP[@]}"
  fi
}

printf '[gradle-bootjar-portable] bootJar (jpdfium=%s, spotless=skipped)\n' "${JPDFIUM_PLATFORMS}"
run_gradle
