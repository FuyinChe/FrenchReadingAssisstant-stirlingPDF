# Third-party notices

French Reading Assistant for Stirling PDF combines several components. This file
summarizes licenses for **end-user distributions** (portable zip, desktop bundle).

## French Reading Assistant (this project)

| Component | License |
|-----------|---------|
| `extensions/french-reader-engine/` | [MIT](LICENSE) |
| `extensions/french-reader-frontend/` | [MIT](LICENSE) |
| `scripts/`, `packaging/`, `docs/` (this repo) | [MIT](LICENSE) |

Copyright (c) 2025 Fuyin Che and French Reading Assistant contributors.

## Stirling PDF (base application)

| Component | License |
|-----------|---------|
| Stirling PDF UI / desktop / Java backend (bundled in portable `app/`) | **Mixed** — see [licenses/STIRLING-PDF-LICENSE](licenses/STIRLING-PDF-LICENSE) |
| MIT-covered Stirling code | MIT (Stirling PDF Inc.) |
| `engine/` and proprietary paths | Separate terms in upstream repo |

Upstream: https://github.com/Stirling-Tools/Stirling-PDF

**French Reading Assistant is not an official Stirling PDF product.**

## Bundled runtimes (portable zip)

| Component | License | Notes |
|-----------|---------|--------|
| Tesseract OCR | Apache 2.0 | UB-Mannheim / Google tesseract |
| tessdata (`fra.traineddata`, etc.) | Apache 2.0 | https://github.com/tesseract-ocr/tessdata |
| OpenJDK (inside Stirling `runtime/jre`) | GPLv2 + Classpath Exception | Temurin / upstream JRE |
| OpenCV (`opencv-python-headless` in engine) | Apache 2.0 | Via PyInstaller bundle |
| edge-tts, FastAPI, etc. | Per PyPI package | See engine build venv |

## Submodule

Development builds use `stirling-upstream/` (git submodule). Its LICENSE and
directory-specific licenses apply to that tree at the pinned commit.

## More detail

[docs/plan/07-license-compliance.md](docs/plan/07-license-compliance.md)
