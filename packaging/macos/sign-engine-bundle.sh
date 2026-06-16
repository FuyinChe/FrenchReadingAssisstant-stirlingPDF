#!/bin/bash
# Ad-hoc sign a PyInstaller onedir engine bundle (all Mach-O files + entitlements).
set -euo pipefail

BUNDLE="${1:?usage: sign-engine-bundle.sh <engine-bundle-dir>}"
ENTITLEMENTS="${2:-$(cd "$(dirname "$0")" && pwd)/engine-entitlements.plist}"
MAIN="${BUNDLE}/french-reader-engine"

if ! command -v codesign >/dev/null 2>&1; then
  echo "[sign-engine-bundle] codesign not found; skipping" >&2
  exit 0
fi

if [[ ! -x "${MAIN}" ]]; then
  echo "[sign-engine-bundle] missing executable: ${MAIN}" >&2
  exit 1
fi

chmod -R u+w "${BUNDLE}" 2>/dev/null || true

sign_file() {
  local file="$1"
  local use_entitlements="${2:-no}"
  if [[ "${use_entitlements}" == "yes" && -f "${ENTITLEMENTS}" ]]; then
    codesign -s - --force --timestamp=none --entitlements "${ENTITLEMENTS}" "${file}"
  else
    codesign -s - --force --timestamp=none "${file}"
  fi
}

while IFS= read -r -d '' file; do
  sign_file "${file}" no
done < <(find "${BUNDLE}" -type f \( -name '*.so' -o -name '*.dylib' \) -print0 2>/dev/null)

while IFS= read -r -d '' file; do
  [[ "${file}" == "${MAIN}" ]] && continue
  sign_file "${file}" no
done < <(find "${BUNDLE}" -type f -perm -111 -print0 2>/dev/null)

sign_file "${MAIN}" yes
echo "[sign-engine-bundle] signed ${MAIN}"
