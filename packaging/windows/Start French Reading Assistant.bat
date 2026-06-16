@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "ROOT=%~dp0"
set "PATH=%ROOT%tesseract;%PATH%"
set "TESSDATA_PREFIX=%ROOT%tesseract\tessdata"
set "FRENCH_READER_ENABLED=true"
set "VITE_FRENCH_READER_ENABLED=true"
set "VITE_FRENCH_READER_API_URL=http://127.0.0.1:5002/french-reader"
rem Stirling Tauri WebView needs these origins for OCR POST (CORS preflight).
if not defined FRENCH_READER_CORS_ORIGINS set "FRENCH_READER_CORS_ORIGINS=http://localhost:5173,http://localhost:8080,http://127.0.0.1:8080,http://127.0.0.1:5173,https://tauri.localhost,http://tauri.localhost,https://asset.localhost,http://asset.localhost"

if exist "%ROOT%VERSION.txt" type "%ROOT%VERSION.txt"
echo.
echo Starting French Reading Assistant...
echo.

if not exist "%ROOT%engine\french-reader-engine.exe" (
  echo [ERROR] Missing engine\french-reader-engine.exe
  echo Run the packaging script on a build machine first.
  pause
  exit /b 1
)

start "French Reader Engine" /MIN "%ROOT%engine\french-reader-engine.exe"

set "READY=0"
for /L %%i in (1,1,45) do (
  powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5002/health' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
  if not errorlevel 1 (
    set "READY=1"
    goto wait_done
  )
  timeout /t 1 /nobreak >nul
)
:wait_done
if "%READY%"=="0" (
  echo [WARN] French Reader engine is still starting. You can continue; OCR may take a moment.
) else (
  echo French Reader engine is ready.
)

set "APP_EXE="
for %%F in ("%ROOT%app\*.exe") do (
  set "APP_EXE=%%~fF"
  goto launch_app
)

echo [ERROR] No .exe found in app\ folder.
pause
exit /b 1

:launch_app
echo Launching: %APP_EXE%
start "" "%APP_EXE%"
echo.
echo Keep this window open while using the app, or close it to stop the French Reader engine.
pause
