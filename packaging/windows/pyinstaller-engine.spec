# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for french-reader-engine (Windows x64 portable)."""

import pathlib

from PyInstaller.utils.hooks import collect_submodules

root = pathlib.Path(SPECPATH).resolve().parents[2]
engine_src = root / "extensions" / "french-reader-engine" / "src"
version_json = engine_src / "french_reader" / "_plugin_version.json"

hiddenimports = collect_submodules("uvicorn")
hiddenimports += collect_submodules("fastapi")
hiddenimports += [
    "french_reader.main",
    "french_reader.router",
    "french_reader.plugin_version",
    "french_reader.config",
    "french_reader.ocr_service",
    "french_reader.tts_service",
    "french_reader.ai_service",
    "french_reader.export_service",
    "french_reader.bubble_detector",
    "french_reader.paragraph_detector",
    "cv2",
    "edge_tts",
    "pytesseract",
    "multipart",
    "reportlab",
]

a = Analysis(
    [str(root / "packaging" / "windows" / "engine-main.py")],
    pathex=[str(engine_src)],
    binaries=[],
    datas=[(str(version_json), "french_reader")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["paddle", "paddleocr", "ultralytics", "torch"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="french-reader-engine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
