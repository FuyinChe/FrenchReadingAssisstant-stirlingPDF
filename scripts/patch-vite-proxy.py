#!/usr/bin/env python3
"""Inject French Reader engine proxy into Stirling vite.config.ts (idempotent)."""
from __future__ import annotations

import sys
from pathlib import Path

MARKER = '"/french-reader"'
SNIPPET = """          "/french-reader": {
            target: process.env.FRENCH_READER_ENGINE_URL || "http://localhost:5002",
            changeOrigin: true,
          },"""


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: patch-vite-proxy.py <vite.config.ts>", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("[patch-vite-proxy] already patched")
        return 0

    anchor = '          "/v1/api-docs": backendProxy,'
    if anchor not in text:
        print("[patch-vite-proxy] anchor not found", file=sys.stderr)
        return 1

    text = text.replace(anchor, f"{anchor}\n{SNIPPET}", 1)
    path.write_text(text, encoding="utf-8")
    print("[patch-vite-proxy] applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
