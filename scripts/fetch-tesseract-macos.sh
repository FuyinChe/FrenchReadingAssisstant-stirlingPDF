#!/usr/bin/env bash
# Stage portable Tesseract OCR for the macOS zip bundle (binary + dylibs + tessdata).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${1:-${ROOT}/dist/portable-staging/tesseract}"
BIN_DIR="${OUTPUT_DIR}/bin"
LIB_DIR="${OUTPUT_DIR}/lib"
SEEN_FILE=""

log() { printf '[fetch-tesseract-macos] %s\n' "$*"; }

ensure_french_tessdata() {
  local tessdata_dir="$1"
  local fra="${tessdata_dir}/fra.traineddata"
  if [[ -f "${fra}" ]]; then
    return 0
  fi
  mkdir -p "${tessdata_dir}"
  log "Downloading fra.traineddata (not in build machine tessdata)..."
  curl -fsSL -o "${fra}" "https://github.com/tesseract-ocr/tessdata_fast/raw/main/fra.traineddata"
  [[ -f "${fra}" ]] || {
    log "ERROR: failed to download French tessdata"
    return 1
  }
}

cleanup() {
  [[ -n "${SEEN_FILE}" && -f "${SEEN_FILE}" ]] && rm -f "${SEEN_FILE}"
}
trap cleanup EXIT

is_seen() {
  local key="$1"
  grep -Fxq "${key}" "${SEEN_FILE}" 2>/dev/null
}

mark_seen() {
  echo "$1" >> "${SEEN_FILE}"
}

resolve_existing() {
  local path="$1"
  local resolved="$path"
  while [[ -L "${resolved}" ]]; do
    local link
    link="$(readlink "${resolved}")"
    if [[ "${link}" != /* ]]; then
      resolved="$(cd "$(dirname "${resolved}")" && pwd)/${link}"
    else
      resolved="${link}"
    fi
  done
  if [[ -f "${resolved}" ]]; then
    printf '%s\n' "${resolved}"
  fi
}

is_system_lib() {
  case "$1" in
    /usr/lib/* | /System/* | /lib/*) return 0 ;;
  esac
  return 1
}

dep_target_name() {
  local dep="$1"
  case "${dep}" in
    @rpath/* | @loader_path/* | @executable_path/*) printf '%s\n' "${dep#@*/}" ;;
    *) basename "${dep}" ;;
  esac
}

find_homebrew_dylib() {
  local name="$1"
  local dir path resolved
  for dir in /opt/homebrew/opt/*/lib /usr/local/opt/*/lib /opt/homebrew/lib /usr/local/lib; do
    path="${dir}/${name}"
    resolved="$(resolve_existing "${path}")" || true
    if [[ -n "${resolved}" ]]; then
      printf '%s\n' "${resolved}"
      return 0
    fi
  done
  return 1
}

