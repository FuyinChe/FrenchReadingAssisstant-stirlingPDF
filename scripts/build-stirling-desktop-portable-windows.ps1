# Build Stirling Tauri desktop exe for portable zip (no MSI/updater signing).
#
# Upstream desktop:build:dev uses Unix cp/mkdir and bare jlink on Windows CI.
# Uses gradle-bootjar-portable.sh + explicit jlink instead of task desktop:prepare.
#
# Usage:
#   .\scripts\build-stirling-desktop-portable-windows.ps1
param()

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Stirling = Join-Path $Root "stirling-upstream"
$Frontend = Join-Path $Stirling "frontend"
$Editor = Join-Path $Frontend "editor"
$TauriSrc = Join-Path $Editor "src-tauri"
$TauriConf = Join-Path $TauriSrc "tauri.conf.json"

$JlinkModules = @(
    "java.base", "java.compiler", "java.desktop", "java.instrument", "java.logging",
    "java.management", "java.naming", "java.net.http", "java.prefs", "java.rmi",
    "java.scripting", "java.security.jgss", "java.security.sasl", "java.sql",
    "java.transaction.xa", "java.xml", "java.xml.crypto", "jdk.crypto.ec",
    "jdk.crypto.cryptoki", "jdk.unsupported", "jdk.dynalink"
) -join ","

function Write-Log([string]$Message) {
    Write-Host "[build-stirling-desktop-portable-windows] $Message"
}

if (-not $env:JAVA_HOME) {
    throw "JAVA_HOME is not set. Install a JDK (e.g. setup-java in CI) before building."
}

$Jlink = Join-Path $env:JAVA_HOME "bin\jlink.exe"
if (-not (Test-Path $Jlink)) {
    throw "jlink not found at $Jlink (JAVA_HOME=$env:JAVA_HOME)"
}

$env:PATH = "$(Join-Path $env:JAVA_HOME 'bin');$env:PATH"

Write-Log "Preparing Stirling frontend (task frontend:prepare MODE=desktop)..."
Push-Location $Stirling
& task frontend:prepare MODE=desktop
if ($LASTEXITCODE -ne 0) { throw "task frontend:prepare MODE=desktop failed" }
Pop-Location

Write-Log "Building Windows provisioner..."
Push-Location $Editor
& node scripts/build-provisioner.mjs
if ($LASTEXITCODE -ne 0) { throw "build-provisioner.mjs failed" }
Pop-Location

Write-Log "Building backend bootJar (windows-x64 JPDFium natives)..."
$GradleScript = Join-Path $Root "scripts/gradle-bootjar-portable.sh"
if (-not (Test-Path $GradleScript)) { throw "missing $GradleScript" }
& bash $GradleScript windows-x64
if ($LASTEXITCODE -ne 0) { throw "gradle-bootjar-portable.sh failed" }

$LibsDir = Join-Path $TauriSrc "libs"
New-Item -ItemType Directory -Force -Path $LibsDir | Out-Null
$Jar = Get-ChildItem -Path (Join-Path $Stirling "app/core/build/libs") -Filter "stirling-pdf-*.jar" |
    Select-Object -First 1
if (-not $Jar) {
    throw "stirling-pdf-*.jar not found under app/core/build/libs"
}
Copy-Item -Force $Jar.FullName $LibsDir
Write-Log "Copied $($Jar.Name) to libs/"

$RuntimeRoot = Join-Path $TauriSrc "runtime"
$RuntimeJre = Join-Path $RuntimeRoot "jre"
if (Test-Path $RuntimeJre) {
    Remove-Item -Recurse -Force $RuntimeJre
}
New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

Write-Log "Creating bundled JRE with jlink..."
& $Jlink `
    --add-modules $JlinkModules `
    --strip-debug `
    --compress=zip-6 `
    --no-header-files `
    --no-man-pages `
    --output $RuntimeJre
if ($LASTEXITCODE -ne 0) { throw "jlink failed" }

# jlink emits read-only files; Tauri's resource copier preserves permissions on rebuild.
Get-ChildItem -Recurse -File $RuntimeJre | ForEach-Object { $_.IsReadOnly = $false }

$ReleaseMarker = Join-Path $RuntimeJre "release"
if (-not (Test-Path $ReleaseMarker)) {
    throw "jlink output missing release marker at $ReleaseMarker"
}
Write-Log "Bundled JRE ready at runtime/jre"

Write-Log "Patching tauri.conf.json for portable build..."
& python (Join-Path $Root "scripts/patch-tauri-portable.py") $TauriConf
if ($LASTEXITCODE -ne 0) { throw "patch-tauri-portable.py failed" }

Write-Log "Running npx tauri build --no-bundle (NOT task desktop:build:dev)..."
Push-Location $Editor
& npx tauri build --no-bundle
if ($LASTEXITCODE -ne 0) { throw "npx tauri build --no-bundle failed" }
Pop-Location

Write-Log "Done. Exe under $Editor\src-tauri\target\release\"
