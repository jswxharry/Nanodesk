# Initialize development environment on Windows (PowerShell)
# Usage: .\nanodesk\scripts\init-venv.ps1

$ErrorActionPreference = "Stop"

$venvPath = ".venv"

Write-Host "==> Creating virtual environment..." -ForegroundColor Cyan
if (Test-Path $venvPath) {
    Write-Host "⚠️  Virtual environment already exists at $venvPath" -ForegroundColor Yellow
    $response = Read-Host "Recreate? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Remove-Item -Recurse -Force $venvPath
        python -m venv $venvPath
    }
} else {
    python -m venv $venvPath
}

Write-Host "`n==> Activating virtual environment..." -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"

Write-Host "`n==> Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "`n==> Installing package in editable mode..." -ForegroundColor Cyan
pip install -e ".[dev]"

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nTo activate the environment in the future, run:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1"
Write-Host "`nTo start nanodesk:" -ForegroundColor Cyan
Write-Host "  nanodesk --help"
