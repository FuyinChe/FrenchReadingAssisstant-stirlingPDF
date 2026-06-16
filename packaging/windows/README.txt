French Reading Assistant for Stirling PDF (Windows portable)
=========================================================

START HERE / 从这里启动
  Double-click:  Start French Reading Assistant.bat

WHAT THIS FOLDER CONTAINS / 目录说明
  app\       Stirling PDF desktop (exe + runtime\jre + libs\*.jar)
  engine\    French Reader OCR / TTS / AI service (local only)
  tesseract\ OCR binaries + tessdata (tesseract.exe and all *.dll; French when bundled)

FIRST RUN / 首次使用
  1. Windows may show SmartScreen — click "More info" → "Run anyway"
  2. Open a PDF in Stirling
  3. Go to Recommended tools → French Reading Assistant
  4. Optional: Settings (gear) → paste LLM API key for AI features

NETWORK / 网络
  - PDF stays on your computer
  - Read aloud (TTS) and AI need internet

OCR DLL errors (libtiff-6.dll, libjpeg-8.dll, …)?
  - Use a newer zip build, or copy all *.dll from a full Tesseract install
    into the tesseract\ folder next to tesseract.exe

VERSION / 版本
  See VERSION.txt in this folder.

SUPPORT / 帮助
  https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF

LICENSE / 许可证
  LICENSE              — MIT (French Reading Assistant original code)
  THIRD-PARTY-NOTICES.md — Stirling PDF + bundled components
  licenses\STIRLING-PDF-LICENSE — Stirling PDF upstream license (MIT + mixed)

Powered by Stirling PDF — https://github.com/Stirling-Tools/Stirling-PDF
(French Reading Assistant is a third-party extension, not an official Stirling product.)
