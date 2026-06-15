from __future__ import annotations

import json
from functools import lru_cache
from importlib import metadata
from pathlib import Path

_VERSION_JSON = Path(__file__).with_name("_plugin_version.json")
_FALLBACK_VERSION = "0.0.0-dev"


@lru_cache
def get_plugin_version_info() -> dict:
    if _VERSION_JSON.is_file():
        return json.loads(_VERSION_JSON.read_text(encoding="utf-8"))
    try:
        dist_version = metadata.version("french-reader-engine")
    except metadata.PackageNotFoundError:
        dist_version = _FALLBACK_VERSION
    return {
        "name": "french-reading-assistant",
        "displayName": "French Reading Assistant",
        "version": dist_version,
        "apiVersion": 1,
    }


def get_plugin_version_string() -> str:
    return str(get_plugin_version_info().get("version", _FALLBACK_VERSION))
