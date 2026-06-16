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
#
# The portable desktop build is core-only (DISABLE_ADDITIONAL_FEATURES=true), so
# it does not use proprietary SAML support. However java-security-toolkit brings
# com.coveo:saml-client transitively, which imports OpenSAML BOM metadata from
# Shibboleth and can still fail the core compile classpath. Exclude that unused
# SAML client for portable bootJar builds.
"${PYTHON}" - "${BUILD_GRADLE}" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
repo_old = '''        maven { url = "https://build.shibboleth.net/maven/releases" }
        maven { url = "https://repository.jboss.org/" }
        mavenCentral()
'''
repo_new = '''        mavenCentral()
        maven { url = "https://build.shibboleth.net/maven/releases" }
        maven { url = "https://repository.jboss.org/" }
'''
if repo_old in text:
    text = text.replace(repo_old, repo_new)
    print("[gradle-bootjar-portable] patched repository order: mavenCentral first")
elif repo_new in text:
    print("[gradle-bootjar-portable] repository order already patched")
else:
    raise SystemExit("[gradle-bootjar-portable] expected repository block not found")

dep_old = "        implementation 'io.github.pixee:java-security-toolkit:1.2.3'\n"
dep_prev = """        implementation('io.github.pixee:java-security-toolkit:1.2.3') {
            exclude group: 'com.coveo', module: 'saml-client'
        }
"""
dep_new = """        implementation('io.github.pixee:java-security-toolkit:1.2.3') {
            exclude group: 'com.coveo', module: 'saml-client'
            exclude group: 'org.opensaml'
        }
"""
if dep_old in text:
    text = text.replace(dep_old, dep_new)
    print("[gradle-bootjar-portable] excluded unused com.coveo:saml-client from java-security-toolkit")
elif dep_prev in text:
    text = text.replace(dep_prev, dep_new)
    print("[gradle-bootjar-portable] updated java-security-toolkit exclusion to include org.opensaml")
elif dep_new in text:
    print("[gradle-bootjar-portable] java-security-toolkit SAML exclusion already patched")
else:
    raise SystemExit("[gradle-bootjar-portable] expected java-security-toolkit dependency not found")

cfg_old = """        // Keep BouncyCastle modules aligned to avoid runtime linkage errors
        resolutionStrategy.force "org.bouncycastle:bcprov-jdk18on:${bouncycastleVersion}"
        resolutionStrategy.force "org.bouncycastle:bcpkix-jdk18on:${bouncycastleVersion}"
        resolutionStrategy.force "org.bouncycastle:bcutil-jdk18on:${bouncycastleVersion}"
"""
cfg_new = """        // Keep BouncyCastle modules aligned to avoid runtime linkage errors
        resolutionStrategy.force "org.bouncycastle:bcprov-jdk18on:${bouncycastleVersion}"
        resolutionStrategy.force "org.bouncycastle:bcpkix-jdk18on:${bouncycastleVersion}"
        resolutionStrategy.force "org.bouncycastle:bcutil-jdk18on:${bouncycastleVersion}"

        // Portable desktop build is core-only; proactively drop SAML-related
        // transitive deps that pull OpenSAML BOM metadata from Shibboleth.
        exclude group: 'com.coveo', module: 'saml-client'
        exclude group: 'org.opensaml'
"""
if cfg_old in text:
    text = text.replace(cfg_old, cfg_new)
    print("[gradle-bootjar-portable] added global excludes for com.coveo/org.opensaml")
elif cfg_new in text:
    print("[gradle-bootjar-portable] global excludes for com.coveo/org.opensaml already patched")
else:
    raise SystemExit("[gradle-bootjar-portable] expected resolutionStrategy block not found")

path.write_text(text, encoding="utf-8")
PY

run_gradle() {
  if [[ -f "./gradlew.bat" ]] && { [[ "${OS:-}" == "Windows_NT" ]] || [[ "$(uname -s 2>/dev/null)" == MINGW* ]] || [[ "$(uname -s 2>/dev/null)" == MSYS* ]]; }; then
    cmd //c gradlew.bat bootJar --no-daemon -PnoSpotless=true -PjpdfiumPlatforms="${JPDFIUM_PLATFORMS}" "${SPOTLESS_SKIP[@]}"
  else
    ./gradlew bootJar --no-daemon -PnoSpotless=true -PjpdfiumPlatforms="${JPDFIUM_PLATFORMS}" "${SPOTLESS_SKIP[@]}"
  fi
}

printf '[gradle-bootjar-portable] bootJar (jpdfium=%s, spotless=skipped)\n' "${JPDFIUM_PLATFORMS}"
run_gradle
