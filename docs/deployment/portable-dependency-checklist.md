# Portable bundle dependency checklist

End-user zip must be self-contained on a machine **without** Homebrew, Chocolatey, Docker, or dev toolchains.

> **完整排障手册：** [portable-packaging-playbook.md](portable-packaging-playbook.md)

## What each layer needs

| Component | Windows (`app\`) | macOS (`app/*.app`) | French Reader (`engine/`) | OCR (`tesseract/`) |
|-----------|------------------|---------------------|---------------------------|---------------------|
| Stirling UI | `stirling-pdf.exe` | `Contents/MacOS/*` | — | — |
| Java backend | `runtime\jre\bin\java.exe` | `Contents/Resources/runtime/jre/bin/java` | — | — |
| Stirling JAR | `libs\stirling-pdf-*.jar` | `Contents/Resources/libs/stirling-pdf-*.jar` | — | — |
| OCR binary | — | — | subprocess | `tesseract.exe` / `bin/tesseract` |
| OCR native deps | — | — | — | all `*.dll` / `lib/*.dylib` |
| French tessdata | — | — | — | `tessdata/fra.traineddata` (Win) / `share/tessdata/fra.traineddata` (Mac) |
| OpenCV bubbles | — | — | bundled in PyInstaller (`cv2`) | — |
| PDF fonts | — | — | `assets/fonts/CharisSIL-*.ttf` in PyInstaller `datas` | — |
| Tesseract OCR | — | — | bundled (`pytesseract`) + PATH | external binary |

## Launcher environment (engine process)

| Variable | Windows | macOS |
|----------|---------|-------|
| `PATH` | `%ROOT%tesseract` | `$ROOT/tesseract/bin` |
| `TESSDATA_PREFIX` | `%ROOT%tesseract\tessdata` | `$ROOT/tesseract/share/tessdata` |
| `DYLD_LIBRARY_PATH` | — | **unset** for engine (tesseract uses `@rpath`) |
| `FRENCH_READER_CORS_ORIGINS` | Tauri desktop origins | same |
| `VITE_FRENCH_READER_API_URL` | baked at Stirling build: `http://127.0.0.1:5002/french-reader` | same |

## Build-time verification

After staging, **before zip**:

```powershell
# Windows
powershell -File .\scripts\verify-portable-staging.ps1 -StagingDir dist\portable-windows\French-Reading-Assistant-*-windows-x64
```

```bash
# macOS
./scripts/verify-portable-staging.sh dist/portable-macos/French-Reading-Assistant-*-macos-arm64
```

Checks include:

1. File layout (engine, tesseract, Stirling, `fra.traineddata`)
2. Tesseract runs (`--version`, `--list-langs` includes `fra`)
3. Engine smoke: `GET /french-reader/status` → `ocr_ready=true`, `bubble_ready=true`
4. OCR roundtrip: `POST /ocr/region` not 5xx
5. PDF export: `POST /export/pdf` returns `%PDF`
6. CORS preflight for `https://tauri.localhost`

`build-portable-windows.ps1` and `build-portable-macos.sh` call these automatically.

## macOS-only: engine codesign

Before engine smoke test, verify runs `sign-engine-bundle.sh` when present. User zips should include this script at bundle root.

## If `fra.traineddata` is missing on the build machine

`fetch-tesseract-windows.ps1` and `fetch-tesseract-macos.sh` download it from [tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast).

## Not bundled (by design)

- **YOLO** (`ultralytics` / `torch`) — OpenCV bubble detection instead
- **PaddleOCR** — Tesseract is the portable OCR engine
- **LLM API keys** — user supplies in Settings; TTS/AI need network
