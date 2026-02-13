# Build script for Nanodesk Desktop with all dependencies
# Run this from project root: .\nanodesk\scripts\build_desktop_with_deps.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Nanodesk Desktop Builder (Full)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "pyproject.toml")) {
    Write-Error "Please run this script from the project root directory"
    exit 1
}

# Install dependencies first
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -e "."

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

# Build with PyInstaller
Write-Host "Building executable..." -ForegroundColor Yellow
pyinstaller nanodesk/desktop/main.py `
    --name="Nanodesk" `
    --windowed `
    --noconfirm `
    --clean `
    --distpath="dist" `
    --workpath="build" `
    --icon="nanodesk/desktop/resources/icons/logo.ico" `
    --add-data="nanodesk/desktop/resources;resources" `
    --add-data="nanodesk;nanodesk" `
    --add-data="nanobot;nanobot" `
    --hidden-import=typer `
    --hidden-import=pydantic `
    --hidden-import=loguru `
    --hidden-import=nanodesk `
    --hidden-import=nanobot `
    --hidden-import=PySide6

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   Build Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output: dist\Nanodesk\Nanodesk.exe" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "   Build Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
