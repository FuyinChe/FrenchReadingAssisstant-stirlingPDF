#Requires -Version 5.1
<#
.SYNOPSIS
  Build a Windows portable ZIP: Stirling desktop + French Reader engine + Tesseract.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\build-portable-windows.ps1

.NOTES
  Run on Windows 10/11 x64 with build prerequisites installed.
  See docs/deployment/windows-portable-packaging.md
#>
param(
    [switch]$SkipDesktop,
    [switch]$SkipZip,
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $OutputRoot) {
    $OutputRoot = Join-Path $Root "dist/portable-windows"
}

function Write-Log([string]$Message) {
    Write-Host "[build-portable-windows] $Message"
}

function Ensure-Command([string]$Name, [string]$Hint = "") {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        $extra = if ($Hint) { " — $Hint" } else { "" }
        throw "Required command not found: $Name$extra"
    }
}

function Invoke-GitBash([string]$ScriptPath) {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) { throw "git not found" }
    $gitRoot = Split-Path (Split-Path $git.Source)
    $bash = Join-Path $gitRoot "bin\bash.exe"
    if (-not (Test-Path $bash)) {
        $bash = Join-Path $gitRoot "usr\bin\bash.exe"
    }
    if (-not (Test-Path $bash)) {
        throw "Git Bash not found. Install Git for Windows."
    }
    & $bash -lc "cd '$($Root -replace '\\','/')' && bash '$($ScriptPath -replace '\\','/')'"
    if ($LASTEXITCODE -ne 0) { throw "bash script failed: $ScriptPath" }
}

Write-Log "Checking prerequisites..."
Ensure-Command git
Ensure-Command python
Ensure-Command node "Node.js 20+"
Ensure-Command java "JDK 25 for Stirling"
Ensure-Command cargo "Rust (rustup) for Tauri"
Ensure-Command task "go-task: scoop install task / choco install go-task"

$VersionJson = Join-Path $Root "extensions/french-reader-version.json"
$VersionObj = Get-Content $VersionJson -Raw | ConvertFrom-Json
$PluginVersion = $VersionObj.version
$BuildId = "$PluginVersion-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$StagingName = "French-Reading-Assistant-$PluginVersion-windows-x64"
$StagingDir = Join-Path $OutputRoot $StagingName

Write-Log "Plugin version $PluginVersion (build $BuildId)"
& python (Join-Path $Root "scripts/sync-plugin-version.py") --platform windows-x64 --build-id $BuildId

Write-Log "Initializing stirling-upstream submodule..."
& git -C $Root submodule update --init --recursive
if ($LASTEXITCODE -ne 0) { throw "git submodule failed" }

$env:FRENCH_READER_ENABLED = "true"
$env:VITE_FRENCH_READER_ENABLED = "true"
$env:VITE_FRENCH_READER_API_URL = "http://127.0.0.1:5002/french-reader"

Write-Log "Installing extensions into Stirling..."
Invoke-GitBash (Join-Path $Root "scripts/install-extensions.sh")

Write-Log "Bundling French Reader engine..."
& (Join-Path $Root "scripts/bundle-sidecar-windows.ps1") -OutputDir (Join-Path $StagingDir "engine")

Write-Log "Staging Tesseract OCR..."
& (Join-Path $Root "scripts/fetch-tesseract-windows.ps1") -OutputDir (Join-Path $StagingDir "tesseract")

