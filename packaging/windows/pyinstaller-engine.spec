# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for french-reader-engine (Windows x64 portable)."""

import pathlib

from PyInstaller.utils.hooks import collect_all, collect_submodules


def _repo_root() -> pathlib.Path:
    spec_file = pathlib.Path(globals().get("SPEC", SPECPATH)).resolve()
    start = spec_file.parent if spec_file.is_file() else spec_file
    for candidate in (start, *start.parents):
        if (candidate / "extensions" / "french-reader-engine" / "pyproject.toml").is_file():
            return candidate
    raise RuntimeError(f"Could not locate repo root from spec at {spec_file}")


root = _repo_root()
engine_src = root / "extensions" / "french-reader-engine" / "src"
version_json = engine_src / "french_reader" / "_plugin_version.json"
fonts_dir = engine_src / "french_reader" / "assets" / "fonts"

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
    "french_reader.pdf_fonts",
    "french_reader.markdown_pdf",
    "french_reader.bubble_detector",
    "french_reader.paragraph_detector",
    "cv2",
    "edge_tts",
    "pytesseract",
    "multipart",
    "reportlab",
]

cv2_datas, cv2_binaries, cv2_hidden = collect_all("cv2")
hiddenimports += cv2_hidden

a = Analysis(
    [str(root / "packaging" / "windows" / "engine-main.py")],
    pathex=[str(engine_src)],
    binaries=cv2_binaries,
    datas=[
        (str(version_json), "french_reader"),
        (str(fonts_dir), "french_reader/assets/fonts"),
    ] + cv2_datas,
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
