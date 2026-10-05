#!/usr/bin/env bash
# Landing site only (no OCR engine).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEB="$ROOT/apps/web"

cd "$WEB"
if [[ ! -d node_modules ]]; then
  npm install
fi
npm run dev