if (-not $SkipDesktop) {
    Write-Log "Building Stirling Tauri desktop (task desktop:build:dev) — exe only, no MSI/updater signing..."
    Push-Location (Join-Path $Root "stirling-upstream")
    # Full desktop:build bundles MSI and signs updater artifacts (needs TAURI_SIGNING_PRIVATE_KEY).
    # Portable zip only needs the release exe; upstream desktop:build:dev uses --no-bundle.
    & task desktop:build:dev
    if ($LASTEXITCODE -ne 0) { throw "task desktop:build:dev failed" }
    Pop-Location

    $BundleRoot = Join-Path $Root "stirling-upstream/frontend/editor/src-tauri/target/release/bundle"
    $ReleaseDir = Join-Path $Root "stirling-upstream/frontend/editor/src-tauri/target/release"
    $TauriSrc = Join-Path $Root "stirling-upstream/frontend/editor/src-tauri"
    $AppDir = Join-Path $StagingDir "app"
    New-Item -ItemType Directory -Force -Path $AppDir | Out-Null

    function Copy-DesktopTree([string]$Name, [string[]]$Candidates) {
        foreach ($src in $Candidates) {
            if (Test-Path $src) {
                $dest = Join-Path $AppDir $Name
                if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
                Copy-Item -Recurse -Force $src $dest
                Write-Log "Copied desktop ${Name} from $src"
                return $true
            }
        }
        return $false
    }

    $Copied = $false
    $ReleaseExe = Get-ChildItem -Path $ReleaseDir -Filter "*.exe" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notmatch 'engine|installer|setup|bundle' } |
        Select-Object -First 1
    if ($ReleaseExe) {
        Copy-Item -Force $ReleaseExe.FullName $AppDir
        Write-Log "Copied desktop exe: $($ReleaseExe.Name)"
        $Copied = $true
    }
    if (-not $Copied) {
        $BundleMatches = Get-ChildItem -Path $BundleRoot -Recurse -Filter "*.exe" -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -notmatch 'engine|bundle' }
        foreach ($item in $BundleMatches) {
            Copy-Item -Force $item.FullName $AppDir
            Write-Log "Copied desktop exe: $($item.Name)"
            $Copied = $true
            break
        }
    }
    if (-not $Copied) {
        throw "Could not find Stirling desktop exe under $ReleaseDir"
    }

    # desktop:build:dev (--no-bundle) only emits the exe; bundled JRE + JAR must sit beside it.
    $runtimeOk = Copy-DesktopTree "runtime" @(
        (Join-Path $ReleaseDir "runtime"),
        (Join-Path $TauriSrc "runtime")
    )
    $libsOk = Copy-DesktopTree "libs" @(
        (Join-Path $ReleaseDir "libs"),
        (Join-Path $TauriSrc "libs")
    )
    if (-not $runtimeOk) { throw "Missing runtime/jre — Stirling Java backend cannot start" }
    if (-not $libsOk) { throw "Missing libs/stirling-pdf jar — Stirling Java backend cannot start" }

    $JavaExe = Join-Path $AppDir "runtime/jre/bin/java.exe"
    $Jar = Get-ChildItem -Path (Join-Path $AppDir "libs") -Filter "stirling-pdf-*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not (Test-Path $JavaExe)) { throw "Bundled JRE missing after staging: $JavaExe" }
    if (-not $Jar) { throw "Stirling PDF jar missing under app\libs after staging" }
    Write-Log "Verified desktop payload: java.exe + $($Jar.Name)"
} else {
    Write-Log "SkipDesktop set — place Stirling .exe in $StagingDir\app manually"
    New-Item -ItemType Directory -Force -Path (Join-Path $StagingDir "app") | Out-Null
}

Copy-Item -Force (Join-Path $Root "packaging/windows/Start French Reading Assistant.bat") $StagingDir
Copy-Item -Force (Join-Path $Root "packaging/windows/README.txt") $StagingDir

$VersionInfo = Get-Content (Join-Path $Root "extensions/french-reader-engine/src/french_reader/_plugin_version.json") -Raw | ConvertFrom-Json
$VersionText = @"
French Reading Assistant (plugin)
Version: $($VersionInfo.version)
Build ID: $($VersionInfo.build.id)
Platform: $($VersionInfo.build.platform)
Built at: $($VersionInfo.build.builtAt)
Stirling PDF: https://github.com/Stirling-Tools/Stirling-PDF
"@
Set-Content -Path (Join-Path $StagingDir "VERSION.txt") -Value $VersionText -Encoding UTF8

$VerifyArgs = @{ StagingDir = $StagingDir }
if ($SkipDesktop) { $VerifyArgs.SkipDesktop = $true }
& (Join-Path $Root "scripts/verify-portable-staging.ps1") @VerifyArgs

if (-not $SkipZip) {
    $ZipPath = Join-Path $OutputRoot "$StagingName.zip"
    if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
    Write-Log "Creating zip: $ZipPath"
    Compress-Archive -Path $StagingDir -DestinationPath $ZipPath -Force
    Write-Log "Done: $ZipPath"
} else {
    Write-Log "SkipZip set — staged folder: $StagingDir"
}

Write-Log "Test on Windows: unzip and double-click 'Start French Reading Assistant.bat'"
