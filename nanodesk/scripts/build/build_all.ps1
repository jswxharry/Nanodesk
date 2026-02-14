# One-click build script for Nanodesk Desktop
# This creates a complete installer with embedded Python
# Usage: .\nanodesk\scripts\build_all.ps1

param(
    [switch]$Clean,
    [switch]$SkipBuild,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
# nanodesk/scripts/build/ → project root (3 levels up)
$ProjectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot))
$ScriptRoot = $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Nanodesk Desktop Complete Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 0: Validate environment
Write-Host "[0/4] Checking environment..." -ForegroundColor Yellow

# Check Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Error "Python not found. Please install Python 3.11+ and add to PATH"
    exit 1
}

$PythonVersion = python --version 2>&1
Write-Host "  Found: $PythonVersion" -ForegroundColor Gray

# Check pip
pip --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip not found"
    exit 1
}

# Check PyInstaller
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "  Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

Write-Host "  Environment OK" -ForegroundColor Green

# Step 1: Prepare embedded Python
Write-Host ""
Write-Host "[1/4] Preparing embedded Python..." -ForegroundColor Yellow

$BuildDir = Join-Path $ProjectRoot "build_desktop"
$EmbeddedDir = Join-Path $BuildDir "embedded_python"

if ($Clean -and (Test-Path $BuildDir)) {
    Write-Host "  Cleaning build directory..." -ForegroundColor Yellow
    Remove-Item $BuildDir -Recurse -Force
}

if (Test-Path (Join-Path $EmbeddedDir "python.exe")) {
    Write-Host "  Embedded Python already exists, skipping" -ForegroundColor Gray
} else {
    python (Join-Path $ScriptRoot "prepare_embedded_python.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to prepare embedded Python"
        exit 1
    }
}

# Step 2: Build desktop application
Write-Host ""
Write-Host "[2/4] Building desktop application..." -ForegroundColor Yellow

if (-not $SkipBuild) {
    & (Join-Path $ScriptRoot "build_desktop.ps1") -SkipEmbeddedPython
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Desktop build failed"
        exit 1
    }
} else {
    Write-Host "  Skipped (use -SkipBuild to skip this step)" -ForegroundColor Gray
}

# Step 3: Create installer
Write-Host ""
Write-Host "[3/4] Creating installer..." -ForegroundColor Yellow

if (-not $SkipInstaller) {
    # Check for ISCC
    $ISCC = Get-Command iscc -ErrorAction SilentlyContinue
    if (-not $ISCC) {
        # Try common install locations
        $PossiblePaths = @(
            "${env:ProgramFiles(x86)}\Inno Setup 6\iscc.exe",
            "${env:ProgramFiles}\Inno Setup 6\iscc.exe",
            "${env:LOCALAPPDATA}\Programs\Inno Setup 6\iscc.exe"
        )
        foreach ($Path in $PossiblePaths) {
            if (Test-Path $Path) {
                $ISCC = $Path
                break
            }
        }
    }
    
    if (-not $ISCC) {
        Write-Host "  WARNING: Inno Setup not found. Skipping installer creation." -ForegroundColor Yellow
        Write-Host "  Download from: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
        $SkipInstaller = $true
    } else {
        Write-Host "  Using Inno Setup: $ISCC" -ForegroundColor Gray
        & $ISCC (Join-Path $ScriptRoot "setup.iss")
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Installer created successfully" -ForegroundColor Green
        } else {
            Write-Warning "Installer creation failed"
        }
    }
}

if ($SkipInstaller) {
    Write-Host "  Skipped" -ForegroundColor Gray
}

# Step 4: Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$DistDir = Join-Path $ProjectRoot "dist"
$PortableDir = Join-Path $DistDir "Nanodesk"
$Installer = Get-ChildItem -Path $DistDir -Filter "Nanodesk-Setup-*.exe" | Select-Object -First 1

Write-Host "Output files:" -ForegroundColor Cyan

if (Test-Path $PortableDir) {
    $Size = (Get-ChildItem $PortableDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  Portable version: $PortableDir" -ForegroundColor White
    Write-Host "                    ($([math]::Round($Size, 1)) MB)" -ForegroundColor Gray
}

if ($Installer) {
    $Size = $Installer.Length / 1MB
    Write-Host "  Installer:        $($Installer.FullName)" -ForegroundColor White
    Write-Host "                    ($([math]::Round($Size, 1)) MB)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Distribution options:" -ForegroundColor Cyan
Write-Host "  1. Portable: Zip the folder '$PortableDir'" -ForegroundColor White
Write-Host "  2. Installer: Share '$($Installer.Name)'" -ForegroundColor White
Write-Host ""
Write-Host "Users do NOT need Python installed!" -ForegroundColor Green
Write-Host ""
