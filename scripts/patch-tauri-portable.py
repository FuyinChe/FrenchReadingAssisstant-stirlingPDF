#!/usr/bin/env python3
"""Patch Stirling tauri.conf.json for portable zip builds (app-only, no updater signing)."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def patch(path: Path) -> None:
    conf = json.loads(path.read_text(encoding="utf-8"))
    bundle = conf.setdefault("bundle", {})
    bundle["targets"] = ["app"]
    bundle["createUpdaterArtifacts"] = False

    updater = conf.get("plugins", {}).get("updater")
    if isinstance(updater, dict):
        # pubkey is required at runtime by the updater plugin; only disable artifact signing
        # and official Stirling update checks for this portable fork.
        updater["endpoints"] = []
        updater["dialog"] = False

    path.write_text(json.dumps(conf, indent=2) + "\n", encoding="utf-8")
    print(f"[patch-tauri-portable] patched {path}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: patch-tauri-portable.py <tauri.conf.json>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"[patch-tauri-portable] not found: {path}", file=sys.stderr)
        return 1
    patch(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
