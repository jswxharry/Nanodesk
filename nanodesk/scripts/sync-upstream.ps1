# Sync upstream changes to nanodesk branch (Windows PowerShell)
# Usage: .\nanodesk\scripts\sync-upstream.ps1

$ErrorActionPreference = "Stop"

Write-Host "==> 1. Updating main branch (tracking upstream)" -ForegroundColor Cyan
git checkout main
if ($LASTEXITCODE -ne 0) { exit 1 }

git fetch upstream
if ($LASTEXITCODE -ne 0) { 
    Write-Host "Error: Failed to fetch upstream. Did you add upstream remote?" -ForegroundColor Red
    Write-Host "Run: git remote add upstream https://github.com/HKUDS/nanobot.git"
    exit 1
}

git merge upstream/main --ff-only
if ($LASTEXITCODE -ne 0) { exit 1 }

git push origin main
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n==> 2. Syncing to nanodesk branch" -ForegroundColor Cyan
git checkout nanodesk
if ($LASTEXITCODE -ne 0) { exit 1 }

git merge main -m "sync: merge upstream changes into nanodesk"
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n==> 3. Handling README conflicts (if any)" -ForegroundColor Cyan
$conflictFiles = git diff --name-only --diff-filter=U
if ($conflictFiles -contains "README.md") {
    Write-Host "⚠️  README.md has conflicts, keeping our version..." -ForegroundColor Yellow
    git checkout --ours README.md
    git add README.md
    git commit -m "sync: resolve README conflict (keep ours)" --no-verify 2>$null
}

Write-Host "`n✅ Sync complete!" -ForegroundColor Green
Write-Host "`nIf there are other conflicts, resolve them and run:" -ForegroundColor Yellow
Write-Host "  git add ."
Write-Host "  git commit -m 'sync: resolve conflicts'"
Write-Host "  git push origin nanodesk"
