#Requires -Version 5.1
<#
.SYNOPSIS
  Stage portable Tesseract OCR for the Windows zip bundle.

.PARAMETER OutputDir
  Target folder (default: dist/portable-staging/tesseract)
#>
param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $OutputDir) {
    $OutputDir = Join-Path $Root "dist/portable-staging/tesseract"
}

function Write-Log([string]$Message) {
    Write-Host "[fetch-tesseract-windows] $Message"
}

function Copy-TesseractTree([string]$Source) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $items = @(
        "tesseract.exe",
        "libtesseract-5.dll",
        "libgcc_s_seh-1.dll",
        "libstdc++-6.dll",
        "libwinpthread-1.dll",
        "libleptonica-6.dll"
    )
    foreach ($item in $items) {
        $src = Join-Path $Source $item
        if (Test-Path $src) {
            Copy-Item -Force $src $OutputDir
        }
    }
    $tessSrc = Join-Path $Source "tessdata"
    if (Test-Path $tessSrc) {
        Copy-Item -Recurse -Force $tessSrc (Join-Path $OutputDir "tessdata")
    }
}

$DefaultInstall = "${env:ProgramFiles}\Tesseract-OCR"
$ChocolateyInstall = Join-Path $env:ProgramData "chocolatey\lib\tesseract\tools"
foreach ($candidate in @($DefaultInstall, $ChocolateyInstall)) {
    if (Test-Path (Join-Path $candidate "tesseract.exe")) {
        Write-Log "Copying from $candidate"
        Copy-TesseractTree $candidate
        exit 0
    }
}

$CacheInstaller = Join-Path $Root "dist/cache/tesseract-ocr-w64-setup.exe"
$CacheDir = Join-Path $Root "dist/cache/tesseract-portable"

if ((Test-Path (Join-Path $CacheDir "tesseract.exe")) -and (Test-Path (Join-Path $CacheDir "tessdata/fra.traineddata"))) {
    Write-Log "Using cached portable Tesseract at $CacheDir"
    Copy-TesseractTree $CacheDir
    exit 0
}

Write-Log @"
Tesseract not found.

Install on this BUILD machine using one of:
  winget install --id UB-Mannheim.TesseractOCR
  choco install tesseract

Or download the Windows installer and place it at:
  $CacheInstaller
Then re-run this script (silent install to dist/cache/tesseract-portable).

After install, verify:
  tesseract --list-langs
  (must include fra)
"@
exit 1
