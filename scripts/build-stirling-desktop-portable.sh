#!/usr/bin/env bash
# Build Stirling Tauri .app for portable zip (no dmg/msi/deb, no updater signing).
#
# Does NOT call upstream desktop:prepare (Gradle Spotless + build.shibboleth.net fails on CI).
# Uses gradle-bootjar-portable.sh + explicit jlink instead.
#
# Usage:
#   ./scripts/build-stirling-desktop-portable.sh aarch64-apple-darwin
#   ./scripts/build-stirling-desktop-portable.sh x86_64-apple-darwin
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STIRLING="${ROOT}/stirling-upstream"
EDITOR="${STIRLING}/frontend/editor"
TAURI_SRC="${EDITOR}/src-tauri"
TAURI_CONF="${TAURI_SRC}/tauri.conf.json"
RUST_TARGET="${1:?Usage: $0 <aarch64-apple-darwin|x86_64-apple-darwin>}"

JLINK_MODULES="java.base,java.compiler,java.desktop,java.instrument,java.logging,java.management,java.naming,java.net.http,java.prefs,java.rmi,java.scripting,java.security.jgss,java.security.sasl,java.sql,java.transaction.xa,java.xml,java.xml.crypto,jdk.crypto.ec,jdk.crypto.cryptoki,jdk.unsupported,jdk.dynalink"

log() { printf '[build-stirling-desktop-portable] %s\n' "$*"; }
die() { log "ERROR: $*"; exit 1; }

case "${RUST_TARGET}" in
  aarch64-apple-darwin) JPDFIUM_PLATFORMS="darwin-arm64" ;;
  x86_64-apple-darwin) JPDFIUM_PLATFORMS="darwin-x64" ;;
  *) die "Unsupported Rust target: ${RUST_TARGET}" ;;
esac

for cmd in task npx python3; do
  command -v "${cmd}" >/dev/null 2>&1 || die "Missing command: ${cmd}"
done

[[ -n "${JAVA_HOME:-}" ]] || die "JAVA_HOME is not set (install JDK 25, e.g. setup-java in CI)"
JLINK="${JAVA_HOME}/bin/jlink"
[[ -x "${JLINK}" ]] || die "jlink not found at ${JLINK}"

export PATH="${JAVA_HOME}/bin:${PATH}"

log "Preparing Stirling frontend (task frontend:prepare MODE=desktop)..."
(cd "${STIRLING}" && task frontend:prepare MODE=desktop)

log "Building backend bootJar (${JPDFIUM_PLATFORMS} JPDFium natives)..."
"${ROOT}/scripts/gradle-bootjar-portable.sh" "${JPDFIUM_PLATFORMS}"

LIBS_DIR="${TAURI_SRC}/libs"
mkdir -p "${LIBS_DIR}"
JAR="$(find "${STIRLING}/app/core/build/libs" -maxdepth 1 -name 'stirling-pdf-*.jar' | head -1)"
[[ -n "${JAR}" ]] || die "stirling-pdf-*.jar not found under app/core/build/libs"
cp -f "${JAR}" "${LIBS_DIR}/"
log "Copied $(basename "${JAR}") to libs/"

RUNTIME_JRE="${TAURI_SRC}/runtime/jre"
rm -rf "${RUNTIME_JRE}"
mkdir -p "${TAURI_SRC}/runtime"

log "Creating bundled JRE with jlink..."
"${JLINK}" \
  --add-modules "${JLINK_MODULES}" \
  --strip-debug \
  --compress=zip-6 \
  --no-header-files \
  --no-man-pages \
  --output "${RUNTIME_JRE}"

chmod -R u+w "${RUNTIME_JRE}"
[[ -f "${RUNTIME_JRE}/release" ]] || die "jlink output missing release marker"
log "Bundled JRE ready at runtime/jre"

log "Patching tauri.conf.json for portable build (app-only, no updater pubkey)..."
python3 "${ROOT}/scripts/patch-tauri-portable.py" "${TAURI_CONF}"

log "Building for ${RUST_TARGET}"
rustup target add "${RUST_TARGET}" >/dev/null 2>&1 || true

# Workflow sets CARGO_BUILD_TARGET per matrix row; without matching `tauri --target`
# native arm64 builds can compile to target/release/ while the bundler expects elsewhere.
unset CARGO_BUILD_TARGET

TAURI_ARGS=(
  build
  --target "${RUST_TARGET}"
  --bundles app
  --verbose
  --config '{"bundle":{"targets":["app"],"createUpdaterArtifacts":false}}'
)

log "Running: npx tauri ${TAURI_ARGS[*]}"
log "(NOT task desktop:build — portable zip only needs .app)"
(cd "${EDITOR}" && npx tauri "${TAURI_ARGS[@]}")

log "Done. Look for .app under ${TAURI_SRC}/target/${RUST_TARGET}/release/bundle/macos/"
