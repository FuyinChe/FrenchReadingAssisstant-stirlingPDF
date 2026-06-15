French Reading Assistant for Stirling PDF (macOS portable)
=========================================================

START HERE / 从这里启动
  Double-click:  Start French Reading Assistant.command
  (若无法打开：右键 → 打开，或在终端 chmod +x 后执行)

CONTENTS / 目录说明
  app/       Stirling PDF.app (with French Reader tool)
  engine/    French Reader OCR / TTS / AI (local :5002)
  tesseract/ OCR binaries + tessdata (French when bundled)

FIRST RUN / 首次使用
  1. macOS may block unsigned apps — System Settings → Privacy & Security → Open Anyway
  2. Open a PDF in Stirling
  3. Recommended tools → French Reading Assistant
  4. Optional: Settings → LLM API key

ARCHITECTURE / 架构
  Apple Silicon (arm64): French-Reading-Assistant-*-macos-arm64.zip
  Intel Mac (x64):       French-Reading-Assistant-*-macos-x64.zip

NETWORK / 网络
  PDF stays local; TTS and AI need internet.

Powered by Stirling PDF — https://github.com/Stirling-Tools/Stirling-PDF
