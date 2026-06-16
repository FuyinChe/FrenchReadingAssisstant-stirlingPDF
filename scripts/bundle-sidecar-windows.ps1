#Requires -Version 5.1
<#
.SYNOPSIS
  Bundle french-reader-engine as a Windows executable (PyInstaller).

.PARAMETER OutputDir
  Directory for french-reader-engine.exe (default: dist/sidecar-windows)
#>
param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $OutputDir) {
    $OutputDir = Join-Path $Root "dist/sidecar-windows"
}

function Write-Log([string]$Message) {
    Write-Host "[bundle-sidecar-windows] $Message"
}

function Ensure-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

Ensure-Command python

Write-Log "Syncing plugin version..."
& python (Join-Path $Root "scripts/sync-plugin-version.py") --platform windows-x64

$EngineDir = Join-Path $Root "extensions/french-reader-engine"
$VenvDir = Join-Path $Root "dist/build-venv-windows"
$Spec = Join-Path $Root "packaging/windows/pyinstaller-engine.spec"

if (-not (Test-Path $VenvDir)) {
    Write-Log "Creating build venv at $VenvDir"
    & python -m venv $VenvDir
}

$Py = Join-Path $VenvDir "Scripts/python.exe"

Write-Log "Installing build dependencies..."
& $Py -m pip install --upgrade pip wheel
& $Py -m pip install pyinstaller
& $Py -m pip install -e "${EngineDir}[bubble]"

Write-Log "Verifying OpenCV (cv2) before PyInstaller..."
& $Py -c "import cv2; print('opencv', cv2.__version__)"
if ($LASTEXITCODE -ne 0) { throw "opencv-python-headless (cv2) not importable in build venv" }

$BuildWork = Join-Path $Root "dist/pyinstaller-work"
$BuildDist = Join-Path $Root "dist/pyinstaller-dist"
New-Item -ItemType Directory -Force -Path $BuildWork, $BuildDist | Out-Null

Write-Log "Running PyInstaller (this may take several minutes)..."
& $Py -m PyInstaller $Spec --noconfirm --clean --workpath $BuildWork --distpath $BuildDist

$BuiltExe = Join-Path $BuildDist "french-reader-engine.exe"
if (-not (Test-Path $BuiltExe)) {
    throw "PyInstaller output not found: $BuiltExe"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Copy-Item -Force $BuiltExe (Join-Path $OutputDir "french-reader-engine.exe")
Write-Log "Engine binary: $(Join-Path $OutputDir 'french-reader-engine.exe')"
