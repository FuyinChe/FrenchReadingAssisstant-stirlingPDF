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

function Get-TesseractLangLines([string]$Exe) {
    $raw = & $Exe --list-langs 2>&1 | ForEach-Object { "$_" }
    return @($raw | ForEach-Object { $_.Trim().TrimEnd([char]13) } | Where-Object {
            $_ -and
            $_ -notmatch '^List of available' -and
            $_ -notmatch '^tesseract v'
        })
}

function Test-StagedTesseractLangs([string]$Exe, [string]$TessRoot) {
    $prevPath = $env:PATH
    $prevTess = $env:TESSDATA_PREFIX
    try {
        $env:PATH = "$TessRoot;$prevPath"
        $prefixes = @(
            $(if ($TessRoot.EndsWith('\')) { $TessRoot } else { "$TessRoot\" }),
            (Join-Path $TessRoot "tessdata"),
            ""
        )
        foreach ($prefix in $prefixes) {
            if ($prefix) {
                $env:TESSDATA_PREFIX = $prefix
            } else {
                Remove-Item Env:TESSDATA_PREFIX -ErrorAction SilentlyContinue
            }
            $langs = Get-TesseractLangLines $Exe
            if ($langs -contains 'fra') {
                Write-Log "Verified fra language pack (TESSDATA_PREFIX=$(if ($prefix) { $prefix } else { '<exe-relative>' }))"
                return $true
            }
        }
        return $false
    } finally {
        $env:PATH = $prevPath
        if ($null -ne $prevTess) {
            $env:TESSDATA_PREFIX = $prevTess
        } else {
            Remove-Item Env:TESSDATA_PREFIX -ErrorAction SilentlyContinue
        }
    }
}

function Ensure-FrenchTessdata([string]$TessDataDir) {
    $fra = Join-Path $TessDataDir "fra.traineddata"
    if (Test-Path $fra) { return }
    New-Item -ItemType Directory -Force -Path $TessDataDir | Out-Null
    $url = "https://github.com/tesseract-ocr/tessdata_fast/raw/main/fra.traineddata"
    Write-Log "Downloading fra.traineddata (not in build machine tessdata)..."
    Invoke-WebRequest -Uri $url -OutFile $fra -UseBasicParsing
    if (-not (Test-Path $fra)) {
        throw "Failed to download French tessdata to $fra"
    }
}

function Copy-TesseractTree([string]$Source) {
    $exe = Join-Path $Source "tesseract.exe"
    if (-not (Test-Path $exe)) {
        throw "tesseract.exe not found under $Source"
    }

    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    Copy-Item -Force $exe (Join-Path $OutputDir "tesseract.exe")

    $dlls = Get-ChildItem -Path $Source -Filter "*.dll" -File -ErrorAction SilentlyContinue
    if (-not $dlls) {
        throw "No Tesseract DLLs found beside $exe"
    }
    foreach ($dll in $dlls) {
        Copy-Item -Force $dll.FullName $OutputDir
    }
    Write-Log "Copied tesseract.exe and $($dlls.Count) DLL(s)"

    $tessSrc = Join-Path $Source "tessdata"
    if (-not (Test-Path $tessSrc)) {
        $alt = Join-Path (Split-Path $Source -Parent) "tessdata"
        if (Test-Path $alt) { $tessSrc = $alt }
    }
    if (Test-Path $tessSrc) {
        $tessDest = Join-Path $OutputDir "tessdata"
        if (Test-Path $tessDest) { Remove-Item -Recurse -Force $tessDest }
        Copy-Item -Recurse -Force $tessSrc $tessDest
    } else {
        throw "tessdata folder missing under $Source"
    }

    Ensure-FrenchTessdata (Join-Path $OutputDir "tessdata")

    $requiredDllPatterns = @(
        "libtesseract*.dll",
        "libleptonica*.dll",
        "libtiff*.dll",
        "libjpeg*.dll",
        "libgif*.dll",
        "libopenjp2*.dll"
    )
    foreach ($pattern in $requiredDllPatterns) {
        if (-not (Get-ChildItem -Path $OutputDir -Filter $pattern -File -ErrorAction SilentlyContinue)) {
            throw "Bundled Tesseract is incomplete: missing $pattern in $OutputDir"
        }
    }

    if (-not (Test-Path (Join-Path $OutputDir "tessdata/fra.traineddata"))) {
        throw "French tessdata missing after staging"
    }

    $stagedExe = Join-Path $OutputDir "tesseract.exe"
    $prevPath = $env:PATH
    $env:PATH = "$OutputDir;$prevPath"
    try {
        $version = & $stagedExe --version 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0 -or $version -match 'was not found|cannot proceed') {
            throw "Staged tesseract.exe failed to run:`n$version"
        }
        Write-Log "Verified staged binary: $($version.Trim().Split([Environment]::NewLine)[0])"
        if (-not (Test-StagedTesseractLangs $stagedExe $OutputDir)) {
            throw "Staged tesseract missing fra in --list-langs (file exists: tessdata/fra.traineddata)"
        }
    } finally {
        $env:PATH = $prevPath
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