resolve_dependency_source() {
  local dep="$1"
  local name resolved
  case "${dep}" in
    @rpath/* | @loader_path/*)
      name="$(dep_target_name "${dep}")"
      find_homebrew_dylib "${name}"
      ;;
    @executable_path/*)
      printf '%s\n' "${BIN_DIR}/$(dep_target_name "${dep}")"
      ;;
    *)
      resolve_existing "${dep}"
      ;;
  esac
}

should_bundle_dep() {
  local dep="$1"
  [[ -z "${dep}" ]] && return 1
  [[ "${dep}" == @* ]] && return 1
  is_system_lib "${dep}" && return 1
  [[ "${dep}" == *homebrew* || "${dep}" == /opt/homebrew/* || "${dep}" == /usr/local/* ]] && return 0
  return 1
}

should_relink_dep() {
  local dep="$1"
  [[ -z "${dep}" ]] && return 1
  is_system_lib "${dep}" && return 1
  case "${dep}" in
    @executable_path/*) return 1 ;;
    @rpath/* | @loader_path/*) return 0 ;;
  esac
  should_bundle_dep "${dep}"
}

copy_dylib_to_lib() {
  local dep_ref="$1"
  local source_ref="${2:-${dep_ref}}"
  local resolved dest_name dest
  resolved="$(resolve_existing "${source_ref}")" || return 0
  dest_name="$(dep_target_name "${dep_ref}")"
  dest="${LIB_DIR}/${dest_name}"
  if [[ -f "${dest}" ]]; then
    mark_seen "${resolved}"
    mark_seen "${dep_ref}"
    return 0
  fi
  cp -f "${resolved}" "${dest}"
  chmod u+rw "${dest}"
  mark_seen "${resolved}"
  mark_seen "${dep_ref}"
  log "Copied ${dest_name}"
  collect_deps "${dest}"
}

collect_deps() {
  local file="$1"
  local dep source
  [[ -f "${file}" ]] || return 0
  is_seen "${file}" && return 0
  mark_seen "${file}"

  while IFS= read -r dep; do
    should_relink_dep "${dep}" || continue
    source="$(resolve_dependency_source "${dep}")" || continue
    should_bundle_dep "${source}" || continue
    copy_dylib_to_lib "${dep}" "${source}"
  done < <(otool -L "${file}" | awk 'NR>1 {gsub(/^[[:space:]]+/, ""); print $1}')
}

relink_target() {
  local target="$1"
  local loader_kind="$2"
  local dep new_path name
  while IFS= read -r dep; do
    should_relink_dep "${dep}" || continue
    name="$(dep_target_name "${dep}")"
    if [[ "${loader_kind}" == "executable" ]]; then
      new_path="@executable_path/../lib/${name}"
    else
      new_path="@loader_path/${name}"
    fi
    install_name_tool -change "${dep}" "${new_path}" "${target}" 2>/dev/null || true
  done < <(otool -L "${target}" | awk 'NR>1 {gsub(/^[[:space:]]+/, ""); print $1}')
}

verify_bundle() {
  local tess="${BIN_DIR}/tesseract"
  export DYLD_LIBRARY_PATH="${LIB_DIR}${DYLD_LIBRARY_PATH:+:${DYLD_LIBRARY_PATH}}"
  export TESSDATA_PREFIX="${OUTPUT_DIR}/share/tessdata"
  local version langs
  if ! version="$("${tess}" --version 2>&1 | head -1)"; then
    log "ERROR: staged tesseract --version failed"
    return 1
  fi
  if [[ "${version}" == dyld* ]]; then
    log "ERROR: staged tesseract failed to load libraries: ${version}"
    return 1
  fi
  log "Verified staged binary: ${version}"
  langs="$("${tess}" --list-langs 2>/dev/null || true)"
  if ! grep -qx "fra" <<< "${langs}"; then
    log "ERROR: French tessdata missing (fra not in --list-langs)"
    return 1
  fi
}

stage_tesseract() {
  local prefix="$1"
  local src_bin="${prefix}/bin/tesseract"
  [[ -x "${src_bin}" ]] || return 1

  SEEN_FILE="$(mktemp)"
  rm -rf "${OUTPUT_DIR}"
  mkdir -p "${BIN_DIR}" "${LIB_DIR}" "${OUTPUT_DIR}/share"

  cp -f "${src_bin}" "${BIN_DIR}/tesseract"
  chmod u+rw "${BIN_DIR}/tesseract"
  chmod +x "${BIN_DIR}/tesseract"

  if [[ -d "${prefix}/share/tessdata" ]]; then
    cp -R "${prefix}/share/tessdata" "${OUTPUT_DIR}/share/"
  elif [[ -d "${prefix}/share/tesseract/tessdata" ]]; then
    cp -R "${prefix}/share/tesseract/tessdata" "${OUTPUT_DIR}/share/"
  elif [[ -d "${prefix}/../share/tessdata" ]]; then
    cp -R "${prefix}/../share/tessdata" "${OUTPUT_DIR}/share/"
  else
    log "ERROR: tessdata not found under ${prefix}"
    return 1
  fi
  chmod -R u+rw "${OUTPUT_DIR}/share/tessdata" 2>/dev/null || true
  ensure_french_tessdata "${OUTPUT_DIR}/share/tessdata" || return 1

  collect_deps "${BIN_DIR}/tesseract"

  install_name_tool -add_rpath "@executable_path/../lib" "${BIN_DIR}/tesseract" 2>/dev/null || true
  relink_target "${BIN_DIR}/tesseract" "executable"
  for dylib in "${LIB_DIR}"/*.dylib; do
    [[ -f "${dylib}" ]] || continue
    install_name_tool -id "@loader_path/$(basename "${dylib}")" "${dylib}" 2>/dev/null || true
    relink_target "${dylib}" "loader"
  done

  for pattern in libtesseract libleptonica libtiff libjpeg libgif libopenjp2; do
    if ! ls "${LIB_DIR}/${pattern}"*.dylib >/dev/null 2>&1; then
      log "ERROR: bundled Tesseract is incomplete: missing ${pattern}*.dylib in ${LIB_DIR}"
      return 1
    fi
  done

  verify_bundle || return 1
  log "Bundled $(find "${LIB_DIR}" -maxdepth 1 -name '*.dylib' | wc -l | tr -d ' ') dylib(s) into ${LIB_DIR}"
  return 0
}

if command -v brew >/dev/null 2>&1; then
  PREFIX="$(brew --prefix tesseract 2>/dev/null || brew --prefix)"
  if stage_tesseract "${PREFIX}"; then
    log "Copied Tesseract from ${PREFIX}"
    exit 0
  fi
fi

for candidate in /opt/homebrew/opt/tesseract /usr/local/opt/tesseract; do
  if stage_tesseract "${candidate}"; then
    log "Copied Tesseract from ${candidate}"
    exit 0
  fi
done

log "Tesseract not found. Install with: brew install tesseract tesseract-lang"
exit 1
