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
BUILD_GRADLE="${STIRLING}/build.gradle"
PYTHON="${PYTHON:-}"

SPOTLESS_SKIP=(
  -x spotlessApply -x spotlessCheck -x spotlessJava
  -x spotlessGradle -x spotlessGradleApply -x spotlessYaml -x spotlessYamlApply
)

cd "${STIRLING}"
export DISABLE_ADDITIONAL_FEATURES=true

if [[ -z "${PYTHON}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
  elif command -v python >/dev/null 2>&1; then
    PYTHON=python
  else
    echo "[gradle-bootjar-portable] python not found" >&2
    exit 1
  fi
fi

# Stirling's upstream repository order puts build.shibboleth.net before
# Maven Central. On GitHub Actions that host is often unreachable, and Gradle
# fails while resolving ordinary Central artifacts such as Spring Boot or Guava.
# Keep Shibboleth available for artifacts that need it, but let Central satisfy
# normal dependencies first.
"${PYTHON}" - "${BUILD_GRADLE}" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = '''        maven { url = "https://build.shibboleth.net/maven/releases" }
        maven { url = "https://repository.jboss.org/" }
        mavenCentral()
'''
new = '''        mavenCentral()
        maven { url = "https://build.shibboleth.net/maven/releases" }
        maven { url = "https://repository.jboss.org/" }
'''
if old in text:
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("[gradle-bootjar-portable] patched repository order: mavenCentral first")
elif new in text:
    print("[gradle-bootjar-portable] repository order already patched")
else:
    raise SystemExit("[gradle-bootjar-portable] expected repository block not found")
PY

run_gradle() {
  if [[ -f "./gradlew.bat" ]] && { [[ "${OS:-}" == "Windows_NT" ]] || [[ "$(uname -s 2>/dev/null)" == MINGW* ]] || [[ "$(uname -s 2>/dev/null)" == MSYS* ]]; }; then
    cmd //c gradlew.bat bootJar --no-daemon -PjpdfiumPlatforms="${JPDFIUM_PLATFORMS}" "${SPOTLESS_SKIP[@]}"
  else
    ./gradlew bootJar --no-daemon -PjpdfiumPlatforms="${JPDFIUM_PLATFORMS}" "${SPOTLESS_SKIP[@]}"
  fi
}

printf '[gradle-bootjar-portable] bootJar (jpdfium=%s, spotless=skipped)\n' "${JPDFIUM_PLATFORMS}"
run_gradle
