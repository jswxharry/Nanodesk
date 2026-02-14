# Test script for embedded Python setup
# Verifies the embedded Python is correctly configured

param(
    [string]$EmbeddedDir = "build_desktop\embedded_python"
)

$ErrorActionPreference = "Stop"
# nanodesk/scripts/build/ → project root (3 levels up)
$ProjectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot))
$EmbeddedPath = Join-Path $ProjectRoot $EmbeddedDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Embedded Python Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if embedded Python exists
$PythonExe = Join-Path $EmbeddedPath "python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Error "Embedded Python not found at: $PythonExe"
    Write-Host "Run: python nanodesk/scripts/prepare_embedded_python.py"
    exit 1
}

Write-Host "Embedded Python: $PythonExe" -ForegroundColor Green
Write-Host ""

# Test 1: Python version
Write-Host "[Test 1] Python version..." -ForegroundColor Yellow
& $PythonExe --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python works" -ForegroundColor Green
} else {
    Write-Error "  ✗ Python failed"
}
Write-Host ""

# Test 2: pip availability
Write-Host "[Test 2] pip availability..." -ForegroundColor Yellow
& $PythonExe -m pip --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ pip works" -ForegroundColor Green
} else {
    Write-Error "  ✗ pip failed"
}
Write-Host ""

# Test 3: Core dependencies
Write-Host "[Test 3] Core dependencies..." -ForegroundColor Yellow
$deps = @("typer", "pydantic", "loguru", "rich", "websockets", "httpx", "litellm")
foreach ($dep in $deps) {
    $result = & $PythonExe -c "import $dep; print('OK')" 2>&1
    if ($result -eq "OK") {
        Write-Host "  ✓ $dep" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dep - $result" -ForegroundColor Red
    }
}
Write-Host ""

# Test 4: Nanobot
Write-Host "[Test 4] Nanobot module..." -ForegroundColor Yellow
$result = & $PythonExe -c "import nanobot; print('OK')" 2>&1
if ($result -eq "OK") {
    Write-Host "  ✓ nanobot" -ForegroundColor Green
} else {
    Write-Host "  ✗ nanobot - $result" -ForegroundColor Red
}
Write-Host ""

# Test 5: Nanodesk launcher
Write-Host "[Test 5] Nanodesk launcher..." -ForegroundColor Yellow
$result = & $PythonExe -c "from nanodesk.launcher import main; print('OK')" 2>&1
if ($result -eq "OK") {
    Write-Host "  ✓ nanodesk.launcher" -ForegroundColor Green
} else {
    Write-Host "  ✗ nanodesk.launcher - $result" -ForegroundColor Red
}
Write-Host ""

# Test 6: Quick gateway test (dry run)
Write-Host "[Test 6] Gateway import test..." -ForegroundColor Yellow
$result = & $PythonExe -c "from nanobot.cli.commands import gateway_command; print('OK')" 2>&1
if ($result -eq "OK") {
    Write-Host "  ✓ Gateway imports OK" -ForegroundColor Green
} else {
    Write-Host "  ✗ Gateway import failed - $result" -ForegroundColor Red
}
Write-Host ""

# Test 7: Directory size
Write-Host "[Test 7] Package size..." -ForegroundColor Yellow
$Size = (Get-ChildItem $EmbeddedPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  Size: $([math]::Round($Size, 2)) MB" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
