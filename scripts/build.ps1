# scripts/build.ps1 -- One-command full build for Open-Write
# ===========================================================
# Run from the repo root:
#   .\scripts\build.ps1
#
# What this does:
#   1. Builds the Python backend into a single .exe (PyInstaller)
#   2. Copies the backend exe to Tauri's sidecar directory
#   3. Builds the React frontend + Tauri shell into a Windows installer (.msi)
#      and a portable executable (.exe)
#
# Prerequisites:
#   - Python 3.10+ on PATH
#   - uv installed (pip install uv)
#   - Node.js 18+ on PATH
#   - Rust toolchain (rustup) for Tauri
#   - Frontend deps installed (cd app && npm install)
#   - Backend deps installed (cd backend && uv sync --dev)
#
# Output:
#   app/src-tauri/target/release/bundle/msi/Open-Write_*.msi  (installer)
#   app/src-tauri/target/release/bundle/nsis/Open-Write_*-setup.exe  (portable)
#   app/src-tauri/binaries/open-write-backend-x86_64-pc-windows-msvc.exe  (sidecar)

[CmdletBinding()]
param(
    # Skip the backend build if the sidecar exe already exists and is fresh.
    # Useful when only frontend code changed.
    [switch]$SkipBackend,

    # Build the Tauri bundle in debug mode (faster, larger exe, no optimization).
    [switch]$Debug
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path "$PSScriptRoot\.."

function Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function OK($msg) {
    Write-Host "    ok: $msg" -ForegroundColor Green
}


# ── Step 1: Build backend sidecar ─────────────────────────────────────────────

$sidecarPath = Join-Path $repoRoot "app\src-tauri\binaries\open-write-backend-x86_64-pc-windows-msvc.exe"

if (-not $SkipBackend) {
    Step "Building backend sidecar (PyInstaller)"
    & (Join-Path $PSScriptRoot "build-backend.ps1")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Backend build failed. Run 'cd backend && uv sync --dev' first."
        exit 1
    }
    OK "Backend sidecar built"
} else {
    if (-not (Test-Path $sidecarPath)) {
        Write-Error "Sidecar not found at $sidecarPath. Remove -SkipBackend or build manually first."
        exit 1
    }
    $sizeMB = [math]::Round((Get-Item $sidecarPath).Length / 1MB, 1)
    Write-Host "    Skipping backend build (using existing sidecar: $sizeMB MB)" -ForegroundColor Yellow
}


# ── Step 2: Build Tauri bundle (frontend + shell + installer) ─────────────────

Step "Building Tauri bundle (frontend + native shell + installer)"

Push-Location (Join-Path $repoRoot "app")
try {
    if ($Debug) {
        npm.cmd run tauri build -- --debug
    } else {
        npm.cmd run tauri build
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tauri build failed. Check the output above for details."
        exit 1
    }
} finally {
    Pop-Location
}

OK "Tauri bundle built"


# ── Step 3: Locate and report outputs ─────────────────────────────────────────

Step "Build outputs"

$bundleDir = Join-Path $repoRoot "app\src-tauri\target\release\bundle"
if ($Debug) {
    $bundleDir = Join-Path $repoRoot "app\src-tauri\target\debug\bundle"
}

$msiDir  = Join-Path $bundleDir "msi"
$nsisDir = Join-Path $bundleDir "nsis"

$artifacts = @()

if (Test-Path $msiDir) {
    $msi = Get-ChildItem $msiDir -Filter "*.msi" | Select-Object -First 1
    if ($msi) {
        $sizeMB = [math]::Round($msi.Length / 1MB, 1)
        Write-Host "    Installer (.msi): $($msi.FullName) ($sizeMB MB)" -ForegroundColor Green
        $artifacts += $msi
    }
}

if (Test-Path $nsisDir) {
    $nsis = Get-ChildItem $nsisDir -Filter "*-setup.exe" | Select-Object -First 1
    if ($nsis) {
        $sizeMB = [math]::Round($nsis.Length / 1MB, 1)
        Write-Host "    Setup (.exe):     $($nsis.FullName) ($sizeMB MB)" -ForegroundColor Green
        $artifacts += $nsis
    }
}

if ($artifacts.Count -eq 0) {
    Write-Warning "No installer artifacts found in $bundleDir. Check the Tauri build output."
} else {
    Write-Host ""
    Write-Host "Build complete! $($artifacts.Count) artifact(s) ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "  The .msi installer installs Open-Write with Start Menu shortcuts." -ForegroundColor Gray
    Write-Host "  The -setup.exe is a portable installer (no Start Menu, runs directly)." -ForegroundColor Gray
    Write-Host "  Both include the backend sidecar -- no Python needed on the target machine." -ForegroundColor Gray
}
