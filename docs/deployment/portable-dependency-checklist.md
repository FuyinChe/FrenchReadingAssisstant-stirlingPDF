# Portable bundle dependency checklist

End-user zip must be self-contained on a machine **without** Homebrew, Chocolatey, Docker, or dev toolchains.

## What each layer needs

| Component | Windows (`app\`) | macOS (`app/*.app`) | French Reader (`engine/`) | OCR (`tesseract/`) |
|-----------|------------------|---------------------|---------------------------|---------------------|
| Stirling UI | `stirling-pdf.exe` | `Contents/MacOS/*` | — | — |
| Java backend | `runtime\jre\bin\java.exe` | `Contents/Resources/runtime/jre/bin/java` | — | — |
| Stirling JAR | `libs\stirling-pdf-*.jar` | `Contents/Resources/libs/stirling-pdf-*.jar` | — | — |
| OCR binary | — | — | subprocess | `tesseract.exe` / `bin/tesseract` |
| OCR native deps | — | — | — | all `*.dll` / `lib/*.dylib` |
| French tessdata | — | — | — | `tessdata/fra.traineddata` |
| OpenCV bubbles | — | — | bundled in PyInstaller (`cv2`) | — |
| Tesseract OCR | — | — | bundled (`pytesseract`) + PATH | external binary |

## Launcher environment (set before engine starts)

| Variable | Windows | macOS |
|----------|---------|-------|
| `PATH` | `%ROOT%tesseract` | `$ROOT/tesseract/bin` |
| `TESSDATA_PREFIX` | `%ROOT%tesseract\` | `$ROOT/tesseract/share/tessdata` |
| `DYLD_LIBRARY_PATH` | — | `$ROOT/tesseract/lib` |
| `FRENCH_READER_CORS_ORIGINS` | Tauri desktop origins | same |
| `VITE_FRENCH_READER_API_URL` | `http://127.0.0.1:5002/french-reader` | same |

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
3. Engine smoke test: `GET /french-reader/status` → `ocr_ready=true`, `bubble_ready=true`

`build-portable-windows.ps1` and `build-portable-macos.sh` call these automatically.

## If `fra.traineddata` is missing on the build machine

`fetch-tesseract-windows.ps1` and `fetch-tesseract-macos.sh` download it from [tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast).

## Not bundled (by design)

- **YOLO** bubble model (`ultralytics` / `torch`) — excluded from PyInstaller; OpenCV bubble detection is used instead
- **PaddleOCR** — excluded; Tesseract is the portable OCR engine
- **LLM API keys** — user supplies in Settings; TTS/AI need network
