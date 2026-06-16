#Requires -Version 5.1
<#
.SYNOPSIS
  Verify a staged Windows portable folder before zipping.

.PARAMETER StagingDir
  Path to French-Reading-Assistant-*-windows-x64 folder.

.PARAMETER SkipDesktop
  Skip Stirling app/runtime checks (engine-only builds).

.PARAMETER SmokeTestEngine
  Start engine briefly and call /french-reader/status (default: true).
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$StagingDir,
    [switch]$SkipDesktop,
    [bool]$SmokeTestEngine = $true
)

$ErrorActionPreference = "Stop"

function Write-Log([string]$Message) {
    Write-Host "[verify-portable-staging] $Message"
}

function Fail([string]$Message) {
    throw "[verify-portable-staging] $Message"
}

if (-not (Test-Path $StagingDir)) {
    Fail "Staging directory not found: $StagingDir"
}

Write-Log "Verifying $StagingDir"

$Launcher = Join-Path $StagingDir "Start French Reading Assistant.bat"
$Engine = Join-Path $StagingDir "engine/french-reader-engine.exe"
$TessExe = Join-Path $StagingDir "tesseract/tesseract.exe"
$TessData = Join-Path $StagingDir "tesseract/tessdata"
$FraData = Join-Path $TessData "fra.traineddata"

foreach ($path in @($Launcher, $Engine, $TessExe)) {
    if (-not (Test-Path $path)) { Fail "Missing required file: $path" }
}

if (-not (Test-Path $FraData)) {
    Fail "Missing French OCR data: $FraData"
}

$dllCount = (Get-ChildItem -Path (Join-Path $StagingDir "tesseract") -Filter "*.dll" -File).Count
if ($dllCount -lt 5) {
    Fail "tesseract/ has only $dllCount DLL(s); expected full dependency set beside tesseract.exe"
}

foreach ($pattern in @("libtesseract*.dll", "libleptonica*.dll", "libtiff*.dll", "libjpeg*.dll")) {
    if (-not (Get-ChildItem -Path (Join-Path $StagingDir "tesseract") -Filter $pattern -File -ErrorAction SilentlyContinue)) {
        Fail "Missing Tesseract dependency pattern: $pattern"
    }
}

$prevPath = $env:PATH
$prevTess = $env:TESSDATA_PREFIX
$TessRoot = Join-Path $StagingDir "tesseract"
$env:PATH = "$TessRoot;$prevPath"
try {
    $tessVersion = & $TessExe --version 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -or $tessVersion -match 'was not found|cannot proceed') {
        Fail "Bundled tesseract.exe failed to run:`n$tessVersion"
    }
    $langsOk = $false
    $prefixes = @(
        $(if ($TessRoot.EndsWith('\')) { $TessRoot } else { "$TessRoot\" }),
        (Join-Path $TessRoot "tessdata"),
        ""
    )
    foreach ($prefix in $prefixes) {
        if ($prefix) { $env:TESSDATA_PREFIX = $prefix } else { Remove-Item Env:TESSDATA_PREFIX -ErrorAction SilentlyContinue }
        $langLines = @(& $TessExe --list-langs 2>&1 | ForEach-Object { "$_".Trim().TrimEnd([char]13) } | Where-Object {
            $_ -and $_ -notmatch '^List of available' -and $_ -notmatch '^tesseract v'
        })
        if ($langLines -contains 'fra') { $langsOk = $true; break }
    }
    if (-not $langsOk) {
        Fail "Bundled tesseract missing fra language (check tessdata/fra.traineddata and TESSDATA_PREFIX)"
    }
    Write-Log "Tesseract OK: $($tessVersion.Trim().Split([Environment]::NewLine)[0]); fra present"
} finally {
    $env:PATH = $prevPath
    if ($null -ne $prevTess) { $env:TESSDATA_PREFIX = $prevTess } else { Remove-Item Env:TESSDATA_PREFIX -ErrorAction SilentlyContinue }
}

if (-not $SkipDesktop) {
    $AppDir = Join-Path $StagingDir "app"
    $JavaExe = Join-Path $AppDir "runtime/jre/bin/java.exe"
    $Jar = Get-ChildItem -Path (Join-Path $AppDir "libs") -Filter "stirling-pdf-*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
    $StirlingExe = Get-ChildItem -Path $AppDir -Filter "*.exe" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notmatch 'engine|setup|install' } | Select-Object -First 1
    if (-not $StirlingExe) { Fail "Missing Stirling desktop exe in app\" }
    if (-not (Test-Path $JavaExe)) { Fail "Missing Stirling JRE: $JavaExe" }
    if (-not $Jar) { Fail "Missing Stirling JAR under app\libs" }
    Write-Log "Stirling desktop OK: $($StirlingExe.Name), $($Jar.Name), java.exe"
}

if ($SmokeTestEngine) {
    $prevCors = $env:FRENCH_READER_CORS_ORIGINS
    $env:PATH = "$(Join-Path $StagingDir 'tesseract');$prevPath"
    $env:TESSDATA_PREFIX = "$(Join-Path $StagingDir 'tesseract')\"
    $env:FRENCH_READER_CORS_ORIGINS = "http://localhost:5173,https://tauri.localhost"
    $proc = $null
    try {
        $proc = Start-Process -FilePath $Engine -PassThru -WindowStyle Hidden
        $status = $null
        for ($i = 0; $i -lt 45; $i++) {
            try {
                $status = Invoke-RestMethod -Uri "http://127.0.0.1:5002/french-reader/status" -TimeoutSec 3
                break
            } catch {
                Start-Sleep -Seconds 1
            }
        }
        if (-not $status) { Fail "Engine did not respond on :5002/french-reader/status" }
        if (-not $status.ocr_ready) { Fail "Engine ocr_ready=false — tesseract/pytesseract not usable" }
        if (-not $status.bubble_ready) { Fail "Engine bubble_ready=false — OpenCV (cv2) not bundled in PyInstaller exe" }
        Write-Log "Engine smoke test OK: ocr_ready=$($status.ocr_ready), bubble_ready=$($status.bubble_ready)"

        $corsHeaders = @{
            Origin = 'https://tauri.localhost'
            'Access-Control-Request-Method' = 'POST'
            'Access-Control-Request-Headers' = 'content-type'
        }
        try {
            $preflight = Invoke-WebRequest -Uri "http://127.0.0.1:5002/french-reader/ocr/region" -Method OPTIONS -Headers $corsHeaders -TimeoutSec 5 -UseBasicParsing
            if ($preflight.StatusCode -ge 400) {
                Fail "CORS preflight failed for Tauri origin (OPTIONS /ocr/region returned $($preflight.StatusCode))"
            }
            Write-Log "CORS preflight OK for https://tauri.localhost"
        } catch {
            Fail "CORS preflight failed for Tauri origin: $($_.Exception.Message)"
        }
    } finally {
        if ($proc -and -not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
        $env:FRENCH_READER_CORS_ORIGINS = $prevCors
    }
}

Write-Log "All checks passed for $StagingDir"
